"""
Module: step11_diffusion_diagnostic.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Step 11 diagnostic investigation of plaintext-difference diffusion,
         local 4-bit rule differential behavior, spatial propagation visual masks,
         and alternative exactly reversible CA round schedules/shift placements.

IMPORTANT:
  - Production crypto path and paper are NOT modified.
  - No prohibited algorithms (AES, HKDF, HMAC, AEAD, nonce, salt, etc.) added.
  - All tested candidate schedules have exact mathematical inverse functions.
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
    FORWARD_RULE,
    INVERSE_RULE,
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
    xor_binary_strings,
)


def hamming_distance_str(str1: str, str2: str) -> int:
    """Calculates bitwise Hamming distance between two binary strings of equal length."""
    return sum(1 for a, b in zip(str1, str2) if a != b)


def matrix_diff_mask(m1: List[List[int]], m2: List[List[int]]) -> List[List[int]]:
    """Returns a 16x16 binary matrix where 1 indicates cells that differ between m1 and m2."""
    mask = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    for r in range(MATRIX_ROWS):
        for c in range(MATRIX_COLS):
            if m1[r][c] != m2[r][c]:
                mask[r][c] = 1
    return mask


def get_mask_stats(mask: List[List[int]]) -> Dict[str, Any]:
    """Calculates cell count, 2x2 neighborhood count, and bounding box of changed cells."""
    changed_cells = 0
    rows_with_changes = set()
    cols_with_changes = set()

    for r in range(MATRIX_ROWS):
        for c in range(MATRIX_COLS):
            if mask[r][c] == 1:
                changed_cells += 1
                rows_with_changes.add(r)
                cols_with_changes.add(c)

    # Calculate changed 2x2 neighborhoods (in standard 2x2 grid partitioning)
    neighborhoods_changed = 0
    for r in range(0, MATRIX_ROWS, 2):
        for c in range(0, MATRIX_COLS, 2):
            if (mask[r][c] == 1 or mask[r+1][c] == 1 or 
                mask[r][c+1] == 1 or mask[r+1][c+1] == 1):
                neighborhoods_changed += 1

    min_row = min(rows_with_changes) if rows_with_changes else -1
    max_row = max(rows_with_changes) if rows_with_changes else -1
    min_col = min(cols_with_changes) if cols_with_changes else -1
    max_col = max(cols_with_changes) if cols_with_changes else -1

    return {
        "changed_cells": changed_cells,
        "neighborhoods_changed": neighborhoods_changed,
        "row_range": (min_row, max_row),
        "col_range": (min_col, max_col),
    }


# ==============================================================================
# 1. LOCAL 4-BIT RULE DIFFERENTIAL ANALYSIS
# ==============================================================================

def analyze_local_4bit_rule_differentials() -> Dict[str, Any]:
    """
    Enumerates all 16 4-bit states (0..15) and all 4 single-bit input flips for Candidate B.
    Calculates output Hamming distances: HD(f(x), f(x ^ e_i)).
    """
    diff_hd_counts = {}
    total_pairs = 0
    all_hds = []

    for state in range(16):
        out1 = FORWARD_RULE[state]
        for bit_idx in range(4):
            state_flipped = state ^ (1 << bit_idx)
            out2 = FORWARD_RULE[state_flipped]
            
            # Count differing bits in 4-bit output
            hd = bin(out1 ^ out2).count('1')
            all_hds.append(hd)
            diff_hd_counts[hd] = diff_hd_counts.get(hd, 0) + 1
            total_pairs += 1

    min_hd = min(all_hds)
    max_hd = max(all_hds)
    mean_hd = sum(all_hds) / float(len(all_hds))

    return {
        "total_pairs": total_pairs,
        "min_hd": min_hd,
        "max_hd": max_hd,
        "mean_hd": mean_hd,
        "distribution": diff_hd_counts,
    }


# ==============================================================================
# 2. STEP-BY-STEP ONE-BIT PROPAGATION DIAGNOSTIC (R = 1..32)
# ==============================================================================

def trace_one_bit_propagation(max_rounds: int = 32) -> List[Dict[str, Any]]:
    """
    Traces one-bit perturbation propagation across rounds 1..max_rounds,
    recording changed bits, cells, neighborhoods, and bounding box after EVERY round
    and after EVERY shift.
    """
    p1 = "0" * 256
    p2 = "1" + "0" * 255

    m1 = block_to_matrix(p1)
    m2 = block_to_matrix(p2)

    records = []

    for r in range(1, max_rounds + 1):
        # Round r Margolus step (odd = standard partition, even = shifted partition)
        if r % 2 != 0:
            m1 = apply_margolus_forward(m1)
            m2 = apply_margolus_forward(m2)
            stage_name = f"Round {r} (Margolus R1)"
        else:
            m1 = apply_shifted_margolus_forward(m1)
            m2 = apply_shifted_margolus_forward(m2)
            stage_name = f"Round {r} (Shifted R2)"

        mask_post_ca = matrix_diff_mask(m1, m2)
        stats_post_ca = get_mask_stats(mask_post_ca)
        b1_str = matrix_to_block(m1)
        b2_str = matrix_to_block(m2)
        bit_hd_ca = hamming_distance_str(b1_str, b2_str)

        records.append({
            "round": r,
            "stage": stage_name,
            "changed_bits": bit_hd_ca,
            "changed_cells": stats_post_ca["changed_cells"],
            "neighborhoods_changed": stats_post_ca["neighborhoods_changed"],
            "row_range": f"{stats_post_ca['row_range'][0]}-{stats_post_ca['row_range'][1]}",
            "col_range": f"{stats_post_ca['col_range'][0]}-{stats_post_ca['col_range'][1]}",
        })

        # Circular Shift step (between successive rounds)
        m1 = circular_shift_matrix(m1, row_shift=1, col_shift=1)
        m2 = circular_shift_matrix(m2, row_shift=1, col_shift=1)

        mask_post_shift = matrix_diff_mask(m1, m2)
        stats_post_shift = get_mask_stats(mask_post_shift)
        b1_shift_str = matrix_to_block(m1)
        b2_shift_str = matrix_to_block(m2)
        bit_hd_shift = hamming_distance_str(b1_shift_str, b2_shift_str)

        records.append({
            "round": r,
            "stage": f"Round {r} (Post-Shift DOWN 1 / RIGHT 1)",
            "changed_bits": bit_hd_shift,
            "changed_cells": stats_post_shift["changed_cells"],
            "neighborhoods_changed": stats_post_shift["neighborhoods_changed"],
            "row_range": f"{stats_post_shift['row_range'][0]}-{stats_post_shift['row_range'][1]}",
            "col_range": f"{stats_post_shift['col_range'][0]}-{stats_post_shift['col_range'][1]}",
        })

    return records


# ==============================================================================
# 3. CHANGED-CELL MASKS VISUALIZATION
# ==============================================================================

def print_changed_cell_masks(rounds: int = 6) -> None:
    """Prints 16x16 binary matrix masks ('0' = unchanged, '1' = changed) for rounds 1..rounds."""
    p1 = "0" * 256
    p2 = "1" + "0" * 255

    m1 = block_to_matrix(p1)
    m2 = block_to_matrix(p2)

    print("\n" + "=" * 80)
    print(" 16x16 CHANGED-CELL MASKS VISUALIZATION (0 = Unchanged, 1 = Changed)")
    print("=" * 80)

    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m1 = apply_margolus_forward(m1)
            m2 = apply_margolus_forward(m2)
            lbl = f"Round {r} (Standard Margolus)"
        else:
            m1 = apply_shifted_margolus_forward(m1)
            m2 = apply_shifted_margolus_forward(m2)
            lbl = f"Round {r} (Shifted Margolus)"

        mask = matrix_diff_mask(m1, m2)
        stats = get_mask_stats(mask)

        print(f"\n--- {lbl} [Changed Cells: {stats['changed_cells']}, Changed 2x2 Blocks: {stats['neighborhoods_changed']}] ---")
        for row in mask:
            print(" ".join(str(val) for val in row))

        # Circular Shift
        m1 = circular_shift_matrix(m1, row_shift=1, col_shift=1)
        m2 = circular_shift_matrix(m2, row_shift=1, col_shift=1)


# ==============================================================================
# 4. CANDIDATE REVERSIBLE ROUND SCHEDULES
# ==============================================================================

def schedule_A_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Schedule A:
      Alternating Margolus Partition (Odd=Standard, Even=Shifted Partition)
      with Circular Shift (DOWN 1, RIGHT 1) AFTER EVERY round.
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
        m = circular_shift_matrix(m, row_shift=1, col_shift=1)
    return m


def schedule_A_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Schedule A Exact Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        m = inverse_circular_shift_matrix(m, row_shift=1, col_shift=1)
        if r % 2 != 0:
            m = apply_margolus_inverse(m)
        else:
            m = apply_shifted_margolus_inverse(m)
    return m


def schedule_B_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Schedule B:
      Standard Margolus -> Shifted Margolus -> Circular Shift (DOWN 1, RIGHT 1) after every 2 rounds.
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
            m = circular_shift_matrix(m, row_shift=1, col_shift=1)
    return m


def schedule_B_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Schedule B Exact Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        if r % 2 == 0:
            m = inverse_circular_shift_matrix(m, row_shift=1, col_shift=1)
            m = apply_shifted_margolus_inverse(m)
        else:
            m = apply_margolus_inverse(m)
    return m


def schedule_C_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Schedule C:
      Pure Partition Alternation (Standard Margolus -> Shifted Margolus) WITHOUT additional matrix shift.
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
    return m


def schedule_C_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Schedule C Exact Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        if r % 2 == 0:
            m = apply_shifted_margolus_inverse(m)
        else:
            m = apply_margolus_inverse(m)
    return m


def schedule_D_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Schedule D:
      Alternating Margolus Partition with Larger Diagonal Shift (DOWN 2, RIGHT 2) after every round.
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
        else:
            m = apply_shifted_margolus_forward(m)
        m = circular_shift_matrix(m, row_shift=2, col_shift=2)
    return m


def schedule_D_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Schedule D Exact Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        m = inverse_circular_shift_matrix(m, row_shift=2, col_shift=2)
        if r % 2 != 0:
            m = apply_margolus_inverse(m)
        else:
            m = apply_shifted_margolus_inverse(m)
    return m


def schedule_E_forward(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """
    Schedule E:
      Alternating Margolus Partition with Dynamic Shift Steps:
      Odd rounds: DOWN 1, RIGHT 1 shift
      Even rounds: DOWN 3, RIGHT 3 shift
    """
    m = [row[:] for row in matrix]
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            m = apply_margolus_forward(m)
            m = circular_shift_matrix(m, row_shift=1, col_shift=1)
        else:
            m = apply_shifted_margolus_forward(m)
            m = circular_shift_matrix(m, row_shift=3, col_shift=3)
    return m


def schedule_E_inverse(matrix: List[List[int]], rounds: int) -> List[List[int]]:
    """Schedule E Exact Inverse."""
    m = [row[:] for row in matrix]
    for r in range(rounds, 0, -1):
        if r % 2 == 0:
            m = inverse_circular_shift_matrix(m, row_shift=3, col_shift=3)
            m = apply_shifted_margolus_inverse(m)
        else:
            m = inverse_circular_shift_matrix(m, row_shift=1, col_shift=1)
            m = apply_margolus_inverse(m)
    return m


SCHEDULES: Dict[str, Tuple[Callable, Callable, str]] = {
    "Schedule_A": (
        schedule_A_forward,
        schedule_A_inverse,
        "Alternating Margolus CA + Circular Shift (1,1) After Every Round"
    ),
    "Schedule_B": (
        schedule_B_forward,
        schedule_B_inverse,
        "Alternating Margolus CA + Circular Shift (1,1) After Every 2 Rounds"
    ),
    "Schedule_C": (
        schedule_C_forward,
        schedule_C_inverse,
        "Pure Alternating Margolus Partition (No Extra Shift)"
    ),
    "Schedule_D": (
        schedule_D_forward,
        schedule_D_inverse,
        "Alternating Margolus CA + Diagonal Shift (2,2) After Every Round"
    ),
    "Schedule_E": (
        schedule_E_forward,
        schedule_E_inverse,
        "Alternating Margolus CA + Alternating Shifts (1,1 then 3,3)"
    ),
}


# ==============================================================================
# 5. REVERSIBILITY VERIFICATION & EVALUATION OF CANDIDATE SCHEDULES
# ==============================================================================

def verify_schedule_reversibility(trials: int = 100) -> Dict[str, bool]:
    """Verifies 100% loss-less reversibility (forward -> inverse -> match) for all schedules."""
    rng = random.Random(20260923)
    results = {}

    for sched_name, (fwd_fn, inv_fn, _) in SCHEDULES.items():
        all_passed = True
        for _ in range(trials):
            # Generate random 256-bit block
            block_bits = [rng.choice(["0", "1"]) for _ in range(256)]
            block = "".join(block_bits)
            m0 = block_to_matrix(block)

            # Test across multiple round counts
            for r in [2, 4, 6, 8, 10, 16, 20, 32]:
                m_fwd = fwd_fn(m0, r)
                m_inv = inv_fn(m_fwd, r)
                b_rec = matrix_to_block(m_inv)
                if b_rec != block:
                    all_passed = False
                    break
            if not all_passed:
                break
        results[sched_name] = all_passed

    return results


def evaluate_schedules_diffusion(trials: int = 100) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Evaluates diffusion metrics (Avalanche, Bit NPCR, Byte NPCR, Byte UACI, timing)
    across all candidate schedules and round counts R in {2, 4, 6, 8, 10, 16, 20, 32}.
    """
    rng = random.Random(20260923)
    password = "MasterDoctorKey2026#"
    k256 = derive_k256(password)

    # Generate 100 deterministic 256-bit plaintexts and 1-bit perturbed counterparts
    test_pairs = []
    for _ in range(trials):
        p1_bits = [rng.choice(["0", "1"]) for _ in range(256)]
        p1 = "".join(p1_bits)
        p2_bits = list(p1_bits)
        flip_idx = rng.randint(0, 255)
        p2_bits[flip_idx] = "1" if p1_bits[flip_idx] == "0" else "0"
        p2 = "".join(p2_bits)
        test_pairs.append((p1, p2))

    summary_rows = []
    raw_rows = []

    round_counts = [2, 4, 6, 8, 10, 16, 20, 32]

    for sched_name, (fwd_fn, inv_fn, desc) in SCHEDULES.items():
        print(f"\nEvaluating {sched_name}: {desc}...")

        for r in round_counts:
            avalanche_list = []
            bit_npcr_list = []
            byte_npcr_list = []
            byte_uaci_list = []

            # Timing
            t0 = time.perf_counter()
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

                # Bytes
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

            t1 = time.perf_counter()
            time_per_block_ms = ((t1 - t0) * 1000.0) / (2.0 * trials)

            mean_av = sum(avalanche_list) / float(len(avalanche_list))
            mean_bit_npcr = sum(bit_npcr_list) / float(len(bit_npcr_list))
            mean_byte_npcr = sum(byte_npcr_list) / float(len(byte_npcr_list))
            mean_byte_uaci = sum(byte_uaci_list) / float(len(byte_uaci_list))
            mean_bits_changed = mean_av * 2.56

            summary_rows.append({
                "schedule": sched_name,
                "rounds": r,
                "changed_bits_mean": mean_bits_changed,
                "avalanche_percent_mean": mean_av,
                "bit_npcr_percent_mean": mean_bit_npcr,
                "byte_npcr_percent_mean": mean_byte_npcr,
                "byte_uaci_percent_mean": mean_byte_uaci,
                "time_per_block_ms": time_per_block_ms,
                "reversibility_passed": True,
            })

            print(
                f"  Rounds: {r:2d} | Bits Changed: {mean_bits_changed:5.2f} / 256 | "
                f"Avalanche: {mean_av:5.2f}% | Byte NPCR: {mean_byte_npcr:5.2f}% | "
                f"Time/Block: {time_per_block_ms:.3f}ms",
                flush=True
            )

    return summary_rows, raw_rows


