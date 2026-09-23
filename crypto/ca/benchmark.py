"""Cellular Automata Benchmarking and Performance Evaluation Framework.

This module provides structured performance benchmarking for CA evolution engines.
It measures execution timing, memory usage (via tracemalloc), throughput, and scalability
across state sizes, rules, and neighborhood models.

System & Version Metadata:
    Includes Python version, platform architecture, processor info, and ISO timestamp
    to ensure research reproducibility.

Isolation:
    This module is standalone and strictly optional. It is never imported or executed
    during standard cryptographic operations.
"""

import json
import platform
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from .dynamic_rules import DynamicRuleEngine
from .evolution import DynamicEvolutionEngine
from .optimizer import OptimizedCAEngine


def _get_sys_version() -> str:
    return sys.version.replace("\n", " ")

def _get_platform() -> str:
    return platform.platform()

def _get_processor() -> str:
    return platform.processor()

def _get_machine() -> str:
    return platform.machine()


# =========================================================
# BENCHMARK METADATA & RESULT DATACLASSES
# =========================================================
@dataclass
class BenchmarkMetadata:
    """System, environment, and hardware metadata for research reproducibility.

    Attributes:
        timestamp: ISO-8601 UTC timestamp of execution.
        python_version: Full Python version string.
        platform: Platform OS and kernel description.
        processor: System CPU / processor architecture.
        machine: Hardware machine type (e.g., AMD64, x86_64).
    """

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_version: str = field(default_factory=_get_sys_version)
    platform: str = field(default_factory=_get_platform)
    processor: str = field(default_factory=_get_processor)
    machine: str = field(default_factory=_get_machine)


