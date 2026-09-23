"""Large-Scale Benchmark Runner Subsystem (`crypto.benchmark.runner`).

Provides `LargeScaleBenchmarkRunner` for reproducible benchmarking across payload sizes (1 KB to 100 MB),
fair multi-cipher comparative evaluations, and resource utilization profiling.
"""

import os
import random
import time
from typing import Any, Dict, List, Optional

from crypto.benchmark.benchmark import (
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkSuite,
    collect_hardware_and_software_metadata,
)
from crypto.benchmark.profiler import CryptographicProfiler
from crypto.primitives.aead import AEADEngine
from research.statistics import StatisticsEngine


def _generate_deterministic_payload(size: int, seed: int = 42) -> bytes:
    """Generate reproducible deterministic byte payload using fixed PRNG seed.

    Args:
        size: Size of payload in bytes.
        seed: Integer seed value.

    Returns:
        bytes: Deterministic payload bytes.
    """
    rng = random.Random(seed)
    return rng.randbytes(size)


class LargeScaleBenchmarkRunner:
    """Large-Scale Cryptographic Benchmark Runner."""

    def __init__(self, config: Optional[BenchmarkConfig] = None) -> None:
        """Initialize LargeScaleBenchmarkRunner."""
        self.config: BenchmarkConfig = config if config is not None else BenchmarkConfig()
        self.aead_engine: AEADEngine = AEADEngine()
        self.stats_engine: StatisticsEngine = StatisticsEngine()
        self.profiler: CryptographicProfiler = CryptographicProfiler()

    def run_suite(self) -> BenchmarkSuite:
        """Execute full large-scale benchmark suite across configured payload sizes.

        Returns:
            BenchmarkSuite: Complete benchmark suite object.
        """
        metadata = collect_hardware_and_software_metadata()
        results: List[BenchmarkResult] = []

        master_key = b"master_key_bytes_large_scale_32"
        aad_bytes = b"IEEE_aad_header_bytes"

        # 1. KDR-CA-AEAD Scalability Benchmarks
        for size in self.config.sizes:
            payload = _generate_deterministic_payload(size, seed=self.config.seed)

            # Warm-up iterations (excluded from statistics)
            for _ in range(self.config.warmup_iterations):
                _ = self.aead_engine.encrypt(payload, master_key=master_key, aad=aad_bytes, check_nonce_reuse=False)

            # Measured iterations
            enc_latencies_ms: List[float] = []
            dec_latencies_ms: List[float] = []
            throughputs_mbps: List[float] = []

            pkg = self.aead_engine.encrypt(payload, master_key=master_key, aad=aad_bytes, check_nonce_reuse=False)
            ct, tag, nonce = pkg["ciphertext"], pkg["tag"], pkg["nonce"]

            self.profiler.start_profiling()
            for _ in range(self.config.iterations):
                t0 = time.perf_counter()
                res_enc = self.aead_engine.encrypt(payload, master_key=master_key, aad=aad_bytes, check_nonce_reuse=False)
                t1 = time.perf_counter()
                _ = self.aead_engine.decrypt(res_enc["ciphertext"], res_enc["tag"], master_key, res_enc["nonce"], aad=aad_bytes)
                t2 = time.perf_counter()

                dt_enc = t1 - t0
                dt_dec = t2 - t1
                enc_latencies_ms.append(dt_enc * 1000.0)
                dec_latencies_ms.append(dt_dec * 1000.0)

                mbps = (size / (1024.0 * 1024.0)) / dt_enc if dt_enc > 0 else 0.0
                throughputs_mbps.append(mbps)

            mem_profile = self.profiler.stop_profiling()

            enc_stats = self.stats_engine.analyze(enc_latencies_ms)
            dec_stats = self.stats_engine.analyze(dec_latencies_ms)
            tp_stats = self.stats_engine.analyze(throughputs_mbps)

            results.append(
                BenchmarkResult(
                    cipher_name="KDR-CA-AEAD",
                    message_size_bytes=size,
                    iterations=self.config.iterations,
                    warmup_iterations=self.config.warmup_iterations,
                    encryption_stats=enc_stats,
                    decryption_stats=dec_stats,
                    throughput_mbps_stats=tp_stats,
                    memory_stats=mem_profile,
                )
            )

        # 2. Reference Cipher Comparative Evaluations (if enabled)
        comparisons_dict: Dict[str, Any] = {}
        if self.config.include_comparisons:
            comparisons_dict = self._run_cipher_comparisons(
                master_key=master_key, aad=aad_bytes, sample_size=self.config.sizes[0] if self.config.sizes else 1024
            )

        return BenchmarkSuite(
            config=self.config,
            metadata=metadata,
            results=results,
            comparisons=comparisons_dict,
        )

    def _run_cipher_comparisons(self, master_key: bytes, aad: bytes, sample_size: int) -> Dict[str, Any]:
        """Run fair comparative evaluation against reference ciphers under identical payloads.

        Ciphers evaluated:
        1. KDR-CA-AEAD
        2. AES-128-GCM
        3. ChaCha20-Poly1305
        4. AES-CTR + HMAC-SHA256
        """
        payload = _generate_deterministic_payload(sample_size, seed=self.config.seed)
        nonce12 = b"\x00" * 12
        ciphers: Dict[str, Any] = {}

        # 1. KDR-CA-AEAD
        lats_kdr: List[float] = []
        for _ in range(self.config.iterations):
            t0 = time.perf_counter()
            _ = self.aead_engine.encrypt(payload, master_key=master_key, aad=aad, check_nonce_reuse=False)
            t1 = time.perf_counter()
            lats_kdr.append((t1 - t0) * 1000.0)

        mean_kdr = self.stats_engine.calculate_mean(lats_kdr)
        ciphers["kdr_ca_aead"] = {
            "cipher_name": "KDR-CA-AEAD",
            "implementation": "Pure Python + CA Engine",
            "latency_ms": self.stats_engine.analyze(lats_kdr),
            "throughput_mbps": round((sample_size / (1024.0 * 1024.0)) / (mean_kdr / 1000.0), 4) if mean_kdr > 0 else 0.0,
        }

        # 2. Native cryptography ciphers if available
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

            # AES-128-GCM
            aes_key = AESGCM.generate_key(bit_length=128)
            aesgcm = AESGCM(aes_key)
            lats_aes: List[float] = []
            for _ in range(self.config.iterations):
                t0 = time.perf_counter()
                _ = aesgcm.encrypt(nonce12, payload, aad)
                t1 = time.perf_counter()
                lats_aes.append((t1 - t0) * 1000.0)
            mean_aes = self.stats_engine.calculate_mean(lats_aes)
            ciphers["aes_128_gcm"] = {
                "cipher_name": "AES-128-GCM",
                "implementation": "Native C (OpenSSL / PyCA Cryptography)",
                "latency_ms": self.stats_engine.analyze(lats_aes),
                "throughput_mbps": round((sample_size / (1024.0 * 1024.0)) / (mean_aes / 1000.0), 4) if mean_aes > 0 else 0.0,
            }

            # ChaCha20-Poly1305
            chacha_key = ChaCha20Poly1305.generate_key()
            chacha = ChaCha20Poly1305(chacha_key)
            lats_chacha: List[float] = []
            for _ in range(self.config.iterations):
                t0 = time.perf_counter()
                _ = chacha.encrypt(nonce12, payload, aad)
                t1 = time.perf_counter()
                lats_chacha.append((t1 - t0) * 1000.0)
            mean_chacha = self.stats_engine.calculate_mean(lats_chacha)
            ciphers["chacha20_poly1305"] = {
                "cipher_name": "ChaCha20-Poly1305",
                "implementation": "Native C (OpenSSL / PyCA Cryptography)",
                "latency_ms": self.stats_engine.analyze(lats_chacha),
                "throughput_mbps": round((sample_size / (1024.0 * 1024.0)) / (mean_chacha / 1000.0), 4) if mean_chacha > 0 else 0.0,
            }

            # AES-CTR + HMAC-SHA256
            ctr_key = os.urandom(16)
            hmac_key = os.urandom(32)
            lats_ctr: List[float] = []
            for _ in range(self.config.iterations):
                t0 = time.perf_counter()
                cipher = Cipher(algorithms.AES(ctr_key), modes.CTR(b"\x00" * 16))
                encryptor = cipher.encryptor()
                ct = encryptor.update(payload) + encryptor.finalize()
                import hmac, hashlib
                tag = hmac.new(hmac_key, aad + ct, hashlib.sha256).digest()
                t1 = time.perf_counter()
                lats_ctr.append((t1 - t0) * 1000.0)
            mean_ctr = self.stats_engine.calculate_mean(lats_ctr)
            ciphers["aes_ctr_hmac_sha256"] = {
                "cipher_name": "AES-CTR + HMAC-SHA256",
                "implementation": "Native C AES-CTR + Python HMAC",
                "latency_ms": self.stats_engine.analyze(lats_ctr),
                "throughput_mbps": round((sample_size / (1024.0 * 1024.0)) / (mean_ctr / 1000.0), 4) if mean_ctr > 0 else 0.0,
            }
        except Exception:
            pass

        return ciphers
