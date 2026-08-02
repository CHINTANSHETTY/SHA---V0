"""
Key Derivation Utilities Module for KDR-CA-AEAD.

Provides helper functions for deterministic HKDF-style SHA-512 byte derivation,
block generation, key splitting, and size validations.
"""

import hashlib
from typing import List
from crypto.key.exceptions import InvalidKeySizeError, KeyDerivationError


def validate_key_size(key_size: int) -> int:
    """
    Validates that key_size is a positive integer.

    Args:
        key_size: Requested key size in bytes.

    Returns:
        Validated key size integer.

    Raises:
        TypeError: If key_size is not an integer.
        InvalidKeySizeError: If key_size <= 0.
    """
    if isinstance(key_size, bool) or not isinstance(key_size, int):
        raise TypeError(f"Key size must be an integer, got {type(key_size).__name__}")
    if key_size <= 0:
        raise InvalidKeySizeError(f"Key size must be greater than 0, got {key_size}")
    return key_size


def derive_blocks(master_key: bytes, block_count: int) -> List[bytes]:
    """
    Generates deterministic block_count SHA-512 blocks (64 bytes each) from master key.

    Block_1 = SHA512(master_key)
    Block_k = SHA512(Block_{k-1})

    Args:
        master_key: Input master key bytes.
        block_count: Number of 64-byte blocks to generate.

    Returns:
        List of 64-byte blocks.

    Raises:
        TypeError: If master_key is not bytes or block_count is not int.
        KeyDerivationError: If master_key is empty or block_count <= 0.
    """
    if not isinstance(master_key, (bytes, bytearray)):
        raise TypeError(f"Master key must be bytes or bytearray, got {type(master_key).__name__}")
    if len(master_key) == 0:
        raise KeyDerivationError("Master key cannot be empty")

    if isinstance(block_count, bool) or not isinstance(block_count, int):
        raise TypeError(f"Block count must be an integer, got {type(block_count).__name__}")
    if block_count <= 0:
        raise KeyDerivationError(f"Block count must be greater than 0, got {block_count}")

    blocks: List[bytes] = []
    previous_digest = bytes(master_key)

    for _ in range(block_count):
        digest = hashlib.sha512(previous_digest).digest()
        blocks.append(digest)
        previous_digest = digest

    return blocks


def derive_bytes(master_key: bytes, length: int) -> bytes:
    """
    Derives an exact specified number of bytes from master_key using chained SHA-512.

    Args:
        master_key: Input master key bytes.
        length: Number of bytes to derive.

    Returns:
        Derived byte stream of exact length.

    Raises:
        TypeError: If inputs are invalid type.
        InvalidKeySizeError / KeyDerivationError: If length <= 0 or key is empty.
    """
    length = validate_key_size(length)

    if not isinstance(master_key, (bytes, bytearray)):
        raise TypeError(f"Master key must be bytes or bytearray, got {type(master_key).__name__}")
    if len(master_key) == 0:
        raise KeyDerivationError("Master key cannot be empty")

    raw_bytes = bytearray()
    previous_digest = bytes(master_key)

    while len(raw_bytes) < length:
        digest = hashlib.sha512(previous_digest).digest()
        raw_bytes.extend(digest)
        previous_digest = digest

    return bytes(raw_bytes[:length])


def split_round_keys(raw_bytes: bytes, key_size: int) -> List[bytes]:
    """
    Splits a raw byte array into a list of round key chunks of exact size key_size.

    Args:
        raw_bytes: Derived raw byte array.
        key_size: Chunk size in bytes per round key.

    Returns:
        List of round key bytes objects.

    Raises:
        TypeError: If inputs are invalid type.
        InvalidKeySizeError: If key_size <= 0.
        KeyDerivationError: If raw_bytes is empty.
    """
    key_size = validate_key_size(key_size)

    if not isinstance(raw_bytes, (bytes, bytearray)):
        raise TypeError(f"Raw bytes input must be bytes or bytearray, got {type(raw_bytes).__name__}")
    if len(raw_bytes) == 0:
        raise KeyDerivationError("Raw bytes input cannot be empty")

    round_keys = []
    total_chunks = len(raw_bytes) // key_size
    for i in range(total_chunks):
        chunk = bytes(raw_bytes[i * key_size : (i + 1) * key_size])
        round_keys.append(chunk)

    return round_keys
