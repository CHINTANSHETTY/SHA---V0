"""Unit tests for Optimized CA Engine (crypto/ca/optimizer.py)."""

import pytest
from crypto.ca.engine import evolve as standard_evolve
from crypto.ca.optimizer import OptimizedCAEngine, pack_bits, unpack_bits


class TestBitPacking:
    """Tests for bit packing and unpacking functions."""

    def test_pack_and_unpack_roundtrip(self):
        """Verify state array converts to bytearray and back without loss."""
        state = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1]  # 10 bits
        packed = pack_bits(state)
        assert len(packed) == 2  # 10 bits -> 2 bytes

        unpacked = unpack_bits(packed, length=10)
        assert unpacked == state

    def test_invalid_bit_in_packing(self):
        """Verify packing non-binary array raises ValueError."""
        with pytest.raises(ValueError):
            pack_bits([1, 0, 2])

    def test_insufficient_packed_bytes(self):
        """Verify unpacking with insufficient length raises ValueError."""
        packed = bytearray([0b11110000])
        with pytest.raises(ValueError):
            unpack_bits(packed, length=16)  # needs 2 bytes, got 1


class TestOptimizedCAEngine:
    """Tests for OptimizedCAEngine."""

    def test_equivalence_with_standard_evolve(self):
        """Verify OptimizedCAEngine results match standard Phase 1 evolve across multiple rules."""
        engine = OptimizedCAEngine()
        init_state = [0, 0, 0, 1, 0, 0, 0, 1, 1, 0]

        for rule in [30, 90, 110, 150, 255]:
            for gens in [1, 5, 10]:
                for boundary in ["periodic", "null"]:
                    std_res = standard_evolve(init_state, rule=rule, generations=gens, boundary=boundary)
                    opt_res = engine.evolve_fast(init_state, rule=rule, generations=gens, boundary=boundary)
                    assert opt_res == std_res, f"Mismatch for rule {rule}, gens {gens}, boundary {boundary}"

    def test_large_state_evolution(self):
        """Verify performance and correctness on large state vectors (10,000+ bits)."""
        engine = OptimizedCAEngine()
        large_state = [i % 2 for i in range(10000)]

        evolved = engine.evolve_fast(large_state, rule=30, generations=5, boundary="periodic")
        assert len(evolved) == 10000
        assert set(evolved).issubset({0, 1})
