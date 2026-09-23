"""Unit tests for SecurityMetrics (crypto/analysis/metrics.py)."""

import pytest
from crypto.analysis.metrics import SecurityMetrics


class TestSecurityMetrics:
    """Tests for SecurityMetrics collection and export."""

    def test_security_metrics_collection(self):
        """Verify SecurityMetrics collects data from all 6 analyzers."""
        metrics = SecurityMetrics()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message for Metrics Collection"

        res = metrics.collect(master_key, plaintext, samples=20)

        assert res["is_collected"] is True
        assert "avalanche" in res
        assert "sac" in res
        assert "bic" in res
        assert "entropy" in res
        assert "randomness" in res
        assert "differential" in res

        summary_str = metrics.summary()
        assert "Security Metrics Summary" in summary_str
        assert "Key Avalanche Effect" in summary_str
