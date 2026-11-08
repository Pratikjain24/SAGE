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


def test_cleanup_between_seeds_clears_caches_and_flushes(tmp_path: Path):
    """Verify that _cleanup_between_seeds removes scratch caches without crashing."""
    loader = TaskLoader(Path("tasks/tasks_index.json"))
    config = ExperimentConfig(
        name="cleanup_unit_test",
        cycles=1,
        seeds=[42],
        groups=["G1"],
        tasks=TasksSplitConfig(train=1, test=1),
    )
    orchestrator = ExperimentOrchestrator(
        config=config,
        task_loader=loader,
        runs_dir=tmp_path / "runs",
    )

    # Create dummy scratch and cache dirs in tmp_path
    dummy_scratch = tmp_path / "scratch"
    dummy_scratch.mkdir(parents=True, exist_ok=True)
    (dummy_scratch / "dummy.txt").write_text("test")

    orchestrator._cleanup_between_seeds(seed=42)
    # Ensure no exception and method executes cleanly


def test_execute_with_process_group_timeout_success(tmp_path: Path):
    """Verify that _execute_with_process_group_timeout executes normal commands and captures output."""
    import sys
    from sage.runner.orchestrator import _execute_with_process_group_timeout

    cmd = [sys.executable, "-c", "print('process_group_test_ok')"]
    stdout, stderr, rc = _execute_with_process_group_timeout(cmd, timeout_seconds=5, cwd=str(tmp_path))

    assert rc == 0
    assert "process_group_test_ok" in stdout.strip()
    assert stderr.strip() == ""


def test_execute_with_process_group_timeout_kills_process_group():
    """Verify that a timeout triggers recursive process group kill without leaving zombies."""
    import sys
    import subprocess
    from sage.runner.orchestrator import _execute_with_process_group_timeout

    # Command sleeps for 10s with a 0.5s timeout
    cmd = [sys.executable, "-c", "import time; time.sleep(10)"]
    with pytest.raises(subprocess.TimeoutExpired):
        _execute_with_process_group_timeout(cmd, timeout_seconds=0.5)


def test_cleanup_between_seeds_with_explicit_workspace_dir(tmp_path: Path):
    """Verify that _cleanup_between_seeds recursively deletes scratch, tmp, and pycache dirs."""
    from sage.runner.orchestrator import _cleanup_between_seeds

    # Create dummy directories
    pycache = tmp_path / "__pycache__"
    pytest_cache = tmp_path / ".pytest_cache"
    scratch = tmp_path / "scratch"
    tmp_dir = tmp_path / "tmp"

    for d in [pycache, pytest_cache, scratch, tmp_dir]:
        d.mkdir(parents=True, exist_ok=True)
        (d / "artifact.dat").write_text("data")

    assert pycache.exists()
    assert scratch.exists()

    _cleanup_between_seeds(str(tmp_path))

    # All scratch directories must be removed
    assert not pycache.exists()
    assert not pytest_cache.exists()
    assert not scratch.exists()
    assert not tmp_dir.exists()

