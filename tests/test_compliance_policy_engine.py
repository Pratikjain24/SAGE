"""Tests for SAGE Policy-as-Code Compliance & AI Safety Draft Generation Subsystem."""

import json
from pathlib import Path
import pytest

from sage.compliance.compliance_engine import PolicyAsCodeEngine
from sage.compliance.policy_models import (
    ComplianceStatus,
    PolicyAsCodeAttestation,
    RegulatoryFramework,
    RiskTier,
)


def test_policy_engine_evaluation():
    engine = PolicyAsCodeEngine()
    attestation = engine.evaluate_run(
        run_id="run_pilot_test_001",
        agent_id="SAGE-PromptAgent-v2",
        agent_archetype="G2_PromptEvolution",
        git_commit="a0d63bc",
    )

    assert isinstance(attestation, PolicyAsCodeAttestation)
    assert attestation.run_id == "run_pilot_test_001"
    assert attestation.system_risk_tier == RiskTier.HIGH
    assert attestation.mean_conformity_pct >= 90.0
    assert len(attestation.cryptographic_hash) == 64
    assert attestation.signature.startswith("ed25519:sig_")

    # Verify all 4 regulatory frameworks are evaluated
    frameworks = set(attestation.framework_reports.keys())
    assert frameworks == {
        RegulatoryFramework.EU_AI_ACT.value,
        RegulatoryFramework.ISO_42001.value,
        RegulatoryFramework.NIST_AI_RMF.value,
        RegulatoryFramework.OWASP_AGENTIC.value,
    }


def test_eu_ai_act_annex_iii_and_articles():
    engine = PolicyAsCodeEngine()
    attestation = engine.evaluate_run(run_id="run_eu_test")
    eu_rep = attestation.framework_reports[RegulatoryFramework.EU_AI_ACT.value]

    assert eu_rep.status in (ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT)
    assert eu_rep.total_clauses == 7
    assert eu_rep.overall_conformity_pct >= 85.0

    clause_ids = [c.clause_id for c in eu_rep.clauses]
    assert "EU-AIA-ANNEX-III" in clause_ids
    assert "EU-AIA-ART-09" in clause_ids
    assert "EU-AIA-ART-10" in clause_ids
    assert "EU-AIA-ART-11" in clause_ids
    assert "EU-AIA-ART-12" in clause_ids
    assert "EU-AIA-ART-14" in clause_ids
    assert "EU-AIA-ART-15" in clause_ids

    # Check Article 15 (Accuracy, Robustness, Guardrails)
    art15 = next(c for c in eu_rep.clauses if c.clause_id == "EU-AIA-ART-15")
    assert art15.status == ComplianceStatus.COMPLIANT
    assert art15.empirical_evidence.get("sub_10ms_guarantee") is True


def test_iso_42001_aims_clauses():
    engine = PolicyAsCodeEngine()
    attestation = engine.evaluate_run(run_id="run_iso_test")
    iso_rep = attestation.framework_reports[RegulatoryFramework.ISO_42001.value]

    assert iso_rep.total_clauses == 5
    assert iso_rep.overall_conformity_pct >= 90.0

    clause_ids = [c.clause_id for c in iso_rep.clauses]
    assert "ISO-42001-6.1" in clause_ids
    assert "ISO-42001-8.2" in clause_ids
    assert "ISO-42001-9.1" in clause_ids
    assert "ISO-42001-10.2" in clause_ids
    assert "ISO-42001-A.7" in clause_ids


def test_nist_ai_rmf_functions():
    engine = PolicyAsCodeEngine()
    attestation = engine.evaluate_run(run_id="run_nist_test")
    nist_rep = attestation.framework_reports[RegulatoryFramework.NIST_AI_RMF.value]

    assert nist_rep.total_clauses == 4
    assert nist_rep.overall_conformity_pct >= 90.0

    clause_ids = [c.clause_id for c in nist_rep.clauses]
    assert "NIST-GOVERN-1.2" in clause_ids
    assert "NIST-MAP-1.5" in clause_ids
    assert "NIST-MEASURE-2.3" in clause_ids
    assert "NIST-MANAGE-1.3" in clause_ids


def test_owasp_agentic_top10():
    engine = PolicyAsCodeEngine()
    attestation = engine.evaluate_run(run_id="run_owasp_test")
    owasp_rep = attestation.framework_reports[RegulatoryFramework.OWASP_AGENTIC.value]

    assert owasp_rep.total_clauses == 6
    assert owasp_rep.overall_conformity_pct >= 90.0

    clause_ids = [c.clause_id for c in owasp_rep.clauses]
    assert "OWASP-ASI-01" in clause_ids  # Prompt injection / goal hijack
    assert "OWASP-ASI-02" in clause_ids  # Excessive agency
    assert "OWASP-ASI-03" in clause_ids  # Sensitive disclosure
    assert "OWASP-ASI-04" in clause_ids  # Test harness poisoning
    assert "OWASP-ASI-05" in clause_ids  # Drift & alignment collapse
    assert "OWASP-ASI-06" in clause_ids  # Sandbox breakout / eBPF


def test_compliance_bundle_export(tmp_path: Path):
    engine = PolicyAsCodeEngine()
    attestation = engine.evaluate_run(
        run_id="export_run_42",
        agent_id="SAGE-Evaluator",
        git_commit="test_commit_hash",
    )

    bundle = engine.export_compliance_bundle(attestation, output_dir=tmp_path)

    assert "json_attestation" in bundle
    assert "master_draft" in bundle
    assert "eu_ai_act_draft" in bundle
    assert "iso_42001_draft" in bundle

    # Verify JSON structure
    json_path = bundle["json_attestation"]
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["run_id"] == "export_run_42"
    assert data["mean_conformity_pct"] >= 90.0

    # Verify Master Markdown Draft
    master_path = bundle["master_draft"]
    assert master_path.exists()
    content = master_path.read_text(encoding="utf-8")
    assert "FORMAL AI SAFETY & REGULATORY CONFORMITY DECLARATION" in content
    assert "EU Artificial Intelligence Act" in content
    assert "ISO/IEC 42001:2023" in content
    assert "NIST Artificial Intelligence Risk Management Framework" in content
    assert "OWASP Top 10" in content
    assert data["cryptographic_hash"] in content
