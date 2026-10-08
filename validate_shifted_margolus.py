"""
Module: validate_shifted_margolus.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Programmatic validation of the shifted 2x2 Margolus Cellular Automata
         transformation functions (apply_shifted_margolus_forward & apply_shifted_margolus_inverse).
"""

import random
from typing import List, Tuple
from ca_matrix import block_to_matrix, matrix_to_block, MATRIX_ROWS, MATRIX_COLS, BLOCK_SIZE
from margolus_ca import FORWARD_RULE, INVERSE_RULE
from margolus_shifted import (
    apply_shifted_margolus_forward,
    apply_shifted_margolus_inverse,
    shifted_neighborhood_to_state,
    state_to_shifted_neighborhood,
    SHIFTED_ROWS,
    SHIFTED_COLS,
)


def test_single_shifted_neighborhood_behavior() -> Tuple[bool, str]:
    """
    TEST 1 — Single shifted neighborhood behavior test.
    For every 4-bit neighborhood state integer from 0 to 15,
    test single shifted neighborhood at (1, 1) and boundary neighborhood (15, 15).
    """
    for state in range(16):
        # Test at (1, 1)
        matrix = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
        state_to_shifted_neighborhood(matrix, 1, 1, state)
        fwd = apply_shifted_margolus_forward(matrix)
        rec = apply_shifted_margolus_inverse(fwd)
        if rec != matrix:
            return False, f"Failed at state 0x{state:X} for shifted position (1, 1)."

        # Test at boundary (15, 15)
        matrix_b = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
        state_to_shifted_neighborhood(matrix_b, 15, 15, state)
        fwd_b = apply_shifted_margolus_forward(matrix_b)
        rec_b = apply_shifted_margolus_inverse(fwd_b)
        if rec_b != matrix_b:
            return False, f"Failed at state 0x{state:X} for boundary position (15, 15)."

    return True, "All 16 single shifted neighborhood states passed for (1,1) and (15,15)."


def test_all_zero_matrix() -> Tuple[bool, str]:
    """
    TEST 2 — All-zero 16x16 matrix shifted reversibility.
    """
    matrix = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    fwd = apply_shifted_margolus_forward(matrix)
    rec = apply_shifted_margolus_inverse(fwd)

    is_equal = (matrix == rec)
    msg = "All-zero matrix round-trip match: PASS" if is_equal else "All-zero matrix round-trip match: FAIL"
    return is_equal, msg


