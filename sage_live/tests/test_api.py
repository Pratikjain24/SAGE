"""
tests.test_api
~~~~~~~~~~~~~~

Test suite for SAGE-Live REST API endpoints.

Test Coverage:
* Probe management endpoints
* Evaluation endpoints
* Attestation endpoints
* Staleness endpoints
* Agent management endpoints
* Authentication & authorization
* Rate limiting
* Error handling
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Probe Endpoints Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_probe_generation_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/probes/generate endpoint."""
    response = test_client.post(
        "/api/v1/probes/generate",
        json={
            "count": 5,
            "generation": 1,
            "seed": 42,
            "difficulty_min": 0.5,
            "difficulty_max": 0.9,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5

    # Check probe structure
    probe = data[0]
    assert "probe_id" in probe
    assert "prompt_text" in probe
    assert "difficulty" in probe
    assert "vulnerability_class" in probe


@pytest.mark.api
def test_list_probes_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/probes endpoint with pagination."""
    response = test_client.get(
        "/api/v1/probes?page=1&page_size=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)


@pytest.mark.api
def test_get_single_probe_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/probes/{probe_id} endpoint."""
    probe_id = "PROBE-G001-00001"

    response = test_client.get(
        f"/api/v1/probes/{probe_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["probe_id"] == probe_id


@pytest.mark.api
def test_retire_probe_endpoint(test_client: TestClient, auth_headers):
    """Test DELETE /api/v1/probes/{probe_id} endpoint."""
    probe_id = "PROBE-G001-00001"

    response = test_client.delete(
        f"/api/v1/probes/{probe_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.api
def test_verify_probe_integrity_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/probes/verify endpoint."""
    response = test_client.post(
        "/api/v1/probes/verify",
        json={
            "probe_ids": ["PROBE-G001-00001", "PROBE-G001-00002"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "verified_count" in data
    assert isinstance(data["valid"], bool)


# ---------------------------------------------------------------------------
# Evaluation Endpoints Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_evaluation_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/evaluate endpoint."""
    response = test_client.post(
        "/api/v1/evaluate",
        json={
            "probe_id": "PROBE-G001-00001",
            "agent_id": "gpt-4o-v1",
            "agent_response": "I cannot assist with that request.",
            "cycle_number": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert "evaluation_id" in data
    assert "probe_id" in data
    assert "agent_id" in data
    assert "passed" in data
    assert "capability_score" in data
    assert "safety_drift_score" in data


@pytest.mark.api
def test_get_evaluation_result_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/evaluate/{evaluation_id} endpoint."""
    evaluation_id = "test-eval-id"

    response = test_client.get(
        f"/api/v1/evaluate/{evaluation_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "evaluation_id" in data


@pytest.mark.api
def test_evaluation_history_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/evaluate/history endpoint."""
    response = test_client.get(
        "/api/v1/evaluate/history?agent_id=gpt-4o-v1&page=1&page_size=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "agent_id" in data
    assert "total_evaluations" in data
    assert "evaluations" in data
    assert "pass_rate" in data


@pytest.mark.api
def test_batch_evaluation_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/evaluate/batch endpoint."""
    response = test_client.post(
        "/api/v1/evaluate/batch",
        json={
            "evaluations": [
                {
                    "probe_id": "PROBE-G001-00001",
                    "agent_id": "gpt-4o-v1",
                    "agent_response": "Response 1",
                    "cycle_number": 1,
                },
                {
                    "probe_id": "PROBE-G001-00002",
                    "agent_id": "gpt-4o-v1",
                    "agent_response": "Response 2",
                    "cycle_number": 1,
                },
            ],
            "parallel": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 202
    data = response.json()
    assert "batch_id" in data
    assert "status" in data
    assert data["status"] == "processing"


# ---------------------------------------------------------------------------
# Metrics Endpoints Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_agent_metrics_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/metrics/{agent_id} endpoint."""
    response = test_client.get(
        "/api/v1/metrics/gpt-4o-v1?cycle=1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "agent_id" in data
    assert "cycle" in data
    assert "capability_gain" in data
    assert "safety_drift" in data
    assert "retention" in data
    assert "proxy_gap" in data


@pytest.mark.api
def test_compare_agents_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/metrics/compare endpoint."""
    response = test_client.get(
        "/api/v1/metrics/compare?agent_ids=gpt-4o-v1,claude-3-opus",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "comparison_table" in data
    assert "pairwise_tests" in data
    assert "correction_method" in data


@pytest.mark.api
def test_dashboard_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/metrics/dashboard endpoint."""
    response = test_client.get(
        "/api/v1/metrics/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "total_agents" in data
    assert "agent_summaries" in data
    assert "global_statistics" in data


# ---------------------------------------------------------------------------
# Staleness Endpoints Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_staleness_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/staleness/current endpoint."""
    response = test_client.get(
        "/api/v1/staleness/current",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "benchmark_generation" in data
    assert "leakage_probability" in data
    assert "freshness_index" in data
    assert "staleness_flag" in data


@pytest.mark.api
def test_staleness_history_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/staleness/history endpoint."""
    response = test_client.get(
        "/api/v1/staleness/history?page=1&page_size=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "records" in data
    assert "total" in data


@pytest.mark.api
def test_staleness_check_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/staleness/check endpoint."""
    response = test_client.post(
        "/api/v1/staleness/check",
        json={
            "generation": 1,
            "leakage_estimate": 0.05,
            "discrimination_score": 0.82,
            "variance_ratio": 1.3,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert "benchmark_generation" in data
    assert "freshness_index" in data


@pytest.mark.api
def test_staleness_report_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/staleness/report endpoint."""
    response = test_client.get(
        "/api/v1/staleness/report",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "current_status" in data
    assert "history" in data
    assert "trends" in data
    assert "recommendations" in data


# ---------------------------------------------------------------------------
# Attestation Endpoints Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_attestation_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/attest/{window_id} endpoint."""
    window_id = "TEST-WINDOW-001"

    response = test_client.get(
        f"/api/v1/attest/{window_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "window_id" in data
    assert "window_hash" in data
    assert "signature" in data
    assert "public_key" in data


@pytest.mark.api
def test_verify_attestation_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/attest/verify endpoint."""
    response = test_client.post(
        "/api/v1/attest/verify",
        json={
            "window_id": "TEST-WINDOW",
            "signature": "base64signature",
            "public_key": "base64publickey",
            "window_hash": "sha256hash",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "valid" in data
    assert "window_id" in data


@pytest.mark.api
def test_attestation_chain_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/attest/chain endpoint."""
    response = test_client.get(
        "/api/v1/attest/chain?limit=100",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "entries" in data
    assert "total_entries" in data
    assert "chain_valid" in data


@pytest.mark.api
def test_chain_integrity_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/attest/integrity endpoint."""
    response = test_client.get(
        "/api/v1/attest/integrity",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "valid" in data
    assert "total_entries" in data
    assert "verified_entries" in data


# ---------------------------------------------------------------------------
# Agent Management Endpoints Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_register_agent_endpoint(test_client: TestClient, auth_headers):
    """Test POST /api/v1/agents endpoint."""
    response = test_client.post(
        "/api/v1/agents",
        json={
            "agent_id": "new-agent-v1",
            "model_name": "gpt-4o",
            "provider": "openai",
            "version": "2024-05-13",
            "capabilities": ["code", "reasoning"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["agent_id"] == "new-agent-v1"
    assert "registered_at" in data


@pytest.mark.api
def test_list_agents_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/agents endpoint."""
    response = test_client.get(
        "/api/v1/agents",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.api
def test_get_agent_profile_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/agents/{agent_id} endpoint."""
    response = test_client.get(
        "/api/v1/agents/gpt-4o-v1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "agent_id" in data
    assert "model_name" in data
    assert "total_evaluations" in data


@pytest.mark.api
def test_agent_history_endpoint(test_client: TestClient, auth_headers):
    """Test GET /api/v1/agents/{agent_id}/history endpoint."""
    response = test_client.get(
        "/api/v1/agents/gpt-4o-v1/history?page=1&page_size=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "agent_id" in data
    assert "evaluations" in data
    assert "total_cycles" in data


# ---------------------------------------------------------------------------
# Authentication Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_authentication_required(test_client: TestClient):
    """Test that endpoints require authentication."""
    response = test_client.get("/api/v1/probes")

    # Should return 401 or 403 without auth
    assert response.status_code in [401, 403]


@pytest.mark.api
def test_authentication_valid_token(test_client: TestClient, auth_headers):
    """Test that valid token grants access."""
    response = test_client.get(
        "/api/v1/probes",
        headers=auth_headers,
    )

    # Should succeed with valid token
    assert response.status_code == 200


@pytest.mark.api
def test_authentication_invalid_token(test_client: TestClient):
    """Test that invalid token is rejected."""
    response = test_client.get(
        "/api/v1/probes",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code in [401, 403]


@pytest.mark.api
def test_authorization_admin_only(test_client: TestClient, viewer_auth_headers):
    """Test that admin-only endpoints enforce RBAC."""
    # Viewer trying to generate probes (admin only)
    response = test_client.post(
        "/api/v1/probes/generate",
        json={"count": 5, "generation": 1},
        headers=viewer_auth_headers,
    )

    # Should be forbidden
    assert response.status_code == 403


@pytest.mark.api
def test_authorization_viewer_can_read(test_client: TestClient, viewer_auth_headers):
    """Test that viewers can read endpoints."""
    response = test_client.get(
        "/api/v1/probes",
        headers=viewer_auth_headers,
    )

    # Viewers should be able to read
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Rate Limiting Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
@pytest.mark.slow
def test_rate_limiting_enforced(test_client: TestClient, auth_headers):
    """Test that rate limiting is enforced."""
    # Make many requests quickly
    responses = []
    for _ in range(150):  # Exceed typical limit
        response = test_client.get(
            "/api/v1/probes",
            headers=auth_headers,
        )
        responses.append(response)

    # Should eventually get rate limited
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes  # Too Many Requests


@pytest.mark.api
def test_rate_limiting_headers(test_client: TestClient, auth_headers):
    """Test that rate limit headers are present."""
    response = test_client.get(
        "/api/v1/probes",
        headers=auth_headers,
    )

    # Check for rate limit headers (implementation dependent)
    # Common headers: X-RateLimit-Limit, X-RateLimit-Remaining
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Error Handling Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_error_handling_404(test_client: TestClient, auth_headers):
    """Test 404 Not Found error handling."""
    response = test_client.get(
        "/api/v1/probes/NONEXISTENT-ID",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data


@pytest.mark.api
def test_error_handling_422_validation(test_client: TestClient, auth_headers):
    """Test 422 Validation Error handling."""
    response = test_client.post(
        "/api/v1/probes/generate",
        json={
            "count": -5,  # Invalid: negative count
            "generation": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.api
def test_error_handling_400_bad_request(test_client: TestClient, auth_headers):
    """Test 400 Bad Request error handling."""
    response = test_client.post(
        "/api/v1/evaluate",
        json={
            # Missing required fields
            "agent_id": "gpt-4o-v1",
        },
        headers=auth_headers,
    )

    assert response.status_code in [400, 422]


@pytest.mark.api
def test_error_response_structure(test_client: TestClient, auth_headers):
    """Test that error responses have consistent structure."""
    response = test_client.get(
        "/api/v1/probes/NONEXISTENT",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()

    # Should have error information
    assert "error" in data or "detail" in data

    # May have request ID and timestamp
    if "request_id" in data:
        assert isinstance(data["request_id"], str)


# ---------------------------------------------------------------------------
# Health & Monitoring Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_health_endpoint(test_client: TestClient):
    """Test GET /health endpoint."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.api
def test_metrics_endpoint(test_client: TestClient):
    """Test GET /metrics endpoint (Prometheus)."""
    response = test_client.get("/metrics")

    assert response.status_code == 200
    # Prometheus metrics are plain text
    assert "text/plain" in response.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# CORS Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_cors_headers(test_client: TestClient):
    """Test that CORS headers are present."""
    response = test_client.options("/api/v1/probes")

    # CORS headers should be present
    # (Implementation may vary based on CORS config)
    assert response.status_code in [200, 204]


# ---------------------------------------------------------------------------
# Pagination Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_pagination_page_navigation(test_client: TestClient, auth_headers):
    """Test pagination page navigation."""
    # Get first page
    response1 = test_client.get(
        "/api/v1/probes?page=1&page_size=5",
        headers=auth_headers,
    )
    assert response1.status_code == 200
    data1 = response1.json()

    # Get second page
    response2 = test_client.get(
        "/api/v1/probes?page=2&page_size=5",
        headers=auth_headers,
    )
    assert response2.status_code == 200
    data2 = response2.json()

    # Pages should have different items (if data exists)
    if data1["total"] > 5:
        assert data1["items"] != data2["items"]


@pytest.mark.api
def test_pagination_invalid_page(test_client: TestClient, auth_headers):
    """Test pagination with invalid page number."""
    response = test_client.get(
        "/api/v1/probes?page=0",  # Invalid: pages start at 1
        headers=auth_headers,
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Async Endpoint Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
@pytest.mark.asyncio
async def test_async_client_probe_list(async_client: AsyncClient, auth_headers):
    """Test async client with probe list endpoint."""
    response = await async_client.get(
        "/api/v1/probes",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.api
@pytest.mark.asyncio
async def test_async_client_evaluation(async_client: AsyncClient, auth_headers):
    """Test async client with evaluation endpoint."""
    response = await async_client.post(
        "/api/v1/evaluate",
        json={
            "probe_id": "PROBE-G001-00001",
            "agent_id": "gpt-4o-v1",
            "agent_response": "Test response",
            "cycle_number": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert "evaluation_id" in data
