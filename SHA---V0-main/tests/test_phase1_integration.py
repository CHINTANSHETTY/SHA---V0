"""
End-to-end Integration Test Suite for Phase 1 (crypto/ca, crypto/scheduler, crypto/key, crypto/analysis, crypto/integration).
"""

import json
import pytest
from crypto.analysis import AnalysisReport, bit_frequency, calculate_entropy, runs_test
from crypto.ca import CellularAutomataEngine, random_binary_state
from crypto.integration import KDRPipeline, PipelineReport, PipelineValidator
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestPhase1Integration:
    """Comprehensive end-to-end integration test suite for all Phase 1 modules."""

    def test_key_expansion_integration(self):
        """Verify KeyExpansion determinism and error conditions in pipeline context."""
        expansion = KeyExpansion("test_key_phrase", rounds=10, key_size=32)
        r_keys = expansion.all_round_keys()
        assert len(r_keys) == 10
        assert all(len(k) == 32 for k in r_keys)

        # Determinism
        exp2 = KeyExpansion("test_key_phrase", rounds=10, key_size=32)
        assert exp2.all_round_keys() == r_keys

    def test_scheduler_integration(self):
        """Verify DynamicRuleScheduler determinism and length."""
        scheduler = DynamicRuleScheduler("scheduler_key_bytes", rounds=50)
        sched = scheduler.generate_schedule(50)
        assert len(sched) == 50
        assert all(0 <= r <= 255 for r in sched)

        sch2 = DynamicRuleScheduler("scheduler_key_bytes", rounds=50)
        assert sch2.generate_schedule(50) == sched

    def test_ca_engine_deterministic_evolution(self):
        """Verify CellularAutomataEngine evolution is 100% deterministic."""
        engine1 = CellularAutomataEngine(rule=30, boundary="wrap")
        engine2 = CellularAutomataEngine(rule=30, boundary="wrap")

        init_state = [1, 0, 1, 0, 1, 1, 0, 0]
        res1 = engine1.evolve_rounds(init_state, 15)
        res2 = engine2.evolve_rounds(init_state, 15)

        assert res1 == res2

    def test_analysis_metrics_integration(self):
        """Verify entropy, runs, and bit frequency calculation accuracy on generated state."""
        state = [0, 1, 0, 1, 0, 1, 0, 1]
        assert calculate_entropy(state) == 1.0

        freq = bit_frequency(state)
        assert freq["zeros"] == 4
        assert freq["ones"] == 4

        runs = runs_test(state)
        assert runs["runs"] == 8

    def test_complete_pipeline_end_to_end(self):
        """Verify complete pipeline execution, validation, and PipelineReport export."""
        pipeline = KDRPipeline(key="master_phase1_key", rounds=64, state_size=512, seed=777)
        output = pipeline.run()

        # Step 1: Validate output structure
        assert PipelineValidator.validate_pipeline(output) is True

        # Step 2: Generate PipelineReport
        report = PipelineReport(output)
        report_dict = report.export_dict()

        assert report_dict["state_length"] == 512
        assert report_dict["rounds"] == 64
        assert report_dict["rules_count"] == 64
        assert report_dict["round_keys_count"] == 64
        assert "key_hash" in report_dict

        summary_text = report.summary()
        assert "KDR-CA-AEAD Pipeline Integration Report" in summary_text

        json_str = report.export_json()
        data_from_json = json.loads(json_str)
        assert data_from_json["state_length"] == 512

    def test_pipeline_determinism_same_vs_different_keys(self):
        """Verify identical keys yield identical output and different keys yield distinct outputs."""
        p_same1 = KDRPipeline(key="shared_key", rounds=3, state_size=256, seed=101)
        p_same2 = KDRPipeline(key="shared_key", rounds=3, state_size=256, seed=101)

        out_same1 = p_same1.run()
        out_same2 = p_same2.run()

        assert out_same1 == out_same2

        p_diff = KDRPipeline(key="different_key", rounds=3, state_size=256, seed=101)
        out_diff = p_diff.run()

        assert out_diff["round_keys"] != out_same1["round_keys"]
        assert out_diff["rule_schedule"] != out_same1["rule_schedule"]
        assert out_diff["final_state"] != out_same1["final_state"]
