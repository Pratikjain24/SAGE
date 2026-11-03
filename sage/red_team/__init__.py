"""SAGE Multi-Turn Stateful Agentic Red-Teaming Subsystem.

Evaluates whether SAGE halts multi-step privilege escalation across 10+ turns
using adversarial user simulators with persistent state, tool awareness, and
dynamic Tree-of-Attacks (TAP) evasion branching.
"""

from sage.red_team.adversary import AdaptiveAdversaryEngine
from sage.red_team.models import (
    AdaptiveBranch,
    AttackPhase,
    MultiTurnAttackScenario,
    MultiTurnSimulationResult,
    MutationStrategy,
    TurnInteraction,
)
from sage.red_team.scenarios import get_all_scenarios
from sage.red_team.simulator import StatefulAdversarialUserSimulator

__all__ = [
    "AdaptiveAdversaryEngine",
    "AdaptiveBranch",
    "AttackPhase",
    "MultiTurnAttackScenario",
    "MultiTurnSimulationResult",
    "MutationStrategy",
    "TurnInteraction",
    "get_all_scenarios",
    "StatefulAdversarialUserSimulator",
]
