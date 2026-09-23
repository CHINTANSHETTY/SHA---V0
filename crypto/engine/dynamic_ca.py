"""
Module:
    dynamic_ca.py

Project:
    KDR-CA-AEAD

Purpose:
    Implements the Keyed Dynamically-Reconfigured Cellular Automata (K-DCA) state engine.
    Applies reversible non-linear local rule transitions, dual-rule coupling, inter-byte state
    chaining, and keyed circular bit rotations.

Author:
    Chintan (Project Lead, Cryptography Lead, Research Lead)

Version:
    1.0.0 (Frozen Architecture Candidate A-Chain)

IEEE Mapping:
    Section IV-C – Keyed Dynamic CA State Engine Architecture

Dependencies:
    typing
    crypto.engine.key_schedule (KeyMaterial)

Security Classification:
    Core Non-Linear Permutation-Substitution Primitive
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, Sequence

if TYPE_CHECKING:
    from crypto.engine.key_schedule import KeyMaterial

__all__ = [
    "DynamicCAEngine",
    "apply_keyed_ca_forward",
    "apply_keyed_ca_inverse",
    "BytesLike",
    "DEFAULT_RULE_OFFSET",
    "INITIAL_FEEDBACK_IV",
]

BytesLike: TypeAlias = bytes | bytearray

# =========================================================
# FROZEN ARCHITECTURAL CONSTANTS (ADR-003 / Phase 2.1C)
# =========================================================
DEFAULT_RULE_OFFSET: int = 13
INITIAL_FEEDBACK_IV: int = 0xC5
EXPECTED_RULE_TABLE_SIZE: int = 32


def _evaluate_eca_byte(position: int, rule1: int, rule2: int) -> int:
    """Evaluates 1D 8-bit periodic Wolfram Elementary Cellular Automata state evolution.

    Preconditions:
        - position is a non-negative integer position index.
        - rule1 and rule2 are uint8 ECA rule numbers in [0, 255].

    Postconditions:
        - Returns a single key-dependent uint8 byte integer in [0, 255].

    Args:
        position: Byte position index in the payload stream.
        rule1: Primary uint8 local ECA rule number.
        rule2: Secondary uint8 local ECA rule number.

    Returns:
        Transformed uint8 byte integer.
    """
    initial_state = (position ^ rule1) & 0xFF
    new_byte = 0

    for i in range(8):
        left = (initial_state >> ((i + 1) % 8)) & 1
        self_bit = (initial_state >> i) & 1
        right = (initial_state >> ((i - 1) % 8)) & 1

        neighborhood = (left << 2) | (self_bit << 1) | right
        new_bit = (rule2 >> neighborhood) & 1
        new_byte |= (new_bit << i)

    return new_byte ^ rule1


def _validate_inputs(data: BytesLike, rule_table: Sequence[int]) -> None:
    """Validates payload and rule table inputs.

    Raises:
        TypeError: If input data or rule_table types are invalid.
        ValueError: If rule_table length != 32 or contains elements outside [0, 255].
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Payload data must be a BytesLike object (bytes or bytearray).")

    if not isinstance(rule_table, (tuple, list)):
        raise TypeError("Rule table must be a tuple or list of uint8 integers.")

    if len(rule_table) != EXPECTED_RULE_TABLE_SIZE:
        raise ValueError(f"Rule table must contain exactly {EXPECTED_RULE_TABLE_SIZE} uint8 rules.")

    for r in rule_table:
        if not isinstance(r, int) or not (0 <= r <= 255):
            raise ValueError("All elements in rule_table must be uint8 integers in range [0, 255].")


