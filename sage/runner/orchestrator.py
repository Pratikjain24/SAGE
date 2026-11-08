"""Experiment Orchestrator: Multi-seed, multi-group, recursive evolutionary benchmark runner.

This module re-exports the experiment orchestrator components for backward compatibility.
The architecture is modularized into:
- sage.runner.task_executor: Single-task execution, sandbox, retry, and scoring
- sage.runner.cycle_manager: Cycle iteration, task dispatching, and evolution triggering
- sage.runner.experiment: Experiment matrix orchestration, crash recovery, and budget tracking
"""

from __future__ import annotations
import gc
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _execute_with_process_group_timeout(cmd: str | List[str], timeout_seconds: float | int, cwd: Optional[str] = None) -> Tuple[str, str, int]:
    """Execute command with proper process group termination.
    
    Prevents zombie child processes (such as vLLM workers, pytest runners) from
    surviving task timeouts, preventing GPU memory fragmentation and cascade slowdown.
    """
    kwargs: Dict[str, Any] = {}
    if os.name == "posix":
        kwargs["preexec_fn"] = os.setsid
    elif os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        cmd,
        shell=isinstance(cmd, str),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
        stdout_str = stdout.decode("utf-8", errors="replace") if isinstance(stdout, bytes) else (stdout or "")
        stderr_str = stderr.decode("utf-8", errors="replace") if isinstance(stderr, bytes) else (stderr or "")
        return stdout_str, stderr_str, proc.returncode
    except subprocess.TimeoutExpired:
        # Kill entire process group, not just parent
        if os.name == "posix":
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass
        else:
            try:
                proc.kill()
            except Exception:
                pass
            # On Windows, also kill child processes
            try:
                subprocess.run(
                    f"taskkill /F /T /PID {proc.pid}",
                    shell=True,
                    capture_output=True,
                    timeout=5,
                )
            except Exception:
                pass
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
        raise


def _cleanup_between_seeds(workspace_dir: str) -> None:
    """Clean scratch state between seeds to prevent cross-contamination."""
    scratch_dirs = ["__pycache__", ".pytest_cache", "scratch", "tmp", ".hypothesis"]
    for d in scratch_dirs:
        target = os.path.join(workspace_dir, d)
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
        # Also clean recursively within workspace
        try:
            for p in Path(workspace_dir).rglob(d):
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
        except Exception:
            pass

    # Force GPU memory release
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
            torch.cuda.synchronize()
    except Exception:
        pass

    # Give OS time to reclaim resources
    gc.collect()
    time.sleep(2)


# Import modular orchestrator subcomponents
from sage.runner.cycle_manager import ARCHETYPE_DESCRIPTIONS, CycleManager
from sage.runner.experiment import ExperimentOrchestrator
from sage.runner.task_executor import TaskExecutor

# Attach helper to ExperimentOrchestrator class for convenience
ExperimentOrchestrator._execute_with_process_group_timeout = staticmethod(_execute_with_process_group_timeout)

__all__ = [
    "ARCHETYPE_DESCRIPTIONS",
    "ExperimentOrchestrator",
    "TaskExecutor",
    "CycleManager",
    "_execute_with_process_group_timeout",
    "_cleanup_between_seeds",
]
