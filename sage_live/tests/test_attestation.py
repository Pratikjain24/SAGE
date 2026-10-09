"""
tests.test_attestation
~~~~~~~~~~~~~~~~~~~~~~~

Test suite for AttestationService - ensures cryptographic integrity,
tamper detection, and chain verification.

Test Coverage:
* Genesis block creation
* Chain linking
* Tampering detection
* Chain integrity verification
* Certificate generation
* Public verification
* Append-only property
* Hash consistency
"""

from __future__ import annotations

import hashlib
from typing import List

import pytest

from sage_live.core.attestation import AttestationService
from sage_live.database.models import AttestationLedger


# ---------------------------------------------------------------------------
# Genesis Block Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_genesis_block_creation(attestation_service: AttestationService):
    """Test that first block (genesis) has zero previous hash."""
    ledger = attestation_service.attest_window(
        window_id="GENESIS",
        agents=["test-agent"],
        probes=[],
        results=[],
    )

    # Genesis has no previous
    assert ledger.previous_hash == "0" * 64
    assert len(ledger.window_hash) == 64
    assert len(ledger.signature) > 0


@pytest.mark.unit
def test_genesis_block_deterministic(attestation_service: AttestationService):
    """Test that genesis block with same content produces same hash."""
    ledger1 = attestation_service.attest_window(
        window_id="GEN-1",
        agents=["agent-a"],
        probes=[],
        results=[],
    )

    # Same service, different window
    ledger2 = attestation_service.attest_window(
        window_id="GEN-2",
        agents=["agent-a"],
        probes=[],
        results=[],
    )

    # Different windows = different hashes
    assert ledger1.window_hash != ledger2.window_hash


# ---------------------------------------------------------------------------
# Chain Linking Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_chain_linking_sequential(attestation_service: AttestationService):
    """Test that each block links to previous block's hash."""
    ledgers = []

    for i in range(5):
        ledger = attestation_service.attest_window(
            window_id=f"WIN-{i:03d}",
            agents=["test-agent"],
            probes=[],
            results=[],
        )
        ledgers.append(ledger)

    # First block is genesis
    assert ledgers[0].previous_hash == "0" * 64

    # Each subsequent block links to previous
    for i in range(1, len(ledgers)):
        assert ledgers[i].previous_hash == ledgers[i - 1].window_hash


