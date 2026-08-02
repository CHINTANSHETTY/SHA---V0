"""
Key Expansion Module for KDR-CA-AEAD.

Derives a sequence of cryptographically strong 512-bit (64-byte) round keys
from a user-provided master key using iterative SHA-512 digest chaining.
"""

import hashlib
from typing import List, Union


class KeyExpansion:
    """
    Deterministic Key Expansion Engine.

    Expands variable-length master key material into 64-byte (512-bit) round keys
    via iterative SHA-512 hashing:
    Digest_1 = SHA512(master_key)
    Digest_k = SHA512(Digest_{k-1})
    """

    ROUND_KEY_BYTES = 64  # 512 bits per round key

    def __init__(self, master_key: Union[bytes, bytearray], rounds: int = 64) -> None:
        """
        Initializes the Key Expansion engine.

        Args:
            master_key: Secret master key material as bytes or bytearray.
            rounds: Number of 64-byte round keys to derive (must be > 0). Default is 64.

        Raises:
            TypeError: If master_key is not bytes/bytearray or rounds is not an integer.
            ValueError: If master_key is empty or rounds <= 0.
        """
        if not isinstance(master_key, (bytes, bytearray)):
            raise TypeError(f"Master key must be bytes or bytearray, got {type(master_key).__name__}")
        if len(master_key) == 0:
            raise ValueError("Master key cannot be empty")

        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError(f"Rounds must be an integer, got {type(rounds).__name__}")
        if rounds <= 0:
            raise ValueError(f"Rounds must be greater than 0, got {rounds}")

        self._master_key = bytes(master_key)
        self._rounds = rounds
        self._round_keys: List[bytes] = []

        self.generate_round_keys()

    @property
    def master_key(self) -> bytes:
        """Returns the master key material."""
        return self._master_key

    def key_size(self) -> int:
        """Returns the byte length of the input master key."""
        return len(self._master_key)

    def round_key_size(self) -> int:
        """Returns the byte length of individual round keys (64 bytes)."""
        return self.ROUND_KEY_BYTES

    def total_rounds(self) -> int:
        """Returns the total number of round keys generated."""
        return len(self._round_keys)

    def generate_round_keys(self) -> List[bytes]:
        """
        Generates the deterministic round key schedule using iterative SHA-512 hashing.

        Returns:
            List of 64-byte round keys.
        """
        self._round_keys.clear()
        previous_digest = self._master_key

        for _ in range(self._rounds):
            digest = hashlib.sha512(previous_digest).digest()
            self._round_keys.append(digest)
            previous_digest = digest

        return list(self._round_keys)

    def get_round_key(self, index: int) -> bytes:
        """
        Retrieves a specific round key by index.

        Args:
            index: Zero-based round key index (0 <= index < rounds).

        Returns:
            64-byte round key bytes.

        Raises:
            TypeError: If index is not an integer.
            IndexError: If index is out of bounds.
        """
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"Round index must be an integer, got {type(index).__name__}")
        if not (0 <= index < len(self._round_keys)):
            raise IndexError(
                f"Round index {index} out of range [0, {len(self._round_keys) - 1}]"
            )
        return self._round_keys[index]

    def all_round_keys(self) -> List[bytes]:
        """
        Returns a copy of all generated round keys.

        Returns:
            List of 64-byte round keys.
        """
        return list(self._round_keys)

    def export_hex(self) -> List[str]:
        """
        Exports all round keys as hexadecimal strings.

        Returns:
            List of 128-character hex strings representing 64-byte round keys.
        """
        return [rk.hex() for rk in self._round_keys]

    @staticmethod
    def import_hex(hex_keys: List[str]) -> List[bytes]:
        """
        Imports hexadecimal string representations back into binary round keys.

        Args:
            hex_keys: List of hexadecimal strings (each 128 hex chars = 64 bytes).

        Returns:
            List of 64-byte round key bytes objects.

        Raises:
            TypeError: If hex_keys is not a list/tuple of strings.
            ValueError: If hex_keys is empty or contains malformed hex strings.
        """
        if not isinstance(hex_keys, (list, tuple)):
            raise TypeError(f"Hex keys must be a list or tuple of strings, got {type(hex_keys).__name__}")
        if len(hex_keys) == 0:
            raise ValueError("Hex keys list cannot be empty")

        imported_keys = []
        for i, hex_str in enumerate(hex_keys):
            if not isinstance(hex_str, str):
                raise TypeError(f"Hex key at index {i} must be a string, got {type(hex_str).__name__}")
            clean_hex = hex_str.strip()
            if len(clean_hex) != KeyExpansion.ROUND_KEY_BYTES * 2:
                raise ValueError(
                    f"Hex key at index {i} must be {KeyExpansion.ROUND_KEY_BYTES * 2} hex characters, got {len(clean_hex)}"
                )
            try:
                key_bytes = bytes.fromhex(clean_hex)
            except ValueError as e:
                raise ValueError(f"Invalid hexadecimal key string at index {i}: {e}")
            imported_keys.append(key_bytes)

        return imported_keys
