"""
Module: ca_matrix.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone matrix conversion module for 256-bit binary block <-> 16x16 binary matrix.

Provides exact bidirectional mapping:
  - block_to_matrix(block: str) -> list[list[int]]
  - matrix_to_block(matrix: list[list[int]]) -> str
  - validate_block(block: str) -> None
  - validate_matrix(matrix: list[list[int]]) -> None
"""

from typing import List

MATRIX_ROWS: int = 16
MATRIX_COLS: int = 16
BLOCK_SIZE: int = 256


def validate_block(block: str) -> None:
    """
    Validates a 256-bit binary string block.

    Raises:
        ValueError: If block is not a string, not 256 chars long,
                    or contains characters other than '0' or '1'.
    """
    if not isinstance(block, str):
        raise ValueError(f"Block must be a string, got {type(block).__name__}.")

    if len(block) != BLOCK_SIZE:
        raise ValueError(
            f"Invalid block length {len(block)}. Block must be exactly {BLOCK_SIZE} bits."
        )

    for idx, char in enumerate(block):
        if char not in ("0", "1"):
            raise ValueError(
                f"Invalid character '{char}' at index {idx}. Block must contain only '0' or '1'."
            )


def validate_matrix(matrix: List[List[int]]) -> None:
    """
    Validates a 16x16 binary integer matrix.

    Raises:
        ValueError: If matrix is not a list of 16 lists of 16 integers,
                    or contains values other than 0 or 1.
    """
    if not isinstance(matrix, list):
        raise ValueError(f"Matrix must be a list, got {type(matrix).__name__}.")

    if len(matrix) != MATRIX_ROWS:
        raise ValueError(
            f"Invalid matrix row count {len(matrix)}. Matrix must have exactly {MATRIX_ROWS} rows."
        )

    for row_idx, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError(
                f"Row {row_idx} must be a list, got {type(row).__name__}."
            )
        if len(row) != MATRIX_COLS:
            raise ValueError(
                f"Invalid column count {len(row)} at row {row_idx}. Each row must have exactly {MATRIX_COLS} columns."
            )
        for col_idx, val in enumerate(row):
            # Strict integer 0 or 1 check (excluding bool if strict int check needed, though bool is subclass of int)
            if type(val) is not int or val not in (0, 1):
                raise ValueError(
                    f"Invalid element '{val}' at position ({row_idx}, {col_idx}). Matrix elements must be integer 0 or 1."
                )


def block_to_matrix(block: str) -> List[List[int]]:
    """
    Converts a 256-bit binary string into a 16x16 binary integer matrix.
    Row-major order mapping:
      block[0:16]   -> matrix row 0
      block[16:32]  -> matrix row 1
      ...
      block[240:256] -> matrix row 15

    Args:
        block: Exactly 256 binary characters ('0' or '1').

    Returns:
        16x16 list[list[int]] binary matrix.
    """
    validate_block(block)

    matrix: List[List[int]] = []
    for r in range(MATRIX_ROWS):
        start_idx = r * MATRIX_COLS
        end_idx = start_idx + MATRIX_COLS
        row_chars = block[start_idx:end_idx]
        row_ints = [int(c) for c in row_chars]
        matrix.append(row_ints)

    return matrix


def matrix_to_block(matrix: List[List[int]]) -> str:
    """
    Reconstructs the original 256-bit binary string from a 16x16 binary matrix.
    Row-major order concatenation.

    Args:
        matrix: Exactly 16x16 list[list[int]] binary matrix with elements in {0, 1}.

    Returns:
        256-bit binary string.
    """
    validate_matrix(matrix)

    chars: List[str] = []
    for r in range(MATRIX_ROWS):
        for c in range(MATRIX_COLS):
            chars.append(str(matrix[r][c]))

    return "".join(chars)


def run_demo() -> None:
    """Runs demonstration of ca_matrix module functions and prints results."""
    print("=" * 80)
    print(" 256-BIT BLOCK <-> 16x16 BINARY MATRIX MODULE DEMONSTRATION")
    print("=" * 80)

    # Test Sample Block: Sequential 16-bit blocks alternating patterns
    sample_block = (
        "0000000000000000" +  # Row 0: all 0s
        "1111111111111111" +  # Row 1: all 1s
        "0101010101010101" +  # Row 2: alternating 01
        "1010101010101010" +  # Row 3: alternating 10
        "0000111100001111" +  # Row 4
        "1111000011110000" +  # Row 5
        "0011001100110011" +  # Row 6
        "1100110011001100" +  # Row 7
        "0110011001100110" +  # Row 8
        "1001100110011001" +  # Row 9
        "1111111100000000" +  # Row 10
        "0000000011111111" +  # Row 11
        "0101101001011010" +  # Row 12
        "1010010110100101" +  # Row 13
        "1100001111000011" +  # Row 14
        "0011110000111100"    # Row 15
    )

    print(f"\n1. Input Block Length: {len(sample_block)} bits")
    print(f"   First 32 bits:     {sample_block[:32]}...")
    print(f"   Last 32 bits:      ...{sample_block[-32:]}")

    # Convert Block to Matrix
    matrix = block_to_matrix(sample_block)
    print(f"\n2. Matrix Dimensions: {len(matrix)} rows x {len(matrix[0])} columns")

    print("\n3. Sample 16x16 Binary Matrix Display:")
    print("    " + " ".join(f"{c:2d}" for c in range(16)))
    print("   +" + "-" * 48)
    for r_idx, row in enumerate(matrix):
        row_str = " ".join(f" {val}" for val in row)
        print(f"R{r_idx:02d}|{row_str}")

    # Reconstruct Block from Matrix
    reconstructed_block = matrix_to_block(matrix)

    # Verification
    roundtrip_match = (sample_block == reconstructed_block)
    print(f"\n4. Round-Trip Verification:")
    print(f"   Reconstructed Length: {len(reconstructed_block)} bits")
    print(f"   Exact Match:          {roundtrip_match}")

    if roundtrip_match:
        print("   SUCCESS: block_to_matrix and matrix_to_block preserve bit order perfectly!")
    else:
        print("   FAILURE: Mismatch detected in round-trip conversion.")

    print("=" * 80)


if __name__ == "__main__":
    run_demo()
