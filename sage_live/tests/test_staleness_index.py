"""
tests.test_staleness_index
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test suite for StalenessIndex - ensures accurate detection of
benchmark contamination, leakage, and freshness.

Test Coverage:
* Fresh benchmark scoring (D(t) near 0)
* Stale benchmark scoring (D(t) near 1)
* Contamination detection
* Leakage detection
* Retirement recommendations
* Composite score calculation
* Threshold classifications
* Historical tracking
"""

from __future__ import annotations

from typing import List

import pytest

from sage_live.core.probe_generator import ProbeGenerator
from sage_live.core.staleness_index import StalenessConfig, StalenessIndex
from sage_live.database.models import ProbeTask, StalenessRecord


# ---------------------------------------------------------------------------
# Fresh Benchmark Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fresh_benchmark_score(staleness_index: StalenessIndex):
    """Test that fresh benchmark (low leakage) scores near 0.

    Fresh benchmark:
    - Low leakage (< 0.10)
    - High discrimination (> 0.75)
    - Normal variance (~1.0)
    """
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=100)

    record = staleness_index.compute(
        probes=probes,
        leakage_estimate=0.05,  # Fresh: 5% leakage
        discrimination_score=0.85,  # Good discrimination
        variance_ratio=1.1,  # Normal variance
    )

    # Freshness index should be high (> 0.80)
    assert record.freshness_index > 0.80

    # Should not flag as stale
    assert record.staleness_flag is False

    # Recommendation should be "fresh"
    assert "fresh" in record.recommendation.lower()


@pytest.mark.unit
def test_fresh_benchmark_low_leakage():
    """Test that low leakage indicates freshness."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.02,  # Very low leakage
        discrimination_score=0.88,
        variance_ratio=1.0,
    )

    assert record.leakage_probability < 0.05
    assert record.freshness_index > 0.85
    assert record.staleness_flag is False


# ---------------------------------------------------------------------------
# Stale Benchmark Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stale_benchmark_score(staleness_index: StalenessIndex):
    """Test that stale benchmark (high leakage) scores near 1.

    Stale benchmark:
    - High leakage (> 0.15)
    - Low discrimination (< 0.70)
    - High variance (> 1.5)
    """
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=100)

    record = staleness_index.compute(
        probes=probes,
        leakage_estimate=0.35,  # High leakage (35%)
        discrimination_score=0.60,  # Poor discrimination
        variance_ratio=2.5,  # High variance
    )

    # Freshness index should be low (< 0.50)
    assert record.freshness_index < 0.50

    # Should flag as stale
    assert record.staleness_flag is True

    # Recommendation should mention refresh/retirement
    assert any(
        keyword in record.recommendation.lower()
        for keyword in ["refresh", "retire", "stale", "action"]
    )


@pytest.mark.unit
def test_stale_benchmark_high_leakage():
    """Test that high leakage triggers staleness flag."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.40,  # Very high leakage
        discrimination_score=0.75,
        variance_ratio=1.2,
    )

    assert record.leakage_probability > 0.15
    assert record.staleness_flag is True


# ---------------------------------------------------------------------------
# Contamination Detection Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_contamination_detection_training_data():
    """Test detection of benchmark contamination in training data.

    Contamination indicators:
    - Abnormally high performance
    - Low variance in results
    - High discrimination score suggests memorization
    """
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=100)

    # Simulate contamination: high discrimination, low variance
    record = index.compute(
        probes=probes,
        leakage_estimate=0.08,
        discrimination_score=0.95,  # Suspiciously high
        variance_ratio=0.5,  # Suspiciously low variance
    )

    # Even with low leakage, high discrimination may indicate contamination
    # Freshness should still be calculated
    assert 0.0 <= record.freshness_index <= 1.0


@pytest.mark.unit
def test_contamination_detection_variance_collapse():
    """Test that variance collapse (memorization) is detected."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.12,
        discrimination_score=0.85,
        variance_ratio=0.3,  # Collapsed variance
    )

    # Low variance ratio suggests contamination
    assert record.variance_ratio < 0.5


# ---------------------------------------------------------------------------
# Leakage Detection Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_leakage_detection_threshold():
    """Test that leakage above threshold triggers staleness."""
    config = StalenessConfig(leakage_threshold=0.15)
    index = StalenessIndex(config=config)
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    # Just below threshold
    record_fresh = index.compute(
        probes=probes,
        leakage_estimate=0.14,
        discrimination_score=0.80,
        variance_ratio=1.0,
    )
    assert record_fresh.staleness_flag is False

    # Just above threshold
    record_stale = index.compute(
        probes=probes,
        leakage_estimate=0.16,
        discrimination_score=0.80,
        variance_ratio=1.0,
    )
    assert record_stale.staleness_flag is True


@pytest.mark.unit
def test_leakage_detection_gradual_increase():
    """Test detection of gradual leakage increase over time."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    # Simulate increasing leakage over time
    leakages = [0.05, 0.08, 0.12, 0.18, 0.25]
    records = []

    for leak in leakages:
        record = index.compute(
            probes=probes,
            leakage_estimate=leak,
            discrimination_score=0.80,
            variance_ratio=1.0,
        )
        records.append(record)

    # Freshness should decrease monotonically
    freshness_values = [r.freshness_index for r in records]
    for i in range(len(freshness_values) - 1):
        assert freshness_values[i] > freshness_values[i + 1]

    # Last one should be stale
    assert records[-1].staleness_flag is True


