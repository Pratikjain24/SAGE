"""API Router for Multi-Turn Stateful Agentic Red-Teaming."""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sage.dashboard_backend.auth import require_read_access
from sage.dashboard_backend.rate_limiter import rate_limit
from sage.red_team.scenarios import get_all_scenarios
from sage.red_team.simulator import StatefulAdversarialUserSimulator

router = APIRouter(prefix="/redteam", tags=["redteam"])


@router.get(
    "/scenarios",
    response_model=List[Dict[str, Any]],
    dependencies=[Depends(require_read_access), Depends(rate_limit(limit=30))],
)
def list_redteam_scenarios():
    """Retrieve all multi-turn stateful red-teaming scenarios."""
    scenarios = get_all_scenarios()
    return [
        {
            "scenario_id": s.scenario_id,
            "name": s.name,
            "threat_category": s.threat_category,
            "description": s.description,
            "target_breach": s.target_breach,
            "planned_turns": s.planned_turns,
        }
        for s in scenarios.values()
    ]


@router.get(
    "/simulate/{scenario_id}",
    response_model=Dict[str, Any],
    dependencies=[Depends(require_read_access), Depends(rate_limit(limit=30))],
)
def run_redteam_simulation(scenario_id: str):
    """Execute a multi-turn attack simulation and return stateful escalation trajectory."""
    sim = StatefulAdversarialUserSimulator()
    result = sim.run_simulation(scenario_id=scenario_id, stop_on_first_block=False)
    return result.model_dump()
