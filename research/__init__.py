"""IEEE Research Benchmarking & Publication Subsystem (`research`).

Provides reproducible benchmarks, statistical calculations, comparative evaluation,
publication-quality figures, automated experiment execution, and IEEE manuscript generators.
"""

from research.benchmark import BenchmarkRunner, get_system_metadata
from research.comparison import ComparisonEngine
from research.experiments import ExperimentRunner
from research.report import IEEEReportGenerator
from research.statistics import StatisticsEngine
from research.visualization import VisualizationEngine

__all__ = [
    "BenchmarkRunner",
    "ComparisonEngine",
    "StatisticsEngine",
    "VisualizationEngine",
    "ExperimentRunner",
    "IEEEReportGenerator",
    "get_system_metadata",
]
