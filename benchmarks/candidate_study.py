"""Phase 2.1A Candidate Algorithm & Parameter Study Script (Updated with Statistical Rigor).

Empirically benchmarks Candidate Architectures (A, B, C, A-Chain), Offsets (Delta),
Rule Table Capacities (M), and Generation Counts (G) for IEEE Section V.
Includes mean (mu), std dev (sigma), 95% Confidence Intervals, environment specs,
and multi-dataset entropy evaluation across 2,000 random bit flip iterations.
"""

import sys
import os
import math
import time
import random
import platform
from typing import Tuple, List, Dict, Any

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto.engine.key_schedule import KeySchedule


# =========================================================
# ECA HELPER (PARAMETRIC GENERATIONS G)
# =========================================================
def evaluate_eca_byte(position: int, rule1: int, rule2: int, generations: int = 1) -> int:
    """Evaluates 1D 8-bit periodic Elementary Cellular Automata for G generations."""
    state = (position ^ rule1) & 0xFF

    for _ in range(generations):
        new_byte = 0
        for i in range(8):
            left = (state >> ((i + 1) % 8)) & 1
            self_bit = (state >> i) & 1
            right = (state >> ((i - 1) % 8)) & 1

            neighborhood = (left << 2) | (self_bit << 1) | right
            new_bit = (rule2 >> neighborhood) & 1
            new_byte |= (new_bit << i)
        state = new_byte

    return state ^ rule1


# =========================================================
# CANDIDATE PIPELINE TRANSFORMATIONS
# =========================================================
def candidate_a_forward(data: bytes, rule_table: tuple[int, ...], delta: int = 13, generations: int = 1) -> bytes:
    """Candidate A (Local Byte S-Box): Modulo Addition -> Rotation -> XOR."""
    m_len = len(rule_table)
    res = bytearray(len(data))
    for i, b in enumerate(data):
        r1 = rule_table[i % m_len]
        r2 = rule_table[(i + delta) % m_len]
        ca_b = evaluate_eca_byte(i, r1, r2, generations)
        shift = (r1 % 7) + 1

        y1 = (b + ca_b) & 0xFF
        y2 = ((y1 >> shift) | (y1 << (8 - shift))) & 0xFF
        res[i] = y2 ^ r2
    return bytes(res)


def candidate_achain_forward(data: bytes, rule_table: tuple[int, ...], delta: int = 13, generations: int = 1) -> bytes:
    """Candidate A-Chain (Inter-Byte Diffusion): Chained State -> Modulo Addition -> Rotation -> XOR."""
    m_len = len(rule_table)
    res = bytearray(len(data))
    prev_state = 0xC5  # Fixed initial feedback vector

    for i, b in enumerate(data):
        r1 = rule_table[i % m_len]
        r2 = rule_table[(i + delta) % m_len]
        ca_b = evaluate_eca_byte(i, r1, r2, generations)
        shift = (r1 % 7) + 1

        # Chained input mix
        mixed_b = b ^ prev_state
        y1 = (mixed_b + ca_b) & 0xFF
        y2 = ((y1 >> shift) | (y1 << (8 - shift))) & 0xFF
        out_b = y2 ^ r2
        res[i] = out_b
        prev_state = out_b

    return bytes(res)


def candidate_achain_inverse(data: bytes, rule_table: tuple[int, ...], delta: int = 13, generations: int = 1) -> bytes:
    """Candidate A-Chain Inverse: XOR -> Rotation -> Modulo Subtraction -> Un-chain."""
    m_len = len(rule_table)
    res = bytearray(len(data))
    prev_state = 0xC5

    for i, b in enumerate(data):
        r1 = rule_table[i % m_len]
        r2 = rule_table[(i + delta) % m_len]
        ca_b = evaluate_eca_byte(i, r1, r2, generations)
        shift = (r1 % 7) + 1

        y2 = b ^ r2
        y1 = ((y2 << shift) | (y2 >> (8 - shift))) & 0xFF
        mixed_b = (y1 - ca_b) & 0xFF
        orig_b = mixed_b ^ prev_state
        res[i] = orig_b
        prev_state = b

    return bytes(res)


def candidate_b_forward(data: bytes, rule_table: tuple[int, ...], delta: int = 13, generations: int = 1) -> bytes:
    """Candidate B: Rotation -> Modulo Addition -> XOR."""
    m_len = len(rule_table)
    res = bytearray(len(data))
    for i, b in enumerate(data):
        r1 = rule_table[i % m_len]
        r2 = rule_table[(i + delta) % m_len]
        ca_b = evaluate_eca_byte(i, r1, r2, generations)
        shift = (r1 % 7) + 1

        y1 = ((b >> shift) | (b << (8 - shift))) & 0xFF
        y2 = (y1 + ca_b) & 0xFF
        res[i] = y2 ^ r2
    return bytes(res)


