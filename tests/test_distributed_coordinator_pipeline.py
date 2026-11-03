"""Unit and integration tests for SAGE Distributed Coordinator Pipeline.

Tests:
1. scripts/verify_distributed_submissions.py:
   - Rejection of mock fallback invocations
   - Rejection of zero-token invocations
   - Manifest SHA-256 verification
   - Package unpacking and audit reporting
2. scripts/merge_distributed_runs.py:
   - Unified trajectory sorting and manifest generation
   - P1 vs P7 inter-hardware cross-check verification (|Δ| ≤ 2.5%)
   - Attestation ledger sealing
"""

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from scripts.merge_distributed_runs import (
    evaluate_cross_check,
    merge_trajectories,
)
from scripts.verify_distributed_submissions import (
    audit_submission,
    audit_trajectory_file,
)
from sage.runner.reproducibility import generate_trajectory_manifest


def make_dummy_event(
    event_type: str = "task_end",
    cycle: int = 1,
    seed: int = 42,
    group: str = "G1",
    task_id: str = "task_001",
    is_fallback: bool = False,
    tokens_in: int = 250,
    tokens_out: int = 120,
    model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
    success: bool = True,
) -> dict:
    return {
        "run_id": f"study_live_distributed_{group}_s{seed}",
        "cycle": cycle,
        "seed": seed,
        "group": group,
        "task_id": task_id,
        "agent_version": f"agent_{group}_v1",
        "ts": "2026-11-03T12:00:00Z",
        "event_type": event_type,
        "payload": {
            "success": success,
            "is_fallback": is_fallback,
            "model_name": model_name,
        },
        "cost": {
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "usd": 0.0005,
            "wall_ms": 1500,
        },
    }


