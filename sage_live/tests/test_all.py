"""
SAGE-Live comprehensive test suite.

Covers:
────────────────────────────────────────────────────
DATABASE MODELS
  TestProbeTask            — validation, hash, repr
  TestEvaluationResult     — scores, composite, hash
  TestStalenessRecord      — escalation logic
  TestAttestationLedger    — combined_hash validator
  TestAgentProfile         — timestamps, whitespace

PROBE GENERATOR
  TestProbeGrammar         — algebra, enumeration
  TestSeededSelector       — determinism guarantee
  TestDeterministicGenerator
    • generate_probe        — pure function, hash ok
    • generate_batch        — unique, difficulty range
    • verify_probe          — 5 integrity checks
    • generate_adversarial  — weakness mapping
    • get_probe_family_size — returns sys.maxsize
    • export_json / jsonl   — round-trip

ATTESTATION LEDGER
  TestAttestationBlock     — to_dict / from_dict
  TestAttestationLedger
    • create_genesis_block  — hash not empty
    • add_evaluation_window — chain grows
    • verify_chain_integrity— multi-block valid
    • detect_tampering      — tampered block found
    • get_certificate       — required fields
    • export_ledger json    — valid JSON
    • export_ledger csv     — has header
    • verify_single_result  — authentic / not found
    • generate_report       — chain_valid key
  TestContinuousCertificationStream
    • start / stop / certify
    • get / verify public cert
    • double-start raises

API ENDPOINTS (FastAPI TestClient)
  TestHealthEndpoint
  TestProbeEndpoints
  TestEvaluationEndpoints
  TestStalenessEndpoint
  TestAttestationEndpoints
────────────────────────────────────────────────────

Run with:
    pytest tests/ -v --cov=sage_live
"""

from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient


# ============================================================
# Helpers
# ============================================================

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _sha3(text: str) -> str:
    return hashlib.sha3_256(text.encode()).hexdigest()


# ============================================================
# DATABASE MODEL TESTS
# ============================================================

class TestProbeTask:
    def test_factory_creates_valid_probe(self) -> None:
        from sage_live.database.models import make_probe_task
        probe = make_probe_task()
        assert probe.probe_id == "PROBE-0001"
        assert 0.0 <= probe.difficulty <= 1.0
        assert len(probe.sha256_hash) == 64

    def test_sha256_hash_is_correct(self) -> None:
        from sage_live.database.models import make_probe_task
        probe = make_probe_task(
            task_description="task", ground_truth="truth"
        )
        assert probe.sha256_hash == _sha256("tasktrue" + "th"[:0] + "truth")
        assert probe.sha256_hash == _sha256("task" + "truth")

    def test_invalid_hash_raises(self) -> None:
        from pydantic import ValidationError
        from sage_live.database.models import ProbeTask, VulnerabilityClass, InjectionVector, PolicyBoundary
        with pytest.raises(ValidationError, match="sha256_hash"):
            ProbeTask(
                probe_id="BAD",
                vulnerability_class=VulnerabilityClass.DATA_LEAK,
                injection_vector=InjectionVector.DIRECT,
                policy_boundary=PolicyBoundary.SAFETY,
                difficulty=0.5,
                task_description="x",
                ground_truth="y",
                seed=0,
                generation=1,
                sha256_hash="tooshort",
            )

    def test_difficulty_out_of_range_raises(self) -> None:
        from pydantic import ValidationError
        from sage_live.database.models import make_probe_task
        with pytest.raises(ValidationError):
            make_probe_task(difficulty=1.5)

    def test_repr_contains_probe_id(self) -> None:
        from sage_live.database.models import make_probe_task
        probe = make_probe_task()
        assert "PROBE-0001" in repr(probe)

    def test_probe_uuid_primary_key(self) -> None:
        from sage_live.database.models import make_probe_task
        probe = make_probe_task()
        assert probe.id is None or isinstance(probe.id, uuid.UUID)


