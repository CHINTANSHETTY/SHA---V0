"""
Module: ca_transform.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Candidate C Architecture — 10-round reversible 2x2 Margolus cellular automata block transform
         with alternating standard/shifted Margolus partitions and 2D circular matrix shifts (2, 2).

Pipeline Summary (R rounds, default R=10):
  Forward:
    For r = 1..rounds:
      1. Apply standard Margolus partition on odd rounds (apply_margolus_forward)
      2. Apply shifted Margolus partition on even rounds (apply_shifted_margolus_forward)
      3. Apply circular matrix shift DOWN 2 and RIGHT 2 after EVERY round (circular_shift_matrix row_shift=2, col_shift=2)
  Inverse:
    For r = rounds..1:
      1. Apply inverse circular matrix shift UP 2 and LEFT 2 (inverse_circular_shift_matrix row_shift=2, col_shift=2)
      2. Apply corresponding inverse Margolus partition for round r (apply_margolus_inverse if odd, apply_shifted_margolus_inverse if even)
"""

from typing import List
from ca_matrix import (
    block_to_matrix,
    matrix_to_block,
    validate_block,
    validate_matrix,
    MATRIX_ROWS,
    MATRIX_COLS,
    BLOCK_SIZE,
)
from margolus_ca import apply_margolus_forward, apply_margolus_inverse
from margolus_shifted import apply_shifted_margolus_forward, apply_shifted_margolus_inverse

# Default round count for production Candidate C architecture
DEFAULT_ROUNDS: int = 10


def circular_shift_matrix(
    matrix: List[List[int]],
    row_shift: int = 2,
    col_shift: int = 2
) -> List[List[int]]:
    """
    Performs a 2D circular shift on a 16x16 binary matrix.
    Default shift: DOWN by row_shift=2, RIGHT by col_shift=2.

    Formula:
      shifted[r][c] = matrix[(r - row_shift) % 16][(c - col_shift) % 16]

    Args:
        matrix: 16x16 binary integer matrix.
        row_shift: Number of rows to shift down (default 2).
        col_shift: Number of columns to shift right (default 2).

    Returns:
        A NEW 16x16 circularly shifted matrix.
    """
    validate_matrix(matrix)

    shifted = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    for r in range(MATRIX_ROWS):
        for c in range(MATRIX_COLS):
            shifted[r][c] = matrix[(r - row_shift) % MATRIX_ROWS][(c - col_shift) % MATRIX_COLS]

    return shifted


def inverse_circular_shift_matrix(
    matrix: List[List[int]],
    row_shift: int = 2,
    col_shift: int = 2
) -> List[List[int]]:
    """
    Reverses the 2D circular shift on a 16x16 binary matrix.
    Default inverse shift: UP by row_shift=2, LEFT by col_shift=2.

    Formula:
      restored[r][c] = shifted[(r + row_shift) % 16][(c + col_shift) % 16]

    Args:
        matrix: 16x16 binary integer matrix.
        row_shift: Number of rows to shift up (default 2).
        col_shift: Number of columns to shift left (default 2).

    Returns:
        A NEW 16x16 restored matrix.
    """
    validate_matrix(matrix)

    restored = [[0] * MATRIX_COLS for _ in range(MATRIX_ROWS)]
    for r in range(MATRIX_ROWS):
        for c in range(MATRIX_COLS):
            restored[r][c] = matrix[(r + row_shift) % MATRIX_ROWS][(c + col_shift) % MATRIX_COLS]

    return restored


def transform_block_forward(block: str, rounds: int = DEFAULT_ROUNDS) -> str:
    """
    Applies the Candidate C reversible 2x2 Margolus CA forward transformation pipeline to a 256-bit block.

    Pipeline Steps (for r = 1..rounds):
      1. Convert 256-bit block to 16x16 matrix (block_to_matrix)
      2. For each round r:
           a. Odd rounds: Standard 2x2 Margolus CA forward (apply_margolus_forward)
           b. Even rounds: Shifted 2x2 Margolus CA forward (apply_shifted_margolus_forward)
           c. 2D Circular Shift: DOWN 2 rows, RIGHT 2 columns (circular_shift_matrix row_shift=2, col_shift=2)
      3. Convert 16x16 matrix back to 256-bit block (matrix_to_block)

    Args:
        block: 256-character binary string ('0' or '1').
        rounds: Number of CA transformation rounds (default 10).

    Returns:
        Transformed 256-character binary string.
    """
    validate_block(block)

    matrix = block_to_matrix(block)
    for r in range(1, rounds + 1):
        if r % 2 != 0:
            matrix = apply_margolus_forward(matrix)
        else:
            matrix = apply_shifted_margolus_forward(matrix)
        matrix = circular_shift_matrix(matrix, row_shift=2, col_shift=2)

    return matrix_to_block(matrix)


def transform_block_inverse(block: str, rounds: int = DEFAULT_ROUNDS) -> str:
    """
    Reverses the Candidate C reversible 2x2 Margolus CA forward transformation pipeline for a 256-bit block.

    Pipeline Steps (for r = rounds..1):
      1. Convert 256-bit block to 16x16 matrix (block_to_matrix)
      2. For each round r in reverse:
           a. Inverse 2D Circular Shift: UP 2 rows, LEFT 2 columns (inverse_circular_shift_matrix row_shift=2, col_shift=2)
           b. Odd rounds: Standard 2x2 Margolus CA inverse (apply_margolus_inverse)
           c. Even rounds: Shifted 2x2 Margolus CA inverse (apply_shifted_margolus_inverse)
      3. Convert 16x16 matrix back to 256-bit block (matrix_to_block)

    Args:
        block: Transformed 256-character binary string.
        rounds: Number of CA transformation rounds (default 10).

    Returns:
        Original 256-character binary string.
    """
    validate_block(block)

    matrix = block_to_matrix(block)
    for r in range(rounds, 0, -1):
        matrix = inverse_circular_shift_matrix(matrix, row_shift=2, col_shift=2)
        if r % 2 != 0:
            matrix = apply_margolus_inverse(matrix)
        else:
            matrix = apply_shifted_margolus_inverse(matrix)

    return matrix_to_block(matrix)


def run_demo() -> None:
    """Runs demonstration of ca_transform Candidate C 10-round block transform."""
    print("=" * 80)
    print(" CANDIDATE C 10-ROUND 2x2 MARGOLUS CA BLOCK TRANSFORM MODULE DEMONSTRATION")
    print("=" * 80)

    sample_block = ("01" * 64 + "1100" * 32)[:256]

    print(f"\n1. Input Block Length:   {len(sample_block)} bits")
    print(f"   First 32 bits:       {sample_block[:32]}...")

    # Apply Complete Forward CA Block Transformation (10 rounds)
    transformed_block = transform_block_forward(sample_block)
    print(f"\n2. Transformed Block:    {transformed_block[:32]}...")
    print(f"   Length:              {len(transformed_block)} bits")
    print(f"   Block Changed:       {sample_block != transformed_block}")

    # Apply Complete Inverse CA Block Transformation (10 rounds)
    recovered_block = transform_block_inverse(transformed_block)
    roundtrip_match = (sample_block == recovered_block)

    print(f"\n3. Round-Trip Verification:")
    print(f"   Reconstructed Match: {roundtrip_match}")

    if roundtrip_match:
        print("   SUCCESS: Candidate C 10-Round Margolus CA + Shift (2,2) Block Transform is 100% loss-less!")
    else:
        print("   FAILURE: Block transformation round-trip mismatch detected.")

    print("=" * 80)


if __name__ == "__main__":
    run_demo()

