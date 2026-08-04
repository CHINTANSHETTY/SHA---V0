"""
Multi-Format Research Evaluation Reporting Subsystem (`crypto.evaluation.reporting`).

Generates publication-grade evaluation reports, CSV metrics datasets, JSON schemas,
and double-column IEEE LaTeX manuscript tables into structured output hierarchy:
`evaluation_results/{benchmark, validation, comparison, reports, latex, csv, json, metadata}/`.
"""

import csv
import datetime
import json
import os
from typing import Any, Dict, List, Optional


class ReportGenerator:
    """Publication-ready multi-format report and dataset exporter."""

    def __init__(self, base_output_dir: str = "evaluation_results") -> None:
        """Initialize ReportGenerator with target directory hierarchy."""
        self.base_dir: str = base_output_dir
        self.subdirs: Dict[str, str] = {
            "benchmark": os.path.join(self.base_dir, "benchmark"),
            "validation": os.path.join(self.base_dir, "validation"),
            "comparison": os.path.join(self.base_dir, "comparison"),
            "reports": os.path.join(self.base_dir, "reports"),
            "latex": os.path.join(self.base_dir, "latex"),
            "csv": os.path.join(self.base_dir, "csv"),
            "json": os.path.join(self.base_dir, "json"),
            "metadata": os.path.join(self.base_dir, "metadata"),
        }
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create structured output subdirectories if they do not exist."""
        for path in self.subdirs.values():
            os.makedirs(path, exist_ok=True)

    def generate_performance_markdown(self, eval_data: Dict[str, Any]) -> str:
        """Generate IEEE Performance Report Markdown chapter.

        Args:
            eval_data: Master evaluation dataset dictionary.

        Returns:
            str: Markdown string.
        """
        benchmarks = eval_data.get("benchmarks", {})
        kdr_data = benchmarks.get("kdr_ca_aead", [])

        md = r"""# Phase 4.2 Comprehensive Evaluation Report: KDR-CA-AEAD

## I. Benchmarking & Scalability Performance Summary

Performance benchmarks evaluated execution latency, throughput scaling, memory allocation, and CPU computation across target payload buffer sizes.

| Payload Size | Enc Latency Mean (ms) | 95% CI Margin (ms) | Enc Throughput (MB/s) | Dec Throughput (MB/s) | Peak Memory (KB) |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for item in kdr_data:
            sz_lbl = f"{item['payload_size_mb']} MB" if item['payload_size_mb'] >= 1.0 else f"{item['payload_size_kb']} KB"
            enc_lat = item["encryption"]["latency_ms"]
            enc_tp = item["encryption"]["throughput_mb_s"]
            dec_tp = item["decryption"]["throughput_mb_s"]
            md += f"| **{sz_lbl}** | `{enc_lat['mean']:.4f} ms` | `±{enc_lat['ci_95_margin']:.4f} ms` | **`{enc_tp['mean']:.2f} MB/s`** | **`{dec_tp['mean']:.2f} MB/s`** | `{item['peak_memory_kb']} KB` |\n"

        md += "\n---\n\n## II. Comparative Benchmark Evaluation\n\n"
        comp = eval_data.get("comparative_analysis", {})
        md += "| Cipher Algorithm | Payload Size | Enc Throughput (MB/s) | Dec Throughput (MB/s) | Latency (ms) |\n"
        md += "| :--- | :--- | :--- | :--- | :--- |\n"
        for cipher, data in comp.items():
            for entry in data:
                sz_lbl = f"{entry['payload_size_kb']} KB"
                md += f"| **{cipher}** | `{sz_lbl}` | `{entry['encryption']['throughput_mb_s']['mean']:.2f} MB/s` | `{entry['decryption']['throughput_mb_s']['mean']:.2f} MB/s` | `{entry['encryption']['latency_ms']['mean']:.4f} ms` |\n"

        return md

    def generate_ieee_latex_tables(self, eval_data: Dict[str, Any]) -> str:
        """Generate IEEE double-column LaTeX table markup for research paper submission.

        Args:
            eval_data: Master evaluation dataset dictionary.

        Returns:
            str: IEEE LaTeX code.
        """
        benchmarks = eval_data.get("benchmarks", {}).get("kdr_ca_aead", [])
        tex = r"""\begin{table*}[htbp]
\caption{KDR-CA-AEAD Performance Scalability Benchmark Summary Across Payload Sizes}
\label{tab:kdr_performance_scaling}
\centering
\begin{tabular}{lcccccc}
\toprule
\textbf{Payload Buffer} & \textbf{Enc Mean (ms)} & \textbf{95\% CI (ms)} & \textbf{Enc Speed (MB/s)} & \textbf{Dec Speed (MB/s)} & \textbf{Peak RAM (KB)} \\
\midrule
"""
        for item in benchmarks:
            sz_lbl = f"{item['payload_size_mb']} MB" if item['payload_size_mb'] >= 1.0 else f"{item['payload_size_kb']} KB"
            enc_lat = item["encryption"]["latency_ms"]
            enc_tp = item["encryption"]["throughput_mb_s"]
            dec_tp = item["decryption"]["throughput_mb_s"]
            tex += f"{sz_lbl} & {enc_lat['mean']:.3f} & \\pm {enc_lat['ci_95_margin']:.3f} & {enc_tp['mean']:.2f} & {dec_tp['mean']:.2f} & {item['peak_memory_kb']:.1f} \\\\\n"

        tex += r"""\bottomrule
\end{tabular}
\end{table*}
"""
        return tex

    def export_all_reports(self, eval_data: Dict[str, Any]) -> Dict[str, str]:
        """Export all reports, CSVs, JSON, LaTeX, and metadata files into evaluation_results/.

        Args:
            eval_data: Master evaluation dataset.

        Returns:
            Dict[str, str]: Dictionary mapping format key to file path.
        """
        # 1. Reports Markdown
        md_content = self.generate_performance_markdown(eval_data)
        md_file = os.path.join(self.subdirs["reports"], "final_evaluation_report.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 2. LaTeX Table
        latex_content = self.generate_ieee_latex_tables(eval_data)
        latex_file = os.path.join(self.subdirs["latex"], "ieee_performance_table.tex")
        with open(latex_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # 3. JSON Summary
        json_file = os.path.join(self.subdirs["json"], "evaluation_summary.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, indent=2)

        # 4. Reproducibility Metadata
        meta_file = os.path.join(self.subdirs["metadata"], "reproducibility_manifest.json")
        repro_data = eval_data.get("reproducibility", {})
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(repro_data, f, indent=2)

        # 5. CSV Export
        csv_file = os.path.join(self.subdirs["csv"], "benchmark_metrics.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Cipher", "Payload_Bytes", "Enc_Mean_ms", "Enc_95CI_ms", "Enc_Throughput_MBs", "Dec_Throughput_MBs", "Peak_RAM_KB"])
            for item in eval_data.get("benchmarks", {}).get("kdr_ca_aead", []):
                writer.writerow([
                    "KDR-CA-AEAD",
                    item["payload_size_bytes"],
                    item["encryption"]["latency_ms"]["mean"],
                    item["encryption"]["latency_ms"]["ci_95_margin"],
                    item["encryption"]["throughput_mb_s"]["mean"],
                    item["decryption"]["throughput_mb_s"]["mean"],
                    item["peak_memory_kb"],
                ])

        return {
            "markdown_report": md_file,
            "latex_table": latex_file,
            "json_summary": json_file,
            "csv_metrics": csv_file,
            "reproducibility_manifest": meta_file,
        }
