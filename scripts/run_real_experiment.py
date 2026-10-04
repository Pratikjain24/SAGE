"""Run a real SAGE experiment with configurable dimensions and live models.

Usage:
    python scripts/run_real_experiment.py --groups G1,G2,G3,G4,G5,G6,G7 --cycles 5 \
        --seeds 42 --train 20 --test 10 --run-id colab_empirical_study

This script enforces strict API-only inference (no mock fallback) and prints a
verification summary proving every recorded episode came from a real model call.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_env() -> None:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    
    # Auto-bridge GROQ_API_KEY to OpenAI environment if needed
    if os.environ.get("GROQ_API_KEY") and not os.environ.get("OPENAI_API_BASE"):
        os.environ.setdefault("OPENAI_API_BASE", "https://api.groq.com/openai/v1")
        os.environ.setdefault("OPENAI_API_KEY", os.environ["GROQ_API_KEY"])


def main() -> int:
    ap = argparse.ArgumentParser(description="Run live empirical SAGE benchmark")
    ap.add_argument("--config", default="configs/experiments/real_groq_strict.yaml", help="Path to config YAML")
    ap.add_argument("--groups", default="G1,G2,G3,G4,G5,G6,G7", help="Comma-separated agent groups")
    ap.add_argument("--cycles", type=int, default=5, help="Number of evolutionary cycles")
    ap.add_argument("--seeds", default="42", help="Comma-separated random seeds")
    ap.add_argument("--train", type=int, default=20, help="Train tasks per cycle")
    ap.add_argument("--test", type=int, default=10, help="Test tasks per cycle")
    ap.add_argument("--run-id", required=True, help="Unique identifier for experiment run")
    ap.add_argument("--max-usd", type=float, default=50.0, help="Budget cap in USD")
    ap.add_argument("--max-workers", type=int, default=1, help="Parallel execution workers")
    args = ap.parse_args()

    load_env()

    import yaml
    from sage.config.models import ExperimentConfig
    from sage.environment.task_loader import TaskLoader
    from sage.runner.orchestrator import ExperimentOrchestrator

    config_path = ROOT / args.config
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        return 1

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    cfg = ExperimentConfig.model_validate(raw)
    cfg.groups = [g.strip() for g in args.groups.split(",") if g.strip()]
    cfg.cycles = args.cycles
    cfg.seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    cfg.tasks.train = args.train
    cfg.tasks.test = args.test
    cfg.budget.max_usd_per_run = args.max_usd

    loader = TaskLoader(ROOT / "tasks/tasks_index.json")
    orch = ExperimentOrchestrator(
        cfg, loader, runs_dir=ROOT / "experiments/runs", max_workers=args.max_workers
    )

    client_name = type(orch.llm_client).__name__
    print(f"[client] {client_name} (allow_fallback={getattr(orch.llm_client, 'allow_fallback', None)})")
    REAL_CLIENTS = ("OpenAICompatibleClient", "LocalLlamaClient")
    if client_name not in REAL_CLIENTS:
        print(
            f"REFUSING TO RUN: client is {client_name}, not a real inference client. "
            "A MockLLMClient would produce synthetic data."
        )
        return 2

    print(f"[matrix] groups={cfg.groups} cycles={cfg.cycles} seeds={cfg.seeds} "
          f"train={cfg.tasks.train} test={cfg.tasks.test}")
    t0 = time.time()
    out_dir = orch.run_experiment(run_id=args.run_id)
    elapsed_min = (time.time() - t0) / 60.0
    print(f"\n[done] Experiment completed in {elapsed_min:.1f} min! Output: {out_dir}")

    # Post-run provenance audit of the produced trajectory
    traj = Path(out_dir) / "trajectory.jsonl"
    n_end = n_fallback = n_zero_tok = n_real = 0
    models: set[str] = set()
    if traj.exists():
        with open(traj, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get("event_type") != "task_end":
                    continue
                n_end += 1
                p = ev.get("payload", {})
                c = ev.get("cost", {})
                if p.get("is_fallback"):
                    n_fallback += 1
                print_model = p.get("model_name")
                if print_model:
                    models.add(print_model)
                tok = c.get("tokens_in", 0) + c.get("tokens_out", 0)
                if tok == 0:
                    n_zero_tok += 1
                else:
                    n_real += 1
        print(f"\n[provenance audit] Total task ends: {n_end}")
        print(f"  - Real LLM calls: {n_real}")
        print(f"  - Zero-token calls: {n_zero_tok}")
        print(f"  - Fallback calls: {n_fallback}")
        print(f"  - Active models recorded: {sorted(models)}")
        if n_fallback or n_zero_tok:
            print("[audit] ⚠️ WARNING: Contaminated episodes present — verify before publishing.")
        else:
            print("[audit] ✅ PASS: 100% Genuine Empirical LLM Trajectory with zero synthetic mock contamination.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
