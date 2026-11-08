"""Experiment Orchestrator: Multi-seed, multi-group, recursive evolutionary benchmark runner with crash recovery, timeouts, and retry policies."""

from __future__ import annotations

import concurrent.futures
import gc
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from sage.adapters.base import AgentAdapter, TaskResult, TaskSpec
from sage.adapters.memory_agent import MemoryAgentAdapter
from sage.adapters.prompt_agent import PromptAgentAdapter
from sage.adapters.reflection_agent import ReflectionAgentAdapter
from sage.adapters.static_agent import StaticAgentAdapter
from sage.adapters.wrapper import VerifierAgentWrapper
from sage.config.models import ExperimentConfig, TaskConfig
from sage.environment.safety_monitor import SafetyMonitor
from sage.environment.task_loader import TaskLoader
from sage.evolution.controller import EvolutionController
from sage.evolution.verifier import EvolutionVerifier
from sage.llm.client import BaseLLMClient, MockLLMClient, OpenAICompatibleClient
from sage.llm.pricing import BudgetGuard
from sage.runner.cycle_manager import ARCHETYPE_DESCRIPTIONS, CycleManager
from sage.runner.reproducibility import (
    generate_trajectory_manifest,
    set_global_seed,
)
from sage.runner.task_executor import TaskExecutor
from sage.scoring.hidden_scorer import HiddenScorer
from sage.trajectory.writer import TrajectoryWriter


