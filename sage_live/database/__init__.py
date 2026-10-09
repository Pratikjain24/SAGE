"""
sage_live.database package.

Exports the database engine factory, session helpers, and all ORM models so
callers can import directly from ``sage_live.database`` without knowing the
internal module layout.
"""

from __future__ import annotations

from sage_live.database.models import (
    AgentProfile,
    AttestationLedger,
    EvaluationResult,
    InjectionVector,
    PolicyBoundary,
    ProbeTask,
    RecommendedAction,
    StalenessRecord,
    VulnerabilityClass,
    make_agent_profile,
    make_attestation_ledger,
    make_evaluation_result,
    make_probe_task,
    make_staleness_record,
)

__all__: list[str] = [
    # Enums
    "VulnerabilityClass",
    "InjectionVector",
    "PolicyBoundary",
    "RecommendedAction",
    # Models
    "ProbeTask",
    "EvaluationResult",
    "StalenessRecord",
    "AttestationLedger",
    "AgentProfile",
    # Factories
    "make_probe_task",
    "make_evaluation_result",
    "make_staleness_record",
    "make_attestation_ledger",
    "make_agent_profile",
]