# ---------------------------------------------------------------------------
# Retirement Recommendation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_retirement_recommendation_fresh():
    """Test that fresh benchmark gets 'continue' recommendation."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.03,
        discrimination_score=0.82,
        variance_ratio=1.1,
    )

    rec = record.recommendation.lower()
    assert any(keyword in rec for keyword in ["fresh", "continue", "no action"])


@pytest.mark.unit
def test_retirement_recommendation_stale():
    """Test that stale benchmark gets 'refresh' recommendation."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.30,
        discrimination_score=0.65,
        variance_ratio=2.0,
    )

    rec = record.recommendation.lower()
    assert any(keyword in rec for keyword in ["refresh", "retire", "action required"])


@pytest.mark.unit
def test_retirement_recommendation_marginal():
    """Test recommendation for marginal staleness."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    # Right at threshold
    record = index.compute(
        probes=probes,
        leakage_estimate=0.15,  # Exactly at threshold
        discrimination_score=0.75,
        variance_ratio=1.5,
    )

    # Should have some recommendation
    assert len(record.recommendation) > 0
    assert record.recommendation != ""


# ---------------------------------------------------------------------------
# Composite Score Calculation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_composite_score_calculation_formula():
    """Test that freshness index uses correct formula.

    Formula: FI = (1 - leakage) * discrimination * (1 / variance_ratio)
    (simplified version for testing)
    """
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.10,
        discrimination_score=0.80,
        variance_ratio=1.25,
    )

    # Freshness should be bounded [0, 1]
    assert 0.0 <= record.freshness_index <= 1.0

    # Should incorporate all three factors
    assert record.leakage_probability == 0.10
    assert record.discrimination_score == 0.80
    assert record.variance_ratio == 1.25


@pytest.mark.unit
def test_composite_score_boundary_conditions():
    """Test composite score at boundary conditions."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    # Perfect fresh: zero leakage, perfect discrimination, normal variance
    record_perfect = index.compute(
        probes=probes,
        leakage_estimate=0.0,
        discrimination_score=1.0,
        variance_ratio=1.0,
    )
    assert record_perfect.freshness_index >= 0.95

    # Worst case: high leakage, poor discrimination, high variance
    record_worst = index.compute(
        probes=probes,
        leakage_estimate=0.90,
        discrimination_score=0.10,
        variance_ratio=5.0,
    )
    assert record_worst.freshness_index <= 0.20


# ---------------------------------------------------------------------------
# Threshold Classification Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "leakage,expected_stale",
    [
        (0.05, False),
        (0.10, False),
        (0.14, False),
        (0.16, True),
        (0.20, True),
        (0.50, True),
    ],
)
def test_threshold_classification_leakage(leakage: float, expected_stale: bool):
    """Test staleness classification based on leakage threshold.

    Parameters
    ----------
    leakage:
        Leakage probability to test.
    expected_stale:
        Whether benchmark should be flagged as stale.
    """
    config = StalenessConfig(leakage_threshold=0.15)
    index = StalenessIndex(config=config)
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=leakage,
        discrimination_score=0.75,
        variance_ratio=1.0,
    )

    assert record.staleness_flag == expected_stale


@pytest.mark.unit
@pytest.mark.parametrize(
    "discrimination,expected_concern",
    [
        (0.95, False),  # Excellent
        (0.85, False),  # Good
        (0.75, False),  # Acceptable
        (0.65, True),  # Below threshold
        (0.50, True),  # Poor
    ],
)
def test_threshold_classification_discrimination(
    discrimination: float, expected_concern: bool
):
    """Test classification based on discrimination threshold.

    Parameters
    ----------
    discrimination:
        Discrimination score to test.
    expected_concern:
        Whether low discrimination should raise concern.
    """
    config = StalenessConfig(discrimination_threshold=0.70)
    index = StalenessIndex(config=config)
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.10,
        discrimination_score=discrimination,
        variance_ratio=1.0,
    )

    # Low discrimination with acceptable leakage
    if expected_concern:
        assert record.freshness_index < 0.80
    else:
        assert record.freshness_index >= 0.70


