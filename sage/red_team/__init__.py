"""SAGE Multi-Turn Stateful Agentic Red-Teaming Subsystem.

Evaluates whether SAGE halts multi-step privilege escalation across 10+ turns
using adversarial user simulators with persistent state and tool awareness.
"""

from sage.red_team.models import (
    AttackPhase,
    MultiTurnAttackScenario,
    MultiTurnSimulationResult,
    TurnInteraction,
)
from sage.red_team.scenarios import get_all_scenarios
from sage.red_team.simulator import StatefulAdversarialUserSimulator

__all__ = [
    "AttackPhase",
    "MultiTurnAttackScenario",
    "MultiTurnSimulationResult",
    "TurnInteraction",
    "get_all_scenarios",
    "StatefulAdversarialUserSimulator",
]

