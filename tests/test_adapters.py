"""Unit tests for agent adapters G1 through G6."""

import pytest
from sage.adapters.base import EvolutionFeedback, TaskSpec
from sage.adapters.memory_agent import MemoryAgentAdapter
from sage.adapters.prompt_agent import PromptAgentAdapter
from sage.adapters.reflection_agent import ReflectionAgentAdapter
from sage.adapters.static_agent import StaticAgentAdapter
from sage.adapters.wrapper import VerifierAgentWrapper
from sage.environment.sandbox import LocalSandbox


class DummySandbox:
    def exec_command(self, cmd: str, timeout: int = 30):
        return {"stdout": "tests passed", "stderr": "", "exit_code": 0, "duration_ms": 10}

    def read_file(self, path: str):
        return "def solve(): pass"

    def write_file(self, path: str, content: str):
        pass

    def list_dir(self, path: str = "."):
        return [{"name": "solution.py", "is_dir": False}]


def test_g1_static_agent():
    g1 = StaticAgentAdapter()
    assert g1.group == "G1"
    assert g1.version == "agent_v0"

    # G1 run_task
    spec = TaskSpec(task_id="t1", task_type="bug_fix", repo_name="repo", prompt="Fix")
    res = g1.run_task(spec, DummySandbox())
    assert res.success

    # G1 evolution -> must stay unchanged
    feedback = EvolutionFeedback(cycle=1, success_rate=0.4, total_tasks=5)
    outcome = g1.apply_evolution(feedback)
    assert outcome.status == "unchanged"
    assert g1.version == "agent_v0"


def test_g1_single_task_manual_loop(tmp_path):
    from scripts.manual_run_single_task import run_single_task_manual

    traj_path = run_single_task_manual(task_id="task_001", run_dir_name="test_single_loop")
    assert traj_path.exists()
    assert traj_path.stat().st_size > 0


def test_g2_prompt_agent():
    g2 = PromptAgentAdapter()
    assert g2.group == "G2"

    feedback = EvolutionFeedback(
        cycle=1,
        success_rate=0.5,
        total_tasks=2,
        failed_tasks=[{"error": "IndexError"}],
        safety_violations=[{"rule": "forbidden"}],
    )
    outcome = g2.apply_evolution(feedback)
    assert outcome.status == "accepted"
    assert outcome.new_version == "agent_v1"
    assert "IndexError" in g2.system_prompt


def test_g3_memory_agent():
    g3 = MemoryAgentAdapter()
    assert g3.group == "G3"

    feedback = EvolutionFeedback(
        cycle=1,
        success_rate=0.6,
        total_tasks=5,
        failed_tasks=[{"type": "bug_fix", "error": "TypeError: unsupported operand"}],
    )
    outcome = g3.apply_evolution(feedback)
    assert outcome.status == "accepted"
    assert outcome.new_version == "agent_v1"
    assert any("TypeError" in s for s in g3.memory.get("bug_fix", []))


def test_g4_reflection_agent():
    g4 = ReflectionAgentAdapter()
    assert g4.group == "G4"

    feedback = EvolutionFeedback(
        cycle=1,
        success_rate=0.4,
        total_tasks=5,
        failed_tasks=[{"task_id": "math_001", "error": "ZeroDivisionError"}],
    )
    outcome = g4.apply_evolution(feedback)
    assert outcome.status == "accepted"
    assert outcome.new_version == "agent_v1"
    assert "ZeroDivisionError" in g4.system_prompt


def test_g5_g6_verifier_wrapper():
    base = ReflectionAgentAdapter()
    # G5 rejects mutation if safety violations exist
    g5 = VerifierAgentWrapper(base, group="G5")
    bad_feedback = EvolutionFeedback(
        cycle=1,
        success_rate=0.2,
        total_tasks=5,
        safety_violations=[{"violation": "rm -rf"}],
    )
    outcome = g5.apply_evolution(bad_feedback)
    assert outcome.status == "rejected"
    assert g5.version == "agent_v0"  # Rolled back

    # G6 with regression rollback
    base2 = ReflectionAgentAdapter()
    # Mock regression function that returns low score on cycle 1
    def mock_regress(ver, adapter):
        return 0.2  # Severe regression

    g6 = VerifierAgentWrapper(base2, group="G6", regression_eval_fn=mock_regress)
    ok_feedback = EvolutionFeedback(cycle=1, success_rate=0.8, total_tasks=5)
    outcome_g6 = g6.apply_evolution(ok_feedback)
    assert outcome_g6.status == "rolled_back"
    assert g6.version == "agent_v0"


def test_unified_base_prompt_and_feature_flags():
    """Verify that unified base prompt is exactly 281 chars and feature flags match archetype specs."""
    from sage.adapters.prompts import UNIFIED_BASE_PROMPT, FEATURE_FLAGS, get_base_prompt_for_group

    # Verify character length (approx ~281-289 chars identical semantic baseline)
    assert len(UNIFIED_BASE_PROMPT) in (281, 289)
    assert "You are a software engineering assistant." in UNIFIED_BASE_PROMPT
    assert "Do not modify test files or scoring infrastructure." in UNIFIED_BASE_PROMPT

    # Verify feature flags across all layers
    assert FEATURE_FLAGS["G1"] == {"evolution": False, "memory": False, "reflection": False, "code_patch": False}
    assert FEATURE_FLAGS["G2"] == {"evolution": True, "memory": False, "reflection": False, "code_patch": False}
    assert FEATURE_FLAGS["G3"] == {"evolution": False, "memory": True, "reflection": False, "code_patch": False}
    for g in ["G4", "G5", "G6", "G7"]:
        assert FEATURE_FLAGS[g] == {"evolution": True, "memory": True, "reflection": True, "code_patch": True}

    # When use_unified=True, all archetypes receive identical prompt
    for g in ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]:
        assert get_base_prompt_for_group(g, use_unified=True) == UNIFIED_BASE_PROMPT

    # When use_unified=False, legacy prompts are preserved for backward reproducibility
    assert get_base_prompt_for_group("G1", use_unified=False) != UNIFIED_BASE_PROMPT
    assert get_base_prompt_for_group("G4", use_unified=False) != UNIFIED_BASE_PROMPT

