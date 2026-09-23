"""
Module: ca_round_experiment.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Generalized experimental framework to evaluate 2, 4, 6, 8, and 10 CA rounds.

Calculates:
  1. Bit Avalanche Effect (%)
  2. Bit-based NPCR (%)
  3. Bit-based UACI (%)
  4. Precise timing metrics (mean & std dev in ms via time.perf_counter)
  5. 100% Reversibility verification per round count

Outputs:
  - ca_round_experiment_results.csv
  - ca_round_experiment_raw.csv
"""

import csv
import math
import random
import time
from typing import List, Tuple, Dict

from ca_matrix import (
    block_to_matrix,
    matrix_to_block,
    validate_matrix,
    validate_block,
    MATRIX_ROWS,
    MATRIX_COLS,
    BLOCK_SIZE,
)
from ca_transform import circular_shift_matrix, inverse_circular_shift_matrix
from margolus_ca import apply_margolus_forward, apply_margolus_inverse
from margolus_shifted import apply_shifted_margolus_forward, apply_shifted_margolus_inverse

VALID_ROUND_COUNTS: Tuple[int, ...] = (2, 4, 6, 8, 10)


def apply_ca_round(matrix: List[List[int]], round_number: int) -> List[List[int]]:
    """
    Applies a single CA round to a 16x16 matrix using alternating Margolus partitions:
      - Odd round  (1, 3, 5, ...): Normal/non-shifted 2x2 Margolus partition
      - Even round (2, 4, 6, ...): Shifted 2x2 Margolus partition (modulo 16)
    """
    if round_number % 2 != 0:
        return apply_margolus_forward(matrix)
    else:
        return apply_shifted_margolus_forward(matrix)


def apply_ca_round_inverse(matrix: List[List[int]], round_number: int) -> List[List[int]]:
    """
    Reverses a single CA round for a 16x16 matrix:
      - Odd round  (1, 3, 5, ...): Inverse normal/non-shifted Margolus partition
      - Even round (2, 4, 6, ...): Inverse shifted Margolus partition
    """
    if round_number % 2 != 0:
        return apply_margolus_inverse(matrix)
    else:
        return apply_shifted_margolus_inverse(matrix)


def apply_ca_rounds(
    matrix: List[List[int]],
    rounds: int,
    include_final_shift: bool = False
) -> List[List[int]]:
    """
    Applies requested number of CA rounds to a 16x16 matrix with 2D circular matrix shift (DOWN 1, RIGHT 1)
    between successive rounds.

    Args:
        matrix: 16x16 binary integer matrix.
        rounds: Number of rounds (must be in VALID_ROUND_COUNTS: 2, 4, 6, 8, 10).
        include_final_shift: If True, applies circular shift after the final round.
                             Default False matches the validated 2-round pipeline.

    Returns:
        Transformed 16x16 matrix.
    """
    validate_matrix(matrix)

    if rounds not in VALID_ROUND_COUNTS:
        raise ValueError(
            f"Invalid round count {rounds}. Must be one of {VALID_ROUND_COUNTS}."
        )

    curr_matrix = [row[:] for row in matrix]

    for k in range(1, rounds + 1):
        curr_matrix = apply_ca_round(curr_matrix, k)
        if k < rounds or include_final_shift:
            curr_matrix = circular_shift_matrix(curr_matrix, row_shift=1, col_shift=1)

    return curr_matrix


def apply_ca_rounds_inverse(
    matrix: List[List[int]],
    rounds: int,
    include_final_shift: bool = False
) -> List[List[int]]:
    """
    Reverses requested number of CA rounds for a 16x16 matrix in exact reverse order.

    Args:
        matrix: Transformed 16x16 binary integer matrix.
        rounds: Number of rounds (must be in VALID_ROUND_COUNTS: 2, 4, 6, 8, 10).
        include_final_shift: Must match value used during forward transformation.

    Returns:
        Original 16x16 matrix.
    """
    validate_matrix(matrix)

    if rounds not in VALID_ROUND_COUNTS:
        raise ValueError(
            f"Invalid round count {rounds}. Must be one of {VALID_ROUND_COUNTS}."
        )

    curr_matrix = [row[:] for row in matrix]

    for k in range(rounds, 0, -1):
        if k < rounds or include_final_shift:
            curr_matrix = inverse_circular_shift_matrix(curr_matrix, row_shift=1, col_shift=1)
        curr_matrix = apply_ca_round_inverse(curr_matrix, k)

    return curr_matrix


