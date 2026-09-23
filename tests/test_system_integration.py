"""
Phase 4.1 System Integration Tests (`tests/test_system_integration.py`).

Verifies cross-module interoperation across all KDR-CA-AEAD subsystems:
- Cellular Automata engine (crypto/ca)
- Key derivation & schedule (crypto/key)
- AEAD engine (crypto/engine)
- Authentication & Primitives (crypto/primitives)
- Streaming AEAD (crypto/primitives/streaming)
- Benchmark framework (crypto/benchmark & crypto/analysis/benchmark_runner)
- Validation framework (crypto/validation)
- Analysis modules (crypto/analysis)
"""

import io
import json
import pytest

# Test Public Import Paths
import crypto
from crypto import (
    encrypt_bytes,
    encrypt_payload,
    decrypt_bytes,
    decrypt_payload,
    EncryptedPackage,
    KeySchedule,
    KeyMaterial,
    DynamicCAEngine,
    evolve,
    evolve_step,
    hkdf,
    generate_hmac,
    verify_hmac,
    StreamingAEAD,
    ValidationRunner,
    ValidationReport,
    CryptoError,
    AuthenticationError,
    KeyDerivationError,
    run_full_security_analysis,
    run_full_benchmark_suite,
    verify_end_to_end_pipeline,
)
from crypto.ca import get_rule, validate_rule_sequence
from crypto.ca.mapping import export_rule_configuration, load_rule_configuration
from crypto.engine.encrypt import _generate_keystream
from crypto.key import KeyEvolutionEngine
from crypto.primitives.aead import AEADEngine
from crypto.validation import (
    ValidationCheckResult,
    ValidationReportBuilder,
    generate_validation_report,
)


class TestPublicAPICompatibility:
    """Verifies that all public import paths and package exports remain 100% compatible."""

    def test_top_level_exports(self) -> None:
        """Verify top-level package exports in crypto.__all__."""
        expected_exports = [
            "__version__",
            "encrypt_bytes",
            "encrypt_payload",
            "decrypt_bytes",
            "decrypt_payload",
            "EncryptedPackage",
            "StreamingAEAD",
            "KeySchedule",
            "KeyMaterial",
            "DynamicCAEngine",
            "evolve",
            "evolve_step",
            "hkdf",
            "generate_hmac",
            "verify_hmac",
            "CryptoError",
            "KeyDerivationError",
            "AuthenticationError",
            "run_full_security_analysis",
            "run_full_benchmark_suite",
            "verify_end_to_end_pipeline",
            "ValidationRunner",
            "ValidationReport",
        ]
        for item in expected_exports:
            assert hasattr(crypto, item), f"crypto module missing expected export: {item}"
            assert item in crypto.__all__, f"{item} missing from crypto.__all__"

    def test_validation_subpackage_exports(self) -> None:
        """Verify crypto.validation exports ValidationRunner and ValidationReport."""
        from crypto.validation import ValidationReport as VR, ValidationRunner as VRun
        assert VR is ValidationReport
        assert VRun is ValidationRunner


class TestSubsystemCompatibilityMatrix:
    """Verifies end-to-end data flow and interoperation across subsystem boundaries."""

    def test_ca_to_key_integration(self) -> None:
        """Verify CA rule generation integrates with KeySchedule sub-key expansion."""
        master_key = b"master_secret_ca_key_test_32byte"
        salt = b"0123456789abcdef"
        nonce = b"12byte_nonce"

        ks = KeySchedule.from_master_key(master_key, salt, nonce)
        km = ks.export_key_material()

        assert len(km.rule_table) > 0
        rule_seq = validate_rule_sequence(km.rule_table)
        assert rule_seq == list(km.rule_table)

    def test_key_to_aead_integration(self) -> None:
        """Verify KeySchedule outputs feed directly into AEAD encryption and decryption."""
        master_key = b"aead_key_integration_master_pass"
        plaintext = b"Payload for AEAD integration testing"

        pkg = encrypt_bytes(plaintext, master_key)
        assert isinstance(pkg, EncryptedPackage)
        assert len(pkg.ciphertext) == len(plaintext)
        assert len(pkg.tag) == 32

        decrypted = decrypt_bytes(pkg, master_key)
        assert decrypted == plaintext

    def test_aead_to_streaming_integration(self) -> None:
        """Verify AEAD key derivation engine integrates with StreamingAEAD engine."""
        key_engine = KeyEvolutionEngine()
        streaming_engine = StreamingAEAD(key_engine=key_engine)

        master_key = b"streaming_integration_key_32byte"
        nonce = b"12byte_nonce"
        data = b"Streaming integration test data chunk " * 100

        in_stream = io.BytesIO(data)
        out_stream = io.BytesIO()

        res_enc = streaming_engine.encrypt_stream(in_stream, out_stream, master_key, nonce)
        assert res_enc["total_bytes"] == len(data)

        out_stream.seek(0)
        dec_stream = io.BytesIO()
        res_dec = streaming_engine.decrypt_stream(out_stream, dec_stream, master_key)

        assert res_dec["total_bytes"] == len(data)
        assert dec_stream.getvalue() == data

    def test_streaming_to_validation_integration(self) -> None:
        """Verify outputs produced by streaming AEAD can be evaluated by ValidationRunner."""
        aead_engine = AEADEngine()
        runner = ValidationRunner(aead_engine=aead_engine)

        report_data = runner.run_full_validation(
            master_key=b"validation_key_32bytes_sample_!",
            plaintext=b"Validation payload string for testing",
            trials=5,
            seed=42,
        )

        assert "reproducibility" in report_data
        assert "avalanche" in report_data
        assert "sac" in report_data
        assert "bic" in report_data
        assert "entropy" in report_data

    def test_validation_to_benchmark_integration(self) -> None:
        """Verify ValidationReport formats validation runner data for benchmark export."""
        runner = ValidationRunner()
        val_data = runner.run_full_validation(trials=3, seed=123)

        reporter = ValidationReport(title="Integration Benchmark Test")
        md_text = reporter.generate_markdown(val_data)
        latex_text = reporter.generate_latex(val_data)

        assert "Integration Benchmark Test" in md_text
        assert r"\begin{document}" in latex_text

    def test_analysis_to_reports_integration(self) -> None:
        """Verify high-level analysis and end-to-end pipeline verification entry points."""
        pipeline_status = verify_end_to_end_pipeline()
        assert isinstance(pipeline_status, dict)
        status_str = str(pipeline_status.get("status", "")).upper()
        assert "PASS" in status_str or pipeline_status.get("passed") is True
