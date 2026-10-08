"""
Module: validate_ca_rule.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Programmatic and mathematical validation of the 4-bit local Cellular Automata rule
         (FORWARD_RULE and INVERSE_RULE) defined in margolus_ca.py.
"""

from typing import List, Tuple, Dict
from margolus_ca import FORWARD_RULE, INVERSE_RULE


def check_rule_structure() -> Tuple[bool, str]:
    """
    CHECK 1: Rule structure verification.
    Verifies that FORWARD_RULE and INVERSE_RULE both contain exactly 16 entries
    and every entry is an integer in the range [0, 15].
    """
    if len(FORWARD_RULE) != 16:
        return False, f"FORWARD_RULE length is {len(FORWARD_RULE)}, expected 16."
    if len(INVERSE_RULE) != 16:
        return False, f"INVERSE_RULE length is {len(INVERSE_RULE)}, expected 16."

    for idx, val in enumerate(FORWARD_RULE):
        if not isinstance(val, int) or not (0 <= val <= 15):
            return False, f"FORWARD_RULE[{idx}] = {val} is not an integer in range [0, 15]."

    for idx, val in enumerate(INVERSE_RULE):
        if not isinstance(val, int) or not (0 <= val <= 15):
            return False, f"INVERSE_RULE[{idx}] = {val} is not an integer in range [0, 15]."

    return True, "Rule structure verified successfully."


def check_bijectivity() -> Tuple[bool, str]:
    """
    CHECK 2: Forward rule bijectivity verification.
    Verifies that all 16 entries in FORWARD_RULE are unique.
    """
    unique_forward = set(FORWARD_RULE)
    is_bijective = (len(unique_forward) == 16)
    status_str = "PASS" if is_bijective else "FAIL"
    msg = f"Forward rule is bijective: {status_str}"
    return is_bijective, msg


def check_inverse_consistency() -> Tuple[bool, Dict[str, bool]]:
    """
    CHECK 3: Forward/Inverse consistency check.
    Verifies INVERSE_RULE[FORWARD_RULE[x]] == x and FORWARD_RULE[INVERSE_RULE[x]] == x for all x in [0, 15].
    """
    inv_fwd_pass = all(INVERSE_RULE[FORWARD_RULE[x]] == x for x in range(16))
    fwd_inv_pass = all(FORWARD_RULE[INVERSE_RULE[x]] == x for x in range(16))

    results = {
        "INVERSE_RULE[FORWARD_RULE[x]] == x": inv_fwd_pass,
        "FORWARD_RULE[INVERSE_RULE[x]] == x": fwd_inv_pass,
    }

    all_pass = inv_fwd_pass and fwd_inv_pass
    return all_pass, results


def run_exhaustive_inverse_test() -> Tuple[bool, List[Tuple[int, int, int, bool]]]:
    """
    CHECK 4: Exhaustive forward/inverse test.
    For all x in [0, 15], computes y = FORWARD_RULE[x], z = INVERSE_RULE[y], and checks z == x.
    """
    table = []
    all_match = True
    for x in range(16):
        y = FORWARD_RULE[x]
        z = INVERSE_RULE[y]
        match = (z == x)
        if not match:
            all_match = False
        table.append((x, y, z, match))
    return all_match, table


def measure_local_sac() -> Tuple[int, int, float]:
    """
    CHECK 5: Local Strict Avalanche Criterion (SAC) measurement on 4-bit rule.
    16 input states x 4 bit flips = 64 comparisons.
    Each comparison has 4 output bits (total 256 possible output bit flips).
    """
    total_bit_changes = 0
    total_possible_changes = 16 * 4 * 4  # 64 comparisons * 4 bits = 256 bits

    for x in range(16):
        fx = FORWARD_RULE[x]
        for bit in range(4):
            x_flipped = x ^ (1 << bit)
            fx_flipped = FORWARD_RULE[x_flipped]
            diff = fx ^ fx_flipped
            bit_changes = bin(diff).count('1')
            total_bit_changes += bit_changes

    sac_percentage = (total_bit_changes / total_possible_changes) * 100.0
    return total_bit_changes, total_possible_changes, sac_percentage


