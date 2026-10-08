"""
Module: validate_margolus.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Programmatic validation of the standard non-shifted 2x2 Margolus Cellular Automata
         transformation functions (apply_margolus_forward & apply_margolus_inverse).
"""

import random
from typing import List, Tuple
from ca_matrix import block_to_matrix, matrix_to_block, MATRIX_ROWS, MATRIX_COLS, BLOCK_SIZE
from margolus_ca import (
    apply_margolus_forward,
    apply_margolus_inverse,
    neighborhood_to_state,
    state_to_neighborhood,
    FORWARD_RULE,
    INVERSE_RULE,
)


def test_single_neighborhood_reversibility() -> Tuple[bool, str]:
    """
    TEST 1 — Single 2x2 neighborhood reversibility.
    For every 4-bit neighborhood state integer from 0 to 15:
    1. Create a 16x16 matrix with top-left neighborhood set to the 4-bit state.
    2. Apply standard Margolus forward transformation.
    3. Apply standard Margolus inverse transformation.
    4. Verify exact recovery of the 2x2 state and full matrix.
    """
    for state in range(16):
        matrix = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
        state_to_neighborhood(matrix, 0, 0, state)

        fwd_matrix = apply_margolus_forward(matrix)
        recovered_matrix = apply_margolus_inverse(fwd_matrix)

        rec_state = neighborhood_to_state(recovered_matrix, 0, 0)
        if rec_state != state or recovered_matrix != matrix:
            return False, f"Failed at state 0x{state:X}: expected state 0x{state:X}, got 0x{rec_state:X}."

    return True, "All 16 single 2x2 neighborhood states passed."


def test_all_zero_matrix() -> Tuple[bool, str]:
    """
    TEST 2 — All-zero 16x16 matrix reversibility.
    """
    matrix = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    fwd_matrix = apply_margolus_forward(matrix)
    recovered_matrix = apply_margolus_inverse(fwd_matrix)

    is_equal = (matrix == recovered_matrix)
    msg = "All-zero matrix round-trip match: PASS" if is_equal else "All-zero matrix round-trip match: FAIL"
    return is_equal, msg


