"""Unit tests for EntropyAnalyzer (crypto/analysis/entropy.py)."""

import pytest
from crypto.analysis.entropy import EntropyAnalyzer


class TestEntropyAnalyzer:
    """Tests for EntropyAnalyzer Shannon entropy, min-entropy, and histograms."""

    def test_shannon_entropy_random(self):
        """Verify pseudo-random byte stream yields high entropy (~7.9+)."""
        analyzer = EntropyAnalyzer()
        # 1000 pseudo-random bytes
        data = bytes((i * 13 + 37) % 256 for i in range(1000))

        shannon = analyzer.calculate_shannon_entropy(data)
        min_ent = analyzer.calculate_min_entropy(data)
        norm_ent = analyzer.calculate_normalized_entropy(data)

        assert 7.8 <= shannon <= 8.0
        assert min_ent > 5.0
        assert 0.95 <= norm_ent <= 1.0

    def test_shannon_entropy_constant(self):
        """Verify constant byte sequence yields 0 entropy."""
        analyzer = EntropyAnalyzer()
        data = b"\xAA" * 100

        assert analyzer.calculate_shannon_entropy(data) == 0.0
        assert analyzer.calculate_min_entropy(data) == 0.0

    def test_histogram_and_analysis(self):
        """Verify histogram generation and full analysis dictionary."""
        analyzer = EntropyAnalyzer()
        data = b"Hello World! Cryptographic AEAD Analysis"

        res = analyzer.analyze(data)
        assert res["total_bytes"] == len(data)
        assert len(res["histogram"]) == 256
        assert sum(res["histogram"]) == len(data)
