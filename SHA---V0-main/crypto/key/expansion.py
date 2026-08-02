"""
Key Expansion Module for KDR-CA-AEAD.

Derives a sequence of cryptographically strong round keys from a user-provided secret
key using master key SHA-512 digest creation and iterative chained SHA-512 hashing.
"""

import hashlib
from typing import Any, Dict, List, Union

from crypto.key.derivation import (
    derive_bytes,
    split_round_keys,
    validate_key_size,
)
from crypto.key.exceptions import (
    InvalidKeyError,
    InvalidKeySizeError,
    KeyExpansionError,
)


class KeyExpansion:
    """
    Deterministic Key Expansion Engine.

    Transforms secret master keys (string, bytes, hex) into SHA-512 master material
    and derives arbitrary length round key schedules using chained SHA-512 hashing.
    """

    def __init__(
        self,
        key: Union[str, bytes, bytearray],
        encoding: str = "utf-8",
        rounds: int = 20,
        key_size: int = 32,
    ) -> None:
        """
        Initializes the Key Expansion engine.

        Args:
            key: Secret master key material as str, bytes, or bytearray.
            encoding: Encoding format if key is string ('utf-8', 'raw', 'bytes', 'hex'). Default is 'utf-8'.
            rounds: Default number of round keys to derive. Default is 20.
            key_size: Default byte length per round key. Default is 32.

        Raises:
            TypeError: If key or encoding is invalid type.
            InvalidKeyError: If key is empty, hex string invalid, or encoding unsupported.
            InvalidKeySizeError: If key_size or rounds <= 0.
        """
        self._canonical_key = self._process_key(key, encoding)
        self._master_digest = hashlib.sha512(self._canonical_key).digest()
        self._round_keys: List[bytes] = []
        self._rounds = rounds
        self._key_size = key_size

        if rounds > 0 and key_size > 0:
            self.generate_round_keys(rounds=rounds, key_size=key_size)

    def _process_key(self, key: Union[str, bytes, bytearray], encoding: str) -> bytes:
        """Helper to process and validate key input in various formats."""
        if not isinstance(encoding, str):
            raise TypeError(f"Encoding must be a string, got {type(encoding).__name__}")

        enc = encoding.strip().lower()
        if enc not in ("utf-8", "utf8", "hex", "raw", "bytes"):
            raise InvalidKeyError(f"Unsupported key encoding: '{encoding}'")

        if key is None:
            raise InvalidKeyError("Secret key cannot be None")

        if isinstance(key, (bytes, bytearray)):
            key_bytes = bytes(key)
        elif isinstance(key, str):
            if enc == "hex":
                clean_hex = key.strip()
                if clean_hex.startswith("0x") or clean_hex.startswith("0X"):
                    clean_hex = clean_hex[2:]
                try:
                    key_bytes = bytes.fromhex(clean_hex)
                except ValueError as e:
                    raise InvalidKeyError(f"Invalid hexadecimal key string: {e}")
            else:
                try:
                    key_bytes = key.encode("utf-8")
                except UnicodeEncodeError as e:
                    raise InvalidKeyError(f"Invalid UTF-8 key string: {e}")
        else:
            raise TypeError(f"Secret key must be str, bytes, or bytearray, got {type(key).__name__}")

        if len(key_bytes) == 0:
            raise InvalidKeyError("Secret key cannot be empty")

        return key_bytes

    def master_key(self) -> bytes:
        """Returns the 64-byte SHA-512 master key digest."""
        return self._master_digest

    def key_size(self) -> int:
        """Returns the byte length of individual stored round keys (or master key length if 0)."""
        return self._key_size if self._key_size > 0 else len(self._master_digest)

    def round_key_size(self) -> int:
        """Returns the byte length of individual stored round keys."""
        return self._key_size

    def total_rounds(self) -> int:
        """Returns the total number of round keys generated."""
        return len(self._round_keys)

    def key_count(self) -> int:
        """Returns the total number of round keys generated."""
        return len(self._round_keys)

    def expand_key(self, length: int = 64) -> bytes:
        """
        Derives an expanded key byte sequence of exact length from the master key.

        Args:
            length: Number of expanded key bytes to generate (must be > 0).

        Returns:
            Derived byte stream.
        """
        return derive_bytes(self._master_digest, length)

    def generate_round_keys(self, rounds: int = 20, key_size: int = 32) -> List[bytes]:
        """
        Generates deterministic round keys using chained SHA-512 key expansion.

        Args:
            rounds: Number of round keys to derive (must be > 0).
            key_size: Byte length of each round key (must be > 0).

        Returns:
            List of derived round key bytes objects.
        """
        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError(f"Rounds must be an integer, got {type(rounds).__name__}")
        if rounds <= 0:
            raise InvalidKeySizeError(f"Rounds must be greater than 0, got {rounds}")

        key_size = validate_key_size(key_size)

        total_bytes_needed = rounds * key_size
        derived_stream = self.expand_key(total_bytes_needed)
        self._round_keys = split_round_keys(derived_stream, key_size)
        self._rounds = rounds
        self._key_size = key_size

        return list(self._round_keys)

    def get_round_key(self, index: int) -> bytes:
        """
        Retrieves a specific round key by index.

        Args:
            index: Zero-based round key index.

        Returns:
            Round key bytes object.
        """
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"Round index must be an integer, got {type(index).__name__}")
        if not (0 <= index < len(self._round_keys)):
            raise IndexError(
                f"Round index {index} out of range [0, {len(self._round_keys) - 1}]"
            )
        return self._round_keys[index]

    def all_round_keys(self) -> List[bytes]:
        """Returns a copy of all generated round keys."""
        return list(self._round_keys)

    def reset(self) -> None:
        """Clears all generated round keys while preserving the master key material."""
        self._round_keys.clear()
        self._rounds = 0

    def export(self) -> Dict[str, Any]:
        """
        Exports the key expansion schedule into a dictionary format.

        Returns:
            Dictionary containing master_key hex digest, round_keys hex list, rounds count, and key_size.
        """
        return {
            "master_key": self._master_digest.hex(),
            "round_keys": [rk.hex() for rk in self._round_keys],
            "rounds": len(self._round_keys),
            "key_size": self._key_size,
        }

    def import_keys(self, data: Dict[str, Any]) -> None:
        """
        Imports and restores a key schedule from an exported dictionary.

        Args:
            data: Exported dictionary containing 'round_keys', 'key_size', etc.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Exported data must be a dict, got {type(data).__name__}")
        if "round_keys" not in data or not isinstance(data["round_keys"], list):
            raise InvalidKeyError("Exported data must contain a 'round_keys' list")
        if len(data["round_keys"]) == 0:
            raise InvalidKeyError("Imported round_keys list cannot be empty")

        key_size = data.get("key_size", len(data["round_keys"][0]) // 2 if data["round_keys"] else 32)
        imported_keys = []
        for i, hex_str in enumerate(data["round_keys"]):
            if not isinstance(hex_str, str):
                raise TypeError(f"Round key hex at index {i} must be a string")
            clean_hex = hex_str.strip()
            try:
                rk_bytes = bytes.fromhex(clean_hex)
            except ValueError as e:
                raise InvalidKeyError(f"Invalid hexadecimal round key at index {i}: {e}")
            if len(rk_bytes) != key_size:
                raise InvalidKeySizeError(
                    f"Round key at index {i} byte length ({len(rk_bytes)}) does not match key_size ({key_size})"
                )
            imported_keys.append(rk_bytes)

        self._round_keys = imported_keys
        self._rounds = len(imported_keys)
        self._key_size = key_size

    @classmethod
    def from_export(cls, data: Dict[str, Any]) -> "KeyExpansion":
        """Creates a KeyExpansion instance from exported dictionary structure."""
        instance = cls(key=b"placeholder_master_key", rounds=0, key_size=0)
        instance.import_keys(data)
        if "master_key" in data and isinstance(data["master_key"], str):
            try:
                instance._master_digest = bytes.fromhex(data["master_key"])
            except ValueError:
                pass
        return instance
