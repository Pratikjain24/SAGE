"""Test suite for workspace pruning, disk conservation, and memory hygiene in ExperimentOrchestrator."""

from pathlib import Path
import pytest
from sage.config.models import ExperimentConfig, TasksSplitConfig
from sage.environment.task_loader import TaskLoader
from sage.runner.orchestrator import ExperimentOrchestrator


def test_orchestrator_workspace_pruning_enabled(tmp_path: Path):
    """Verify that when prune_workspaces=True, task workspace directories are removed after scoring."""
    loader = TaskLoader(Path("tasks/tasks_index.json"))
    config = ExperimentConfig(
        name="prune_test",
        cycles=1,
        seeds=[42],
        groups=["G1"],
        tasks=TasksSplitConfig(train=1, test=1),
        max_tasks_per_cycle=1,
    )

    runs_dir = tmp_path / "runs"
    orchestrator = ExperimentOrchestrator(
        config=config,
        task_loader=loader,
        runs_dir=runs_dir,
        prune_workspaces=True,
    )
    out_dir = orchestrator.run_experiment(run_id="pruned_run")

    # Trajectory must be recorded
    assert (out_dir / "trajectory.jsonl").exists()

    # Scratch directory for task workspace should be empty or deleted
    scratch_dir = out_dir / "scratch" / "seed_42"
    if scratch_dir.exists():
        ws_dirs = list(scratch_dir.iterdir())
        assert len(ws_dirs) == 0, f"Expected 0 retained workspaces, found: {ws_dirs}"


def test_orchestrator_workspace_retention_disabled(tmp_path: Path):
    """Verify that when prune_workspaces=False, task workspace directories are retained."""
    loader = TaskLoader(Path("tasks/tasks_index.json"))
    config = ExperimentConfig(
        name="retain_test",
        cycles=1,
        seeds=[42],
        groups=["G1"],
        tasks=TasksSplitConfig(train=1, test=1),
        max_tasks_per_cycle=1,
    )

    runs_dir = tmp_path / "runs"
    orchestrator = ExperimentOrchestrator(
        config=config,
        task_loader=loader,
        runs_dir=runs_dir,
        prune_workspaces=False,
    )
    out_dir = orchestrator.run_experiment(run_id="retained_run")

    assert (out_dir / "trajectory.jsonl").exists()
    scratch_dir = out_dir / "scratch" / "seed_42"
    assert scratch_dir.exists()
    assert len(list(scratch_dir.iterdir())) >= 1
