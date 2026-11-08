"""Unit tests for IRT difficulty estimator and stratified task splitter (FIX-18)."""

import pytest
from sage.tasks.difficulty import IRTDifficultyEstimator


def test_irt_difficulty_estimator_basic():
    # Setup 10 tasks with known pass rates
    results = {
        "task_easy_1": [True, True, True, True, True],     # p = 1.0 (clipped to 0.99)
        "task_easy_2": [True, True, True, True, False],    # p = 0.8
        "task_med_1":  [True, True, False, False, True],   # p = 0.6
        "task_med_2":  [False, True, False, True, False],  # p = 0.4
        "task_hard_1": [False, False, False, True, False], # p = 0.2
        "task_hard_2": [False, False, False, False, False],# p = 0.0 (clipped to 0.01)
    }

    estimator = IRTDifficultyEstimator(results)

    # Higher beta = harder task
    assert estimator.difficulties["task_easy_1"] < estimator.difficulties["task_med_1"]
    assert estimator.difficulties["task_med_1"] < estimator.difficulties["task_hard_1"]
    assert estimator.difficulties["task_hard_1"] < estimator.difficulties["task_hard_2"]

    rep = estimator.report()
    assert rep["n_tasks"] == 6
    assert rep["easiest_task"] == "task_easy_1"
    assert rep["hardest_task"] == "task_hard_2"
    assert "mean_beta" in rep
    assert "quartiles" in rep

    # Test get_difficulty_report() schema matching IRT spec
    diff_rep = estimator.get_difficulty_report()
    assert diff_rep["n_tasks"] == 6
    assert diff_rep["easiest"] == "task_easy_1"
    assert diff_rep["hardest"] == "task_hard_2"
    assert "mean_difficulty" in diff_rep
    assert "std_difficulty" in diff_rep
    assert "quartiles" in diff_rep
    assert "Q1" in diff_rep["quartiles"]
    assert "Q2" in diff_rep["quartiles"]
    assert "Q3" in diff_rep["quartiles"]


def test_irt_stratified_split():
    # 20 synthetic tasks
    results = {
        f"task_{i}": [i > 5, i > 10, i > 15, i > 8, i > 12]
        for i in range(20)
    }
    estimator = IRTDifficultyEstimator(results)
    task_ids = list(results.keys())

    train, test = estimator.stratified_split(task_ids, train_ratio=0.6, n_strata=4, seed=42)

    assert len(train) + len(test) == len(task_ids)
    assert set(train).isdisjoint(set(test))
    assert len(train) == 12
    assert len(test) == 8

    balance = estimator.balance_summary(train, test)
    assert "delta_mean_beta" in balance
    # The stratified split should keep mean difficulty difference small
    assert balance["delta_mean_beta"] < 0.5


