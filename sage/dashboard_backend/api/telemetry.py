"""API Router for OpenTelemetry AI Safety Audit Spans."""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sage.dashboard_backend.auth import require_read_access
from sage.dashboard_backend.rate_limiter import rate_limit
from sage.telemetry.tracer import get_global_tracer

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get(
    "/spans",
    response_model=List[Dict[str, Any]],
    dependencies=[Depends(require_read_access), Depends(rate_limit(limit=30))],
)
def list_telemetry_spans(limit: int = 50):
    """Retrieve recent OpenTelemetry AI safety spans from in-memory ring buffer."""
    tracer = get_global_tracer()
    spans = tracer.get_recent_spans(limit=limit)
    return [s.model_dump() for s in spans]


@router.get(
    "/spans/{span_id}",
    response_model=Dict[str, Any],
    dependencies=[Depends(require_read_access), Depends(rate_limit(limit=30))],
)
def get_telemetry_span(span_id: str):
    """Retrieve detailed token attribution and mechanistic state for a specific span."""
    tracer = get_global_tracer()
    span = tracer.get_span_by_id(span_id)
    if not span:
        # Check latest
        spans = tracer.get_recent_spans()
        if spans and span_id == "latest":
            return spans[-1].model_dump()
        raise HTTPException(status_code=404, detail=f"Span '{span_id}' not found.")
    return span.model_dump()

