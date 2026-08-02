# Phase 1 Architecture Specification: Cryptographic Foundation

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Developer:** Ashwitha  
**Document Status:** FINAL ARCHITECTURE BLUEPRINT  

---

## 1. System Overview

Phase 1 establishes the core mathematical and algorithmic foundation of the **KDR-CA-AEAD** cryptographic framework. Designed specifically for lightweight healthcare edge security, Phase 1 delivers four modular sub-packages operating under strict deterministic guarantees.

```text
                               ┌────────────────────────────────────────┐
                               │            Master Key (bytes)          │
                               └───────────────────┬────────────────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         ▼                                                   ▼
         ┌───────────────────────────────┐                   ┌───────────────────────────────┐
         │     Key Expansion Module      │                   │    Dynamic Rule Scheduler     │
         │     (crypto/key/expansion.py) │                   │ (crypto/scheduler/scheduler.py)│
         └───────────────┬───────────────┘                   └───────────────┬───────────────┘
                         │                                                   │
                         │ Round Keys (512-bit)                              │ CA Rule Sequence (0-255)
                         ▼                                                   ▼
         ┌───────────────────────────────────────────────────────────────────────────────────┐
         │                          Cellular Automata Engine                                 │
         │                         (crypto/ca/engine.py)                                     │
         └─────────────────────────────────────────┬─────────────────────────────────────────┘
                                                   │
                                                   │ Evolved Binary States
                                                   ▼
                                 ┌───────────────────────────────────┐
                                 │  Randomness & Entropy Evaluation  │
                                 │        (crypto/analysis/)         │
                                 └───────────────────────────────────┘
```

---

## 2. Component Sub-Packages

### 2.1 Cellular Automata Rule Engine (`crypto/ca/`)
- **Responsibility**: State transition engine for 1D Elementary Cellular Automata.
- **Key Modules**:
  - `rules.py`: Algorithmic evaluation of Wolfram neighborhood rules ($0 \dots 255$) via `(rule >> index) & 1`.
  - `engine.py`: Reusable `CellularAutomataEngine` class managing boundary conditions (`wrap` periodic & `fixed_zero`).
  - `utils.py`: Bit sequence validation, ASCII/hex conversion, and CSPRNG state initialization.

### 2.2 Dynamic Rule Scheduler (`crypto/scheduler/`)
- **Responsibility**: Key-dependent, pseudo-random derivation of CA rule sequences.
- **Key Modules**:
  - `mapping.py`: Map byte values $[0, 255]$ into Wolfram rules $[0, 255]$.
  - `scheduler.py`: `DynamicRuleScheduler` employing iterative SHA-512 digest chaining ($D_1 = \text{SHA512}(K), D_k = \text{SHA512}(D_{k-1})$) and `optimize_schedule` for rule diversity.

### 2.3 Key Expansion Module (`crypto/key/`)
- **Responsibility**: Derivation of cryptographically strong 512-bit (64-byte) round keys from variable-length master keys.
- **Key Modules**:
  - `expansion.py`: `KeyExpansion` class performing SHA-512 key expansion, index retrieval, and hex serialization (`export_hex`, `import_hex`).

### 2.4 Randomness & Entropy Evaluation Toolkit (`crypto/analysis/`)
- **Responsibility**: Information-theoretic and statistical quality evaluation of CA binary streams.
- **Key Modules**:
  - `entropy.py`: Shannon Entropy $H(X)$, bit frequency statistics, and empirical probability distribution.
  - `randomness.py`: Runs test, normalized autocorrelation coefficient $A(d)$, Hamming distance, and avalanche effect ratio.

---

## 3. Data Flow & Integration Pipeline

```text
[ Input Master Key & Initial Binary State ]
                 │
                 ├─► KeyExpansion.generate_round_keys() ──► [ Round Keys K_0 ... K_n (64B) ]
                 ├─► DynamicRuleScheduler.generate_schedule() ──► [ Rules R_0 ... R_n (0-255) ]
                 │
                 ▼
     [ For each Round i in 0 ... N ]:
          1. Rule R_i ──► CellularAutomataEngine.set_rule(R_i)
          2. Round Key K_i ──► Prepared for Cipher XOR / Permutation
          3. State S_i ──► CellularAutomataEngine.evolve(S_{i-1})
                 │
                 ▼
[ Evolved State S_N ] ──► [ shannon_entropy(), runs_test(), avalanche_effect() ]
```

---

## 4. Key Design Principles

1. **Strict Determinism**: Zero unseeded randomness in key derivation, rule scheduling, or statistical analysis.
2. **Zero External Dependencies**: Core algorithms implemented using Python standard libraries (`math`, `hashlib`).
3. **Decoupled Architecture**: Each sub-package operates independently with well-defined APIs.
4. **Key Separation**: Distinct master keys produce non-overlapping rule schedules and round key streams.
