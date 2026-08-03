"""Unit tests for NonceManager (crypto/primitives/nonce.py)."""

import pytest
from crypto.primitives.nonce import (
    InvalidNonceError,
    NonceManager,
    NonceReuseError,
)


class TestNonceManager:
    """Tests for NonceManager generation, validation, and reuse detection."""

    def test_random_nonce_generation(self):
        """Verify CSPRNG random nonce generation."""
        mgr = NonceManager(default_length=12)
        n1 = mgr.generate()
        n2 = mgr.generate()

        assert len(n1) == 12
        assert len(n2) == 12
        assert n1 != n2

    def test_nonce_reuse_detection(self):
        """Verify registering duplicate nonce raises NonceReuseError."""
        mgr = NonceManager()
        n = b"012345678912"  # 12 bytes

        assert mgr.register(n) is True
        with pytest.raises(NonceReuseError):
            mgr.register(n)

    def test_deterministic_nonce_generation(self):
        """Verify deterministic nonce generation from seed and counter."""
        mgr = NonceManager()
        seed = b"nonce_seed_bytes_1234567890"

        n0 = mgr.generate_deterministic(seed, counter=0)
        n1 = mgr.generate_deterministic(seed, counter=1)

        assert len(n0) == 12
        assert len(n1) == 12
        assert n0 != n1

    def test_lru_capacity_eviction(self):
        """Verify LRU cache evicts oldest nonces when max_capacity is reached."""
        mgr = NonceManager(max_capacity=100)
        # Register 100 nonces
        first_nonce = None
        for i in range(100):
            n = f"nonce_{i:07d}".encode()  # 13 bytes
            if i == 0:
                first_nonce = n
            mgr.register(n)

        assert len(mgr._lru_cache) == 100

        # Adding 101st nonce evicts the first_nonce
        new_nonce = b"nonce_1000000"
        mgr.register(new_nonce)
        assert len(mgr._lru_cache) == 100

        # first_nonce can now be re-registered without error because it was evicted
        assert mgr.register(first_nonce) is True

    def test_invalid_nonce_length_raises_error(self):
        """Verify invalid nonce length raises InvalidNonceError."""
        mgr = NonceManager()
        with pytest.raises(InvalidNonceError):
            mgr.validate(b"short")  # 5 bytes < 8
