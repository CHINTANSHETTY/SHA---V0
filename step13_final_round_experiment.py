"""
Module: step13_final_round_experiment.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Step 13 final candidate C round-count evaluation for R in {2, 4, 6, 8, 10}
         (with R=16 as observation only) under strict project constraints.

Candidate C Pipeline Specification:
  Forward:
    - Odd rounds: Standard 2x2 Margolus partition (apply_margolus_forward)
    - Even rounds: Shifted 2x2 Margolus partition (apply_shifted_margolus_forward)
    - Circular matrix shift DOWN 2 and RIGHT 2 after EVERY CA round (circular_shift_matrix row_shift=2, col_shift=2)
  Inverse:
    - Reverse rounds loop (R..1)
    - Inverse circular matrix shift UP 2 and LEFT 2 (inverse_circular_shift_matrix row_shift=2, col_shift=2)
    - Corresponding inverse Margolus partition for the round

IMPORTANT:
  - Production crypto files and paper files are NOT modified.
  - No prohibited primitives (AES, HKDF, HMAC, AEAD, nonce, salt, etc.) added.
  - No subjective/promotional language ("secure", "optimal", "best") used.
"""

import csv
import math
import random
import time
from typing import List, Tuple, Dict, Any, Callable

from ca_matrix import (
    block_to_matrix,
    matrix_to_block,
    MATRIX_ROWS,
    MATRIX_COLS,
    BLOCK_SIZE,
)
from margolus_ca import (
    apply_margolus_forward,
    apply_margolus_inverse,
)
from margolus_shifted import (
    apply_shifted_margolus_forward,
    apply_shifted_margolus_inverse,
)
from ca_transform import (
    circular_shift_matrix,
    inverse_circular_shift_matrix,
)
from research_crypto_utils import (
    derive_k256,
    text_to_binary,
    binary_to_text,
    add_length_header,
    extract_with_length_header,
    pad_to_256,
    split_into_blocks,
    xor_binary_strings,
)
from synthetic_healthcare_data import (
    generate_synthetic_dataset,
    record_to_string,
)


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


# ==============================================================================
# 1. CANDIDATE C FORWARD & INVERSE TRANSFORMATIONS
# ==============================================================================

def candidate_C_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Candidate C Forward Transformation:
      For each round r (1..rounds):
        1. Apply standard Margolus partition on odd rounds.
        2. Apply shifted Margolus partition on even rounds.
        3. Apply circular matrix shift DOWN 2 and RIGHT 2 after EVERY round.
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
        m = circular_shift_matrix(m, row_shift=2, col_shift=2)
    return m