def apply_keyed_ca_forward(
    data: BytesLike,
    rule_table: Sequence[int],
    delta: int = DEFAULT_RULE_OFFSET
) -> bytes:
    """Applies Keyed Dynamic Cellular Automata Candidate A-Chain forward transformation.

    Pipeline (Candidate A-Chain):
        1. Mix input byte with previous state feedback vector: mixed_b = p_i ^ prev_state
        2. Keyed Modulo Addition: y1 = (mixed_b + S_ECA) mod 256
        3. Keyed Circular Right Rotation: y2 = ROTR_8(y1, (R_1 mod 7) + 1)
        4. XOR Secondary Rule Mixing: t_i = y2 ^ R_2
        5. Update feedback vector: prev_state = t_i

    Args:
        data: Plaintext input bytes or bytearray buffer.
        rule_table: Sequence of 32 uint8 CA rules derived from KeySchedule.
        delta: Dual-rule coupling prime offset index (default 13).

    Returns:
        Transformed bytes buffer of identical length.
    """
    if not data:
        return b""

    _validate_inputs(data, rule_table)

    table_len = len(rule_table)
    result = bytearray(len(data))
    prev_state = INITIAL_FEEDBACK_IV

    for i, byte_val in enumerate(data):
        rule1 = rule_table[i % table_len]
        rule2 = rule_table[(i + delta) % table_len]

        ca_byte = _evaluate_eca_byte(i, rule1, rule2)
        shift_amt = (rule1 % 7) + 1

        # Step 1: Inter-byte state chaining mix & modulo addition
        mixed_byte = byte_val ^ prev_state
        y1 = (mixed_byte + ca_byte) & 0xFF

        # Step 2: Keyed circular right shift
        y2 = ((y1 >> shift_amt) | (y1 << (8 - shift_amt))) & 0xFF

        # Step 3: XOR rule mixing & feedback update
        out_byte = y2 ^ rule2
        result[i] = out_byte
        prev_state = out_byte

    return bytes(result)


def apply_keyed_ca_inverse(
    data: BytesLike,
    rule_table: Sequence[int],
    delta: int = DEFAULT_RULE_OFFSET
) -> bytes:
    """Applies Keyed Dynamic Cellular Automata Candidate A-Chain inverse transformation.

    Pipeline Inverse:
        1. Step 3 Inverse: y2 = t_i ^ R_2
        2. Step 2 Inverse: y1 = ROTL_8(y2, (R_1 mod 7) + 1)
        3. Step 1 Inverse: mixed_b = (y1 - S_ECA) mod 256
        4. State Un-chaining: p_i = mixed_b ^ prev_state
        5. Update feedback vector: prev_state = t_i

    Args:
        data: Transformed input bytes or bytearray buffer.
        rule_table: Sequence of 32 uint8 CA rules derived from KeySchedule.
        delta: Dual-rule coupling prime offset index (default 13).

    Returns:
        Recovered original plaintext bytes buffer of identical length.
    """
    if not data:
        return b""

    _validate_inputs(data, rule_table)

    table_len = len(rule_table)
    result = bytearray(len(data))
    prev_state = INITIAL_FEEDBACK_IV

    for i, byte_val in enumerate(data):
        rule1 = rule_table[i % table_len]
        rule2 = rule_table[(i + delta) % table_len]

        ca_byte = _evaluate_eca_byte(i, rule1, rule2)
        shift_amt = (rule1 % 7) + 1

        # Step 3 Inverse: XOR un-mixing
        y2 = byte_val ^ rule2

        # Step 2 Inverse: Keyed circular left shift
        y1 = ((y2 << shift_amt) | (y2 >> (8 - shift_amt))) & 0xFF

        # Step 1 Inverse: Modulo subtraction & state un-chaining
        mixed_byte = (y1 - ca_byte) & 0xFF
        orig_byte = mixed_byte ^ prev_state

        result[i] = orig_byte
        prev_state = byte_val

    return bytes(result)


class DynamicCAEngine:
    """Keyed Dynamically-Reconfigured Cellular Automata Engine Class Instance."""

    def __init__(self, rule_table: Sequence[int], delta: int = DEFAULT_RULE_OFFSET) -> None:
        """Initializes DynamicCAEngine instance with an immutable rule table."""
        _validate_inputs(b"\x00", rule_table)
        self._rule_table: tuple[int, ...] = tuple(rule_table)
        self._delta: int = delta

    @classmethod
    def from_key_material(
        cls,
        key_material: KeyMaterial,
        delta: int = DEFAULT_RULE_OFFSET
    ) -> DynamicCAEngine:
        """Factory constructor instantiating engine from KeyMaterial instance."""
        return cls(key_material.rule_table, delta)

    @property
    def rule_table(self) -> tuple[int, ...]:
        """Returns immutable rule table tuple."""
        return self._rule_table

    def transform_forward(self, data: BytesLike) -> bytes:
        """Applies forward Dynamic CA Candidate A-Chain transformation."""
        return apply_keyed_ca_forward(data, self._rule_table, self._delta)

    def transform_inverse(self, data: BytesLike) -> bytes:
        """Applies inverse Dynamic CA Candidate A-Chain transformation."""
        return apply_keyed_ca_inverse(data, self._rule_table, self._delta)
