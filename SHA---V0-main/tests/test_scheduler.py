"""
Unit tests for Dynamic Rule Scheduler (crypto/scheduler/scheduler.py).
"""

import pytest
from crypto.scheduler import (
    DynamicRuleScheduler,
    InvalidKeyError,
    ScheduleExhaustedError,
    optimize_schedule,
)


class TestDynamicRuleScheduler:
    """Test suite for DynamicRuleScheduler and optimize_schedule."""

    def test_key_formats_utf8_string_bytes_hex(self):
        """Verify scheduler accepts key in utf-8 string, bytes, and hex string format."""
        s_str = DynamicRuleScheduler("secret_key", encoding="utf-8")
        s_bytes = DynamicRuleScheduler(b"secret_key", encoding="raw")
        assert s_str.schedule == s_bytes.schedule

        hex_key = "7365637265745f6b6579"  # hex of "secret_key"
        s_hex = DynamicRuleScheduler(hex_key, encoding="hex")
        assert s_hex.schedule == s_str.schedule

    def test_same_key_produces_identical_schedules(self):
        """Verify identical secret keys produce identical rule schedules (determinism)."""
        key = b"supersecretkey123"
        s1 = DynamicRuleScheduler(key, rounds=64)
        s2 = DynamicRuleScheduler(key, rounds=64)
        assert s1.schedule == s2.schedule

    def test_different_keys_produce_different_schedules(self):
        """Verify different secret keys produce distinct rule schedules (avalanche)."""
        k1 = b"secretkey_A"
        k2 = b"secretkey_B"
        s1 = DynamicRuleScheduler(k1, rounds=64)
        s2 = DynamicRuleScheduler(k2, rounds=64)
        assert s1.schedule != s2.schedule

    def test_default_schedule_length(self):
        """Verify default rounds generates exactly 64 rules."""
        scheduler = DynamicRuleScheduler("testkey")
        assert len(scheduler.schedule) == 64
        assert scheduler.rounds == 64

    def test_expansion_beyond_64_rounds(self):
        """Verify generating extended schedules (> 64 rounds via chained hashing)."""
        scheduler100 = DynamicRuleScheduler("testkey", rounds=100)
        assert len(scheduler100.schedule) == 100

        scheduler200 = DynamicRuleScheduler("testkey", rounds=200)
        assert len(scheduler200.schedule) == 200

        s64 = DynamicRuleScheduler("testkey", rounds=64)
        assert s64.schedule[:60] == scheduler100.schedule[:60]

    def test_next_rule_advancement_and_history(self):
        """Verify next_rule advances index and tracks history correctly."""
        scheduler = DynamicRuleScheduler("testkey", rounds=5)
        expected_schedule = scheduler.schedule

        assert scheduler.current_index() == 0
        assert scheduler.history() == []

        served_rules = []
        for i in range(5):
            rule = scheduler.next_rule()
            served_rules.append(rule)
            assert scheduler.current_index() == i + 1
            assert scheduler.history() == served_rules

        assert served_rules == expected_schedule

    def test_peek_does_not_consume_rule(self):
        """Verify peek returns next rule without consuming it."""
        scheduler = DynamicRuleScheduler("testkey", rounds=5)
        first_rule = scheduler.peek()
        assert first_rule == scheduler.schedule[0]
        assert scheduler.current_index() == 0
        assert scheduler.next_rule() == first_rule
        assert scheduler.current_index() == 1

    def test_remaining_rules(self):
        """Verify remaining returns unconsumed rules."""
        scheduler = DynamicRuleScheduler("testkey", rounds=5)
        assert len(scheduler.remaining()) == 5
        scheduler.next_rule()
        scheduler.next_rule()
        assert len(scheduler.remaining()) == 3
        assert scheduler.remaining() == scheduler.schedule[2:]

    def test_next_rule_exhaustion_raises_exception(self):
        """Verify calling next_rule or peek when schedule is exhausted raises ScheduleExhaustedError."""
        scheduler = DynamicRuleScheduler("testkey", rounds=3)
        for _ in range(3):
            scheduler.next_rule()

        with pytest.raises(ScheduleExhaustedError, match="Schedule exhausted"):
            scheduler.next_rule()

        with pytest.raises(ScheduleExhaustedError, match="Schedule exhausted"):
            scheduler.peek()

    def test_reset(self):
        """Verify reset clears history and resets current_index to 0."""
        scheduler = DynamicRuleScheduler("testkey", rounds=5)
        for _ in range(3):
            scheduler.next_rule()

        assert scheduler.current_index() == 3
        assert len(scheduler.history()) == 3

        scheduler.reset()
        assert scheduler.current_index() == 0
        assert scheduler.history() == []

        # After reset, next_rule should yield the first rule again
        assert scheduler.next_rule() == scheduler.schedule[0]

    def test_export_and_import_schedule(self):
        """Verify export returns dictionary structure and import_schedule restores state."""
        scheduler = DynamicRuleScheduler("export_test_key", rounds=10)
        exported = scheduler.export()

        assert "key_hash" in exported
        assert "rules" in exported
        assert exported["rounds"] == 10
        assert len(exported["rules"]) == 10

        new_scheduler = DynamicRuleScheduler.from_export(exported)
        assert new_scheduler.schedule == scheduler.schedule
        assert new_scheduler.rounds == 10

    def test_invalid_key_handling(self):
        """Verify invalid key inputs raise appropriate exceptions."""
        with pytest.raises(InvalidKeyError, match="cannot be empty"):
            DynamicRuleScheduler("")

        with pytest.raises(InvalidKeyError, match="cannot be empty"):
            DynamicRuleScheduler(b"")

        with pytest.raises(InvalidKeyError, match="Invalid hexadecimal key string"):
            DynamicRuleScheduler("invalid_hex_string_zzz", encoding="hex")

        with pytest.raises(InvalidKeyError, match="Unsupported key encoding"):
            DynamicRuleScheduler("validkey", encoding="unsupported_fmt")

        with pytest.raises(TypeError, match="Secret key must be str, bytes, or bytearray"):
            DynamicRuleScheduler(12345)  # type: ignore

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

    def test_optimize_schedule_consecutive_rules(self):
        """Verify optimize_schedule eliminates >= 4 identical consecutive rules."""
        input_schedule = [30, 30, 30, 30, 30, 90]
        optimized = optimize_schedule(input_schedule)

        for i in range(3, len(optimized)):
            slice_4 = optimized[i - 3 : i + 1]
            assert not (slice_4[0] == slice_4[1] == slice_4[2] == slice_4[3])

    def test_optimize_schedule_short_list(self):
        """Verify optimize_schedule handles lists shorter than 4 elements."""
        short = [30, 30, 30]
        assert optimize_schedule(short) == [30, 30, 30]
