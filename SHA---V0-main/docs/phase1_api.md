# Phase 1 Developer API Reference Specification

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Developer:** Ashwitha  
**Document Status:** OFFICIAL API SPECIFICATION  

---

## 1. Cellular Automata Package (`crypto/ca/`)

### 1.1 `apply_rule(rule_number: int, left: int, center: int, right: int) -> int`
Evaluates an Elementary Cellular Automata local transition rule ($0 \dots 255$) on a 3-bit neighborhood.
- **Parameters**: `rule_number` (int, $0..255$), `left` (int, 0/1), `center` (int, 0/1), `right` (int, 0/1).
- **Returns**: Resulting bit integer ($0$ or $1$).
- **Raises**: `TypeError`, `ValueError`.

### 1.2 `CellularAutomataEngine(rule: int = 30, boundary: str = "wrap")`
Class managing 1D CA state evolution.
- **Methods**:
  - `evolve(state: Any) -> list[int]`: Evolves binary state vector by 1 step.
  - `evolve_rounds(state: Any, rounds: int) -> list[int]`: Evolves state vector by `rounds` steps.
  - `set_rule(rule: int) -> None`: Sets active Wolfram rule number ($0 \dots 255$).
  - `set_boundary(mode: str) -> None`: Sets boundary mode (`"wrap"` or `"fixed_zero"`).
- **Properties**: `rule`, `boundary`.

### 1.3 CA Utilities (`crypto/ca/utils.py`)
- `string_to_bits(s: str) -> list[int]`: Converts text or binary digit string to bit array.
- `bits_to_string(bits: list[int], mode: str = "binary") -> str`: Converts bit array to string (`"binary"` or `"ascii"`).
- `validate_binary_state(state: Any) -> list[int]`: Validates and normalizes bit sequence.
- `random_binary_state(length: int, seed: int | None = None) -> list[int]`: Generates random bit array.
- `state_to_hex(state: list[int]) -> str`: Converts bit array to hex string.
- `hex_to_state(hex_str: str) -> list[int]`: Converts hex string to bit array.

---

## 2. Dynamic Rule Scheduler (`crypto/scheduler/`)

### 2.1 `map_byte_to_rule(byte: int) -> int`
Maps a single byte integer $[0, 255]$ into a Wolfram CA rule number $[0, 255]$.

### 2.2 `map_bytes_to_rules(data: bytes) -> list[int]`
Maps a bytes sequence to a list of Wolfram rule numbers.

### 2.3 `optimize_schedule(schedule: list[int]) -> list[int]`
Enforces rule diversity by deterministically altering any sequence containing $\ge 4$ identical consecutive rules.

### 2.4 `DynamicRuleScheduler(key: bytes, rounds: int = 64)`
Derives a deterministic, key-dependent rule schedule using SHA-512 digest chaining.
- **Methods**:
  - `generate_schedule() -> list[int]`: Generates and optimizes rule schedule.
  - `next_rule() -> int`: Advances pointer and returns next rule.
  - `reset() -> None`: Resets pointer to 0 and clears history.
  - `get_history() -> list[int]`: Returns copy of served rule history.
  - `current_index() -> int`: Returns current index pointer.
- **Properties**: `key`, `rounds`, `schedule`.

---

## 3. Key Expansion Module (`crypto/key/`)

### 3.1 `KeyExpansion(master_key: bytes, rounds: int = 64)`
Expands a master key into a sequence of 512-bit (64-byte) round keys via iterative SHA-512 digest chaining.
- **Methods**:
  - `generate_round_keys() -> list[bytes]`: Computes all round keys.
  - `get_round_key(index: int) -> bytes`: Returns 64-byte round key at specified index.
  - `all_round_keys() -> list[bytes]`: Returns copy of all round keys.
  - `total_rounds() -> int`: Returns total round count.
  - `key_size() -> int`: Returns master key byte length.
  - `round_key_size() -> int`: Returns 64.
  - `export_hex() -> list[str]`: Exports round keys as 128-character hex strings.
  - `@staticmethod import_hex(hex_keys: list[str]) -> list[bytes]`: Imports hex strings back into binary round keys.

---

## 4. Randomness & Entropy Evaluation (`crypto/analysis/`)

### 4.1 Entropy Functions (`crypto/analysis/entropy.py`)
- `shannon_entropy(bits: Any) -> float`: Calculates Shannon entropy $H(X) \in [0.0, 1.0]$.
- `bit_frequency(bits: Any) -> dict[str, Any]`: Calculates bit counts and ratios (`zeros`, `ones`, `zero_ratio`, `one_ratio`).
- `probability_distribution(bits: Any) -> dict[int, float]`: Calculates empirical probability distribution `{0: p0, 1: p1}`.

### 4.2 Randomness Functions (`crypto/analysis/randomness.py`)
- `runs_test(bits: Any) -> dict[str, int]`: Returns run counts (`runs`, `zero_runs`, `one_runs`).
- `autocorrelation(bits: Any, lag: int = 1) -> float`: Calculates normalized autocorrelation coefficient $A(d) \in [-1.0, 1.0]$.
- `hamming_distance(bits1: Any, bits2: Any) -> int`: Calculates bit difference count between equal-length vectors.
- `avalanche_effect(bits1: Any, bits2: Any) -> float`: Calculates avalanche ratio $\frac{\text{Hamming Distance}}{\text{Length}} \in [0.0, 1.0]$.

---

## 5. Usage Example

```python
from crypto.ca import CellularAutomataEngine
from crypto.scheduler import DynamicRuleScheduler
from crypto.key import KeyExpansion
from crypto.analysis import shannon_entropy, avalanche_effect, runs_test

# 1. Initialize Key Expansion & Scheduler
master_key = b"sample_master_key_2026"
rounds = 10

expansion = KeyExpansion(master_key, rounds=rounds)
scheduler = DynamicRuleScheduler(master_key, rounds=rounds)

# 2. Initialize CA Engine
engine = CellularAutomataEngine(boundary="wrap")
initial_state = [1, 0, 1, 0, 1, 1, 0, 0]
current_state = list(initial_state)

# 3. Step Through Pipeline
for i in range(rounds):
    rule = scheduler.next_rule()
    round_key = expansion.get_round_key(i)

    engine.set_rule(rule)
    current_state = engine.evolve(current_state)

# 4. Statistical Quality Analysis
entropy = shannon_entropy(current_state)
avalanche = avalanche_effect(initial_state, current_state)
runs = runs_test(current_state)

print(f"Final Entropy: {entropy:.4f}, Avalanche: {avalanche:.4f}, Runs: {runs['runs']}")
```
