"""
Unit tests for Integration Pipeline (crypto/integration/pipeline.py).
"""

import pytest
from crypto.integration import KDRPipeline


class TestKDRPipeline:
    """Test suite for KDRPipeline class."""

    def test_pipeline_execution(self):
        """Verify pipeline runs and produces all required output keys."""
        pipeline = KDRPipeline(key="research-key-2026", rounds=50, state_size=256, seed=42)
        out = pipeline.run()

        assert "initial_state" in out
        assert "final_state" in out
        assert "rule_schedule" in out
        assert "round_keys" in out
        assert "analysis" in out

        assert len(out["initial_state"]) == 256
        assert len(out["final_state"]) == 256
        assert len(out["rule_schedule"]) == 50
        assert len(out["round_keys"]) == 50
        assert out["analysis"]["length"] == 256

    def test_pipeline_getter_methods(self):
        """Verify pipeline getter methods after execution."""
        pipeline = KDRPipeline(key="getter_test_key", rounds=10, state_size=128, seed=123)
        pipeline.run()

        assert len(pipeline.initial_state()) == 128
        assert len(pipeline.final_state()) == 128
        assert len(pipeline.rule_schedule()) == 10
        assert len(pipeline.round_keys()) == 10
        assert pipeline.analysis()["length"] == 128

    def test_same_key_produces_identical_outputs(self):
        """Verify determinism: identical key and seed produce identical outputs."""
        p1 = KDRPipeline(key="identical_key", rounds=30, state_size=512, seed=999)
        p2 = KDRPipeline(key="identical_key", rounds=30, state_size=512, seed=999)

        o1 = p1.run()
        o2 = p2.run()

        assert o1["initial_state"] == o2["initial_state"]
        assert o1["rule_schedule"] == o2["rule_schedule"]
        assert o1["round_keys"] == o2["round_keys"]
        assert o1["final_state"] == o2["final_state"]
        assert o1["analysis"] == o2["analysis"]

    def test_different_keys_produce_different_outputs(self):
        """Verify distinct keys produce distinct rule schedules, round keys, and final states."""
        p1 = KDRPipeline(key="key_alpha", rounds=30, state_size=512, seed=999)
        p2 = KDRPipeline(key="key_beta", rounds=30, state_size=512, seed=999)

        o1 = p1.run()
        o2 = p2.run()

        assert o1["round_keys"] != o2["round_keys"]
        assert o1["rule_schedule"] != o2["rule_schedule"]
        assert o1["final_state"] != o2["final_state"]

    @pytest.mark.parametrize("state_bits", [256, 512, 1024, 2048])
    def test_performance_different_state_sizes(self, state_bits):
        """Verify successful execution for 256, 512, 1024, and 2048 bits lattice sizes."""
        pipeline = KDRPipeline(key="perf_key", rounds=20, state_size=state_bits, seed=42)
        out = pipeline.run()

        assert len(out["initial_state"]) == state_bits
        assert len(out["final_state"]) == state_bits
        assert out["analysis"]["length"] == state_bits

    def test_invalid_rounds_or_state_size_handling(self):
        """Verify invalid rounds or state_size parameters raise ValueError."""
        with pytest.raises(ValueError, match="Rounds must be a positive integer"):
            KDRPipeline(key="valid", rounds=0, state_size=256)

        with pytest.raises(ValueError, match="Rounds must be a positive integer"):
            KDRPipeline(key="valid", rounds=-10, state_size=256)

        with pytest.raises(ValueError, match="State size must be a positive integer"):
            KDRPipeline(key="valid", rounds=10, state_size=0)

        with pytest.raises(ValueError, match="State size must be a positive integer"):
            KDRPipeline(key="valid", rounds=10, state_size=-256)