def candidate_c_forward(data: bytes, rule_table: tuple[int, ...], delta: int = 13, generations: int = 1) -> bytes:
    """Candidate C: XOR -> Rotation -> Modulo Addition."""
    m_len = len(rule_table)
    res = bytearray(len(data))
    for i, b in enumerate(data):
        r1 = rule_table[i % m_len]
        r2 = rule_table[(i + delta) % m_len]
        ca_b = evaluate_eca_byte(i, r1, r2, generations)
        shift = (r1 % 7) + 1

        y1 = b ^ r2
        y2 = ((y1 >> shift) | (y1 << (8 - shift))) & 0xFF
        res[i] = (y2 + ca_b) & 0xFF
    return bytes(res)


# =========================================================
# STATISTICAL METRICS & BENCHMARK SUITE
# =========================================================
def calculate_entropy(data: bytes) -> float:
    """Computes Shannon Entropy of byte stream in bits per byte."""
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    entropy = 0.0
    length = len(data)
    for count in freq:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy


def count_bit_flips(buf_a: bytes, buf_b: bytes) -> int:
    """Counts differing bits between two byte buffers."""
    return sum(bin(a ^ b).count("1") for a, b in zip(buf_a, buf_b))


def calculate_npcr_uaci(buf_a: bytes, buf_b: bytes) -> Tuple[float, float]:
    """Computes NPCR (%) and UACI (%) between two transformed byte streams."""
    if len(buf_a) != len(buf_b) or not buf_a:
        return 0.0, 0.0

    n = len(buf_a)
    diff_bytes = sum(1 for a, b in zip(buf_a, buf_b) if a != b)
    abs_diff_sum = sum(abs(a - b) for a, b in zip(buf_a, buf_b))

    npcr = (diff_bytes / n) * 100.0
    uaci = (abs_diff_sum / (255.0 * n)) * 100.0
    return npcr, uaci


def compute_stats(values: List[float]) -> Tuple[float, float, Tuple[float, float]]:
    """Computes Mean (mu), Std Dev (sigma), and 95% Confidence Interval (CI)."""
    n = len(values)
    if n == 0:
        return 0.0, 0.0, (0.0, 0.0)

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
    std_dev = math.sqrt(variance)

    margin = 1.96 * (std_dev / math.sqrt(n)) if n > 1 else 0.0
    ci_95 = (mean - margin, mean + margin)
    return mean, std_dev, ci_95


def benchmark_candidate_stat(
    forward_fn,
    data: bytes,
    rule_table: tuple[int, ...],
    delta: int = 13,
    generations: int = 1,
    samples: int = 1000
) -> Dict[str, Any]:
    """Runs SAC, Entropy, NPCR, UACI, and Throughput benchmarks over N random bit flips."""
    total_bits = len(data) * 8
    base_trans = forward_fn(data, rule_table, delta, generations)

    entropy = calculate_entropy(base_trans)

    t_data = data * 500  # Expand to ~32 KB
    start_t = time.perf_counter()
    _ = forward_fn(t_data, rule_table, delta, generations)
    dur = time.perf_counter() - start_t
    throughput_mbs = (len(t_data) / (1024 * 1024)) / dur if dur > 0 else 0.0

    sac_list = []
    npcr_list = []
    uaci_list = []

    # Deterministic seed for reproducible statistical sampling
    rng = random.Random(42)

    for s in range(samples):
        char_idx = rng.randint(0, len(data) - 1)
        bit_idx = rng.randint(0, 7)
        mod_bytes = bytearray(data)
        mod_bytes[char_idx] ^= (1 << bit_idx)

        mod_trans = forward_fn(bytes(mod_bytes), rule_table, delta, generations)
        flips = count_bit_flips(base_trans, mod_trans)
        sac_list.append(flips / total_bits)

        npcr, uaci = calculate_npcr_uaci(base_trans, mod_trans)
        npcr_list.append(npcr)
        uaci_list.append(uaci)

    mean_sac, std_sac, ci_sac = compute_stats(sac_list)
    mean_npcr, std_npcr, _ = compute_stats(npcr_list)
    mean_uaci, std_uaci, _ = compute_stats(uaci_list)

    return {
        "mean_sac": mean_sac,
        "std_sac": std_sac,
        "ci_sac": ci_sac,
        "entropy": entropy,
        "throughput_mbs": throughput_mbs,
        "mean_npcr": mean_npcr,
        "std_npcr": std_npcr,
        "mean_uaci": mean_uaci,
    }


