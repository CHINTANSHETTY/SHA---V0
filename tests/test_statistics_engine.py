"""Unit tests for StatisticsEngine (research/statistics.py)."""

import pytest
from research.statistics import StatisticsEngine


class TestStatisticsEngine:
    """Tests for StatisticsEngine mean, median, variance, std dev, 95% CI, and percentiles."""

    def test_statistics_calculations(self):
        """Verify statistical metrics on known dataset."""
        engine = StatisticsEngine()
        data = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]

        res = engine.analyze(data)

        assert res["sample_count"] == 10
        assert res["mean"] == 19.0
        assert res["median"] == 19.0
        assert res["min"] == 10.0
        assert res["max"] == 28.0
        assert res["confidence_interval_95"][0] < 19.0 < res["confidence_interval_95"][1]
        assert "p50" in res["percentiles"]

        summary_str = engine.summary(res)
        assert "Statistical Summary" in summary_str
        assert "Mean: 19.000000" in summary_str

    def test_empty_dataset_handling(self):
        """Verify handling of empty or single-element datasets."""
        engine = StatisticsEngine()

        empty_res = engine.analyze([])
        assert empty_res["sample_count"] == 0
        assert empty_res["mean"] == 0.0

        single_res = engine.analyze([42.0])
        assert single_res["sample_count"] == 1
        assert single_res["mean"] == 42.0
        assert single_res["variance"] == 0.0
