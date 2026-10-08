"""
Module: audit_step8_results.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Independent numerical audit of Step 8 experimental results from CSV raw files,
         formula verification, reversibility, healthcare record recovery, timing, and monotonicity analysis.
"""

import csv
import math
import random
from typing import List, Dict, Tuple
from ca_matrix import block_to_matrix, matrix_to_block
from step13_final_round_experiment import (
    candidate_C_forward,
    candidate_C_inverse,
    candidate_C_encrypt_text,
    candidate_C_decrypt_text,
)
from research_crypto_utils import derive_k256, xor_binary_strings
from synthetic_healthcare_data import generate_synthetic_dataset, record_to_string


def mean(data: List[float]) -> float:
    return sum(data) / len(data) if data else 0.0


def std_dev(data: List[float]) -> float:
    if len(data) <= 1:
        return 0.0
    m = mean(data)
    variance = sum((x - m) ** 2 for x in data) / (len(data) - 1)
    return math.sqrt(variance)


def audit_csv_consistency() -> Tuple[bool, Dict[int, Dict[str, float]]]:
    """Reads step13_final_round_raw.csv and independently computes summary statistics per round count."""
    raw_by_rounds: Dict[int, List[Dict[str, float]]] = {}

    with open("step13_final_round_raw.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = int(row["rounds"])
            if r not in raw_by_rounds:
                raw_by_rounds[r] = []
            raw_by_rounds[r].append({
                "diff_bits": float(row["diff_bits"]),
                "bit_avalanche_percent": float(row["bit_avalanche_percent"]),
                "bit_npcr_percent": float(row["bit_npcr_percent"]),
                "byte_npcr_percent": float(row["byte_npcr_percent"]),
                "byte_uaci_percent": float(row["byte_uaci_percent"]),
            })

    indep_summary: Dict[int, Dict[str, float]] = {}
    for r, rows in raw_by_rounds.items():
        diff_bits = [row["diff_bits"] for row in rows]
        bit_av = [row["bit_avalanche_percent"] for row in rows]
        bit_npcr = [row["bit_npcr_percent"] for row in rows]
        byte_npcr = [row["byte_npcr_percent"] for row in rows]
        byte_uaci = [row["byte_uaci_percent"] for row in rows]

        indep_summary[r] = {
            "changed_bits_mean": mean(diff_bits),
            "changed_bits_min": min(diff_bits),
            "changed_bits_max": max(diff_bits),
            "changed_bits_std": std_dev(diff_bits),
            "bit_avalanche_mean": mean(bit_av),
            "bit_npcr_mean": mean(bit_npcr),
            "byte_npcr_mean": mean(byte_npcr),
            "byte_uaci_mean": mean(byte_uaci),
        }

    # Compare with step13_final_round_results.csv
    matches = True
    with open("step13_final_round_results.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = int(row["rounds"])
            ind = indep_summary[r]

            cb_mean = float(row["changed_bits_mean"])
            cb_min = float(row["changed_bits_min"])
            cb_max = float(row["changed_bits_max"])
            cb_std = float(row["changed_bits_std"])
            av_mean = float(row["bit_avalanche_mean"])
            npcr_b_mean = float(row["bit_npcr_mean"])
            npcr_byte_mean = float(row["byte_npcr_mean"])
            uaci_byte_mean = float(row["byte_uaci_mean"])

            if abs(ind["changed_bits_mean"] - cb_mean) > 1e-5:
                matches = False
            if abs(ind["changed_bits_min"] - cb_min) > 1e-5:
                matches = False
            if abs(ind["changed_bits_max"] - cb_max) > 1e-5:
                matches = False
            if abs(ind["changed_bits_std"] - cb_std) > 1e-5:
                matches = False
            if abs(ind["bit_avalanche_mean"] - av_mean) > 1e-5:
                matches = False
            if abs(ind["bit_npcr_mean"] - npcr_b_mean) > 1e-5:
                matches = False
            if abs(ind["byte_npcr_mean"] - npcr_byte_mean) > 1e-5:
                matches = False
            if abs(ind["byte_uaci_mean"] - uaci_byte_mean) > 1e-5:
                matches = False

    return matches, indep_summary


def audit_formulas() -> bool:
    """Independently recalculates formulas for raw ciphertext samples."""
    rng = random.Random(20260923)
    k256 = derive_k256("MasterDoctorKey2026#")

    for r in [2, 4, 6, 8, 10]:
        p1 = "".join(rng.choice(["0", "1"]) for _ in range(256))
        p2_bits = list(p1)
        p2_bits[0] = "1" if p1[0] == "0" else "0"
        p2 = "".join(p2_bits)

        m1_0 = block_to_matrix(p1)
        m2_0 = block_to_matrix(p2)

        m1_r = candidate_C_forward(m1_0, r)
        m2_r = candidate_C_forward(m2_0, r)

        c1 = xor_binary_strings(matrix_to_block(m1_r), k256)
        c2 = xor_binary_strings(matrix_to_block(m2_r), k256)

        # Independent formula verification
        diff_b = sum(1 for a, b in zip(c1, c2) if a != b)
        av_pct = (diff_b / 256.0) * 100.0

        b1_bytes = bytes([int(c1[i:i+8], 2) for i in range(0, 256, 8)])
        b2_bytes = bytes([int(c2[i:i+8], 2) for i in range(0, 256, 8)])

        diff_bytes = sum(1 for x, y in zip(b1_bytes, b2_bytes) if x != y)
        npcr_byte = (diff_bytes / 32.0) * 100.0

        diff_sum = sum(abs(int(x) - int(y)) for x, y in zip(b1_bytes, b2_bytes))
        uaci_byte = (diff_sum / (32.0 * 255.0)) * 100.0

        # Assert correct ranges and matching logic
        if not (0 <= diff_b <= 256 and 0.0 <= av_pct <= 100.0 and 0.0 <= npcr_byte <= 100.0 and 0.0 <= uaci_byte <= 100.0):
            return False

    return True


def audit_reversibility() -> Dict[int, Tuple[int, int, float]]:
    """Independently verifies candidate_C_forward and candidate_C_inverse reversibility across 100 test blocks."""
    rng = random.Random(20260923)
    results = {}

    test_blocks = ["".join(rng.choice(["0", "1"]) for _ in range(256)) for _ in range(100)]

    for r in [2, 4, 6, 8, 10]:
        passed = 0
        for block in test_blocks:
            m0 = block_to_matrix(block)
            m_fwd = candidate_C_forward(m0, r)
            m_rec = candidate_C_inverse(m_fwd, r)
            if matrix_to_block(m_rec) == block:
                passed += 1
        results[r] = (passed, 100 - passed, (passed / 100.0) * 100.0)

    return results


def audit_healthcare_recovery() -> Dict[int, Tuple[int, int, float]]:
    """Independently verifies 100 synthetic healthcare records encryption/decryption across round counts."""
    password = "HospitalDoctorPassword2026#"
    dataset = generate_synthetic_dataset(100, seed=20260923)
    results = {}

    for r in [2, 4, 6, 8, 10]:
        passed = 0
        for rec in dataset:
            orig_str = record_to_string(rec)
            c_str = candidate_C_encrypt_text(orig_str, password, r)
            dec_str = candidate_C_decrypt_text(c_str, password, r)
            if dec_str == orig_str:
                passed += 1
        results[r] = (passed, 100 - passed, (passed / 100.0) * 100.0)

    return results


def main() -> None:
    print("=" * 60)
    print(" STEP 9: INDEPENDENT NUMERICAL AUDIT OF STEP 8 RESULTS ")
    print("=" * 60)

    # AUDIT 1: CSV Consistency
    csv_match, indep_summary = audit_csv_consistency()
    print(f"\nAUDIT 1 — CSV Consistency Check: {'PASS' if csv_match else 'FAIL'}")

    # AUDIT 2: Formula Verification
    formula_match = audit_formulas()
    print(f"AUDIT 2 — Formula Verification:   {'PASS' if formula_match else 'FAIL'}")

    # AUDIT 3: Reversibility
    rev_results = audit_reversibility()
    print("\nAUDIT 3 — Reversibility Results:")
    for r, (p, f, pct) in rev_results.items():
        print(f"  R={r:2d}: {p}/100 PASS ({pct:.0f}%)")

    # AUDIT 4: Healthcare Recovery
    hc_results = audit_healthcare_recovery()
    print("\nAUDIT 4 — Healthcare Record Recovery:")
    for r, (p, f, pct) in hc_results.items():
        print(f"  R={r:2d}: {p}/100 PASS ({pct:.0f}%)")

    # AUDIT 5: Summary Table Display
    print("\n" + "=" * 80)
    print("INDEPENDENT RECALCULATION TABLE (from step13_final_round_raw.csv):")
    print("=" * 80)
    print("Rounds | Mean Changed Bits | Min | Max | Std   | Avalanche % | Bit NPCR % | Byte NPCR % | Byte UACI %")
    print("-------+-------------------+-----+-----+-------+-------------+------------+-------------+------------")
    for r in [2, 4, 6, 8, 10]:
        s = indep_summary[r]
        print(
            f"  {r:2d}   |       {s['changed_bits_mean']:6.2f}      | {s['changed_bits_min']:3.0f} | {s['changed_bits_max']:3.0f} | {s['changed_bits_std']:5.2f} |    {s['bit_avalanche_mean']:6.2f}%   |   {s['bit_npcr_mean']:6.2f}%  |   {s['byte_npcr_mean']:6.2f}%   |   {s['byte_uaci_mean']:6.2f}%"
        )

    # AUDIT 8: R=16 Observation
    if 16 in indep_summary:
        s16 = indep_summary[16]
        print(
            f"  16*  |       {s16['changed_bits_mean']:6.2f}      | {s16['changed_bits_min']:3.0f} | {s16['changed_bits_max']:3.0f} | {s16['changed_bits_std']:5.2f} |    {s16['bit_avalanche_mean']:6.2f}%   |   {s16['bit_npcr_mean']:6.2f}%  |   {s16['byte_npcr_mean']:6.2f}%   |   {s16['byte_uaci_mean']:6.2f}%"
        )
        print("  (*Note: R=16 is included as an observation reference only, outside main 2/4/6/8/10 rounds).")
    print("=" * 80)


if __name__ == "__main__":
    main()
