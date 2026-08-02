"""
Unit tests for Avalanche Effect Module (crypto/analysis/avalanche.py).
"""

import pytest
from crypto.analysis import (
    ComparisonError,
    avalanche_effect,
    calculate_avalanche,
    hamming_distance,
)


class TestAvalancheAnalysis:
    """Test suite for avalanche effect and Hamming distance calculations."""

    def test_identical_sequences(self):
        """Verify identical sequences have Hamming distance 0 and avalanche percentage 0%."""
        b1 = [1, 0, 1, 1, 0, 0, 1, 0]
        b2 = [1, 0, 1, 1, 0, 0, 1, 0]

        assert hamming_distance(b1, b2) == 0
        assert avalanche_effect(b1, b2) == 0.0

        res = calculate_avalanche(b1, b2)
        assert res["distance"] == 0
        assert res["percentage"] == 0.0

    def test_opposite_sequences(self):
        """Verify completely inverted sequences have max Hamming distance and 100% avalanche."""
        b1 = [1, 0, 1, 0]
        b2 = [0, 1, 0, 1]

        assert hamming_distance(b1, b2) == 4
        assert avalanche_effect(b1, b2) == 1.0

        res = calculate_avalanche(b1, b2)
        assert res["distance"] == 4
        assert res["percentage"] == 100.0

    def test_50_percent_difference(self):
        """Verify 50% bit difference results in 0.5 ratio / 50.0 percentage."""
        b1 = [0, 0, 0, 0]
        b2 = [1, 1, 0, 0]

        assert hamming_distance(b1, b2) == 2
        assert avalanche_effect(b1, b2) == 0.5

        res = calculate_avalanche(b1, b2)
        assert res["distance"] == 2
        assert res["percentage"] == 50.0

    def test_unequal_length_sequences_raise_error(self):
        """Verify unequal sequence lengths raise ComparisonError."""
        with pytest.raises(ComparisonError, match="lengths must be equal"):
            hamming_distance([1, 0, 1], [1, 0])

        with pytest.raises(ComparisonError, match="lengths must be equal"):
            calculate_avalanche([1, 0, 1], [1, 0, 1, 0])
