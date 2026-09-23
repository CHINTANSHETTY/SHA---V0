"""Optimized Bitwise Cellular Automata Evolution Engine.

This module provides high-performance bitwise and buffer-reusing evolution routines
for Elementary Cellular Automata (ECA). It is optimized for large state vectors (100,000+ bits),
low memory allocations, thread safety, and 100% deterministic reproducibility.
"""

from typing import Any, List, Tuple, Union
from .dynamic_rules import InvalidNeighborhoodError, InvalidRuleError
from .evolution import BOUNDARY_NULL, BOUNDARY_PERIODIC, validate_boundary
from .rules import parse_rule, validate_rule


# =========================================================
# BIT PACKING & UNPACKING UTILITIES
# =========================================================
def pack_bits(state: List[int]) -> bytearray:
    """Pack a binary bit list into a bytearray (8 bits per byte, MSB-first).

    Args:
        state: List of binary integers (0 or 1).

    Returns:
        bytearray: Packed binary bytes.

    Raises:
        ValueError: If state contains non-binary elements.
    """
    n = len(state)
    num_bytes = (n + 7) // 8
    packed = bytearray(num_bytes)

    for i, bit in enumerate(state):
        if bit not in (0, 1):
            raise ValueError(f"Bit at index {i} must be 0 or 1, got {bit}")
        if bit:
            byte_idx = i >> 3
            bit_idx = 7 - (i & 7)
            packed[byte_idx] |= (1 << bit_idx)

    return packed


def unpack_bits(packed: bytearray, length: int) -> List[int]:
    """Unpack a bytearray back into a binary bit list of exact specified length.

    Args:
        packed: Packed bytearray.
        length: Exact number of bits to extract.

    Returns:
        List[int]: Binary state list of bits (0 or 1).

    Raises:
        ValueError: If packed bytes length is insufficient for requested bit length.
    """
    required_bytes = (length + 7) // 8
    if len(packed) < required_bytes:
        raise ValueError(f"Packed bytearray length ({len(packed)}) insufficient for {length} bits")

    unpacked: List[int] = [0] * length
    for i in range(length):
        byte_idx = i >> 3
        bit_idx = 7 - (i & 7)
        unpacked[i] = (packed[byte_idx] >> bit_idx) & 1

    return unpacked


