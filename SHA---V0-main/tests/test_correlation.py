"""
Unit tests for Correlation Analysis Module (crypto/analysis/correlation.py).
"""

import pytest
from crypto.analysis import (
    ComparisonError,
    autocorrelation,
    correlation,
    pearson_correlation,
)


class TestCorrelationAnalysis:
    """Test suite for Pearson correlation and autocorrelation functions."""

    def test_identical_sequences_correlation(self):
        """Verify identical sequences have Pearson correlation r = 1.0."""
        bits = [1, 0, 1, 1, 0, 1, 0, 0]
        assert correlation(bits, bits) == 1.0
        assert pearson_correlation(bits, bits) == 1.0

    def test_inverse_sequences_correlation(self):
        """Verify inverted sequences have Pearson correlation r = -1.0."""
        b1 = [1, 0, 1, 1, 0]
        b2 = [0, 1, 0, 0, 1]
        assert correlation(b1, b2) == -1.0

    def test_uncorrelated_sequences(self):
        """Verify orthogonal / uncorrelated sequences have r ≈ 0.0."""
        b1 = [1, 1, 0, 0]
        b2 = [1, 0, 1, 0]
        assert correlation(b1, b2) == 0.0

    def test_constant_sequence_zero_variance(self):
        """Verify constant sequences with zero variance return 0.0 correlation safely."""
        b1 = [1, 1, 1, 1]
        b2 = [1, 0, 1, 0]
        assert correlation(b1, b2) == 0.0

    def test_unequal_length_sequences_raise_error(self):
        """Verify unequal sequence lengths raise ComparisonError."""
        with pytest.raises(ComparisonError, match="lengths must be equal"):
            correlation([1, 0, 1], [1, 0])

    def test_autocorrelation(self):
        """Verify autocorrelation calculation at lag 1."""
        bits = [1, 0, 1, 0, 1, 0]
        assert autocorrelation(bits, lag=1) == -1.0
        assert autocorrelation(bits, lag=2) == 1.0

    def test_autocorrelation_invalid_lag(self):
        """Verify invalid lag parameter raises appropriate exceptions."""
        with pytest.raises(ValueError, match="Lag must be in range"):
            autocorrelation([1, 0, 1, 0], lag=0)

        with pytest.raises(ValueError, match="Lag must be in range"):
            autocorrelation([1, 0, 1, 0], lag=4)

        with pytest.raises(TypeError, match="Lag must be an integer"):
            autocorrelation([1, 0, 1, 0], lag=1.5)  # type: ignore
