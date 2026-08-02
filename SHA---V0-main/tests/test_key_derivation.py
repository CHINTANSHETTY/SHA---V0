"""
Unit tests for Key Derivation Module (crypto/key/derivation.py).
"""

import pytest
from crypto.key import (
    InvalidKeySizeError,
    KeyDerivationError,
    derive_blocks,
    derive_bytes,
    split_round_keys,
    validate_key_size,
)


class TestKeyDerivation:
    """Test suite for functions in crypto/key/derivation.py."""

    def test_validate_key_size_valid(self):
        """Verify key size validation accepts positive integers."""
        assert validate_key_size(16) == 16
        assert validate_key_size(32) == 32
        assert validate_key_size(64) == 64

    def test_validate_key_size_invalid(self):
        """Verify invalid key sizes raise appropriate errors."""
        with pytest.raises(InvalidKeySizeError, match="must be greater than 0"):
            validate_key_size(0)

        with pytest.raises(InvalidKeySizeError, match="must be greater than 0"):
            validate_key_size(-16)

        with pytest.raises(TypeError, match="must be an integer"):
            validate_key_size(32.5)  # type: ignore

        with pytest.raises(TypeError, match="must be an integer"):
            validate_key_size(True)  # type: ignore

    def test_derive_bytes_deterministic(self):
        """Verify derive_bytes produces identical byte streams for identical inputs."""
        master_key = b"master_secret_bytes_123"
        b1 = derive_bytes(master_key, length=128)
        b2 = derive_bytes(master_key, length=128)

        assert isinstance(b1, bytes)
        assert len(b1) == 128
        assert b1 == b2

    def test_derive_bytes_arbitrary_length(self):
        """Verify derive_bytes supports arbitrary length output."""
        master_key = b"master_secret"
        for size in (1, 15, 64, 100, 1024):
            derived = derive_bytes(master_key, length=size)
            assert len(derived) == size

    def test_derive_bytes_avalanche_effect(self):
        """Verify changing single bit in master_key produces completely different derived bytes."""
        k1 = b"master_secret_key_1"
        k2 = b"master_secret_key_2"

        d1 = derive_bytes(k1, length=64)
        d2 = derive_bytes(k2, length=64)

        assert d1 != d2

    def test_derive_blocks_count(self):
        """Verify derive_blocks generates exact requested 64-byte blocks."""
        master_key = b"master_key_blocks"
        blocks = derive_blocks(master_key, block_count=5)

        assert len(blocks) == 5
        for b in blocks:
            assert isinstance(b, bytes)
            assert len(b) == 64

    def test_derive_blocks_invalid_inputs(self):
        """Verify derive_blocks error handling."""
        with pytest.raises(TypeError, match="Master key must be bytes"):
            derive_blocks("not_bytes", block_count=2)  # type: ignore

        with pytest.raises(KeyDerivationError, match="Master key cannot be empty"):
            derive_blocks(b"", block_count=2)

        with pytest.raises(KeyDerivationError, match="Block count must be greater than 0"):
            derive_blocks(b"valid", block_count=0)

    def test_split_round_keys_valid(self):
        """Verify split_round_keys splits byte array into chunks."""
        raw = b"A" * 64  # 64 bytes
        keys = split_round_keys(raw, key_size=16)

        assert len(keys) == 4
        for k in keys:
            assert k == b"A" * 16

    def test_split_round_keys_invalid_inputs(self):
        """Verify split_round_keys error conditions."""
        with pytest.raises(TypeError, match="Raw bytes input must be bytes"):
            split_round_keys("string", key_size=16)  # type: ignore

        with pytest.raises(KeyDerivationError, match="Raw bytes input cannot be empty"):
            split_round_keys(b"", key_size=16)
