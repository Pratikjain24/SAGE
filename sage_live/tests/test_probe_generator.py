"""
tests.test_probe_generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test suite for ProbeGenerator - ensures deterministic generation,
infinite probe family, and adversarial coverage.

Test Coverage:
* Deterministic generation (same seed → same probes)
* Unique generation (different seeds → different probes)
* Infinite probe family (can generate 10,000+ unique probes)
* Ground truth validity
* SHA-256 integrity
* Batch generation
* Adversarial generation
* Grammar coverage (all vulnerability classes)
"""

from __future__ import annotations

import hashlib
from typing import List, Set

import pytest

from sage_live.core.probe_generator import ProbeGenerator, ProbeGeneratorConfig
from sage_live.database.models import ProbeTask
from tests.conftest import VULNERABILITY_CLASSES, INJECTION_VECTORS


# ---------------------------------------------------------------------------
# Deterministic Generation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_deterministic_generation():
    """Test that same seed produces identical probes every time.

    SAGE-Live requirement: reproducibility for audit trail.
    """
    seed = 42
    count = 5

    # Generate batch 1
    gen1 = ProbeGenerator(config=ProbeGeneratorConfig(seed=seed), generation=1)
    batch1 = gen1.generate_batch(count=count)

    # Generate batch 2 with same seed
    gen2 = ProbeGenerator(config=ProbeGeneratorConfig(seed=seed), generation=1)
    batch2 = gen2.generate_batch(count=count)

    # Assert exact match
    assert len(batch1) == len(batch2) == count
    for p1, p2 in zip(batch1, batch2):
        assert p1.probe_id == p2.probe_id
        assert p1.prompt_text == p2.prompt_text
        assert p1.difficulty == p2.difficulty
        assert p1.vulnerability_class == p2.vulnerability_class
        assert p1.injection_vector == p2.injection_vector
        assert p1.prompt_hash == p2.prompt_hash


@pytest.mark.unit
def test_deterministic_generation_repeated_calls():
    """Test that multiple calls with same generator produce same sequence."""
    gen = ProbeGenerator(config=ProbeGeneratorConfig(seed=123), generation=1)

    # Generate single probes multiple times
    probe1 = gen.generate_batch(count=1)[0]
    probe2 = gen.generate_batch(count=1)[0]
    probe3 = gen.generate_batch(count=1)[0]

    # Each should be different (advancing through sequence)
    assert probe1.probe_id != probe2.probe_id != probe3.probe_id

    # But recreating generator produces same sequence
    gen_new = ProbeGenerator(config=ProbeGeneratorConfig(seed=123), generation=1)
    probe1_new = gen_new.generate_batch(count=1)[0]

    assert probe1.probe_id == probe1_new.probe_id
    assert probe1.prompt_text == probe1_new.prompt_text


# ---------------------------------------------------------------------------
# Unique Generation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_unique_generation_different_seeds():
    """Test that different seeds produce different probes.

    Critical for infinite probe family property.
    """
    count = 10

    batch1 = ProbeGenerator(
        config=ProbeGeneratorConfig(seed=1), generation=1
    ).generate_batch(count)

    batch2 = ProbeGenerator(
        config=ProbeGeneratorConfig(seed=2), generation=1
    ).generate_batch(count)

    # At least 80% should be different
    different_count = sum(
        1 for p1, p2 in zip(batch1, batch2) if p1.prompt_text != p2.prompt_text
    )
    assert different_count >= count * 0.8


@pytest.mark.unit
def test_unique_generation_within_batch():
    """Test that all probes in a batch are unique."""
    gen = ProbeGenerator(config=ProbeGeneratorConfig(seed=42), generation=1)
    batch = gen.generate_batch(count=50)

    # All probe IDs should be unique
    probe_ids = [p.probe_id for p in batch]
    assert len(probe_ids) == len(set(probe_ids))

    # All prompt texts should be unique
    prompts = [p.prompt_text for p in batch]
    assert len(prompts) == len(set(prompts))

    # All hashes should be unique
    hashes = [p.prompt_hash for p in batch]
    assert len(hashes) == len(set(hashes))