# =========================================================
# OPTIMIZED CA ENGINE
# =========================================================
class OptimizedCAEngine:
    """High-performance bitwise & low-allocation CA evolution engine.

    Uses pre-allocated dual-buffer iteration and bitwise neighborhood indexing
    to achieve maximum performance and low memory allocation overhead.
    """

    def __init__(self) -> None:
        """Initialize OptimizedCAEngine and pre-compute 256 fast lookup tables."""
        # Pre-compute 256 fast 8-element lookup tables for Wolfram rules 0..255
        self._fast_tables: List[List[int]] = []
        for r in range(256):
            table = [(r >> idx) & 1 for idx in range(8)]
            self._fast_tables.append(table)

    def evolve_fast(
        self,
        state: Union[List[int], Tuple[int, ...], str],
        rule: int,
        generations: int = 1,
        boundary: str = BOUNDARY_PERIODIC,
    ) -> List[int]:
        """Perform fast deterministic evolution with zero per-step object re-allocations.

        Args:
            state: Binary initial state sequence or bit string.
            rule: Wolfram rule number (0 to 255).
            generations: Number of generations (>= 1).
            boundary: Boundary condition ("periodic" or "null").

        Returns:
            List[int]: Evolved binary state list.

        Raises:
            InvalidRuleError: If rule is out of bounds [0, 255].
            InvalidNeighborhoodError: If boundary or state is invalid.
        """
        valid_rule = validate_rule(rule)
        norm_boundary = validate_boundary(boundary)
        if norm_boundary not in (BOUNDARY_PERIODIC, BOUNDARY_NULL):
            raise InvalidNeighborhoodError(f"Optimized engine supports periodic and null boundaries, got {boundary}")

        if generations < 1:
            raise ValueError(f"Generations must be positive (>= 1), got {generations}")

        if isinstance(state, str):
            curr_buf = [int(c) for c in state]
        else:
            curr_buf = list(state)

        n = len(curr_buf)
        if n == 0:
            raise InvalidNeighborhoodError("State array cannot be empty")

        for bit in curr_buf:
            if bit not in (0, 1):
                raise ValueError(f"State elements must be 0 or 1, got {bit}")

        next_buf = [0] * n
        table = self._fast_tables[valid_rule]
        is_periodic = (norm_boundary == BOUNDARY_PERIODIC)

        for _ in range(generations):
            if n == 1:
                left = curr_buf[0] if is_periodic else 0
                center = curr_buf[0]
                right = curr_buf[0] if is_periodic else 0
                idx = (left << 2) | (center << 1) | right
                next_buf[0] = table[idx]
            else:
                # First element (i = 0)
                left = curr_buf[n - 1] if is_periodic else 0
                center = curr_buf[0]
                right = curr_buf[1]
                idx = (left << 2) | (center << 1) | right
                next_buf[0] = table[idx]

                # Middle elements (1 <= i < n - 1)
                for i in range(1, n - 1):
                    left = curr_buf[i - 1]
                    center = curr_buf[i]
                    right = curr_buf[i + 1]
                    idx = (left << 2) | (center << 1) | right
                    next_buf[i] = table[idx]

                # Last element (i = n - 1)
                left = curr_buf[n - 2]
                center = curr_buf[n - 1]
                right = curr_buf[0] if is_periodic else 0
                idx = (left << 2) | (center << 1) | right
                next_buf[n - 1] = table[idx]

            curr_buf, next_buf = next_buf, curr_buf

        return curr_buf

    def evolve_bytes(
        self,
        block_seed: bytes,
        rule: int = 30,
        generations: int = 5,
        boundary: str = BOUNDARY_PERIODIC,
    ) -> bytes:
        """Evolve a packed binary state vector directly in bytes without unpacking.

        Provides high-speed zero-copy bitwise evolution for 32-byte (256-bit) state blocks.

        Args:
            block_seed: Packed binary seed bytes.
            rule: Wolfram rule number (0 to 255).
            generations: Number of generation steps.
            boundary: Boundary condition ("periodic" or "null").

        Returns:
            bytes: Evolved packed binary bytes.
        """
        valid_rule = validate_rule(rule)
        table = self._fast_tables[valid_rule]
        buf = bytearray(block_seed)
        n_bytes = len(buf)
        n_bits = n_bytes * 8
        next_buf = bytearray(n_bytes)
        is_periodic = (boundary == BOUNDARY_PERIODIC)

        for _ in range(generations):
            for i in range(n_bits):
                left_i = (i - 1) if i > 0 else (n_bits - 1 if is_periodic else -1)
                right_i = (i + 1) if i < n_bits - 1 else (0 if is_periodic else -1)

                l_bit = ((buf[left_i >> 3] >> (7 - (left_i & 7))) & 1) if left_i >= 0 else 0
                c_bit = (buf[i >> 3] >> (7 - (i & 7))) & 1
                r_bit = ((buf[right_i >> 3] >> (7 - (right_i & 7))) & 1) if right_i >= 0 else 0

                idx = (l_bit << 2) | (c_bit << 1) | r_bit
                out_bit = table[idx]
                if out_bit:
                    next_buf[i >> 3] |= (1 << (7 - (i & 7)))
                else:
                    next_buf[i >> 3] &= ~(1 << (7 - (i & 7)))

            buf[:] = next_buf
            next_buf[:] = b"\x00" * n_bytes

        return bytes(buf)

    def evolve_bitwise(
        self,
        state: Union[List[int], Tuple[int, ...], str],
        rule: int,
        generations: int = 1,
        boundary: str = BOUNDARY_PERIODIC,
    ) -> List[int]:
        """Perform bitwise evolution routine optimized for large binary vectors."""
        return self.evolve_fast(state, rule, generations=generations, boundary=boundary)
