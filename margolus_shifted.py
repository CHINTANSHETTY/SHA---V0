"""
Module: margolus_shifted.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone implementation of the SECOND (shifted by 1 cell in both dimensions
         with periodic wrap-around) 2x2 Margolus Cellular-Automata transformation step
         over a 16x16 binary matrix.

Processes 64 non-overlapping shifted 2x2 neighborhoods using periodic modulo-16 addressing
and the optimal reversible 4-bit local rule (FORWARD_RULE & INVERSE_RULE).
"""

from typing import List, Tuple
from ca_matrix import validate_matrix as validate_16x16_matrix, MATRIX_ROWS, MATRIX_COLS
from margolus_ca import FORWARD_RULE, INVERSE_RULE

# Top-left coordinates for the shifted partition (offset = 1)
SHIFTED_ROWS: List[int] = [1, 3, 5, 7, 9, 11, 13, 15]
SHIFTED_COLS: List[int] = [1, 3, 5, 7, 9, 11, 13, 15]


def shifted_neighborhood_to_state(matrix: List[List[int]], row: int, col: int) -> int:
    """
    Extracts a 4-bit state integer from a shifted 2x2 neighborhood at top-left corner (row, col)
    using periodic modulo-16 addressing for boundary wrap-around.

    Coordinates:
      top_left     = matrix[row % 16][col % 16]          (MSB, << 3)
      top_right    = matrix[row % 16][(col + 1) % 16]    (<< 2)
      bottom_left  = matrix[(row + 1) % 16][col % 16]    (<< 1)
      bottom_right = matrix[(row + 1) % 16][(col + 1) % 16] (LSB, << 0)
    """
    top_left = matrix[row % MATRIX_ROWS][col % MATRIX_COLS]
    top_right = matrix[row % MATRIX_ROWS][(col + 1) % MATRIX_COLS]
    bottom_left = matrix[(row + 1) % MATRIX_ROWS][col % MATRIX_COLS]
    bottom_right = matrix[(row + 1) % MATRIX_ROWS][(col + 1) % MATRIX_COLS]

    return (top_left << 3) | (top_right << 2) | (bottom_left << 1) | bottom_right


def state_to_shifted_neighborhood(matrix: List[List[int]], row: int, col: int, state: int) -> None:
    """
    Writes a 4-bit state integer back into a shifted 2x2 neighborhood at top-left corner (row, col)
    using periodic modulo-16 addressing for boundary wrap-around.
    """
    matrix[row % MATRIX_ROWS][col % MATRIX_COLS] = (state >> 3) & 1
    matrix[row % MATRIX_ROWS][(col + 1) % MATRIX_COLS] = (state >> 2) & 1
    matrix[(row + 1) % MATRIX_ROWS][col % MATRIX_COLS] = (state >> 1) & 1
    matrix[(row + 1) % MATRIX_ROWS][(col + 1) % MATRIX_COLS] = state & 1


def get_shifted_neighborhood_cells(row: int, col: int) -> List[Tuple[int, int]]:
    """
    Returns the exact 4 grid cell coordinates (r, c) belonging to the shifted
    neighborhood with top-left corner (row, col) using modulo-16 addressing.
    """
    return [
        (row % MATRIX_ROWS, col % MATRIX_COLS),
        (row % MATRIX_ROWS, (col + 1) % MATRIX_COLS),
        ((row + 1) % MATRIX_ROWS, col % MATRIX_COLS),
        ((row + 1) % MATRIX_ROWS, (col + 1) % MATRIX_COLS),
    ]


def apply_shifted_margolus_forward(matrix: List[List[int]]) -> List[List[int]]:
    """
    Applies the SECOND (shifted by 1 cell with periodic wrap-around) 2x2 Margolus
    forward transformation to a 16x16 matrix.
    Partition: 64 non-overlapping shifted 2x2 blocks (r, c in {1, 3, 5, ..., 15}).

    Returns:
        A NEW 16x16 binary matrix containing the transformed state.
    """
    validate_16x16_matrix(matrix)

    output_matrix = [row[:] for row in matrix]

    for r in SHIFTED_ROWS:
        for c in SHIFTED_COLS:
            curr_state = shifted_neighborhood_to_state(matrix, r, c)
            next_state = FORWARD_RULE[curr_state]
            state_to_shifted_neighborhood(output_matrix, r, c, next_state)

    return output_matrix