class ExperimentOrchestrator:
    """Orchestrates experiment matrix: Groups x Seeds x Cycles x Tasks with hardening controls."""

    def __init__(
        self,
        config: ExperimentConfig,
        task_loader: TaskLoader,
        runs_dir: Optional[Path] = None,
        max_retries: int = 2,
        retry_backoff: float = 0.2,
        llm_client: Optional[BaseLLMClient] = None,
        max_workers: int = 8,
        verbose: bool = True,
        prune_workspaces: bool = True,
    ):
        self.config = config
        self.task_loader = task_loader
        self.runs_dir = Path(runs_dir or os.environ.get("SAGE_RUNS_DIR") or Path("experiments/runs"))
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.verbose = verbose
        self.prune_workspaces = prune_workspaces
        if llm_client is not None:
            self.llm_client = llm_client
        elif config.model.family == "anthropic" or "anthropic.com" in (config.model.api_base or ""):
            from sage.llm.client import AnthropicClient
            self.llm_client = AnthropicClient(config.model)
        elif config.model.api_base in ("local", "in_process", "direct") or config.model.name.endswith(".gguf"):
            from sage.llm.client import LocalLlamaClient
            model_p = config.model.name if config.model.name.endswith(".gguf") else "models/qwen2.5-coder-3b-instruct-q4_k_m.gguf"
            self.llm_client = LocalLlamaClient(model_path=model_p, n_threads=8)
        elif config.model.api_base:
            self.llm_client = OpenAICompatibleClient(config.model)
        else:
            self.llm_client = MockLLMClient(model_name=config.model.name)
        self.max_workers = max(1, max_workers)
        self.budget_guard = BudgetGuard(
            max_usd_budget=config.budget.max_usd_per_run,
            max_wall_hours=config.budget.max_wall_hours,
            max_tokens_per_task=config.budget.max_tokens_per_task,
        )
        self.task_executor = TaskExecutor(
            config=self.config,
            task_loader=self.task_loader,
            budget_guard=self.budget_guard,
            max_retries=self.max_retries,
            retry_backoff=self.retry_backoff,
            verbose=self.verbose,
            prune_workspaces=self.prune_workspaces,
        )

    def _create_agent(self, group: str) -> AgentAdapter:
        """Instantiate agent adapter corresponding to group tag."""
        if group == "G1":
            return StaticAgentAdapter(llm_client=self.llm_client)
        elif group == "G2":
            return PromptAgentAdapter(llm_client=self.llm_client)
        elif group == "G3":
            return MemoryAgentAdapter(llm_client=self.llm_client)
        elif group == "G4":
            return ReflectionAgentAdapter(llm_client=self.llm_client)
        elif group == "G5":
            base = ReflectionAgentAdapter(llm_client=self.llm_client)
            return VerifierAgentWrapper(base, group="G5")
        elif group in ("G6", "G6*"):
            base = ReflectionAgentAdapter(llm_client=self.llm_client)
            return VerifierAgentWrapper(
                base,
                group="G6",
                config={
                    "enable_rollback": True,
                    "canary_target": "oracle",
                    "min_capability_retention": self.config.verifier.min_capability_retention,
                },
            )
        elif group == "G7":
            base = ReflectionAgentAdapter(llm_client=self.llm_client)
            return VerifierAgentWrapper(
                base,
                group="G7",
                config={
                    "enable_rollback": True,
                    "canary_target": "proxy",
                    "min_capability_retention": self.config.verifier.min_capability_retention,
                },
            )
        else:
            return StaticAgentAdapter(llm_client=self.llm_client)

    def _scan_existing_trajectory(
        self, trajectory_path: Path
    ) -> Tuple[
        Set[Tuple[int, str, int, str]],
        Dict[Tuple[int, str, int, str], Dict[str, Any]],
        Set[Tuple[int, str, int]],
        List[Dict[str, Any]],
    ]:
        """Scan existing trajectory.jsonl for crash recovery checkpoints.

        Returns:
            completed_tasks: Set of (seed, group, cycle, task_id)
            task_end_results: Dict mapping (seed, group, cycle, task_id) to result summary dict
            completed_evolution_cycles: Set of (seed, group, cycle)
            restored_metrics: Pre-crash cycle metrics reconstructed from events
        """
        completed_tasks: Set[Tuple[int, str, int, str]] = set()
        task_end_results: Dict[Tuple[int, str, int, str], Dict[str, Any]] = {}
        completed_evolution_cycles: Set[Tuple[int, str, int]] = set()
        restored_metrics: List[Dict[str, Any]] = []

        if not trajectory_path.exists():
            return completed_tasks, task_end_results, completed_evolution_cycles, restored_metrics

        total_usd = 0.0
        total_tin = 0
        total_tout = 0

        with open(trajectory_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    ev_type = ev.get("event_type")
                    seed = ev.get("seed")
                    group = ev.get("group")
                    cycle = ev.get("cycle")
                    task_id = ev.get("task_id")
                    cost = ev.get("cost") or {}

                    total_usd += float(cost.get("usd", 0.0))
                    total_tin += int(cost.get("tokens_in", 0))
                    total_tout += int(cost.get("tokens_out", 0))

                    if ev_type == "task_end" and seed is not None and group and cycle is not None and task_id:
                        key = (int(seed), str(group), int(cycle), str(task_id))
                        completed_tasks.add(key)
                        payload = ev.get("payload") or {}
                        task_end_results[key] = {
                            "task_id": str(task_id),
                            "type": str(payload.get("task_type") or ""),
                            "success": bool(payload.get("success", False)),
                            "gt_score": float(payload.get("ground_truth_score", 0.0)),
                            "proxy_score": float(payload.get("proxy_score", 0.0)),
                            "proxy_gap": float(payload.get("proxy_gap", 0.0)),
                            "proxy_gap_positive": float(payload.get("proxy_gap_positive", max(0.0, float(payload.get("proxy_gap", 0.0))))),
                            "proxy_gap_negative": float(payload.get("proxy_gap_negative", 0.0)),
                            "proxy_gap_signed": float(payload.get("proxy_gap_signed", payload.get("proxy_gap", 0.0))),
                            "cost_usd": float(cost.get("usd", 0.0)),
                            "status": payload.get("status", "completed"),
                        }
                    elif ev_type in ("evolution_decision", "rollback") and seed is not None and group and cycle is not None:
                        completed_evolution_cycles.add((int(seed), str(group), int(cycle)))
                except Exception:
                    continue

        self.budget_guard.restore_spent(usd=total_usd, tokens_in=total_tin, tokens_out=total_tout)
        return completed_tasks, task_end_results, completed_evolution_cycles, restored_metrics

    def _run_task_with_timeout(
        self,
        agent: AgentAdapter,
        spec: TaskSpec,
        sandbox: Any,
        timeout_sec: float | int,
    ) -> TaskResult:
        """Execute agent task under strict wall-clock timeout constraints."""
        return self.task_executor.run_task_with_timeout(agent, spec, sandbox, timeout_sec)

    def _run_task_with_retry(
        self,
        agent: AgentAdapter,
        spec: TaskSpec,
        sandbox: Any,
        safety_monitor: SafetyMonitor,
        timeout_sec: float | int,
    ) -> TaskResult:
        """Run task with exponential backoff on transient errors, terminating immediately on fatal blocks."""
        return self.task_executor.run_task_with_retry(
            agent=agent,
            spec=spec,
            sandbox=sandbox,
            safety_monitor=safety_monitor,
            timeout_sec=timeout_sec,
            timeout_fn=self._run_task_with_timeout,
        )

    def _execute_single_task(
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
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Tuple[int, str, int, str]]:
        """Execute and score a single task inside its isolated workspace with telemetry logging."""
        return self.task_executor.execute_single_task(
            task=task,
            seed=seed,
            group=group,
            cycle=cycle,
            agent=agent,
            run_name=run_name,
            run_dir=run_dir,
            writer=writer,
            scorer=scorer,
            task_idx=task_idx,
            total_tasks=total_tasks,
            run_task_fn=self._run_task_with_retry,
        )

    def _cleanup_between_seeds(self, workspace_dir: Optional[str | int] = None, seed: Optional[int] = None) -> None:
        """Clean scratch state between seeds to prevent cross-contamination."""
        if isinstance(workspace_dir, int):
            seed = workspace_dir
            workspace_dir = None
        ws = str(workspace_dir or getattr(self.config, "workspace_dir", ".") or ".")
        scratch_dirs = ["__pycache__", ".pytest_cache", "scratch", "tmp", ".hypothesis"]
        for d in scratch_dirs:
            target = os.path.join(ws, d)
            if os.path.exists(target):
                shutil.rmtree(target, ignore_errors=True)
            # Also clean subdirectories recursively
            try:
                for p in Path(ws).rglob(d):
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
        if self.verbose:
            msg = "[CLEANUP] Scratch & GPU VRAM reset complete"
            if seed is not None:
                msg += f" for seed {seed}"
            print(f"{msg}.", flush=True)

    def _execute_cycle(
        self,
        seed: int,
        group: str,
        cycle: int,
        agent: AgentAdapter,
        run_name: str,
        run_dir: Path,
        writer: TrajectoryWriter,
        scorer: HiddenScorer,
        train_tasks: List[TaskConfig],
        test_tasks: List[TaskConfig],
        completed_tasks: Set[Tuple[int, str, int, str]],
        task_end_results: Dict[Tuple[int, str, int, str], Dict[str, Any]],
        completed_evolution_cycles: Set[Tuple[int, str, int]],
        cycle_manager: CycleManager,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Delegate cycle execution to CycleManager, providing polymorphic task execution override."""
        return cycle_manager.execute_cycle(
            seed=seed,
            group=group,
            cycle=cycle,
            agent=agent,
            run_name=run_name,
            run_dir=run_dir,
            writer=writer,
            scorer=scorer,
            train_tasks=train_tasks,
            test_tasks=test_tasks,
            completed_tasks=completed_tasks,
            task_end_results=task_end_results,
            completed_evolution_cycles=completed_evolution_cycles,
            execute_task_fn=self._execute_single_task,
        )

    def run_experiment(self, run_id: Optional[str] = None) -> Path:
        """Execute full experiment run with crash recovery, timeout safeguards, and budget tracking."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        run_name = run_id or f"{self.config.name}_{timestamp}"
        run_dir = self.runs_dir / run_name
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save active experiment config
        config_path = run_dir / "config.json"
        if not config_path.exists():
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(self.config.model_dump_json(indent=2))

        writer_path = run_dir / "trajectory.jsonl"
        completed_tasks, task_end_results, completed_evolution_cycles, _ = (
            self._scan_existing_trajectory(writer_path)
        )
        if completed_tasks and self.verbose:
            print(
                f"\n[RECOVERY] Resuming run '{run_name}': detected {len(completed_tasks)} completed task(s) "
                f"across {len(completed_evolution_cycles)} completed evolution cycle(s).\n"
                f"           Skipping already evaluated steps and resuming execution...",
                flush=True,
            )

        writer = TrajectoryWriter(writer_path)

        train_tasks, test_tasks = self.task_loader.split_tasks(self.config.tasks)
        if not train_tasks:
            train_tasks = [
                TaskConfig(
                    id="sample_task_1",
                    type="bug_fix",
                    repo="math_engine",
                    prompt="Fix edge case in polynomial roots calculation.",
                )
            ]

        if getattr(self.config, "judge", None) and self.config.judge.enabled:
            from sage.scoring.llm_judge import LLMJudge
            scorer = HiddenScorer(llm_judge=LLMJudge(self.config.judge))
        else:
            scorer = HiddenScorer()
        verifier = EvolutionVerifier(
            rules=self.config.verifier.rules,
            max_acceptable_drift=self.config.verifier.max_acceptable_drift,
        )
        controller = EvolutionController(
            verifier=verifier,
            snapshots_dir=run_dir / "agent_state",
            config=self.config.model_dump() if hasattr(self.config, "model_dump") else {},
        )

        cycle_manager = CycleManager(
            config=self.config,
            task_executor=self.task_executor,
            controller=controller,
            budget_guard=self.budget_guard,
            max_workers=self.max_workers,
            verbose=self.verbose,
        )

        all_cycle_metrics: List[Dict[str, Any]] = []

        try:
            for seed in self.config.seeds:
                workspace_dir = str(getattr(self.config, "workspace_dir", ".") or ".")
                self._cleanup_between_seeds(workspace_dir=workspace_dir, seed=seed)
                set_global_seed(seed, getattr(self.config, "reproducibility", None))
                for group in self.config.groups:
                    agent = self._create_agent(group)
                    agent.reset()

                    for cycle in range(self.config.cycles):
                        metric_entry, _, _ = self._execute_cycle(
                            seed=seed,
                            group=group,
                            cycle=cycle,
                            agent=agent,
                            run_name=run_name,
                            run_dir=run_dir,
                            writer=writer,
                            scorer=scorer,
                            train_tasks=train_tasks,
                            test_tasks=test_tasks,
                            completed_tasks=completed_tasks,
                            task_end_results=task_end_results,
                            completed_evolution_cycles=completed_evolution_cycles,
                            cycle_manager=cycle_manager,
                        )
                        all_cycle_metrics.append(metric_entry)

                self._cleanup_between_seeds(workspace_dir=workspace_dir, seed=seed)

        finally:
            writer.close()

        # Save metrics JSON (merging with existing records if present across multi-cell runs)
        results_dir = run_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        metrics_file = results_dir / "cycle_metrics.json"

        final_metrics = []
        if metrics_file.exists():
            try:
                existing_metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
                current_keys = {(m.get("seed"), m.get("group"), m.get("cycle")) for m in all_cycle_metrics}
                final_metrics = [
                    m for m in existing_metrics
                    if (m.get("seed"), m.get("group"), m.get("cycle")) not in current_keys
                ]
            except Exception:
                final_metrics = []
        final_metrics.extend(all_cycle_metrics)
        final_metrics.sort(key=lambda m: (str(m.get("group", "")), int(m.get("seed", 0)), int(m.get("cycle", 0))))

        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(final_metrics, f, indent=2)

        # Compute and record inductive generalization gap reports across groups
        gen_reports: Dict[str, Any] = {}
        by_group: Dict[str, List[Dict[str, Any]]] = {}
        for m in final_metrics:
            by_group.setdefault(m["group"], []).append(m)

        for grp, c_list in by_group.items():
            if len(c_list) >= 2:
                c0 = c_list[0]["success_rate"]
                c_evolve_final = c_list[-2]["success_rate"] if len(c_list) > 2 else c_list[0]["success_rate"]
                c_eval_final = c_list[-1]["success_rate"]
                rep = self.task_loader.calculate_generalization_gap(
                    p0_evolve=c0,
                    pT_evolve=c_evolve_final,
                    p0_eval=c0,
                    pT_eval=c_eval_final,
                    group=grp,
                    n_evolve=len(train_tasks),
                    n_eval=len(test_tasks),
                )
                gen_reports[grp] = rep.to_dict()

        if gen_reports:
            gen_file = results_dir / "generalization_gap.json"
            final_gen = {}
            if gen_file.exists():
                try:
                    final_gen = json.loads(gen_file.read_text(encoding="utf-8"))
                except Exception:
                    final_gen = {}
            final_gen.update(gen_reports)
            with open(gen_file, "w", encoding="utf-8") as f:
                json.dump(final_gen, f, indent=2)

        # Generate cryptographic SHA-256 trajectory manifest for reviewer verification
        generate_trajectory_manifest(run_dir, self.config)

        return run_dir

