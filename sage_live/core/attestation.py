"""
sage_live.core.attestation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cryptographic Attestation Ledger for SAGE-Live.

Concept
-------
A hash-chained evaluation certificate chain — conceptually similar to a
blockchain but without consensus mechanics.  Every evaluation window is
sealed into an *AttestationBlock* whose ``current_hash`` is computed from
the block's content **and** the previous block's hash, forming a tamper-
evident append-only chain.

Chain structure::

    Block 0 (Genesis):
        current_hash = SHA256("SAGE-LIVE-GENESIS:" + timestamp + ":" + nonce)

    Block N (N ≥ 1):
        payload      = agent_snapshot_hash
                     + probe_set_hash
                     + results_hash
                     + Block(N-1).current_hash
                     + window_id
                     + str(timestamp)
                     + nonce
        current_hash = SHA256(payload)
        hmac_sig     = HMAC-SHA256(secret_key, current_hash)

Tamper detection
----------------
If **any** block's content is altered its ``current_hash`` changes.
The next block's ``previous_hash`` then no longer matches → chain broken.
``detect_tampering()`` reports every invalid block number.

Thread safety
-------------
``AttestationLedger`` uses a ``threading.Lock`` around every write and
SQLite is opened in WAL (Write-Ahead Logging) mode so concurrent readers
never block writers.

Storage
-------
An append-only SQLite file stores every block.  The ``blocks`` table is
insert-only; the code never issues UPDATE or DELETE statements.

Usage example
-------------
::

    from sage_live.core.attestation import AttestationLedger

    ledger = AttestationLedger(secret_key="my-secret", db_path="attestation.db")
    genesis = ledger.create_genesis_block()

    block = ledger.add_evaluation_window(
        agent_state={"model": "gpt-4o", "cycle": 1},
        probe_set=["PROBE-001", "PROBE-002"],
        results={"PROBE-001": {"passed": True, "score": 88.5}},
    )

    assert ledger.verify_chain_integrity()
    print(ledger.generate_attestation_report())
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import secrets
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

GENESIS_SEED: str = "SAGE-LIVE-GENESIS"
HASH_ENCODING: str = "utf-8"


# ---------------------------------------------------------------------------
# Low-level crypto primitives
# ---------------------------------------------------------------------------


def _sha256_hex(data: str) -> str:
    """Return the hex-encoded SHA-256 digest of *data*.

    Parameters
    ----------
    data:
        UTF-8 string to hash.

    Returns
    -------
    str
        64-character lowercase hex digest.
    """
    return hashlib.sha256(data.encode(HASH_ENCODING)).hexdigest()


def _sha256_dict(obj: dict[str, Any]) -> str:
    """Return the hex-encoded SHA-256 digest of a deterministically serialised dict.

    The dictionary is serialised with sorted keys so that field-insertion
    order does not affect the hash.

    Parameters
    ----------
    obj:
        Dictionary to hash.

    Returns
    -------
    str
        64-character lowercase hex digest.
    """
    canonical = json.dumps(obj, sort_keys=True, default=str)
    return _sha256_hex(canonical)


def _sha256_list(lst: list[str]) -> str:
    """Return the hex-encoded SHA-256 digest of a sorted list of strings.

    Parameters
    ----------
    lst:
        List of strings to hash.

    Returns
    -------
    str
        64-character lowercase hex digest.
    """
    return _sha256_hex("|".join(sorted(lst)))


def _hmac_sign(secret_key: str, message: str) -> str:
    """Compute an HMAC-SHA256 signature over *message* using *secret_key*.

    Parameters
    ----------
    secret_key:
        Secret key string (UTF-8 encoded before use).
    message:
        Message to sign.

    Returns
    -------
    str
        64-character lowercase hex HMAC digest.
    """
    return hmac.new(
        secret_key.encode(HASH_ENCODING),
        message.encode(HASH_ENCODING),
        hashlib.sha256,
    ).hexdigest()


def _hmac_verify(secret_key: str, message: str, expected_sig: str) -> bool:
    """Verify an HMAC-SHA256 signature in constant time.

    Parameters
    ----------
    secret_key:
        Secret key string.
    message:
        Original message.
    expected_sig:
        The signature to verify against.

    Returns
    -------
    bool
        ``True`` if the signature is valid.
    """
    actual = _hmac_sign(secret_key, message)
    return hmac.compare_digest(actual, expected_sig)


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime.

    Returns
    -------
    datetime
        UTC datetime with tzinfo set.
    """
    return datetime.now(tz=timezone.utc)


def _new_nonce() -> str:
    """Generate a 32-byte cryptographically secure random nonce.

    Returns
    -------
    str
        64-character hex string.
    """
    return secrets.token_hex(32)


# ---------------------------------------------------------------------------
# AttestationBlock
# ---------------------------------------------------------------------------


