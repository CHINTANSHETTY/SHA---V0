"""
Module: step12_architecture_validation.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Step 12 controlled architecture validation comparing Candidate A, B, C, D
         across round counts R in {2, 4, 6, 8, 10, 16} under strict project constraints.

Candidates Evaluated:
  - Candidate A: Current production architecture (Alternating Margolus + Shift (1,1) per round)
  - Candidate B: Alternating Margolus partitions WITHOUT extra matrix shift
  - Candidate C: Alternating Margolus partitions WITH Shift (2,2) per round
  - Candidate D: Alternating Margolus partitions WITH Shift (1,1) after every 2-round pair

IMPORTANT:
  - Production code path and paper are NOT modified.
  - No prohibited algorithms (AES, HKDF, HMAC, AEAD, nonce, salt, etc.) added.
  - All tested candidate architectures have explicit, mathematically exact inverse functions.
  - No winner is declared or hardcoded in code.
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
# 1. CANDIDATE ARCHITECTURES (A, B, C, D) FORWARD & INVERSE DEFINITIONS
# ==============================================================================

# --- CANDIDATE A: Production Architecture ---
def candidate_A_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate A Forward: Margolus Partition + Circular Shift (1,1) after EVERY round."""
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
        m = circular_shift_matrix(m, row_shift=1, col_shift=1)
    return m


def candidate_A_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate A Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        m = inverse_circular_shift_matrix(m, row_shift=1, col_shift=1)
        if r % 2 != 0:
            m = apply_margolus_inverse(m)
        else:
            m = apply_shifted_margolus_inverse(m)
    return m


# --- CANDIDATE B: Pure Alternating Partitions (No Shift) ---
def candidate_B_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate B Forward: Alternating Margolus Partitions WITHOUT extra matrix shift."""
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
    return m


def candidate_B_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate B Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        if r % 2 == 0:
            m = apply_shifted_margolus_inverse(m)
        else:
            m = apply_margolus_inverse(m)
    return m


# --- CANDIDATE C: Alternating Partitions with Circular Shift (2,2) ---
def candidate_C_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate C Forward: Alternating Margolus Partitions WITH Circular Shift (2,2) after EVERY round."""
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
        m = circular_shift_matrix(m, row_shift=2, col_shift=2)
    return m


def candidate_C_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate C Inverse: Inverse Circular Shift (2,2 UP/LEFT) -> Inverse Margolus Partition."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        m = inverse_circular_shift_matrix(m, row_shift=2, col_shift=2)
        if r % 2 != 0:
            m = apply_margolus_inverse(m)
        else:
            m = apply_shifted_margolus_inverse(m)
    return m


# --- CANDIDATE D: Shift (1,1) Only After Every 2-Round Partition Pair ---
def candidate_D_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Candidate D Forward:
      Standard Margolus (R1) -> Shifted Margolus (R2) -> Circular Shift (1,1) AFTER every 2 rounds.
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
            m = circular_shift_matrix(m, row_shift=1, col_shift=1)
    return m


def candidate_D_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Candidate D Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        if r % 2 == 0:
            m = inverse_circular_shift_matrix(m, row_shift=1, col_shift=1)
            m = apply_shifted_margolus_inverse(m)
        else:
            m = apply_margolus_inverse(m)
    return m


CANDIDATES: Dict[str, Tuple[Callable, Callable, str]] = {
    "Candidate_A": (
        candidate_A_forward,
        candidate_A_inverse,
        "Production Pipeline: Alternating Margolus + Shift (1,1) Per Round"
    ),
    "Candidate_B": (
        candidate_B_forward,
        candidate_B_inverse,
        "Alternating Partitions Without Extra Matrix Shift"
    ),
    "Candidate_C": (
        candidate_C_forward,
        candidate_C_inverse,
        "Alternating Partitions + Circular Shift (2,2) Per Round"
    ),
    "Candidate_D": (
        candidate_D_forward,
        candidate_D_inverse,
        "Alternating Partitions + Shift (1,1) After Every 2 Rounds"
    ),
}


# ==============================================================================
# 2. VERIFICATION ROUTINES (CIRCULAR SHIFT & SCHEDULE PRINTING)
# ==============================================================================

def verify_candidate_C_circular_shift() -> bool:
    """
    Verifies that Candidate C's forward shift (DOWN 2, RIGHT 2) and inverse shift (UP 2, LEFT 2)
    are exact 2D circular matrix shifts on a 16x16 grid.
    """
    rng = random.Random(20260923)
    grid = [[rng.randint(0, 1) for _ in range(16)] for _ in range(16)]
    
    shifted = circular_shift_matrix(grid, row_shift=2, col_shift=2)
    restored = inverse_circular_shift_matrix(shifted, row_shift=2, col_shift=2)

    return grid == restored