def transform_block_with_rounds(
    block: str,
    rounds: int,
    include_final_shift: bool = False
) -> str:
    """
    Applies forward CA transformation for requested round count to a 256-bit block string.
    """
    validate_block(block)
    m0 = block_to_matrix(block)
    m1 = apply_ca_rounds(m0, rounds, include_final_shift)
    return matrix_to_block(m1)


def inverse_transform_block_with_rounds(
    block: str,
    rounds: int,
    include_final_shift: bool = False
) -> str:
    """
    Applies inverse CA transformation for requested round count to a 256-bit block string.
    """
    validate_block(block)
    m1 = block_to_matrix(block)
    m0 = apply_ca_rounds_inverse(m1, rounds, include_final_shift)
    return matrix_to_block(m0)


# =========================================================
# EXPERIMENTAL CRYPTOGRAPHIC METRICS (BIT-BASED)
# =========================================================

def calculate_hamming_distance(str1: str, str2: str) -> int:
    """Calculates bit Hamming distance between two equal-length binary strings."""
    if len(str1) != len(str2):
        raise ValueError("Strings must be of equal length for Hamming distance.")
    return sum(1 for a, b in zip(str1, str2) if a != b)


def calculate_bit_avalanche(c1: str, c2: str) -> float:
    """
    Calculates Bit Avalanche Effect percentage:
      Avalanche (%) = HammingDistance(C1, C2) / 256 * 100
    """
    dist = calculate_hamming_distance(c1, c2)
    return (dist / BLOCK_SIZE) * 100.0


def calculate_bit_npcr(c1: str, c2: str) -> float:
    """
    Calculates Bit-Based NPCR (Number of Pixels/Bits Change Rate) percentage:
      NPCR (%) = Changed Bits / 256 * 100
    """
    return calculate_bit_avalanche(c1, c2)


def calculate_bit_uaci(c1: str, c2: str) -> float:
    """
    Calculates Bit-Based UACI (Unified Average Changing Intensity) percentage:
      UACI (%) = sum(|c1_i - c2_i|) / (256 * 1) * 100
    For binary string values, this is mathematically identical to the bit change rate.
    """
    diff_sum = sum(abs(int(a) - int(b)) for a, b in zip(c1, c2))
    return (diff_sum / BLOCK_SIZE) * 100.0


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