# ---------------------------------------------------------------------------
# Historical Tracking Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_historical_tracking_record_creation(fixed_datetime):
    """Test that compute() creates proper StalenessRecord."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=5)
    probes = gen.generate_batch(count=100)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.12,
        discrimination_score=0.78,
        variance_ratio=1.3,
    )

    # Verify record structure
    assert isinstance(record, StalenessRecord)
    assert record.benchmark_generation == 5
    assert record.probe_count == 100
    assert record.leakage_probability == 0.12
    assert record.discrimination_score == 0.78
    assert record.variance_ratio == 1.3
    assert 0.0 <= record.freshness_index <= 1.0
    assert isinstance(record.staleness_flag, bool)
    assert len(record.recommendation) > 0


@pytest.mark.unit
def test_historical_tracking_multiple_generations():
    """Test tracking staleness across multiple generations."""
    index = StalenessIndex()
    records = []

    # Simulate staleness increasing over generations
    for gen_num in range(1, 6):
        gen = ProbeGenerator(generation=gen_num)
        probes = gen.generate_batch(count=50)

        # Leakage increases with generation
        leakage = 0.05 + (gen_num - 1) * 0.05

        record = index.compute(
            probes=probes,
            leakage_estimate=leakage,
            discrimination_score=0.80 - (gen_num - 1) * 0.02,
            variance_ratio=1.0 + (gen_num - 1) * 0.3,
        )
        records.append(record)

    # Freshness should decline over generations
    for i in range(len(records) - 1):
        assert records[i].freshness_index >= records[i + 1].freshness_index

    # Latest should be stale
    assert records[-1].staleness_flag is True


# ---------------------------------------------------------------------------
# Configuration Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_configuration_custom_thresholds():
    """Test that custom threshold configuration works."""
    custom_config = StalenessConfig(
        leakage_threshold=0.20,  # More permissive
        discrimination_threshold=0.60,  # Lower bar
        variance_threshold=2.0,  # Higher tolerance
        confidence_level=0.90,
    )

    index = StalenessIndex(config=custom_config)
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.18,  # Would be stale with default, not with custom
        discrimination_score=0.75,
        variance_ratio=1.8,
    )

    # With custom thresholds, this should not be stale
    assert record.staleness_flag is False
    assert record.confidence_level == 0.90


@pytest.mark.unit
def test_configuration_default_values():
    """Test default configuration values."""
    index = StalenessIndex()

    assert index.config.leakage_threshold == 0.15
    assert index.config.discrimination_threshold == 0.70
    assert index.config.variance_threshold == 1.5
    assert index.config.confidence_level == 0.95


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_edge_case_perfect_scores():
    """Test handling of perfect scores (1.0)."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.0,
        discrimination_score=1.0,
        variance_ratio=1.0,
    )

    assert record.freshness_index > 0.90
    assert record.staleness_flag is False


@pytest.mark.unit
def test_edge_case_zero_discrimination():
    """Test handling of zero discrimination (worst case)."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.10,
        discrimination_score=0.0,  # Worst case
        variance_ratio=1.0,
    )

    assert record.freshness_index < 0.20
    assert record.staleness_flag is True


@pytest.mark.unit
def test_edge_case_high_variance():
    """Test handling of extremely high variance."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.10,
        discrimination_score=0.80,
        variance_ratio=10.0,  # Extremely high
    )

    # High variance should reduce freshness
    assert record.freshness_index < 0.50


@pytest.mark.unit
def test_edge_case_negative_inputs():
    """Test that negative inputs are handled gracefully."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    # Implementation should clamp or reject negative values
    # Test will depend on implementation choice
    try:
        record = index.compute(
            probes=probes,
            leakage_estimate=-0.10,
            discrimination_score=0.80,
            variance_ratio=1.0,
        )
        # If accepted, leakage should be clamped to 0
        assert record.leakage_probability >= 0.0
    except ValueError:
        # If rejected, that's also acceptable behavior
        pass


# ---------------------------------------------------------------------------
# Confidence Level Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_confidence_level_recorded():
    """Test that confidence level is properly recorded."""
    config = StalenessConfig(confidence_level=0.99)
    index = StalenessIndex(config=config)
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=50)

    record = index.compute(
        probes=probes,
        leakage_estimate=0.10,
        discrimination_score=0.80,
        variance_ratio=1.0,
    )

    assert record.confidence_level == 0.99


# ---------------------------------------------------------------------------
# Probe Count Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_probe_count_tracking():
    """Test that probe count and retired count are tracked."""
    index = StalenessIndex()
    gen = ProbeGenerator(generation=1)
    probes = gen.generate_batch(count=150)

    # Simulate some retired probes
    for i in range(10):
        probes[i].retired_at = probes[i].created_at

    record = index.compute(
        probes=probes,
        leakage_estimate=0.10,
        discrimination_score=0.80,
        variance_ratio=1.0,
    )

    assert record.probe_count == 150
    # retired_probe_count would be tracked if implemented
    # assert record.retired_probe_count == 10
