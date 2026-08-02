"""
Determinism & Key Sensitivity Integration Tests for Phase 1.

Verifies strict deterministic reproducibility and key sensitivity across the complete
Phase 1 cryptographic pipeline.
"""

import pytest
from crypto.analysis import avalanche_effect, hamming_distance, shannon_entropy
from crypto.ca import CellularAutomataEngine
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestDeterminism:
    """Test suite verifying pipeline determinism and sensitivity."""

    def test_pipeline_determinism_identical_inputs(self):
        """Verify identical master key and initial state produce 100% bit-identical results."""
        master_key = b"strict_determinism_key_2026"
        initial_state = [1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1]
        rounds = 16

        # Execution Run 1
        exp1 = KeyExpansion(master_key, rounds=rounds)
        sch1 = DynamicRuleScheduler(master_key, rounds=rounds)
        eng1 = CellularAutomataEngine(boundary="wrap")
        state1 = list(initial_state)
        for i in range(rounds):
            eng1.set_rule(sch1.next_rule())
            state1 = eng1.evolve(state1)
        entropy1 = shannon_entropy(state1)
        avalanche1 = avalanche_effect(initial_state, state1)

        # Execution Run 2 (separate instances, identical parameters)
        exp2 = KeyExpansion(master_key, rounds=rounds)
        sch2 = DynamicRuleScheduler(master_key, rounds=rounds)
        eng2 = CellularAutomataEngine(boundary="wrap")
        state2 = list(initial_state)
        for i in range(rounds):
            eng2.set_rule(sch2.next_rule())
            state2 = eng2.evolve(state2)
        entropy2 = shannon_entropy(state2)
        avalanche2 = avalanche_effect(initial_state, state2)

        # Assert strict bit-for-bit identity
        assert exp1.all_round_keys() == exp2.all_round_keys()
        assert sch1.schedule == sch2.schedule
        assert state1 == state2
        assert entropy1 == entropy2
        assert avalanche1 == avalanche2

    def test_key_sensitivity_distinct_outputs(self):
        """Verify different master keys yield distinct schedules, round keys, and CA states."""
        key_A = b"master_key_alpha_2026"
        key_B = b"master_key_beta_2026"
        initial_state = [1, 0, 0, 1, 1, 0, 1, 0]
        rounds = 10

        exp_A = KeyExpansion(key_A, rounds=rounds)
        sch_A = DynamicRuleScheduler(key_A, rounds=rounds)
        eng_A = CellularAutomataEngine(boundary="wrap")
        state_A = list(initial_state)
        for i in range(rounds):
            eng_A.set_rule(sch_A.next_rule())
            state_A = eng_A.evolve(state_A)

        exp_B = KeyExpansion(key_B, rounds=rounds)
        sch_B = DynamicRuleScheduler(key_B, rounds=rounds)
        eng_B = CellularAutomataEngine(boundary="wrap")
        state_B = list(initial_state)
        for i in range(rounds):
            eng_B.set_rule(sch_B.next_rule())
            state_B = eng_B.evolve(state_B)

        assert exp_A.all_round_keys() != exp_B.all_round_keys()
        assert sch_A.schedule != sch_B.schedule
        assert state_A != state_B

    def test_initial_state_avalanche_sensitivity(self):
        """Verify 1-bit flip in initial state propagates to significant output divergence."""
        master_key = b"avalanche_sensitivity_key"
        rounds = 10

        state_orig = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        state_flip = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 1 bit flipped

        sch1 = DynamicRuleScheduler(master_key, rounds=rounds)
        sch2 = DynamicRuleScheduler(master_key, rounds=rounds)
        eng1 = CellularAutomataEngine(boundary="wrap")
        eng2 = CellularAutomataEngine(boundary="wrap")

        out1 = list(state_orig)
        out2 = list(state_flip)

        for _ in range(rounds):
            r1 = sch1.next_rule()
            r2 = sch2.next_rule()
            eng1.set_rule(r1)
            eng2.set_rule(r2)
            out1 = eng1.evolve(out1)
            out2 = eng2.evolve(out2)

        # Output states should differ significantly
        dist = hamming_distance(out1, out2)
        avalanche = avalanche_effect(out1, out2)

        assert out1 != out2
        assert dist > 0
        assert 0.0 < avalanche <= 1.0