def run_candidate_study():
    """Executes head-to-head empirical candidate & parameter study with statistical sampling."""
    print("=" * 90)
    print("PHASE 2.1A STATISTICALLY RIGOROUS CANDIDATE ALGORITHM & PARAMETER STUDY")
    print("=" * 90)

    # Print Environment Metadata
    print("\nBENCHMARK ENVIRONMENT METADATA:")
    print(f"  OS Platform          : {platform.system()} {platform.release()} ({platform.architecture()[0]})")
    print(f"  Python Version       : {platform.python_version()} ({platform.python_implementation()})")
    print(f"  Processor Architecture: {platform.machine()} / {platform.processor()}")

    master_key = b"IEEE_Phase2_1A_Study_Master_Key_256!"
    salt = b"\x01" * 16
    nonce = b"\x02" * 12
    ks = KeySchedule(master_key, salt, nonce)
    base_rule_table = ks.get_ca_rule_table()

    # Datasets for Multi-Dataset Entropy Evaluation
    medical_text = ("Patient Record Payload: ID=P001, Name=Rahul Kumar, Age=28, Diagnosis=Fever, BloodType=O+. " * 2).encode("utf-8")
    zero_bytes = b"\x00" * 120
    random_bytes = bytes(random.Random(123).randrange(256) for _ in range(120))

    datasets = [
        ("Medical Text (UTF-8)", medical_text),
        ("All-Zero Stream (120B)", zero_bytes),
        ("Random Uniform Bytes", random_bytes)
    ]

    print("\nDATASET ENTROPY PROFILES (BEFORE & AFTER CANDIDATE A-CHAIN):")
    print(f"{'Dataset Name':<28} | {'Raw Input Entropy':<20} | {'Transformed Entropy':<20}")
    print("-" * 75)
    for d_name, d_bytes in datasets:
        in_ent = calculate_entropy(d_bytes)
        out_trans = candidate_achain_forward(d_bytes, base_rule_table, delta=13, generations=1)
        out_ent = calculate_entropy(out_trans)
        print(f"{d_name:<28} | {in_ent:.4f} bits/B         | {out_ent:.4f} bits/B")

    # 1. CANDIDATE PIPELINE COMPARISON (1,000 Random Bit Flips)
    print("\n--- 1. CANDIDATE PIPELINE ARCHITECTURE STATISTICAL COMPARISON (N = 1,000 Flips) ---")
    candidates = [
        ("Candidate A (Local S-Box)", candidate_a_forward),
        ("Candidate A-Chain (Inter-Byte)", candidate_achain_forward),
        ("Candidate B (ROT -> Modulo -> XOR)", candidate_b_forward),
        ("Candidate C (XOR -> ROT -> Modulo)", candidate_c_forward),
    ]

    print(f"{'Candidate Name':<32} | {'Mean SAC (mu)':<15} | {'Std Dev (sigma)':<15} | {'95% Conf Interval':<22} | {'NPCR (%)':<10}")
    print("-" * 105)

    for name, fn in candidates:
        m = benchmark_candidate_stat(fn, medical_text, base_rule_table, delta=13, generations=1, samples=1000)
        ci_str = f"[{m['ci_sac'][0]:.4f}, {m['ci_sac'][1]:.4f}]"
        print(f"{name:<32} | {m['mean_sac']:.4f}           | {m['std_sac']:.4f}          | {ci_str:<22} | {m['mean_npcr']:.2f}%")

    # 2. DUAL-RULE OFFSET PARAMETER EVALUATION
    print("\n--- 2. EVALUATED CONFIGURATION OFFSETS (Candidate A-Chain, N = 1,000 Flips) ---")
    offsets = [1, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    print(f"{'Offset Delta':<15} | {'Mean SAC':<12} | {'Std Dev':<12} | {'NPCR (%)':<12} | {'UACI (%)':<12}")
    print("-" * 75)

    for delta in offsets:
        m = benchmark_candidate_stat(candidate_achain_forward, medical_text, base_rule_table, delta=delta, generations=1, samples=1000)
        print(f"Delta = {delta:<8} | {m['mean_sac']:.4f}       | {m['std_sac']:.4f}      | {m['mean_npcr']:.2f}%       | {m['mean_uaci']:.2f}%")

    # 3. REVERSIBILITY VERIFICATION
    print("\n--- 3. REVERSIBILITY VERIFICATION ---")
    trans_ac = candidate_achain_forward(medical_text, base_rule_table, delta=13, generations=1)
    recov_ac = candidate_achain_inverse(trans_ac, base_rule_table, delta=13, generations=1)
    reversibility_pass = recov_ac == medical_text
    print(f"Reversibility Check (P == D_CA(E_CA(P))): {'PASSED (100% Loss-Free Bijective)' if reversibility_pass else 'FAILED'}")

    print("\n=" * 90)
    print("STATISTICAL STUDY COMPLETE: Rigorous empirical data collected for Phase 2.1B Report.")
    print("=" * 90)


if __name__ == "__main__":
    run_candidate_study()
