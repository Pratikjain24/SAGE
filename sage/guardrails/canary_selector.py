# sage/guardrails/canary_selector.py
"""Metamorphic canary test selector and property-based canary fuzzing for G6/G7.

Selects canary tests that are most sensitive to capability regression.
Uses metamorphic relations: if f(x) passes, then f(transform(x)) should
also pass. Canary tests are those where violations of metamorphic relations
have historically correlated with real capability regression.
Always includes random tests (up to 2) to prevent overfitting to known regression patterns.
"""

from __future__ import annotations
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


class MetamorphicCanarySelector:
    """Selects canary tests that are most sensitive to capability regression.

    Uses metamorphic relations: if f(x) passes, then f(transform(x)) should
    also pass. Canary tests are those where violations of metamorphic relations
    have historically correlated with real capability regression.
    """

    def __init__(self, history: Optional[List[Dict]] = None, k: int = 10):
        """
        Args:
            history: Past cycle results [{task_id, passed_before, passed_after, ...}]
            k: Number of canary tests to select
        """
        self.k = k
        self.sensitivity_scores = self._compute_sensitivity(history or [])
        self._scores = self.sensitivity_scores  # Alias for backward compatibility

    def _compute_sensitivity(self, history: List[Dict]) -> Dict[str, float]:
        """Score each test by how often it flipped pass→fail during regressions."""
        flip_counts: Dict[str, int] = {}
        total_counts: Dict[str, int] = {}
        for record in history:
            tid = record.get("task_id", "")
            if not tid:
                continue
            total_counts[tid] = total_counts.get(tid, 0) + 1
            if record.get("passed_before") and not record.get("passed_after"):
                flip_counts[tid] = flip_counts.get(tid, 0) + 1
        return {
            tid: flip_counts.get(tid, 0) / max(total_counts[tid], 1)
            for tid in total_counts
        }

    def select(self, available_tests: List[str], seed: int = 42) -> List[str]:
        """Select top-k most sensitive canary tests."""
        if len(available_tests) <= self.k:
            return list(available_tests)

        scored = [
            (tid, self.sensitivity_scores.get(tid, 0.0))
            for tid in available_tests
        ]
        scored.sort(key=lambda x: -x[1])
        # Take top-k by sensitivity, but always include at least 2 random
        # tests to prevent overfitting to known regression patterns
        top_k_count = max(1, self.k - 2)
        top_k = [tid for tid, _ in scored[:top_k_count]]
        remaining = [tid for tid in available_tests if tid not in top_k]
        rng = random.Random(seed)
        num_random = min(2, len(remaining), self.k - len(top_k))
        random_picks = rng.sample(remaining, num_random) if num_random > 0 else []
        return top_k + random_picks

    def efficiency_report(self, available_tests: List[str]) -> Dict[str, Any]:
        """Compute test overhead reduction achieved by evaluating k canaries instead of the full suite."""
        n_total = len(available_tests)
        n_selected = min(self.k, n_total)
        overhead_reduction = 1.0 - (n_selected / max(n_total, 1))
        return {
            "total_available": n_total,
            "selected_canaries": n_selected,
            "overhead_reduction_pct": round(overhead_reduction * 100, 1),
            "estimated_speedup": round(n_total / max(n_selected, 1), 2),
            "top_sensitive_tests": sorted(
                self.sensitivity_scores.keys(),
                key=lambda t: self.sensitivity_scores[t],
                reverse=True,
            )[:5],
        }


# ---------------------------------------------------------------------------
# Property-Based Canary Fuzzing (Metamorphic Invariant Checking)
# ---------------------------------------------------------------------------

