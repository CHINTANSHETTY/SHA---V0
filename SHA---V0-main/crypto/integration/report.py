"""
Integration Report Module for KDR-CA-AEAD Pipeline.

Aggregates pipeline execution metrics, state lengths, rule schedules, round keys,
and statistical analysis results into structured integration reports.
"""

import hashlib
import json
from typing import Any, Dict, Union
from crypto.integration.validator import validate_pipeline


class PipelineReport:
    """Pipeline Integration Report Generator."""

    def __init__(self, pipeline_output: Union[Dict[str, Any], None] = None) -> None:
        """
        Initializes PipelineReport with optional pipeline execution output.

        Args:
            pipeline_output: Output dictionary from KDRPipeline.run().
        """
        self._report_data: Dict[str, Any] = {}
        if pipeline_output is not None:
            self.generate(pipeline_output)

    def generate(self, pipeline_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a comprehensive integration report from pipeline execution output.

        Args:
            pipeline_output: Output dictionary from KDRPipeline.run().

        Returns:
            Integration report dictionary.
        """
        validate_pipeline(pipeline_output)

        init_state = pipeline_output["initial_state"]
        final_state = pipeline_output["final_state"]
        schedule = pipeline_output["rule_schedule"]
        round_keys = pipeline_output["round_keys"]
        analysis = pipeline_output["analysis"]

        key_hash = hashlib.sha512(round_keys[0]).hexdigest() if round_keys else ""

        self._report_data = {
            "state_length": len(final_state),
            "rounds": len(schedule),
            "rules_count": len(schedule),
            "round_keys_count": len(round_keys),
            "entropy": analysis.get("entropy", 0.0),
            "frequency": analysis.get("frequency", {}),
            "runs": analysis.get("runs", {}),
            "key_hash": key_hash,
        }
        return dict(self._report_data)

    def summary(self) -> str:
        """
        Generates a formatted human-readable summary of the integration report.

        Returns:
            Summary text string.
        """
        if not self._report_data:
            return "No pipeline integration report generated yet."

        freq = self._report_data["frequency"]
        runs = self._report_data["runs"]
        entropy = self._report_data["entropy"]

        return (
            f"=== KDR-CA-AEAD Pipeline Integration Report ===\n"
            f"Lattice State Size: {self._report_data['state_length']} bits\n"
            f"Evolution Rounds  : {self._report_data['rounds']}\n"
            f"Generated Rules   : {self._report_data['rules_count']}\n"
            f"Derived Round Keys: {self._report_data['round_keys_count']}\n"
            f"Key Hash Digest   : {self._report_data['key_hash'][:16]}...\n"
            f"Shannon Entropy   : {entropy:.6f} bits/bit\n"
            f"Bit Frequency     : 0s={freq.get('zeros', 0)} ({freq.get('zero_ratio', 0.0):.2%}), "
            f"1s={freq.get('ones', 0)} ({freq.get('one_ratio', 0.0):.2%})\n"
            f"Runs Statistics   : Total={runs.get('runs', 0)}, Longest={runs.get('longest_run', 0)}, "
            f"Avg={runs.get('average_run', 0.0):.2f}\n"
            f"================================================="
        )

    def export_dict(self) -> Dict[str, Any]:
        """Returns a copy of the generated integration report dictionary."""
        return dict(self._report_data)

    def export_json(self) -> str:
        """Exports the generated integration report as a formatted JSON string."""
        return json.dumps(self._report_data, indent=2)
