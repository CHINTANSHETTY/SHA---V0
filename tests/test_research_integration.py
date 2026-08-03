"""End-to-End Integration Tests for Phase 2.5 Research Framework.

Validates end-to-end integration between:
ExperimentRunner -> BenchmarkRunner -> ComparisonEngine -> StatisticsEngine -> VisualizationEngine -> IEEEReportGenerator
"""

import os
import tempfile
import pytest
from research import (
    BenchmarkRunner,
    ComparisonEngine,
    ExperimentRunner,
    IEEEReportGenerator,
    StatisticsEngine,
    VisualizationEngine,
)


class TestPhase25ResearchIntegration:
    """Integration test suite for Phase 2.5 Research & Publication Framework."""

    def test_full_research_pipeline_integration(self):
        """Verify complete research pipeline execution from benchmark to manuscript export."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. Automated Experiment Runner
            exp_runner = ExperimentRunner(base_dir=tmp_dir)
            exp_data = exp_runner.run_suite(seed=12345, sizes=[64, 256, 1024], iterations=3)

            assert exp_data["seed"] == 12345
            assert "benchmark" in exp_data
            assert "comparison" in exp_data

            # 2. Statistics Analysis Verification
            stats_engine = StatisticsEngine()
            latencies = [0.5, 0.6, 0.4, 0.55, 0.52]
            stats = stats_engine.analyze(latencies)
            assert stats["sample_count"] == 5

            # 3. Visualization Engine Export
            viz = VisualizationEngine()
            fig_dir = os.path.join(tmp_dir, "figures")
            figs = viz.export_all_figures(fig_dir, benchmark_data=exp_data["benchmark"])
            assert len(figs) >= 4
            for fig_path in figs:
                assert os.path.exists(fig_path)
                assert os.path.getsize(fig_path) > 100

            # 4. IEEE Report Generator Export
            report_gen = IEEEReportGenerator()
            report_dir = os.path.join(tmp_dir, "reports")
            reports = report_gen.export_all_reports(exp_data, report_dir)

            assert os.path.exists(reports["markdown"])
            assert os.path.exists(reports["latex"])
            assert os.path.exists(reports["json"])
            assert os.path.getsize(reports["markdown"]) > 100
            assert os.path.getsize(reports["latex"]) > 100
