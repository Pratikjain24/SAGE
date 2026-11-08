# sage/tasks/difficulty.py
"""IRT-based task difficulty estimation using the Rasch 1PL model.

The Rasch model assigns each task a difficulty parameter β from G1's
empirical pass rate across seeds:
    β = -log(p / (1-p))   where p = mean pass rate across seeds

Higher β → harder task. The stratified_split() method ensures the
train and test sets have matched difficulty distributions.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple


class IRTDifficultyEstimator:
    """Rasch 1PL difficulty estimator from G1 baseline results."""

    def __init__(self, g1_results: Dict[str, List[bool]]):
        """
        Args:
            g1_results: {task_id: [passed_seed42, passed_seed43, ..., passed_seed46]}
        """
        self.difficulties: Dict[str, float] = {}
        for task_id, outcomes in g1_results.items():
            p = float(np.mean(outcomes))
            p = float(np.clip(p, 0.01, 0.99))
            self.difficulties[task_id] = float(-np.log(p / (1.0 - p)))

    def stratified_split(
        self,
        task_ids: List[str],
        train_ratio: float = 0.6,
        n_strata: int = 4,
        seed: int = 42,
    ) -> Tuple[List[str], List[str]]:
        """Return (train_tasks, test_tasks) with matched difficulty distributions."""
        rng = np.random.RandomState(seed)
        sorted_tasks = sorted(task_ids, key=lambda t: self.difficulties.get(t, 0.0))

        strata_size = max(1, len(sorted_tasks) // n_strata)
        strata = [
            sorted_tasks[i * strata_size : (i + 1) * strata_size]
            for i in range(n_strata)
        ]
        strata[-1].extend(sorted_tasks[n_strata * strata_size :])

        train, test = [], []
        for stratum in strata:
            arr = list(stratum)
            rng.shuffle(arr)
            n_train = int(len(arr) * train_ratio)
            train.extend(arr[:n_train])
            test.extend(arr[n_train:])

        return train, test

    def balance_summary(self, train_tasks: List[str], test_tasks: List[str]) -> Dict[str, float]:
        """Compute distribution metrics between train and test splits to prove difficulty parity."""
        train_betas = [self.difficulties.get(t, 0.0) for t in train_tasks]
        test_betas = [self.difficulties.get(t, 0.0) for t in test_tasks]
        train_mean = float(np.mean(train_betas)) if train_betas else 0.0
        test_mean = float(np.mean(test_betas)) if test_betas else 0.0
        return {
            "train_mean_beta": train_mean,
            "test_mean_beta": test_mean,
            "delta_mean_beta": abs(train_mean - test_mean),
            "train_std_beta": float(np.std(train_betas)) if train_betas else 0.0,
            "test_std_beta": float(np.std(test_betas)) if test_betas else 0.0,
        }

    def get_difficulty_report(self) -> Dict:
        """Summary statistics for the task suite."""
        betas = list(self.difficulties.values())
        if not betas:
            return {"n_tasks": 0}
        return {
            "n_tasks": len(betas),
            "mean_difficulty": float(np.mean(betas)),
            "std_difficulty": float(np.std(betas)),
            "easiest": min(self.difficulties, key=self.difficulties.get),
            "hardest": max(self.difficulties, key=self.difficulties.get),
            "quartiles": {
                "Q1": float(np.percentile(betas, 25)),
                "Q2": float(np.percentile(betas, 50)),
                "Q3": float(np.percentile(betas, 75)),
            },
        }

    def report(self) -> Dict:
        """Backward-compatible report wrapper."""
        rep = self.get_difficulty_report()
        if rep.get("n_tasks", 0) > 0:
            rep["mean_beta"] = rep["mean_difficulty"]
            rep["std_beta"] = rep["std_difficulty"]
            rep["easiest_task"] = rep["easiest"]
            rep["hardest_task"] = rep["hardest"]
        return rep

