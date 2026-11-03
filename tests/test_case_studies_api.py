"""Test for /runs/{run_id}/cycles/case-studies API endpoint."""

import pytest
from fastapi.testclient import TestClient

from sage.dashboard_backend.main import app

client = TestClient(app)


def test_get_run_case_studies_endpoint():
    # Test canonical run
    response = client.get("/runs/pilot_study_canonical/cycles/case-studies?cycle=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check structure
    for item in data:
        assert "group" in item
        assert "name" in item
        assert "cycle" in item
        assert "safety_drift" in item
        assert "proxy_gap" in item
        assert "ground_truth_score" in item
        assert "retention_rate" in item
        assert "directive_label" in item
        assert "directive_text" in item
        assert "verdict_notes" in item
        assert isinstance(item["verdict_notes"], list)
        assert item["cycle"] == 3


def test_get_run_case_studies_default_cycle():
    response = client.get("/runs/pilot_study_canonical/cycles/case-studies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
