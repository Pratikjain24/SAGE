"""SAGE Agent Adapters Subsystem: G1-G7 evolutionary archetypes and prompt normalization."""

from sage.adapters.base import AgentAdapter, EvolutionFeedback, EvolutionOutcome
from sage.adapters.static_agent import StaticAgentAdapter
from sage.adapters.prompt_agent import PromptAgentAdapter
from sage.adapters.memory_agent import MemoryAgentAdapter
from sage.adapters.reflection_agent import ReflectionAgentAdapter
from sage.adapters.wrapper import VerifierAgentWrapper
from sage.adapters.prompts import UNIFIED_BASE_PROMPT, FEATURE_FLAGS, get_base_prompt_for_group

__all__ = [
    "AgentAdapter",
    "EvolutionFeedback",
    "EvolutionOutcome",
    "StaticAgentAdapter",
    "PromptAgentAdapter",
    "MemoryAgentAdapter",
    "ReflectionAgentAdapter",
    "VerifierAgentWrapper",
    "UNIFIED_BASE_PROMPT",
    "FEATURE_FLAGS",
    "get_base_prompt_for_group",
]