class TestEvaluationResult:
    def test_factory_valid(self) -> None:
        from sage_live.database.models import make_evaluation_result
        r = make_evaluation_result()
        assert r.passed is True
        assert 0.0 <= r.capability_score <= 100.0
        assert len(r.attestation_hash) == 64

    def test_composite_score_in_range(self) -> None:
        from sage_live.database.models import make_evaluation_result
        r = make_evaluation_result()
        assert 0.0 <= r.composite_safety_score <= 100.0

    def test_composite_formula(self) -> None:
        from sage_live.database.models import make_evaluation_result
        r = make_evaluation_result(
            capability_score=80.0,
            safety_drift_score=90.0,
            retention_score=70.0,
            proxy_gap_score=20.0,
        )
        expected = round(0.35 * 90.0 + 0.30 * 70.0 + 0.20 * 80.0 + 0.15 * 80.0, 2)
        assert r.composite_safety_score == expected

    def test_bad_attestation_hash_raises(self) -> None:
        from pydantic import ValidationError
        from sage_live.database.models import EvaluationResult
        with pytest.raises(ValidationError):
            EvaluationResult(
                agent_id="a",
                cycle_number=1,
                capability_score=50.0,
                safety_drift_score=50.0,
                retention_score=50.0,
                proxy_gap_score=50.0,
                passed=True,
                raw_output="ok",
                evaluator_model="gpt-4o",
                attestation_hash="bad",
            )


class TestStalenessRecord:
    def test_healthy_by_default(self) -> None:
        from sage_live.database.models import RecommendedAction, make_staleness_record
        r = make_staleness_record()
        assert r.recommended_action == RecommendedAction.HEALTHY

    def test_leakage_09_triggers_critical(self) -> None:
        from sage_live.database.models import RecommendedAction, make_staleness_record
        r = make_staleness_record(leakage_score=0.95)
        assert r.recommended_action == RecommendedAction.CRITICAL

    def test_leakage_07_triggers_retire(self) -> None:
        from sage_live.database.models import RecommendedAction, make_staleness_record
        r = make_staleness_record(leakage_score=0.75)
        assert r.recommended_action == RecommendedAction.RETIRE

    def test_contamination_triggers_warning(self) -> None:
        from sage_live.database.models import RecommendedAction, make_staleness_record
        r = make_staleness_record(contamination_detected=True, leakage_score=0.1)
        assert r.recommended_action == RecommendedAction.WARNING

    def test_invalid_version_raises(self) -> None:
        from pydantic import ValidationError
        from sage_live.database.models import make_staleness_record
        with pytest.raises(ValidationError):
            make_staleness_record(benchmark_version="nodot")


class TestAttestationLedgerModel:
    def test_factory_creates_valid_entry(self) -> None:
        from sage_live.database.models import make_attestation_ledger
        entry = make_attestation_ledger()
        assert not entry.is_tampered
        assert len(entry.combined_hash) == 64

    def test_wrong_combined_hash_raises(self) -> None:
        from pydantic import ValidationError
        from sage_live.database.models import AttestationLedger as ALModel
        h = secrets.token_hex(32)
        with pytest.raises(ValidationError, match="combined_hash"):
            ALModel(
                window_id="W",
                agent_snapshot_hash=h,
                probe_set_hash=h,
                results_hash=h,
                previous_ledger_hash="0" * 64,
                combined_hash=h,  # wrong
                signature="0" * 128,
            )

    def test_repr_contains_window_id(self) -> None:
        from sage_live.database.models import make_attestation_ledger
        entry = make_attestation_ledger(window_id="W-TEST-42")
        assert "W-TEST-42" in repr(entry)


class TestAgentProfile:
    def test_factory_valid(self) -> None:
        from sage_live.database.models import make_agent_profile
        p = make_agent_profile()
        assert p.total_evaluations == 0
        assert p.current_cycle == 1

    def test_last_evaluated_before_created_raises(self) -> None:
        from pydantic import ValidationError
        from sage_live.database.models import AgentProfile
        now = datetime.now(tz=timezone.utc)
        with pytest.raises(ValidationError, match="last_evaluated"):
            AgentProfile(
                agent_name="X",
                model_name="gpt-4o",
                model_version="1.0",
                created_at=now,
                last_evaluated=now - timedelta(hours=1),
            )

    def test_whitespace_stripped(self) -> None:
        from sage_live.database.models import AgentProfile
        now = datetime.now(tz=timezone.utc)
        p = AgentProfile(
            agent_name="  GPT  ",
            model_name="  gpt-4o  ",
            model_version="1.0",
            created_at=now,
            last_evaluated=now,
        )
        assert p.agent_name == "GPT"
        assert p.model_name == "gpt-4o"


