"""Unit tests for StatisticalEngine (crypto/validation/statistics.py)."""

import pytest
from crypto.validation.statistics import StatisticalEngine


class TestStatisticalEngineValidation:
    """Tests for StatisticalEngine advanced statistical metrics."""

    def test_correlation_metrics(self):
        """Verify Pearson, Spearman, Kendall Tau, and Autocorrelation calculations."""
        engine = StatisticalEngine()
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]

        r = engine.pearson_correlation(x, y)
        assert abs(r - 1.0) < 1e-5

        rho = engine.spearman_correlation(x, y)
        assert abs(rho - 1.0) < 1e-5

        tau = engine.kendall_tau(x, y)
        assert abs(tau - 1.0) < 1e-5

        autocorr = engine.autocorrelation(x, lag=1)
        assert 0.8 <= autocorr <= 1.0

    def test_entropy_and_chi_square(self):
        """Verify Shannon entropy, Min-entropy, and Chi-square calculations."""
        engine = StatisticalEngine()
        # 256 distinct byte values -> uniform distribution, ideal entropy 8.0
        data = bytes(range(256))

        h_shannon = engine.shannon_entropy(data)
        assert h_shannon == 8.0

        h_min = engine.min_entropy(data)
        assert h_min == 8.0

        chi2 = engine.chi_square_statistic(data)
        assert chi2["chi_square"] == 0.0

    def test_hamming_distance_and_propagation(self):
        """Verify Hamming distance and propagation ratio."""
        engine = StatisticalEngine()
        b1 = b"\x00" * 32
        b2 = b"\x01" + (b"\x00" * 31)

        hd = engine.hamming_distance(b1, b2)
        assert hd == 1

        ratio = engine.propagation_ratio(b1, b2)
        assert ratio == round(1.0 / 256.0, 6)
