"""
Unit tests for Key Expansion module (crypto/key/expansion.py).
"""

import pytest
from crypto.ca import CellularAutomataEngine
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestKeyExpansion:
    """Test suite for KeyExpansion class."""

    def test_valid_initialization(self):
        """Verify initialization with valid master key and default rounds."""
        master_key = b"supersecretmasterkey"
        expansion = KeyExpansion(master_key)

        assert expansion.master_key == master_key
        assert expansion.key_size() == len(master_key)
        assert expansion.round_key_size() == 64
        assert expansion.total_rounds() == 64
        assert len(expansion.all_round_keys()) == 64

    def test_custom_rounds_initialization(self):
        """Verify initialization with custom round count."""
        expansion = KeyExpansion(b"masterkey", rounds=128)
        assert expansion.total_rounds() == 128
        assert len(expansion.all_round_keys()) == 128

    def test_invalid_master_key_types(self):
        """Verify non-bytes master key inputs raise TypeError."""
        with pytest.raises(TypeError, match="Master key must be bytes or bytearray"):
            KeyExpansion("string_key")  # type: ignore

        with pytest.raises(TypeError, match="Master key must be bytes or bytearray"):
            KeyExpansion(12345)  # type: ignore

        with pytest.raises(TypeError, match="Master key must be bytes or bytearray"):
            KeyExpansion(None)  # type: ignore

    def test_empty_master_key(self):
        """Verify empty master key raises ValueError."""
        with pytest.raises(ValueError, match="Master key cannot be empty"):
            KeyExpansion(b"")

    def test_invalid_rounds_values(self):
        """Verify invalid round numbers raise ValueError or TypeError."""
        with pytest.raises(ValueError, match="Rounds must be greater than 0"):
            KeyExpansion(b"key", rounds=0)

        with pytest.raises(ValueError, match="Rounds must be greater than 0"):
            KeyExpansion(b"key", rounds=-10)

        with pytest.raises(TypeError, match="Rounds must be an integer"):
            KeyExpansion(b"key", rounds=64.5)  # type: ignore

        with pytest.raises(TypeError, match="Rounds must be an integer"):
            KeyExpansion(b"key", rounds=True)  # type: ignore

    def test_deterministic_expansion(self):
        """Verify identical master keys produce identical round key sequences."""
        key = b"consistent_key_material_123"
        e1 = KeyExpansion(key, rounds=32)
        e2 = KeyExpansion(key, rounds=32)
        assert e1.all_round_keys() == e2.all_round_keys()

    def test_different_keys_produce_different_round_keys(self):
        """Verify distinct master keys produce distinct round keys."""
        k1 = b"master_key_alpha"
        k2 = b"master_key_beta"
        e1 = KeyExpansion(k1, rounds=32)
        e2 = KeyExpansion(k2, rounds=32)
        assert e1.all_round_keys() != e2.all_round_keys()

    def test_round_key_size_always_64_bytes(self):
        """Verify every derived round key is exactly 64 bytes (512 bits)."""
        expansion = KeyExpansion(b"short_key", rounds=50)
        for rk in expansion.all_round_keys():
            assert isinstance(rk, bytes)
            assert len(rk) == 64

    def test_get_round_key(self):
        """Verify retrieving specific round keys by index."""
        expansion = KeyExpansion(b"masterkey", rounds=10)
        rk0 = expansion.get_round_key(0)
        rk9 = expansion.get_round_key(9)

        assert isinstance(rk0, bytes)
        assert len(rk0) == 64
        assert rk0 != rk9

    def test_get_round_key_out_of_bounds(self):
        """Verify out-of-bounds round key index raises IndexError."""
        expansion = KeyExpansion(b"masterkey", rounds=10)

        with pytest.raises(IndexError, match="out of range"):
            expansion.get_round_key(-1)

        with pytest.raises(IndexError, match="out of range"):
            expansion.get_round_key(10)

    def test_get_round_key_invalid_type(self):
        """Verify non-integer round key index raises TypeError."""
        expansion = KeyExpansion(b"masterkey", rounds=10)

        with pytest.raises(TypeError, match="Round index must be an integer"):
            expansion.get_round_key("0")  # type: ignore

        with pytest.raises(TypeError, match="Round index must be an integer"):
            expansion.get_round_key(1.5)  # type: ignore

    def test_export_and_import_hex_roundtrip(self):
        """Verify exporting round keys to hex and re-importing them."""
        expansion = KeyExpansion(b"export_import_key", rounds=16)
        hex_list = expansion.export_hex()

        assert len(hex_list) == 16
        assert all(isinstance(h, str) and len(h) == 128 for h in hex_list)

        imported_bytes = KeyExpansion.import_hex(hex_list)
        assert imported_bytes == expansion.all_round_keys()

    def test_import_hex_invalid_inputs(self):
        """Verify import_hex raises appropriate exceptions for invalid inputs."""
        with pytest.raises(TypeError, match="Hex keys must be a list or tuple"):
            KeyExpansion.import_hex("not_a_list")  # type: ignore

        with pytest.raises(ValueError, match="Hex keys list cannot be empty"):
            KeyExpansion.import_hex([])

        with pytest.raises(TypeError, match="must be a string"):
            KeyExpansion.import_hex([12345])  # type: ignore

        with pytest.raises(ValueError, match="must be 128 hex characters"):
            KeyExpansion.import_hex(["short_hex_string"])

        with pytest.raises(ValueError, match="Invalid hexadecimal key string"):
            # 128 characters but invalid hex char 'z'
            bad_hex = "z" * 128
            KeyExpansion.import_hex([bad_hex])

    def test_integration_with_scheduler_and_ca_engine(self):
        """Verify compatibility with DynamicRuleScheduler and CellularAutomataEngine."""
        master_key = b"integrated_master_passphrase"
        rounds = 8

        expansion = KeyExpansion(master_key, rounds=rounds)
        scheduler = DynamicRuleScheduler(master_key, rounds=rounds)
        engine = CellularAutomataEngine(boundary="wrap")

        state = [1, 0, 1, 0, 1, 1, 0, 0]

        for i in range(rounds):
            rk = expansion.get_round_key(i)
            rule = scheduler.next_rule()

            assert len(rk) == 64
            assert 0 <= rule <= 255

            engine.set_rule(rule)
            state = engine.evolve(state)

        assert len(state) == 8
