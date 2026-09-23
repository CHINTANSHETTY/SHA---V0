"""
Module: research_crypto_utils.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone cryptographic utilities for the revised research cipher:
         - SHA-512 K256 key derivation (first 256 bits of SHA-512 hash)
         - 256-bit binary XOR key mixing
         - 32-bit length-header framing and zero-padding to 256-bit boundary
         - UTF-8 binary <-> text conversion
"""

import hashlib
from typing import List

BLOCK_SIZE: int = 256
HEADER_SIZE: int = 32


def derive_k256(password: str) -> str:
    """
    Derives a 256-bit binary key string (K256) from a password using SHA-512.

    Process:
      1. Compute SHA-512 digest of UTF-8 password bytes (512 bits / 64 bytes).
      2. Extract the first 32 bytes (first 256 bits).
      3. Format each byte into an 8-bit binary string ('0' and '1').

    Args:
        password: User password string.

    Returns:
        256-character binary string representing K256.

    Raises:
        ValueError: If password is empty or not a string.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty.")

    digest = hashlib.sha512(password.encode("utf-8")).digest()
    k256_bytes = digest[:32]

    return "".join(format(b, "08b") for b in k256_bytes)


def xor_binary_strings(bin_a: str, bin_b: str) -> str:
    """
    Performs bitwise XOR between two equal-length binary strings.

    Args:
        bin_a: Binary string of '0' and '1'.
        bin_b: Binary string of '0' and '1'.

    Returns:
        XOR result binary string of identical length.
    """
    if len(bin_a) != len(bin_b):
        raise ValueError(
            f"Binary strings must be of equal length for XOR ({len(bin_a)} vs {len(bin_b)})."
        )

    return "".join("0" if a == b else "1" for a, b in zip(bin_a, bin_b))


def text_to_binary(text: str) -> str:
    """
    Converts UTF-8 string text into an 8-bit binary string representation.
    """
    if not isinstance(text, str):
        raise ValueError(f"Text must be a string, got {type(text).__name__}.")

    utf8_bytes = text.encode("utf-8")
    return "".join(format(b, "08b") for b in utf8_bytes)


def binary_to_text(binary_data: str) -> str:
    """
    Converts an 8-bit binary string representation back into a UTF-8 text string.
    """
    if len(binary_data) % 8 != 0:
        raise ValueError(f"Binary data length ({len(binary_data)}) is not a multiple of 8 bits.")

    byte_vals = bytearray()
    for i in range(0, len(binary_data), 8):
        byte_chunk = binary_data[i:i + 8]
        byte_vals.append(int(byte_chunk, 2))

    return byte_vals.decode("utf-8")


def add_length_header(binary_data: str) -> str:
    """
    Prepends a 32-bit big-endian binary length header encoding len(binary_data).
    """
    header = format(len(binary_data), "032b")
    return header + binary_data


def extract_with_length_header(binary_data: str) -> str:
    """
    Reads the 32-bit binary length header and extracts the exact original binary payload.

    Raises:
        ValueError: If binary_data is shorter than 32 bits or encoded length exceeds payload.
    """
    if len(binary_data) < HEADER_SIZE:
        raise ValueError("Binary data too short for 32-bit length header.")

    orig_len = int(binary_data[:HEADER_SIZE], 2)
    end_idx = HEADER_SIZE + orig_len

    if end_idx > len(binary_data):
        raise ValueError(
            f"Header indicates length {orig_len} bits, but available data is only {len(binary_data) - HEADER_SIZE} bits."
        )

    return binary_data[HEADER_SIZE:end_idx]


def pad_to_256(binary_data: str) -> str:
    """
    Appends '0' bits to binary data to reach the next 256-bit boundary.
    If already a multiple of 256, returns unchanged.
    """
    remainder = len(binary_data) % BLOCK_SIZE
    if remainder == 0:
        return binary_data

    pad_bits = BLOCK_SIZE - remainder
    return binary_data + ("0" * pad_bits)


def split_into_blocks(binary_data: str, block_size: int = BLOCK_SIZE) -> List[str]:
    """
    Splits binary string data into block_size blocks (default 256 bits).
    """
    if not binary_data:
        return []

    if len(binary_data) % block_size != 0:
        raise ValueError(
            f"Binary data length ({len(binary_data)}) is not a multiple of {block_size} bits."
        )

    return [binary_data[i:i + block_size] for i in range(0, len(binary_data), block_size)]
