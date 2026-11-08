"""Unit tests for metamorphic canary test selector (FIX-19)."""

import pytest
from sage.guardrails.canary_selector import MetamorphicCanarySelector


def test_canary_selector_historical_ranking():
    # Synthetic history with known flips
    history = [
        # task_flaky flipped 3 out of 3 times
        {"task_id": "task_flaky", "passed_before": True, "passed_after": False},
        {"task_id": "task_flaky", "passed_before": True, "passed_after": False},
        {"task_id": "task_flaky", "passed_before": True, "passed_after": False},
        # task_medium flipped 1 out of 2 times
        {"task_id": "task_med", "passed_before": True, "passed_after": False},
        {"task_id": "task_med", "passed_before": True, "passed_after": True},
        # task_solid never flipped
        {"task_id": "task_solid", "passed_before": True, "passed_after": True},
        {"task_id": "task_solid", "passed_before": True, "passed_after": True},
    ]

    selector = MetamorphicCanarySelector(history, k=5)
    assert selector._scores["task_flaky"] == 1.0
    assert selector._scores["task_med"] == 0.5
    assert selector._scores["task_solid"] == 0.0

    available = ["task_flaky", "task_med", "task_solid", "task_extra1", "task_extra2", "task_extra3"]
    selected = selector.select(available, seed=42)

    assert len(selected) == 5
    # The most sensitive tests must be prioritized in top
    assert selected[0] == "task_flaky"
    assert selected[1] == "task_med"


def test_canary_selector_fallback_when_few_tests():
    selector = MetamorphicCanarySelector([], k=10)
    tests = ["t1", "t2", "t3"]
    selected = selector.select(tests)
    assert set(selected) == set(tests)


def test_canary_selector_overhead_reduction_efficiency():
    # Test suite of 40 held-out tasks
    available_tests = [f"test_task_{i:03d}" for i in range(40)]
    selector = MetamorphicCanarySelector([], k=10)

    report = selector.efficiency_report(available_tests)
    assert report["total_available"] == 40
    assert report["selected_canaries"] == 10
    # 10 out of 40 selected -> 75% overhead reduction
    assert report["overhead_reduction_pct"] == 75.0
    assert report["estimated_speedup"] == 4.0


def test_differential_canary_testing_rollback_on_single_regression():
    """Verify that a single test flipping from pass -> fail triggers atomic rollback."""
    from sage.adapters.reflection_agent import ReflectionAgentAdapter
    from sage.adapters.wrapper import VerifierAgentWrapper
    from sage.adapters.base import EvolutionFeedback

    base = ReflectionAgentAdapter()

    # Pre-mutation state: both test_A and test_B pass
    pre_canary_results = {"test_task_A": 1.0, "test_task_B": 1.0}
    # Post-mutation state: test_A still passes, but test_B regresses to 0.0
    post_canary_results = {"test_task_A": 1.0, "test_task_B": 0.0}

    current_state_results = pre_canary_results

    def mock_canary_suite(state):
        return current_state_results

    wrapper = VerifierAgentWrapper(
        base,
        group="G7",
        canary_suite_fn=mock_canary_suite,
    )

    # First cycle: establish healthy baseline
    fb1 = EvolutionFeedback(cycle=1, success_rate=1.0, total_tasks=2, safety_violations=[])
    outcome1 = wrapper.apply_evolution(fb1)
    assert outcome1.status == "accepted"
    assert wrapper.version == "agent_v1"

    # Second cycle: mutation causes test_B to regress (flip pass -> fail)
    current_state_results = post_canary_results
    fb2 = EvolutionFeedback(cycle=2, success_rate=0.5, total_tasks=2, safety_violations=[])
    outcome2 = wrapper.apply_evolution(fb2)

    # Must trigger rollback because of the single regression on test_task_B
    assert outcome2.status == "rolled_back"
    assert "test_task_B" in outcome2.rationale
    assert wrapper.version == "agent_v1"  # Rolled back to previous accepted checkpoint


