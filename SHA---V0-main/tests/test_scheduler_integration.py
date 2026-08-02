"""
Integration tests for Dynamic Rule Scheduler with Cellular Automata Engine (Phase 1.1 + Phase 1.2).
"""

import pytest
from crypto.ca import CellularAutomataEngine, random_binary_state, state_to_hex
from crypto.scheduler import DynamicRuleScheduler


class TestSchedulerIntegration:
    """Integration test suite connecting DynamicRuleScheduler with CellularAutomataEngine."""

    def test_scheduler_drives_ca_engine_rounds(self):
        """Verify scheduler rule sequence drives CA state evolution round-by-round."""
        scheduler = DynamicRuleScheduler("research-key-2026", rounds=10)
        engine = CellularAutomataEngine(boundary="wrap")

        initial_state = random_binary_state(128, seed=42)
        state = list(initial_state)

        scheduled_rules = scheduler.generate_schedule(10)
        assert len(scheduled_rules) == 10

        for rule in scheduled_rules:
            engine.set_rule(rule)
            state = engine.evolve(state)

        assert len(state) == len(initial_state)
        assert state != initial_state

    def test_different_keys_produce_different_evolved_states(self):
        """Verify different keys produce distinct evolved CA states from same initial state."""
        s1 = DynamicRuleScheduler("key_alpha", rounds=20)
        s2 = DynamicRuleScheduler("key_beta", rounds=20)

        e1 = CellularAutomataEngine(boundary="wrap")
        e2 = CellularAutomataEngine(boundary="wrap")

        initial = random_binary_state(256, seed=123)
        state1 = list(initial)
        state2 = list(initial)

        for rule in s1.remaining():
            e1.set_rule(rule)
            state1 = e1.evolve(state1)

        for rule in s2.remaining():
            e2.set_rule(rule)
            state2 = e2.evolve(state2)

        assert state1 != state2

    def test_integration_with_fixed_zero_boundary(self):
        """Verify scheduler integration under fixed_zero boundary condition."""
        scheduler = DynamicRuleScheduler("fixed_zero_key", rounds=15)
        engine = CellularAutomataEngine(boundary="fixed_zero")

        initial = random_binary_state(64, seed=999)
        state = list(initial)

        while len(scheduler.remaining()) > 0:
            rule = scheduler.next_rule()
            engine.set_rule(rule)
            state = engine.evolve(state)

        assert len(state) == 64
        hex_output = state_to_hex(state)
        assert isinstance(hex_output, str)
        assert len(hex_output) == 16
