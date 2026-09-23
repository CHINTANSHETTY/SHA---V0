"""
Module: margolus_ca.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone implementation of one non-shifted 2x2 Margolus Cellular-Automata
         transformation step over a 16x16 binary matrix.

Processes 64 non-overlapping 2x2 neighborhoods using the cryptographically optimal
reversible 4-bit local rule (FORWARD_RULE & INVERSE_RULE).
"""

from typing import List
from ca_matrix import validate_matrix as validate_16x16_matrix, MATRIX_ROWS, MATRIX_COLS

# =========================================================
# REVERSIBLE 4-BIT LOCAL RULE TABLES (Candidate B / PICCOLO Optimal CA)
# =========================================================

FORWARD_RULE: List[int] = [
    0x0E, 0x04, 0x0B, 0x02,
    0x03, 0x08, 0x00, 0x09,
    0x01, 0x0A, 0x07, 0x0F,
    0x06, 0x0C, 0x05, 0x0D
]

INVERSE_RULE: List[int] = [
    0x06, 0x08, 0x03, 0x04,
    0x01, 0x0E, 0x0C, 0x0A,
    0x05, 0x07, 0x09, 0x02,
    0x0D, 0x0F, 0x00, 0x0B
]


def neighborhood_to_state(matrix: List[List[int]], row: int, col: int) -> int:
    """
    Extracts a 4-bit state integer from a 2x2 neighborhood at top-left corner (row, col).
    Row-major bit ordering inside 2x2 block:
      bit0 = matrix[row][col]     (MSB, << 3)
      bit1 = matrix[row][col+1]   (<< 2)
      bit2 = matrix[row+1][col]   (<< 1)
      bit3 = matrix[row+1][col+1] (LSB, << 0)
    """
    bit0 = matrix[row][col]
    bit1 = matrix[row][col + 1]
    bit2 = matrix[row + 1][col]
    bit3 = matrix[row + 1][col + 1]

    return (bit0 << 3) | (bit1 << 2) | (bit2 << 1) | bit3


def state_to_neighborhood(matrix: List[List[int]], row: int, col: int, state: int) -> None:
    """
    Writes a 4-bit state integer back into a 2x2 neighborhood at top-left corner (row, col).
    Row-major bit ordering:
      matrix[row][col]     = (state >> 3) & 1
      matrix[row][col+1]   = (state >> 2) & 1
      matrix[row+1][col]   = (state >> 1) & 1
      matrix[row+1][col+1] = state & 1
    """
    matrix[row][col] = (state >> 3) & 1
    matrix[row][col + 1] = (state >> 2) & 1
    matrix[row + 1][col] = (state >> 1) & 1
    matrix[row + 1][col + 1] = state & 1


def apply_margolus_forward(matrix: List[List[int]]) -> List[List[int]]:
    """
    Applies non-shifted 2x2 Margolus forward transformation to a 16x16 matrix.
    Partition: 64 non-overlapping 2x2 blocks (r, c in {0, 2, 4, ..., 14}).

    Returns:
        A NEW 16x16 binary matrix containing the transformed state.
    """
    validate_16x16_matrix(matrix)

    # Create deep copy for output matrix
    output_matrix = [row[:] for row in matrix]

    for r in range(0, MATRIX_ROWS, 2):
        for c in range(0, MATRIX_COLS, 2):
            curr_state = neighborhood_to_state(matrix, r, c)
            next_state = FORWARD_RULE[curr_state]
            state_to_neighborhood(output_matrix, r, c, next_state)

    return output_matrix


def apply_margolus_inverse(matrix: List[List[int]]) -> List[List[int]]:
    """
    Applies non-shifted 2x2 Margolus inverse transformation to a 16x16 matrix.
    Partition: 64 non-overlapping 2x2 blocks (r, c in {0, 2, 4, ..., 14}).

    Returns:
        A NEW 16x16 binary matrix containing the recovered original state.
    """
    validate_16x16_matrix(matrix)

    # Create deep copy for output matrix
    output_matrix = [row[:] for row in matrix]

    for r in range(0, MATRIX_ROWS, 2):
        for c in range(0, MATRIX_COLS, 2):
            curr_state = neighborhood_to_state(matrix, r, c)
            prev_state = INVERSE_RULE[curr_state]
            state_to_neighborhood(output_matrix, r, c, prev_state)

    return output_matrix


def run_demo() -> None:
    """Runs demonstration of margolus_ca module functions and prints results."""
    print("=" * 80)
    print(" NON-SHIFTED 2x2 MARGOLUS CELLULAR AUTOMATA MODULE DEMONSTRATION")
    print("=" * 80)

    # Create sample 16x16 matrix (all zeros except top-left 2x2 block = 0xB)
    sample_matrix = [[0] * 16 for _ in range(16)]
    # Top-left neighborhood (0, 0): [1 0 / 1 1] -> 0xB
    sample_matrix[0][0] = 1
    sample_matrix[0][1] = 0
    sample_matrix[1][0] = 1
    sample_matrix[1][1] = 1

    input_state_0 = neighborhood_to_state(sample_matrix, 0, 0)
    print(f"\n1. Initial Top-Left (0, 0) Neighborhood State: 0x{input_state_0:X} ({format(input_state_0, '04b')})")

    # Apply Forward Margolus Transformation
    forward_matrix = apply_margolus_forward(sample_matrix)
    forward_state_0 = neighborhood_to_state(forward_matrix, 0, 0)
    expected_forward = FORWARD_RULE[input_state_0]

    print(f"2. Forward Transformed State at (0, 0):        0x{forward_state_0:X} ({format(forward_state_0, '04b')})")
    print(f"   Expected Forward Output:                    0x{expected_forward:X} ({format(expected_forward, '04b')})")
    print(f"   Match: {forward_state_0 == expected_forward}")

    # Apply Inverse Margolus Transformation
    recovered_matrix = apply_margolus_inverse(forward_matrix)
    roundtrip_match = (sample_matrix == recovered_matrix)

    print(f"\n3. Round-Trip Verification (apply_margolus_inverse(apply_margolus_forward(M)) == M):")
    print(f"   Exact Reconstructed Match: {roundtrip_match}")

    if roundtrip_match:
        print("   SUCCESS: Non-shifted 2x2 Margolus transformation is 100% loss-less and reversible!")
    else:
        print("   FAILURE: Mismatch detected in Margolus transformation round-trip.")

    print("=" * 80)


if __name__ == "__main__":
    run_demo()
