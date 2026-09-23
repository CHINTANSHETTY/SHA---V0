"""End-to-End Integration Tests for Phase 2.4 Security Subsystem.

Validates end-to-end integration between:
AEADEngine -> AvalancheAnalyzer -> SACAnalyzer -> BICAnalyzer -> EntropyAnalyzer -> RandomnessAnalyzer -> DifferentialAnalyzer -> SecurityMetrics -> SecurityReport
"""

import hashlib
import os
import tempfile
import pytest
from crypto.analysis.avalanche import AvalancheAnalyzer, SACAnalyzer
from crypto.analysis.differential import BICAnalyzer, DifferentialAnalyzer
from crypto.analysis.entropy import EntropyAnalyzer
from crypto.analysis.metrics import SecurityMetrics
from crypto.analysis.randomness import RandomnessAnalyzer
from crypto.analysis.report import SecurityReport
from crypto.primitives.aead import AEADEngine
from crypto.primitives.hkdf import hkdf_expand


class TestPhase24SecurityIntegration:
    """Integration test suite for Phase 2.4 Security Enhancement Framework."""

    def test_full_security_analysis_workflow_integration(self):
        """Verify full end-to-end pipeline from AEADEngine outputs to SecurityReport generation."""
        aead = AEADEngine()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Healthcare Electronic Health Record (EHR) Patient Payload 2026"
        aad = b"header_metadata_context"

        # 1. AEAD Encryption
        enc_res = aead.encrypt(plaintext, master_key=master_key, aad=aad, check_nonce_reuse=False)
        ciphertext = enc_res["ciphertext"]
        tag = enc_res["tag"]
        nonce = enc_res["nonce"]
        full_ct = ciphertext + tag

        # 2. Individual Analyzer Invocations
        avalanche = AvalancheAnalyzer(aead_engine=aead)
        av_res = avalanche.analyze_key(master_key, plaintext, nonce=nonce, samples=20)
        assert av_res["passed"] is True

        sac = SACAnalyzer(aead_engine=aead)
        sac_res = sac.analyze(master_key, plaintext, nonce=nonce, samples=10)
        assert sac_res["passed"] is True

        bic = BICAnalyzer(aead_engine=aead)
        bic_res = bic.analyze(master_key, plaintext, nonce=nonce, samples=32)
        assert bic_res["independence_score"] > 0.70

        entropy = EntropyAnalyzer()
        ent_res = entropy.analyze(full_ct)
        assert ent_res["shannon_entropy"] >= 5.0

        randomness = RandomnessAnalyzer()
        prk = hashlib.sha256(b"master_key_bytes_123456789012345").digest()
        rand_bytes = hkdf_expand(prk, info=b"NIST_randomness_test_seed", length=2000)
        rand_res = randomness.analyze(rand_bytes)
        assert rand_res["overall_passed"] is True

        diff = DifferentialAnalyzer(aead_engine=aead)
        diff_res = diff.analyze(master_key, plaintext, delta_bytes=b"\x01\x00\x00\x00", target="key")
        assert diff_res["passed"] is True

        # 3. Consolidated SecurityMetrics Collection
        metrics = SecurityMetrics()
        metrics_dict = metrics.collect(master_key, plaintext, nonce=nonce, samples=20)
        assert metrics_dict["is_collected"] is True

        # 4. Report Generation in Markdown, JSON, and CSV
        report = SecurityReport()
        md_report = report.generate(metrics, format="markdown")
        assert "# IEEE Security Evaluation Report" in md_report

        json_report = report.generate(metrics, format="json")
        assert "metadata" in json_report

        csv_report = report.generate(metrics, format="csv")
        assert "Metric_Category" in csv_report

        # 5. File Export
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            report.export(tmp_path, metrics, format="markdown")
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 100
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
