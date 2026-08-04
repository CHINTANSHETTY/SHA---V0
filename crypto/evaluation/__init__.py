"""
Cryptographic Research Framework Evaluation Package (`crypto.evaluation`).

Provides unified evaluation tools, statistical consolidation, performance benchmarking,
security validation, comparative analysis, and multi-format report generation.
"""

from crypto.evaluation.consolidation import PerformanceConsolidator, compute_statistics
from crypto.evaluation.evaluator import FrameworkEvaluator, run_full_evaluation_pipeline
from crypto.evaluation.reporting import ReportGenerator

__all__ = [
    "FrameworkEvaluator",
    "PerformanceConsolidator",
    "ReportGenerator",
    "compute_statistics",
    "run_full_evaluation_pipeline",
]
