"""Unit tests for RandomnessAnalyzer (crypto/analysis/randomness.py)."""

import hashlib
import pytest
from crypto.analysis.randomness import RandomnessAnalyzer, run_randomness_suite
from crypto.primitives.hkdf import hkdf_expand


class TestRandomnessAnalyzer:
    """Tests for RandomnessAnalyzer NIST SP 800-22 statistical tests."""

    def test_randomness_suite_pass(self):
        """Verify RFC 5869 HKDF pseudorandom expanded byte stream passes NIST statistical randomness suite."""
        analyzer = RandomnessAnalyzer(alpha=0.01)
        prk = hashlib.sha256(b"master_key_bytes_123456789012345").digest()
        data = hkdf_expand(prk, info=b"NIST_randomness_test_seed", length=2000)

        res = analyzer.analyze(data)

        assert "monobit_test" in res
        assert "runs_test" in res
        assert "frequency_analysis" in res
        assert "serial_test" in res
        assert res["entropy"] >= 7.80
        assert res["overall_passed"] is True

        summary_str = analyzer.summary(res)
        assert "Randomness Suite Summary" in summary_str