def apply_shifted_margolus_inverse(matrix: List[List[int]]) -> List[List[int]]:
    """
    Applies the SECOND (shifted by 1 cell with periodic wrap-around) 2x2 Margolus
    inverse transformation to a 16x16 matrix.
    Partition: 64 non-overlapping shifted 2x2 blocks (r, c in {1, 3, 5, ..., 15}).

    Returns:
        A NEW 16x16 binary matrix containing the recovered original state.
    """
    validate_16x16_matrix(matrix)

    output_matrix = [row[:] for row in matrix]

    for r in SHIFTED_ROWS:
        for c in SHIFTED_COLS:
            curr_state = shifted_neighborhood_to_state(matrix, r, c)
            prev_state = INVERSE_RULE[curr_state]
            state_to_shifted_neighborhood(output_matrix, r, c, prev_state)

    return output_matrix


def run_demo() -> None:
    """Runs demonstration of margolus_shifted module functions and prints results."""
    print("=" * 80)
    print(" SHIFTED (SECOND PARTITION) 2x2 MARGOLUS CA MODULE DEMONSTRATION")
    print("=" * 80)

    # Demonstrate Boundary Wrap-around at (15, 15)
    sample_matrix = [[0] * 16 for _ in range(16)]
    # Set cells for shifted neighborhood (15, 15):
    # (15, 15)=1, (15, 0)=0, (0, 15)=1, (0, 0)=1 -> 1011_2 = 0xB
    sample_matrix[15][15] = 1
    sample_matrix[15][0] = 0
    sample_matrix[0][15] = 1
    sample_matrix[0][0] = 1

    boundary_state = shifted_neighborhood_to_state(sample_matrix, 15, 15)
    print(f"\n1. Boundary Neighborhood (15, 15) Wrap-Around Cells:")
    print(f"   Top-Left (15, 15):   {sample_matrix[15][15]}")
    print(f"   Top-Right (15, 0):   {sample_matrix[15][0]}")
    print(f"   Bottom-Left (0, 15): {sample_matrix[0][15]}")
    print(f"   Bottom-Right (0, 0): {sample_matrix[0][0]}")
    print(f"   Extracted 4-Bit State: 0x{boundary_state:X} ({format(boundary_state, '04b')})")

    # Apply Forward Shifted Margolus Transformation
    forward_matrix = apply_shifted_margolus_forward(sample_matrix)
    forward_state = shifted_neighborhood_to_state(forward_matrix, 15, 15)
    expected_forward = FORWARD_RULE[boundary_state]

    print(f"\n2. Forward Transformed Shifted State at (15, 15): 0x{forward_state:X} ({format(forward_state, '04b')})")
    print(f"   Expected Forward Output:                         0x{expected_forward:X} ({format(expected_forward, '04b')})")
    print(f"   Match: {forward_state == expected_forward}")

    # Apply Inverse Shifted Margolus Transformation
    recovered_matrix = apply_shifted_margolus_inverse(forward_matrix)
    roundtrip_match = (sample_matrix == recovered_matrix)

    print(f"\n3. Round-Trip Verification (apply_shifted_margolus_inverse(apply_shifted_margolus_forward(M)) == M):")
    print(f"   Exact Reconstructed Match: {roundtrip_match}")

    if roundtrip_match:
        print("   SUCCESS: Shifted 2x2 Margolus transformation is 100% loss-less and reversible!")
    else:
        print("   FAILURE: Mismatch detected in shifted Margolus transformation round-trip.")

    print("=" * 80)


if __name__ == "__main__":
    run_demo()