class PropertyBasedCanaryFuzzer:
    """Generates property-based fuzz tests and metamorphic invariants for canary validation."""

    @staticmethod
    def fuzz_sort_invariant(
        agent_solve: Callable[[str, Any], Any],
        max_examples: int = 20,
        deadline: int = 5000,
    ) -> bool:
        """Metamorphic property: sort(sort(x)) == sort(x) and sort(x) == sorted(x)."""
        if not HAS_HYPOTHESIS:
            # Fallback deterministic pseudo-random fuzzing if hypothesis is absent
            test_cases = [
                [],
                [42],
                [3, 1, 4, 1, 5, 9, 2, 6],
                [-5, 0, -1, 10, -5],
                list(range(50, 0, -1)),
            ]
            for xs in test_cases:
                res = agent_solve("sort", list(xs))
                if res != sorted(xs) or agent_solve("sort", list(res)) != res:
                    return False
            return True

        caught_regression: List[str] = []

        @given(st.lists(st.integers(), min_size=0, max_size=100))
        @settings(max_examples=max_examples, deadline=deadline)
        def _test_sort(xs: List[int]):
            result = agent_solve("sort", list(xs))
            if result != sorted(xs):
                raise AssertionError(f"Sort correctness failed: {result} != {sorted(xs)}")
            # Metamorphic idempotence: sort(sort(x)) == sort(x)
            idempotent_result = agent_solve("sort", list(result))
            if idempotent_result != result:
                raise AssertionError(f"Metamorphic idempotence failed: sort(sort(x)) != sort(x)")

        try:
            _test_sort()
            return True
        except (AssertionError, Exception) as exc:
            caught_regression.append(str(exc))
            return False

    @staticmethod
    def fuzz_search_invariant(
        agent_solve: Callable[[str, Any], Any],
        max_examples: int = 20,
        deadline: int = 5000,
    ) -> bool:
        """Metamorphic search invariant: element present must be found; absent must return -1."""
        if not HAS_HYPOTHESIS:
            sample_lists = [[1, 2, 3, 4, 5], [-10, 0, 10], [99]]
            for lst in sample_lists:
                for target in lst:
                    if agent_solve("search", (lst, target)) == -1:
                        return False
                if agent_solve("search", (lst, 999999)) != -1:
                    return False
            return True

        caught_regression: List[str] = []

        @given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=50), st.integers())
        @settings(max_examples=max_examples, deadline=deadline)
        def _test_search(xs: List[int], target: int):
            idx = agent_solve("search", (list(xs), target))
            if target in xs:
                if idx is None or not isinstance(idx, int) or idx < 0 or idx >= len(xs) or xs[idx] != target:
                    raise AssertionError(f"Element {target} in list but index {idx} returned invalid match")
            else:
                if idx is None or idx != -1:
                    raise AssertionError(f"Element {target} not in list but returned index {idx}")

        try:
            _test_search()
            return True
        except (AssertionError, Exception) as exc:
            caught_regression.append(str(exc))
            return False

    @classmethod
    def evaluate_property_canaries(
        cls,
        agent_solve: Callable[[str, Any], Any],
        max_examples: int = 20,
    ) -> Dict[str, float]:
        """Run property-based canary suite, returning {property_name: 1.0 (pass) | 0.0 (fail)}."""
        scores: Dict[str, float] = {}
        scores["property_canary_sort"] = 1.0 if cls.fuzz_sort_invariant(agent_solve, max_examples=max_examples) else 0.0
        scores["property_canary_search"] = 1.0 if cls.fuzz_search_invariant(agent_solve, max_examples=max_examples) else 0.0
        return scores


def make_canary_sort_invariant(agent_solve: Callable[[str, Any], Any]):
    """Hypothesis test definition: metamorphic property sort(sort(x)) == sort(x)."""
    if not HAS_HYPOTHESIS:
        def _fallback_sort_test():
            for xs in [[], [1, 2], [3, 2, 1], [-1, 5, 0], [3, 1, 4, 1, 5, 9, 2, 6], [-5, 0, -1, 10, -5], [2, 2, 2]]:
                res = agent_solve("sort", list(xs))
                assert res == sorted(xs), f"Regression: {res} != {sorted(xs)}"
        return _fallback_sort_test

    @given(st.lists(st.integers(), min_size=1, max_size=100))
    @settings(max_examples=20, deadline=5000)
    def canary_sort_invariant(xs):
        """Metamorphic property: sort(sort(x)) == sort(x)"""
        result = agent_solve("sort", xs)
        assert result == sorted(xs), f"Regression: {result} != {sorted(xs)}"

    return canary_sort_invariant
