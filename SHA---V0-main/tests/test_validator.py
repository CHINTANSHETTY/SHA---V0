"""
Unit tests for Pipeline Validator (crypto/integration/validator.py).
"""

import pytest
from crypto.integration import (
    PipelineValidationError,
    PipelineValidator,
    validate_analysis,
    validate_pipeline,
    validate_round_keys,
    validate_schedule,
    validate_state,
)


class TestPipelineValidator:
    """Test suite for PipelineValidator and validation helper functions."""

    def test_validate_state_valid(self):
        """Verify valid binary state vectors pass validation."""
        assert validate_state([0, 1, 1, 0]) is True
        assert PipelineValidator.validate_state((1, 0, 0, 1)) is True

    def test_validate_state_invalid(self):
        """Verify invalid binary states raise PipelineValidationError."""
        with pytest.raises(PipelineValidationError, match="must be list or tuple"):
            validate_state("1010")  # type: ignore

        with pytest.raises(PipelineValidationError, match="cannot be empty"):
            validate_state([])

        with pytest.raises(PipelineValidationError, match="must be bit integer"):
            validate_state([0, 2, 1])

        with pytest.raises(PipelineValidationError, match="must be bit integer"):
            validate_state([0, True, 1])  # type: ignore

    def test_validate_schedule_valid(self):
        """Verify valid Wolfram rule schedules pass validation."""
        assert validate_schedule([0, 30, 90, 110, 150, 255]) is True

    def test_validate_schedule_invalid(self):
        """Verify invalid rule numbers or types raise PipelineValidationError."""
        with pytest.raises(PipelineValidationError, match="cannot be empty"):
            validate_schedule([])

        with pytest.raises(PipelineValidationError, match="must be integer in"):
            validate_schedule([30, -1, 90])

        with pytest.raises(PipelineValidationError, match="must be integer in"):
            validate_schedule([30, 256, 90])

        with pytest.raises(PipelineValidationError, match="must be integer in"):
            validate_schedule([30, "90", 110])  # type: ignore

    def test_validate_round_keys_valid(self):
        """Verify valid round key lists pass validation."""
        keys = [b"A" * 32, b"B" * 32, b"C" * 32]
        assert validate_round_keys(keys) is True

    def test_validate_round_keys_invalid(self):
        """Verify invalid round key elements or length mismatches raise PipelineValidationError."""
        with pytest.raises(PipelineValidationError, match="cannot be empty"):
            validate_round_keys([])

        with pytest.raises(PipelineValidationError, match="must be bytes"):
            validate_round_keys([b"A" * 32, "string_key"])  # type: ignore

        with pytest.raises(PipelineValidationError, match="invalid byte length"):
            validate_round_keys([b"A" * 32, b"B" * 16])

    def test_validate_analysis_valid(self):
        """Verify valid analysis report dict passes validation."""
        analysis = {
            "entropy": 0.99,
            "frequency": {"zeros": 10, "ones": 10, "zero_ratio": 0.5, "one_ratio": 0.5},
            "runs": {"runs": 10, "longest_run": 3, "average_run": 2.0},
            "length": 20,
        }
        assert validate_analysis(analysis) is True

    def test_validate_analysis_invalid(self):
        """Verify missing fields or invalid entropy values raise PipelineValidationError."""
        with pytest.raises(PipelineValidationError, match="missing required key"):
            validate_analysis({"entropy": 0.5})

        with pytest.raises(PipelineValidationError, match="Entropy must be float in"):
            validate_analysis({"entropy": 1.5, "frequency": {}, "runs": {}, "length": 20})

    def test_validate_pipeline_full_valid(self):
        """Verify full pipeline output dictionary passes validation."""
        valid_output = {
            "initial_state": [0, 1, 0, 1],
            "final_state": [1, 0, 1, 0],
            "rule_schedule": [30, 90],
            "round_keys": [b"A" * 32, b"B" * 32],
            "analysis": {
                "entropy": 1.0,
                "frequency": {"zeros": 2, "ones": 2, "zero_ratio": 0.5, "one_ratio": 0.5},
                "runs": {"runs": 4, "longest_run": 1, "average_run": 1.0},
                "length": 4,
            },
        }
        assert validate_pipeline(valid_output) is True

    def test_validate_pipeline_state_length_mismatch(self):
        """Verify mismatched initial and final state lengths raise PipelineValidationError."""
        invalid_output = {
            "initial_state": [0, 1, 0, 1],
            "final_state": [1, 0],
            "rule_schedule": [30, 90],
            "round_keys": [b"A" * 32, b"B" * 32],
            "analysis": {
                "entropy": 1.0,
                "frequency": {},
                "runs": {},
                "length": 2,
            },
        }
        with pytest.raises(PipelineValidationError, match="length and final state length must match"):
            validate_pipeline(invalid_output)
