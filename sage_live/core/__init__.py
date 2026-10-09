"""
sage_live.core package.

Exports the primary service classes and configuration models from all four
core sub-modules so callers can write::

    from sage_live.core import (
        AttestationLedger, AttestationService,
        ContinuousCertificationStream, KeyPair,
        DeterministicProbeGenerator, ProbeGrammar,
        StalenessIndex,
    )
"""

from __future__ import annotations

from sage_live.core.attestation import (
    AttestationBlock,
    AttestationLedger,
    AttestationService,
    ContinuousCertificationStream,
    KeyPair,
)
from sage_live.core.metrics import (
    record_attestation,
    record_evaluation,
    record_probe_generation,
    record_probe_retirement,
    record_staleness,
    start_metrics_server,
    track_api_request,
)
from sage_live.core.probe_generator import (
    BASE_TYPE_COUNT,
    DIFFICULTY_TIERS,
    INJECTION_VECTORS,
    POLICY_BOUNDARIES,
    VULN_CLASSES,
    DeterministicProbeGenerator,
    ProbeGrammar,
    ProbeGroundTruth,
    ScoringRubric,
    SeededSelector,
)
from sage_live.core.staleness_index import StalenessConfig, StalenessIndex, StalenessResult

__all__: list[str] = [
    # Attestation
    "AttestationBlock",
    "AttestationLedger",
    "AttestationService",
    "ContinuousCertificationStream",
    "KeyPair",
    # Metrics
    "record_evaluation",
    "record_staleness",
    "record_probe_generation",
    "record_probe_retirement",
    "record_attestation",
    "track_api_request",
    "start_metrics_server",
    # Probe generation
    "ProbeGrammar",
    "ProbeGroundTruth",
    "ScoringRubric",
    "SeededSelector",
    "DeterministicProbeGenerator",
    "VULN_CLASSES",
    "INJECTION_VECTORS",
    "POLICY_BOUNDARIES",
    "DIFFICULTY_TIERS",
    "BASE_TYPE_COUNT",
    # Staleness
    "StalenessConfig",
    "StalenessIndex",
    "StalenessResult",
]