def test_all_one_matrix() -> Tuple[bool, str]:
    """
    TEST 3 — All-one 16x16 matrix reversibility.
    """
    matrix = [[1] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    fwd_matrix = apply_margolus_forward(matrix)
    recovered_matrix = apply_margolus_inverse(fwd_matrix)

    is_equal = (matrix == recovered_matrix)
    msg = "All-one matrix round-trip match: PASS" if is_equal else "All-one matrix round-trip match: FAIL"
    return is_equal, msg


def test_checkerboard_matrix() -> Tuple[bool, str]:
    """
    TEST 4 — Checkerboard 16x16 matrix reversibility.
    """
    matrix = [[(r + c) % 2 for c in range(MATRIX_COLS)] for r in range(MATRIX_ROWS)]
    fwd_matrix = apply_margolus_forward(matrix)
    recovered_matrix = apply_margolus_inverse(fwd_matrix)

    is_equal = (matrix == recovered_matrix)
    msg = "Checkerboard matrix round-trip match: PASS" if is_equal else "Checkerboard matrix round-trip match: FAIL"
    return is_equal, msg


def test_random_matrices(count: int = 100, seed: int = 42) -> Tuple[int, int, float, List]:
    """
    TEST 5 — Random 16x16 binary matrices reversibility test.
    Generates `count` deterministic random 16x16 matrices.
    """
    rng = random.Random(seed)
    passed = 0
    failed = 0
    failures = []

    for i in range(count):
        matrix = [[rng.randint(0, 1) for _ in range(MATRIX_COLS)] for _ in range(MATRIX_ROWS)]
        fwd = apply_margolus_forward(matrix)
        inv = apply_margolus_inverse(fwd)

        if inv == matrix:
            passed += 1
        else:
            failed += 1
            failures.append((i, matrix, fwd, inv))

    reversibility_pct = (passed / count) * 100.0
    return passed, failed, reversibility_pct, failures


def test_block_interface(count: int = 100, seed: int = 42) -> Tuple[int, int, float, List]:
    """
    TEST 6 — 256-bit block interface round-trip test.
    Generates `count` deterministic random 256-bit binary strings.
    """
    rng = random.Random(seed)
    passed = 0
    failed = 0
    failures = []

    for i in range(count):
        block = "".join(str(rng.randint(0, 1)) for _ in range(BLOCK_SIZE))

        matrix = block_to_matrix(block)
        fwd_matrix = apply_margolus_forward(matrix)
        inv_matrix = apply_margolus_inverse(fwd_matrix)
        recovered_block = matrix_to_block(inv_matrix)

        if recovered_block == block:
            passed += 1
        else:
            failed += 1
            failures.append((i, block, recovered_block))

    pct = (passed / count) * 100.0
    return passed, failed, pct, failures


def main() -> None:
    print("=" * 60)
    print(" STANDARD 2x2 MARGOLUS CA TRANSFORMATION VALIDATION ")
    print("=" * 60)

    # TEST 1
    t1_pass, t1_msg = test_single_neighborhood_reversibility()
    print(f"\nTEST 1 — Single 2x2 Neighborhood Reversibility:")
    print(f"  {t1_msg}")

    # TEST 2
    t2_pass, t2_msg = test_all_zero_matrix()
    print(f"\nTEST 2 — All-Zero Matrix Test:")
    print(f"  {t2_msg}")

    # TEST 3
    t3_pass, t3_msg = test_all_one_matrix()
    print(f"\nTEST 3 — All-One Matrix Test:")
    print(f"  {t3_msg}")

    # TEST 4
    t4_pass, t4_msg = test_checkerboard_matrix()
    print(f"\nTEST 4 — Checkerboard Matrix Test:")
    print(f"  {t4_msg}")

    # TEST 5
    rand_pass, rand_fail, rand_pct, rand_failures = test_random_matrices(count=100, seed=42)
    print(f"\nTEST 5 — Random 16x16 Binary Matrices (100 runs, seed=42):")
    print(f"  Passed: {rand_pass}/100 ({rand_pct:.2f}%)")
    print(f"  Failed: {rand_fail}/100")

    # TEST 6
    block_pass, block_fail, block_pct, block_failures = test_block_interface(count=100, seed=42)
    print(f"\nTEST 6 — 256-Bit Block Interface Round-Trip (100 runs, seed=42):")
    print(f"  Passed: {block_pass}/100 ({block_pct:.2f}%)")
    print(f"  Failed: {block_fail}/100")

    overall_pass = (
        t1_pass
        and t2_pass
        and t3_pass
        and t4_pass
        and (rand_fail == 0)
        and (block_fail == 0)
    )

    print("\n" + "=" * 40)
    print("STANDARD MARGOLUS VALIDATION")
    print("=" * 40)
    print(f"Single 2x2 exhaustive test: {'PASS' if t1_pass else 'FAIL'}")
    print(f"All-zero matrix test: {'PASS' if t2_pass else 'FAIL'}")
    print(f"All-one matrix test: {'PASS' if t3_pass else 'FAIL'}")
    print(f"Checkerboard test: {'PASS' if t4_pass else 'FAIL'}")
    print(f"Random 16x16 matrices: {rand_pass}/100 PASS")
    print(f"256-bit block round-trip: {block_pass}/100 PASS")
    print(f"\nOverall validation: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 40)

    if not overall_pass:
        print("\nFAILURE DETAILS:")
        if not t1_pass:
            print(f"TEST 1 Failure: {t1_msg}")
        if rand_failures:
            first_fail = rand_failures[0]
            print(f"First failing random matrix test (Index {first_fail[0]}):")
            print(f"  Original: {first_fail[1]}")
            print(f"  Transformed: {first_fail[2]}")
            print(f"  Recovered: {first_fail[3]}")
        if block_failures:
            first_fail = block_failures[0]
            print(f"First failing 256-bit block test (Index {first_fail[0]}):")
            print(f"  Original:  {first_fail[1]}")
            print(f"  Recovered: {first_fail[2]}")


if __name__ == "__main__":
    main()
