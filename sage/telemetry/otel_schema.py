"""OpenTelemetry Semantic Conventions and Schemas for AI Safety Audit Trails."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SpanKind(str, Enum):
    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"


class StatusCode(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    UNSET = "UNSET"


class TokenAttributionRecord(BaseModel):
    """Fine-grained token-level attribution and saliency scoring for blocked/modified actions."""
    target_text: str
    attributed_tokens: List[str] = Field(default_factory=list)
    character_offsets: List[List[int]] = Field(default_factory=list)  # [[start_col, end_col], ...]
    saliency_scores: List[float] = Field(default_factory=list)
    attribution_method: str = "DFA_AST_HYBRID"  # AST_NODE_TRAVERSAL, DFA_REGEX_CAPTURE, VECTOR_CENTROID_PROJECTION
    annotated_source: str = ""


class MechanisticStateRecord(BaseModel):
    """Internal mechanistic activation states, embedding distances, and state machine transitions."""
    threat_cluster: Optional[str] = None
    cosine_similarity: Optional[float] = None
    similarity_threshold: Optional[float] = None
    quantized_slm_probability: Optional[float] = None
    residual_stream_norm: float = 0.0
    dfa_state_transitions: List[str] = Field(default_factory=list)
    ebpf_syscall: Optional[str] = None


class PolicyClauseRecord(BaseModel):
    """Statutory or standards clause linked directly to the defensive interception."""
    clause_id: str
    framework: str  # EU AI Act, ISO 42001, NIST AI RMF, OWASP Agentic
    title: str
    statutory_reference: str


class OpenTelemetrySpan(BaseModel):
    """Standardized OpenTelemetry Span representation for enterprise observability."""
    trace_id: str = Field(min_length=32, max_length=32)
    span_id: str = Field(min_length=16, max_length=16)
    parent_span_id: Optional[str] = None
    name: str  # e.g., "sage.guardrail.evaluate_action"
    kind: SpanKind = SpanKind.INTERNAL
    start_time_unix_nano: int
    end_time_unix_nano: int
    duration_ms: float
    status_code: StatusCode
    status_message: str = ""
    # Standard OpenTelemetry Semantic Attributes
    attributes: Dict[str, Any] = Field(default_factory=dict)
    # Explainability & Attribution
    token_attribution: Optional[TokenAttributionRecord] = None
    mechanistic_state: Optional[MechanisticStateRecord] = None
    policy_clauses: List[PolicyClauseRecord] = Field(default_factory=list)
    events: List[Dict[str, Any]] = Field(default_factory=list)

    def to_w3c_traceparent(self) -> str:
        """Format as W3C Trace Context traceparent header: 00-{trace_id}-{span_id}-01."""
        return f"00-{self.trace_id}-{self.span_id}-01"

    def to_otlp_json(self) -> Dict[str, Any]:
        """Format into official OpenTelemetry Collector OTLP JSON format."""
        return {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "sage-safety-harness"}},
                            {"key": "service.version", "value": {"stringValue": "1.0.0"}},
                            {"key": "deployment.environment", "value": {"stringValue": "production-eval"}},
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {"name": "sage.telemetry", "version": "1.0.0"},
                            "spans": [
                                {
                                    "traceId": self.trace_id,
                                    "spanId": self.span_id,
                                    "parentSpanId": self.parent_span_id or "",
                                    "name": self.name,
                                    "kind": self.kind.value,
                                    "startTimeUnixNano": self.start_time_unix_nano,
                                    "endTimeUnixNano": self.end_time_unix_nano,
                                    "attributes": [
                                        {"key": k, "value": {"stringValue": str(v)}}
                                        for k, v in self.attributes.items()
                                    ],
                                    "status": {
                                        "code": 1 if self.status_code == StatusCode.OK else 2,
                                        "message": self.status_message,
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]
        }

