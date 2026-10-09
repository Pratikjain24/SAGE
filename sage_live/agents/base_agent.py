"""
sage_live.agents.base_agent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Abstract base class for all agents that participate in SAGE-Live evaluations.

All concrete agents (evaluators, red-team attackers, blue-team defenders) must
inherit from :class:`BaseAgent` and implement :meth:`run`.

The base class provides:
* Structured logging via loguru
* Automatic retry logic (via tenacity)
* Token-budget enforcement
* Standard response schema via :class:`AgentResponse`
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field
from tenacity import (
    RetryError,
    retry,
    stop_after_attempt,
    wait_exponential,
)


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class AgentResponse(BaseModel):
    """Structured response returned by every agent.

    Attributes
    ----------
    agent_id:
        Unique identifier of the agent that produced this response.
    run_id:
        UUID for this specific invocation — useful for log correlation.
    content:
        The agent's text output.
    tokens_used:
        Number of tokens consumed by the LLM call (if known).
    latency_seconds:
        Wall-clock time elapsed during :meth:`BaseAgent.run`.
    metadata:
        Arbitrary extra data the concrete agent may attach.
    """

    agent_id: str
    run_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    tokens_used: int = Field(default=0, ge=0)
    latency_seconds: float = Field(default=0.0, ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class BaseAgent(ABC):
    """Abstract base class for SAGE-Live agents.

    Subclasses must implement :meth:`run`.  The base class handles retry
    logic, timing, and structured logging automatically.

    Parameters
    ----------
    agent_id:
        Unique string identifier for this agent instance.
    model_name:
        Name of the underlying LLM (e.g. ``"gpt-4o"``).
    max_tokens:
        Maximum number of tokens allowed per LLM call.
    max_retries:
        Number of times to retry on transient failures.
    """

    def __init__(
        self,
        agent_id: str,
        model_name: str,
        max_tokens: int = 2048,
        max_retries: int = 3,
    ) -> None:
        """Initialise the base agent with identity and retry configuration."""
        self.agent_id = agent_id
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self._logger = logger.bind(agent_id=agent_id, model=model_name)
        self._logger.info("Agent initialised")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """Execute the agent with retry logic and timing.

        This is the public entry point.  It wraps :meth:`_run_with_retry`
        with structured logging and elapsed-time measurement.

        Parameters
        ----------
        prompt:
            The input prompt to pass to the agent.
        **kwargs:
            Additional keyword arguments forwarded to :meth:`run`.

        Returns
        -------
        AgentResponse
            Structured response from the agent.

        Raises
        ------
        RuntimeError
            If all retry attempts are exhausted.
        """
        self._logger.debug("Executing (prompt_len={})", len(prompt))
        start = time.perf_counter()
        try:
            response = self._run_with_retry(prompt, **kwargs)
        except RetryError as exc:
            raise RuntimeError(
                f"Agent {self.agent_id} exhausted all {self.max_retries} retries"
            ) from exc
        elapsed = time.perf_counter() - start
        response.latency_seconds = round(elapsed, 4)
        self._logger.info(
            "Completed in {:.3f}s (tokens={})",
            elapsed,
            response.tokens_used,
        )
        return response

    @abstractmethod
    def run(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """Core agent logic — implement in every concrete subclass.

        Parameters
        ----------
        prompt:
            The input prompt.
        **kwargs:
            Subclass-specific keyword arguments.

        Returns
        -------
        AgentResponse
            The agent's structured response.
        """

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_with_retry(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """Wrap :meth:`run` with exponential backoff retries.

        Parameters
        ----------
        prompt:
            Input prompt.
        **kwargs:
            Forwarded to :meth:`run`.

        Returns
        -------
        AgentResponse
            Response from the first successful :meth:`run` call.
        """

        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )
        def _inner() -> AgentResponse:
            return self.run(prompt, **kwargs)

        return _inner()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"agent_id={self.agent_id!r}, "
            f"model={self.model_name!r})"
        )


__all__: list[str] = [
    "AgentResponse",
    "BaseAgent",
]
