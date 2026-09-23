"""
Module: ca_rule_analysis.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone mathematical design, evaluation, and analysis script for
         candidate reversible 4-bit (2x2) Cellular Automata local rules.

Calculates exact cryptographic metrics for candidate 4-bit permutations:
  1. Bijectivity (1-to-1 state mapping, invertibility across 16 states)
  2. Vectorial Nonlinearity N_S (via Walsh-Hadamard Transform over F_2^4)
  3. Strict Avalanche Criterion (SAC - average bit flip probability & 4x4 matrix)
  4. Differential Uniformity delta_S (max DDT count for non-zero input differences)
"""

import random
from typing import List, Tuple, Dict


def is_bijective(perm: List[int]) -> bool:
    """Confirms if a 4-bit state mapping [0..15] -> [0..15] is a valid bijection."""
    if len(perm) != 16:
        return False
    return sorted(perm) == list(range(16))


def get_inverse_mapping(perm: List[int]) -> List[int]:
    """Derives the exact inverse permutation table for a bijective 4-bit rule."""
    if not is_bijective(perm):
        raise ValueError("Cannot invert non-bijective permutation.")
    inv = [0] * 16
    for i, val in enumerate(perm):
        inv[val] = i
    return inv


def compute_nonlinearity(perm: List[int]) -> int:
    """
    Calculates the vectorial nonlinearity N_S of a 4-bit S-box / permutation S.
    Formula:
      N_S = 2^(n-1) - 0.5 * max_{b in {1..15}, w in {0..15}} |W_{f_b}(w)|
    where f_b(x) = b . S(x) (bitwise dot product) and W_{f_b}(w) is the Walsh transform:
      W_{f_b}(w) = sum_{x=0..15} (-1)^( (b . S(x)) ^ (w . x) )
    """
    n = 4
    max_walsh = 0

    # Loop over all non-zero linear combinations of output bits b in {1..15}
    for b in range(1, 16):
        # Loop over all input mask frequencies w in {0..15}
        for w in range(16):
            walsh_sum = 0
            for x in range(16):
                # Component boolean function output: b . S(x) (mod 2 parity)
                dot_b_sx = bin(b & perm[x]).count('1') % 2
                # Input linear mask: w . x (mod 2 parity)
                dot_w_x = bin(w & x).count('1') % 2

                exponent = dot_b_sx ^ dot_w_x
                if exponent == 1:
                    walsh_sum -= 1
                else:
                    walsh_sum += 1

            if abs(walsh_sum) > max_walsh:
                max_walsh = abs(walsh_sum)

    # Nonlinearity N_S = 2^(4-1) - max_walsh / 2 = 8 - max_walsh / 2
    return 8 - (max_walsh // 2)


def compute_sac(perm: List[int]) -> Tuple[float, List[List[float]], float]:
    """
    Calculates the Strict Avalanche Criterion (SAC) for a 4-bit permutation.
    For each input bit i (0..3) and output bit j (0..3):
      sac_matrix[i][j] = prob that flipping input bit i causes output bit j to flip.
    Returns:
      (average_sac, sac_matrix, max_sac_deviation)
    """
    sac_matrix = [[0.0 for _ in range(4)] for _ in range(4)]
    max_dev = 0.0

    for i in range(4):
        bit_mask_i = 1 << i
        for x in range(16):
            x_flipped = x ^ bit_mask_i
            y1 = perm[x]
            y2 = perm[x_flipped]
            diff = y1 ^ y2
            for j in range(4):
                if (diff >> j) & 1:
                    sac_matrix[i][j] += 1.0

    for i in range(4):
        for j in range(4):
            sac_matrix[i][j] /= 16.0
            dev = abs(sac_matrix[i][j] - 0.5)
            if dev > max_dev:
                max_dev = dev

    avg_sac = sum(sum(row) for row in sac_matrix) / 16.0
    return avg_sac, sac_matrix, max_dev


def compute_ddt(perm: List[int]) -> Tuple[int, List[List[int]]]:
    """
    Computes the Difference Distribution Table (DDT) and Differential Uniformity delta_S.
    DDT[dx][dy] = count of x in {0..15} such that S(x) ^ S(x ^ dx) == dy.
    Differential Uniformity delta_S = max DDT[dx][dy] for dx != 0.
    """
    ddt = [[0 for _ in range(16)] for _ in range(16)]

    for x in range(16):
        for dx in range(16):
            dy = perm[x] ^ perm[x ^ dx]
            ddt[dx][dy] += 1

    max_diff = 0
    for dx in range(1, 16):
        for dy in range(16):
            if ddt[dx][dy] > max_diff:
                max_diff = ddt[dx][dy]

    return max_diff, ddt


def format_hex_perm(perm: List[int]) -> str:
    """Formats 4-bit permutation list into clean hex string representation."""
    return "[" + ", ".join(f"0x{x:X}" for x in perm) + "]"


def format_binary_state(val: int) -> str:
    """Formats integer 0..15 as 4-bit binary string."""
    return format(val, "04b")


def print_detailed_rule_report(opt: Dict):
    """Prints exhaustive cryptographic analysis for a single candidate rule."""
    print("=" * 100)
    print(f" DETAILED CRYPTOGRAPHIC ANALYSIS: {opt['name']}")
    print("=" * 100)
    print(f"Candidate Name:            {opt['name']}")
    print(f"Permutation Table (Hex):   {format_hex_perm(opt['perm'])}")
    inv_opt = get_inverse_mapping(opt["perm"])
    print(f"Inverse Table (Hex):       {format_hex_perm(inv_opt)}")
    print(f"Bijectivity:               {opt['bijective']} (16 unique 4-bit output states)")
    print(f"Nonlinearity (N_S):        {opt['nonlinearity']} (Theoretical Maximum for 4-bit S-Box = 4)")
    print(f"Strict Avalanche (SAC):    {opt['sac_avg']:.4f} (Ideal = 0.5000, Max Dev = {opt['sac_dev']:.4f})")
    print(f"Differential Uniformity:   {opt['diff_uniformity']} (Theoretical Minimum for 4-bit bijection = 4)")

    print("\nState Mapping Table (4-bit binary & hex):")
    print(f"{'Input State (Hex)':<20} | {'Input (Bin)':<15} | {'Output State (Hex)':<20} | {'Output (Bin)':<15}")
    print("-" * 75)
    for x in range(16):
        y = opt["perm"][x]
        hex_in = f"0x{x:X}"
        hex_out = f"0x{y:X}"
        print(f"{hex_in:<20} | {format_binary_state(x):<15} | {hex_out:<20} | {format_binary_state(y):<15}")

    print("-" * 75)

    print("\nSAC Matrix (Input Bit i vs Output Bit j Flip Probability):")
    print(f"{'Input Bit':<12} | {'Out Bit 0':<10} | {'Out Bit 1':<10} | {'Out Bit 2':<10} | {'Out Bit 3':<10}")
    print("-" * 65)
    for i in range(4):
        row_str = " | ".join(f"{opt['sac_matrix'][i][j]:.4f}" for j in range(4))
        print(f"Bit {i:<8} | {row_str}")
    print("-" * 65)
    print()


def analyze_candidate_rules():
    """Generates and analyzes candidate 4-bit local rules."""
    candidates = {}

    # Candidate 0: Identity Rule (Baseline)
    candidates["Rule 0 (Identity)"] = list(range(16))

    # Candidate 1: 2-bit FBCA extended to 4-bit (Legacy Rule acting on 2 x 2-bit pairs)
    # Legacy FBCA: 00->00, 01->10, 10->01, 11->11
    fbca_2bit = {0: 0, 1: 2, 2: 1, 3: 3}
    rule_legacy_4bit = []
    for x in range(16):
        high2 = (x >> 2) & 3
        low2 = x & 3
        rule_legacy_4bit.append((fbca_2bit[high2] << 2) | fbca_2bit[low2])
    candidates["Rule 1 (Legacy 2-bit FBCA extended)"] = rule_legacy_4bit

    # Candidate 2: Linear Permutation (Bit Shift / XOR)
    rule_linear = [(((x << 1) & 0xF | (x >> 3)) ^ 0x3) for x in range(16)]
    candidates["Rule 2 (Linear Rotation/XOR)"] = rule_linear

    # Candidate 3: Structured Non-Linear Reversible 4-bit CA
    rule_ca_structured = [
        0x0E, 0x0F, 0x01, 0x00, 0x0A, 0x0B, 0x04, 0x05,
        0x02, 0x08, 0x0C, 0x06, 0x0D, 0x03, 0x07, 0x09
    ]
    candidates["Rule 3 (Structured Non-Linear CA)"] = rule_ca_structured

    # Candidate 4: Optimal 4-bit Permutation A (PRESENT S-Box)
    candidates["Rule 4 (Optimal 4-bit CA - Candidate A / PRESENT)"] = [
        0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2
    ]

    # Candidate 5: Optimal 4-bit Permutation B (PICCOLO / RECTANGLE S-Box)
    candidates["Rule 5 (Optimal 4-bit CA - Candidate B / PICCOLO)"] = [
        0xE, 0x4, 0xB, 0x2, 0x3, 0x8, 0x0, 0x9, 0x1, 0xA, 0x7, 0xF, 0x6, 0xC, 0x5, 0xD
    ]

    # Candidate 6: Optimal 4-bit Permutation C (Golden Class S-Box)
    candidates["Rule 6 (Optimal 4-bit CA - Candidate C / Golden Class)"] = [
        0x3, 0xE, 0x1, 0xA, 0x0, 0x7, 0xB, 0xC, 0xD, 0x4, 0x6, 0xF, 0x2, 0x9, 0x8, 0x5
    ]

    # Candidate 7: Deterministically Seeded Random Search Candidate
    random.seed(20260922)
    rand_perm = list(range(16))
    random.shuffle(rand_perm)
    candidates["Rule 7 (Seeded Pseudorandom Permutation)"] = rand_perm

    print("=" * 105)
    print(" 4-BIT (2x2) CELLULAR AUTOMATA LOCAL RULE ANALYSIS REPORT")
    print("=" * 105)
    print()

    results = []

    for name, perm in candidates.items():
        bijective = is_bijective(perm)
        nl = compute_nonlinearity(perm) if bijective else 0
        avg_sac, sac_matrix, max_sac_dev = compute_sac(perm) if bijective else (0.0, [], 0.0)
        du, ddt = compute_ddt(perm) if bijective else (0, [])

        results.append({
            "name": name,
            "perm": perm,
            "bijective": bijective,
            "nonlinearity": nl,
            "sac_avg": avg_sac,
            "sac_dev": max_sac_dev,
            "sac_matrix": sac_matrix,
            "diff_uniformity": du,
            "ddt": ddt
        })

    # Print Summary Table
    print(f"{'Rule ID / Name':<53} | {'Bijective':<10} | {'NL':<5} | {'Avg SAC':<8} | {'SAC MaxDev':<10} | {'Diff Unif':<10}")
    print("-" * 105)

    for r in results:
        bij_str = "YES" if r["bijective"] else "NO"
        print(f"{r['name']:<53} | {bij_str:<10} | {r['nonlinearity']:<5} | {r['sac_avg']:<8.3f} | {r['sac_dev']:<10.3f} | {r['diff_uniformity']:<10}")

    print("-" * 105)
    print()

    # Detailed report for Candidate 4 and Candidate 5
    opt_a = [r for r in results if "Candidate A" in r["name"]][0]
    opt_b = [r for r in results if "Candidate B" in r["name"]][0]

    print_detailed_rule_report(opt_a)
    print_detailed_rule_report(opt_b)

    return results


if __name__ == "__main__":
    analyze_candidate_rules()