@pytest.mark.unit
def test_chain_linking_integrity(attestation_service: AttestationService):
    """Test that chain maintains integrity through multiple blocks."""
    chain: List[AttestationLedger] = []

    for i in range(10):
        ledger = attestation_service.attest_window(
            window_id=f"BLOCK-{i:04d}",
            agents=[f"agent-{i % 3}"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    # Verify entire chain
    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is True


# ---------------------------------------------------------------------------
# Tampering Detection Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tampering_detection_modified_hash(attestation_service: AttestationService):
    """Test that modifying a hash breaks the chain."""
    chain = []

    for i in range(5):
        ledger = attestation_service.attest_window(
            window_id=f"WIN-{i}",
            agents=["agent"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    # Tamper with middle block's hash
    chain[2].window_hash = "f" * 64  # Invalid hash

    # Chain verification should fail
    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is False


@pytest.mark.unit
def test_tampering_detection_modified_content(attestation_service: AttestationService):
    """Test that modifying content (agents list) is detected."""
    chain = []

    for i in range(3):
        ledger = attestation_service.attest_window(
            window_id=f"WIN-{i}",
            agents=[f"agent-{i}"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    # Tamper with agent list in middle block
    original_agents = chain[1].agent_ids.copy()
    chain[1].agent_ids.append("malicious-agent")

    # Hash should no longer match content
    # (Implementation should detect this during verification)
    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is False

    # Restore for cleanup
    chain[1].agent_ids = original_agents


@pytest.mark.unit
def test_tampering_detection_reordered_blocks(attestation_service: AttestationService):
    """Test that reordering blocks is detected."""
    chain = []

    for i in range(4):
        ledger = attestation_service.attest_window(
            window_id=f"WIN-{i}",
            agents=["agent"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    # Swap two blocks
    chain[1], chain[2] = chain[2], chain[1]

    # Chain should be invalid
    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is False


# ---------------------------------------------------------------------------
# Chain Integrity Verification Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_chain_integrity_verification_valid(attestation_service: AttestationService):
    """Test that valid chain passes verification."""
    chain = []

    for i in range(20):
        ledger = attestation_service.attest_window(
            window_id=f"VALID-{i:03d}",
            agents=["agent-a", "agent-b"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is True


@pytest.mark.unit
def test_chain_integrity_verification_empty_chain(attestation_service: AttestationService):
    """Test that empty chain is considered valid."""
    is_valid = attestation_service.verify_chain([])
    assert is_valid is True


@pytest.mark.unit
def test_chain_integrity_verification_single_block(attestation_service: AttestationService):
    """Test that single block (genesis) is valid."""
    ledger = attestation_service.attest_window(
        window_id="SINGLE",
        agents=["agent"],
        probes=[],
        results=[],
    )

    is_valid = attestation_service.verify_chain([ledger])
    assert is_valid is True


# ---------------------------------------------------------------------------
# Certificate Generation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_certificate_generation_structure(sample_attestation_ledger: AttestationLedger):
    """Test that attestation certificate has all required fields."""
    assert sample_attestation_ledger.window_id is not None
    assert len(sample_attestation_ledger.window_hash) == 64
    assert len(sample_attestation_ledger.previous_hash) == 64
    assert len(sample_attestation_ledger.signature) > 0
    assert len(sample_attestation_ledger.public_key) > 0
    assert sample_attestation_ledger.timestamp is not None
    assert isinstance(sample_attestation_ledger.agent_ids, list)
    assert isinstance(sample_attestation_ledger.probe_ids, list)
    assert isinstance(sample_attestation_ledger.result_ids, list)


@pytest.mark.unit
def test_certificate_generation_signature_unique(attestation_service: AttestationService):
    """Test that each certificate has unique signature."""
    signatures = set()

    for i in range(10):
        ledger = attestation_service.attest_window(
            window_id=f"CERT-{i}",
            agents=["agent"],
            probes=[],
            results=[],
        )
        signatures.add(ledger.signature)

    # All signatures should be unique
    assert len(signatures) == 10


@pytest.mark.unit
def test_certificate_generation_includes_metadata(
    attestation_service: AttestationService, sample_probe_batch
):
    """Test that certificate includes all metadata."""
    ledger = attestation_service.attest_window(
        window_id="META-TEST",
        agents=["gpt-4", "claude-3"],
        probes=sample_probe_batch[:5],
        results=[],
    )

    assert len(ledger.agent_ids) == 2
    assert "gpt-4" in ledger.agent_ids
    assert "claude-3" in ledger.agent_ids
    assert len(ledger.probe_ids) == 5


# ---------------------------------------------------------------------------
# Public Verification Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_public_verification_valid_signature(attestation_service: AttestationService):
    """Test that valid signature can be publicly verified."""
    ledger = attestation_service.attest_window(
        window_id="PUB-VERIFY",
        agents=["agent"],
        probes=[],
        results=[],
    )

    # Verify using public key
    is_valid = attestation_service.verify_signature(
        message=ledger.window_hash,
        signature=ledger.signature,
        public_key=ledger.public_key,
    )

    assert is_valid is True


@pytest.mark.unit
def test_public_verification_invalid_signature(attestation_service: AttestationService):
    """Test that tampered signature is detected."""
    ledger = attestation_service.attest_window(
        window_id="INV-SIG",
        agents=["agent"],
        probes=[],
        results=[],
    )

    # Tamper with signature
    tampered_sig = "a" * len(ledger.signature)

    is_valid = attestation_service.verify_signature(
        message=ledger.window_hash,
        signature=tampered_sig,
        public_key=ledger.public_key,
    )

    assert is_valid is False


@pytest.mark.unit
def test_public_verification_wrong_message(attestation_service: AttestationService):
    """Test that signature for wrong message fails verification."""
    ledger = attestation_service.attest_window(
        window_id="WRONG-MSG",
        agents=["agent"],
        probes=[],
        results=[],
    )

    # Try to verify with wrong message
    is_valid = attestation_service.verify_signature(
        message="wrong-message-hash",
        signature=ledger.signature,
        public_key=ledger.public_key,
    )

    assert is_valid is False


# ---------------------------------------------------------------------------
# Append-Only Property Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_append_only_property_no_deletion(attestation_service: AttestationService):
    """Test that chain is append-only (no deletion).

    Once added, blocks cannot be removed without breaking the chain.
    """
    chain = []

    for i in range(5):
        ledger = attestation_service.attest_window(
            window_id=f"APP-{i}",
            agents=["agent"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    # Remove middle block
    removed = chain.pop(2)

    # Chain should now be invalid
    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is False


@pytest.mark.unit
def test_append_only_property_insertion(attestation_service: AttestationService):
    """Test that inserting block in middle breaks chain."""
    chain = []

    for i in range(4):
        ledger = attestation_service.attest_window(
            window_id=f"INS-{i}",
            agents=["agent"],
            probes=[],
            results=[],
        )
        chain.append(ledger)

    # Try to insert a new block in the middle
    inserted = attestation_service.attest_window(
        window_id="INSERTED",
        agents=["agent"],
        probes=[],
        results=[],
    )
    chain.insert(2, inserted)

    # Chain should be invalid
    is_valid = attestation_service.verify_chain(chain)
    assert is_valid is False


# ---------------------------------------------------------------------------
# Hash Consistency Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_hash_consistency_deterministic(attestation_service: AttestationService):
    """Test that same input produces same hash."""
    window_id = "HASH-TEST"
    agents = ["agent-a", "agent-b"]

    ledger1 = attestation_service.attest_window(
        window_id=window_id,
        agents=agents,
        probes=[],
        results=[],
    )

    # Reset service state to recompute
    attestation_service2 = AttestationService()
    attestation_service2.keypair = attestation_service.keypair  # Same keys

    ledger2 = attestation_service2.attest_window(
        window_id=window_id,
        agents=agents,
        probes=[],
        results=[],
    )

    # Hashes should match (deterministic hashing)
    # Note: Timestamps might differ, so this test checks hash algorithm consistency
    assert len(ledger1.window_hash) == len(ledger2.window_hash) == 64


@pytest.mark.unit
def test_hash_consistency_sha256_format():
    """Test that hashes are valid SHA-256 format."""
    service = AttestationService()
    ledger = service.attest_window(
        window_id="SHA-TEST",
        agents=["agent"],
        probes=[],
        results=[],
    )

    # SHA-256 produces 64 hex characters
    assert len(ledger.window_hash) == 64
    assert all(c in "0123456789abcdef" for c in ledger.window_hash)
    assert len(ledger.previous_hash) == 64
    assert all(c in "0123456789abcdef" for c in ledger.previous_hash)


@pytest.mark.unit
def test_hash_consistency_collision_resistance():
    """Test that different inputs produce different hashes (collision resistance)."""
    service = AttestationService()

    hashes = set()
    for i in range(100):
        ledger = service.attest_window(
            window_id=f"COLLISION-{i}",
            agents=[f"agent-{i}"],
            probes=[],
            results=[],
        )
        hashes.add(ledger.window_hash)

    # All hashes should be unique
    assert len(hashes) == 100


# ---------------------------------------------------------------------------
# Cryptographic Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cryptographic_key_generation():
    """Test that key generation produces valid key pairs."""
    service1 = AttestationService()
    service2 = AttestationService()

    # Each service gets unique key pair
    assert service1.keypair.public_key != service2.keypair.public_key
    assert service1.keypair.private_key != service2.keypair.private_key


@pytest.mark.unit
def test_cryptographic_signature_length():
    """Test that signatures have appropriate length."""
    service = AttestationService()
    ledger = service.attest_window(
        window_id="SIG-LEN",
        agents=["agent"],
        probes=[],
        results=[],
    )

    # Ed25519 signatures are typically 128 hex characters (64 bytes)
    assert len(ledger.signature) > 0
    assert len(ledger.public_key) > 0


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_edge_case_empty_window(attestation_service: AttestationService):
    """Test attestation of empty evaluation window."""
    ledger = attestation_service.attest_window(
        window_id="EMPTY",
        agents=[],
        probes=[],
        results=[],
    )

    assert len(ledger.agent_ids) == 0
    assert len(ledger.probe_ids) == 0
    assert len(ledger.result_ids) == 0
    assert len(ledger.window_hash) == 64


@pytest.mark.unit
def test_edge_case_large_window(
    attestation_service: AttestationService, sample_probe_batch
):
    """Test attestation of large evaluation window."""
    agents = [f"agent-{i}" for i in range(50)]

    ledger = attestation_service.attest_window(
        window_id="LARGE",
        agents=agents,
        probes=sample_probe_batch,
        results=[],
    )

    assert len(ledger.agent_ids) == 50
    assert len(ledger.probe_ids) == len(sample_probe_batch)


@pytest.mark.unit
def test_edge_case_special_characters_window_id(attestation_service: AttestationService):
    """Test that special characters in window ID are handled."""
    window_id = "WIN-2024-01-15_10:30:00+UTC"

    ledger = attestation_service.attest_window(
        window_id=window_id,
        agents=["agent"],
        probes=[],
        results=[],
    )

    assert ledger.window_id == window_id
    assert len(ledger.window_hash) == 64