def test_audit_trajectory_valid(tmp_path: Path):
    traj_path = tmp_path / "trajectory.jsonl"
    events = [
        make_dummy_event(task_id=f"task_{i}", tokens_in=200, tokens_out=100)
        for i in range(10)
    ]
    with open(traj_path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    res = audit_trajectory_file(traj_path)
    assert res.is_valid is True
    assert res.total_tasks == 10
    assert res.real_calls == 10
    assert res.fallback_calls == 0
    assert res.zero_token_calls == 0
    assert res.total_tokens_in == 2000
    assert res.total_tokens_out == 1000
    assert "Qwen/Qwen2.5-Coder-7B-Instruct" in res.models_seen


def test_audit_trajectory_rejects_mock_fallback(tmp_path: Path):
    traj_path = tmp_path / "trajectory.jsonl"
    events = [
        make_dummy_event(task_id="task_001", is_fallback=False),
        make_dummy_event(task_id="task_002", is_fallback=True),  # Mock fallback!
    ]
    with open(traj_path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    res = audit_trajectory_file(traj_path)
    assert res.is_valid is False
    assert res.fallback_calls == 1
    assert any("mock fallback" in err for err in res.errors)


def test_audit_trajectory_rejects_zero_tokens(tmp_path: Path):
    traj_path = tmp_path / "trajectory.jsonl"
    events = [
        make_dummy_event(task_id="task_001", tokens_in=0, tokens_out=0),  # Zero tokens!
    ]
    with open(traj_path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    res = audit_trajectory_file(traj_path)
    assert res.is_valid is False
    assert res.zero_token_calls == 1
    assert any("0 tokens" in err for err in res.errors)


def test_audit_trajectory_manifest_verification(tmp_path: Path):
    traj_path = tmp_path / "trajectory.jsonl"
    events = [make_dummy_event(task_id="task_001")]
    with open(traj_path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    man_file = generate_trajectory_manifest(tmp_path)
    res = audit_trajectory_file(traj_path, manifest_path=man_file)
    assert res.is_valid is True
    assert res.manifest_verified is True

    # Tamper with trajectory and verify audit flags mismatch
    with open(traj_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(make_dummy_event(task_id="task_tamper")) + "\n")

    tampered_res = audit_trajectory_file(traj_path, manifest_path=man_file)
    assert tampered_res.is_valid is False
    assert any("mismatch" in err.lower() for err in tampered_res.errors)


def test_audit_zip_submission(tmp_path: Path):
    pkg_dir = tmp_path / "G1_seeds42-46_submission"
    runs_dir = pkg_dir / "runs" / "study_live_distributed_G1_s42"
    runs_dir.mkdir(parents=True, exist_ok=True)
    state_dir = pkg_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "done_G1_42").touch()

    (pkg_dir / "notes.txt").write_text(
        "Contributor ID : P1\nAssigned Layer : G1\nSeeds Tested   : [42]\n",
        encoding="utf-8",
    )

    traj_path = runs_dir / "trajectory.jsonl"
    with open(traj_path, "w", encoding="utf-8") as f:
        for i in range(5):
            f.write(json.dumps(make_dummy_event(task_id=f"task_{i}")) + "\n")

    zip_file = tmp_path / "G1_seeds42-46.zip"
    shutil.make_archive(str(tmp_path / "G1_seeds42-46"), "zip", pkg_dir)

    sub_res = audit_submission(zip_file, expected_seeds=[42])
    assert sub_res.is_valid is True
    assert sub_res.contributor_id == "P1"
    assert sub_res.group == "G1"
    assert sub_res.state_markers_found == 1
    assert sub_res.runs_found == 1


def test_inter_hardware_cross_check_replication():
    # P1 G1 solve rate: 80% (8/10 passed)
    p1_events = [
        make_dummy_event(task_id=f"p1_{i}", group="G1", success=(i < 8))
        for i in range(10)
    ]
    # P7 G1 replication: 80% (8/10 passed)
    p7_events = [
        make_dummy_event(task_id=f"p7_{i}", group="G1", success=(i < 8))
        for i in range(10)
    ]

    res = evaluate_cross_check(p1_events, p7_events, tolerance=0.025)
    assert res.passed is True
    assert res.delta == 0.0

    # Test discrepancy exceeding tolerance (e.g. 80% vs 50% -> delta = 30%)
    p7_divergent = [
        make_dummy_event(task_id=f"p7_{i}", group="G1", success=(i < 5))
        for i in range(10)
    ]
    div_res = evaluate_cross_check(p1_events, p7_divergent, tolerance=0.025)
    assert div_res.passed is False
    assert div_res.delta == pytest.approx(0.30, abs=1e-5)


def test_merge_trajectories_and_attestation_sealing(tmp_path: Path):
    run_dir_1 = tmp_path / "runs" / "study_live_distributed_G1_s42"
    run_dir_2 = tmp_path / "runs" / "study_live_distributed_G2_s42"
    run_dir_1.mkdir(parents=True, exist_ok=True)
    run_dir_2.mkdir(parents=True, exist_ok=True)

    with open(run_dir_1 / "trajectory.jsonl", "w", encoding="utf-8") as f:
        for i in range(5):
            f.write(json.dumps(make_dummy_event(task_id=f"g1_task_{i}", group="G1")) + "\n")

    with open(run_dir_2 / "trajectory.jsonl", "w", encoding="utf-8") as f:
        for i in range(5):
            f.write(json.dumps(make_dummy_event(task_id=f"g2_task_{i}", group="G2")) + "\n")

    out_dir = tmp_path / "merged_out"
    db_path = tmp_path / "test_attestation.db"
    merged_p, _ = merge_trajectories(
        run_dirs=[run_dir_1, run_dir_2],
        output_dir=out_dir,
        db_path=db_path,
        secret_key="test_merger_secret_key_12345678901234",
    )

    assert merged_p.exists()
    assert (out_dir / "trajectory_manifest.json").exists()

    # Read merged lines
    lines = [json.loads(l) for l in merged_p.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 10
    groups_in_merged = {l["group"] for l in lines}
    assert groups_in_merged == {"G1", "G2"}

    # Verify Attestation Ledger sealing
    from sage_live.core.attestation import AttestationLedger

    ledger = AttestationLedger(
        secret_key="test_merger_secret_key_12345678901234",
        db_path=str(db_path),
    )
    assert ledger.chain_length > 0
    assert ledger.verify_chain_integrity() is True
