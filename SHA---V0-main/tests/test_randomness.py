"""
Unit tests for Randomness Analysis module (crypto/analysis/randomness.py).
"""

import pytest
from crypto.analysis import (
    autocorrelation,
    avalanche_effect,
    hamming_distance,
    runs_test,
    shannon_entropy,
)
from crypto.ca import CellularAutomataEngine
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestRandomness:
    """Test suite for randomness analysis functions."""

    def test_runs_test(self):
        """Verify runs test counts contiguous bit sequences correctly."""
        # Sequence: [1, 1] (one_run_1), [0, 0] (zero_run_1), [1] (one_run_2) -> total 3 runs
        bits = [1, 1, 0, 0, 1]
        res = runs_test(bits)
        assert res["runs"] == 3
        assert res["zero_runs"] == 1
        assert res["one_runs"] == 2

    def test_runs_test_alternating(self):
        """Verify runs test on alternating bit sequence."""
        bits = [1, 0, 1, 0, 1, 0]
        res = runs_test(bits)
        assert res["runs"] == 6
        assert res["zero_runs"] == 3
        assert res["one_runs"] == 3

    def test_hamming_distance(self):
        """Verify Hamming distance between binary state vectors."""
        b1 = [1, 0, 1, 1, 0]
        b2 = [0, 0, 1, 0, 0]  # Differs at index 0 and 3 -> 2
        assert hamming_distance(b1, b2) == 2

    def test_hamming_distance_identical(self):
        """Verify Hamming distance of identical sequences is 0."""
        b = [0, 1, 1, 0]
        assert hamming_distance(b, b) == 0

    def test_hamming_distance_unequal_lengths(self):
        """Verify Hamming distance raises ValueError for unequal sequence lengths."""
        with pytest.raises(ValueError, match="Sequence lengths must be equal"):
            hamming_distance([1, 0], [1, 0, 1])

    def test_avalanche_effect(self):
        """Verify avalanche effect ratio calculation."""
        b1 = [1, 0, 1, 0]
        b2 = [0, 1, 0, 1]  # All 4 bits flipped -> ratio 1.0
        assert avalanche_effect(b1, b2) == 1.0

        b3 = [1, 0, 1, 0]  # 0 bits flipped -> ratio 0.0
        assert avalanche_effect(b1, b3) == 0.0

        b4 = [1, 1, 1, 0]  # 1 bit flipped (index 1) -> 1/4 = 0.25
        assert avalanche_effect(b1, b4) == 0.25

    def test_autocorrelation(self):
        """Verify autocorrelation calculation."""
        # Alternating sequence: [1, 0, 1, 0, 1, 0] -> at lag 1, values differ -> -1.0
        alt = [1, 0, 1, 0, 1, 0]
        assert autocorrelation(alt, lag=1) == -1.0

        # Constant sequence: [1, 1, 1, 1, 1] -> at lag 1, values match -> 1.0
        const = [1, 1, 1, 1, 1]
        assert autocorrelation(const, lag=1) == 1.0

    def test_autocorrelation_invalid_lag(self):
        """Verify invalid lag values raise ValueError or TypeError."""
        bits = [1, 0, 1, 0]
        with pytest.raises(ValueError, match="Lag must be in range"):
            autocorrelation(bits, lag=0)

        with pytest.raises(ValueError, match="Lag must be in range"):
            autocorrelation(bits, lag=4)

        with pytest.raises(TypeError, match="Lag must be an integer"):
            autocorrelation(bits, lag=1.5)  # type: ignore

    def test_integration_with_ca_scheduler_key(self):
        """Integration test: analyze CA states driven by scheduler and key expansion."""
        master_key = b"crypto_entropy_test_key"
        rounds = 10

        expansion = KeyExpansion(master_key, rounds=rounds)
        scheduler = DynamicRuleScheduler(master_key, rounds=rounds)
        engine = CellularAutomataEngine(boundary="wrap")

        state = [0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0]  # 16 bits

        prev_state = list(state)
        for i in range(rounds):
            rule = scheduler.next_rule()
            rk = expansion.get_round_key(i)
            engine.set_rule(rule)
            new_state = engine.evolve(prev_state)

            # Perform statistical metrics
            h = shannon_entropy(new_state)
            runs_info = runs_test(new_state)
            avalanche = avalanche_effect(prev_state, new_state)

            assert 0.0 <= h <= 1.0
            assert runs_info["runs"] > 0
            assert 0.0 <= avalanche <= 1.0
            assert len(rk) == 64

            prev_state = new_state
