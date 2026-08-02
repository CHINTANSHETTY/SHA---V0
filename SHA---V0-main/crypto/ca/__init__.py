"""
Cellular Automata (CA) Package for KDR-CA-AEAD.
"""

from crypto.ca.engine import CellularAutomataEngine
from crypto.ca.rules import apply_rule, get_rule_truth_table, validate_rule_number
from crypto.ca.utils import (
    bits_to_string,
    hex_to_state,
    random_binary_state,
    state_to_hex,
    string_to_bits,
    validate_binary_state,
)

__all__ = [
    "apply_rule",
    "get_rule_truth_table",
    "validate_rule_number",
    "CellularAutomataEngine",
    "string_to_bits",
    "bits_to_string",
    "validate_binary_state",
    "random_binary_state",
    "state_to_hex",
    "hex_to_state",
]