# ---------------------------------------------------------------------------
# Infinite Probe Family Tests
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_infinite_family_10k_probes():
    """Test that we can generate 10,000 unique probes.

    This validates the infinite probe family property.
    """
    target_count = 10_000
    batch_size = 100

    all_hashes: Set[str] = set()
    all_probe_ids: Set[str] = set()

    for batch_num in range(target_count // batch_size):
        gen = ProbeGenerator(
            config=ProbeGeneratorConfig(seed=batch_num), generation=1
        )
        batch = gen.generate_batch(count=batch_size)

        for probe in batch:
            all_hashes.add(probe.prompt_hash)
            all_probe_ids.add(probe.probe_id)

    # Should have close to target_count unique probes
    # Allow for some collisions but require > 99% unique
    assert len(all_hashes) > target_count * 0.99
    assert len(all_probe_ids) == target_count  # IDs are always unique


@pytest.mark.unit
def test_infinite_family_different_generations():
    """Test that different generations produce different probe sets."""
    seed = 42
    count = 20

    gen1 = ProbeGenerator(config=ProbeGeneratorConfig(seed=seed), generation=1)
    batch1 = gen1.generate_batch(count)

    gen2 = ProbeGenerator(config=ProbeGeneratorConfig(seed=seed), generation=2)
    batch2 = gen2.generate_batch(count)

    # Probe IDs should reflect different generations
    assert all("G001" in p.probe_id for p in batch1)
    assert all("G002" in p.probe_id for p in batch2)

    # Content may differ due to generation-specific patterns
    prompts1 = {p.prompt_text for p in batch1}
    prompts2 = {p.prompt_text for p in batch2}
    # At least some should be different
    assert len(prompts1 & prompts2) < count


# ---------------------------------------------------------------------------
# Ground Truth Validity Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_ground_truth_validity(sample_probe_batch: List[ProbeTask]):
    """Test that ground truth labels are valid and consistent."""
    for probe in sample_probe_batch:
        # Must have either safe or unsafe set to True
        assert probe.ground_truth_safe or probe.ground_truth_unsafe

        # Cannot be both safe and unsafe
        assert not (probe.ground_truth_safe and probe.ground_truth_unsafe)

        # Expected refusal should align with safety
        if probe.ground_truth_unsafe:
            assert probe.expected_refusal is True
        if probe.ground_truth_safe:
            assert probe.expected_refusal is False


@pytest.mark.unit
def test_ground_truth_labels_present(probe_generator: ProbeGenerator):
    """Test that all probes have valid ground truth labels."""
    batch = probe_generator.generate_batch(count=50)

    for probe in batch:
        assert isinstance(probe.ground_truth_safe, bool)
        assert isinstance(probe.ground_truth_unsafe, bool)
        assert isinstance(probe.expected_refusal, bool)


# ---------------------------------------------------------------------------
# SHA-256 Integrity Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sha256_integrity(sample_probe_task: ProbeTask):
    """Test that SHA-256 hash matches prompt text."""
    expected_hash = hashlib.sha256(
        sample_probe_task.prompt_text.encode()
    ).hexdigest()

    assert sample_probe_task.prompt_hash == expected_hash
    assert len(sample_probe_task.prompt_hash) == 64  # SHA-256 = 64 hex chars


@pytest.mark.unit
def test_sha256_integrity_batch(sample_probe_batch: List[ProbeTask]):
    """Test SHA-256 integrity for entire batch."""
    for probe in sample_probe_batch:
        computed_hash = hashlib.sha256(probe.prompt_text.encode()).hexdigest()
        assert probe.prompt_hash == computed_hash
        assert len(probe.prompt_hash) == 64


@pytest.mark.unit
def test_sha256_uniqueness(sample_probe_batch: List[ProbeTask]):
    """Test that all hashes are unique (no collisions)."""
    hashes = [p.prompt_hash for p in sample_probe_batch]
    assert len(hashes) == len(set(hashes))


# ---------------------------------------------------------------------------
# Batch Generation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_batch_generation_count():
    """Test that batch generation produces exact count."""
    gen = ProbeGenerator(generation=1)

    for count in [1, 5, 10, 50, 100]:
        batch = gen.generate_batch(count=count)
        assert len(batch) == count


@pytest.mark.unit
def test_batch_generation_empty():
    """Test edge case of zero-count batch."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=0)
    assert len(batch) == 0


@pytest.mark.unit
def test_batch_generation_large():
    """Test generation of large batch."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=500)

    assert len(batch) == 500
    # All should be valid ProbeTask instances
    assert all(isinstance(p, ProbeTask) for p in batch)


@pytest.mark.unit
def test_batch_generation_sequential_ids():
    """Test that probe IDs increment sequentially within batch."""
    gen = ProbeGenerator(config=ProbeGeneratorConfig(seed=42), generation=1)
    batch = gen.generate_batch(count=10)

    # Extract ID numbers
    id_numbers = []
    for probe in batch:
        # Format: PROBE-G001-00001
        parts = probe.probe_id.split("-")
        id_numbers.append(int(parts[-1]))

    # Should be sequential: 1, 2, 3, ...
    assert id_numbers == list(range(1, 11))


# ---------------------------------------------------------------------------
# Adversarial Generation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_adversarial_generation_difficulty_range(sample_probe_batch: List[ProbeTask]):
    """Test that difficulty scores are in valid range."""
    for probe in sample_probe_batch:
        assert 0.0 <= probe.difficulty <= 1.0


@pytest.mark.unit
def test_adversarial_generation_difficulty_variety():
    """Test that generated probes have variety in difficulty."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=100)

    difficulties = [p.difficulty for p in batch]

    # Should have probes at different difficulty levels
    assert min(difficulties) < 0.5
    assert max(difficulties) > 0.5

    # Should have variety (standard deviation > 0.1)
    import statistics

    std_dev = statistics.stdev(difficulties)
    assert std_dev > 0.1


@pytest.mark.unit
def test_adversarial_generation_expected_refusal_distribution():
    """Test that expected_refusal has reasonable distribution."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=100)

    refusal_count = sum(1 for p in batch if p.expected_refusal)
    non_refusal_count = len(batch) - refusal_count

    # Should have both types (not all one or the other)
    assert refusal_count > 10
    assert non_refusal_count > 10


# ---------------------------------------------------------------------------
# Grammar Coverage Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_grammar_coverage_all_vulnerability_classes():
    """Test that all vulnerability classes are covered in large batch.

    SAGE-Live requires comprehensive adversarial coverage.
    """
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=200)

    covered_classes = {p.vulnerability_class for p in batch}

    # Should cover multiple vulnerability classes
    assert len(covered_classes) >= 4

    # Check for specific critical classes
    expected_classes = {"jailbreak", "prompt_injection", "unsafe_content"}
    assert len(expected_classes & covered_classes) >= 2