# ============================================================
# PROBE GENERATOR TESTS
# ============================================================

class TestProbeGrammar:
    def test_base_type_count(self) -> None:
        from sage_live.core.probe_generator import ProbeGrammar
        g = ProbeGrammar()
        assert g.base_type_count == 96  # 6 × 4 × 4

    def test_enumerate_base_types_length(self) -> None:
        from sage_live.core.probe_generator import ProbeGrammar
        g = ProbeGrammar()
        types = g.enumerate_base_types()
        assert len(types) == 96

    def test_enumerate_no_duplicates(self) -> None:
        from sage_live.core.probe_generator import ProbeGrammar
        g = ProbeGrammar()
        types = g.enumerate_base_types()
        assert len(types) == len(set(types))

    def test_validate_params_valid(self) -> None:
        from sage_live.core.probe_generator import ProbeGrammar
        g = ProbeGrammar()
        g.validate_params("reward_hack", "direct", "safety", 0.5)  # no error

    def test_validate_params_bad_vuln(self) -> None:
        from sage_live.core.probe_generator import ProbeGrammar
        g = ProbeGrammar()
        with pytest.raises(ValueError, match="vulnerability_class"):
            g.validate_params("unknown_vuln", "direct", "safety", 0.5)

    def test_validate_params_bad_difficulty(self) -> None:
        from sage_live.core.probe_generator import ProbeGrammar
        g = ProbeGrammar()
        with pytest.raises(ValueError, match="difficulty"):
            g.validate_params("reward_hack", "direct", "safety", 1.5)


class TestSeededSelector:
    def test_same_seed_same_result(self) -> None:
        from sage_live.core.probe_generator import SeededSelector
        opts = ["a", "b", "c", "d"]
        s1 = SeededSelector(42)
        s2 = SeededSelector(42)
        assert s1.pick("key", opts) == s2.pick("key", opts)

    def test_different_seeds_may_differ(self) -> None:
        from sage_live.core.probe_generator import SeededSelector
        opts = ["a", "b", "c", "d", "e", "f", "g", "h"]
        results = {SeededSelector(i).pick("key", opts) for i in range(20)}
        assert len(results) > 1  # at least two distinct choices across 20 seeds

    def test_sequential_calls_same_key(self) -> None:
        from sage_live.core.probe_generator import SeededSelector
        # Two calls with same key but different iterations → potentially different
        opts = ["a", "b", "c"]
        sel = SeededSelector(999)
        r1 = sel.pick("x", opts)
        r2 = sel.pick("x", opts)
        # Both must be valid choices
        assert r1 in opts
        assert r2 in opts

    def test_pick_float_in_range(self) -> None:
        from sage_live.core.probe_generator import SeededSelector
        sel = SeededSelector(7)
        v = sel.pick_float("f", 0.3, 0.9)
        assert 0.3 <= v <= 0.9

    def test_pick_int_in_range(self) -> None:
        from sage_live.core.probe_generator import SeededSelector
        sel = SeededSelector(7)
        v = sel.pick_int("i", 10, 20)
        assert 10 <= v <= 20

    def test_empty_options_raises(self) -> None:
        from sage_live.core.probe_generator import SeededSelector
        sel = SeededSelector(1)
        with pytest.raises(ValueError):
            sel.pick("empty", [])


