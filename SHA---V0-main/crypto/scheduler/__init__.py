"""
Dynamic Rule Scheduler Package for KDR-CA-AEAD.
"""

from crypto.scheduler.exceptions import (
    InvalidKeyError,
    InvalidRuleError,
    ScheduleExhaustedError,
    SchedulerError,
)
from crypto.scheduler.mapping import (
    bytes_to_rules,
    map_byte_to_rule,
    map_bytes_to_rules,
    rule_from_byte,
    validate_rule,
)
from crypto.scheduler.scheduler import DynamicRuleScheduler, optimize_schedule

__all__ = [
    "rule_from_byte",
    "bytes_to_rules",
    "map_byte_to_rule",
    "map_bytes_to_rules",
    "validate_rule",
    "optimize_schedule",
    "DynamicRuleScheduler",
    "SchedulerError",
    "InvalidKeyError",
    "InvalidRuleError",
    "ScheduleExhaustedError",
]
