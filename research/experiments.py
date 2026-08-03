"""Automated Experiment Execution & Data Storage Subsystem.

Provides `ExperimentRunner` for batch experiment execution, deterministic random seeding,
and structured preservation of raw trial data and aggregated experiment summaries.
"""

import json
import os
import random
from typing import Any, Dict, List, Optional

from research.benchmark import BenchmarkRunner
from research.comparison import ComparisonEngine


class ExperimentRunner:
    """Automated Experiment Execution Runner."""

    def __init__(self, base_dir: str = "results") -> None:
        """Initialize ExperimentRunner and prepare output directories.

        Args:
            base_dir: Base directory for experiment outputs (defaults to "results").
        """
        self.base_dir: str = base_dir
        self.raw_dir: str = os.path.join(base_dir, "raw_data")
        self.summary_dir: str = os.path.join(base_dir, "summary")
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.summary_dir, exist_ok=True)

    def run_suite(
        self,
        seed: int = 42,
        sizes: Optional[List[int]] = None,
        iterations: int = 20,
    ) -> Dict[str, Any]:
        """Execute automated benchmark and comparative research experiment suite.

        Enforces deterministic execution using specified seed value.

        Args:
            seed: Deterministic integer seed.
            sizes: Payload sizes in bytes.
            iterations: Trial count per benchmark.

        Returns:
            Dict[str, Any]: Comprehensive experiment results dictionary.
        """
        # Set deterministic seeds
        random.seed(seed)

        bench_runner = BenchmarkRunner()
        comp_engine = ComparisonEngine()

        bench_data = bench_runner.run(sizes=sizes, iterations=iterations)
        comp_data = comp_engine.compare_all(iterations=iterations)

        experiment_dataset = {
            "seed": seed,
            "benchmark": bench_data,
            "comparison": comp_data,
        }

        # Save raw data & summary
        raw_file = os.path.join(self.raw_dir, f"experiment_seed_{seed}_raw.json")
        summary_file = os.path.join(self.summary_dir, f"experiment_seed_{seed}_summary.json")

        self.save_experiment_data(experiment_dataset, raw_file)
        self.save_experiment_data({"seed": seed, "comparison": comp_data}, summary_file)

        return experiment_dataset

    def save_experiment_data(self, data: Dict[str, Any], filepath: str) -> None:
        """Save experiment dataset to JSON file.

        Args:
            data: Data dictionary.
            filepath: Destination file path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_experiment_data(self, filepath: str) -> Dict[str, Any]:
        """Load experiment dataset from JSON file.

        Args:
            filepath: Source file path.

        Returns:
            Dict[str, Any]: Loaded dataset dictionary.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