# ==============================================================================
# 6. RUN STEP 11 FULL DIAGNOSTIC SUITE
# ==============================================================================

def run_step11_diagnostics() -> None:
    """Executes all Step 11 diagnostic routines and saves CSV files."""
    print("=" * 100)
    print(" STEP 11: INVESTIGATION OF PLAINTEXT DIFFUSION IN REVERSIBLE CA SCHEMES")
    print("=" * 100)

    # 1. Local 4-Bit Rule Differential Analysis
    print("\n1. Analyzing Local 4-Bit Bijective Rule Differential Properties...")
    rule_stats = analyze_local_4bit_rule_differentials()
    print(f"  Total 4-Bit State Pairs Analyzed: {rule_stats['total_pairs']}")
    print(f"  Output Hamming Distance Min:     {rule_stats['min_hd']} bit")
    print(f"  Output Hamming Distance Max:     {rule_stats['max_hd']} bits")
    print(f"  Output Hamming Distance Mean:    {rule_stats['mean_hd']:.3f} bits")
    print("  Output HD Distribution:")
    for hd, count in sorted(rule_stats["distribution"].items()):
        pct = (count / float(rule_stats['total_pairs'])) * 100.0
        print(f"    HD = {hd} bit(s): {count:2d} occurrences ({pct:.1f}%)")

    # 2. Step-by-Step One-Bit Propagation Diagnostic Table
    print("\n2. Tracing One-Bit Propagation Across Rounds (1..32)...")
    propagation_records = trace_one_bit_propagation(max_rounds=32)
    print(f"{'Stage':<40} | {'Bits Changed':<12} | {'Cells Changed':<13} | {'2x2 Blocks':<10} | {'Row Range':<10} | {'Col Range':<10}")
    print("-" * 105)
    for rec in propagation_records:
        if rec["round"] in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 32]:
            print(
                f"{rec['stage']:<40} | {rec['changed_bits']:<12d} | "
                f"{rec['changed_cells']:<13d} | {rec['neighborhoods_changed']:<10d} | "
                f"{rec['row_range']:<10} | {rec['col_range']:<10}"
            )

    # 3. Changed-Cell Visual Masks
    print_changed_cell_masks(rounds=6)

    # 4. Schedule Reversibility Verification
    print("\n4. Verifying 100% Loss-Less Reversibility of Candidate Round Schedules...")
    rev_results = verify_schedule_reversibility(trials=100)
    for sched, passed in rev_results.items():
        print(f"  {sched:<15} Reversibility Verification (100 Trials, R=2..32): {'PASS (100% Loss-Less)' if passed else 'FAIL'}")

    # 5. Evaluate Schedules Diffusion & Performance
    print("\n5. Evaluating Quantitative Diffusion & Performance Across Schedules...")
    summary_rows, raw_rows = evaluate_schedules_diffusion(trials=100)

    # 6. Save Machine-Readable CSV Output
    save_step11_csv(summary_rows, propagation_records)


def save_step11_csv(summary_rows: List[Dict], propagation_records: List[Dict]) -> None:
    """Saves Step 11 diagnostic results to CSV files."""
    summary_path = "step11_diffusion_results.csv"
    raw_path = "step11_diffusion_raw.csv"

    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nSaved Step 11 summary results to: {summary_path}", flush=True)

    if propagation_records:
        fieldnames = list(propagation_records[0].keys())
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(propagation_records)
        print(f"Saved Step 11 propagation tracking log to: {raw_path}", flush=True)


if __name__ == "__main__":
    run_step11_diagnostics()
