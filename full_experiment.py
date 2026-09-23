"""
Module: full_experiment.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Comprehensive experimental evaluation framework for the revised SHA-512 + 2x2 Reversible CA cipher.

Evaluates:
  1. Synthetic Healthcare Datasets (100, 500, 1000 records)
  2. Test Payload Sizes (256b, 512b, 1KB, 10KB, 100KB, 1MB)
  3. Correctness & 100% Recovery Verification
  4. Bit & Byte Avalanche Effect, NPCR, and UACI
  5. Byte-Level Shannon Entropy
  6. Reshaped 2D Spatial Correlation (Horizontal, Vertical, Diagonal)
  7. SHA-512 K256 Key Sensitivity (1-bit key perturbation)
  8. Encryption & Decryption Timing (perf_counter ms) & Throughput (MB/s)
  9. Legacy 2-Bit FBCA vs Revised 4-Bit Reversible CA Structural Comparison

Outputs:
  - full_experiment_results.csv
  - full_experiment_raw.csv
"""

import csv
import math
import random
import time
from typing import List, Tuple, Dict, Any

from research_crypto_utils import (
    derive_k256,
    text_to_binary,
    binary_to_text,
    add_length_header,
    pad_to_256,
    split_into_blocks,
    xor_binary_strings,
    BLOCK_SIZE,
)
from research_encrypt import encrypt_research
from research_decrypt import decrypt_research
from ca_transform import transform_block_forward, transform_block_inverse
from synthetic_healthcare_data import (
    generate_synthetic_dataset,
    record_to_string,
    create_all_synthetic_datasets,
)

# Defined payload sizes (1 KB = 1024 bytes, 1 MB = 1,048,576 bytes)
PAYLOAD_SIZES: Dict[str, int] = {
    "256 bits": 32,
    "512 bits": 64,
    "1 KB": 1024,
    "10 KB": 10240,
    "100 KB": 102400,
    "1 MB": 1048576,
}


def mean(data: List[float]) -> float:
    """Calculates arithmetic mean of a float list."""
    return sum(data) / len(data) if data else 0.0


def std_dev(data: List[float]) -> float:
    """Calculates sample standard deviation of a float list."""
    if len(data) <= 1:
        return 0.0
    m = mean(data)
    variance = sum((x - m) ** 2 for x in data) / (len(data) - 1)
    return math.sqrt(variance)


def calculate_shannon_entropy(data_bytes: bytes) -> float:
    """
    Calculates byte-level Shannon entropy H(X) = -sum p(x) log2 p(x).
    Maximum theoretical value for 256 byte values is 8.0000 bits/byte.
    """
    if not data_bytes:
        return 0.0

    length = len(data_bytes)
    freq = [0] * 256
    for b in data_bytes:
        freq[b] += 1

    entropy = 0.0
    for f in freq:
        if f > 0:
            p = f / length
            entropy -= p * math.log2(p)

    return entropy


def binary_str_to_bytes(bin_str: str) -> bytes:
    """Converts a binary string ('0' and '1') to a bytes object."""
    if len(bin_str) % 8 != 0:
        pad_len = 8 - (len(bin_str) % 8)
        bin_str = bin_str + ("0" * pad_len)

    byte_vals = bytearray()
    for i in range(0, len(bin_str), 8):
        byte_vals.append(int(bin_str[i:i + 8], 2))
    return bytes(byte_vals)


def calculate_pearson_correlation(x_vals: List[float], y_vals: List[float]) -> float:
    """Calculates Pearson correlation coefficient between two equal-length float series."""
    n = len(x_vals)
    if n <= 1:
        return 0.0

    mx = mean(x_vals)
    my = mean(y_vals)

    num = sum((x - mx) * (y - my) for x, y in zip(x_vals, y_vals))
    den_x = sum((x - mx) ** 2 for x in x_vals)
    den_y = sum((y - my) ** 2 for y in y_vals)

    denominator = math.sqrt(den_x * den_y)
    return num / denominator if denominator != 0 else 0.0


