"""
Unit tests for Dynamic Rule Scheduler (crypto/scheduler/scheduler.py).
"""

import pytest
from crypto.ca import CellularAutomataEngine
from crypto.scheduler import DynamicRuleScheduler, optimize_schedule


class TestDynamicRuleScheduler:
    """Test suite for DynamicRuleScheduler and optimize_schedule."""

    def test_same_key_produces_identical_schedules(self):
        """Verify identical secret keys produce identical rule schedules."""
        key = b"supersecretkey123"
        s1 = DynamicRuleScheduler(key, rounds=64)
        s2 = DynamicRuleScheduler(key, rounds=64)
        assert s1.schedule == s2.schedule

    def test_different_keys_produce_different_schedules(self):
        """Verify different secret keys produce distinct rule schedules."""
        k1 = b"secretkey_A"
        k2 = b"secretkey_B"
        s1 = DynamicRuleScheduler(k1, rounds=64)
        s2 = DynamicRuleScheduler(k2, rounds=64)
        assert s1.schedule != s2.schedule

    def test_default_schedule_length(self):
        """Verify default rounds generates exactly 64 rules."""
        scheduler = DynamicRuleScheduler(b"testkey")
        assert len(scheduler.schedule) == 64
        assert scheduler.rounds == 64

    def test_extended_schedule_generation(self):
        """Verify generating extended schedules (> 64 rounds via iterative hashing)."""
        scheduler100 = DynamicRuleScheduler(b"testkey", rounds=100)
        assert len(scheduler100.schedule) == 100

        scheduler200 = DynamicRuleScheduler(b"testkey", rounds=200)
        assert len(scheduler200.schedule) == 200

        # First 64 rules of 100-round schedule match base 64-round schedule (before optimization)
        # Verify deterministic extension
        s64 = DynamicRuleScheduler(b"testkey", rounds=64)
        assert s64.schedule[:60] == scheduler100.schedule[:60]

    def test_next_rule_advancement_and_history(self):
        """Verify next_rule advances index and tracks history correctly."""
        scheduler = DynamicRuleScheduler(b"testkey", rounds=5)
        expected_schedule = scheduler.schedule

        assert scheduler.current_index() == 0
        assert scheduler.get_history() == []

        served_rules = []
        for i in range(5):
            rule = scheduler.next_rule()
            served_rules.append(rule)
            assert scheduler.current_index() == i + 1
            assert scheduler.get_history() == served_rules

        assert served_rules == expected_schedule

    def test_next_rule_exhaustion_raises_index_error(self):
        """Verify calling next_rule when schedule is exhausted raises IndexError."""
        scheduler = DynamicRuleScheduler(b"testkey", rounds=3)
        for _ in range(3):
            scheduler.next_rule()

        with pytest.raises(IndexError, match="Schedule exhausted"):
            scheduler.next_rule()

    def test_reset(self):
        """Verify reset clears history and resets current_index to 0."""
        scheduler = DynamicRuleScheduler(b"testkey", rounds=5)
        for _ in range(3):
            scheduler.next_rule()

        assert scheduler.current_index() == 3
        assert len(scheduler.get_history()) == 3

        scheduler.reset()
        assert scheduler.current_index() == 0
        assert scheduler.get_history() == []

        # After reset, next_rule should yield the first rule again
        assert scheduler.next_rule() == scheduler.schedule[0]

    def test_optimize_schedule_consecutive_rules(self):
        """Verify optimize_schedule eliminates >= 4 identical consecutive rules."""
        input_schedule = [30, 30, 30, 30, 30, 90]
        optimized = optimize_schedule(input_schedule)

        # Check no 4 identical consecutive elements exist
        for i in range(3, len(optimized)):
            slice_4 = optimized[i - 3 : i + 1]
            assert not (slice_4[0] == slice_4[1] == slice_4[2] == slice_4[3])

    def test_optimize_schedule_short_list(self):
        """Verify optimize_schedule handles lists shorter than 4 elements."""
        short = [30, 30, 30]
        assert optimize_schedule(short) == [30, 30, 30]

    def test_invalid_key_handling(self):
        """Verify invalid key inputs raise appropriate exceptions."""
        with pytest.raises(TypeError, match="Secret key must be bytes"):
            DynamicRuleScheduler("string_key")  # type: ignore

        with pytest.raises(ValueError, match="Secret key cannot be empty"):
            DynamicRuleScheduler(b"")

    def test_invalid_rounds_handling(self):
        """Verify invalid rounds inputs raise appropriate exceptions."""
        with pytest.raises(ValueError, match="Rounds must be greater than 0"):
            DynamicRuleScheduler(b"validkey", rounds=0)

        with pytest.raises(ValueError, match="Rounds must be greater than 0"):
            DynamicRuleScheduler(b"validkey", rounds=-10)

        with pytest.raises(TypeError, match="Rounds must be an integer"):
            DynamicRuleScheduler(b"validkey", rounds=64.5)  # type: ignore

        with pytest.raises(TypeError, match="Rounds must be an integer"):
            DynamicRuleScheduler(b"validkey", rounds=True)  # type: ignore

    def test_integration_with_ca_engine(self):
        """Verify seamless integration with Phase 1.1 CellularAutomataEngine."""
        key = b"integration_secret_key"
        scheduler = DynamicRuleScheduler(key, rounds=3)
        engine = CellularAutomataEngine(boundary="wrap")

        initial_state = [0, 1, 0, 1, 1, 0, 0, 1]
        current_state = list(initial_state)

        for _ in range(3):
            rule = scheduler.next_rule()
            engine.set_rule(rule)
            current_state = engine.evolve(current_state)

        assert len(current_state) == len(initial_state)
        assert current_state != initial_state