@dataclass
class BenchmarkResult:
    """Encapsulates execution timing, memory, and throughput metrics for a single benchmark run.

    Attributes:
        rule_id: Rule identifier (e.g. 30 or "Rule30").
        engine_type: Name of the evolution engine tested ("DynamicEvolutionEngine" or "OptimizedCAEngine").
        state_size: Number of binary bits in state vector.
        generations: Number of evolution steps.
        neighborhood_model: Radius and boundary model description (e.g. "Radius 1 (periodic)").
        execution_time_seconds: Total execution time in seconds.
        peak_memory_bytes: Peak memory allocation in bytes during run.
        throughput_ops_per_sec: Operations (generations) per second.
        throughput_bits_per_sec: Total bit evaluations per second (state_size * generations / sec).
        metadata: System metadata instance.
    """

    rule_id: Union[int, str]
    engine_type: str
    state_size: int
    generations: int
    neighborhood_model: str
    execution_time_seconds: float
    peak_memory_bytes: int
    throughput_ops_per_sec: float
    throughput_bits_per_sec: float
    metadata: BenchmarkMetadata = field(default_factory=BenchmarkMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result into a serializable dictionary."""
        d = asdict(self)
        d["rule_id"] = str(self.rule_id)
        return d


# =========================================================
# CA BENCHMARK FRAMEWORK
# =========================================================
class CABenchmark:
    """Cellular Automata Benchmarking Suite.

    Evaluates execution speed, memory footprint, throughput, and scaling for CA engines.
    """

    def __init__(self) -> None:
        """Initialize CABenchmark suite."""
        self._dynamic_engine = DynamicEvolutionEngine()
        self._optimized_engine = OptimizedCAEngine()

    def benchmark_rule(
        self,
        rule_id: Union[int, str] = 30,
        state_size: int = 1000,
        generations: int = 100,
        engine_type: str = "optimized",
        radius: int = 1,
        boundary: str = "periodic",
    ) -> BenchmarkResult:
        """Benchmark a single CA evolution configuration.

        Args:
            rule_id: Rule ID (int or str).
            state_size: Number of cells in state array.
            generations: Number of evolution generations.
            engine_type: "optimized" for OptimizedCAEngine, "dynamic" for DynamicEvolutionEngine.
            radius: Neighborhood radius (1 or 2).
            boundary: Boundary condition ("periodic", "null", "reflective", "fixed").

        Returns:
            BenchmarkResult: Metrics object.
        """
        init_state = [i % 2 for i in range(state_size)]
        nb_model = f"Radius {radius} ({boundary})"

        tracemalloc.start()
        tracemalloc.reset_peak()
        start_time = time.perf_counter()

        if engine_type.lower() in ("optimized", "fast"):
            engine_name = "OptimizedCAEngine"
            if isinstance(rule_id, int):
                rule_val = rule_id
            else:
                rule_val = int(rule_id)
            _ = self._optimized_engine.evolve_fast(init_state, rule=rule_val, generations=generations, boundary=boundary)
        else:
            engine_name = "DynamicEvolutionEngine"
            _ = self._dynamic_engine.evolve(init_state, rule_or_scheduler=rule_id, generations=generations, radius=radius, boundary=boundary)

        end_time = time.perf_counter()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed = max(end_time - start_time, 1e-9)  # Avoid zero division
        ops_per_sec = generations / elapsed
        bits_per_sec = (state_size * generations) / elapsed

        return BenchmarkResult(
            rule_id=rule_id,
            engine_type=engine_name,
            state_size=state_size,
            generations=generations,
            neighborhood_model=nb_model,
            execution_time_seconds=elapsed,
            peak_memory_bytes=peak_mem,
            throughput_ops_per_sec=ops_per_sec,
            throughput_bits_per_sec=bits_per_sec,
            metadata=BenchmarkMetadata(),
        )

    def run_benchmark(
        self,
        rules: Optional[List[Union[int, str]]] = None,
        state_sizes: Optional[List[int]] = None,
        generations: int = 100,
        engine_types: Optional[List[str]] = None,
    ) -> List[BenchmarkResult]:
        """Run a benchmark suite across multiple rules, state sizes, and engines.

        Args:
            rules: List of rule IDs to benchmark (defaults to [30, 90, 110, 150]).
            state_sizes: List of state bit lengths (defaults to [100, 1000, 10000]).
            generations: Generations per run (defaults to 100).
            engine_types: List of engine names (defaults to ["optimized", "dynamic"]).

        Returns:
            List[BenchmarkResult]: List of result objects.
        """
        rule_list = rules if rules is not None else [30, 90, 110, 150]
        size_list = state_sizes if state_sizes is not None else [100, 1000, 10000]
        engines = engine_types if engine_types is not None else ["optimized", "dynamic"]

        results: List[BenchmarkResult] = []
        for r in rule_list:
            for s in size_list:
                for eng in engines:
                    # Skip non-integer rules for optimized engine if not integer
                    if eng == "optimized" and not isinstance(r, int):
                        continue
                    res = self.benchmark_rule(rule_id=r, state_size=s, generations=generations, engine_type=eng)
                    results.append(res)

        return results

    def generate_report(self, results: List[BenchmarkResult], format: str = "markdown") -> str:
        """Generate a structured Markdown or JSON report from benchmark results.

        Args:
            results: List of BenchmarkResult objects.
            format: Output format ("markdown" or "json").

        Returns:
            str: Formatted report text.
        """
        if format.lower() == "json":
            return json.dumps([r.to_dict() for r in results], indent=2)

        meta = results[0].metadata if results else BenchmarkMetadata()
        lines: List[str] = [
            "# Cellular Automata Performance Benchmark Report",
            "",
            "## System Metadata",
            f"- **Timestamp**: `{meta.timestamp}`",
            f"- **Python Version**: `{meta.python_version}`",
            f"- **Platform**: `{meta.platform}`",
            f"- **Processor**: `{meta.processor}`",
            "",
            "## Benchmark Results",
            "",
            "| Rule | Engine | State Size | Generations | Time (s) | Peak Mem (KB) | Ops/sec | Throughput (Mbps) |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for r in results:
            mem_kb = r.peak_memory_bytes / 1024.0
            mbps = r.throughput_bits_per_sec / 1e6
            lines.append(
                f"| {r.rule_id} | {r.engine_type} | {r.state_size:,} | {r.generations:,} | "
                f"{r.execution_time_seconds:.4f} | {mem_kb:.2f} | {r.throughput_ops_per_sec:,.1f} | {mbps:.2f} |"
            )

        return "\n".join(lines)