def run_experiment(
    num_blocks: int = 100,
    seed: int = 20260923,
    timing_trials: int = 100
) -> Tuple[List[Dict], List[Dict]]:
    """
    Executes the CA round-count experiment across 2, 4, 6, 8, and 10 rounds.

    Args:
        num_blocks: Number of random 256-bit test blocks (default 100).
        seed: Fixed random seed for 100% reproducibility.
        timing_trials: Number of repetitions for execution timing.

    Returns:
        (summary_results, raw_trial_results)
    """
    print("=" * 100)
    print(" CA ROUND-COUNT EXPERIMENTAL FRAMEWORK EXECUTION")
    print("=" * 100)
    print(f"Test Parameters: Seed={seed}, Blocks={num_blocks}, Round Counts={VALID_ROUND_COUNTS}\n")

    random.seed(seed)

    # 1. Generate deterministic test blocks and flipped-bit pairs
    test_pairs = []
    for _ in range(num_blocks):
        b_bits = [str(random.randint(0, 1)) for _ in range(BLOCK_SIZE)]
        block = "".join(b_bits)

        # Flip exactly 1 bit at a random index
        flip_idx = random.randint(0, BLOCK_SIZE - 1)
        b_prime_bits = b_bits[:]
        b_prime_bits[flip_idx] = "1" if b_bits[flip_idx] == "0" else "0"
        block_prime = "".join(b_prime_bits)

        test_pairs.append((block, block_prime, flip_idx))

    raw_results = []
    summary_results = []

    for rounds in VALID_ROUND_COUNTS:
        print(f"Evaluating {rounds} CA Rounds...")

        avalanche_list = []
        npcr_list = []
        uaci_list = []
        reversibility_passed = True

        # Metric Collection Loop
        for trial_idx, (b, b_prime, f_idx) in enumerate(test_pairs):
            c = transform_block_with_rounds(b, rounds)
            c_prime = transform_block_with_rounds(b_prime, rounds)

            # Reversibility verification
            rec_b = inverse_transform_block_with_rounds(c, rounds)
            rec_b_prime = inverse_transform_block_with_rounds(c_prime, rounds)

            if rec_b != b or rec_b_prime != b_prime:
                reversibility_passed = False

            av = calculate_bit_avalanche(c, c_prime)
            npcr = calculate_bit_npcr(c, c_prime)
            uaci = calculate_bit_uaci(c, c_prime)

            avalanche_list.append(av)
            npcr_list.append(npcr)
            uaci_list.append(uaci)

            raw_results.append({
                "trial": trial_idx + 1,
                "rounds": rounds,
                "flip_idx": f_idx,
                "avalanche_percent": av,
                "npcr_percent": npcr,
                "uaci_percent": uaci,
                "reversibility_pass": rec_b == b and rec_b_prime == b_prime,
            })

        # Timing Measurement Loop (100 trials using perf_counter)
        sample_b = test_pairs[0][0]
        # Warm-up
        for _ in range(5):
            _ = transform_block_with_rounds(sample_b, rounds)

        timing_ms_list = []
        for _ in range(timing_trials):
            t0 = time.perf_counter()
            _ = transform_block_with_rounds(sample_b, rounds)
            t1 = time.perf_counter()
            timing_ms_list.append((t1 - t0) * 1000.0)

        summary_results.append({
            "rounds": rounds,
            "mean_avalanche_percent": mean(avalanche_list),
            "std_avalanche_percent": std_dev(avalanche_list),
            "mean_npcr_percent": mean(npcr_list),
            "std_npcr_percent": std_dev(npcr_list),
            "mean_uaci_percent": mean(uaci_list),
            "std_uaci_percent": std_dev(uaci_list),
            "mean_encryption_time_ms": mean(timing_ms_list),
            "std_encryption_time_ms": std_dev(timing_ms_list),
            "reversibility_passed": reversibility_passed,
        })

    # Save CSV Results
    save_csv_files(summary_results, raw_results)

    # Print Summary Table
    print_summary_table(summary_results)

    return summary_results, raw_results


def save_csv_files(summary: List[Dict], raw: List[Dict]) -> None:
    """Saves summary and raw experimental results to CSV files."""
    summary_path = "ca_round_experiment_results.csv"
    raw_path = "ca_round_experiment_raw.csv"

    # Save Summary CSV
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    print(f"Saved summary results to: {summary_path}")

    # Save Raw CSV
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw[0].keys()))
        writer.writeheader()
        writer.writerows(raw)
    print(f"Saved raw trial results to: {raw_path}\n")


def print_summary_table(summary: List[Dict]) -> None:
    """Prints a clean, structured summary table of experimental results."""
    print("=" * 115)
    print(" CA ROUND-COUNT EXPERIMENTAL SUMMARY TABLE")
    print("=" * 115)
    header = (
        f"{'Rounds':<8} | {'Mean Avail (%)':<15} | {'Std Avail (%)':<15} | "
        f"{'Mean NPCR (%)':<15} | {'Mean UACI (%)':<15} | {'Mean Time (ms)':<16} | {'Reversible':<10}"
    )
    print(header)
    print("-" * 115)

    for s in summary:
        rev_str = "PASSED" if s["reversibility_passed"] else "FAILED"
        print(
            f"{s['rounds']:<8} | "
            f"{s['mean_avalanche_percent']:<15.3f} | "
            f"{s['std_avalanche_percent']:<15.3f} | "
            f"{s['mean_npcr_percent']:<15.3f} | "
            f"{s['mean_uaci_percent']:<15.3f} | "
            f"{s['mean_encryption_time_ms']:<16.4f} | "
            f"{rev_str:<10}"
        )

    print("-" * 115)
    print("Note: All metrics reflect bit-based avalanche/NPCR/UACI over 256-bit binary blocks.\n")


if __name__ == "__main__":
    run_experiment()
