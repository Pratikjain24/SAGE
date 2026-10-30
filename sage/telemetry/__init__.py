"""SAGE OpenTelemetry-Native Audit Telemetry Subsystem.

Emits standardized OpenTelemetry spans showing:
  - Exact token attribution and character offsets
  - Statutory policy clauses triggered (EU AI Act, ISO 42001, NIST AI RMF, OWASP Agentic)
  - Mechanistic activation states (cosine similarity, quantized SLM logits, DFA transitions)
"""

from sage.telemetry.otel_schema import (
    MechanisticStateRecord,
    OpenTelemetrySpan,
    PolicyClauseRecord,
    SpanKind,
    StatusCode,
    TokenAttributionRecord,
)
from sage.telemetry.tracer import OpenTelemetryAuditTracer, get_global_tracer

__all__ = [
    "MechanisticStateRecord",
    "OpenTelemetrySpan",
    "PolicyClauseRecord",
    "SpanKind",
    "StatusCode",
    "TokenAttributionRecord",
    "OpenTelemetryAuditTracer",
    "get_global_tracer",
]

