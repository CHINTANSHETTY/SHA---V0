"""Unit tests for DifferentialAnalyzer (crypto/analysis/differential.py)."""

import pytest
from crypto.analysis.differential import DifferentialAnalyzer


class TestDifferentialAnalyzer:
    """Tests for DifferentialAnalyzer XOR difference propagation."""

    def test_compare_ciphers(self):
        """Verify compare function correctly counts XOR bit differences."""
        analyzer = DifferentialAnalyzer()
        ct1 = b"\x00\x00\x00\x00"
        ct2 = b"\xFF\x00\x0F\x00"

        comp = analyzer.compare(ct1, ct2)
        # 8 + 0 + 4 + 0 = 12 bits changed out of 32 bits
        assert comp["changed_bits"] == 12
        assert comp["total_bits"] == 32
        assert comp["difference_ratio"] == 0.375

    def test_differential_propagation(self):
        """Verify controlled input difference propagates to ~50% output bit changes."""
        analyzer = DifferentialAnalyzer()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message for Differential Test"
        delta_bytes = b"\x01\x00\x00\x00"

        res = analyzer.analyze(master_key, plaintext, delta_bytes=delta_bytes)

        assert res["input_difference_bits"] == 1
        assert res["output_difference_bits"] > 0
        assert 0.35 <= res["differential_probability"] <= 0.65
        assert res["passed"] is True
