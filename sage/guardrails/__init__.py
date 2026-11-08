"""SAGE Guardrails Subsystem: Sub-10ms Cascading Deterministic + SLM Engine.

Eliminates synchronous external LLM judge overhead (800ms-2s latency) with
in-process zero-copy DFA/AST kernels, vector-centroid embeddings, and quantized SLMs.
"""

from sage.guardrails.canary_selector import (
    MetamorphicCanarySelector,
    PropertyBasedCanaryFuzzer,
    make_canary_sort_invariant,
)
from sage.guardrails.fast_guard import (
    GuardrailVerdict,
    Sub10msGuardrailEngine,
    Tier1DeterministicKernel,
    Tier2VectorCentroidGuard,
    Tier3QuantizedSLMGuard,
    Tier4eBPFWASMSpecification,
)

__all__ = [
    "GuardrailVerdict",
    "MetamorphicCanarySelector",
    "PropertyBasedCanaryFuzzer",
    "make_canary_sort_invariant",
    "Sub10msGuardrailEngine",
    "Tier1DeterministicKernel",
    "Tier2VectorCentroidGuard",
    "Tier3QuantizedSLMGuard",
    "Tier4eBPFWASMSpecification",
]