def candidate_C_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Candidate C Inverse Transformation:
      For each round r in reverse (rounds..1):
        1. Apply inverse circular matrix shift UP 2 and LEFT 2.
        2. Apply corresponding inverse Margolus partition.
    """
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        m = inverse_circular_shift_matrix(m, row_shift=2, col_shift=2)
        if r % 2 != 0:
            m = apply_margolus_inverse(m)
        else:
            m = apply_shifted_margolus_inverse(m)
    return m


# ==============================================================================
# 2. END-TO-END HEALTHCARE APPLICATION PIPELINE SIMULATOR
# ==============================================================================

def candidate_C_encrypt_text(plaintext: str, password: str, rounds: int) -> str:
    """Simulates Candidate C Healthcare Application Encryption."""
    k256 = derive_k256(password)
    raw_bin = text_to_binary(plaintext)
    framed_bin = add_length_header(raw_bin)
    padded_bin = pad_to_256(framed_bin)
    blocks = split_into_blocks(padded_bin, BLOCK_SIZE)

    cipher_blocks = []
    for blk in blocks:
        m0 = block_to_matrix(blk)
        m_r = candidate_C_forward(m0, rounds)
        b_ca = matrix_to_block(m_r)
        c_blk = xor_binary_strings(b_ca, k256)
        cipher_blocks.append(c_blk)

    return "".join(cipher_blocks)


def candidate_C_decrypt_text(ciphertext: str, password: str, rounds: int) -> str:
    """Simulates Candidate C Healthcare Application Decryption."""
    k256 = derive_k256(password)
    blocks = split_into_blocks(ciphertext, BLOCK_SIZE)

    dec_blocks = []
    for c_blk in blocks:
        b_ca = xor_binary_strings(c_blk, k256)
        m_r = block_to_matrix(b_ca)
        m0 = candidate_C_inverse(m_r, rounds)
        b_dec = matrix_to_block(m0)
        dec_blocks.append(b_dec)

    padded_bin = "".join(dec_blocks)
    framed_bin = extract_with_length_header(padded_bin)
    return binary_to_text(framed_bin)


def test_candidate_C_healthcare_pipeline(rounds: int) -> bool:
    """
    Validates Healthcare Application Pipeline recovery for Candidate C across:
      1. Ordinary ASCII text
      2. Unicode healthcare text (e.g. °C, Müller)
      3. Multi-block healthcare record (>500 chars)
      4. 100 Synthetic Healthcare Records
    """
    password = "HospitalDoctorPassword2026#"

    test_cases = [
        "PatientID=P001;Age=45;Gender=F;BP=120/80;Diagnosis=Diabetes",
        "PatientID=P002;Doctor=Dr. Müller;Diagnosis=Cardiomyopathy;Note=Patient feel 75% better; Temp=36.6°C",
        "MultiBlockRecord: " + ("B" * 500) + ";Medication=Metformin;Date=2026-09-23",
    ]

    for tc in test_cases:
        c_str = candidate_C_encrypt_text(tc, password, rounds)
        rec_str = candidate_C_decrypt_text(c_str, password, rounds)
        if rec_str != tc:
            return False

    records = generate_synthetic_dataset(100, seed=20260923)
    for rec in records:
        rec_str = record_to_string(rec)
        c_str = candidate_C_encrypt_text(rec_str, password, rounds)
        rec_str = candidate_C_decrypt_text(c_str, password, rounds)
        if rec_str != rec_str:
            return False

    return True


# ==============================================================================
# 3. RUN STEP 13 EXPERIMENT
# ==============================================================================

def run_step13_experiment() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Runs Step 13 Candidate C final round-count evaluation for R in {2, 4, 6, 8, 10} and R=16."""
    print("=" * 100)
    print(" STEP 13: FINAL CANDIDATE C ROUND-COUNT EXPERIMENT (R = 2, 4, 6, 8, 10)")
    print("=" * 100)

    trials = 100
    seed = 20260923
    rng = random.Random(seed)
    password = "MasterDoctorKey2026#"
    k256 = derive_k256(password)

    # Construct identical 100 256-bit plaintext test pairs
    test_pairs = []
    for _ in range(trials):
        p1_bits = [rng.choice(["0", "1"]) for _ in range(256)]
        p1 = "".join(p1_bits)
        p2_bits = list(p1_bits)
        flip_idx = rng.randint(0, 255)
        p2_bits[flip_idx] = "1" if p1_bits[flip_idx] == "0" else "0"
        p2 = "".join(p2_bits)
        test_pairs.append((p1, p2))

    summary_rows: List[Dict[str, Any]] = []
    raw_rows: List[Dict[str, Any]] = []

    required_rounds = [2, 4, 6, 8, 10]
    observation_rounds = [16]
    all_rounds = required_rounds + observation_rounds

    print("\nEvaluating Candidate C across round counts R in {2, 4, 6, 8, 10} (and R=16 observation)...")

    for r in all_rounds:
        # A. Reversibility Test
        rev_count = 0
        for p1, _ in test_pairs:
            m0 = block_to_matrix(p1)
            m_r = candidate_C_forward(m0, r)
            m_rec = candidate_C_inverse(m_r, r)
            if matrix_to_block(m_rec) == p1:
                rev_count += 1
        rev_passed = (rev_count == trials)
        rev_pct = (rev_count / float(trials)) * 100.0

        # Healthcare Pipeline Validation
        hc_passed = test_candidate_C_healthcare_pipeline(r)

        # B-F. Diffusion Metrics
        changed_bits_list = []
        avalanche_list = []
        bit_npcr_list = []
        byte_npcr_list = []
        byte_uaci_list = []

        for trial_idx, (p1, p2) in enumerate(test_pairs):
            m1_0 = block_to_matrix(p1)
            m2_0 = block_to_matrix(p2)

            m1_r = candidate_C_forward(m1_0, r)
            m2_r = candidate_C_forward(m2_0, r)

            b1_ca = matrix_to_block(m1_r)
            b2_ca = matrix_to_block(m2_r)

            c1 = xor_binary_strings(b1_ca, k256)
            c2 = xor_binary_strings(b2_ca, k256)

            diff_b = sum(1 for a, b in zip(c1, c2) if a != b)
            bit_av = (diff_b / 256.0) * 100.0
            bit_npcr = (diff_b / 256.0) * 100.0

            b1_bytes = bytes([int(c1[i:i+8], 2) for i in range(0, 256, 8)])
            b2_bytes = bytes([int(c2[i:i+8], 2) for i in range(0, 256, 8)])

            diff_bytes = sum(1 for x, y in zip(b1_bytes, b2_bytes) if x != y)
            byte_npcr = (diff_bytes / 32.0) * 100.0

            diff_sum = sum(abs(int(x) - int(y)) for x, y in zip(b1_bytes, b2_bytes))
            byte_uaci = (diff_sum / (32.0 * 255.0)) * 100.0

            changed_bits_list.append(float(diff_b))
            avalanche_list.append(bit_av)
            bit_npcr_list.append(bit_npcr)
            byte_npcr_list.append(byte_npcr)
            byte_uaci_list.append(byte_uaci)

            raw_rows.append({
                "trial": trial_idx + 1,
                "rounds": r,
                "diff_bits": diff_b,
                "bit_avalanche_percent": bit_av,
                "bit_npcr_percent": bit_npcr,
                "byte_npcr_percent": byte_npcr,
                "byte_uaci_percent": byte_uaci,
            })

        # G. Timing (perf_counter ms)
        # Warm-up
        for p1, _ in test_pairs[:2]:
            _ = candidate_C_forward(block_to_matrix(p1), r)

        times_ms = []
        for p1, _ in test_pairs[:20]:
            m0 = block_to_matrix(p1)
            t0 = time.perf_counter()
            _ = candidate_C_forward(m0, r)
            t1 = time.perf_counter()
            times_ms.append((t1 - t0) * 1000.0)

        mean_t = mean(times_ms)
        std_t = std_dev(times_ms)

        mean_cb = mean(changed_bits_list)
        min_cb = min(changed_bits_list)
        max_cb = max(changed_bits_list)
        std_cb = std_dev(changed_bits_list)

        mean_av = mean(avalanche_list)
        mean_bit_npcr = mean(bit_npcr_list)
        mean_byte_npcr = mean(byte_npcr_list)
        mean_byte_uaci = mean(byte_uaci_list)

        is_observation = (r not in required_rounds)

        summary_rows.append({
            "candidate": "Candidate_C",
            "rounds": r,
            "is_observation_only": is_observation,
            "changed_bits_mean": mean_cb,
            "changed_bits_min": min_cb,
            "changed_bits_max": max_cb,
            "changed_bits_std": std_cb,
            "bit_avalanche_mean": mean_av,
            "bit_npcr_mean": mean_bit_npcr,
            "byte_npcr_mean": mean_byte_npcr,
            "byte_uaci_mean": mean_byte_uaci,
            "enc_time_ms_mean": mean_t,
            "enc_time_ms_std": std_t,
            "reversibility_pass_percent": rev_pct,
            "healthcare_pipeline_pass": hc_passed,
        })

        obs_tag = " (Observation Only)" if is_observation else ""
        print(
            f"  Rounds: {r:2d}{obs_tag:<18} | Changed Bits: {mean_cb:5.2f} (Min: {min_cb:2.0f}, Max: {max_cb:3.0f}, Std: {std_cb:4.2f}) | "
            f"Avalanche: {mean_av:5.2f}% | Byte NPCR: {mean_byte_npcr:5.2f}% | Byte UACI: {mean_byte_uaci:5.2f}% | "
            f"Time: {mean_t:.3f}ms | Rev: {rev_pct:.0f}%",
            flush=True
        )

    # Save Output CSV Files
    save_step13_csv(summary_rows, raw_rows)

    return summary_rows, raw_rows


def save_step13_csv(summary_rows: List[Dict], raw_rows: List[Dict]) -> None:
    """Saves Step 13 final round-count evaluation results to CSV files."""
    summary_path = "step13_final_round_results.csv"
    raw_path = "step13_final_round_raw.csv"

    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nSaved Step 13 summary results to: {summary_path}", flush=True)

    if raw_rows:
        fieldnames = list(raw_rows[0].keys())
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(raw_rows)
        print(f"Saved Step 13 raw trial results to: {raw_path}", flush=True)


if __name__ == "__main__":
    run_step13_experiment()
