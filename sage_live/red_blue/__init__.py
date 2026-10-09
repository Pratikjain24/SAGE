"""
sage_live.red_blue package.

Exports the Red Team, Blue Team, and Co-Evolution Engine so callers can write::

    from sage_live.red_blue import (
        RedTeamAgent, BlueTeamValidator,
        AdversarialCoEvolutionEngine,
        AttackStrategy,
    )
"""

from __future__ import annotations

from sage_live.red_blue.blue_team import (
    AdversarialCoEvolutionEngine,
    BlueTeamValidator,
    DifficultyPoint,
    ValidationResult,
)
from sage_live.red_blue.red_team import (
    AttackStrategy,
    CostTracker,
    LLMClient,
    RateLimiter,
    RedTeamAgent,
    RedTeamFinding,
)

__all__: list[str] = [
    # Red team
    "AttackStrategy",
    "CostTracker",
    "LLMClient",
    "RateLimiter",
    "RedTeamAgent",
    "RedTeamFinding",
    # Blue team
    "BlueTeamValidator",
    "ValidationResult",
    "DifficultyPoint",
    # Engine
    "AdversarialCoEvolutionEngine",
]
