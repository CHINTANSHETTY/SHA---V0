#!/usr/bin/env python3
"""
Benchmark Demo Script - KDR-CA-AEAD v1.0.0

This script demonstrates execution time and throughput profiling
for encryption operations across varying payload sizes.
"""

import time
from crypto import encrypt_bytes, decrypt_bytes


def profile_size(payload_size_kb, iterations=100):
    master_key = b"Nagamrutha_Research_Master_Key_32B"
    payload = b"A" * (payload_size_kb * 1024)

    start_time = time.perf_counter()
    for _ in range(iterations):
        pkg = encrypt_bytes(payload, master_key)
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time_ms = (total_time / iterations) * 1000
    total_data_mb = (payload_size_kb * iterations) / 1024
    throughput_mbs = total_data_mb / total_time

    return avg_time_ms, throughput_mbs


def main():
    print("=" * 65)
    print("  KDR-CA-AEAD v1.0.0 - Micro-Benchmark Profiling Demo")
    print("=" * 65)

    sizes_kb = [1, 10, 100]
    print("\n| Payload Size | Iterations | Avg Latency (ms) | Throughput (MB/s) |")
    print("| :--- | :--- | :--- | :--- |")

    for size_kb in sizes_kb:
        avg_ms, throughput = profile_size(size_kb, iterations=50)
        print(f"| {size_kb:4d} KB       | 50         | {avg_ms:12.3f} ms | {throughput:14.2f} MB/s |")

    print("\n[SUCCESS] Benchmark profiling demonstration complete!")


if __name__ == "__main__":
    main()