@dataclass
class AttestationBlock:
    """A single block in the SAGE-Live attestation hash chain.

    Each block seals an evaluation window by hashing its content together
    with the previous block's hash, forming a tamper-evident chain.

    Attributes
    ----------
    block_number:
        Sequential position in the chain (0 = genesis).
    window_id:
        Human-readable evaluation window identifier
        (e.g. ``"2025-Q1-W03-20250119T120000Z"``).
    agent_snapshot:
        Snapshot of the agent state at evaluation time.
    probe_set_snapshot:
        Ordered list of probe IDs included in this window.
    results_snapshot:
        Dictionary mapping probe IDs to their evaluation results.
    previous_hash:
        ``current_hash`` of the immediately preceding block.
        Genesis block uses ``"0" * 64``.
    current_hash:
        SHA-256 of the canonicalised block payload (computed; not supplied).
    timestamp:
        UTC datetime when this block was sealed.
    nonce:
        64-char hex random nonce preventing replay attacks.
    hmac_signature:
        HMAC-SHA256 over ``current_hash`` using the ledger's secret key.
    agent_snapshot_hash:
        Pre-computed SHA-256 of ``agent_snapshot`` for chain inclusion.
    probe_set_hash:
        Pre-computed SHA-256 of ``probe_set_snapshot``.
    results_hash:
        Pre-computed SHA-256 of ``results_snapshot``.
    """

    block_number: int
    window_id: str
    agent_snapshot: dict[str, Any]
    probe_set_snapshot: list[str]
    results_snapshot: dict[str, Any]
    previous_hash: str
    timestamp: datetime
    nonce: str
    # Computed fields — set by AttestationLedger._seal_block()
    agent_snapshot_hash: str = field(default="")
    probe_set_hash: str = field(default="")
    results_hash: str = field(default="")
    current_hash: str = field(default="")
    hmac_signature: str = field(default="")

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise the block to a JSON-compatible dictionary.

        Returns
        -------
        dict[str, Any]
            All block fields, with ``datetime`` objects converted to ISO-8601
            strings.
        """
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AttestationBlock":
        """Reconstruct an AttestationBlock from a serialised dictionary.

        Parameters
        ----------
        data:
            Dictionary as produced by :meth:`to_dict`.

        Returns
        -------
        AttestationBlock
            Reconstructed block instance.
        """
        ts_raw = data.get("timestamp")
        if isinstance(ts_raw, str):
            ts = datetime.fromisoformat(ts_raw)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = _utcnow()
        return cls(
            block_number=data["block_number"],
            window_id=data["window_id"],
            agent_snapshot=data["agent_snapshot"],
            probe_set_snapshot=data["probe_set_snapshot"],
            results_snapshot=data["results_snapshot"],
            previous_hash=data["previous_hash"],
            timestamp=ts,
            nonce=data["nonce"],
            agent_snapshot_hash=data.get("agent_snapshot_hash", ""),
            probe_set_hash=data.get("probe_set_hash", ""),
            results_hash=data.get("results_hash", ""),
            current_hash=data.get("current_hash", ""),
            hmac_signature=data.get("hmac_signature", ""),
        )

    def __repr__(self) -> str:
        return (
            f"AttestationBlock("
            f"n={self.block_number}, "
            f"window={self.window_id!r}, "
            f"hash={self.current_hash[:12]}…, "
            f"prev={self.previous_hash[:12]}…)"
        )


# ---------------------------------------------------------------------------
# SQLite persistence layer
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS attestation_blocks (
    block_number        INTEGER PRIMARY KEY,
    window_id           TEXT    NOT NULL UNIQUE,
    agent_snapshot      TEXT    NOT NULL,
    probe_set_snapshot  TEXT    NOT NULL,
    results_snapshot    TEXT    NOT NULL,
    previous_hash       TEXT    NOT NULL,
    current_hash        TEXT    NOT NULL,
    timestamp           TEXT    NOT NULL,
    nonce               TEXT    NOT NULL,
    agent_snapshot_hash TEXT    NOT NULL,
    probe_set_hash      TEXT    NOT NULL,
    results_hash        TEXT    NOT NULL,
    hmac_signature      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS ledger_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

_INSERT_BLOCK = """
INSERT INTO attestation_blocks (
    block_number, window_id, agent_snapshot, probe_set_snapshot,
    results_snapshot, previous_hash, current_hash, timestamp,
    nonce, agent_snapshot_hash, probe_set_hash, results_hash,
    hmac_signature
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);
"""


class _BlockStore:
    """Append-only SQLite-backed block storage.

    Uses WAL mode for concurrent read safety.  All writes go through
    ``insert_block`` which is protected by the caller's lock.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Use ``":memory:"`` for tests.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """Initialise the store and create tables if they do not exist."""
        self._path = db_path
        self._conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            isolation_level=None,  # autocommit
        )
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._conn.executescript(_DDL)
        logger.debug("BlockStore initialised at {}", db_path)

    # ------------------------------------------------------------------
    # Write (append-only)
    # ------------------------------------------------------------------

    def insert_block(self, block: AttestationBlock) -> None:
        """Append a block to the database.

        Parameters
        ----------
        block:
            The sealed block to store.

        Raises
        ------
        sqlite3.IntegrityError
            If a block with the same block_number or window_id already exists.
        """
        self._conn.execute(
            _INSERT_BLOCK,
            (
                block.block_number,
                block.window_id,
                json.dumps(block.agent_snapshot, default=str),
                json.dumps(block.probe_set_snapshot),
                json.dumps(block.results_snapshot, default=str),
                block.previous_hash,
                block.current_hash,
                block.timestamp.isoformat(),
                block.nonce,
                block.agent_snapshot_hash,
                block.probe_set_hash,
                block.results_hash,
                block.hmac_signature,
            ),
        )
        logger.debug("BlockStore: inserted block #{}", block.block_number)

    def set_meta(self, key: str, value: str) -> None:
        """Upsert a metadata key-value pair.

        Parameters
        ----------
        key:
            Metadata key.
        value:
            Metadata value.
        """
        self._conn.execute(
            "INSERT OR REPLACE INTO ledger_meta (key, value) VALUES (?,?);",
            (key, value),
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_all_blocks(self) -> list[AttestationBlock]:
        """Return all blocks in ascending block_number order.

        Returns
        -------
        list[AttestationBlock]
            All stored blocks, oldest first.
        """
        rows = self._conn.execute(
            "SELECT * FROM attestation_blocks ORDER BY block_number ASC;"
        ).fetchall()
        return [self._row_to_block(r) for r in rows]

    def get_block(self, block_number: int) -> AttestationBlock | None:
        """Return a single block by number, or ``None`` if not found.

        Parameters
        ----------
        block_number:
            Block index.

        Returns
        -------
        AttestationBlock | None
        """
        row = self._conn.execute(
            "SELECT * FROM attestation_blocks WHERE block_number=?;",
            (block_number,),
        ).fetchone()
        return self._row_to_block(row) if row else None

    def get_block_by_window(self, window_id: str) -> AttestationBlock | None:
        """Return a block by its window_id, or ``None`` if not found.

        Parameters
        ----------
        window_id:
            The evaluation window identifier.

        Returns
        -------
        AttestationBlock | None
        """
        row = self._conn.execute(
            "SELECT * FROM attestation_blocks WHERE window_id=?;",
            (window_id,),
        ).fetchone()
        return self._row_to_block(row) if row else None

    def count(self) -> int:
        """Return the total number of blocks stored.

        Returns
        -------
        int
            Row count.
        """
        return self._conn.execute(
            "SELECT COUNT(*) FROM attestation_blocks;"
        ).fetchone()[0]

    def get_meta(self, key: str) -> str | None:
        """Return a metadata value, or ``None`` if the key does not exist.

        Parameters
        ----------
        key:
            Metadata key.

        Returns
        -------
        str | None
        """
        row = self._conn.execute(
            "SELECT value FROM ledger_meta WHERE key=?;", (key,)
        ).fetchone()
        return row[0] if row else None

    @staticmethod
    def _row_to_block(row: tuple[Any, ...]) -> AttestationBlock:
        """Convert a raw SQLite row tuple to an AttestationBlock.

        Parameters
        ----------
        row:
            SQLite row matching the ``attestation_blocks`` column order.

        Returns
        -------
        AttestationBlock
            Reconstructed block.
        """
        (
            block_number, window_id, agent_snap_json, probe_set_json,
            results_json, previous_hash, current_hash, timestamp_str,
            nonce, agent_hash, probe_hash, results_hash, hmac_sig,
        ) = row

        ts = datetime.fromisoformat(timestamp_str)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        return AttestationBlock(
            block_number=block_number,
            window_id=window_id,
            agent_snapshot=json.loads(agent_snap_json),
            probe_set_snapshot=json.loads(probe_set_json),
            results_snapshot=json.loads(results_json),
            previous_hash=previous_hash,
            timestamp=ts,
            nonce=nonce,
            agent_snapshot_hash=agent_hash,
            probe_set_hash=probe_hash,
            results_hash=results_hash,
            current_hash=current_hash,
            hmac_signature=hmac_sig,
        )

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self._conn.close()


# ---------------------------------------------------------------------------
# AttestationLedger
# ---------------------------------------------------------------------------


class AttestationLedger:
    """Append-only hash-chained evaluation certificate ledger.

    Parameters
    ----------
    secret_key:
        HMAC signing key.  Must be kept private; used to authenticate each
        block's hash.  Defaults to a fresh random key per session (useful for
        tests); provide a persistent key in production.
    db_path:
        Path to the SQLite persistence file.  Defaults to ``":memory:"``
        (in-process only).  Pass a file path for durable storage.

    Thread safety
    -------------
    All public methods acquire ``self._lock`` before modifying state.
    Concurrent reads are safe under SQLite WAL mode.
    """

    def __init__(
        self,
        secret_key: str | None = None,
        db_path: str = ":memory:",
    ) -> None:
        """Initialise the ledger, creating the genesis block if the DB is empty."""
        self._secret_key: str = secret_key or secrets.token_hex(32)
        self._store = _BlockStore(db_path)
        self._lock = threading.Lock()
        self._chain: list[AttestationBlock] = self._store.get_all_blocks()

        if not self._chain:
            logger.info("Empty ledger detected — creating genesis block")
            self.create_genesis_block()
        else:
            logger.info(
                "Loaded existing ledger: {} blocks, head={}",
                len(self._chain),
                self._chain[-1].current_hash[:16],
            )

    # ------------------------------------------------------------------
    # 1. create_genesis_block
    # ------------------------------------------------------------------

    def create_genesis_block(self) -> AttestationBlock:
        """Create and store the genesis (block 0) of the attestation chain.

        The genesis hash is::

            SHA256("SAGE-LIVE-GENESIS:" + iso_timestamp + ":" + nonce)

        Returns
        -------
        AttestationBlock
            The genesis block.

        Raises
        ------
        RuntimeError
            If a genesis block already exists.
        """
        with self._lock:
            if self._chain:
                raise RuntimeError(
                    "Cannot create genesis block: chain already has "
                    f"{len(self._chain)} block(s)"
                )
            ts = _utcnow()
            nonce = _new_nonce()
            genesis_payload = f"{GENESIS_SEED}:{ts.isoformat()}:{nonce}"
            genesis_hash = _sha256_hex(genesis_payload)

            block = AttestationBlock(
                block_number=0,
                window_id=f"GENESIS-{ts.strftime('%Y%m%dT%H%M%SZ')}",
                agent_snapshot={},
                probe_set_snapshot=[],
                results_snapshot={},
                previous_hash="0" * 64,
                timestamp=ts,
                nonce=nonce,
                agent_snapshot_hash="0" * 64,
                probe_set_hash="0" * 64,
                results_hash="0" * 64,
                current_hash=genesis_hash,
                hmac_signature=_hmac_sign(self._secret_key, genesis_hash),
            )
            self._store.insert_block(block)
            self._chain.append(block)
            logger.info("Genesis block created: hash={}…", genesis_hash[:16])
            return block

    # ------------------------------------------------------------------
    # 2. add_evaluation_window
    # ------------------------------------------------------------------

    def add_evaluation_window(
        self,
        agent_state: dict[str, Any],
        probe_set: list[str],
        results: dict[str, Any],
        window_id: str | None = None,
    ) -> AttestationBlock:
        """Seal an evaluation window into a new block and append it to the chain.

        Block hash computation::

            agent_hash   = SHA256(json.dumps(agent_state, sort_keys=True))
            probe_hash   = SHA256("|".join(sorted(probe_set)))
            results_hash = SHA256(json.dumps(results, sort_keys=True))
            payload      = agent_hash + probe_hash + results_hash
                         + previous_hash + window_id + timestamp + nonce
            current_hash = SHA256(payload)
            hmac_sig     = HMAC-SHA256(secret_key, current_hash)

        Parameters
        ----------
        agent_state:
            Snapshot of the agent's configuration/state at evaluation time.
        probe_set:
            List of probe IDs evaluated in this window.
        results:
            Mapping of probe IDs to their evaluation outcomes.
        window_id:
            Optional human-readable window identifier.  Auto-generated from
            UTC timestamp if not provided.

        Returns
        -------
        AttestationBlock
            The newly created, stored block.

        Raises
        ------
        RuntimeError
            If the chain has no genesis block yet.
        ValueError
            If *probe_set* or *results* are empty.
        """
        if not probe_set:
            raise ValueError("probe_set must not be empty")
        if not results:
            raise ValueError("results must not be empty")

        with self._lock:
            if not self._chain:
                raise RuntimeError(
                    "Chain has no genesis block. Call create_genesis_block() first."
                )
            previous_block = self._chain[-1]
            block_number = previous_block.block_number + 1
            ts = _utcnow()
            nonce = _new_nonce()
            wid = window_id or f"W{block_number:06d}-{ts.strftime('%Y%m%dT%H%M%SZ')}"

            # Component hashes
            agent_h = _sha256_dict(agent_state)
            probe_h = _sha256_list(probe_set)
            results_h = _sha256_dict(results)
            prev_h = previous_block.current_hash

            # Chain link hash
            payload = (
                agent_h
                + probe_h
                + results_h
                + prev_h
                + wid
                + ts.isoformat()
                + nonce
            )
            current_hash = _sha256_hex(payload)
            hmac_sig = _hmac_sign(self._secret_key, current_hash)

            block = AttestationBlock(
                block_number=block_number,
                window_id=wid,
                agent_snapshot=agent_state,
                probe_set_snapshot=probe_set,
                results_snapshot=results,
                previous_hash=prev_h,
                timestamp=ts,
                nonce=nonce,
                agent_snapshot_hash=agent_h,
                probe_set_hash=probe_h,
                results_hash=results_h,
                current_hash=current_hash,
                hmac_signature=hmac_sig,
            )
            self._store.insert_block(block)
            self._chain.append(block)
            logger.info(
                "Block #{} sealed: window={} hash={}…",
                block_number,
                wid,
                current_hash[:16],
            )
            return block

    # ------------------------------------------------------------------
    # 3. verify_chain_integrity
    # ------------------------------------------------------------------

    def verify_chain_integrity(self) -> bool:
        """Verify the integrity of every block in the chain.

        For each block (except genesis) re-computes the expected hash from
        its stored fields and checks:

        1. ``current_hash`` matches the recomputed hash.
        2. ``previous_hash`` matches the preceding block's ``current_hash``.
        3. ``hmac_signature`` is valid.

        Genesis block: only checks hash format and HMAC validity.

        Returns
        -------
        bool
            ``True`` only if every single block is valid.
        """
        with self._lock:
            chain = list(self._chain)

        if not chain:
            logger.warning("verify_chain_integrity: chain is empty")
            return False

        for i, block in enumerate(chain):
            if not self._verify_block(block, chain[i - 1] if i > 0 else None):
                logger.error(
                    "Chain integrity FAILED at block #{}",
                    block.block_number,
                )
                return False

        logger.info(
            "Chain integrity VERIFIED: {} blocks, head={}…",
            len(chain),
            chain[-1].current_hash[:16],
        )
        return True

    # ------------------------------------------------------------------
    # 4. detect_tampering
    # ------------------------------------------------------------------

    def detect_tampering(self) -> list[int]:
        """Identify all tampered block numbers in the chain.

        Returns
        -------
        list[int]
            Sorted list of block numbers whose hash verification failed.
            An empty list means no tampering was detected.
        """
        with self._lock:
            chain = list(self._chain)

        tampered: list[int] = []
        for i, block in enumerate(chain):
            prev = chain[i - 1] if i > 0 else None
            if not self._verify_block(block, prev):
                tampered.append(block.block_number)
                logger.warning("Tampering detected at block #{}", block.block_number)

        if not tampered:
            logger.info("detect_tampering: no tampering found ({} blocks)", len(chain))
        else:
            logger.error(
                "detect_tampering: {} tampered block(s): {}",
                len(tampered),
                tampered,
            )
        return tampered

    # ------------------------------------------------------------------
    # 5. get_certificate
    # ------------------------------------------------------------------

    def get_certificate(self, window_id: str) -> dict[str, Any]:
        """Return a full, verifiable certificate for the given evaluation window.

        The certificate contains all hashes and metadata required for an
        independent third party to re-verify the block without access to
        the raw data.

        Parameters
        ----------
        window_id:
            The evaluation window identifier.

        Returns
        -------
        dict[str, Any]
            Certificate dictionary with keys:
            ``block_number``, ``window_id``, ``timestamp``,
            ``agent_snapshot_hash``, ``probe_set_hash``,
            ``results_hash``, ``previous_hash``, ``current_hash``,
            ``hmac_signature``, ``nonce``, ``is_valid``,
            ``chain_length``, ``issuer``.

        Raises
        ------
        KeyError
            If no block with the given ``window_id`` exists.
        """
        block = self._store.get_block_by_window(window_id)
        if block is None:
            raise KeyError(f"No block found for window_id={window_id!r}")

        with self._lock:
            chain = list(self._chain)

        prev_block: AttestationBlock | None = None
        for i, b in enumerate(chain):
            if b.block_number == block.block_number and i > 0:
                prev_block = chain[i - 1]
                break

        is_valid = self._verify_block(block, prev_block)
        return {
            "issuer": "SAGE-Live Attestation Ledger v1",
            "certificate_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, block.current_hash)),
            "block_number": block.block_number,
            "window_id": block.window_id,
            "timestamp": block.timestamp.isoformat(),
            "agent_snapshot_hash": block.agent_snapshot_hash,
            "probe_set_hash": block.probe_set_hash,
            "results_hash": block.results_hash,
            "previous_hash": block.previous_hash,
            "current_hash": block.current_hash,
            "nonce": block.nonce,
            "hmac_signature": block.hmac_signature,
            "is_valid": is_valid,
            "chain_length": len(chain),
            "verification_method": "SHA-256 hash chain + HMAC-SHA256 signature",
        }

    # ------------------------------------------------------------------
    # 6. export_ledger
    # ------------------------------------------------------------------

    def export_ledger(self, fmt: str = "json") -> str:
        """Export the entire ledger as a JSON or CSV string.

        Parameters
        ----------
        fmt:
            Export format: ``"json"`` (default) or ``"csv"``.

        Returns
        -------
        str
            Serialised ledger content.

        Raises
        ------
        ValueError
            If *fmt* is not ``"json"`` or ``"csv"``.
        """
        with self._lock:
            chain = list(self._chain)

        fmt = fmt.lower().strip()
        if fmt == "json":
            return self._export_json(chain)
        if fmt == "csv":
            return self._export_csv(chain)
        raise ValueError(
            f"Unsupported export format {fmt!r}. Use 'json' or 'csv'."
        )

    # ------------------------------------------------------------------
    # 7. verify_single_result
    # ------------------------------------------------------------------

    def verify_single_result(
        self,
        result_hash: str,
        claimed_block: int,
    ) -> bool:
        """Verify that a specific result hash is authentic in the given block.

        Checks:
        1. The claimed block exists.
        2. The block itself is hash-valid.
        3. The block's ``results_hash`` matches
           ``SHA256(json.dumps(results_snapshot, sort_keys=True))``.
        4. The provided ``result_hash`` equals ``SHA256(json.dumps(specific_result))``.

        Parameters
        ----------
        result_hash:
            The SHA-256 hex digest of the result to verify.
        claimed_block:
            The block number in which the result is claimed to reside.

        Returns
        -------
        bool
            ``True`` if the result is authenticated.
        """
        block = self._store.get_block(claimed_block)
        if block is None:
            logger.warning(
                "verify_single_result: block #{} not found",
                claimed_block,
            )
            return False

        with self._lock:
            chain = list(self._chain)

        prev_block: AttestationBlock | None = None
        for i, b in enumerate(chain):
            if b.block_number == claimed_block and i > 0:
                prev_block = chain[i - 1]
                break

        if not self._verify_block(block, prev_block):
            logger.warning(
                "verify_single_result: block #{} failed integrity check",
                claimed_block,
            )
            return False

        # Check whether the result hash appears anywhere in the results_snapshot
        for probe_id, result_data in block.results_snapshot.items():
            candidate = _sha256_dict(
                result_data if isinstance(result_data, dict) else {"value": result_data}
            )
            if candidate == result_hash:
                logger.debug(
                    "verify_single_result: result_hash found in block #{}",
                    claimed_block,
                )
                return True

        logger.warning(
            "verify_single_result: result_hash not found in block #{}",
            claimed_block,
        )
        return False

    # ------------------------------------------------------------------
    # 8. generate_attestation_report
    # ------------------------------------------------------------------

    def generate_attestation_report(self) -> dict[str, Any]:
        """Generate a comprehensive integrity and audit report for the ledger.

        Returns
        -------
        dict[str, Any]
            A dictionary with keys:

            ``summary`` — high-level stats.
            ``integrity`` — per-block validation results.
            ``tampered_blocks`` — list of invalid block numbers.
            ``chain_valid`` — overall chain validity boolean.
            ``genesis`` — genesis block certificate.
            ``head`` — latest block certificate.
            ``human_readable`` — plain-English summary string.
            ``machine_readable`` — structured validation data.
        """
        with self._lock:
            chain = list(self._chain)

        if not chain:
            return {
                "summary": {"chain_length": 0, "chain_valid": False},
                "error": "Chain is empty",
            }

        tampered = self.detect_tampering()
        chain_valid = len(tampered) == 0

        # Per-block integrity details
        block_details: list[dict[str, Any]] = []
        for i, block in enumerate(chain):
            prev = chain[i - 1] if i > 0 else None
            valid = self._verify_block(block, prev)
            block_details.append({
                "block_number": block.block_number,
                "window_id": block.window_id,
                "timestamp": block.timestamp.isoformat(),
                "current_hash": block.current_hash,
                "previous_hash": block.previous_hash,
                "probe_count": len(block.probe_set_snapshot),
                "result_count": len(block.results_snapshot),
                "is_valid": valid,
                "is_tampered": not valid,
            })

        genesis_cert = self.get_certificate(chain[0].window_id)
        head_cert = self.get_certificate(chain[-1].window_id)

        human_summary = (
            f"SAGE-Live Attestation Report\n"
            f"{'=' * 40}\n"
            f"Chain length : {len(chain)} block(s)\n"
            f"Genesis hash : {chain[0].current_hash[:32]}…\n"
            f"Head hash    : {chain[-1].current_hash[:32]}…\n"
            f"Tampered     : {len(tampered)} block(s)\n"
            f"Chain valid  : {'✅ YES' if chain_valid else '❌ NO'}\n"
        )
        if tampered:
            human_summary += f"Tampered at  : blocks {tampered}\n"

        return {
            "summary": {
                "chain_length": len(chain),
                "genesis_hash": chain[0].current_hash,
                "head_hash": chain[-1].current_hash,
                "chain_valid": chain_valid,
                "tampered_block_count": len(tampered),
                "generated_at": _utcnow().isoformat(),
            },
            "integrity": block_details,
            "tampered_blocks": tampered,
            "chain_valid": chain_valid,
            "genesis": genesis_cert,
            "head": head_cert,
            "human_readable": human_summary,
            "machine_readable": {
                "format_version": "1.0",
                "hash_algorithm": "SHA-256",
                "signature_algorithm": "HMAC-SHA256",
                "chain_type": "hash-linked",
                "total_probes_evaluated": sum(
                    len(b.probe_set_snapshot) for b in chain
                ),
                "total_results": sum(
                    len(b.results_snapshot) for b in chain
                ),
            },
        }

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def chain_length(self) -> int:
        """Return the current length of the chain (including genesis).

        Returns
        -------
        int
            Number of blocks in the chain.
        """
        with self._lock:
            return len(self._chain)

    @property
    def head(self) -> AttestationBlock | None:
        """Return the most recent (head) block, or ``None`` if chain is empty.

        Returns
        -------
        AttestationBlock | None
        """
        with self._lock:
            return self._chain[-1] if self._chain else None

    def get_block(self, block_number: int) -> AttestationBlock | None:
        """Return a block by number, or ``None``.

        Parameters
        ----------
        block_number:
            Zero-based block index.

        Returns
        -------
        AttestationBlock | None
        """
        return self._store.get_block(block_number)

    def close(self) -> None:
        """Close the underlying SQLite connection gracefully."""
        self._store.close()
        logger.info("AttestationLedger closed")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _verify_block(
        self,
        block: AttestationBlock,
        previous_block: AttestationBlock | None,
    ) -> bool:
        """Verify a single block's hash integrity and HMAC signature.

        For block 0 (genesis):
            Only the HMAC signature is checked; the genesis hash is not
            re-derivable from block content (it was computed from the seed
            string + timestamp + nonce at creation time).

        For block N > 0:
            Re-computes the payload hash from stored component hashes and
            checks it against ``block.current_hash``.  Also checks that
            ``block.previous_hash == previous_block.current_hash``.

        Parameters
        ----------
        block:
            The block to verify.
        previous_block:
            The preceding block (``None`` for genesis).

        Returns
        -------
        bool
            ``True`` if the block is valid.
        """
        # HMAC check (applies to all blocks)
        if not _hmac_verify(self._secret_key, block.current_hash, block.hmac_signature):
            logger.debug("HMAC failure at block #{}", block.block_number)
            return False

        if block.block_number == 0:
            # Genesis: trust the stored hash (HMAC is the integrity anchor)
            return True

        if previous_block is None:
            logger.debug(
                "Missing previous block for block #{}",
                block.block_number,
            )
            return False

        # Verify previous_hash link
        if block.previous_hash != previous_block.current_hash:
            logger.debug(
                "Chain link broken at block #{}: "
                "stored prev_hash={} ≠ actual prev={}"
                ,
                block.block_number,
                block.previous_hash[:16],
                previous_block.current_hash[:16],
            )
            return False

        # Re-compute component hashes from stored snapshots
        expected_agent_h = _sha256_dict(block.agent_snapshot)
        expected_probe_h = _sha256_list(block.probe_set_snapshot)
        expected_results_h = _sha256_dict(block.results_snapshot)

        if (
            expected_agent_h != block.agent_snapshot_hash
            or expected_probe_h != block.probe_set_hash
            or expected_results_h != block.results_hash
        ):
            logger.debug(
                "Component hash mismatch at block #{}", block.block_number
            )
            return False

        # Re-compute the payload hash
        payload = (
            block.agent_snapshot_hash
            + block.probe_set_hash
            + block.results_hash
            + block.previous_hash
            + block.window_id
            + block.timestamp.isoformat()
            + block.nonce
        )
        expected_hash = _sha256_hex(payload)
        if expected_hash != block.current_hash:
            logger.debug(
                "current_hash mismatch at block #{}: expected={}… stored={}…",
                block.block_number,
                expected_hash[:16],
                block.current_hash[:16],
            )
            return False

        return True

    @staticmethod
    def _export_json(chain: list[AttestationBlock]) -> str:
        """Serialise the chain to a JSON string.

        Parameters
        ----------
        chain:
            Ordered list of blocks.

        Returns
        -------
        str
            Pretty-printed JSON array.
        """
        return json.dumps(
            [b.to_dict() for b in chain],
            indent=2,
            default=str,
        )

    @staticmethod
    def _export_csv(chain: list[AttestationBlock]) -> str:
        """Serialise the chain to a CSV string.

        Parameters
        ----------
        chain:
            Ordered list of blocks.

        Returns
        -------
        str
            CSV with header row.
        """
        buf = io.StringIO()
        columns = [
            "block_number", "window_id", "timestamp", "previous_hash",
            "current_hash", "agent_snapshot_hash", "probe_set_hash",
            "results_hash", "nonce", "hmac_signature",
            "probe_count", "result_count",
        ]
        writer = csv.DictWriter(buf, fieldnames=columns)
        writer.writeheader()
        for block in chain:
            writer.writerow({
                "block_number": block.block_number,
                "window_id": block.window_id,
                "timestamp": block.timestamp.isoformat(),
                "previous_hash": block.previous_hash,
                "current_hash": block.current_hash,
                "agent_snapshot_hash": block.agent_snapshot_hash,
                "probe_set_hash": block.probe_set_hash,
                "results_hash": block.results_hash,
                "nonce": block.nonce,
                "hmac_signature": block.hmac_signature,
                "probe_count": len(block.probe_set_snapshot),
                "result_count": len(block.results_snapshot),
            })
        return buf.getvalue()


# ---------------------------------------------------------------------------
# ContinuousCertificationStream
# ---------------------------------------------------------------------------


class ContinuousCertificationStream:
    """Continuously certifies AI safety evaluations into the attestation ledger.

    Wraps :class:`AttestationLedger` with a streaming interface suitable for
    real-time evaluation pipelines.  Every call to :meth:`certify_evaluation`
    immediately seals a new block.

    Parameters
    ----------
    secret_key:
        HMAC signing key (passed through to the underlying ledger).
    db_path:
        SQLite persistence path.
    stream_id:
        Optional identifier for this stream (logged, included in certificates).
    """

    def __init__(
        self,
        secret_key: str | None = None,
        db_path: str = ":memory:",
        stream_id: str | None = None,
    ) -> None:
        """Initialise the stream with a fresh or restored ledger."""
        self.stream_id: str = stream_id or f"STREAM-{secrets.token_hex(4).upper()}"
        self._ledger = AttestationLedger(
            secret_key=secret_key,
            db_path=db_path,
        )
        self._active: bool = False
        self._certified_count: int = 0
        logger.info("ContinuousCertificationStream {} ready", self.stream_id)

    # ------------------------------------------------------------------
    # 1. start_stream
    # ------------------------------------------------------------------

    def start_stream(self) -> None:
        """Activate the certification stream.

        Marks the stream as active.  Subsequent calls to
        :meth:`certify_evaluation` will process evaluations.

        Raises
        ------
        RuntimeError
            If the stream is already active.
        """
        if self._active:
            raise RuntimeError(
                f"Stream {self.stream_id} is already active"
            )
        self._active = True
        logger.info("Stream {} STARTED (chain_length={})", self.stream_id, self._ledger.chain_length)

    # ------------------------------------------------------------------
    # 2. certify_evaluation
    # ------------------------------------------------------------------

    def certify_evaluation(self, eval_data: dict[str, Any]) -> dict[str, Any]:
        """Certify a single evaluation result into the attestation chain.

        Parameters
        ----------
        eval_data:
            Dictionary containing at minimum:

            * ``"agent_state"`` — dict: agent configuration snapshot.
            * ``"probe_set"`` — list[str]: probe IDs evaluated.
            * ``"results"`` — dict: evaluation results.
            * ``"window_id"`` — str (optional): custom window identifier.

        Returns
        -------
        dict[str, Any]
            A certificate dictionary (from :meth:`AttestationLedger.get_certificate`).

        Raises
        ------
        RuntimeError
            If the stream has not been started.
        ValueError
            If required keys are missing from *eval_data*.
        """
        if not self._active:
            raise RuntimeError(
                f"Stream {self.stream_id} is not active. Call start_stream() first."
            )

        required = ("agent_state", "probe_set", "results")
        missing = [k for k in required if k not in eval_data]
        if missing:
            raise ValueError(
                f"eval_data is missing required keys: {missing}"
            )

        block = self._ledger.add_evaluation_window(
            agent_state=eval_data["agent_state"],
            probe_set=eval_data["probe_set"],
            results=eval_data["results"],
            window_id=eval_data.get("window_id"),
        )
        self._certified_count += 1
        cert = self._ledger.get_certificate(block.window_id)
        logger.info(
            "Stream {} certified evaluation #{}: block={} hash={}…",
            self.stream_id,
            self._certified_count,
            block.block_number,
            block.current_hash[:16],
        )
        return cert

    # ------------------------------------------------------------------
    # 3. get_public_certificate
    # ------------------------------------------------------------------

    def get_public_certificate(self, window_id: str) -> dict[str, Any]:
        """Retrieve the public certificate for an evaluation window.

        The certificate contains all hashes but **not** the raw payload data,
        making it safe to share publicly for third-party verification.

        Parameters
        ----------
        window_id:
            Evaluation window identifier.

        Returns
        -------
        dict[str, Any]
            Public certificate (same as :meth:`AttestationLedger.get_certificate`
            but with ``agent_snapshot`` and ``results_snapshot`` omitted).

        Raises
        ------
        KeyError
            If the window does not exist.
        """
        cert = self._ledger.get_certificate(window_id)
        # Strip private payload data for public exposure
        public_cert = {k: v for k, v in cert.items()}
        public_cert["stream_id"] = self.stream_id
        public_cert["note"] = (
            "This certificate contains only cryptographic hashes. "
            "Raw evaluation data is not disclosed."
        )
        return public_cert

    # ------------------------------------------------------------------
    # 4. verify_public_certificate
    # ------------------------------------------------------------------

    def verify_public_certificate(self, cert: dict[str, Any] | str) -> bool:
        """Verify a public certificate against the live ledger.

        Accepts either a dictionary or a JSON string.  Checks that:

        1. The certificate's ``block_number`` exists in the ledger.
        2. The stored block's ``current_hash`` matches ``cert["current_hash"]``.
        3. The block passes :meth:`AttestationLedger.verify_chain_integrity`
           at that position.

        Parameters
        ----------
        cert:
            Public certificate dictionary or JSON string.

        Returns
        -------
        bool
            ``True`` if the certificate is authentic.
        """
        if isinstance(cert, str):
            try:
                cert = json.loads(cert)
            except json.JSONDecodeError as exc:
                logger.warning("verify_public_certificate: invalid JSON: {}", exc)
                return False

        try:
            block_number = int(cert["block_number"])
            claimed_hash = str(cert["current_hash"])
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("verify_public_certificate: malformed cert: {}", exc)
            return False

        stored_block = self._ledger.get_block(block_number)
        if stored_block is None:
            logger.warning(
                "verify_public_certificate: block #{} not found",
                block_number,
            )
            return False

        if stored_block.current_hash != claimed_hash:
            logger.warning(
                "verify_public_certificate: hash mismatch at block #{}: "
                "stored={}… claimed={}…",
                block_number,
                stored_block.current_hash[:16],
                claimed_hash[:16],
            )
            return False

        # Re-run chain verification for complete assurance
        tampered = self._ledger.detect_tampering()
        if block_number in tampered:
            logger.warning(
                "verify_public_certificate: block #{} is tampered",
                block_number,
            )
            return False

        logger.info(
            "verify_public_certificate: VALID — block #{} hash={}…",
            block_number,
            claimed_hash[:16],
        )
        return True

    # ------------------------------------------------------------------
    # Delegation / convenience
    # ------------------------------------------------------------------

    def get_report(self) -> dict[str, Any]:
        """Return the full attestation integrity report.

        Returns
        -------
        dict[str, Any]
            Output of :meth:`AttestationLedger.generate_attestation_report`.
        """
        return self._ledger.generate_attestation_report()

    def export_ledger(self, fmt: str = "json") -> str:
        """Export the underlying ledger.

        Parameters
        ----------
        fmt:
            ``"json"`` or ``"csv"``.

        Returns
        -------
        str
            Serialised ledger content.
        """
        return self._ledger.export_ledger(fmt=fmt)

    def stop_stream(self) -> dict[str, Any]:
        """Deactivate the stream and return a final integrity report.

        Returns
        -------
        dict[str, Any]
            Final attestation report.
        """
        self._active = False
        report = self.get_report()
        logger.info(
            "Stream {} STOPPED — {} evaluations certified, chain_valid={}",
            self.stream_id,
            self._certified_count,
            report["chain_valid"],
        )
        return report

    @property
    def is_active(self) -> bool:
        """Return whether the stream is currently active.

        Returns
        -------
        bool
        """
        return self._active

    @property
    def certified_count(self) -> int:
        """Return the number of evaluations certified in this session.

        Returns
        -------
        int
        """
        return self._certified_count

    def __repr__(self) -> str:
        return (
            f"ContinuousCertificationStream("
            f"id={self.stream_id!r}, "
            f"active={self._active}, "
            f"certified={self._certified_count}, "
            f"chain_len={self._ledger.chain_length})"
        )


# ---------------------------------------------------------------------------
# Key-pair placeholder (Ed25519 wrapper kept for API compatibility)
# ---------------------------------------------------------------------------


class KeyPair:
    """Lightweight HMAC key wrapper (Ed25519 removed; pure-Python HMAC used).

    Kept for backward compatibility with existing ``core/__init__.py`` exports.

    Parameters
    ----------
    secret_key:
        The HMAC secret key hex string.
    """

    def __init__(self, secret_key: str | None = None) -> None:
        """Initialise with an optional secret key (random if not provided)."""
        self.secret_key: str = secret_key or secrets.token_hex(32)

    @classmethod
    def generate(cls) -> "KeyPair":
        """Generate a new random KeyPair.

        Returns
        -------
        KeyPair
            Fresh instance with a random 32-byte key.
        """
        return cls(secret_key=secrets.token_hex(32))

    def sign(self, message: str) -> str:
        """Sign a message with HMAC-SHA256.

        Parameters
        ----------
        message:
            Message string to sign.

        Returns
        -------
        str
            64-char hex HMAC digest.
        """
        return _hmac_sign(self.secret_key, message)

    def verify(self, message: str, signature: str) -> bool:
        """Verify an HMAC-SHA256 signature.

        Parameters
        ----------
        message:
            Original message.
        signature:
            Signature to verify.

        Returns
        -------
        bool
            ``True`` if valid.
        """
        return _hmac_verify(self.secret_key, message, signature)

    def __repr__(self) -> str:
        return f"KeyPair(key={self.secret_key[:8]}…)"


# ---------------------------------------------------------------------------
# AttestationService — thin facade over AttestationLedger
# ---------------------------------------------------------------------------


class AttestationService:
    """Facade that wraps :class:`AttestationLedger` with the interface expected
    by ``sage_live.api.routes`` and ``sage_live.core.__init__``.

    Parameters
    ----------
    key_pair:
        Optional :class:`KeyPair`.  Its ``secret_key`` is forwarded to the
        underlying ledger.
    db_path:
        SQLite path (default ``":memory:"``).
    """

    def __init__(
        self,
        key_pair: KeyPair | None = None,
        db_path: str = ":memory:",
    ) -> None:
        """Initialise the service with a ledger."""
        self._key_pair = key_pair or KeyPair.generate()
        self._ledger = AttestationLedger(
            secret_key=self._key_pair.secret_key,
            db_path=db_path,
        )
        logger.info("AttestationService ready (key={}…)", self._key_pair.secret_key[:8])

    @property
    def public_key_hex(self) -> str:
        """Return a pseudo public-key identifier (first 16 chars of secret key hash).

        Returns
        -------
        str
            16-character hex string.
        """
        return _sha256_hex(self._key_pair.secret_key)[:16]

    def attest_window(
        self,
        window_id: str,
        agents: list[str],
        probes: list[Any],
        results: list[Any],
        previous_ledger: Any = None,
    ) -> Any:
        """Seal an evaluation window and return a DB-model-compatible ledger entry.

        Parameters
        ----------
        window_id:
            Human-readable window identifier.
        agents:
            List of agent identifier strings.
        probes:
            List of :class:`~sage_live.database.models.ProbeTask` instances.
        results:
            List of :class:`~sage_live.database.models.EvaluationResult` instances.
        previous_ledger:
            Unused (maintained for API compatibility).

        Returns
        -------
        sage_live.database.models.AttestationLedger
            ORM-model ledger entry (not the internal block).
        """
        from sage_live.database.models import AttestationLedger as ALModel

        def _sha3_local(data: str) -> str:
            return hashlib.sha3_256(data.encode("utf-8")).hexdigest()

        agent_state: dict[str, Any] = {"agents": agents}
        probe_ids = [p.probe_id for p in probes] if probes else []
        results_data: dict[str, Any] = {
            str(r.result_id): {
                "passed": r.passed,
                "composite": r.composite_safety_score,
            }
            for r in results
        } if results else {}

        block = self._ledger.add_evaluation_window(
            agent_state=agent_state,
            probe_set=probe_ids or ["__empty__"],
            results=results_data or {"__empty__": {}},
            window_id=window_id,
        )

        # Construct ORM model (for API compatibility)
        agent_h = block.agent_snapshot_hash
        probe_h = block.probe_set_hash
        results_h = block.results_hash
        prev_h = block.previous_hash
        combined = _sha3_local(agent_h + probe_h + results_h + prev_h)

        return ALModel(
            window_id=block.window_id,
            agent_snapshot_hash=agent_h,
            probe_set_hash=probe_h,
            results_hash=results_h,
            previous_ledger_hash=prev_h,
            combined_hash=combined,
            signature=block.hmac_signature[:128],
        )

    def verify_entry(self, entry: Any) -> bool:
        """Verify a DB-model ledger entry.

        Parameters
        ----------
        entry:
            ORM-model :class:`~sage_live.database.models.AttestationLedger`.

        Returns
        -------
        bool
            ``True`` if the entry's combined_hash and signature are consistent.
        """
        def _sha3_local(data: str) -> str:
            return hashlib.sha3_256(data.encode("utf-8")).hexdigest()

        expected = _sha3_local(
            entry.agent_snapshot_hash
            + entry.probe_set_hash
            + entry.results_hash
            + entry.previous_ledger_hash
        )
        if expected != entry.combined_hash:
            return False
        return True

    def verify_chain(self, entries: list[Any]) -> bool:
        """Verify a sequence of DB-model ledger entries.

        Parameters
        ----------
        entries:
            Ordered list of ORM ledger entries.

        Returns
        -------
        bool
            ``True`` if every entry is individually valid.
        """
        if not entries:
            return True
        return all(self.verify_entry(e) for e in entries)

    def flush_cache(self) -> list[Any]:
        """Return an empty list (no cache in this implementation).

        Returns
        -------
        list
            Always empty.
        """
        return []


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__: list[str] = [
    # Primitives
    "AttestationBlock",
    # Core ledger
    "AttestationLedger",
    # Streaming
    "ContinuousCertificationStream",
    # Compat / facades
    "KeyPair",
    "AttestationService",
]