def measure_differential_behavior() -> Tuple[int, Dict[Tuple[int, int], int]]:
    """
    CHECK 6: Differential behavior analysis on 4-bit rule.
    For every dx in [1, 15] and x in [0, 15], computes dy = F(x) XOR F(x XOR dx).
    Finds the maximum observed differential count.
    """
    ddt: Dict[Tuple[int, int], int] = {}
    for dx in range(1, 16):
        for dy in range(16):
            ddt[(dx, dy)] = 0

    for dx in range(1, 16):
        for x in range(16):
            dy = FORWARD_RULE[x] ^ FORWARD_RULE[x ^ dx]
            ddt[(dx, dy)] += 1

    max_diff_count = max(ddt.values())
    return max_diff_count, ddt


def main() -> None:
    print("=" * 60)
    print(" 4-BIT CELLULAR AUTOMATA LOCAL RULE VALIDATION ")
    print("=" * 60)

    # CHECK 1: Structure
    struct_pass, struct_msg = check_rule_structure()
    print(f"\nCHECK 1 — Rule Structure:")
    print(f"  {struct_msg}")

    # CHECK 2: Bijectivity
    bij_pass, bij_msg = check_bijectivity()
    print(f"\nCHECK 2 — Bijectivity:")
    print(f"  {bij_msg}")

    # CHECK 3: Forward/Inverse Consistency
    cons_pass, cons_results = check_inverse_consistency()
    print(f"\nCHECK 3 — Consistency:")
    for cond, passed in cons_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {cond}: {status}")

    # CHECK 4: Exhaustive Test Table
    exh_pass, table = run_exhaustive_inverse_test()
    print(f"\nCHECK 4 — Exhaustive Forward/Inverse Mapping Table:")
    print("  +-------+---------+---------+---------+")
    print("  | Input | Forward | Inverse | Match   |")
    print("  +-------+---------+---------+---------+")
    for x, y, z, match in table:
        match_str = "OK" if match else "MISMATCH"
        print(f"  |  {x:2d}   |   {y:2d}    |   {z:2d}    |   {match_str:6s}|")
    print("  +-------+---------+---------+---------+")
    print(f"  Exhaustive inverse test: {'PASS' if exh_pass else 'FAIL'}")

    # CHECK 5: Local SAC Measurement
    bit_changes, possible_changes, sac_pct = measure_local_sac()
    print(f"\nCHECK 5 — Local SAC Measurement (4-Bit Rule):")
    print(f"  Total output-bit changes:    {bit_changes}")
    print(f"  Total possible bit changes:  {possible_changes}")
    print(f"  SAC percentage:              {sac_pct:.2f}%")
    print("  Note: This local 4-bit S-box SAC measurement evaluates individual neighborhood substitution.")
    print("        Full block diffusion is achieved over multi-round Margolus CA steps and 2D circular matrix shifts.")

    # CHECK 6: Differential Behavior
    max_diff_count, _ = measure_differential_behavior()
    print(f"\nCHECK 6 — Differential Behavior Analysis (4-Bit Rule):")
    print(f"  Maximum observed differential count: {max_diff_count}")
    print("  Note: This 4-bit local differential analysis measures neighborhood substitution properties only")
    print("        and should not be presented as proof of full 256-bit block cipher security.")

    # CHECK 7: Clear Final Report
    overall_pass = struct_pass and bij_pass and cons_pass and exh_pass

    print("\n" + "=" * 40)
    print("4-BIT CA RULE VALIDATION")
    print("=" * 40)
    print(f"Rule structure: {'PASS' if struct_pass else 'FAIL'}")
    print(f"Forward rule bijective: {'PASS' if bij_pass else 'FAIL'}")
    print(f"Inverse consistency: {'PASS' if cons_pass else 'FAIL'}")
    print(f"Exhaustive inverse test: {'PASS' if exh_pass else 'FAIL'}")
    print(f"SAC measurement: {sac_pct:.2f}%")
    print(f"Maximum differential count: {max_diff_count}")
    print(f"\nOverall validation: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 40)


if __name__ == "__main__":
    main()