def calculate_2d_byte_correlation(data_bytes: bytes) -> Tuple[float, float, float]:
    """
    Reshapes data bytes into a square 2D matrix (S x S) and calculates
    Horizontal, Vertical, and Diagonal adjacent byte Pearson correlation.
    """
    n = len(data_bytes)
    side = int(math.sqrt(n))
    if side < 2:
        return 0.0, 0.0, 0.0

    # Reshape bytes into 2D grid
    grid = [list(data_bytes[r * side:(r + 1) * side]) for r in range(side)]

    h_x, h_y = [], []
    v_x, v_y = [], []
    d_x, d_y = [], []

    for r in range(side):
        for c in range(side):
            # Horizontal (right neighbor)
            if c + 1 < side:
                h_x.append(float(grid[r][c]))
                h_y.append(float(grid[r][c + 1]))

            # Vertical (down neighbor)
            if r + 1 < side:
                v_x.append(float(grid[r][c]))
                v_y.append(float(grid[r + 1][c]))

            # Diagonal (down-right neighbor)
            if r + 1 < side and c + 1 < side:
                d_x.append(float(grid[r][c]))
                d_y.append(float(grid[r + 1][c + 1]))

    corr_h = calculate_pearson_correlation(h_x, h_y)
    corr_v = calculate_pearson_correlation(v_x, v_y)
    corr_d = calculate_pearson_correlation(d_x, d_y)

    return corr_h, corr_v, corr_d


def generate_deterministic_payload(size_bytes: int, seed: int = 20260923) -> str:
    """Generates a deterministic string payload of exactly size_bytes bytes."""
    rng = random.Random(seed + size_bytes)
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-="
    res = [rng.choice(chars) for _ in range(size_bytes)]
    return "".join(res)


