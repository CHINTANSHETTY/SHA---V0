"""Unit tests for ForwardKeyChain (crypto/key/adaptive_schedule.py)."""

import pytest
from crypto.key.adaptive_schedule import ChainDepletedError, ForwardKeyChain
from crypto.key.evolution import InvalidContextError


class TestForwardKeyChain:
    """Tests for ForwardKeyChain ratcheting and forward secrecy."""

    def test_one_way_ratchet_progression(self):
        """Verify forward-secure key ratcheting produces distinct 32-byte keys."""
        init_key = b"initial_master_key_1234567890123"
        chain = ForwardKeyChain(initial_key=init_key, chain_length=10)

        k0 = chain.current_key()
        assert k0 == init_key

        k1 = chain.next_key()
        assert len(k1) == 32
        assert k1 != k0

        k2 = chain.next_key()
        assert len(k2) == 32
        assert k2 != k1 and k2 != k0

    def test_chain_depletion_raises_error(self):
        """Verify ratcheting past chain_length raises ChainDepletedError."""
        init_key = b"initial_master_key_1234567890123"
        chain = ForwardKeyChain(initial_key=init_key, chain_length=2)

        chain.next_key()  # step 1
        chain.next_key()  # step 2 (max reached)

        with pytest.raises(ChainDepletedError):
            chain.next_key()  # step 3 should fail

    def test_invalid_initial_key_raises_error(self):
        """Verify short initial key raises InvalidContextError."""
        with pytest.raises(InvalidContextError):
            ForwardKeyChain(initial_key=b"short", chain_length=5)

    def test_checkpoint_metadata(self):
        """Verify checkpoint returns metadata without key exposure."""
        init_key = b"initial_master_key_1234567890123"
        chain = ForwardKeyChain(initial_key=init_key, chain_length=5)
        chain.next_key()

        chk = chain.checkpoint()
        assert chk["step_count"] == 1
        assert chk["max_chain_length"] == 5
        assert chk["is_active"] is True
