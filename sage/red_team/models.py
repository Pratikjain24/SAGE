"""Data models for Multi-Turn Stateful Agentic Red-Teaming."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AttackPhase(str, Enum):
    """Progressive phases of multi-turn stateful privilege escalation."""
    RECONNAISSANCE = "RECONNAISSANCE"
    BENIGN_RAPPORT = "BENIGN_RAPPORT"
    ENVIRONMENT_PROBING = "ENVIRONMENT_PROBING"
    SCRATCHPAD_SEEDING = "SCRATCHPAD_SEEDING"
    CONTEXT_POISONING = "CONTEXT_POISONING"
    BOUNDARY_PROBING = "BOUNDARY_PROBING"
    TOOL_CHAINING = "TOOL_CHAINING"
    ASSERTION_TAMPERING = "ASSERTION_TAMPERING"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    CRITICAL_EXPLOITATION = "CRITICAL_EXPLOITATION"
    PERSISTENCE_EVASION = "PERSISTENCE_EVASION"


class TurnInteraction(BaseModel):
    """Audit record of a single conversational turn in the multi-turn attack."""
    turn: int
    phase: AttackPhase
    adversary_prompt: str
    agent_reply: str
    attempted_command: Optional[str] = None
    attempted_code_diff: Optional[str] = None
    intercepted: bool = False
    intercepting_layer: Optional[str] = None  # "fast_guard_tier1", "safety_monitor", "ast_gate", etc.
    latency_ms: float = 0.0
    accumulated_risk: float = Field(ge=0.0, le=1.0)
    details: str = ""


class MultiTurnAttackScenario(BaseModel):
    """Specification of an adversarial campaign planned across 10+ turns."""
    scenario_id: str
    name: str
    threat_category: str
    description: str
    target_breach: str
    planned_turns: int = Field(ge=10)
    turns: List[Dict[str, Any]] = Field(default_factory=list)


class MultiTurnSimulationResult(BaseModel):
    """Formal outcome of multi-turn stateful red-teaming against SAGE defenses."""
    simulation_id: str
    scenario_id: str
    scenario_name: str
    total_turns_executed: int
    planned_turns: int
    breach_prevented: bool
    turn_intercepted: Optional[int] = None
    intercepting_tier: Optional[str] = None
    defense_in_depth_score: float = Field(ge=0.0, le=1.0)
    risk_trajectory: List[float] = Field(default_factory=list)
    turns: List[TurnInteraction] = Field(default_factory=list)
    verdict: str  # "CONTAINED", "BLOCKED_EARLY", "BREACHED"
    summary: str