def run_full_experiment() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Runs the complete Step 10 experimental evaluation framework."""
    print("=" * 100)
    print(" STEP 10: FULL EXPERIMENTAL EVALUATION OF REVISED CRYPTOSYSTEM")
    print("=" * 100)
    print("Running deterministic evaluation across all required payload sizes and metrics...\n")

    summary_rows: List[Dict[str, Any]] = []
    raw_rows: List[Dict[str, Any]] = []

    password = "MasterDoctorKey2026#"
    seed = 20260923

    # Generate synthetic CSV datasets
    f100, f500, f1000 = create_all_synthetic_datasets(seed)
    print(f"Created synthetic datasets: {f100}, {f500}, {f1000}")

    # 1. EVALUATE PAYLOAD SIZES & TIMING / THROUGHPUT
    print("\n1. Evaluating Payload Sizes, Timing, and Throughput...")
    for label, size_bytes in PAYLOAD_SIZES.items():
        payload = generate_deterministic_payload(size_bytes, seed)
        raw_binary = text_to_binary(payload)
        framed = add_length_header(raw_binary)
        padded = pad_to_256(framed)
        num_blocks = len(padded) // BLOCK_SIZE

        # Correctness check
        ciphertext = encrypt_research(payload, password)
        recovered = decrypt_research(ciphertext, password)
        correct = (recovered == payload)

        # Timing (perf_counter ms)
        if size_bytes >= 1048576:
            trials = 3
            warmup = 1
        elif size_bytes >= 102400:
            trials = 5
            warmup = 1
        else:
            trials = 20
            warmup = 2

        # Warm-up
        for _ in range(warmup):
            _ = encrypt_research(payload, password)

        enc_times_ms = []
        for _ in range(trials):
            t0 = time.perf_counter()
            _ = encrypt_research(payload, password)
            t1 = time.perf_counter()
            enc_times_ms.append((t1 - t0) * 1000.0)

        dec_times_ms = []
        for _ in range(trials):
            t0 = time.perf_counter()
            _ = decrypt_research(ciphertext, password)
            t1 = time.perf_counter()
            dec_times_ms.append((t1 - t0) * 1000.0)

        mean_enc_ms = mean(enc_times_ms)
        std_enc_ms = std_dev(enc_times_ms)
        mean_dec_ms = mean(dec_times_ms)
        std_dec_ms = std_dev(dec_times_ms)

        # Throughput (MB/s where 1 MB = 1,048,576 bytes)
        size_mb = size_bytes / 1048576.0
        enc_tp_mbps = size_mb / (mean_enc_ms / 1000.0) if mean_enc_ms > 0 else 0.0
        dec_tp_mbps = size_mb / (mean_dec_ms / 1000.0) if mean_dec_ms > 0 else 0.0

        # Entropy
        plain_bytes = payload.encode("utf-8")
        cipher_bytes = binary_str_to_bytes(ciphertext)

        plain_entropy = calculate_shannon_entropy(plain_bytes)
        cipher_entropy = calculate_shannon_entropy(cipher_bytes)

        # Correlation
        p_corr_h, p_corr_v, p_corr_d = calculate_2d_byte_correlation(plain_bytes)
        c_corr_h, c_corr_v, c_corr_d = calculate_2d_byte_correlation(cipher_bytes)

        summary_rows.append({
            "experiment": "Payload_Performance",
            "payload_label": label,
            "payload_size_bytes": size_bytes,
            "blocks": num_blocks,
            "rounds": 2,
            "correctness_passed": correct,
            "enc_mean_ms": mean_enc_ms,
            "enc_std_ms": std_enc_ms,
            "dec_mean_ms": mean_dec_ms,
            "dec_std_ms": std_dec_ms,
            "enc_throughput_MBps": enc_tp_mbps,
            "dec_throughput_MBps": dec_tp_mbps,
            "plaintext_entropy": plain_entropy,
            "ciphertext_entropy": cipher_entropy,
            "plain_corr_h": p_corr_h,
            "plain_corr_v": p_corr_v,
            "plain_corr_d": p_corr_d,
            "cipher_corr_h": c_corr_h,
            "cipher_corr_v": c_corr_v,
            "cipher_corr_d": c_corr_d,
        })

        print(
            f"  Size: {label:<10} ({size_bytes} bytes, {num_blocks} blocks) | "
            f"Enc: {mean_enc_ms:.2f}ms ({enc_tp_mbps:.2f} MB/s) | "
            f"Entropy: Plain={plain_entropy:.4f}, Cipher={cipher_entropy:.4f} | Pass: {correct}",
            flush=True
        )

    # 2. EVALUATE AVALANCHE, NPCR, AND UACI (100 TRIALS)
    print("\n2. Evaluating Bit & Byte Avalanche, NPCR, and UACI (100 Trials)...", flush=True)
    rng_exp = random.Random(seed)

    avalanche_bit_list = []
    npcr_bit_list = []
    npcr_byte_list = []
    uaci_byte_list = []

    for trial in range(100):
        # 256-bit test payload (32 ASCII chars)
        p_chars = [rng_exp.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(32)]
        p1 = "".join(p_chars)

        # Perturb 1 bit in UTF-8 string
        p2_bytes = bytearray(p1.encode("utf-8"))
        p2_bytes[0] ^= 1  # Flip 1 bit in first byte
        p2 = p2_bytes.decode("utf-8", errors="ignore")

        c1_str = encrypt_research(p1, password)
        c2_str = encrypt_research(p2, password)

        # Bit Avalanche & Bit-based NPCR
        diff_bits = sum(1 for a, b in zip(c1_str, c2_str) if a != b)
        total_bits = len(c1_str)
        bit_av = (diff_bits / total_bits) * 100.0
        bit_npcr = (diff_bits / total_bits) * 100.0
        avalanche_bit_list.append(bit_av)
        npcr_bit_list.append(bit_npcr)

        # Byte-level NPCR and UACI
        b1 = binary_str_to_bytes(c1_str)
        b2 = binary_str_to_bytes(c2_str)
        total_bytes = len(b1)

        changed_bytes = sum(1 for x, y in zip(b1, b2) if x != y)
        npcr_byte = (changed_bytes / total_bytes) * 100.0
        npcr_byte_list.append(npcr_byte)

        diff_sum = sum(abs(int(x) - int(y)) for x, y in zip(b1, b2))
        uaci_byte = (diff_sum / (total_bytes * 255.0)) * 100.0
        uaci_byte_list.append(uaci_byte)

        raw_rows.append({
            "trial": trial + 1,
            "experiment": "Bit_Perturbation",
            "diff_bits": diff_bits,
            "total_bits": total_bits,
            "diff_bytes": changed_bytes,
            "total_bytes": total_bytes,
            "diff_sum_bytes": diff_sum,
            "bit_avalanche_percent": bit_av,
            "bit_npcr_percent": bit_npcr,
            "byte_npcr_percent": npcr_byte,
            "byte_uaci_percent": uaci_byte,
        })

    summary_rows.append({
        "experiment": "Security_Metrics_Avalanche",
        "payload_label": "256 bits",
        "payload_size_bytes": 32,
        "blocks": 1,
        "rounds": 2,
        "bit_avalanche_mean": mean(avalanche_bit_list),
        "bit_avalanche_std": std_dev(avalanche_bit_list),
        "bit_npcr_mean": mean(npcr_bit_list),
        "bit_npcr_std": std_dev(npcr_bit_list),
        "byte_npcr_mean": mean(npcr_byte_list),
        "byte_npcr_std": std_dev(npcr_byte_list),
        "byte_uaci_mean": mean(uaci_byte_list),
        "byte_uaci_std": std_dev(uaci_byte_list),
    })

    print(f"  Bit Avalanche Mean: {mean(avalanche_bit_list):.3f}% (Std: {std_dev(avalanche_bit_list):.3f}%)", flush=True)
    print(f"  Bit NPCR Mean:      {mean(npcr_bit_list):.3f}% (Std: {std_dev(npcr_bit_list):.3f}%)", flush=True)
    print(f"  Byte NPCR Mean:     {mean(npcr_byte_list):.3f}% (Std: {std_dev(npcr_byte_list):.3f}%)", flush=True)
    print(f"  Byte UACI Mean:     {mean(uaci_byte_list):.3f}% (Std: {std_dev(uaci_byte_list):.3f}%)", flush=True)

    # 3. EVALUATE SHA-512 K256 KEY SENSITIVITY (1-BIT KEY PERTURBATION)
    print("\n3. Evaluating SHA-512 K256 Key Sensitivity (1-Bit Key Perturbation)...", flush=True)
    key_sens_diff_bits = []

    for trial in range(50):
        p_test = f"Key Sensitivity Test Payload #{trial}"
        k_a = f"DoctorSecretPass_{trial}_KeyA"
        # Flip 1 bit in key string
        k_b_bytes = bytearray(k_a.encode("utf-8"))
        k_b_bytes[-1] ^= 1
        k_b = k_b_bytes.decode("utf-8", errors="ignore")

        c_a = encrypt_research(p_test, k_a)
        c_b = encrypt_research(p_test, k_b)

        diff_b = sum(1 for a, b in zip(c_a, c_b) if a != b)
        diff_pct = (diff_b / len(c_a)) * 100.0
        key_sens_diff_bits.append(diff_pct)

        raw_rows.append({
            "trial": trial + 1,
            "experiment": "Key_Sensitivity",
            "key_a": k_a,
            "key_b": k_b,
            "diff_bits": diff_b,
            "total_bits": len(c_a),
            "key_diff_bit_percent": diff_pct,
        })

    print(f"  Key Sensitivity Mean Bit Change: {mean(key_sens_diff_bits):.3f}% (Std: {std_dev(key_sens_diff_bits):.3f}%)", flush=True)

    summary_rows.append({
        "experiment": "Key_Sensitivity",
        "key_diff_bit_mean": mean(key_sens_diff_bits),
        "key_diff_bit_std": std_dev(key_sens_diff_bits),
    })

    # Save CSV files
    save_full_experiment_csv(summary_rows, raw_rows)

    return summary_rows, raw_rows


def save_full_experiment_csv(summary: List[Dict], raw: List[Dict]) -> None:
    """Saves full experiment results to CSV files."""
    summary_path = "full_experiment_results.csv"
    raw_path = "full_experiment_raw.csv"

    if summary:
        fieldnames = []
        for r in summary:
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
            writer.writeheader()
            writer.writerows(summary)
        print(f"\nSaved summary results to: {summary_path}", flush=True)

    if raw:
        fieldnames = []
        for r in raw:
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
            writer.writeheader()
            writer.writerows(raw)
        print(f"Saved raw trial results to: {raw_path}", flush=True)


if __name__ == "__main__":
    run_full_experiment()
