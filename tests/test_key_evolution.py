"""Unit tests for KeyEvolutionEngine (crypto/key/evolution.py)."""

import pytest
from crypto.key.evolution import (
    AUTH_KEY_LABEL,
    ENC_KEY_LABEL,
    ROUND_KEY_LABEL,
    SESSION_KEY_LABEL,
    InvalidContextError,
    InvalidKeyLengthError,
    KeyEvolutionEngine,
)


class TestKeyEvolutionEngine:
    """Tests for KeyEvolutionEngine key derivation and domain separation."""

    def test_evolve_master_key_ratchet(self):
        """Verify master key one-way ratchet evolution."""
        engine = KeyEvolutionEngine()
        m1 = b"0123456789abcdef0123456789abcdef"
        m2 = engine.evolve(m1)

        assert len(m2) == 32
        assert m2 != m1

        # Second evolution step
        m3 = engine.evolve(m2)
        assert len(m3) == 32
        assert m3 != m2 and m3 != m1

    def test_domain_separation_invariance(self):
        """Verify different derivation functions produce distinct keys from same master key."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"

        k_round = engine.derive_round_key(master, round_num=1)
        k_session = engine.derive_session_key(master, session_id="sess_1")
        k_epoch = engine.derive_epoch_key(master, epoch_num=1)
        k_ca = engine.derive_ca_key(master, ca_id=30)
        k_auth = engine.derive_auth_key(master)
        k_enc = engine.derive_encryption_key(master)

        derived_keys = [k_round, k_session, k_epoch, k_ca, k_auth, k_enc]
        # All derived keys must be 32 bytes and pairwise unique
        assert all(len(k) == 32 for k in derived_keys)
        assert len(set(derived_keys)) == len(derived_keys), "Domain separation collision detected!"

    def test_deterministic_derivation(self):
        """Verify identical inputs produce identical derived keys."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"

        k1 = engine.derive_round_key(master, round_num=5)
        k2 = engine.derive_round_key(master, round_num=5)

        assert k1 == k2

    def test_context_sensitivity(self):
        """Verify changing context or parameter produces different derived keys."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"

        r1 = engine.derive_round_key(master, round_num=1)
        r2 = engine.derive_round_key(master, round_num=2)
        assert r1 != r2

        s1 = engine.derive_session_key(master, session_id="sess_1")
        s2 = engine.derive_session_key(master, session_id="sess_2")
        assert s1 != s2

    def test_invalid_master_key_raises_error(self):
        """Verify short or non-bytes master key raises InvalidContextError."""
        engine = KeyEvolutionEngine()
        with pytest.raises(InvalidContextError):
            engine.derive_round_key(b"short", round_num=1)
        with pytest.raises(InvalidContextError):
            engine.derive_round_key("not_bytes", round_num=1)

    def test_invalid_key_length_raises_error(self):
        """Verify key length out of bounds raises InvalidKeyLengthError."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"
        with pytest.raises(InvalidKeyLengthError):
            engine.derive_auth_key(master, key_length=8)  # < 16
        with pytest.raises(InvalidKeyLengthError):
            engine.derive_auth_key(master, key_length=10000)  # > 8160

    def test_export_state(self):
        """Verify export_state metadata."""
        engine = KeyEvolutionEngine(default_key_length=64)
        master = b"master_key_bytes_123456789012345"
        _ = engine.derive_auth_key(master)

        st = engine.export_state()
        assert st["default_key_length"] == 64
        assert st["derivation_count"] == 1
