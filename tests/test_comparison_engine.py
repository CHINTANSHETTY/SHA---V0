"""Unit tests for ComparisonEngine (research/comparison.py)."""

import json
import os
import tempfile
import pytest
from research.comparison import ComparisonEngine


class TestComparisonEngine:
    """Tests for ComparisonEngine cipher comparative evaluations and table generation."""

    def test_compare_all(self):
        """Verify comparative evaluation returns statistics for KDR-CA-AEAD, AES-GCM, and ChaCha20."""
        engine = ComparisonEngine()
        res = engine.compare_all(plaintext=b"Comparative Analysis Payload", iterations=5)

        assert "kdr_ca_aead" in res
        assert "aes_128_gcm" in res
        assert "chacha20_poly1305" in res

        kdr = res["kdr_ca_aead"]
        assert kdr["throughput_mbps"] > 0.0
        assert kdr["avalanche_percent"] > 40.0
        assert "implementation_type" in kdr

    def test_generate_table_and_export(self):
        """Verify Markdown table generation and summary export."""
        engine = ComparisonEngine()
        table_md = engine.generate_table()

        assert "| Cipher Scheme |" in table_md
        assert "| `KDR-CA-AEAD (Phase 2.3)` |" in table_md

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            engine.export_summary(tmp_path)
            assert os.path.exists(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "kdr_ca_aead" in data
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
