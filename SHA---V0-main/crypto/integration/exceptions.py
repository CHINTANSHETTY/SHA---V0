"""
Custom Exception Classes for Integration Layer.
"""


class IntegrationError(Exception):
    """Base exception class for pipeline integration errors."""
    pass


class PipelineValidationError(IntegrationError, ValueError):
    """Raised when pipeline structure or output validation fails."""
    pass
