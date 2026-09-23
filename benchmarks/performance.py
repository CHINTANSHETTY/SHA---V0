"""
Execution Throughput (MB/s) & Latency Performance Benchmark.

IEEE Mapping: Section V-B (Performance & Execution Throughput Evaluation)
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto.engine.encrypt import encrypt_payload
from crypto.engine.decrypt import decrypt_payload


def run_throughput_benchmark():
    """Measures encryption and decryption speed (MB/s) across payload sizes."""
    sizes_kb = [1, 10, 100, 1000]  # 1 KB to 1 MB
    password = "benchmark_secure_password_123"

    print("=== KDR-CA-AEAD PERFORMANCE THROUGHPUT BENCHMARK ===")
    print(f"{'Payload Size':<15} | {'Enc Time (ms)':<15} | {'Enc Speed (MB/s)':<18} | {'Dec Time (ms)':<15} | {'Dec Speed (MB/s)':<18}")
    print("-" * 88)

    for size_kb in sizes_kb:
        payload_bytes = b"A" * (size_kb * 1024)
        payload_str = payload_bytes.decode("ascii")

        # Encryption benchmark
        t0 = time.perf_counter()
        pkg = encrypt_payload(payload_str, password)
        t1 = time.perf_counter()
        enc_time = (t1 - t0) * 1000  # ms
        enc_speed = (size_kb / 1024) / (t1 - t0) if (t1 - t0) > 0 else 0

        # Decryption benchmark
        t2 = time.perf_counter()
        decrypted = decrypt_payload(pkg, password)
        t3 = time.perf_counter()
        dec_time = (t3 - t2) * 1000  # ms
        dec_speed = (size_kb / 1024) / (t3 - t2) if (t3 - t2) > 0 else 0

        assert decrypted == payload_str

        print(f"{size_kb:<4} KB ({size_kb*1024:<6} B) | {enc_time:<15.2f} | {enc_speed:<18.2f} | {dec_time:<15.2f} | {dec_speed:<18.2f}")


if __name__ == "__main__":
    run_throughput_benchmark()