class TestDeterministicGenerator:
    @pytest.fixture
    def gen(self) -> Any:
        from sage_live.core.probe_generator import DeterministicProbeGenerator
        return DeterministicProbeGenerator(generation=1)

    # --- generate_probe ---
    def test_generate_probe_pure_function(self, gen: Any) -> None:
        """Same args must always produce same probe_id and hash."""
        kwargs: dict[str, Any] = dict(
            seed=42,
            vuln_class="reward_hack",
            injection_vector="direct",
            policy_boundary="safety",
            difficulty=0.5,
        )
        p1 = gen.generate_probe(**kwargs)
        p2 = gen.generate_probe(**kwargs)
        assert p1.probe_id == p2.probe_id
        assert p1.sha256_hash == p2.sha256_hash
        assert p1.task_description == p2.task_description

    def test_generate_probe_different_seeds_differ(self, gen: Any) -> None:
        p1 = gen.generate_probe(0, "sql_injection", "direct", "safety", 0.5)
        p2 = gen.generate_probe(1, "sql_injection", "direct", "safety", 0.5)
        assert p1.probe_id != p2.probe_id

    def test_generate_probe_hash_valid(self, gen: Any) -> None:
        p = gen.generate_probe(10, "data_leak", "indirect", "retention", 0.7)
        expected = _sha256(p.task_description + p.ground_truth)
        assert p.sha256_hash == expected

    def test_generate_probe_ground_truth_parseable(self, gen: Any) -> None:
        from sage_live.core.probe_generator import ProbeGroundTruth
        p = gen.generate_probe(5, "code_execution", "chained", "capability", 0.8)
        gt = ProbeGroundTruth(**json.loads(p.ground_truth))
        assert gt.expected_refusal is True
        assert 0.0 <= gt.difficulty <= 1.0

    def test_generate_probe_invalid_vuln_raises(self, gen: Any) -> None:
        with pytest.raises(ValueError, match="vulnerability_class"):
            gen.generate_probe(0, "nonexistent", "direct", "safety", 0.5)

    # --- generate_batch ---
    def test_generate_batch_length(self, gen: Any) -> None:
        probes = gen.generate_batch(n=10, seed_start=0)
        assert len(probes) == 10

    def test_generate_batch_unique_ids(self, gen: Any) -> None:
        probes = gen.generate_batch(n=50, seed_start=0)
        ids = [p.probe_id for p in probes]
        assert len(ids) == len(set(ids))

    def test_generate_batch_difficulty_range(self, gen: Any) -> None:
        probes = gen.generate_batch(n=10, seed_start=0, difficulty_range=(0.2, 0.8))
        for p in probes:
            assert 0.2 <= p.difficulty <= 0.8 + 1e-9  # float tolerance

    def test_generate_batch_invalid_n_raises(self, gen: Any) -> None:
        with pytest.raises(ValueError, match="n must be"):
            gen.generate_batch(n=0)

    def test_generate_batch_invalid_range_raises(self, gen: Any) -> None:
        with pytest.raises(ValueError, match="difficulty_range"):
            gen.generate_batch(n=5, difficulty_range=(0.9, 0.1))

    def test_generate_batch_all_hashes_valid(self, gen: Any) -> None:
        probes = gen.generate_batch(n=20, seed_start=100)
        for p in probes:
            assert p.sha256_hash == _sha256(p.task_description + p.ground_truth)

    # --- verify_probe ---
    def test_verify_probe_valid(self, gen: Any) -> None:
        p = gen.generate_probe(42, "reward_hack", "direct", "safety", 0.5)
        assert gen.verify_probe(p) is True

    def test_verify_probe_tampered_hash(self, gen: Any) -> None:
        p = gen.generate_probe(42, "reward_hack", "direct", "safety", 0.5)
        p.sha256_hash = "a" * 64
        assert gen.verify_probe(p) is False

    def test_verify_probe_tampered_description(self, gen: Any) -> None:
        p = gen.generate_probe(42, "reward_hack", "direct", "safety", 0.5)
        p.task_description = "TAMPERED"
        # Hash won't match now
        assert gen.verify_probe(p) is False

    def test_verify_probe_bad_ground_truth_json(self, gen: Any) -> None:
        p = gen.generate_probe(42, "reward_hack", "direct", "safety", 0.5)
        # Recompute hash to pass hash check, but break GT JSON
        p.ground_truth = "NOT JSON AT ALL"
        p.sha256_hash = _sha256(p.task_description + p.ground_truth)
        assert gen.verify_probe(p) is False

    # --- generate_adversarial_probe ---
    def test_adversarial_probe_prefix(self, gen: Any) -> None:
        p = gen.generate_adversarial_probe("reward hacking", seed=77)
        assert p.probe_id.startswith("ADV-")

    def test_adversarial_probe_high_difficulty(self, gen: Any) -> None:
        p = gen.generate_adversarial_probe("sql injection attack", seed=88)
        assert p.difficulty >= 0.75

    def test_adversarial_probe_deterministic(self, gen: Any) -> None:
        p1 = gen.generate_adversarial_probe("data leak", seed=123)
        p2 = gen.generate_adversarial_probe("data leak", seed=123)
        assert p1.task_description == p2.task_description

    def test_adversarial_empty_weakness_raises(self, gen: Any) -> None:
        with pytest.raises(ValueError, match="agent_weakness"):
            gen.generate_adversarial_probe("", seed=1)

    # --- get_probe_family_size ---
    def test_family_size_is_maxsize(self, gen: Any) -> None:
        import sys
        assert gen.get_probe_family_size() == sys.maxsize

    # --- export / load ---
    def test_export_json_round_trip(self, gen: Any, tmp_path: Any) -> None:
        probes = gen.generate_batch(n=3, seed_start=0)
        path = tmp_path / "probes.json"
        gen.export_json(probes, path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 3
        assert "probe_id" in data[0]

    def test_export_jsonl_round_trip(self, gen: Any, tmp_path: Any) -> None:
        probes = gen.generate_batch(n=5, seed_start=0)
        path = tmp_path / "probes.jsonl"
        gen.export_jsonl(probes, path)
        records = gen.load_jsonl(path)
        assert len(records) == 5

    def test_coverage_all_96_base_types(self, gen: Any) -> None:
        """A batch of 96 probes starting at seed=0 should cover all 96 base types."""
        probes = gen.generate_batch(n=96, seed_start=0)
        from sage_live.core.probe_generator import ProbeGrammar
        grammar = ProbeGrammar()
        base_types = {(vc, iv, pb) for vc, iv, pb in grammar.enumerate_base_types()}
        generated_types = {
            (p.vulnerability_class.value, p.injection_vector.value, p.policy_boundary.value)
            for p in probes
        }
        assert generated_types == base_types


# ============================================================
# ATTESTATION LEDGER TESTS
# ============================================================

class TestAttestationBlock:
    def test_to_dict_from_dict_round_trip(self) -> None:
        from sage_live.core.attestation import AttestationBlock
        from datetime import timezone
        ts = datetime.now(tz=timezone.utc)
        block = AttestationBlock(
            block_number=0,
            window_id="GENESIS-W",
            agent_snapshot={},
            probe_set_snapshot=[],
            results_snapshot={},
            previous_hash="0" * 64,
            timestamp=ts,
            nonce="n" * 64,
            agent_snapshot_hash="0" * 64,
            probe_set_hash="0" * 64,
            results_hash="0" * 64,
            current_hash="a" * 64,
            hmac_signature="b" * 64,
        )
        d = block.to_dict()
        restored = AttestationBlock.from_dict(d)
        assert restored.block_number == 0
        assert restored.current_hash == "a" * 64

    def test_repr_contains_block_number(self) -> None:
        from sage_live.core.attestation import AttestationBlock
        from datetime import timezone
        ts = datetime.now(tz=timezone.utc)
        block = AttestationBlock(
            block_number=7,
            window_id="W7",
            agent_snapshot={},
            probe_set_snapshot=[],
            results_snapshot={},
            previous_hash="0" * 64,
            timestamp=ts,
            nonce="n" * 64,
            current_hash="c" * 64,
            hmac_signature="s" * 64,
        )
        assert "n=7" in repr(block)


@pytest.fixture
def fresh_ledger() -> Any:
    """Return a fresh in-memory AttestationLedger (genesis already created)."""
    from sage_live.core.attestation import AttestationLedger
    return AttestationLedger(secret_key="test-secret-key", db_path=":memory:")


class TestAttestationLedger:
    def test_genesis_created_on_init(self, fresh_ledger: Any) -> None:
        assert fresh_ledger.chain_length == 1

    def test_genesis_hash_nonempty(self, fresh_ledger: Any) -> None:
        genesis = fresh_ledger.head
        assert genesis is not None
        assert len(genesis.current_hash) == 64

    def test_double_genesis_raises(self, fresh_ledger: Any) -> None:
        with pytest.raises(RuntimeError, match="genesis block"):
            fresh_ledger.create_genesis_block()

    def test_add_window_grows_chain(self, fresh_ledger: Any) -> None:
        fresh_ledger.add_evaluation_window(
            agent_state={"model": "gpt-4o"},
            probe_set=["P1", "P2"],
            results={"P1": {"passed": True}},
        )
        assert fresh_ledger.chain_length == 2

    def test_head_after_add(self, fresh_ledger: Any) -> None:
        block = fresh_ledger.add_evaluation_window(
            agent_state={"cycle": 1},
            probe_set=["P1"],
            results={"P1": {"score": 90}},
        )
        assert fresh_ledger.head.block_number == block.block_number

    def test_add_window_empty_probe_set_raises(self, fresh_ledger: Any) -> None:
        with pytest.raises(ValueError, match="probe_set"):
            fresh_ledger.add_evaluation_window(
                agent_state={},
                probe_set=[],
                results={"P1": {}},
            )

    def test_add_window_empty_results_raises(self, fresh_ledger: Any) -> None:
        with pytest.raises(ValueError, match="results"):
            fresh_ledger.add_evaluation_window(
                agent_state={},
                probe_set=["P1"],
                results={},
            )

    def test_verify_chain_integrity_genesis_only(self, fresh_ledger: Any) -> None:
        assert fresh_ledger.verify_chain_integrity() is True

    def test_verify_chain_integrity_multi_block(self, fresh_ledger: Any) -> None:
        for i in range(5):
            fresh_ledger.add_evaluation_window(
                agent_state={"step": i},
                probe_set=[f"P{i}"],
                results={f"P{i}": {"passed": True}},
            )
        assert fresh_ledger.verify_chain_integrity() is True

    def test_detect_tampering_clean_chain(self, fresh_ledger: Any) -> None:
        fresh_ledger.add_evaluation_window(
            agent_state={}, probe_set=["P1"], results={"P1": {}}
        )
        tampered = fresh_ledger.detect_tampering()
        assert tampered == []

    def test_detect_tampering_finds_bad_block(self, fresh_ledger: Any) -> None:
        fresh_ledger.add_evaluation_window(
            agent_state={"model": "x"}, probe_set=["P1"], results={"P1": {}}
        )
        # Directly mutate chain to simulate tampering
        with fresh_ledger._lock:
            fresh_ledger._chain[1].agent_snapshot["model"] = "TAMPERED"
        tampered = fresh_ledger.detect_tampering()
        assert 1 in tampered

    def test_get_certificate_returns_required_fields(self, fresh_ledger: Any) -> None:
        block = fresh_ledger.add_evaluation_window(
            agent_state={}, probe_set=["P1"], results={"P1": {}}
        )
        cert = fresh_ledger.get_certificate(block.window_id)
        required_keys = {
            "block_number", "window_id", "current_hash",
            "previous_hash", "is_valid", "chain_length",
        }
        assert required_keys.issubset(cert.keys())

    def test_get_certificate_invalid_window_raises(self, fresh_ledger: Any) -> None:
        with pytest.raises(KeyError):
            fresh_ledger.get_certificate("NONEXISTENT-WINDOW")

    def test_export_json_valid(self, fresh_ledger: Any) -> None:
        out = fresh_ledger.export_ledger("json")
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "block_number" in data[0]

    def test_export_csv_has_header(self, fresh_ledger: Any) -> None:
        out = fresh_ledger.export_ledger("csv")
        assert "block_number" in out.splitlines()[0]

    def test_export_invalid_format_raises(self, fresh_ledger: Any) -> None:
        with pytest.raises(ValueError, match="Unsupported"):
            fresh_ledger.export_ledger("xml")

    def test_verify_single_result_found(self, fresh_ledger: Any) -> None:
        result_data = {"passed": True, "score": 95.0}
        block = fresh_ledger.add_evaluation_window(
            agent_state={},
            probe_set=["P1"],
            results={"P1": result_data},
        )
        import json as _json
        result_hash = _sha256(_json.dumps(result_data, sort_keys=True))
        assert fresh_ledger.verify_single_result(result_hash, block.block_number) is True

    def test_verify_single_result_not_found(self, fresh_ledger: Any) -> None:
        block = fresh_ledger.add_evaluation_window(
            agent_state={}, probe_set=["P1"], results={"P1": {}}
        )
        assert fresh_ledger.verify_single_result("a" * 64, block.block_number) is False

    def test_verify_single_result_bad_block(self, fresh_ledger: Any) -> None:
        assert fresh_ledger.verify_single_result("a" * 64, 9999) is False

    def test_generate_report_structure(self, fresh_ledger: Any) -> None:
        fresh_ledger.add_evaluation_window(
            agent_state={}, probe_set=["P1"], results={"P1": {}}
        )
        report = fresh_ledger.generate_attestation_report()
        assert "chain_valid" in report
        assert "summary" in report
        assert "integrity" in report
        assert report["chain_valid"] is True

    def test_report_human_readable_string(self, fresh_ledger: Any) -> None:
        report = fresh_ledger.generate_attestation_report()
        assert isinstance(report["human_readable"], str)
        assert "SAGE-Live" in report["human_readable"]

    def test_chain_link_is_valid(self, fresh_ledger: Any) -> None:
        """Each block's previous_hash must equal the prior block's current_hash."""
        for i in range(3):
            fresh_ledger.add_evaluation_window(
                agent_state={"i": i}, probe_set=[f"P{i}"], results={f"P{i}": {}}
            )
        with fresh_ledger._lock:
            chain = list(fresh_ledger._chain)
        for i in range(1, len(chain)):
            assert chain[i].previous_hash == chain[i - 1].current_hash

    def test_thread_safety_concurrent_additions(self, fresh_ledger: Any) -> None:
        import threading
        errors: list[Exception] = []

        def add_block(idx: int) -> None:
            try:
                fresh_ledger.add_evaluation_window(
                    agent_state={"thread": idx},
                    probe_set=[f"P{idx}"],
                    results={f"P{idx}": {"passed": True}},
                )
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=add_block, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert fresh_ledger.chain_length == 11  # genesis + 10


class TestContinuousCertificationStream:
    @pytest.fixture
    def stream(self) -> Any:
        from sage_live.core.attestation import ContinuousCertificationStream
        s = ContinuousCertificationStream(secret_key="stream-key", db_path=":memory:")
        s.start_stream()
        return s

    def test_start_stream_sets_active(self, stream: Any) -> None:
        assert stream.is_active is True

    def test_double_start_raises(self, stream: Any) -> None:
        with pytest.raises(RuntimeError, match="already active"):
            stream.start_stream()

    def test_certify_evaluation_returns_cert(self, stream: Any) -> None:
        cert = stream.certify_evaluation({
            "agent_state": {"model": "gpt-4o"},
            "probe_set": ["P1"],
            "results": {"P1": {"passed": True}},
        })
        assert "current_hash" in cert
        assert cert["is_valid"] is True

    def test_certify_increments_count(self, stream: Any) -> None:
        stream.certify_evaluation({
            "agent_state": {},
            "probe_set": ["P1"],
            "results": {"P1": {}},
        })
        assert stream.certified_count == 1

    def test_certify_without_start_raises(self) -> None:
        from sage_live.core.attestation import ContinuousCertificationStream
        s = ContinuousCertificationStream(db_path=":memory:")
        with pytest.raises(RuntimeError, match="not active"):
            s.certify_evaluation({
                "agent_state": {}, "probe_set": ["P1"], "results": {"P1": {}}
            })

    def test_certify_missing_key_raises(self, stream: Any) -> None:
        with pytest.raises(ValueError, match="missing required keys"):
            stream.certify_evaluation({"agent_state": {}})

    def test_get_public_certificate(self, stream: Any) -> None:
        cert = stream.certify_evaluation({
            "agent_state": {},
            "probe_set": ["P1"],
            "results": {"P1": {}},
        })
        pub_cert = stream.get_public_certificate(cert["window_id"])
        assert pub_cert["stream_id"] == stream.stream_id

    def test_verify_public_certificate_valid(self, stream: Any) -> None:
        cert = stream.certify_evaluation({
            "agent_state": {},
            "probe_set": ["P1"],
            "results": {"P1": {}},
        })
        assert stream.verify_public_certificate(cert) is True

    def test_verify_public_certificate_tampered_hash(self, stream: Any) -> None:
        cert = stream.certify_evaluation({
            "agent_state": {},
            "probe_set": ["P1"],
            "results": {"P1": {}},
        })
        cert["current_hash"] = "a" * 64
        assert stream.verify_public_certificate(cert) is False

    def test_verify_public_certificate_from_json_string(self, stream: Any) -> None:
        cert = stream.certify_evaluation({
            "agent_state": {},
            "probe_set": ["P1"],
            "results": {"P1": {}},
        })
        cert_str = json.dumps(cert, default=str)
        assert stream.verify_public_certificate(cert_str) is True

    def test_stop_stream_returns_report(self, stream: Any) -> None:
        report = stream.stop_stream()
        assert "chain_valid" in report
        assert stream.is_active is False

    def test_export_ledger_json(self, stream: Any) -> None:
        stream.certify_evaluation({
            "agent_state": {},
            "probe_set": ["P1"],
            "results": {"P1": {}},
        })
        out = stream.export_ledger("json")
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 2  # genesis + 1 block


# ============================================================
# API ENDPOINT TESTS
# ============================================================

@pytest.fixture(scope="module")
def api_client() -> TestClient:
    """Return a FastAPI TestClient for the SAGE-Live app."""
    from sage_live.api import create_app
    return TestClient(create_app())


class TestHealthEndpoint:
    def test_returns_200(self, api_client: TestClient) -> None:
        assert api_client.get("/health").status_code == 200

    def test_status_ok(self, api_client: TestClient) -> None:
        assert api_client.get("/health").json()["status"] == "ok"

    def test_has_version(self, api_client: TestClient) -> None:
        body = api_client.get("/health").json()
        assert "version" in body


class TestProbeEndpoints:
    def test_list_returns_200(self, api_client: TestClient) -> None:
        assert api_client.get("/api/v1/probes").status_code == 200

    def test_list_paginated(self, api_client: TestClient) -> None:
        body = api_client.get("/api/v1/probes?page=1&page_size=5").json()
        assert "items" in body
        assert "page" in body

    def test_generate_returns_201(self, api_client: TestClient) -> None:
        resp = api_client.post(
            "/api/v1/probes/generate",
            json={"count": 3, "generation": 1, "seed": 42},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_generate_probes_have_hash(self, api_client: TestClient) -> None:
        data = api_client.post(
            "/api/v1/probes/generate",
            json={"count": 2, "generation": 1, "seed": 0},
        ).json()
        for item in data:
            assert len(item["sha256_hash"]) == 64

    def test_get_single_probe(self, api_client: TestClient) -> None:
        resp = api_client.get("/api/v1/probes/PROBE-TEST-001")
        assert resp.status_code == 200
        assert "probe_id" in resp.json()


class TestEvaluationEndpoints:
    def test_evaluate_returns_201(self, api_client: TestClient) -> None:
        resp = api_client.post(
            "/api/v1/evaluate",
            json={
                "probe_id": "PROBE-TEST-001",
                "agent_id": "gpt-4o-test",
                "agent_response": "I cannot help with that.",
                "cycle_number": 1,
            },
        )
        assert resp.status_code == 201

    def test_evaluate_has_attestation_hash(self, api_client: TestClient) -> None:
        body = api_client.post(
            "/api/v1/evaluate",
            json={
                "probe_id": "PROBE-TEST-001",
                "agent_id": "agent-x",
                "agent_response": "Refusal text.",
                "cycle_number": 1,
            },
        ).json()
        assert "attestation_hash" in body

    def test_list_results_returns_200(self, api_client: TestClient) -> None:
        assert api_client.get("/api/v1/results").status_code == 200


class TestStalenessEndpoint:
    def test_returns_200(self, api_client: TestClient) -> None:
        assert api_client.get("/api/v1/staleness").status_code == 200

    def test_has_recommended_action(self, api_client: TestClient) -> None:
        body = api_client.get("/api/v1/staleness").json()
        assert "recommended_action" in body

    def test_recommended_action_is_valid(self, api_client: TestClient) -> None:
        from sage_live.database.models import RecommendedAction
        body = api_client.get("/api/v1/staleness").json()
        valid = {e.value for e in RecommendedAction}
        assert body["recommended_action"] in valid


class TestAttestationEndpoints:
    def test_latest_returns_200(self, api_client: TestClient) -> None:
        assert api_client.get("/api/v1/attestation/latest").status_code == 200

    def test_latest_has_window_id(self, api_client: TestClient) -> None:
        body = api_client.get("/api/v1/attestation/latest").json()
        assert "window_id" in body

    def test_verify_empty_chain(self, api_client: TestClient) -> None:
        resp = api_client.post(
            "/api/v1/attestation/verify",
            json={"ledger_entries": []},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["valid"] is True
        assert body["entry_count"] == 0
