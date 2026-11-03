#!/usr/bin/env python3
"""SAGE Distributed Study: Submission Verifier & Provenance Auditor.

Audits contributor ZIP submissions or unpacked run directories from Kaggle/remote nodes:
1. Validates archive integrity, directory layout, and notes metadata.
2. Mathematically verifies zero mock-fallbacks and genuine token counts in trajectories.
3. Cryptographically audits SHA-256 digests against trajectory manifests.
4. Checks task completeness across seeds and cycles.
5. Emits machine-readable verification reports and human-readable CLI tables.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class RunAuditResult:
    run_id: str
    group: str
    seed: int
    total_events: int = 0
    total_tasks: int = 0
    passed_tasks: int = 0
    real_calls: int = 0
    fallback_calls: int = 0
    zero_token_calls: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    models_seen: List[str] = field(default_factory=list)
    manifest_verified: bool = False
    manifest_error: Optional[str] = None
    trajectory_sha256: str = ""
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)


@dataclass
class SubmissionAuditResult:
    submission_path: str
    contributor_id: str = "Unknown"
    group: str = "Unknown"
    seeds_claimed: List[int] = field(default_factory=list)
    notes_found: bool = False
    runs_found: int = 0
    state_markers_found: int = 0
    runs: List[RunAuditResult] = field(default_factory=list)
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 digest of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def audit_trajectory_file(
    traj_path: Path,
    expected_group: Optional[str] = None,
    expected_seed: Optional[int] = None,
    manifest_path: Optional[Path] = None,
    expected_model: Optional[str] = None,
) -> RunAuditResult:
    """Audit a single trajectory.jsonl file for integrity, zero-mock, and genuine tokens."""
    run_id = traj_path.parent.name
    res = RunAuditResult(
        run_id=run_id,
        group=expected_group or "Unknown",
        seed=expected_seed or -1,
    )

    if not traj_path.exists():
        res.errors.append(f"Trajectory file missing: {traj_path}")
        return res

    res.trajectory_sha256 = compute_sha256(traj_path)

    # 1. Manifest verification if present
    if manifest_path and manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                mdata = json.load(mf)
            raw_sha = mdata.get("raw_sha256", "")
            if raw_sha and raw_sha != res.trajectory_sha256:
                res.manifest_error = f"SHA-256 mismatch: manifest={raw_sha[:12]} vs file={res.trajectory_sha256[:12]}"
                res.errors.append(res.manifest_error)
            else:
                res.manifest_verified = True
        except Exception as e:
            res.manifest_error = f"Manifest read failed: {e}"
            res.errors.append(res.manifest_error)

    # 2. Event analysis
    models: Set[str] = set()
    try:
        with open(traj_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError as e:
                    res.errors.append(f"JSON parse error at line {line_idx}: {e}")
                    continue

                res.total_events += 1
                ev_type = ev.get("event_type")

                # Extract run metadata if not set
                if res.group == "Unknown" and ev.get("group"):
                    res.group = str(ev["group"])
                if res.seed == -1 and ev.get("seed") is not None:
                    res.seed = int(ev["seed"])

                if ev_type == "task_end":
                    res.total_tasks += 1
                    payload = ev.get("payload", {})
                    cost = ev.get("cost", {})
                    tin = int(cost.get("tokens_in", 0) or 0)
                    tout = int(cost.get("tokens_out", 0) or 0)
                    res.total_tokens_in += tin
                    res.total_tokens_out += tout

                    if payload.get("is_fallback") is True:
                        res.fallback_calls += 1
                        res.errors.append(f"Task {ev.get('task_id')} flagged as mock fallback!")

                    if (tin + tout) == 0:
                        res.zero_token_calls += 1
                        res.errors.append(f"Task {ev.get('task_id')} recorded 0 tokens (synthetic/unexecuted)!")
                    else:
                        res.real_calls += 1

                    m_name = payload.get("model_name")
                    if m_name:
                        models.add(str(m_name))

                    if payload.get("success") is True:
                        res.passed_tasks += 1

    except Exception as e:
        res.errors.append(f"Failed to read trajectory: {e}")

    res.models_seen = sorted(list(models))

    # Strict model verification if requested
    if expected_model and models:
        for m in models:
            if expected_model.lower() not in m.lower():
                res.errors.append(f"Model mismatch: seen '{m}', expected '{expected_model}'")

    res.is_valid = len(res.errors) == 0 and res.total_tasks > 0 and res.fallback_calls == 0 and res.zero_token_calls == 0
    return res


def audit_submission_directory(
    root_dir: Path,
    submission_path_str: str,
    strict_tasks: Optional[int] = None,
    expected_seeds: Optional[List[int]] = None,
    expected_model: Optional[str] = None,
) -> SubmissionAuditResult:
    """Audit an uncompressed submission directory."""
    sub_res = SubmissionAuditResult(submission_path=submission_path_str)

    # 1. Inspect notes.txt
    notes_file = root_dir / "notes.txt"
    if notes_file.exists():
        sub_res.notes_found = True
        try:
            notes_content = notes_file.read_text(encoding="utf-8")
            for line in notes_content.splitlines():
                if "Contributor ID" in line and ":" in line:
                    sub_res.contributor_id = line.split(":", 1)[1].strip()
                elif "Assigned Layer" in line and ":" in line:
                    assigned = line.split(":", 1)[1].strip()
                    sub_res.group = assigned.split()[0]
                elif "Seeds Tested" in line and ":" in line:
                    seeds_str = line.split(":", 1)[1].strip()
                    try:
                        sub_res.seeds_claimed = json.loads(seeds_str)
                    except Exception:
                        pass
        except Exception as e:
            sub_res.warnings.append(f"Failed parsing notes.txt: {e}")
    else:
        sub_res.warnings.append("notes.txt not found in submission root")

    # 2. Check state markers
    state_dir = root_dir / "state"
    if state_dir.exists():
        markers = list(state_dir.glob("done_*"))
        sub_res.state_markers_found = len(markers)
    else:
        sub_res.warnings.append("state/ directory not found")

    # 3. Locate runs
    runs_dir = root_dir / "runs"
    if not runs_dir.exists():
        # Fallback: maybe runs are at top-level
        candidate_dirs = [d for d in root_dir.iterdir() if d.is_dir() and (d / "trajectory.jsonl").exists()]
    else:
        candidate_dirs = [d for d in runs_dir.iterdir() if d.is_dir() and (d / "trajectory.jsonl").exists()]

    sub_res.runs_found = len(candidate_dirs)
    if not candidate_dirs:
        sub_res.errors.append("No valid run directories containing trajectory.jsonl found")
        sub_res.is_valid = False
        return sub_res

    # Audit each run
    completed_seeds: Set[int] = set()
    for rdir in sorted(candidate_dirs, key=lambda p: p.name):
        traj_p = rdir / "trajectory.jsonl"
        man_p = rdir / "trajectory_manifest.json"
        run_audit = audit_trajectory_file(
            traj_p,
            manifest_path=man_p if man_p.exists() else None,
            expected_model=expected_model,
        )
        if run_audit.seed != -1:
            completed_seeds.add(run_audit.seed)
        sub_res.runs.append(run_audit)
        if not run_audit.is_valid:
            sub_res.errors.extend([f"[{run_audit.run_id}] {e}" for e in run_audit.errors])

    # Check seeds completeness if requested
    target_seeds = expected_seeds or [42, 43, 44, 45, 46]
    missing_seeds = set(target_seeds) - completed_seeds
    if missing_seeds:
        sub_res.warnings.append(f"Missing expected seeds: {sorted(list(missing_seeds))}")

    # Check total tasks per run if strict
    if strict_tasks is not None:
        for r in sub_res.runs:
            if r.total_tasks < strict_tasks:
                sub_res.errors.append(f"[{r.run_id}] Insufficient tasks: {r.total_tasks} < {strict_tasks}")

    sub_res.is_valid = len(sub_res.errors) == 0 and len(sub_res.runs) > 0
    return sub_res


def audit_submission(
    submission_path: Path,
    strict_tasks: Optional[int] = None,
    expected_seeds: Optional[List[int]] = None,
    expected_model: Optional[str] = None,
) -> SubmissionAuditResult:
    """Audit either a zip archive or a directory."""
    sub_path = Path(submission_path)
    if not sub_path.exists():
        res = SubmissionAuditResult(submission_path=str(sub_path))
        res.errors.append(f"Path does not exist: {sub_path}")
        return res

    if sub_path.is_file() and sub_path.suffix.lower() == ".zip":
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            try:
                with zipfile.ZipFile(sub_path, "r") as z:
                    z.extractall(tmp_path)
            except Exception as e:
                res = SubmissionAuditResult(submission_path=str(sub_path))
                res.errors.append(f"Failed to extract zip archive: {e}")
                return res

            # Handle case where zip contains an outer single folder
            entries = list(tmp_path.iterdir())
            if len(entries) == 1 and entries[0].is_dir() and (entries[0] / "runs").exists():
                search_root = entries[0]
            else:
                search_root = tmp_path

            return audit_submission_directory(
                search_root,
                str(sub_path),
                strict_tasks=strict_tasks,
                expected_seeds=expected_seeds,
                expected_model=expected_model,
            )
    elif sub_path.is_dir():
        return audit_submission_directory(
            sub_path,
            str(sub_path),
            strict_tasks=strict_tasks,
            expected_seeds=expected_seeds,
            expected_model=expected_model,
        )
    else:
        res = SubmissionAuditResult(submission_path=str(sub_path))
        res.errors.append(f"Unsupported submission format: {sub_path} (must be .zip or directory)")
        return res


def print_audit_report(results: List[SubmissionAuditResult]) -> None:
    """Format and print an audit summary table."""
    print("\n" + "=" * 80)
    print("SAGE DISTRIBUTED STUDY: CONTRIBUTOR SUBMISSION AUDIT REPORT")
    print("=" * 80)

    for sub in results:
        status_sym = "[PASS]" if sub.is_valid else "[FAIL]"
        print(f"\nSubmission: {Path(sub.submission_path).name}")
        print(f"  Status        : {status_sym}")
        print(f"  Contributor   : {sub.contributor_id} (Assigned: {sub.group})")
        print(f"  Runs Audited  : {sub.runs_found}")
        print(f"  State Markers : {sub.state_markers_found}")

        if sub.warnings:
            for w in sub.warnings:
                print(f"  [WARN] {w}")

        if sub.errors:
            for err in sub.errors:
                print(f"  [FAIL] {err}")

        # Run level breakdown
        print("  Run Details:")
        for r in sub.runs:
            print(
                f"    - {r.run_id}: tasks={r.total_tasks}, real={r.real_calls}, "
                f"fallback={r.fallback_calls}, tokens_out={r.total_tokens_out:,}, "
                f"models={r.models_seen}, pass_rate={r.passed_tasks}/{r.total_tasks}"
            )

    print("\n" + "=" * 80)
    all_valid = all(s.is_valid for s in results) if results else False
    if all_valid:
        print("OVERALL VERDICT: ALL SUBMISSIONS VERIFIED AUTHENTIC & COMPLETE")
    else:
        print("OVERALL VERDICT: ONE OR MORE SUBMISSIONS FAILED INTEGRITY VERIFICATION")
    print("=" * 80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit SAGE distributed contributor submissions for authenticity and completeness."
    )
    parser.add_argument(
        "--submission",
        "-s",
        type=Path,
        help="Path to an individual .zip submission or directory.",
    )
    parser.add_argument(
        "--submissions-dir",
        "-d",
        type=Path,
        help="Directory containing multiple submission .zip files or directories.",
    )
    parser.add_argument(
        "--strict-tasks",
        type=int,
        default=None,
        help="Enforce minimum total tasks per run (e.g. 100 for 1 cycle or 500 for 5 cycles).",
    )
    parser.add_argument(
        "--expected-model",
        type=str,
        default=None,
        help="Require specific model name in trajectories (e.g. 'qwen2.5-coder').",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to emit machine-readable JSON report.",
    )
    args = parser.parse_args()

    targets: List[Path] = []
    if args.submission:
        targets.append(args.submission)
    elif args.submissions_dir:
        sdir = args.submissions_dir
        if not sdir.exists():
            print(f"Error: directory does not exist: {sdir}", file=sys.stderr)
            sys.exit(1)
        # Find zips and directories
        zips = list(sdir.glob("*.zip"))
        subdirs = [p for p in sdir.iterdir() if p.is_dir() and not p.name.startswith(".")]
        targets.extend(sorted(zips + subdirs))
    else:
        # Default fallback: check current working directory for submission zips
        default_zips = list(Path.cwd().glob("*submission*.zip")) + list(Path.cwd().glob("*seeds*.zip"))
        if default_zips:
            targets.extend(default_zips)
        else:
            parser.print_help()
            sys.exit(1)

    results: List[SubmissionAuditResult] = []
    for t in targets:
        audit_res = audit_submission(
            t,
            strict_tasks=args.strict_tasks,
            expected_model=args.expected_model,
        )
        results.append(audit_res)

    print_audit_report(results)

    if args.json_out:
        out_dict = {
            "overall_valid": all(s.is_valid for s in results),
            "submissions": [asdict(s) for s in results],
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(out_dict, f, indent=2)
        print(f"JSON report written to: {args.json_out}")

    all_passed = all(s.is_valid for s in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