def get_candidate_D_schedule_sequence(rounds: int = 4) -> List[str]:
    """Returns the explicit mathematical sequence of CA partition and shift operations for Candidate D."""
    seq = []
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            seq.append(f"Round {r}: Standard Margolus 2x2 Partition")
        else:
            seq.append(f"Round {r}: Shifted Margolus 2x2 Partition")
            seq.append(f"Post-Round {r}: Circular Matrix Shift (DOWN 1, RIGHT 1)")
    return seq


# ==============================================================================
# 3. END-TO-END HEALTHCARE APPLICATION PIPELINE SIMULATOR
# ==============================================================================

def simulate_pipeline_encrypt(
    plaintext: str,
    password: str,
    fwd_fn: Callable,
    rounds: int
) -> str:
    """Simulates Healthcare Application Encryption Pipeline for any candidate CA architecture."""
    k256 = derive_k256(password)
    raw_bin = text_to_binary(plaintext)
    framed_bin = add_length_header(raw_bin)
    padded_bin = pad_to_256(framed_bin)
    blocks = split_into_blocks(padded_bin, BLOCK_SIZE)

    cipher_blocks = []
    for blk in blocks:
        m0 = block_to_matrix(blk)
        m_r = fwd_fn(m0, rounds)
        b_ca = matrix_to_block(m_r)
        c_blk = xor_binary_strings(b_ca, k256)
        cipher_blocks.append(c_blk)

    return "".join(cipher_blocks)


def simulate_pipeline_decrypt(
    ciphertext: str,
    password: str,
    inv_fn: Callable,
    rounds: int
) -> str:
    """Simulates Healthcare Application Decryption Pipeline for any candidate CA architecture."""
    k256 = derive_k256(password)
    blocks = split_into_blocks(ciphertext, BLOCK_SIZE)

    dec_blocks = []
    for c_blk in blocks:
        b_ca = xor_binary_strings(c_blk, k256)
        m_r = block_to_matrix(b_ca)
        m0 = inv_fn(m_r, rounds)
        b_dec = matrix_to_block(m0)
        dec_blocks.append(b_dec)

    padded_bin = "".join(dec_blocks)
    framed_bin = extract_with_length_header(padded_bin)
    return binary_to_text(framed_bin)


def test_healthcare_pipeline_recovery(
    fwd_fn: Callable,
    inv_fn: Callable,
    rounds: int
) -> bool:
    """
    Tests end-to-end Healthcare Application Pipeline recovery across:
      1. Ordinary Healthcare Text
      2. Unicode Healthcare Text
      3. Multi-Block Healthcare Text
      4. 100 Synthetic Healthcare Records
    """
    password = "MasterDoctorKey2026#"

    test_cases = [
        "PatientID=P001;Age=45;Gender=F;BP=120/80;Diagnosis=Diabetes",
        "PatientID=P002;Doctor=Dr. Müller;Diagnosis=Cardiomyopathy;Note=Patient feel 75% better; Temp=36.6°C",
        "MultiBlockRecord: " + ("A" * 500) + ";Medication=Metformin;Date=2026-09-23",
    ]

    for tc in test_cases:
        c_text = simulate_pipeline_encrypt(tc, password, fwd_fn, rounds)
        rec_text = simulate_pipeline_decrypt(c_text, password, inv_fn, rounds)
        if rec_text != tc:
            return False

    # Test 100 Synthetic Records
    records = generate_synthetic_dataset(100, seed=20260923)
    for rec in records:
        rec_str = record_to_string(rec)
        c_text = simulate_pipeline_encrypt(rec_str, password, fwd_fn, rounds)
        rec_text = simulate_pipeline_decrypt(c_text, password, inv_fn, rounds)
        if rec_text != rec_str:
            return False

    return True


# ==============================================================================
# 4. STEP 12 FULL EXPERIMENTAL EVALUATION
# ==============================================================================

