"""
Validation Module for Cryptographic Integration Pipeline.

Validates the structural integrity, type correctness, and value bounds of pipeline outputs,
rule schedules, round keys, state vectors, and statistical analysis reports.
"""

from typing import Any, Dict, List
from crypto.integration.exceptions import PipelineValidationError


class PipelineValidator:
    """Validator for KDR-CA-AEAD pipeline components and execution outputs."""

    @staticmethod
    def validate_state(state: Any) -> bool:
        """
        Validates binary state vector.

        Args:
            state: Binary state vector.

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If state is invalid.
        """
        if not isinstance(state, (list, tuple)):
            raise PipelineValidationError(f"State must be list or tuple, got {type(state).__name__}")
        if len(state) == 0:
            raise PipelineValidationError("State vector cannot be empty")
        for i, b in enumerate(state):
            if isinstance(b, bool) or not isinstance(b, int) or b not in (0, 1):
                raise PipelineValidationError(f"State element at index {i} must be bit integer 0 or 1, got {b}")
        return True

    @staticmethod
    def validate_schedule(schedule: Any) -> bool:
        """
        Validates rule schedule sequence.

        Args:
            schedule: Rule schedule list.

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If schedule is invalid.
        """
        if not isinstance(schedule, (list, tuple)):
            raise PipelineValidationError(f"Schedule must be list or tuple, got {type(schedule).__name__}")
        if len(schedule) == 0:
            raise PipelineValidationError("Rule schedule cannot be empty")
        for i, r in enumerate(schedule):
            if isinstance(r, bool) or not isinstance(r, int) or not (0 <= r <= 255):
                raise PipelineValidationError(f"Rule at index {i} must be integer in [0, 255], got {r}")
        return True

    @staticmethod
    def validate_round_keys(round_keys: Any) -> bool:
        """
        Validates list of round keys bytes objects.

        Args:
            round_keys: Round keys list.

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If round keys structure is invalid.
        """
        if not isinstance(round_keys, (list, tuple)):
            raise PipelineValidationError(f"Round keys must be list or tuple, got {type(round_keys).__name__}")
        if len(round_keys) == 0:
            raise PipelineValidationError("Round keys list cannot be empty")
        first_len = len(round_keys[0]) if isinstance(round_keys[0], (bytes, bytearray)) else 0
        for i, rk in enumerate(round_keys):
            if not isinstance(rk, (bytes, bytearray)):
                raise PipelineValidationError(f"Round key at index {i} must be bytes, got {type(rk).__name__}")
            if len(rk) == 0 or len(rk) != first_len:
                raise PipelineValidationError(
                    f"Round key at index {i} has invalid byte length {len(rk)}, expected {first_len}"
                )
        return True

    @staticmethod
    def validate_analysis(analysis: Any) -> bool:
        """
        Validates statistical analysis report dictionary.

        Args:
            analysis: Analysis report dictionary.

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If analysis report is invalid.
        """
        if not isinstance(analysis, dict):
            raise PipelineValidationError(f"Analysis report must be dict, got {type(analysis).__name__}")
        required_keys = ("entropy", "frequency", "runs", "length")
        for key in required_keys:
            if key not in analysis:
                raise PipelineValidationError(f"Analysis report missing required key: '{key}'")

        entropy = analysis["entropy"]
        if not isinstance(entropy, (int, float)) or not (0.0 <= entropy <= 1.0):
            raise PipelineValidationError(f"Entropy must be float in [0.0, 1.0], got {entropy}")

        return True

    @staticmethod
    def validate_pipeline(pipeline_output: Any) -> bool:
        """
        Validates complete pipeline execution output dictionary.

        Args:
            pipeline_output: Output dictionary from KDRPipeline.run().

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If pipeline output is missing keys or invalid.
        """
        if not isinstance(pipeline_output, dict):
            raise PipelineValidationError(f"Pipeline output must be dict, got {type(pipeline_output).__name__}")

        required_keys = ("initial_state", "final_state", "rule_schedule", "round_keys", "analysis")
        for key in required_keys:
            if key not in pipeline_output:
                raise PipelineValidationError(f"Pipeline output missing required field: '{key}'")

        PipelineValidator.validate_state(pipeline_output["initial_state"])
        PipelineValidator.validate_state(pipeline_output["final_state"])
        PipelineValidator.validate_schedule(pipeline_output["rule_schedule"])
        PipelineValidator.validate_round_keys(pipeline_output["round_keys"])
        PipelineValidator.validate_analysis(pipeline_output["analysis"])

        if len(pipeline_output["initial_state"]) != len(pipeline_output["final_state"]):
            raise PipelineValidationError("Initial state length and final state length must match")

        return True


def validate_pipeline(pipeline_output: Any) -> bool:
    """Function wrapper for PipelineValidator.validate_pipeline."""
    return PipelineValidator.validate_pipeline(pipeline_output)


def validate_schedule(schedule: Any) -> bool:
    """Function wrapper for PipelineValidator.validate_schedule."""
    return PipelineValidator.validate_schedule(schedule)


def validate_round_keys(round_keys: Any) -> bool:
    """Function wrapper for PipelineValidator.validate_round_keys."""
    return PipelineValidator.validate_round_keys(round_keys)


def validate_state(state: Any) -> bool:
    """Function wrapper for PipelineValidator.validate_state."""
    return PipelineValidator.validate_state(state)


def validate_analysis(analysis: Any) -> bool:
    """Function wrapper for PipelineValidator.validate_analysis."""
    return PipelineValidator.validate_analysis(analysis)
