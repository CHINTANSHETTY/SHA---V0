"""
Unit tests for Entropy Analysis module (crypto/analysis/entropy.py).
"""

import pytest
from crypto.analysis import (
    bit_frequency,
    probability_distribution,
    shannon_entropy,
)


class TestEntropy:
    """Test suite for Shannon Entropy and probability distribution functions."""

    def test_shannon_entropy_all_zeros(self):
        """Verify Shannon entropy of an all-zero sequence is 0.0."""
        assert shannon_entropy([0, 0, 0, 0, 0, 0]) == 0.0

    def test_shannon_entropy_all_ones(self):
        """Verify Shannon entropy of an all-one sequence is 0.0."""
        assert shannon_entropy([1, 1, 1, 1, 1, 1]) == 0.0

    def test_shannon_entropy_balanced_sequence(self):
        """Verify Shannon entropy of an perfectly balanced 50/50 sequence is 1.0."""
        assert shannon_entropy([0, 1, 0, 1, 0, 1, 0, 1]) == 1.0
        assert shannon_entropy("01010101") == 1.0

    def test_shannon_entropy_unbalanced_sequence(self):
        """Verify Shannon entropy of an unbalanced sequence lies between 0.0 and 1.0."""
        # 3 zeros, 1 one -> p(0)=0.75, p(1)=0.25 -> H(X) ~ 0.811278...
        h = shannon_entropy([0, 0, 0, 1])
        assert 0.0 < h < 1.0
        assert round(h, 4) == 0.8113

    def test_bit_frequency(self):
        """Verify bit frequency counts and ratio calculations."""
        bits = [0, 1, 0, 1, 1, 0, 0, 0]  # 5 zeros, 3 ones
        freq = bit_frequency(bits)

        assert freq["zeros"] == 5
        assert freq["ones"] == 3
        assert freq["zero_ratio"] == 0.625
        assert freq["one_ratio"] == 0.375

    def test_probability_distribution(self):
        """Verify probability distribution dict."""
        bits = [0, 1, 0, 1]
        dist = probability_distribution(bits)

        assert dist[0] == 0.5
        assert dist[1] == 0.5

    def test_entropy_invalid_inputs(self):
        """Verify appropriate exceptions for invalid entropy inputs."""
        with pytest.raises(ValueError, match="State sequence cannot be empty"):
            shannon_entropy([])

        with pytest.raises(ValueError, match="State binary string contains invalid character"):
            shannon_entropy("0120")

        with pytest.raises(TypeError, match="State cannot be None"):
            shannon_entropy(None)  # type: ignore

        with pytest.raises(TypeError, match="State must be a list, tuple, or string"):
            shannon_entropy(12345)  # type: ignore
