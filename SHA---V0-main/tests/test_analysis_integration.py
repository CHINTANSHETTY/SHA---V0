"""
Integration tests verifying multi-phase interoperability:
KeyExpansion (Phase 1.3) + DynamicRuleScheduler (Phase 1.2) + CA Engine (Phase 1.1) + Analysis Toolkit (Phase 1.4).
"""

import json
import pytest
from crypto.analysis import AnalysisReport, avalanche_effect, calculate_entropy, correlation
from crypto.ca import CellularAutomataEngine, random_binary_state
from crypto.key import KeyExpansion
from crypto.scheduler import DynamicRuleScheduler


class TestAnalysisIntegration:
    """Integration test suite verifying Analysis Toolkit across Phases 1.1-1.4."""

    def test_full_pipeline_analysis_report(self):
        """
        Verify exact sample code pipeline from prompt Part 8:
        DynamicRuleScheduler -> CellularAutomataEngine -> AnalysisReport.
        """
        scheduler = DynamicRuleScheduler("research-key")
        engine = CellularAutomataEngine()
        state = random_binary_state(1024, seed=42)

        for rule in scheduler.generate_schedule(200):
            engine.set_rule(rule)
            state = engine.evolve(state)

        report = AnalysisReport()
        results = report.generate(state)

        assert "entropy" in results
        assert "frequency" in results
        assert "runs" in results
        assert results["length"] == 1024
        assert 0.0 <= results["entropy"] <= 1.0

        summary_text = report.summary()
        assert "Statistical Analysis Report" in summary_text

        json_str = report.export_json()
        exported_dict = json.loads(json_str)
        assert exported_dict["length"] == 1024

    def test_avalanche_and_correlation_between_two_states(self):
        """Verify measuring avalanche effect and correlation between CA outputs."""
        e1 = CellularAutomataEngine(rule=30, boundary="wrap")
        e2 = CellularAutomataEngine(rule=90, boundary="wrap")

        initial_state1 = random_binary_state(512, seed=123)
        initial_state2 = list(initial_state1)
        initial_state2[0] ^= 1  # Flip 1 bit for avalanche test

        st1 = e1.evolve_rounds(initial_state1, 20)
        st2 = e2.evolve_rounds(initial_state2, 20)

        aval = avalanche_effect(st1, st2)
        corr = correlation(st1, st2)

        # High-quality CA cryptographic evolution yields avalanche ~ 0.5 and correlation ~ 0
        assert 0.35 <= aval <= 0.65
        assert -0.3 <= corr <= 0.3
