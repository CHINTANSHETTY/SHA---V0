"""Unit tests for SACAnalyzer (crypto/analysis/avalanche.py)."""

import pytest
from crypto.analysis.avalanche import SACAnalyzer


class TestSACAnalyzer:
    """Tests for SACAnalyzer matrix shape, probability calculations, and export."""

    def test_sac_analysis(self):
        """Verify SAC matrix generation and mean probability near 0.5."""
        sac = SACAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Sample Payload Bytes"  # 20 bytes = 160 bits

        res = sac.analyze(master_key, plaintext, samples=10)

        assert res["input_bits_evaluated"] == 10
        assert res["output_bits"] > 0
        assert len(res["sac_matrix"]) == 10
        assert len(res["sac_matrix"][0]) == res["output_bits"]
        assert 0.35 <= res["mean_sac_probability"] <= 0.65

    def test_export_matrix(self):
        """Verify export_matrix returns structured matrix output."""
        sac = SACAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Sample Payload Bytes"

        sac.analyze(master_key, plaintext, samples=5)
        exported = sac.export_matrix("matrix")

        assert isinstance(exported, list)
        assert len(exported) == 5
