"""
sage_live.core.staleness_index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Computes a multi-dimensional staleness score for the SAGE-Live benchmark pool
and recommends retirement or refresh actions.

Scoring model
-------------
The composite staleness score is a weighted sum of four sub-scores, each
normalised to ``[0.0, 1.0]`` where **1.0 = completely stale**:

1. **Age score** — linear ramp from 0 at 0 days to 1 at ``threshold_days``.
2. **Leakage score** — provided externally; passthrough.
3. **Coverage score** — fraction of vulnerability classes with fewer than
   ``min_coverage`` probes.
4. **Variance score** — 1 minus the normalised discrimination score.

The recommended action is derived from thresholds applied to the composite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence

from loguru import logger
from pydantic import BaseModel, Field

from sage_live.database.models import ProbeTask, RecommendedAction, StalenessRecord


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class StalenessConfig(BaseModel):
    """Configuration for the staleness index computation.

    Attributes
    ----------
    threshold_days:
        Age (in days) at which a probe is considered fully stale (age_score = 1).
    weight_age:
        Weight applied to the age sub-score.
    weight_leakage:
        Weight applied to the leakage sub-score.
    weight_coverage:
        Weight applied to the coverage sub-score.
    weight_variance:
        Weight applied to the variance sub-score.
    min_coverage:
        Minimum number of active probes per vulnerability class before coverage
        score begins to penalise.
    retire_threshold:
        Composite score above which ``retire`` is recommended.
    critical_threshold:
        Composite score above which ``critical`` is recommended.
    warning_threshold:
        Composite score above which ``warning`` is recommended.
    """

    threshold_days: float = Field(default=30.0, gt=0)
    weight_age: float = Field(default=0.4, ge=0.0, le=1.0)
    weight_leakage: float = Field(default=0.3, ge=0.0, le=1.0)
    weight_coverage: float = Field(default=0.2, ge=0.0, le=1.0)
    weight_variance: float = Field(default=0.1, ge=0.0, le=1.0)
    min_coverage: int = Field(default=5, ge=1)
    retire_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    critical_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    warning_threshold: float = Field(default=0.40, ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Result dataclass (lightweight — not persisted here)
# ---------------------------------------------------------------------------


@dataclass
class StalenessResult:
    """Holds the outcome of one staleness scan.

    Attributes
    ----------
    composite_score:
        Overall staleness (0 = fresh, 1 = fully stale).
    age_score:
        Sub-score based on probe age.
    leakage_score:
        Sub-score based on external leakage estimate.
    coverage_score:
        Sub-score based on class coverage gaps.
    variance_score:
        Sub-score based on benchmark discrimination.
    recommended_action:
        System recommendation derived from composite_score.
    retirement_candidates:
        Probe IDs recommended for retirement.
    """

    composite_score: float
    age_score: float
    leakage_score: float
    coverage_score: float
    variance_score: float
    recommended_action: RecommendedAction
    retirement_candidates: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Staleness index
# ---------------------------------------------------------------------------


class StalenessIndex:
    """Computes staleness scores for the active probe pool.

    Parameters
    ----------
    config:
        Runtime configuration; defaults to :class:`StalenessConfig`.

    Example
    -------
    >>> idx = StalenessIndex()
    >>> result = idx.compute(probes=active_probes, leakage_estimate=0.1)
    >>> print(result.recommended_action)
    """

    def __init__(self, config: StalenessConfig | None = None) -> None:
        """Initialise the staleness index with optional config."""
        self.config = config or StalenessConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(
        self,
        probes: Sequence[ProbeTask],
        leakage_estimate: float = 0.0,
        discrimination_score: float = 1.0,
        variance_ratio: float = 1.0,
        benchmark_version: str = "0.1.0",
    ) -> StalenessRecord:
        """Run the staleness scan and return a persisted-ready :class:`StalenessRecord`.

        Parameters
        ----------
        probes:
            All currently active probe tasks.
        leakage_estimate:
            Probability (0–1) that probe answers have leaked into training data.
        discrimination_score:
            How well the benchmark discriminates agents (0–1, higher = better).
        variance_ratio:
            Ratio of inter-agent to intra-agent score variance.
        benchmark_version:
            Semantic version of the benchmark being assessed.

        Returns
        -------
        StalenessRecord
            Fully populated staleness record ready for DB insertion.
        """
        logger.info(
            "Running staleness scan (probes={}, leakage={:.3f})",
            len(probes),
            leakage_estimate,
        )

        age_score = self._compute_age_score(probes)
        coverage_score = self._compute_coverage_score(probes)
        variance_score = self._compute_variance_score(discrimination_score)
        leakage_score = max(0.0, min(1.0, leakage_estimate))

        cfg = self.config
        composite = (
            cfg.weight_age * age_score
            + cfg.weight_leakage * leakage_score
            + cfg.weight_coverage * coverage_score
            + cfg.weight_variance * variance_score
        )
        composite = round(composite, 4)

        action = self._derive_action(composite, leakage_score)
        candidates = self._find_retirement_candidates(probes)

        logger.info(
            "Staleness scan complete: composite={:.4f}, action={}",
            composite,
            action.value,
        )

        return StalenessRecord(
            benchmark_version=benchmark_version,
            discrimination_score=round(discrimination_score, 4),
            variance_ratio=round(variance_ratio, 4),
            contamination_detected=leakage_score >= 0.5,  # noqa: PLR2004
            leakage_score=round(leakage_score, 4),
            recommended_action=action,
            probe_retirement_candidates=candidates,
        )

    # ------------------------------------------------------------------
    # Sub-score helpers
    # ------------------------------------------------------------------

    def _compute_age_score(self, probes: Sequence[ProbeTask]) -> float:
        """Compute mean normalised age score across all probes.

        Parameters
        ----------
        probes:
            Active probe tasks.

        Returns
        -------
        float
            Age score in ``[0.0, 1.0]``.
        """
        if not probes:
            return 0.0
        now = datetime.now(tz=timezone.utc)
        scores: list[float] = []
        for probe in probes:
            created = probe.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age_days = (now - created).total_seconds() / 86_400
            scores.append(min(1.0, age_days / self.config.threshold_days))
        return round(sum(scores) / len(scores), 4)

    def _compute_coverage_score(self, probes: Sequence[ProbeTask]) -> float:
        """Measure how many vulnerability classes are under-represented.

        Parameters
        ----------
        probes:
            Active probe tasks.

        Returns
        -------
        float
            Coverage score in ``[0.0, 1.0]`` (1 = no coverage at all).
        """
        from sage_live.database.models import VulnerabilityClass

        class_counts: dict[str, int] = {c.value: 0 for c in VulnerabilityClass}
        for probe in probes:
            class_counts[probe.vulnerability_class.value] += 1

        under = sum(
            1 for cnt in class_counts.values() if cnt < self.config.min_coverage
        )
        total_classes = len(class_counts) or 1
        return round(under / total_classes, 4)

    def _compute_variance_score(self, discrimination_score: float) -> float:
        """Convert discrimination score to a staleness sub-score.

        Parameters
        ----------
        discrimination_score:
            How well the benchmark discriminates (higher = better).

        Returns
        -------
        float
            Variance score in ``[0.0, 1.0]`` (1 = no discrimination = stale).
        """
        return round(1.0 - max(0.0, min(1.0, discrimination_score)), 4)

    def _derive_action(
        self, composite: float, leakage_score: float
    ) -> RecommendedAction:
        """Map the composite staleness score to a recommended action.

        Parameters
        ----------
        composite:
            Composite staleness score in ``[0.0, 1.0]``.
        leakage_score:
            Raw leakage probability in ``[0.0, 1.0]``.

        Returns
        -------
        RecommendedAction
            The recommended action enum value.
        """
        cfg = self.config
        if composite >= cfg.critical_threshold or leakage_score >= 0.9:  # noqa: PLR2004
            return RecommendedAction.CRITICAL
        if composite >= cfg.retire_threshold or leakage_score >= 0.7:  # noqa: PLR2004
            return RecommendedAction.RETIRE
        if composite >= cfg.warning_threshold:
            return RecommendedAction.WARNING
        return RecommendedAction.HEALTHY

    def _find_retirement_candidates(self, probes: Sequence[ProbeTask]) -> list[str]:
        """Identify probes that are individually stale enough to retire.

        A probe is a retirement candidate if its individual age score is 1.0
        (fully stale) **or** it has already been retired.

        Parameters
        ----------
        probes:
            Active probe tasks.

        Returns
        -------
        list[str]
            List of ``probe_id`` strings.
        """
        now = datetime.now(tz=timezone.utc)
        threshold = self.config.threshold_days
        candidates: list[str] = []
        for probe in probes:
            created = probe.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age_days = (now - created).total_seconds() / 86_400
            if age_days >= threshold or not probe.is_active:
                candidates.append(probe.probe_id)
        return candidates


__all__: list[str] = [
    "StalenessConfig",
    "StalenessResult",
    "StalenessIndex",
]