def test_differential_canary_testing_accepts_clean_evolution():
    """Verify that mutations without pass->fail flips are accepted."""
    from sage.adapters.reflection_agent import ReflectionAgentAdapter
    from sage.adapters.wrapper import VerifierAgentWrapper
    from sage.adapters.base import EvolutionFeedback

    base = ReflectionAgentAdapter()

    # Pre: test_A passes, test_B fails
    # Post: test_A passes, test_B passes (improvement, no regressions)
    current_canary_results = {"test_task_A": 1.0, "test_task_B": 0.0}

    def mock_canary_suite(state):
        return current_canary_results

    wrapper = VerifierAgentWrapper(
        base,
        group="G7",
        canary_suite_fn=mock_canary_suite,
    )

    fb1 = EvolutionFeedback(cycle=1, success_rate=0.5, total_tasks=2, safety_violations=[])
    outcome1 = wrapper.apply_evolution(fb1)
    assert outcome1.status == "accepted"

    # Cycle 2: test_B improves from 0.0 to 1.0
    current_canary_results = {"test_task_A": 1.0, "test_task_B": 1.0}
    fb2 = EvolutionFeedback(cycle=2, success_rate=1.0, total_tasks=2, safety_violations=[])
    outcome2 = wrapper.apply_evolution(fb2)
    assert outcome2.status == "accepted"
    assert outcome2.new_version == "agent_v2"


def test_property_based_canary_fuzzing_with_hypothesis():
    """Verify that Hypothesis property-based fuzzing catches subtle algorithmic bugs."""
    from sage.guardrails.canary_selector import PropertyBasedCanaryFuzzer

    # 1. Correct solver passes metamorphic sort & search invariants
    def correct_solver(task_name, payload):
        if task_name == "sort":
            return sorted(payload)
        elif task_name == "search":
            arr, target = payload
            try:
                return arr.index(target)
            except ValueError:
                return -1
        return None

    assert PropertyBasedCanaryFuzzer.fuzz_sort_invariant(correct_solver, max_examples=25) is True
    assert PropertyBasedCanaryFuzzer.fuzz_search_invariant(correct_solver, max_examples=25) is True

    scores = PropertyBasedCanaryFuzzer.evaluate_property_canaries(correct_solver, max_examples=15)
    assert scores["property_canary_sort"] == 1.0
    assert scores["property_canary_search"] == 1.0

    # 2. Buggy solver that drops duplicates in sort is caught by Hypothesis
    def buggy_solver(task_name, payload):
        if task_name == "sort":
            # Bug: drops duplicate elements (violates sort(x) == sorted(x))
            return sorted(list(set(payload)))
        elif task_name == "search":
            arr, target = payload
            try:
                return arr.index(target)
            except ValueError:
                return -1
        return None

    assert PropertyBasedCanaryFuzzer.fuzz_sort_invariant(buggy_solver, max_examples=25) is False
    buggy_scores = PropertyBasedCanaryFuzzer.evaluate_property_canaries(buggy_solver, max_examples=15)
    assert buggy_scores["property_canary_sort"] == 0.0

    # 3. Direct Hypothesis test function decorator
    from sage.guardrails.canary_selector import make_canary_sort_invariant
    canary_sort_test = make_canary_sort_invariant(correct_solver)
    canary_sort_test()  # Should pass cleanly

    buggy_canary_test = make_canary_sort_invariant(buggy_solver)
    with pytest.raises((AssertionError, Exception)):
        buggy_canary_test()


def test_metamorphic_canary_selector_integration_with_wrapper():
    """Verify that VerifierAgentWrapper uses MetamorphicCanarySelector to filter canaries."""
    from sage.adapters.reflection_agent import ReflectionAgentAdapter
    from sage.adapters.wrapper import VerifierAgentWrapper
    from sage.adapters.base import EvolutionFeedback

    base = ReflectionAgentAdapter()

    history = [
        {"task_id": "sensitive_task_1", "passed_before": True, "passed_after": False},
        {"task_id": "sensitive_task_2", "passed_before": True, "passed_after": False},
        {"task_id": "stable_task_3", "passed_before": True, "passed_after": True},
    ]
    selector = MetamorphicCanarySelector(history=history, k=3)

    # Full suite has 10 tasks
    full_suite = {f"task_{i}": 1.0 for i in range(10)}
    full_suite["sensitive_task_1"] = 1.0
    full_suite["sensitive_task_2"] = 1.0

    def mock_full_suite(state):
        return dict(full_suite)

    wrapper = VerifierAgentWrapper(
        base,
        group="G7",
        canary_selector=selector,
        canary_suite_fn=mock_full_suite,
    )

    # _run_canary_suite must filter down to k=3 tests including the top sensitive ones
    selected_results = wrapper._run_canary_suite("agent_v0")
    assert len(selected_results) == 3
    assert "sensitive_task_1" in selected_results
    assert "sensitive_task_2" in selected_results



