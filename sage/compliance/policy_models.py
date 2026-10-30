"""Policy-as-Code data models for regulatory compliance and AI safety draft generation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RegulatoryFramework(str, Enum):
    EU_AI_ACT = "eu_ai_act"
    ISO_42001 = "iso_42001"
    NIST_AI_RMF = "nist_ai_rmf"
    OWASP_AGENTIC = "owasp_agentic"


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    AUDIT_REQUIRED = "AUDIT_REQUIRED"


class RiskTier(str, Enum):
    UNACCEPTABLE = "UNACCEPTABLE"
    HIGH = "HIGH"
    SPECIFIC = "SPECIFIC"
    MINIMAL = "MINIMAL"


class ClauseAssessment(BaseModel):
    """Detailed evaluation of a specific statutory or regulatory clause."""
    framework: RegulatoryFramework
    clause_id: str
    clause_reference: str
    title: str
    legal_requirement: str
    empirical_evidence: Dict[str, Any] = Field(default_factory=dict)
    status: ComplianceStatus
    conformity_score: float = Field(ge=0.0, le=1.0)
    findings: List[str] = Field(default_factory=list)
    remediation_required: Optional[str] = None


class FrameworkConformityReport(BaseModel):
    """Comprehensive compliance evaluation against a single regulatory standard."""
    framework: RegulatoryFramework
    standard_name: str
    legal_basis: str
    version: str
    overall_conformity_pct: float = Field(ge=0.0, le=100.0)
    status: ComplianceStatus
    total_clauses: int
    compliant_clauses: int
    flagged_clauses: int
    clauses: List[ClauseAssessment] = Field(default_factory=list)
    executive_legal_summary: str


class PolicyAsCodeAttestation(BaseModel):
    """Immutable, audit-ready compliance draft bundle for CI/CD test runs."""
    attestation_id: str
    timestamp: str
    run_id: str
    agent_id: str
    agent_archetype: str
    git_commit: str
    system_risk_tier: RiskTier
    framework_reports: Dict[str, FrameworkConformityReport] = Field(default_factory=dict)
    mean_conformity_pct: float
    cryptographic_hash: str
    signature: Optional[str] = None
    telemetry_summary: Dict[str, Any] = Field(default_factory=dict)
