"""
Unit tests for Key Expansion module (crypto/key/expansion.py).
"""

import pytest
from crypto.key import (
    InvalidKeyError,
    InvalidKeySizeError,
    KeyExpansion,
)


class TestKeyExpansion:
    """Test suite for KeyExpansion class."""

    def test_key_validation_formats(self):
        """Verify initialization with UTF-8 string, bytes, bytearray, and hex string."""
        e_str = KeyExpansion("secret_master_key")
        e_bytes = KeyExpansion(b"secret_master_key")
        e_bytearray = KeyExpansion(bytearray(b"secret_master_key"))
        assert e_str.master_key() == e_bytes.master_key() == e_bytearray.master_key()

        hex_key = "7365637265745f6d61737465725f6b6579"
        e_hex = KeyExpansion(hex_key, encoding="hex")
        assert e_hex.master_key() == e_str.master_key()

    def test_invalid_key_handling(self):
        """Verify invalid key inputs raise InvalidKeyError."""
        with pytest.raises(InvalidKeyError, match="Secret key cannot be empty"):
            KeyExpansion("")

        with pytest.raises(InvalidKeyError, match="Secret key cannot be empty"):
            KeyExpansion(b"")

        with pytest.raises(InvalidKeyError, match="Invalid hexadecimal key string"):
            KeyExpansion("not_a_valid_hex_str_zz", encoding="hex")

        with pytest.raises(InvalidKeyError, match="Unsupported key encoding"):
            KeyExpansion("valid_key", encoding="invalid_encoding")

        with pytest.raises(TypeError, match="Secret key must be str, bytes, or bytearray"):
            KeyExpansion(12345)  # type: ignore

    def test_master_key_digest_is_64_bytes(self):
        """Verify master_key() returns 64-byte SHA-512 digest."""
        expansion = KeyExpansion("test_master_key")
        mk = expansion.master_key()
        assert isinstance(mk, bytes)
        assert len(mk) == 64

    def test_expand_key_arbitrary_length(self):
        """Verify expand_key returns requested exact byte length."""
        expansion = KeyExpansion("research-key")
        assert len(expansion.expand_key(64)) == 64
        assert len(expansion.expand_key(1024)) == 1024
        assert len(expansion.expand_key(2048)) == 2048

    def test_generate_round_keys(self):
        """Verify generate_round_keys returns correct count and size of round keys."""
        expansion = KeyExpansion("research-key")
        round_keys = expansion.generate_round_keys(rounds=20, key_size=32)

        assert len(round_keys) == 20
        assert expansion.key_count() == 20
        assert expansion.round_key_size() == 32

        for rk in round_keys:
            assert isinstance(rk, bytes)
            assert len(rk) == 32

    def test_get_round_key_and_all_round_keys(self):
        """Verify get_round_key retrieval and all_round_keys list."""
        expansion = KeyExpansion("round_key_test", rounds=10, key_size=16)
        all_keys = expansion.all_round_keys()
        assert len(all_keys) == 10

        assert expansion.get_round_key(0) == all_keys[0]
        assert expansion.get_round_key(9) == all_keys[9]

    def test_get_round_key_out_of_bounds(self):
        """Verify out-of-bounds round key index raises IndexError."""
        expansion = KeyExpansion("masterkey", rounds=5, key_size=32)
        with pytest.raises(IndexError, match="out of range"):
            expansion.get_round_key(-1)

        with pytest.raises(IndexError, match="out of range"):
            expansion.get_round_key(5)

    def test_reset(self):
        """Verify reset clears round keys while preserving master key."""
        expansion = KeyExpansion("reset_test_key", rounds=10, key_size=32)
        mk_before = expansion.master_key()
        assert expansion.key_count() == 10

        expansion.reset()
        assert expansion.key_count() == 0
        assert expansion.all_round_keys() == []
        assert expansion.master_key() == mk_before

    def test_export_and_import_keys(self):
        """Verify export returns valid dictionary and import_keys restores state."""
        expansion = KeyExpansion("export_test_key", rounds=8, key_size=32)
        exported = expansion.export()

        assert "master_key" in exported
        assert "round_keys" in exported
        assert exported["rounds"] == 8
        assert exported["key_size"] == 32
        assert len(exported["round_keys"]) == 8

        new_expansion = KeyExpansion.from_export(exported)
        assert new_expansion.all_round_keys() == expansion.all_round_keys()
        assert new_expansion.key_count() == 8
        assert new_expansion.round_key_size() == 32

    def test_import_keys_invalid_inputs(self):
        """Verify import_keys error handling for invalid input data."""
        expansion = KeyExpansion("import_test_key")

        with pytest.raises(TypeError, match="Exported data must be a dict"):
            expansion.import_keys("not_a_dict")  # type: ignore

        with pytest.raises(InvalidKeyError, match="Exported data must contain a 'round_keys' list"):
            expansion.import_keys({"no_round_keys": True})

        with pytest.raises(InvalidKeyError, match="Imported round_keys list cannot be empty"):
            expansion.import_keys({"round_keys": []})

        with pytest.raises(InvalidKeySizeError, match="does not match key_size"):
            # 16 bytes hex vs key_size 32
            expansion.import_keys({"round_keys": ["a" * 32], "key_size": 32})
