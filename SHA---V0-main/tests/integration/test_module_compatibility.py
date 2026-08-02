"""
Module Compatibility Integration Tests for Phase 1.

Verifies public API exports, cross-module parameter passing, and error propagation
across crypto.ca, crypto.scheduler, crypto.key, and crypto.analysis packages.
"""

import pytest
# Verify top-level package exports
from crypto.analysis import (
    autocorrelation,
    avalanche_effect,
    bit_frequency,
    hamming_distance,
    probability_distribution,
    runs_test,
    shannon_entropy,
)
from crypto.ca import (
    CellularAutomataEngine,
    apply_rule,
    bits_to_string,
    get_rule_truth_table,
    hex_to_state,
    random_binary_state,
    state_to_hex,
    string_to_bits,
    validate_binary_state,
    validate_rule_number,
)
from crypto.key import KeyExpansion
from crypto.scheduler import (
    DynamicRuleScheduler,
    map_byte_to_rule,
    map_bytes_to_rules,
    optimize_schedule,
    validate_rule,
)


class TestModuleCompatibility:
    """Test suite for cross-module compatibility and public API validation."""

    def test_public_api_imports(self):
        """Verify all expected public symbols are cleanly imported from top-level packages."""
        assert callable(apply_rule)
        assert callable(CellularAutomataEngine)
        assert callable(map_byte_to_rule)
        assert callable(DynamicRuleScheduler)
        assert callable(KeyExpansion)
        assert callable(shannon_entropy)
        assert callable(runs_test)

    def test_scheduler_to_ca_engine_compatibility(self):
        """Verify output of DynamicRuleScheduler directly feeds CellularAutomataEngine.set_rule."""
        key = b"compat_key_123"
        scheduler = DynamicRuleScheduler(key, rounds=10)
        engine = CellularAutomataEngine()

        state = [0, 1, 0, 1, 1, 0, 1, 0]

        for _ in range(10):
            rule = scheduler.next_rule()
            engine.set_rule(rule)  # Must accept rule without error
            state = engine.evolve(state)

        assert len(state) == 8

    def test_key_expansion_to_scheduler_compatibility(self):
        """Verify KeyExpansion and DynamicRuleScheduler consume identical master key material."""
        key = b"shared_master_key"
        expansion = KeyExpansion(key, rounds=16)
        scheduler = DynamicRuleScheduler(key, rounds=16)

        assert expansion.total_rounds() == scheduler.rounds
        assert expansion.key_size() == len(scheduler.key)

    def test_ca_engine_to_analysis_compatibility(self):
        """Verify state output from CellularAutomataEngine feeds directly into analysis functions."""
        engine = CellularAutomataEngine(rule=30, boundary="wrap")
        initial_state = [1, 0, 1, 0, 0, 1, 1, 0]

        evolved = engine.evolve(initial_state)

        # Analysis functions must accept evolved state directly
        entropy = shannon_entropy(evolved)
        freq = bit_frequency(evolved)
        prob = probability_distribution(evolved)
        runs = runs_test(evolved)
        dist = hamming_distance(initial_state, evolved)
        avalanche = avalanche_effect(initial_state, evolved)
        ac = autocorrelation(evolved, lag=1)

        assert 0.0 <= entropy <= 1.0
        assert freq["zeros"] + freq["ones"] == 8
        assert prob[0] + prob[1] == 1.0
        assert runs["runs"] > 0
        assert 0 <= dist <= 8
        assert 0.0 <= avalanche <= 1.0
        assert -1.0 <= ac <= 1.0

    def test_error_propagation_across_modules(self):
        """Verify descriptive error types propagate correctly across module boundaries."""
        # Empty master key raises ValueError in both scheduler and expansion
        with pytest.raises(ValueError, match="cannot be empty"):
            KeyExpansion(b"")

        with pytest.raises(ValueError, match="cannot be empty"):
            DynamicRuleScheduler(b"")

        # Invalid type key raises TypeError in both
        with pytest.raises(TypeError):
            KeyExpansion("string_key")  # type: ignore

        with pytest.raises(TypeError):
            DynamicRuleScheduler("string_key")  # type: ignore
