# `crypto.ca` API Reference

**Subsystem:** One-Dimensional Cellular Automata State Engine & Rule Permutations  
**IEEE Mapping:** Section IV-A & IV-C  

---

## Overview

The `crypto.ca` package provides deterministic 1D Elementary Cellular Automata (ECA) evolution, 8-bit Wolfram rule parsing (0–255), state mapping, and boundary condition evaluation ("periodic" and "null").

---

## Public Functions & Classes

### 1. `crypto.ca.engine.evolve_step`

```python
def evolve_step(
    state: Union[List[int], Tuple[int, ...], str],
    lookup: Union[LookupTable, Dict[Neighborhood, int]],
    boundary: str = "periodic",
) -> State
```

Performs a single generation evolution step for a 1D Cellular Automaton binary state array.

- **Parameters:**
  - `state`: Binary state array (`[0, 1, 0, 1]`) or bit string (`"0101"`).
  - `lookup`: Dictionary mapping 3-cell neighborhood tuples `(L, C, R)` to output bits (derived via `parse_rule`).
  - `boundary`: Boundary condition string (`"periodic"` or `"null"`). Default is `"periodic"`.
- **Returns:** List of integer bits (`0` or `1`) representing the next generation state.
- **Raises:** `TypeError` if input types are invalid; `ValueError` if state elements or boundary string are unsupported.

---

### 2. `crypto.ca.engine.evolve`

```python
def evolve(
    state: Union[List[int], Tuple[int, ...], str],
    rule: Any,
    generations: Any = 1,
    boundary: Any = "periodic",
) -> State
```

Performs multi-generation deterministic 1D cellular automata evolution.

- **Parameters:**
  - `state`: Initial binary state.
  - `rule`: Wolfram rule integer (0 to 255).
  - `generations`: Number of evolution steps (positive integer `>= 1`). Default `1`.
  - `boundary`: Boundary condition (`"periodic"` or `"null"`). Default `"periodic"`.
- **Returns:** Final binary state array after requested evolution generations.

---

### 3. `crypto.ca.rules.parse_rule`

```python
def parse_rule(rule: Any) -> LookupTable
```

Parses a Wolfram rule integer (0–255) into an 8-element neighborhood lookup dictionary mapping `(L, C, R)` → output bit.

- **Parameters:**
  - `rule`: Integer rule number in range `[0, 255]`.
- **Returns:** Immutable dictionary mapping neighborhood tuples `(1, 1, 0)` → `0` or `1`.

---

### 4. `crypto.ca.mapping.bytes_to_bits` / `bits_to_bytes`

```python
def bytes_to_bits(data: bytes) -> List[int]:
    """Converts a raw bytes buffer into a flat list of 0/1 bits."""

def bits_to_bytes(bits: List[int]) -> bytes:
    """Converts a flat list of 8*N 0/1 bits back into a raw bytes buffer."""
```

Usage Example:
```python
from crypto.ca.engine import evolve
from crypto.ca.mapping import bytes_to_bits, bits_to_bytes

raw_bytes = b"EHR"
bits = bytes_to_bits(raw_bytes)
evolved_bits = evolve(bits, rule=30, generations=8, boundary="periodic")
evolved_bytes = bits_to_bytes(evolved_bits)
```
