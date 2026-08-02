"""
Unit tests for Entropy Analysis Module (crypto/analysis/entropy.py).
"""

import pytest
from crypto.analysis import (
    InvalidSequenceError,
    bit_frequency,
    calculate_entropy,
    probability_distribution,
    shannon_entropy,
    validate_sequence,
)


class TestEntropyAnalysis:
    """Test suite for functions in crypto/analysis/entropy.py."""

    def test_sequence_input_formats(self):
        """Verify inputs accept list[int], tuple[int], and binary string."""
        assert validate_sequence([0, 1, 0, 1]) == [0, 1, 0, 1]
        assert validate_sequence((1, 0, 1, 0)) == [1, 0, 1, 0]
        assert validate_sequence("0101") == [0, 1, 0, 1]

    def test_sequence_invalid_inputs(self):
        """Verify invalid sequence inputs raise appropriate errors."""
        with pytest.raises(TypeError, match="Sequence cannot be None"):
            validate_sequence(None)

        with pytest.raises(TypeError, match="Sequence must be list, tuple, or string"):
            validate_sequence(12345)  # type: ignore

        with pytest.raises(InvalidSequenceError, match="Sequence string cannot be empty"):
            validate_sequence("")

        with pytest.raises(InvalidSequenceError, match="Invalid binary character"):
            validate_sequence("01021")

        with pytest.raises(InvalidSequenceError, match="Sequence element must be 0 or 1"):
            validate_sequence([0, 1, 2])

        with pytest.raises(TypeError, match="Sequence element must be int"):
            validate_sequence([0, True, 1])  # type: ignore

    def test_all_zeros_entropy(self):
        """Verify all-zeros sequence has Shannon Entropy H(X) = 0.0."""
        bits = [0] * 100
        assert calculate_entropy(bits) == 0.0
        assert shannon_entropy(bits) == 0.0

    def test_all_ones_entropy(self):
        """Verify all-ones sequence has Shannon Entropy H(X) = 0.0."""
        bits = [1] * 100
        assert calculate_entropy(bits) == 0.0

    def test_balanced_sequence_entropy(self):
        """Verify balanced 50/50 sequence has maximal Shannon Entropy H(X) = 1.0."""
        bits = [0, 1] * 50
        assert calculate_entropy(bits) == 1.0

    def test_bit_frequency(self):
        """Verify bit frequency counts and ratios."""
        bits = [0, 0, 0, 1]
        freq = bit_frequency(bits)
        assert freq["zeros"] == 3
        assert freq["ones"] == 1
        assert freq["zero_ratio"] == 0.75
        assert freq["one_ratio"] == 0.25

    def test_probability_distribution(self):
        """Verify probability distribution output."""
        bits = [1, 1, 1, 0]
        dist = probability_distribution(bits)
        assert dist[0] == 0.25
        assert dist[1] == 0.75
