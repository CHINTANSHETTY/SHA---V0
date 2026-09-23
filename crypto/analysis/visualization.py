"""
Module:
    visualization.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Publication-Quality Graph Generation Subsystem for IEEE Paper Submission.
    Generates high-resolution PNG plots for Avalanche Effect, Entropy Profiles,
    Byte Histograms, Correlation Scatter, and Comparative Cipher Benchmarks.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)

IEEE Mapping:
    Section V & VI – Figures & Graphical Plots for Publication
"""

from __future__ import annotations

import os
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")  # Non-interactive background renderer
import matplotlib.pyplot as plt

from crypto.analysis.randomness import run_randomness_suite
from crypto.analysis.statistics import (
    measure_plaintext_avalanche,
    measure_key_avalanche,
    calculate_histogram_uniformity,
    calculate_correlation_coefficients,
    compare_with_reference_ciphers,
)
from crypto.engine.encrypt import encrypt_bytes


def plot_avalanche_effect(
    output_dir: str,
    pt_avalanche: Dict[str, Any],
    key_avalanche: Dict[str, Any]
) -> str:
    """Generates avalanche.png: Plaintext & Key Avalanche Effect versus Ideal 50% line."""
    plt.figure(figsize=(8, 5))

    pt_ratios = [r * 100.0 for r in pt_avalanche.get("raw_ratios", [])]
    key_ratios = [r * 100.0 for r in key_avalanche.get("raw_ratios", [])]

    samples_pt = range(1, len(pt_ratios) + 1)
    samples_key = range(1, len(key_ratios) + 1)

    plt.plot(samples_pt, pt_ratios, label="Plaintext Bit Flip Avalanche (%)", color="#1f77b4", alpha=0.85, linewidth=1.5)
    plt.plot(samples_key, key_ratios, label="Key Bit Flip Avalanche (%)", color="#ff7f0e", alpha=0.85, linewidth=1.5)

    plt.axhline(y=50.0, color="r", linestyle="--", linewidth=2.0, label="Ideal Strict Avalanche Criterion (50%)")

    plt.title("Strict Avalanche Criterion (SAC) Analysis - KDR-CA-AEAD", fontsize=12, fontweight="bold")
    plt.xlabel("1-Bit Flip Sample Index", fontsize=10)
    plt.ylabel("Output Ciphertext Bit Flip Percentage (%)", fontsize=10)
    plt.ylim(30, 70)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "avalanche.png")
    file_path_svg = os.path.join(output_dir, "avalanche.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_entropy_profile(output_dir: str, ciphertext: bytes) -> str:
    """Generates entropy.png: Shannon Entropy profile across 16-byte windows vs Theoretical Max 8.0."""
    plt.figure(figsize=(8, 5))

    window_size = 16
    entropies = []
    num_windows = max(1, len(ciphertext) // window_size)

    for i in range(num_windows):
        block = ciphertext[i * window_size : (i + 1) * window_size]
        if block:
            from crypto.analysis.randomness import calculate_shannon_entropy
            entropies.append(calculate_shannon_entropy(block))

    plt.plot(range(1, len(entropies) + 1), entropies, marker="o", markersize=4, color="#2ca02c", linewidth=1.8, label="Local Window Entropy")
    plt.axhline(y=8.0, color="k", linestyle="--", linewidth=1.8, label="Theoretical Max Entropy (8.0 bits/byte)")
    plt.axhline(y=7.9, color="orange", linestyle=":", linewidth=1.5, label="NIST Acceptable Randomness Limit (7.9 bits/byte)")

    plt.title("Shannon Entropy Profile Across Payload Blocks", fontsize=12, fontweight="bold")
    plt.xlabel("Block Window Index (16 Bytes / Block)", fontsize=10)
    plt.ylabel("Entropy (bits/byte)", fontsize=10)
    plt.ylim(5.0, 8.5)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "entropy.png")
    file_path_svg = os.path.join(output_dir, "entropy.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_byte_histogram(output_dir: str, ciphertext: bytes) -> str:
    """Generates histogram.png & histogram.svg: Byte Occurrence Frequency Distribution (0 to 255)."""
    plt.figure(figsize=(8, 5))

    freq = [0] * 256
    for b in ciphertext:
        freq[b] += 1

    expected = len(ciphertext) / 256.0

    plt.bar(range(256), freq, color="#9467bd", alpha=0.75, width=1.0, edgecolor="none", label="Observed Byte Frequencies")
    plt.axhline(y=expected, color="red", linestyle="--", linewidth=2.0, label=f"Ideal Uniform Distribution (E = {expected:.1f})")

    plt.title("Ciphertext Byte Value Occurrence Histogram (0–255)", fontsize=12, fontweight="bold")
    plt.xlabel("Byte Decimal Value (0 to 255)", fontsize=10)
    plt.ylabel("Frequency Count", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "histogram.png")
    file_path_svg = os.path.join(output_dir, "histogram.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_correlation_scatter(output_dir: str, plaintext: bytes, ciphertext: bytes) -> str:
    """Generates correlation.png & correlation.svg: Plaintext vs Ciphertext Byte Value Correlation Scatter Plot."""
    plt.figure(figsize=(8, 5))

    n = min(len(plaintext), len(ciphertext))
    pt_vals = list(plaintext[:n])
    ct_vals = list(ciphertext[:n])

    plt.scatter(pt_vals, ct_vals, alpha=0.6, color="#d62728", edgecolors="none", s=25, label="Data Point (P_i, C_i)")

    plt.title("Plaintext vs Ciphertext Byte Value Correlation Scatter", fontsize=12, fontweight="bold")
    plt.xlabel("Plaintext Byte Value (0–255)", fontsize=10)
    plt.ylabel("Ciphertext Byte Value (0–255)", fontsize=10)
    plt.xlim(0, 255)
    plt.ylim(0, 255)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "correlation.png")
    file_path_svg = os.path.join(output_dir, "correlation.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_comparison_chart(output_dir: str, comparison_data: Dict[str, Any]) -> str:
    """Generates comparison.png & comparison.svg: Bar Chart Comparing KDR-CA-AEAD vs AES-128-GCM and ChaCha20-Poly1305."""
    plt.figure(figsize=(8, 5))

    ciphers = ["KDR-CA-AEAD", "AES-128-GCM", "ChaCha20-Poly1305"]
    avalanche_vals = [
        comparison_data["kdr_ca_aead"]["avalanche_percent"],
        comparison_data["aes_128_gcm"]["avalanche_percent"],
        comparison_data["chacha20_poly1305"]["avalanche_percent"],
    ]

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    bars = plt.bar(ciphers, avalanche_vals, color=colors, width=0.5, alpha=0.85)
    plt.axhline(y=50.0, color="r", linestyle="--", linewidth=1.8, label="Ideal SAC (50.0%)")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height + 0.5, f"{height:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=10)

    plt.title("Comparative Plaintext Avalanche Effect Benchmark (%)", fontsize=12, fontweight="bold")
    plt.ylabel("Measured Avalanche Ratio (%)", fontsize=10)
    plt.ylim(0, 65)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "comparison.png")
    file_path_svg = os.path.join(output_dir, "comparison.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def generate_all_security_plots(output_dir: str) -> Dict[str, str]:
    """Runs all visual plot routines and saves publication graph artifacts to output_dir.

    Args:
        output_dir: Target directory path for image artifacts.

    Returns:
        Dictionary mapping graph names to output file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    pt = b"Healthcare EHR Patient Data Payload: Diagnostic Lab Reports and Prescription Log 2026" * 8
    key = b"Nagamrutha_Research_Master_Key_32B"

    # Sample dataset computation
    pt_avalanche = measure_plaintext_avalanche(key, pt, samples=100)
    key_avalanche = measure_key_avalanche(key, pt, samples=100)

    pkg = encrypt_bytes(pt, key)
    ct = pkg.ciphertext

    comparison_data = compare_with_reference_ciphers(pt, key, samples=50)

    path_avalanche = plot_avalanche_effect(output_dir, pt_avalanche, key_avalanche)
    path_entropy = plot_entropy_profile(output_dir, ct)
    path_histogram = plot_byte_histogram(output_dir, ct)
    path_correlation = plot_correlation_scatter(output_dir, pt, ct)
    path_comparison = plot_comparison_chart(output_dir, comparison_data)

    return {
        "avalanche": path_avalanche,
        "entropy": path_entropy,
        "histogram": path_histogram,
        "correlation": path_correlation,
        "comparison": path_comparison,
    }


# =========================================================
# PHASE 2.4 BENCHMARK VISUALIZATION ROUTINES (300 DPI)
# =========================================================

def plot_enc_dec_time(output_dir: str, master_results: Dict[str, Any]) -> str:
    """Generates enc_dec_time.png: Encryption vs Decryption execution time (ms) curve."""
    plt.figure(figsize=(8, 5))

    kdr_evals = master_results.get("ciphers", {}).get("kdr_ca_aead", [])
    labels = [e.get("payload_size_kb", 0) for e in kdr_evals]

    enc_times = [e["encryption"]["mean_ms"] for e in kdr_evals]
    dec_times = [e["decryption"]["mean_ms"] for e in kdr_evals]

    x = range(len(labels))
    plt.plot(x, enc_times, marker="o", linewidth=2.0, color="#1f77b4", label="Encryption Time (ms)")
    plt.plot(x, dec_times, marker="s", linestyle="--", linewidth=2.0, color="#ff7f0e", label="Decryption Time (ms)")

    plt.xticks(x, [f"{sz} KB" if sz >= 1 else f"{int(sz*1024)} B" for sz in labels], rotation=30)
    plt.yscale("log")
    plt.title("KDR-CA-AEAD Encryption vs Decryption Execution Time (Log Scale)", fontsize=12, fontweight="bold")
    plt.xlabel("Payload Buffer Size", fontsize=10)
    plt.ylabel("Execution Latency (ms)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "enc_dec_time.png")
    file_path_svg = os.path.join(output_dir, "enc_dec_time.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_throughput_scaling(output_dir: str, master_results: Dict[str, Any]) -> str:
    """Generates throughput_scaling.png & throughput_scaling.svg: Throughput (MB/s) vs payload buffer size."""
    plt.figure(figsize=(8, 5))

    ciphers = master_results.get("ciphers", {})
    colors = {"kdr_ca_aead": "#1f77b4", "aes_256_gcm": "#ff7f0e", "chacha20_poly1305": "#2ca02c"}
    labels_map = {"kdr_ca_aead": "KDR-CA-AEAD (Proposed)", "aes_256_gcm": "AES-256-GCM", "chacha20_poly1305": "ChaCha20-Poly1305"}

    for c_key, evals in ciphers.items():
        x_lbls = [e.get("payload_size_kb", 0) for e in evals]
        tp = [e["encryption"]["throughput_mb_per_sec"] for e in evals]
        x = range(len(x_lbls))
        plt.plot(x, tp, marker="o", linewidth=2.0, color=colors.get(c_key, "b"), label=labels_map.get(c_key, c_key))

    first_evals = next(iter(ciphers.values()))
    x_lbls = [e.get("payload_size_kb", 0) for e in first_evals]
    plt.xticks(range(len(x_lbls)), [f"{sz} KB" if sz >= 1 else f"{int(sz*1024)} B" for sz in x_lbls], rotation=30)

    plt.title("Encryption Throughput Scaling (MB/s) Across Buffer Sizes", fontsize=12, fontweight="bold")
    plt.xlabel("Payload Buffer Size", fontsize=10)
    plt.ylabel("Throughput (MB/sec)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "throughput_scaling.png")
    file_path_svg = os.path.join(output_dir, "throughput_scaling.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_memory_usage(output_dir: str, master_results: Dict[str, Any]) -> str:
    """Generates memory_usage.png & memory_usage.svg: Peak memory footprint (KB) across payload buffer sizes."""
    plt.figure(figsize=(8, 5))

    kdr_evals = master_results.get("ciphers", {}).get("kdr_ca_aead", [])
    x_lbls = [e.get("payload_size_kb", 0) for e in kdr_evals]
    mem_kb = [e["encryption"]["peak_memory_kb"] for e in kdr_evals]

    x = range(len(x_lbls))
    plt.bar(x, mem_kb, color="#9467bd", alpha=0.85, width=0.5, edgecolor="black", label="Peak Allocation (KB)")
    plt.xticks(x, [f"{sz} KB" if sz >= 1 else f"{int(sz*1024)} B" for sz in x_lbls], rotation=30)

    plt.title("Peak Memory Allocation Footprint Across Buffer Sizes", fontsize=12, fontweight="bold")
    plt.xlabel("Payload Buffer Size", fontsize=10)
    plt.ylabel("Peak Memory Allocation (KB)", fontsize=10)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "memory_usage.png")
    file_path_svg = os.path.join(output_dir, "memory_usage.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_cpu_utilization(output_dir: str, master_results: Dict[str, Any]) -> str:
    """Generates cpu_utilization.png & cpu_utilization.svg: Microseconds per byte execution cost."""
    plt.figure(figsize=(8, 5))

    kdr_evals = master_results.get("ciphers", {}).get("kdr_ca_aead", [])
    x_lbls = [e.get("payload_size_kb", 0) for e in kdr_evals]
    us_per_byte = [e["encryption"]["us_per_byte"] for e in kdr_evals]

    x = range(len(x_lbls))
    plt.plot(x, us_per_byte, marker="D", linewidth=2.0, color="#d62728", label="Microseconds per Byte (μs/B)")
    plt.xticks(x, [f"{sz} KB" if sz >= 1 else f"{int(sz*1024)} B" for sz in x_lbls], rotation=30)

    plt.title("CPU Computational Overhead per Byte (μs/Byte)", fontsize=12, fontweight="bold")
    plt.xlabel("Payload Buffer Size", fontsize=10)
    plt.ylabel("Execution Cost (μs / Byte)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "cpu_utilization.png")
    file_path_svg = os.path.join(output_dir, "cpu_utilization.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_comparative_performance(output_dir: str, master_results: Dict[str, Any]) -> str:
    """Generates comparative_performance.png & comparative_performance.svg: Bar chart comparing cipher throughputs."""
    plt.figure(figsize=(8, 5))

    ciphers = master_results.get("ciphers", {})
    cipher_names = ["KDR-CA-AEAD", "AES-256-GCM", "ChaCha20-Poly1305"]
    c_keys = ["kdr_ca_aead", "aes_256_gcm", "chacha20_poly1305"]

    throughputs = []
    for k in c_keys:
        evals = ciphers.get(k, [])
        idx = min(5, len(evals) - 1) if evals else 0
        tp = evals[idx]["encryption"]["throughput_mb_per_sec"] if evals else 0.0
        throughputs.append(tp)

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    bars = plt.bar(cipher_names, throughputs, color=colors, width=0.5, alpha=0.85)

    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, h + 1.0, f"{h:.1f} MB/s", ha="center", va="bottom", fontweight="bold", fontsize=10)

    plt.title("Comparative Encryption Throughput (100 KB Payload Buffer)", fontsize=12, fontweight="bold")
    plt.ylabel("Throughput (MB/sec)", fontsize=10)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "comparative_performance.png")
    file_path_svg = os.path.join(output_dir, "comparative_performance.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def plot_scalability_curve(output_dir: str, master_results: Dict[str, Any]) -> str:
    """Generates scalability_curve.png & scalability_curve.svg: Execution time vs payload size."""
    plt.figure(figsize=(8, 5))

    kdr_evals = master_results.get("ciphers", {}).get("kdr_ca_aead", [])
    sizes_mb = [e.get("payload_size_mb", 0) for e in kdr_evals]
    times_ms = [e["encryption"]["mean_ms"] for e in kdr_evals]

    plt.plot(sizes_mb, times_ms, marker="o", linewidth=2.2, color="#8c564b", label="KDR-CA-AEAD Scaling Curve")

    plt.title("Linear Scalability Curve O(N) Execution Complexity", fontsize=12, fontweight="bold")
    plt.xlabel("Payload Buffer Size (MB)", fontsize=10)
    plt.ylabel("Encryption Time (ms)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=9)
    plt.tight_layout()

    file_path = os.path.join(output_dir, "scalability_curve.png")
    file_path_svg = os.path.join(output_dir, "scalability_curve.svg")
    plt.savefig(file_path, dpi=300)
    plt.savefig(file_path_svg)
    plt.close()
    return file_path


def generate_all_benchmark_plots(output_dir: str, master_results: Dict[str, Any]) -> Dict[str, str]:
    """Generates all 6 publication-ready 300 DPI benchmark PNG plots.

    Args:
        output_dir: Target output directory.
        master_results: Benchmark master metrics dictionary.

    Returns:
        Dictionary mapping graph names to output file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    p1 = plot_enc_dec_time(output_dir, master_results)
    p2 = plot_throughput_scaling(output_dir, master_results)
    p3 = plot_memory_usage(output_dir, master_results)
    p4 = plot_cpu_utilization(output_dir, master_results)
    p5 = plot_comparative_performance(output_dir, master_results)
    p6 = plot_scalability_curve(output_dir, master_results)

    return {
        "enc_dec_time": p1,
        "throughput_scaling": p2,
        "memory_usage": p3,
        "cpu_utilization": p4,
        "comparative_performance": p5,
        "scalability_curve": p6,
    }

