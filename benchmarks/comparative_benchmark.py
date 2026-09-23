"""
Phase 5 Comparative Performance Benchmark Suite (Fast Iteration Tuning).

IEEE Mapping: Section V-B (Comparative Throughput, Latency & Resource Analysis)

Head-to-head performance comparison of KDR-CA-AEAD against:
  1. AES-256-GCM (NIST SP 800-38D Standard)
  2. ChaCha20-Poly1305 (RFC 8439 Standard)
  3. KDR-CA-AEAD (Our Proposed Cipher Engine)

Evaluated across payload sizes: 64 B, 1 KB, 64 KB, 1 MB.
"""

import sys
import os
import time
import gc
from typing import Dict, Any, List

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from crypto.engine.encrypt import encrypt_bytes
from crypto.engine.decrypt import decrypt_bytes
from crypto.primitives.random import generate_salt, generate_nonce


def benchmark_kdr_ca_aead(payload: bytes, key: bytes, iterations: int) -> Dict[str, float]:
    """Benchmarks KDR-CA-AEAD encryption & decryption performance."""
    salt = generate_salt(16)
    nonce = generate_nonce(12)

    # Warmup
    _ = encrypt_bytes(payload, key, salt=salt, nonce=nonce)

    gc.collect()
    start_enc = time.perf_counter()
    for _ in range(iterations):
        pkg = encrypt_bytes(payload, key, salt=salt, nonce=nonce)
    enc_time = (time.perf_counter() - start_enc) / iterations

    gc.collect()
    start_dec = time.perf_counter()
    for _ in range(iterations):
        _ = decrypt_bytes(pkg, key)
    dec_time = (time.perf_counter() - start_dec) / iterations

    payload_mb = len(payload) / (1024 * 1024)
    enc_throughput = payload_mb / enc_time if enc_time > 0 else 0.0
    dec_throughput = payload_mb / dec_time if dec_time > 0 else 0.0

    return {
        "enc_latency_us": enc_time * 1e6,
        "dec_latency_us": dec_time * 1e6,
        "enc_throughput_mbs": enc_throughput,
        "dec_throughput_mbs": dec_throughput,
        "overhead_bytes": len(pkg.ciphertext) + len(pkg.tag) + len(pkg.salt) + len(pkg.nonce) - len(payload)
    }


def benchmark_aes_256_gcm(payload: bytes, key: bytes, iterations: int) -> Dict[str, float]:
    """Benchmarks AES-256-GCM encryption & decryption performance."""
    aesgcm = AESGCM(key)
    nonce = generate_nonce(12)
    aad = b"KDR-CA-AEAD-Benchmark-AAD"

    _ = aesgcm.encrypt(nonce, payload, aad)

    gc.collect()
    start_enc = time.perf_counter()
    for _ in range(iterations):
        ct = aesgcm.encrypt(nonce, payload, aad)
    enc_time = (time.perf_counter() - start_enc) / iterations

    gc.collect()
    start_dec = time.perf_counter()
    for _ in range(iterations):
        _ = aesgcm.decrypt(nonce, ct, aad)
    dec_time = (time.perf_counter() - start_dec) / iterations

    payload_mb = len(payload) / (1024 * 1024)
    return {
        "enc_latency_us": enc_time * 1e6,
        "dec_latency_us": dec_time * 1e6,
        "enc_throughput_mbs": payload_mb / enc_time if enc_time > 0 else 0.0,
        "dec_throughput_mbs": payload_mb / dec_time if dec_time > 0 else 0.0,
        "overhead_bytes": len(ct) - len(payload)
    }


def benchmark_chacha20_poly1305(payload: bytes, key: bytes, iterations: int) -> Dict[str, float]:
    """Benchmarks ChaCha20-Poly1305 encryption & decryption performance."""
    chacha = ChaCha20Poly1305(key)
    nonce = generate_nonce(12)
    aad = b"KDR-CA-AEAD-Benchmark-AAD"

    _ = chacha.encrypt(nonce, payload, aad)

    gc.collect()
    start_enc = time.perf_counter()
    for _ in range(iterations):
        ct = chacha.encrypt(nonce, payload, aad)
    enc_time = (time.perf_counter() - start_enc) / iterations

    gc.collect()
    start_dec = time.perf_counter()
    for _ in range(iterations):
        _ = chacha.decrypt(nonce, ct, aad)
    dec_time = (time.perf_counter() - start_dec) / iterations

    payload_mb = len(payload) / (1024 * 1024)
    return {
        "enc_latency_us": enc_time * 1e6,
        "dec_latency_us": dec_time * 1e6,
        "enc_throughput_mbs": payload_mb / enc_time if enc_time > 0 else 0.0,
        "dec_throughput_mbs": payload_mb / dec_time if dec_time > 0 else 0.0,
        "overhead_bytes": len(ct) - len(payload)
    }


def run_comparative_benchmarks():
    """Executes comparative performance benchmarks across payload sizes."""
    print("=" * 95)
    print("PHASE 5 COMPARATIVE CIPHER PERFORMANCE BENCHMARK SUITE")
    print("Head-to-head comparison: KDR-CA-AEAD vs AES-256-GCM vs ChaCha20-Poly1305")
    print("=" * 95)

    key_32 = b"Master_Key_256_Bit_32_Bytes_Long"

    sizes = [
        ("64 B Payload", 64, 100),
        ("1 KB Payload", 1024, 30),
        ("64 KB Payload", 64 * 1024, 5),
        ("1 MB Payload", 1024 * 1024, 2),
    ]

    for label, size_bytes, iters in sizes:
        payload = b"\x42" * size_bytes
        print(f"\n--- PAYLOAD EVALUATION: {label} ({size_bytes:,} bytes, {iters} iterations) ---")
        print(f"{'Cipher System':<25} | {'Enc Latency (us)':<18} | {'Enc Throughput':<18} | {'Dec Throughput':<18}")
        print("-" * 90)

        # 1. KDR-CA-AEAD
        res_kdr = benchmark_kdr_ca_aead(payload, key_32, iters)
        print(f"{'KDR-CA-AEAD (Proposed)':<25} | {res_kdr['enc_latency_us']:>12.2f} us    | {res_kdr['enc_throughput_mbs']:>12.2f} MB/s | {res_kdr['dec_throughput_mbs']:>12.2f} MB/s")

        # 2. AES-256-GCM
        res_aes = benchmark_aes_256_gcm(payload, key_32, iters)
        print(f"{'AES-256-GCM (Hardware)':<25} | {res_aes['enc_latency_us']:>12.2f} us    | {res_aes['enc_throughput_mbs']:>12.2f} MB/s | {res_aes['dec_throughput_mbs']:>12.2f} MB/s")

        # 3. ChaCha20-Poly1305
        res_chacha = benchmark_chacha20_poly1305(payload, key_32, iters)
        print(f"{'ChaCha20-Poly1305 (Software)':<25} | {res_chacha['enc_latency_us']:>12.2f} us    | {res_chacha['enc_throughput_mbs']:>12.2f} MB/s | {res_chacha['dec_throughput_mbs']:>12.2f} MB/s")

    print("\n=" * 95)
    print("PHASE 5 COMPARATIVE BENCHMARK COMPLETE")
    print("=" * 95)


if __name__ == "__main__":
    run_comparative_benchmarks()