def test_all_one_matrix() -> Tuple[bool, str]:
    """
    TEST 3 — All-one 16x16 matrix shifted reversibility.
    """
    matrix = [[1] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    fwd = apply_shifted_margolus_forward(matrix)
    rec = apply_shifted_margolus_inverse(fwd)

    is_equal = (matrix == rec)
    msg = "All-one matrix round-trip match: PASS" if is_equal else "All-one matrix round-trip match: FAIL"
    return is_equal, msg


def test_checkerboard_matrix() -> Tuple[bool, str]:
    """
    TEST 4 — Checkerboard 16x16 matrix shifted reversibility.
    matrix[r][c] = (r + c) % 2
    """
    matrix = [[(r + c) % 2 for c in range(MATRIX_COLS)] for r in range(MATRIX_ROWS)]
    fwd = apply_shifted_margolus_forward(matrix)
    rec = apply_shifted_margolus_inverse(fwd)

    is_equal = (matrix == rec)
    msg = "Checkerboard matrix round-trip match: PASS" if is_equal else "Checkerboard matrix round-trip match: FAIL"
    return is_equal, msg


def test_random_matrices(count: int = 100, seed: int = 42) -> Tuple[int, int, float, List]:
    """
    TEST 5 — Random 16x16 binary matrices shifted reversibility test.
    Generates `count` deterministic random 16x16 matrices.
    """
    rng = random.Random(seed)
    passed = 0
    failed = 0
    failures = []

    for i in range(count):
        matrix = [[rng.randint(0, 1) for _ in range(MATRIX_COLS)] for _ in range(MATRIX_ROWS)]
        fwd = apply_shifted_margolus_forward(matrix)
        inv = apply_shifted_margolus_inverse(fwd)

        if inv == matrix:
            passed += 1
        else:
            failed += 1
            failures.append((i, matrix, fwd, inv))

    reversibility_pct = (passed / count) * 100.0
    return passed, failed, reversibility_pct, failures


def test_block_interface(count: int = 100, seed: int = 42) -> Tuple[int, int, float, List]:
    """
    TEST 6 — 256-bit block interface shifted round-trip test.
    Generates `count` deterministic random 256-bit binary strings.
    """
    rng = random.Random(seed)
    passed = 0
    failed = 0
    failures = []

    for i in range(count):
        block = "".join(str(rng.randint(0, 1)) for _ in range(BLOCK_SIZE))

        matrix = block_to_matrix(block)
        fwd_matrix = apply_shifted_margolus_forward(matrix)
        inv_matrix = apply_shifted_margolus_inverse(fwd_matrix)
        recovered_block = matrix_to_block(inv_matrix)

        if recovered_block == block:
            passed += 1
        else:
            failed += 1
            failures.append((i, block, recovered_block))

    pct = (passed / count) * 100.0
    return passed, failed, pct, failures


def test_boundary_wraparound() -> Tuple[int, int, List]:
    """
    TEST 7 — Boundary and periodic wrap-around test patterns.
    Tests sparse patterns specifically placing bits on boundaries (rows 0, 15; cols 0, 15; corners).
    """
    boundary_patterns = []

    # Pattern 1: Single bit at corner (0, 0)
    p1 = [[0] * 16 for _ in range(16)]
    p1[0][0] = 1
    boundary_patterns.append(("Corner (0,0)", p1))

    # Pattern 2: Single bit at corner (15, 15)
    p2 = [[0] * 16 for _ in range(16)]
    p2[15][15] = 1
    boundary_patterns.append(("Corner (15,15)", p2))

    # Pattern 3: All 4 corners set to 1
    p3 = [[0] * 16 for _ in range(16)]
    p3[0][0] = 1
    p3[0][15] = 1
    p3[15][0] = 1
    p3[15][15] = 1
    boundary_patterns.append(("All 4 Corners", p3))

    # Pattern 4: Top row (row 0) alternating
    p4 = [[0] * 16 for _ in range(16)]
    for c in range(16):
        p4[0][c] = c % 2
    boundary_patterns.append(("Top Row Alternating", p4))

    # Pattern 5: Bottom row (row 15) alternating
    p5 = [[0] * 16 for _ in range(16)]
    for c in range(16):
        p5[15][c] = (c + 1) % 2
    boundary_patterns.append(("Bottom Row Alternating", p5))

    # Pattern 6: Left column (col 0) alternating
    p6 = [[0] * 16 for _ in range(16)]
    for r in range(16):
        p6[r][0] = r % 2
    boundary_patterns.append(("Left Column Alternating", p6))

    # Pattern 7: Right column (col 15) alternating
    p7 = [[0] * 16 for _ in range(16)]
    for r in range(16):
        p7[r][15] = (r + 1) % 2
    boundary_patterns.append(("Right Column Alternating", p7))

    # Pattern 8: Outer boundary frame (row 0, row 15, col 0, col 15 all set to 1)
    p8 = [[0] * 16 for _ in range(16)]
    for i in range(16):
        p8[0][i] = 1
        p8[15][i] = 1
        p8[i][0] = 1
        p8[i][15] = 1
    boundary_patterns.append(("Outer Boundary Frame", p8))

    passed = 0
    failed = 0
    failures = []

    for label, matrix in boundary_patterns:
        fwd = apply_shifted_margolus_forward(matrix)
        rec = apply_shifted_margolus_inverse(fwd)
        if rec == matrix:
            passed += 1
        else:
            failed += 1
            failures.append((label, matrix, fwd, rec))

    return passed, len(boundary_patterns), failures


def main() -> None:
    print("=" * 60)
    print(" SHIFTED 2x2 MARGOLUS CA TRANSFORMATION VALIDATION ")
    print("=" * 60)

    # TEST 1
    t1_pass, t1_msg = test_single_shifted_neighborhood_behavior()
    print(f"\nTEST 1 — Single Shifted Neighborhood Behavior:")
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

    # TEST 7
    bnd_pass, bnd_total, bnd_failures = test_boundary_wraparound()
    print(f"\nTEST 7 — Boundary and Periodic Wrap-Around Test Patterns:")
    print(f"  Passed: {bnd_pass}/{bnd_total}")
    print(f"  Failed: {len(bnd_failures)}")

    overall_pass = (
        t1_pass
        and t2_pass
        and t3_pass
        and t4_pass
        and (rand_fail == 0)
        and (block_fail == 0)
        and (len(bnd_failures) == 0)
    )

    print("\n" + "=" * 40)
    print("SHIFTED MARGOLUS VALIDATION")
    print("=" * 40)
    print(f"All-zero matrix: {'PASS' if t2_pass else 'FAIL'}")
    print(f"All-one matrix: {'PASS' if t3_pass else 'FAIL'}")
    print(f"Checkerboard: {'PASS' if t4_pass else 'FAIL'}")
    print(f"Random 16x16 matrices: {rand_pass}/100 PASS")
    print(f"256-bit block round-trip: {block_pass}/100 PASS")
    print(f"Boundary/wrap-around tests: {bnd_pass}/{bnd_total} PASS")
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
        if bnd_failures:
            first_fail = bnd_failures[0]
            print(f"First failing boundary pattern test ({first_fail[0]}):")
            print(f"  Original:  {first_fail[1]}")
            print(f"  Recovered: {first_fail[3]}")


if __name__ == "__main__":
    main()
