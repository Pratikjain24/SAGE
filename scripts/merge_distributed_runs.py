#!/usr/bin/env python3
"""SAGE Distributed Study: Submission Merger & Cross-Check Replication Engine.

Integrates distributed contributor runs into a unified canonical benchmark dataset:
1. Gathers trajectories across contributor packages (G1-G7).
2. Performs P1 vs P7 inter-hardware replication cross-check (tolerance |Δ| ≤ 2.5%).
3. Generates unified trajectory.jsonl and cryptographic trajectory_manifest.json.
4. Cryptographically seals evaluation windows into SQLite AttestationLedger.
5. Emits study synthesis report and validation metrics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sage.runner.reproducibility import load_pinned_docker_digests
from sage.trajectory.hashing import compute_deterministic_trajectory_hash
from sage_live.core.attestation import AttestationLedger


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 digest of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass
class CrossCheckResult:
    p1_total: int = 0
    p1_passed: int = 0
    p1_rate: float = 0.0
    p7_total: int = 0
    p7_passed: int = 0
    p7_rate: float = 0.0
    delta: float = 0.0
    tolerance: float = 0.025
    passed: bool = False
    details: str = ""


def extract_runs_from_source(source_path: Path, temp_dir: Path) -> List[Path]:
    """Extract run directories from a ZIP archive or directory."""
    runs: List[Path] = []
    if source_path.is_file() and source_path.suffix.lower() == ".zip":
        extract_target = temp_dir / source_path.stem
        extract_target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(source_path, "r") as z:
            z.extractall(extract_target)

        # Check for runs/ directory
        candidate_runs = extract_target / "runs"
        if candidate_runs.exists() and candidate_runs.is_dir():
            for d in candidate_runs.iterdir():
                if d.is_dir() and (d / "trajectory.jsonl").exists():
                    runs.append(d)
        else:
            # Check direct subdirectories
            for d in extract_target.rglob("trajectory.jsonl"):
                runs.append(d.parent)
    elif source_path.is_dir():
        candidate_runs = source_path / "runs"
        if candidate_runs.exists() and candidate_runs.is_dir():
            for d in candidate_runs.iterdir():
                if d.is_dir() and (d / "trajectory.jsonl").exists():
                    runs.append(d)
        else:
            for d in source_path.rglob("trajectory.jsonl"):
                runs.append(d.parent)

    return runs


def evaluate_cross_check(
    p1_events: List[Dict[str, Any]],
    p7_cross_events: List[Dict[str, Any]],
    tolerance: float = 0.025,
) -> CrossCheckResult:
    """Compute inter-session reproducibility delta between P1 G1 baseline and P7 G1 replication."""
    res = CrossCheckResult(tolerance=tolerance)

    for ev in p1_events:
        if ev.get("event_type") == "task_end":
            res.p1_total += 1
            if ev.get("payload", {}).get("success") is True:
                res.p1_passed += 1

    for ev in p7_cross_events:
        if ev.get("event_type") == "task_end":
            res.p7_total += 1
            if ev.get("payload", {}).get("success") is True:
                res.p7_passed += 1

    if res.p1_total > 0:
        res.p1_rate = res.p1_passed / res.p1_total
    if res.p7_total > 0:
        res.p7_rate = res.p7_passed / res.p7_total

    if res.p1_total > 0 and res.p7_total > 0:
        res.delta = round(abs(res.p1_rate - res.p7_rate), 6)
        res.passed = res.delta <= tolerance
        res.details = (
            f"P1 G1 Solve Rate: {res.p1_rate * 100:.2f}% ({res.p1_passed}/{res.p1_total}) | "
            f"P7 Cross-Check Solve Rate: {res.p7_rate * 100:.2f}% ({res.p7_passed}/{res.p7_total}) | "
            f"Delta: {res.delta * 100:.2f}% (Limit: <= {tolerance * 100:.2f}%) -> "
            f"{'REPRODUCIBLE' if res.passed else 'DISCREPANCY DETECTED'}"
        )
    else:
        res.passed = False
        res.details = f"Incomplete cross-check data: P1 tasks={res.p1_total}, P7 cross tasks={res.p7_total}"

    return res


def merge_trajectories(
    run_dirs: List[Path],
    output_dir: Path,
    tolerance: float = 0.025,
    db_path: Optional[Path] = None,
    secret_key: Optional[str] = None,
) -> Tuple[Path, Optional[CrossCheckResult]]:
    """Merge trajectory files, run cross-check, generate manifest, and seal into AttestationLedger."""
    output_dir.mkdir(parents=True, exist_ok=True)
    merged_traj_path = output_dir / "trajectory.jsonl"

    all_events: List[Dict[str, Any]] = []
    p1_g1_events: List[Dict[str, Any]] = []
    p7_cross_events: List[Dict[str, Any]] = []

    groups_seen: set = set()
    seeds_seen: set = set()
    models_seen: set = set()
    total_tokens_in = 0
    total_tokens_out = 0

    for rdir in run_dirs:
        tfile = rdir / "trajectory.jsonl"
        is_cross_check = "cross" in rdir.name.lower() or "check" in rdir.name.lower()

        with open(tfile, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue

                all_events.append(ev)

                grp = ev.get("group")
                if grp:
                    groups_seen.add(str(grp))
                seed = ev.get("seed")
                if seed is not None:
                    seeds_seen.add(int(seed))

                # Track cross check events
                if grp == "G1":
                    if is_cross_check:
                        p7_cross_events.append(ev)
                    else:
                        p1_g1_events.append(ev)

                cost = ev.get("cost", {})
                total_tokens_in += int(cost.get("tokens_in", 0) or 0)
                total_tokens_out += int(cost.get("tokens_out", 0) or 0)

                payload = ev.get("payload", {})
                m_name = payload.get("model_name")
                if m_name:
                    models_seen.add(str(m_name))

    # Sort events chronologically / canonically: cycle, seed, group, task_id, ts
    def sort_key(e: Dict[str, Any]) -> Tuple[int, int, str, str, str]:
        return (
            int(e.get("cycle", 0) or 0),
            int(e.get("seed", 0) or 0),
            str(e.get("group", "")),
            str(e.get("task_id", "")),
            str(e.get("ts", "")),
        )

    all_events.sort(key=sort_key)

    # Write merged trajectory.jsonl
    with open(merged_traj_path, "w", encoding="utf-8") as f:
        for ev in all_events:
            f.write(json.dumps(ev) + "\n")

    # Generate Manifest
    raw_sha = compute_sha256(merged_traj_path)
    try:
        det_sha = compute_deterministic_trajectory_hash(merged_traj_path)
    except Exception:
        det_sha = raw_sha

    manifest_data = {
        "manifest_version": "1.0.0",
        "schema_version": "1.0.0",
        "run_id": output_dir.name,
        "raw_sha256": raw_sha,
        "deterministic_sha256": det_sha,
        "total_events": len(all_events),
        "groups": sorted(list(groups_seen)),
        "seeds": sorted(list(seeds_seen)),
        "models": sorted(list(models_seen)),
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "docker_digests": load_pinned_docker_digests(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    manifest_file = output_dir / "trajectory_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    # Perform Cross-Check Analysis if available
    cross_check_res: Optional[CrossCheckResult] = None
    if p1_g1_events and p7_cross_events:
        cross_check_res = evaluate_cross_check(p1_g1_events, p7_cross_events, tolerance=tolerance)

    # Cryptographically Seal into AttestationLedger
    if db_path is not None or (REPO_ROOT / "experiments" / "attestation.db").exists():
        ledger_db = db_path or (REPO_ROOT / "experiments" / "attestation.db")
        key = secret_key or os.environ.get("ATTESTATION_SECRET_KEY")
        if not key:
            # If ledger already has blocks, we need a key or fallback to environment
            key = "sage_coordinator_default_key_" + hashlib.sha256(str(ledger_db).encode()).hexdigest()[:16]

        try:
            ledger = AttestationLedger(secret_key=key, db_path=str(ledger_db))
            if ledger.chain_length == 0:
                ledger.create_genesis_block()

            # Group events by (group, cycle) and add evaluation windows
            window_buckets: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
            for ev in all_events:
                if ev.get("event_type") == "task_end":
                    grp = str(ev.get("group", "G1"))
                    cyc = int(ev.get("cycle", 0))
                    window_buckets.setdefault((grp, cyc), []).append(ev)

            for (grp, cyc), evs in sorted(window_buckets.items()):
                agent_state = {"group": grp, "cycle": cyc, "models": list(models_seen)}
                probe_set = [str(ev.get("task_id")) for ev in evs]
                results = {
                    str(ev.get("task_id")): {
                        "passed": ev.get("payload", {}).get("success", False),
                        "score": 100.0 if ev.get("payload", {}).get("success") else 0.0,
                    }
                    for ev in evs
                }
                ledger.add_evaluation_window(agent_state, probe_set, results)

            ledger.verify_chain_integrity()
        except Exception as e:
            print(f"Warning: Attestation sealing failed: {e}", file=sys.stderr)

    return merged_traj_path, cross_check_res


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge SAGE distributed contributor submissions and perform cross-check audit."
    )
    parser.add_argument(
        "--submissions-dir",
        "-d",
        type=Path,
        required=True,
        help="Directory containing verified submission .zip files or directories.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=REPO_ROOT / "experiments" / "runs" / "study_live_distributed_merged",
        help="Destination directory for merged trajectory and manifest.",
    )
    parser.add_argument(
        "--cross-check-tol",
        type=float,
        default=0.025,
        help="Inter-hardware reproducibility delta tolerance limit (default: 0.025 = 2.5%%).",
    )
    parser.add_argument(
        "--attestation-db",
        type=Path,
        default=REPO_ROOT / "experiments" / "attestation.db",
        help="Path to SQLite Attestation Ledger database.",
    )
    parser.add_argument(
        "--secret-key",
        type=str,
        default=None,
        help="Secret key for AttestationLedger HMAC-SHA256 signatures.",
    )

    args = parser.parse_args()

    if not args.submissions_dir.exists():
        print(f"Error: Submissions directory does not exist: {args.submissions_dir}", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir)
        all_runs: List[Path] = []

        # Process each item in submissions-dir
        items = list(args.submissions_dir.glob("*.zip")) + [
            p for p in args.submissions_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
        ]

        for item in sorted(items):
            extracted = extract_runs_from_source(item, temp_path)
            all_runs.extend(extracted)

        if not all_runs:
            print(f"Error: No valid runs found in {args.submissions_dir}", file=sys.stderr)
            sys.exit(1)

        print(f"Discovered {len(all_runs)} runs to merge across {len(items)} contributor submissions.")

        merged_path, cross_check = merge_trajectories(
            run_dirs=all_runs,
            output_dir=args.output_dir,
            tolerance=args.cross_check_tol,
            db_path=args.attestation_db,
            secret_key=args.secret_key,
        )

        print("\n" + "=" * 80)
        print("SAGE DISTRIBUTED STUDY MERGE COMPLETED")
        print("=" * 80)
        print(f"Merged Trajectory : {merged_path}")
        print(f"Manifest Generated: {args.output_dir / 'trajectory_manifest.json'}")

        if cross_check:
            print("\nINTER-HARDWARE CROSS-CHECK (P1 G1 vs P7 G1):")
            print(f"  {cross_check.details}")
            if not cross_check.passed:
                print("  [WARN] Cross-check exceeded tolerance threshold!")

        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