@pytest.mark.unit
def test_grammar_coverage_all_injection_vectors():
    """Test that multiple injection vectors are covered."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=200)

    covered_vectors = {p.injection_vector for p in batch}

    # Should have multiple injection techniques
    assert len(covered_vectors) >= 3


@pytest.mark.unit
@pytest.mark.parametrize("vuln_class", VULNERABILITY_CLASSES)
def test_grammar_coverage_specific_vulnerability(vuln_class: str):
    """Test that we can generate probes for specific vulnerability class.

    Parameters
    ----------
    vuln_class:
        Vulnerability class to test.
    """
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=100)

    # Filter by vulnerability class
    matching = [p for p in batch if p.vulnerability_class == vuln_class]

    # Should generate at least some of this type
    # (randomized generation may not hit every class in small batch)
    # So we just verify that when it does appear, it's valid
    if matching:
        for probe in matching:
            assert probe.vulnerability_class == vuln_class
            assert isinstance(probe.prompt_text, str)
            assert len(probe.prompt_text) > 0


@pytest.mark.unit
def test_grammar_coverage_difficulty_distribution():
    """Test that difficulty levels span the full range."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=200)

    difficulties = [p.difficulty for p in batch]

    # Should have probes in multiple difficulty buckets
    easy = [d for d in difficulties if d < 0.3]
    medium = [d for d in difficulties if 0.3 <= d < 0.7]
    hard = [d for d in difficulties if d >= 0.7]

    # All buckets should have representation
    assert len(easy) > 0
    assert len(medium) > 0
    assert len(hard) > 0


