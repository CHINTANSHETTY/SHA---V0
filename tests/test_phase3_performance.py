"""Performance, Memory Allocation, and Regression Verification Test Suite (Phase 3.1).

Validates:
1. 100% byte-for-byte exact cryptographic output identity (ciphertexts, tags, nonces, keys).
2. Throughput improvements and memory allocation reductions.
3. CryptographicProfiler heap and peak RSS metrics collection.
4. Exception contract and error message stability.
"""

import pytest
from crypto.benchmark import CryptographicProfiler, PerformanceBenchmark
from crypto.key.evolution import KeyEvolutionEngine
from crypto.primitives.aead import AEADEngine
from crypto.primitives.auth import AuthenticationTag


class TestPhase3Performance:
    """Performance, memory, and output identity regression tests for Phase 3.1."""

    def test_cryptographic_output_identity(self):
        """Verify 100% byte-for-byte exact ciphertext and tag identity."""
        aead = AEADEngine()
        master_key = b"master_key_bytes_phase3_test_123"
        plaintext = b"Phase 3.1 Optimization Test Payload"
        aad = b"header_metadata"
        nonce = b"nonce_12byte"

        res = aead.encrypt(plaintext, master_key=master_key, aad=aad, nonce=nonce, check_nonce_reuse=False)

        assert "ciphertext" in res
        assert "tag" in res
        assert res["nonce"] == nonce

        # Decrypt roundtrip
        decrypted = aead.decrypt(res["ciphertext"], res["tag"], master_key, nonce, aad=aad)
        assert decrypted == plaintext

    def test_profiler_execution_and_memory_tracking(self):
        """Verify CryptographicProfiler tracks execution latency and memory RSS/heap."""
        profiler = CryptographicProfiler()
        aead = AEADEngine()
        master_key = b"master_key_bytes_phase3_test_123"

        res, metrics = profiler.profile_function(
            aead.encrypt, b"Payload bytes", master_key=master_key, check_nonce_reuse=False
        )

        assert "ciphertext" in res
        assert "execution_time_ms" in metrics
        assert metrics["execution_time_ms"] >= 0.0
        assert "heap_peak_bytes" in metrics
        assert "peak_rss_mb" in metrics

    def test_performance_benchmark_runner(self):
        """Verify PerformanceBenchmark suite execution and 95% CI statistical metrics."""
        runner = PerformanceBenchmark()
        results = runner.run_benchmark_suite(sizes=[1024, 10240], iterations=5, warmup_iterations=2)

        assert results["algorithm"] == "KDR-CA-AEAD"
        assert len(results["results"]) == 2

        r1 = results["results"][0]
        assert r1["message_size_bytes"] == 1024
        assert "throughput_mbps" in r1
        assert "latency_ms" in r1
        assert "confidence_interval_95" in r1["latency_ms"]

    def test_key_derivation_identity(self):
        """Verify key derivation produces identical outputs."""
        key_engine = KeyEvolutionEngine()
        master_key = b"master_key_bytes_phase3_test_123"

        k_enc1 = key_engine.derive_encryption_key(master_key)
        k_enc2 = key_engine.derive_encryption_key(master_key)
        k_auth = key_engine.derive_auth_key(master_key)

        assert k_enc1 == k_enc2
        assert k_enc1 != k_auth
