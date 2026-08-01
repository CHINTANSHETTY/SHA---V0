"""
Keyed Dynamically-Reconfigured Cellular Automata (K-DCA) Local Rule Engine.

IEEE Mapping: Section IV-C (Keyed Dynamic CA State Engine)
"""


def _ca_rule_keystream_byte(position: int, rule1: int, rule2: int) -> int:
    """Computes a key-dependent 8-bit Cellular Automata transformation byte.

    Uses 1D periodic elementary CA rule_num over rule state.

    Args:
        position: Byte position index in payload.
        rule1: First local CA rule number uint8 (0-255).
        rule2: Second local CA rule number uint8 (0-255).

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


def apply_keyed_ca_forward(data: bytes, rule_table: list[int]) -> bytes:
    """Applies Keyed Dynamic Cellular Automata forward transformation.

    Args:
        data: Plaintext payload bytes.
        rule_table: List of 32 uint8 rule numbers derived from K_r.

    Returns:
        Transformed bytes of identical length.
    """
    if not data:
        return b""

    if not rule_table:
        raise ValueError("Rule table cannot be empty.")

    table_len = len(rule_table)
    result = bytearray(len(data))

    for i, byte_val in enumerate(data):
        rule1 = rule_table[i % table_len]
        rule2 = rule_table[(i + 13) % table_len]

        ca_byte = _ca_rule_keystream_byte(i, rule1, rule2)

        # Step 1: Reversible key-dependent modulo addition
        added = (byte_val + ca_byte) & 0xFF

        # Step 2: Keyed circular right shift
        shift_amt = (rule1 % 7) + 1
        rotated = ((added >> shift_amt) | (added << (8 - shift_amt))) & 0xFF

        # Step 3: XOR mixing with rule2
        result[i] = rotated ^ rule2

    return bytes(result)


def apply_keyed_ca_inverse(data: bytes, rule_table: list[int]) -> bytes:
    """Applies Keyed Dynamic Cellular Automata inverse transformation.

    Args:
        data: Transformed payload bytes.
        rule_table: List of 32 uint8 rule numbers derived from K_r.

    Returns:
        Original plaintext bytes.
    """
    if not data:
        return b""

    if not rule_table:
        raise ValueError("Rule table cannot be empty.")

    table_len = len(rule_table)
    result = bytearray(len(data))

    for i, byte_val in enumerate(data):
        rule1 = rule_table[i % table_len]
        rule2 = rule_table[(i + 13) % table_len]

        ca_byte = _ca_rule_keystream_byte(i, rule1, rule2)
        shift_amt = (rule1 % 7) + 1

        # Reverse Step 3: XOR un-mixing
        rotated = byte_val ^ rule2

        # Reverse Step 2: Keyed circular left shift
        added = ((rotated << shift_amt) | (rotated >> (8 - shift_amt))) & 0xFF

        # Reverse Step 1: Reversible modulo subtraction
        original_byte = (added - ca_byte) & 0xFF

        result[i] = original_byte

    return bytes(result)
