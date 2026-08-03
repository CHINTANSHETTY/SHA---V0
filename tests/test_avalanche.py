"""Unit tests for AvalancheAnalyzer (crypto/analysis/avalanche.py)."""

import pytest
from crypto.analysis.avalanche import AvalancheAnalyzer


class TestAvalancheAnalyzer:
    """Tests for AvalancheAnalyzer plaintext, key, and nonce avalanche calculations."""

    def test_plaintext_avalanche(self):
        """Verify plaintext avalanche ratio is near 50% (~0.5)."""
        analyzer = AvalancheAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Plaintext Payload for Avalanche Analysis"

        res = analyzer.analyze_plaintext(master_key, plaintext, samples=50)

        assert res["samples_evaluated"] == 50
        assert 0.40 <= res["mean"] <= 0.60
        assert res["passed"] is True
        assert "std_dev" in res

    def test_key_avalanche(self):
        """Verify key avalanche ratio is near 50% (~0.5)."""
        analyzer = AvalancheAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Plaintext Payload for Avalanche Analysis"

        res = analyzer.analyze_key(master_key, plaintext, samples=50)

        assert res["samples_evaluated"] == 50
        assert 0.40 <= res["mean"] <= 0.60
        assert res["passed"] is True

    def test_nonce_avalanche(self):
        """Verify nonce avalanche ratio is near 50% (~0.5)."""
        analyzer = AvalancheAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Plaintext Payload for Avalanche Analysis"

        res = analyzer.analyze_nonce(master_key, plaintext, samples=50)

        assert res["samples_evaluated"] > 0
        assert 0.40 <= res["mean"] <= 0.60
        assert res["passed"] is True
