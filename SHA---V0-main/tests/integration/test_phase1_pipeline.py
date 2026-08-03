"""
End-to-End Pipeline Integration Tests for Phase 1.

Verifies complete integration between KeyExpansion, DynamicRuleScheduler,
CellularAutomataEngine, and Analysis Toolkit.
"""

from crypto.analysis import (
    autocorrelation,
    avalanche_effect,
    bit_frequency,
    runs_test,
    shannon_entropy,
)
from crypto.ca import CellularAutomataEngine
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestPhase1Pipeline:
    """Integration test suite for the complete Phase 1 cryptographic pipeline."""

    def test_full_phase1_pipeline_execution(self):
        """Verify seamless execution of the end-to-end Phase 1 cryptographic workflow."""
        master_key = b"phase1_master_pipeline_key_2026"
        rounds = 10
        initial_state = [0, 1, 0, 1, 1, 0, 1, 0]

        # 1. Initialize Key Expansion
        expansion = KeyExpansion(key=master_key, rounds=rounds, key_size=64)
        assert expansion.total_rounds() == rounds
        assert len(expansion._canonical_key) == len(master_key)

        # 2. Initialize Dynamic Rule Scheduler
        scheduler = DynamicRuleScheduler(master_key, rounds=rounds)
        assert scheduler.rounds == rounds
        assert len(scheduler.schedule) == rounds

        # 3. Initialize Cellular Automata Engine
        engine = CellularAutomataEngine(boundary="wrap")

        # 4. Execute Multi-Round Evolution
        current_state = list(initial_state)
        for i in range(rounds):
            rule = scheduler.next_rule()
            round_key = expansion.get_round_key(i)

            assert 0 <= rule <= 255
            assert isinstance(round_key, bytes)
            assert len(round_key) == 64

            engine.set_rule(rule)
            current_state = engine.evolve(current_state)
            assert len(current_state) == len(initial_state)

        # 5. Evaluate Statistical Quality of Final State
        entropy = shannon_entropy(current_state)
        runs_info = runs_test(current_state)
        avalanche = avalanche_effect(initial_state, current_state)
        freq = bit_frequency(current_state)
        ac = autocorrelation(current_state, lag=1)

        assert 0.0 <= entropy <= 1.0
        assert runs_info["runs"] > 0
        assert 0.0 <= avalanche <= 1.0
        assert freq["zeros"] + freq["ones"] == len(current_state)
        assert -1.0 <= ac <= 1.0

    def test_pipeline_with_variable_state_lengths(self):
        """Verify pipeline handles various state vector lengths (16, 32, 64 bits)."""
        master_key = b"variable_length_test_key"
        rounds = 5

        expansion = KeyExpansion(key=master_key, rounds=rounds, key_size=64)
        scheduler = DynamicRuleScheduler(master_key, rounds=rounds)
        engine = CellularAutomataEngine(boundary="wrap")

        for state_length in (16, 32, 64):
            scheduler.reset()
            initial_state = [(i % 2) for i in range(state_length)]
            current_state = list(initial_state)

            for i in range(rounds):
                rule = scheduler.next_rule()
                rk = expansion.get_round_key(i)
                assert len(rk) == 64

                engine.set_rule(rule)
                current_state = engine.evolve(current_state)

            assert len(current_state) == state_length
            entropy = shannon_entropy(current_state)
            assert 0.0 <= entropy <= 1.0
