"""Unit tests for SecurityReport (crypto/analysis/report.py)."""

import json
import os
import tempfile
import pytest
from crypto.analysis.metrics import SecurityMetrics
from crypto.analysis.report import SecurityReport


class TestSecurityReport:
    """Tests for SecurityReport Markdown, JSON, CSV generation and export."""

    def test_report_markdown(self):
        """Verify Markdown report generation contains IEEE metadata and tables."""
        metrics = SecurityMetrics()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message for Report Generation"
        metrics.collect(master_key, plaintext, samples=10)

        report = SecurityReport()
        md = report.generate(metrics, format="markdown")

        assert "# IEEE Security Evaluation Report" in md
        assert "Key Avalanche Effect" in md
        assert "Algorithm" in md
        assert "Protocol Version" in md

    def test_report_json(self):
        """Verify JSON report generation is valid JSON with metadata schema."""
        metrics = SecurityMetrics()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message"
        metrics.collect(master_key, plaintext, samples=10)

        report = SecurityReport()
        js_str = report.generate(metrics, format="json")
        data = json.loads(js_str)

        assert "metadata" in data
        assert "metrics" in data
        assert data["metadata"]["algorithm"] == "KDR-CA-AEAD"

    def test_report_csv_export(self):
        """Verify CSV export writes formatted CSV file."""
        metrics = SecurityMetrics()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Payload Message"
        metrics.collect(master_key, plaintext, samples=10)

        report = SecurityReport()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            report.export(tmp_path, metrics, format="csv")
            assert os.path.exists(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "Metric_Category,Metric_Name,Value,Status" in content
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
