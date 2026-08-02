"""
Integration tests verifying interoperability between Key Expansion (Phase 1.3),
Dynamic Rule Scheduler (Phase 1.2), and Cellular Automata Engine (Phase 1.1).
"""

import pytest
from crypto.ca import CellularAutomataEngine, random_binary_state, state_to_hex
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestKeyIntegration:
    """Integration test suite verifying KeyExpansion with DynamicRuleScheduler & CA Engine."""

    def test_full_phase1_pipeline_integration(self):
        """
        Verify the exact sample pipeline from prompt Part 8:
        KeyExpansion -> DynamicRuleScheduler -> CellularAutomataEngine.
        """
        expansion = KeyExpansion("research-key")

        round_keys = expansion.generate_round_keys(rounds=100, key_size=32)
        assert len(round_keys) == 100
        assert len(round_keys[0]) == 32

        scheduler = DynamicRuleScheduler(round_keys[0])
        engine = CellularAutomataEngine()
        initial_state = random_binary_state(256, seed=42)
        state = list(initial_state)

        scheduled_rules = scheduler.generate_schedule(100)
        assert len(scheduled_rules) == 100

        for rule in scheduled_rules:
            engine.set_rule(rule)
            state = engine.evolve(state)

        assert len(state) == len(initial_state)
        assert state != initial_state

    def test_different_round_keys_drive_different_schedulers(self):
        """Verify round keys derived from same master key yield distinct rule schedules."""
        expansion = KeyExpansion("master_research_key", rounds=5, key_size=32)
        r_keys = expansion.all_round_keys()

        s1 = DynamicRuleScheduler(r_keys[0], rounds=10)
        s2 = DynamicRuleScheduler(r_keys[1], rounds=10)

        assert s1.schedule != s2.schedule

    def test_end_to_end_state_hex_reproducibility(self):
        """Verify deterministic reproducibility of evolved state hex across independent runs."""
        exp1 = KeyExpansion("reproducibility_key")
        rk1 = exp1.generate_round_keys(rounds=10, key_size=32)[0]
        sched1 = DynamicRuleScheduler(rk1, rounds=10)
        eng1 = CellularAutomataEngine(boundary="wrap")
        state1 = random_binary_state(128, seed=100)

        for rule in sched1.schedule:
            eng1.set_rule(rule)
            state1 = eng1.evolve(state1)
        hex1 = state_to_hex(state1)

        exp2 = KeyExpansion("reproducibility_key")
        rk2 = exp2.generate_round_keys(rounds=10, key_size=32)[0]
        sched2 = DynamicRuleScheduler(rk2, rounds=10)
        eng2 = CellularAutomataEngine(boundary="wrap")
        state2 = random_binary_state(128, seed=100)

        for rule in sched2.schedule:
            eng2.set_rule(rule)
            state2 = eng2.evolve(state2)
        hex2 = state_to_hex(state2)

        assert hex1 == hex2