def run_step12_validation() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Runs Step 12 controlled architecture validation and metrics evaluation."""
    print("=" * 100)
    print(" STEP 12: FINAL ARCHITECTURE VALIDATION UNDER PROJECT CONSTRAINTS")
    print("=" * 100)

    # 1. Circular Shift & Candidate Schedule Sequence Verification
    print("\n1. Verifying Candidate C Circular Shift & Candidate D Schedule Sequence...")
    c_shift_valid = verify_candidate_C_circular_shift()
    print(f"  Candidate C 2D Circular Shift (DOWN 2/RIGHT 2 <-> UP 2/LEFT 2): {'PASS' if c_shift_valid else 'FAIL'}")

    cand_d_seq = get_candidate_D_schedule_sequence(rounds=4)
    print("  Candidate D Explicit Schedule Sequence (R=4):")
    for step in cand_d_seq:
        print(f"    - {step}")

    # 2. Identical Test Inputs Construction
    trials = 100
    seed = 20260923
    rng = random.Random(seed)
    password = "MasterDoctorKey2026#"
    k256 = derive_k256(password)

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
    round_counts = [2, 4, 6, 8, 10, 16]

    # 3. Evaluate Candidates A, B, C, D across Rounds
    print("\n2. Evaluating Reversibility, Diffusion, and Performance across Candidates A-D...")

    for cand_name, (fwd_fn, inv_fn, desc) in CANDIDATES.items():
        print(f"\n--- {cand_name}: {desc} ---")

        for r in round_counts:
            # Reversibility test over 100 blocks
            rev_passed = True
            for p1, _ in test_pairs:
                m0 = block_to_matrix(p1)
                m_r = fwd_fn(m0, r)
                m_rec = inv_fn(m_r, r)
                if matrix_to_block(m_rec) != p1:
                    rev_passed = False
                    break

            # Healthcare pipeline recovery test
            hc_passed = test_healthcare_pipeline_recovery(fwd_fn, inv_fn, r)

            # Diffusion metrics
            avalanche_list = []
            bit_npcr_list = []
            byte_npcr_list = []
            byte_uaci_list = []

            for p1, p2 in test_pairs:
                m1_0 = block_to_matrix(p1)
                m2_0 = block_to_matrix(p2)

                m1_r = fwd_fn(m1_0, r)
                m2_r = fwd_fn(m2_0, r)

                b1_ca = matrix_to_block(m1_r)
                b2_ca = matrix_to_block(m2_r)

                c1 = xor_binary_strings(b1_ca, k256)
                c2 = xor_binary_strings(b2_ca, k256)

                diff_bits = sum(1 for a, b in zip(c1, c2) if a != b)
                bit_av = (diff_bits / 256.0) * 100.0
                bit_npcr = (diff_bits / 256.0) * 100.0

                b1_bytes = bytes([int(c1[i:i+8], 2) for i in range(0, 256, 8)])
                b2_bytes = bytes([int(c2[i:i+8], 2) for i in range(0, 256, 8)])

                diff_bytes = sum(1 for x, y in zip(b1_bytes, b2_bytes) if x != y)
                byte_npcr = (diff_bytes / 32.0) * 100.0

                diff_sum = sum(abs(int(x) - int(y)) for x, y in zip(b1_bytes, b2_bytes))
                byte_uaci = (diff_sum / (32.0 * 255.0)) * 100.0

                avalanche_list.append(bit_av)
                bit_npcr_list.append(bit_npcr)
                byte_npcr_list.append(byte_npcr)
                byte_uaci_list.append(byte_uaci)

            # Timing (perf_counter ms for 256-bit block encryption)
            times_ms = []
            for p1, _ in test_pairs[:20]:
                m0 = block_to_matrix(p1)
                t0 = time.perf_counter()
                _ = fwd_fn(m0, r)
                t1 = time.perf_counter()
                times_ms.append((t1 - t0) * 1000.0)

            mean_t = mean(times_ms)
            std_t = std_dev(times_ms)

            mean_av = mean(avalanche_list)
            mean_bit_npcr = mean(bit_npcr_list)
            mean_byte_npcr = mean(byte_npcr_list)
            mean_byte_uaci = mean(byte_uaci_list)
            mean_bits_changed = mean_av * 2.56

            summary_rows.append({
                "candidate": cand_name,
                "rounds": r,
                "changed_bits_mean": mean_bits_changed,
                "bit_avalanche_mean": mean_av,
                "bit_npcr_mean": mean_bit_npcr,
                "byte_npcr_mean": mean_byte_npcr,
                "byte_uaci_mean": mean_byte_uaci,
                "encryption_time_ms": mean_t,
                "std_time_ms": std_t,
                "reversibility_pass": rev_passed,
                "healthcare_recovery_pass": hc_passed,
            })

            print(
                f"  Rounds: {r:2d} | Bits Changed: {mean_bits_changed:5.2f} / 256 | "
                f"Avalanche: {mean_av:5.2f}% | Byte NPCR: {mean_byte_npcr:5.2f}% | "
                f"Byte UACI: {mean_byte_uaci:5.2f}% | Time: {mean_t:.3f}ms | "
                f"Reversibility: {'PASS' if rev_passed else 'FAIL'}",
                flush=True
            )

    # 4. Save Output CSV Files
    save_step12_csv(summary_rows, raw_rows)

    return summary_rows, raw_rows


def save_step12_csv(summary_rows: List[Dict], raw_rows: List[Dict]) -> None:
    """Saves Step 12 validation results to CSV files."""
    summary_path = "step12_architecture_results.csv"
    raw_path = "step12_architecture_raw.csv"

    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nSaved Step 12 architecture results to: {summary_path}", flush=True)

    if raw_rows:
        fieldnames = list(raw_rows[0].keys())
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(raw_rows)
        print(f"Saved Step 12 raw trial results to: {raw_path}", flush=True)


if __name__ == "__main__":
    run_step12_validation()
