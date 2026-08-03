"""Unit tests for ExperimentRunner (research/experiments.py)."""

import json
import os
import tempfile
import pytest
from research.experiments import ExperimentRunner


class TestExperimentRunner:
    """Tests for ExperimentRunner batch execution and reproducible data storage."""

    def test_run_suite_and_storage(self):
        """Verify experiment suite execution, raw data preservation, and loading."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            runner = ExperimentRunner(base_dir=tmp_dir)
            res = runner.run_suite(seed=42, sizes=[64, 256], iterations=3)

            assert res["seed"] == 42
            assert "benchmark" in res
            assert "comparison" in res

            raw_file = os.path.join(tmp_dir, "raw_data", "experiment_seed_42_raw.json")
            assert os.path.exists(raw_file)

            loaded = runner.load_experiment_data(raw_file)
            assert loaded["seed"] == 42
