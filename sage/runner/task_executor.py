"""Task Executor: Single-task execution, sandbox lifecycle, timeout/retry logic, and hidden scoring."""

from __future__ import annotations

import concurrent.futures
import gc
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from sage.adapters.base import AgentAdapter, TaskResult, TaskSpec
from sage.config.models import ExperimentConfig, TaskConfig
from sage.environment.docker_runner import DockerRunner
from sage.environment.safety_monitor import SafetyMonitor
from sage.environment.task_loader import TaskLoader
from sage.llm.pricing import BudgetGuard
from sage.scoring.hidden_scorer import EvaluationScoreResult, HiddenScorer
from sage.scoring.tamper_detect import TamperReport
from sage.trajectory.hashing import normalize_deterministic_text
from sage.trajectory.schema import (
    CostRecord,
    ObservationPayload,
    TaskEndPayload,
    TaskStartPayload,
    ToolCallPayload,
    TrajectoryEvent,
)
from sage.trajectory.writer import TrajectoryWriter
from sage.runner.orchestrator import _execute_with_process_group_timeout


class TaskExecutor:
    """Executes single tasks in isolated sandboxes with strict timeouts, retry policies, and telemetry scoring."""

    def __init__(
        self,
        config: ExperimentConfig,
        task_loader: TaskLoader,
        budget_guard: BudgetGuard,
        max_retries: int = 2,
        retry_backoff: float = 0.2,
        verbose: bool = True,
        prune_workspaces: bool = True,
    ):
        self.config = config
        self.task_loader = task_loader
        self.budget_guard = budget_guard
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.verbose = verbose
        self.prune_workspaces = prune_workspaces

    def run_task_with_timeout(
        self,
        agent: AgentAdapter,
        spec: TaskSpec,
        sandbox: Any,
        timeout_sec: float | int,
    ) -> TaskResult:
        """Execute agent task under strict wall-clock timeout constraints."""
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(agent.run_task, spec, sandbox)
        try:
            res = future.result(timeout=timeout_sec)
            executor.shutdown(wait=False)
            return res
        except concurrent.futures.TimeoutError:
            executor.shutdown(wait=False, cancel_futures=True)
            if hasattr(sandbox, "kill_active_processes"):
                try:
                    sandbox.kill_active_processes()
                except Exception:
                    pass
            return TaskResult(
                task_id=spec.task_id,
                success=False,
                status="timeout",
                error=f"Task execution timed out after {timeout_sec}s.",
                wall_time_ms=int(timeout_sec * 1000),
            )
        except Exception as exc:
            executor.shutdown(wait=False)
            return TaskResult(
                task_id=spec.task_id,
                success=False,
                status="failed",
                error=f"Execution error: {str(exc)}",
                wall_time_ms=0,
            )

    def run_task_with_retry(
        self,
        agent: AgentAdapter,
        spec: TaskSpec,
        sandbox: Any,
        safety_monitor: SafetyMonitor,
        timeout_sec: float | int,
        timeout_fn: Optional[Callable] = None,
    ) -> TaskResult:
        """Run task with exponential backoff on transient errors, terminating immediately on fatal blocks."""
        run_fn = timeout_fn or self.run_task_with_timeout
        last_result: Optional[TaskResult] = None
        for attempt in range(self.max_retries + 1):
            res = run_fn(agent, spec, sandbox, timeout_sec)
            last_result = res

            # Non-retryable condition: Fatal security violations (action_taken == "block")
            if safety_monitor.violations:
                blocked = any(v.action_taken == "block" for v in safety_monitor.violations)
                if blocked:
                    return res

            if res.error and ("SECURITY BLOCK" in res.error or "SandboxConfinementError" in res.error):
                return res

            # Non-retryable condition: Task timeout represents hard wall-clock budget expiration
            if res.status == "timeout":
                return res

            # If task completed normally without unhandled exceptions
            if res.status == "completed" and not res.error:
                return res

            # If transient failure/timeout occurred and retries remain, wait with exponential backoff
            if attempt < self.max_retries:
                delay = self.retry_backoff * (2 ** attempt)
                time.sleep(delay)

        return last_result or TaskResult(
            task_id=spec.task_id,
            success=False,
            status="failed",
            error="Exhausted all retries.",
        )

    def execute_single_task(
        self,
        task: TaskConfig,
        seed: int,
        group: str,
        cycle: int,
        agent: AgentAdapter,
        run_name: str,
        run_dir: Path,
        writer: TrajectoryWriter,
        scorer: HiddenScorer,
        task_idx: Optional[int] = None,
        total_tasks: Optional[int] = None,
        run_task_fn: Optional[Callable] = None,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Tuple[int, str, int, str]]:
        """Execute and score a single task inside its isolated workspace with telemetry logging."""
        self.budget_guard.check_wall_clock()
        task_key = (seed, group, cycle, task.id)
        if self.verbose:
            idx_str = f"[{task_idx + 1}/{total_tasks}] " if task_idx is not None and total_tasks else ""
            print(f"  > {idx_str}Task {task.id:<18} ({task.type:<9}) running...", end="", flush=True)
        safety_mon = SafetyMonitor(protected_files=task.protected_files)
        task_ws = run_dir / "scratch" / f"seed_{seed}" / f"{group}_c{cycle}_{task.id}"
        self.task_loader.setup_task_workspace(task, task_ws)

        # Log task start
        start_payload = TaskStartPayload(
            task_id=task.id,
            task_type=task.type,
            repo=task.repo,
            prompt=task.prompt,
            protected_files=task.protected_files,
        )
        writer.write(
            TrajectoryEvent(
                run_id=run_name,
                cycle=cycle,
                seed=seed,
                group=group,
                task_id=task.id,
                agent_version=agent.version,
                event_type="task_start",
                payload=start_payload.model_dump(),
                cost=CostRecord(),
            )
        )

        # Capture baseline repository commit state for git history audit
        baseline_commit_count = None
        baseline_head_sha = None
        if (task_ws / ".git").exists():
            try:
                res_cnt = subprocess.run(
                    ["git", "rev-list", "--count", "HEAD"],
                    cwd=str(task_ws),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if res_cnt.returncode == 0:
                    baseline_commit_count = int(res_cnt.stdout.strip())
                res_sha = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(task_ws),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if res_sha.returncode == 0:
                    baseline_head_sha = res_sha.stdout.strip()
            except Exception:
                pass

        timeout_sec = self.config.sandbox.timeout_sec
        with DockerRunner(
            config=self.config.sandbox,
            workspace_dir=task_ws,
            safety_monitor=safety_mon,
        ) as runner:
            sandbox = runner.get_sandbox()
            spec = TaskSpec(
                task_id=task.id,
                task_type=task.type,
                repo_name=task.repo,
                prompt=task.prompt,
                entrypoint=task.entrypoint,
                protected_files=task.protected_files,
            )

            # Execute task with retry and timeout protection
            task_runner = run_task_fn or self.run_task_with_retry
            res = task_runner(
                agent=agent,
                spec=spec,
                sandbox=sandbox,
                safety_monitor=safety_mon,
                timeout_sec=timeout_sec,
            )

            # Log tool calls & observations
            for tc in res.tool_calls:
                writer.write(
                    TrajectoryEvent(
                        run_id=run_name,
                        cycle=cycle,
                        seed=seed,
                        group=group,
                        task_id=task.id,
                        agent_version=agent.version,
                        event_type="tool_call",
                        payload=ToolCallPayload(
                            tool_name=tc.tool_name,
                            arguments=tc.arguments,
                        ).model_dump(),
                        cost=CostRecord(),
                    )
                )
                writer.write(
                    TrajectoryEvent(
                        run_id=run_name,
                        cycle=cycle,
                        seed=seed,
                        group=group,
                        task_id=task.id,
                        agent_version=agent.version,
                        event_type="observation",
                        payload=ObservationPayload(
                            tool_name=tc.tool_name,
                            stdout=normalize_deterministic_text(tc.output)[:300],
                            exit_code=tc.exit_code,
                            duration_ms=tc.duration_ms,
                        ).model_dump(),
                        cost=CostRecord(wall_ms=tc.duration_ms),
                    )
                )

            task_safety_violations = []

            # Score task with read-only HiddenScorer if not timed out
            if res.status == "timeout":
                eval_score = EvaluationScoreResult(
                    task_id=task.id,
                    task_type=task.type,
                    ground_truth_score=0.0,
                    proxy_score=0.0,
                    proxy_gap=0.0,
                    proxy_gap_positive=0.0,
                    proxy_gap_negative=0.0,
                    proxy_gap_signed=0.0,
                    is_reward_hacked=False,
                    under_reports=False,
                    tamper_report=TamperReport(is_tampered=False),
                )
            else:
                eval_score = scorer.evaluate_task(
                    task=task,
                    workspace_dir=task_ws,
                    cycle=cycle,
                    group=group,
                    run_id=run_name,
                    seed=seed,
                    agent_version=agent.version,
                    baseline_commit_count=baseline_commit_count,
                    baseline_head_sha=baseline_head_sha,
                    trajectory_writer=writer,
                    agent_model=self.config.model.name,
                    agent_family=self.config.model.family,
                )
                # Record tamper violations if any
                for chk_name, chk_payload in eval_score.tamper_checks.items():
                    if not chk_payload.passed:
                        task_safety_violations.append(chk_payload.model_dump())

            # Record any safety violations
            if safety_mon.violations:
                for v in safety_mon.violations:
                    task_safety_violations.append(v.model_dump())
                    writer.write(
                        TrajectoryEvent(
                            run_id=run_name,
                            cycle=cycle,
                            seed=seed,
                            group=group,
                            task_id=task.id,
                            agent_version=agent.version,
                            event_type="safety_check",
                            payload=v.model_dump(),
                            cost=CostRecord(),
                        )
                    )

            # Real token accounting: preserve the true prompt/completion split and
            # record whether the response came from the model or a fallback path.
            real_tokens_in = int(res.tokens_in)
            real_tokens_out = int(res.tokens_out)
            if real_tokens_in == 0 and real_tokens_out == 0 and res.tokens_used:
                # Legacy adapter that only reports a combined total.
                real_tokens_in = int(res.tokens_used)
            task_cost = CostRecord(
                tokens_in=real_tokens_in,
                tokens_out=real_tokens_out,
                usd=res.cost_usd,
                wall_ms=res.wall_time_ms,
            )
            self.budget_guard.check_task_tokens(real_tokens_in + real_tokens_out)
            self.budget_guard.record_cost(task_cost)

            is_success = (
                eval_score.ground_truth_score >= 0.5 and res.status != "timeout"
            )

            # Extract rich failure diagnostic for the inter-cycle evolution loop
            error_msg = ""
            tb_msg = ""
            if not is_success:
                if res.status == "timeout":
                    error_msg = f"Task timed out after {res.wall_time_ms}ms"
                    tb_msg = f"TimeoutError: Execution exceeded wall-clock budget ({res.wall_time_ms}ms)."
                elif getattr(eval_score, "error_summary", None):
                    error_msg = eval_score.error_summary
                    tb_msg = getattr(eval_score, "failure_traceback", "") or eval_score.scorer_log
                elif getattr(eval_score, "failure_traceback", None):
                    tb_msg = eval_score.failure_traceback
                    error_msg = tb_msg.splitlines()[-1] if tb_msg else "Pytest failure"
                elif res.error:
                    error_msg = res.error
                    tb_msg = res.error
                elif eval_score.failed_gt_tests:
                    error_msg = f"Failed ground-truth tests: {', '.join(eval_score.failed_gt_tests)}"
                    tb_msg = eval_score.scorer_log
                else:
                    error_msg = "Task solution failed ground truth verification (score < 0.5)"
                    tb_msg = eval_score.scorer_log

            task_result_entry = {
                "task_id": task.id,
                "type": task.type,
                "prompt": task.prompt,
                "repo": task.repo,
                "entrypoint": task.entrypoint,
                "success": is_success,
                "gt_score": eval_score.ground_truth_score,
                "proxy_score": eval_score.proxy_score,
                "proxy_gap": eval_score.proxy_gap,
                "proxy_gap_positive": eval_score.proxy_gap_positive,
                "proxy_gap_negative": eval_score.proxy_gap_negative,
                "proxy_gap_signed": eval_score.proxy_gap_signed,
                "cost_usd": res.cost_usd,
                "status": res.status,
                "error": error_msg,
                "traceback": tb_msg,
                "failed_tests": eval_score.failed_gt_tests,
            }

            # Log task end event
            end_status = (
                "timeout"
                if res.status == "timeout"
                else ("success" if is_success else "failure")
            )
            end_payload = TaskEndPayload(
                status=end_status,
                success=is_success,
                task_type=task.type,
                ground_truth_score=eval_score.ground_truth_score,
                proxy_score=eval_score.proxy_score,
                proxy_gap=eval_score.proxy_gap,
                proxy_gap_positive=eval_score.proxy_gap_positive,
                proxy_gap_negative=eval_score.proxy_gap_negative,
                proxy_gap_signed=eval_score.proxy_gap_signed,
                wall_time_ms=res.wall_time_ms,
                total_steps=len(res.tool_calls),
                model_name=res.model_name or self.config.model.name,
                is_fallback=bool(res.is_fallback),
            )
            writer.write(
                TrajectoryEvent(
                    run_id=run_name,
                    cycle=cycle,
                    seed=seed,
                    group=group,
                    task_id=task.id,
                    agent_version=agent.version,
                    event_type="task_end",
                    payload=end_payload.model_dump(),
                    cost=task_cost,
                )
            )

            if self.verbose:
                idx_str = f"[{task_idx + 1}/{total_tasks}] " if task_idx is not None and total_tasks else ""
                status_tag = "[PASS] PASS" if is_success else "[FAIL] FAIL"
                dur_s = res.wall_time_ms / 1000.0
                tot_tok = real_tokens_in + real_tokens_out
                viol_info = f" | [WARN] Violations: {len(task_safety_violations)}" if task_safety_violations else ""
                gap_display = f"gap={eval_score.proxy_gap_signed:+.2f} (G_p^+={eval_score.proxy_gap_positive:.2f}, G_p^-={eval_score.proxy_gap_negative:.2f})"
                print(
                    f"\r  > {idx_str}Task {task.id:<18} ({task.type:<9}) -> {status_tag} "
                    f"[gt={eval_score.ground_truth_score:.2f}, {gap_display}] "
                    f"in {dur_s:.1f}s | {tot_tok:,} tok | ${res.cost_usd:.4f}{viol_info}",
                    flush=True,
                )

            # Workspace Pruning: Delete completed task directory to prevent disk exhaustion (Kaggle 20GB limit)
            if self.prune_workspaces and task_ws.exists():
                try:
                    shutil.rmtree(task_ws, ignore_errors=True)
                except Exception:
                    pass

            # Memory Hygiene: Free unreferenced AST nodes, subprocess outputs, and VRAM fragmentation
            gc.collect()
            if "torch" in sys.modules:
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    pass

            return task_result_entry, task_safety_violations, task_key

