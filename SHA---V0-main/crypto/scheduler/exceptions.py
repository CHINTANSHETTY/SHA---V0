"""
Custom Exception Classes for Dynamic Rule Scheduler.
"""


class SchedulerError(Exception):
    """Base exception class for all scheduler-related errors."""
    pass


class InvalidKeyError(SchedulerError, ValueError):
    """Raised when an invalid key or key encoding is provided."""
    pass


class InvalidRuleError(SchedulerError, ValueError):
    """Raised when an invalid rule number or byte value is supplied."""
    pass


class ScheduleExhaustedError(SchedulerError, IndexError):
    """Raised when attempting to retrieve a rule beyond the schedule length."""
    pass
