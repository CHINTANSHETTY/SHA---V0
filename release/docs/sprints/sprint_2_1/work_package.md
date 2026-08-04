# ENGINEERING WORK PACKAGE & RESEARCH ARCHITECTURE SPECIFICATION: PHASE 2.1 & 2.1A (DYNAMIC CELLULAR AUTOMATA ENGINE)

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Module Target:** `crypto/engine/dynamic_ca.py`  
**Assigned Lead:** Chintan (Project Lead, Cryptography Lead, Research Lead)  
**Phase:** Phase 2 (Dynamic Cellular Automata Core) – Sub-Phase 2.1 (Architecture & Research Study Design)  
**IEEE Paper Mapping:** Section IV-C (*Keyed Dynamic CA State Engine*) & Section V (*Empirical Nonlinearity, SAC, and Parameter Optimization Study*)  
**Document Status:** REVISED RESEARCH ARCHITECTURE SPECIFICATION & CANDIDATE ALGORITHM STUDY FRAMEWORK  

---

## 1. Executive Summary & Purpose

`crypto/engine/dynamic_ca.py` defines the novel core research contribution of the KDR-CA-AEAD framework: a **Keyed Dynamically-Reconfigured 1D Elementary Cellular Automata (ECA) Permutation-Substitution Engine**.

Unlike standard block ciphers or static substitution boxes (S-Boxes), the Dynamic CA Engine injects key-dependent non-linear state transformations prior to stream cipher encryption. It combines Wolfram 1D Elementary Cellular Automata evolutions with a 3-step reversible algebraic transformation pipeline.

> **CRITICAL RESEARCH DIRECTIVE**: To ensure IEEE-grade scientific rigor, architectural parameters (dual-rule coupling offset $\Delta$, transformation pipeline step ordering, ECA generation count $G$, and rule table capacity $M$) are treated as **hypothesized research variables** to be empirically evaluated across candidate architectures in **Phase 2.1A**, rather than frozen arbitrarily.

---

## 2. Research Hypotheses ($H_1 \dots H_4$)

To satisfy formal cryptographic peer-review standards, Phase 2.1 establishes four testable scientific hypotheses:

### Hypothesis $H_1$ (Dual-Rule Coupling vs. Single-Rule Coupling)
* **Statement**: Coupling a primary rule $R_1$ with a secondary rule $R_2$ via prime offset index $\Delta$ eliminates periodic rule alignment artifacts and yields higher non-linearity and strict avalanche propagation than single-rule application ($R_1 = R_2$).

### Hypothesis $H_2$ (Algebraic Step Pipeline Ordering)
* **Statement**: Pipeline ordering $P \to \text{Modulo Addition} \to \text{Bit Rotation} \to \text{XOR}$ (Candidate A) achieves higher non-linear state confusion and differential uniformity than alternative orderings (Candidate B: Rotation $\to$ Modulo $\to$ XOR; Candidate C: XOR $\to$ Rotation $\to$ Modulo).

### Hypothesis $H_3$ (Prime Offset Index Distribution)
* **Statement**: Selecting prime offsets $\Delta \in \{3, 5, 7, 11, 13, 17, 19, 23, 29, 31\}$ decorrelates rule table access patterns significantly better than sequential ($\Delta = 1$) or non-prime offsets, minimizing cross-block auto-correlation in payload streams.

### Hypothesis $H_4$ (ECA Generation Count $G$ and Rule Table Capacity $M$)
* **Statement**: Single-generation evolution ($G = 1$) over an 8-bit periodic boundary provides optimal byte non-linearity per CPU cycle without memory overhead, and $M = 32$ rule table capacity provides exact 256-bit entropy alignment with SHA-256 HKDF outputs.

---

## 3. Position inside Cryptographic Pipeline

```
[ Master Key (BytesLike) ] + [ Salt (16B) ] + [ Nonce (12B) ]
                                    │
                                    ▼
                         [ KeySchedule Engine ]
                        (crypto/engine/key_schedule.py)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │ (K_r / rule_table)       │ (K_c)                    │ (K_a)
         ▼                          │                          │
[ Plaintext Payload (P) ]           │                          │
         │                          │                          │
         ▼                          │                          │
[ Dynamic CA Engine ] ──────────────┘                          │
(crypto/engine/dynamic_ca.py)                                  │
         │                                                     │
         ▼ (Transformed State T)                               │
[ Stream XOR Cipher ] ─────────────────────────────────────────┤
(encrypt.py / decrypt.py)                                      │
         │                                                     │
         ▼ (Ciphertext C)                                      │
[ HMAC-SHA256 AEAD Tag ] ──────────────────────────────────────┘
(authentication.py)
```

---

## 4. Module Responsibilities & Explicit Boundaries

### Responsibilities (What the Module SHALL Do):
1. **Bijective Transformation**: SHALL execute 100% loss-free, reversible forward and inverse state transformations on byte streams.
2. **Keyed Rule Evaluation**: SHALL evaluate 1D 8-bit periodic Wolfram Elementary Cellular Automata (ECA) rules ($0 \dots 255$) dynamically per payload byte.
3. **Parametric Dual-Rule Coupling**: SHALL derive secondary coupled rules using configurable offset parameter $\Delta$.
4. **Reversible Step Pipeline**: SHALL execute a 3-step algebraic pipeline configured by candidate architecture selection.
5. **Arbitrary Length Support**: SHALL process payloads of any byte length ($0 \dots N$ bytes) deterministically.