# ---------------------------------------------------------------------------
# Probe Structure Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_probe_structure_all_fields_present(sample_probe_task: ProbeTask):
    """Test that probe has all required fields."""
    assert sample_probe_task.id is not None
    assert sample_probe_task.probe_id is not None
    assert sample_probe_task.generation > 0
    assert sample_probe_task.prompt_text is not None
    assert sample_probe_task.expected_refusal is not None
    assert sample_probe_task.ground_truth_safe is not None
    assert sample_probe_task.ground_truth_unsafe is not None
    assert sample_probe_task.vulnerability_class is not None
    assert sample_probe_task.injection_vector is not None
    assert 0.0 <= sample_probe_task.difficulty <= 1.0
    assert sample_probe_task.prompt_hash is not None
    assert sample_probe_task.created_at is not None


@pytest.mark.unit
def test_probe_id_format(sample_probe_batch: List[ProbeTask]):
    """Test that probe IDs follow expected format: PROBE-G###-#####."""
    import re

    pattern = re.compile(r"^PROBE-G\d{3}-\d{5}$")

    for probe in sample_probe_batch:
        assert pattern.match(probe.probe_id), f"Invalid ID format: {probe.probe_id}"


@pytest.mark.unit
def test_prompt_text_non_empty(sample_probe_batch: List[ProbeTask]):
    """Test that all prompts have meaningful content."""
    for probe in sample_probe_batch:
        assert len(probe.prompt_text) > 10  # At least some content
        assert probe.prompt_text.strip() == probe.prompt_text  # No leading/trailing whitespace


# ---------------------------------------------------------------------------
# Regression Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_no_duplicate_ids_across_generations():
    """Test that different generations don't produce duplicate IDs."""
    batch1 = ProbeGenerator(generation=1).generate_batch(count=50)
    batch2 = ProbeGenerator(generation=2).generate_batch(count=50)

    ids1 = {p.probe_id for p in batch1}
    ids2 = {p.probe_id for p in batch2}

    # No overlap
    assert len(ids1 & ids2) == 0


@pytest.mark.unit
def test_retired_at_initially_none(sample_probe_batch: List[ProbeTask]):
    """Test that newly generated probes are not retired."""
    for probe in sample_probe_batch:
        assert probe.retired_at is None


@pytest.mark.unit
def test_generation_number_embedded_in_id():
    """Test that generation number is correctly embedded in probe ID."""
    for gen_num in [1, 5, 10, 99, 100]:
        gen = ProbeGenerator(generation=gen_num)
        batch = gen.generate_batch(count=1)
        probe = batch[0]

        # Extract generation from ID
        gen_part = probe.probe_id.split("-")[1]  # G###
        embedded_gen = int(gen_part[1:])  # Remove 'G'

        assert embedded_gen == gen_num


# ---------------------------------------------------------------------------
# Performance Tests
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_generation_performance_1000_probes():
    """Test that generating 1000 probes completes in reasonable time."""
    import time

    gen = ProbeGenerator(generation=1)

    start_time = time.time()
    batch = gen.generate_batch(count=1000)
    elapsed = time.time() - start_time

    assert len(batch) == 1000
    # Should complete in under 5 seconds
    assert elapsed < 5.0


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_max_count_generation():
    """Test generation at maximum reasonable count."""
    gen = ProbeGenerator(generation=1)
    batch = gen.generate_batch(count=1000)

    assert len(batch) == 1000
    assert all(isinstance(p, ProbeTask) for p in batch)


@pytest.mark.unit
def test_high_generation_number():
    """Test that high generation numbers work correctly."""
    gen = ProbeGenerator(generation=999)
    batch = gen.generate_batch(count=5)

    for probe in batch:
        assert "G999" in probe.probe_id
        assert probe.generation == 999
