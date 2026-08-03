"""Unit tests for BICAnalyzer (crypto/analysis/differential.py)."""

import pytest
from crypto.analysis.differential import BICAnalyzer


class TestBICAnalyzer:
    """Tests for BICAnalyzer bit independence correlation matrix."""

    def test_bic_analysis(self):
        """Verify BIC analysis computes low average correlation (< 0.20) and high independence score."""
        bic = BICAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message for BIC Evaluation"

        res = bic.analyze(master_key, plaintext, samples=32)

        assert res["output_bits_evaluated"] > 0
        assert res["average_correlation"] < 0.25
        assert res["independence_score"] > 0.75
        assert res["passed"] is True

    def test_export_results(self):
        """Verify export_results returns matrix dictionary."""
        bic = BICAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message"

        bic.analyze(master_key, plaintext, samples=10)
        exported = bic.export_results("dict")

        assert "size" in exported
        assert "matrix" in exported
