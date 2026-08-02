"""
Cellular Automata Utility Functions Module.

Provides state validation, bit conversions, random state generation,
and binary/hex encoding helpers for CA state vectors.
"""

import random
import secrets
from typing import Any, List, Union


def validate_binary_state(state: Any) -> List[int]:
    """
    Validates and normalizes a binary state into a list of bit integers (0 or 1).

    Args:
        state: Input binary state. Can be a list/tuple of 0/1 integers,
               or a binary digit string (e.g., "0110").

    Returns:
        List of integer bits (0 or 1).

    Raises:
        TypeError: If state is not an iterable sequence or contains non-integer/non-string elements.
        ValueError: If state is empty or contains values other than 0 or 1.
    """
    if state is None:
        raise TypeError("State cannot be None")

    if isinstance(state, str):
        if not state:
            raise ValueError("State string cannot be empty")
        for char in state:
            if char not in ("0", "1"):
                raise ValueError(f"State binary string contains invalid character '{char}'")
        return [int(char) for char in state]

    if not isinstance(state, (list, tuple)):
        raise TypeError(f"State must be a list, tuple, or string, got {type(state).__name__}")

    if len(state) == 0:
        raise ValueError("State sequence cannot be empty")

    normalized = []
    for elem in state:
        if isinstance(elem, bool) or not isinstance(elem, int):
            raise TypeError(f"State elements must be integers (0 or 1), got {type(elem).__name__}")
        if elem not in (0, 1):
            raise ValueError(f"State elements must be 0 or 1, got {elem}")
        normalized.append(elem)

    return normalized


def string_to_bits(s: str) -> List[int]:
    """
    Converts a string into a list of bit integers (0 or 1).

    If the string contains only '0' and '1' characters, it is parsed directly as a bit string.
    Otherwise, each character is converted to its 8-bit UTF-8 representation.

    Args:
        s: Input string.

    Returns:
        List of bits (0 or 1).

    Raises:
        TypeError: If input is not a string.
        ValueError: If string is empty.
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string input, got {type(s).__name__}")
    if not s:
        raise ValueError("Input string cannot be empty")

    # If s consists only of '0' and '1', parse directly as a binary digit string
    if all(c in ("0", "1") for c in s):
        return [int(c) for c in s]

    # Convert UTF-8 bytes to 8-bit sequences
    bits = []
    for byte in s.encode("utf-8"):
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_string(bits: List[int], mode: str = "binary") -> str:
    """
    Converts a list of bit integers into a string.

    Args:
        bits: List of bit integers (0 or 1).
        mode: Output mode. "binary" (default) returns a string of '0' and '1'.
              "ascii" / "text" converts 8-bit groups back to characters.

    Returns:
        Converted string representation.

    Raises:
        ValueError: If mode is unsupported or bits are invalid.
    """
    validated_bits = validate_binary_state(bits)

    if mode.lower() in ("binary", "bin"):
        return "".join(str(b) for b in validated_bits)
    elif mode.lower() in ("ascii", "text", "utf-8"):
        if len(validated_bits) % 8 != 0:
            raise ValueError(f"Bit length ({len(validated_bits)}) must be a multiple of 8 for ASCII mode")
        byte_values = []
        for i in range(0, len(validated_bits), 8):
            byte_val = 0
            for b in validated_bits[i:i + 8]:
                byte_val = (byte_val << 1) | b
            byte_values.append(byte_val)
        return bytes(byte_values).decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported mode '{mode}'. Use 'binary' or 'ascii'")


def random_binary_state(length: int, seed: Union[int, None] = None) -> List[int]:
    """
    Generates a random binary state of the specified length.

    Args:
        length: Number of bits to generate (must be >= 1).
        seed: Optional integer seed for deterministic testing.
              If None, CSPRNG (`secrets`) is used.

    Returns:
        List of length random bit integers (0 or 1).

    Raises:
        TypeError: If length is not an integer.
        ValueError: If length < 1.
    """
    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError(f"Length must be an integer, got {type(length).__name__}")
    if length < 1:
        raise ValueError(f"Length must be at least 1, got {length}")

    if seed is not None:
        rng = random.Random(seed)
        return [rng.randint(0, 1) for _ in range(length)]
    else:
        return [secrets.randbelow(2) for _ in range(length)]


def state_to_hex(state: List[int]) -> str:
    """
    Converts a binary state vector to a hex string representation.

    If the bit length is not a multiple of 4, zero bits are prepended for alignment.

    Args:
        state: Binary state vector.

    Returns:
        Hexadecimal string (e.g., "1f" or "a3").
    """
    bits = validate_binary_state(state)
    remainder = len(bits) % 4
    if remainder != 0:
        pad_count = 4 - remainder
        bits = [0] * pad_count + bits

    hex_chars = []
    for i in range(0, len(bits), 4):
        val = (bits[i] << 3) | (bits[i + 1] << 2) | (bits[i + 2] << 1) | bits[i + 3]
        hex_chars.append(f"{val:x}")

    return "".join(hex_chars)


def hex_to_state(hex_str: str) -> List[int]:
    """
    Converts a hexadecimal string representation into a binary state vector.

    Args:
        hex_str: Hexadecimal string (e.g., "a3", "1F", or "0xa3").

    Returns:
        List of bit integers (0 or 1).

    Raises:
        TypeError: If input is not a string.
        ValueError: If string is empty or contains non-hexadecimal characters.
    """
    if not isinstance(hex_str, str):
        raise TypeError(f"Expected string input, got {type(hex_str).__name__}")

    clean_hex = hex_str.strip()
    if clean_hex.startswith("0x") or clean_hex.startswith("0X"):
        clean_hex = clean_hex[2:]

    if not clean_hex:
        raise ValueError("Hex string cannot be empty")

    bits = []
    for char in clean_hex:
        try:
            val = int(char, 16)
        except ValueError:
            raise ValueError(f"Invalid hexadecimal character '{char}'")
        for shift in (3, 2, 1, 0):
            bits.append((val >> shift) & 1)

    return bits