### Non-Responsibilities (What the Module SHALL NOT Do):
1. **SHALL NOT** generate, derive, or manipulate cryptographic keys (handled by `key_schedule.py`).
2. **SHALL NOT** generate keystream bytes or execute CTR-mode XOR encryption (handled by `encrypt.py`).
3. **SHALL NOT** compute or verify HMAC authentication tags (handled by `authentication.py`).
4. **SHALL NOT** introduce non-deterministic or unseeded randomness.
5. **SHALL NOT** maintain mutable persistent state across transformation calls.

---

## 5. Candidate Architecture Formulations (Phase 2.1A Study)

To determine the optimal transformation pipeline order, Phase 2.1A formulates three candidate architectures:

### Candidate Architecture A (Modulo Addition $\to$ Rotation $\to$ XOR)
$$\text{Forward: } y_1 = (p_i + S_{\text{ECA}}) \bmod 256, \quad y_2 = \text{ROTR}_8(y_1, k_{\text{shift}}), \quad t_i = y_2 \oplus R_2$$
$$\text{Inverse: } y_2 = t_i \oplus R_2, \quad y_1 = \text{ROTL}_8(y_2, k_{\text{shift}}), \quad p_i = (y_1 - S_{\text{ECA}}) \bmod 256$$

### Candidate Architecture B (Rotation $\to$ Modulo Addition $\to$ XOR)
$$\text{Forward: } y_1 = \text{ROTR}_8(p_i, k_{\text{shift}}), \quad y_2 = (y_1 + S_{\text{ECA}}) \bmod 256, \quad t_i = y_2 \oplus R_2$$
$$\text{Inverse: } y_2 = t_i \oplus R_2, \quad y_1 = (y_2 - S_{\text{ECA}}) \bmod 256, \quad p_i = \text{ROTL}_8(y_1, k_{\text{shift}})$$

### Candidate Architecture C (XOR $\to$ Rotation $\to$ Modulo Addition)
$$\text{Forward: } y_1 = p_i \oplus R_2, \quad y_2 = \text{ROTR}_8(y_1, k_{\text{shift}}), \quad t_i = (y_2 + S_{\text{ECA}}) \bmod 256$$
$$\text{Inverse: } y_2 = (t_i - S_{\text{ECA}}) \bmod 256, \quad y_1 = \text{ROTL}_8(y_2, k_{\text{shift}}), \quad p_i = y_1 \oplus R_2$$

---

## 6. Parameter Optimization Design Matrix

Phase 2.1A evaluates candidate parameters against empirical cryptanalytic metrics:

| Parameter | Studied Values / Range | Selection Criteria / Metric |
| :--- | :---: | :--- |
| **Pipeline Candidate** | `Candidate A`, `Candidate B`, `Candidate C` | Strict Avalanche Criterion (SAC), Non-linearity |
| **Offset Parameter ($\Delta$)** | `1, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31` | Cross-block Auto-correlation & NPCR / UACI |
| **Rule Table Capacity ($M$)** | `16, 32, 64, 128` | Entropy per Byte vs. Throughput (MB/s) |
| **ECA Generation Count ($G$)** | `1, 2, 4, 8` | S-Box Substitution Profile vs. Latency |

---

## 7. Precise Cryptographic & Implementation Terminology

1. **Non-linearity & Cryptanalysis**:
   - *Revised Wording*: "Intended to increase non-linearity and state confusion. The effectiveness and diffusion properties will be evaluated empirically in Phase 2.1A/2.1B using NIST SP 800-22 randomness batteries and avalanche criteria."
2. **Timing Side-Channel Resistance**:
   - *Revised Wording*: "No secret-dependent branching. No secret-dependent lookup tables. Implementation designed to minimize timing variability in Python execution."

---

## 8. Revised Multi-Phase Roadmap for Phase 2

```
Phase 2.1 Architecture & Research Specification (This Document)
        │
        ▼
Phase 2.1A Candidate Architecture Study & Experimental Evaluation
        │ (Benchmark Candidates A, B, C; Offsets Δ; Generations G)
        ▼
Phase 2.1B Parameter Optimization & Empirical Selection Report
        │ (Freeze winning candidate & parameter values)
        ▼
Phase 2.1C Final Architecture Freeze & ARB Sign-Off
        │
        ▼
Phase 2.2 Production Engine Implementation (crypto/engine/dynamic_ca.py)
        │
        ▼
Phase 2.3 Unit Testing & Validation (tests/unit/test_dynamic_ca.py)
```

---

## 9. Acceptance Criteria & Definition of Done

- [x] All 10 supervisor review points addressed.
- [x] Formal research hypotheses $H_1 \dots H_4$ formulated.
- [x] Candidate Architectures A, B, and C formally defined.
- [x] Configurable parameter matrix ($\Delta, M, G$) specified.
- [x] Scientific terminology updated (non-linearity, timing variability).
- [x] Revised Phase 2.1A / 2.1B roadmap incorporated.
- [x] Ready for Phase 2.1A Experimental Evaluation.
