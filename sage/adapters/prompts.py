"""Standardized base prompt and architectural feature flags for SAGE agent archetypes (FIX-4.2).

Ensures all layers (G1-G7) start from an identical prompt length and semantic baseline,
eliminating prompt-length confounding in ablation studies.
"""

from __future__ import annotations
from typing import Any, Dict

# 281 characters — identical semantic baseline for all layers
UNIFIED_BASE_PROMPT = (
    "You are a software engineering assistant. "
    "Analyze the task, read the existing code, identify issues, "
    "and write a correct, secure solution. "
    "Follow the test specifications exactly. "
    "Do not use dangerous imports (os, subprocess, eval, exec). "
    "Do not modify test files or scoring infrastructure."
)

FEATURE_FLAGS: Dict[str, Dict[str, bool]] = {
    "G1": {"evolution": False, "memory": False, "reflection": False, "code_patch": False},
    "G2": {"evolution": True,  "memory": False, "reflection": False, "code_patch": False},
    "G3": {"evolution": False, "memory": True,  "reflection": False, "code_patch": False},
    "G4": {"evolution": True,  "memory": True,  "reflection": True,  "code_patch": True},
    "G5": {"evolution": True,  "memory": True,  "reflection": True,  "code_patch": True},
    "G6": {"evolution": True,  "memory": True,  "reflection": True,  "code_patch": True},
    "G7": {"evolution": True,  "memory": True,  "reflection": True,  "code_patch": True},
}


def get_base_prompt_for_group(group: str, use_unified: bool = False) -> str:
    """Return the system prompt for a group, optionally enforcing the normalized unified prompt."""
    if use_unified:
        return UNIFIED_BASE_PROMPT

    from sage.adapters.static_agent import DEFAULT_G1_PROMPT
    from sage.adapters.prompt_agent import DEFAULT_G2_PROMPT
    from sage.adapters.memory_agent import DEFAULT_G3_PROMPT
    from sage.adapters.reflection_agent import DEFAULT_G4_PROMPT

    legacy_prompts = {
        "G1": DEFAULT_G1_PROMPT,
        "G2": DEFAULT_G2_PROMPT,
        "G3": DEFAULT_G3_PROMPT,
        "G4": DEFAULT_G4_PROMPT,
        "G5": DEFAULT_G4_PROMPT,
        "G6": DEFAULT_G4_PROMPT,
        "G7": DEFAULT_G4_PROMPT,
    }
    return legacy_prompts.get(group, UNIFIED_BASE_PROMPT)

