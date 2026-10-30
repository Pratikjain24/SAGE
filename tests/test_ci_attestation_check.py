"""Unit tests for automated CI attestation checks and SQLite WAL verification.

Verifies:
1. SQLite WAL mode and database integrity.
2. Cryptographic hash-chain verification and HMAC signature checking.
3. Detection of tampered blocks in the SQLite ledger.
4. Schema validation of verification_attestation.json.
5. SAGE-Live CLI `attest verify`, `attest status`, and `attest inspect` subcommands.
"""

from __future__ import annotations
import json
import shutil
import sqlite3
from pathlib import Path
import pytest
from typer.testing import CliRunner

from sage_live.cli import (
    app,
    verify_sqlite_wal,
    verify_attestation_chain,
    verify_attestation_document,
)

runner = CliRunner()


@pytest.fixture
def repo_root() -> Path:
    """Return repository root path."""
    return Path(__file__).resolve().parent.parent


def test_sqlite_wal_journal_mode(repo_root: Path):
    """Verify that experiments/attestation.db is in SQLite WAL mode and passes integrity check."""
    db_path = repo_root / "experiments" / "attestation.db"
    assert db_path.exists(), f"Database not found at {db_path}"

    passed, message, details = verify_sqlite_wal(db_path)
    assert passed is True
    assert details["integrity"].lower() == "ok"
    assert details["journal_mode"].lower() == "wal"
    assert details["block_count"] >= 1


def test_attestation_chain_integrity(repo_root: Path):
    """Verify that the cryptographic hash chain in experiments/attestation.db is 100% intact."""
    db_path = repo_root / "experiments" / "attestation.db"
    key_path = repo_root / "experiments" / "attestation.key"

    passed, message, details = verify_attestation_chain(db_path, key_path=key_path, create_if_empty=False)
    assert passed is True
    assert details["chain_valid"] is True
    assert len(details["tampered_blocks"]) == 0
    assert details["total_blocks"] >= 1
    assert len(details["head_hash"]) == 64
    assert len(details["genesis_hash"]) == 64


def test_verification_attestation_document(repo_root: Path):
    """Verify that verification_attestation.json conforms to schema and contracts."""
    attest_json = repo_root / "verification_attestation.json"
    assert attest_json.exists()

    passed, message, details = verify_attestation_document(attest_json)
    assert passed is True
    assert details["version"] == "1.0.0"
    assert details["status"] == "VERIFIED"
    assert details["benchmark"] == "SAGE"
    assert details["has_ci_contract"] is True
    assert details["has_local_contract"] is True


def test_tampered_block_detection(tmp_path: Path, repo_root: Path):
    """Simulate malicious tampering of an attestation block in SQLite and verify detection."""
    # Copy authentic DB and key to temporary directory
    src_db = repo_root / "experiments" / "attestation.db"
    src_key = repo_root / "experiments" / "attestation.key"

    tampered_db = tmp_path / "tampered.db"
    tampered_key = tmp_path / "attestation.key"
    shutil.copy2(src_db, tampered_db)
    shutil.copy2(src_key, tampered_key)

    # Confirm authentic copy passes
    passed, _, details = verify_attestation_chain(tampered_db, key_path=tampered_key, create_if_empty=False)
    assert passed is True

    # Maliciously modify a block's current_hash in SQLite
    conn = sqlite3.connect(str(tampered_db))
    conn.execute("UPDATE attestation_blocks SET current_hash='0000000000000000000000000000000000000000000000000000000000000000' WHERE block_number=1;")
    conn.commit()
    conn.close()

    # Verify that the tamper detector flags block #1
    passed, msg, details = verify_attestation_chain(tampered_db, key_path=tampered_key, create_if_empty=False)
    assert passed is False
    assert 1 in details["tampered_blocks"]
    assert "compromised" in msg.lower()


def test_cli_attest_verify_command(repo_root: Path):
    """Test `sage-live attest verify` CLI execution."""
    result = runner.invoke(app, [
        "attest", "verify",
        "--db-path", str(repo_root / "experiments" / "attestation.db"),
        "--key-path", str(repo_root / "experiments" / "attestation.key"),
        "--attestation-json", str(repo_root / "verification_attestation.json"),
    ])
    assert result.exit_code == 0
    assert "PASS" in result.output
    assert "SQLite WAL Journaling" in result.output
    assert "Hash-Chain Cryptographic Integrity" in result.output


def test_cli_attest_status_and_inspect_commands(repo_root: Path):
    """Test `sage-live attest status` and `inspect` subcommands."""
    status_res = runner.invoke(app, [
        "attest", "status",
        "--db-path", str(repo_root / "experiments" / "attestation.db"),
        "--key-path", str(repo_root / "experiments" / "attestation.key"),
    ])
    assert status_res.exit_code == 0
    assert "VALID" in status_res.output

    inspect_res = runner.invoke(app, [
        "attest", "inspect",
        "--db-path", str(repo_root / "experiments" / "attestation.db"),
        "--limit", "3",
    ])
    assert inspect_res.exit_code == 0
    assert "Attestation Ledger" in inspect_res.output
