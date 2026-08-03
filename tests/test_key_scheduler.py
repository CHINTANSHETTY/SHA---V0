"""Unit tests for AdaptiveKeyScheduler (crypto/key/adaptive_schedule.py)."""

import pytest
from crypto.key.adaptive_schedule import AdaptiveKeyScheduler, SchedulerError
from crypto.key.evolution import KeyEvolutionEngine


class TestAdaptiveKeyScheduler:
    """Tests for AdaptiveKeyScheduler modes and deterministic behavior."""

    def test_sequential_mode(self):
        """Verify sequential mode derives round keys sequentially."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"
        sched = AdaptiveKeyScheduler(mode=AdaptiveKeyScheduler.MODE_SEQUENTIAL)

        k0 = sched.next_key(engine, master)
        k1 = sched.next_key(engine, master)

        assert k0 == engine.derive_round_key(master, round_num=0)
        assert k1 == engine.derive_round_key(master, round_num=1)
        assert k0 != k1

    def test_cyclic_mode(self):
        """Verify cyclic mode loops through round sequence."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"
        rounds = [10, 20, 30]
        sched = AdaptiveKeyScheduler(mode=AdaptiveKeyScheduler.MODE_CYCLIC, round_sequence=rounds)

        k0 = sched.next_key(engine, master)
        k1 = sched.next_key(engine, master)
        k2 = sched.next_key(engine, master)
        k3 = sched.next_key(engine, master)

        assert k0 == engine.derive_round_key(master, round_num=10)
        assert k1 == engine.derive_round_key(master, round_num=20)
        assert k2 == engine.derive_round_key(master, round_num=30)
        assert k3 == k0  # cycles back to 10

    def test_session_mode(self):
        """Verify session mode derives session keys."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"
        sessions = ["s1", "s2"]
        sched = AdaptiveKeyScheduler(mode=AdaptiveKeyScheduler.MODE_SESSION, session_sequence=sessions)

        k0 = sched.next_key(engine, master)
        k1 = sched.next_key(engine, master)

        assert k0 == engine.derive_session_key(master, session_id="s1")
        assert k1 == engine.derive_session_key(master, session_id="s2")

    def test_deterministic_random_mode(self):
        """Verify deterministic random mode produces reproducible key sequence."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"

        s1 = AdaptiveKeyScheduler(mode=AdaptiveKeyScheduler.MODE_DETERMINISTIC_RANDOM, seed_value=999)
        s2 = AdaptiveKeyScheduler(mode=AdaptiveKeyScheduler.MODE_DETERMINISTIC_RANDOM, seed_value=999)

        seq1 = [s1.next_key(engine, master) for _ in range(5)]
        seq2 = [s2.next_key(engine, master) for _ in range(5)]

        assert seq1 == seq2

    def test_export_schedule_non_destructive(self):
        """Verify export_schedule returns sequence without mutating step counter."""
        engine = KeyEvolutionEngine()
        master = b"master_key_bytes_123456789012345"
        sched = AdaptiveKeyScheduler(mode=AdaptiveKeyScheduler.MODE_SEQUENTIAL)

        exported = sched.export_schedule(engine, master, length=3)
        assert len(exported) == 3
        # First call to next_key should still be step 0
        assert sched.next_key(engine, master) == exported[0]
