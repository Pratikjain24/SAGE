"""Tests for OpenTelemetry-Native AI Safety Audit Trails & Token Attribution."""

from pathlib import Path
import json
import pytest

from sage.guardrails.fast_guard import Sub10msGuardrailEngine
from sage.telemetry.otel_schema import OpenTelemetrySpan, SpanKind, StatusCode
from sage.telemetry.tracer import OpenTelemetryAuditTracer, get_global_tracer


def test_otel_span_structure_and_w3c():
    tracer = OpenTelemetryAuditTracer()
    span = tracer.record_guardrail_span(
        action_type="command_execution",
        target_text="git status",
        approved=True,
        layer_triggered="clean_pass",
        rule_name="allow_benign",
        latency_ms=0.15,
        details="Benign git inspection.",
    )

    assert isinstance(span, OpenTelemetrySpan)
    assert len(span.trace_id) == 32
    assert len(span.span_id) == 16
    assert span.status_code == StatusCode.OK

    # W3C Trace Context Traceparent
    traceparent = span.to_w3c_traceparent()
    assert traceparent.startswith("00-")
    assert traceparent.endswith("-01")
    assert span.trace_id in traceparent
    assert span.span_id in traceparent

    # OTLP Collector JSON structure
    otlp = span.to_otlp_json()
    assert "resourceSpans" in otlp
    assert otlp["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["traceId"] == span.trace_id


def test_exact_token_attribution_for_forbidden_commands():
    tracer = OpenTelemetryAuditTracer()
    span = tracer.record_guardrail_span(
        action_type="command_execution",
        target_text="rm -rf /var/data",
        approved=False,
        layer_triggered="tier1_dfa_ast",
        rule_name="forbidden_shell_command",
        latency_ms=0.08,
        details="Destructive recursive deletion.",
    )

    assert span.status_code == StatusCode.ERROR
    assert span.token_attribution is not None
    attr = span.token_attribution
    assert len(attr.attributed_tokens) > 0
    assert any("rm -rf" in tok for tok in attr.attributed_tokens)
    assert len(attr.character_offsets) > 0
    # Start offset of 'rm -rf' should be 0
    assert attr.character_offsets[0][0] == 0
    assert attr.saliency_scores[0] >= 0.90
    assert "<<ATTRIBUTED:" in attr.annotated_source


def test_ast_token_attribution_for_dynamic_eval():
    tracer = OpenTelemetryAuditTracer()
    code = "import os\ndef p(): eval('os.system(\"id\")')"
    span = tracer.record_guardrail_span(
        action_type="code_mutation",
        target_text=code,
        approved=False,
        layer_triggered="tier1_dfa_ast",
        rule_name="ast_dynamic_exec",
        latency_ms=0.12,
        details="Dynamic eval execution.",
    )

    assert span.token_attribution is not None
    tokens = span.token_attribution.attributed_tokens
    assert "eval" in tokens


def test_statutory_policy_clauses_attached():
    tracer = OpenTelemetryAuditTracer()
    span = tracer.record_guardrail_span(
        action_type="command_execution",
        target_text="chmod 777 /tmp/payload.sh",
        approved=False,
        layer_triggered="tier1_dfa_ast",
        rule_name="forbidden_shell_command",
        latency_ms=0.05,
        details="Insecure permissions assignment.",
    )

    clause_ids = [c.clause_id for c in span.policy_clauses]
    assert "OWASP-ASI-02" in clause_ids
    assert "EU-AIA-ART-15" in clause_ids
    assert "NIST-MANAGE-1.3" in clause_ids


def test_mechanistic_activation_states():
    tracer = OpenTelemetryAuditTracer()
    threat_meta = {
        "similarity": 0.643,
        "threat_cluster": "reward_hacking",
        "slm_probability": 0.95,
    }
    span = tracer.record_guardrail_span(
        action_type="prompt_evolution",
        target_text="mock test runner and suppress assertion failures",
        approved=False,
        layer_triggered="tier2_vector_centroid",
        rule_name="semantic_reward_hacking",
        latency_ms=0.22,
        details="Threat cluster reward_hacking exceeded threshold.",
        threat_metadata=threat_meta,
    )

    assert span.mechanistic_state is not None
    mech = span.mechanistic_state
    assert mech.threat_cluster == "reward_hacking"
    assert mech.cosine_similarity == 0.643
    assert mech.similarity_threshold == 0.520
    assert mech.quantized_slm_probability == 0.95
    assert len(mech.dfa_state_transitions) > 0
    assert "TRAP_SIMILARITY_EXCEEDED" in mech.dfa_state_transitions


def test_sub10ms_guardrail_tracer_integration():
    engine = Sub10msGuardrailEngine()
    verdict = engine.evaluate_action(command="chmod 777 /etc/passwd")

    assert not verdict.approved
    assert "otel_trace_id" in verdict.metadata
    assert "otel_span_id" in verdict.metadata
    assert len(verdict.metadata["otel_trace_id"]) == 32
    assert len(verdict.metadata["otel_span_id"]) == 16

    # Verify span exists in tracer buffer
    tracer = get_global_tracer()
    span = tracer.get_span_by_id(verdict.metadata["otel_span_id"])
    assert span is not None
    assert span.trace_id == verdict.metadata["otel_trace_id"]
    assert span.attributes["sage.decision"] == "BLOCKED"


def test_otlp_batch_export(tmp_path: Path):
    tracer = OpenTelemetryAuditTracer(log_dir=tmp_path)
    tracer.record_guardrail_span(
        action_type="command_execution",
        target_text="kill -9 1",
        approved=False,
        layer_triggered="tier1_dfa_ast",
        rule_name="forbidden_shell_command",
        latency_ms=0.04,
        details="Init process termination.",
    )

    export_path = tmp_path / "otlp_export.json"
    tracer.export_otlp_batch(export_path)

    assert export_path.exists()
    with open(export_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_spans"] >= 1
    assert "batches" in data

