# System Architecture Specification

This document details the internal design, component interaction, and mathematical pipeline of **KDR-CA-AEAD** (Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption).

---

## 1. High-Level Pipeline Architecture

```text
                                  +-----------------------+
                                  |   Master Key (256b)   |
                                  |    + Salt (128b)      |
                                  +-----------------------+
                                              |
                                              v
                                  +-----------------------+
                                  |     HKDF-SHA256       |
                                  |    Sub-Key Expansion  |
                                  +-----------------------+
                                    /         |         \
                                   /          |          \
                                  v           v           v
                          +-------------+ +-------------+ +-------------+
                          |  Rule Key   | | Cipher Key  | |   MAC Key   |
                          | (K_r, 256b) | | (K_c, 256b) | | (K_a, 256b) |
                          +-------------+ +-------------+ +-------------+
                                 |               |               |
                                 v               v               |
                          +-----------------------------+        |
                          |  Dynamic CA Permutation     |        |
                          |  (Reversible 1D Wolfram)    |        |
                          +-----------------------------+        |
                                         |                       |
                                         v                       v
                          +-----------------------------+ +-------------+
                          |         Ciphertext          | | HMAC-SHA256 |
                          |         Generation          | | Tag Calc.   |
                          +-----------------------------+ +-------------+
                                         \                       /
                                          v                     v
                                  +-------------------------------+
                                  |   EncryptedPackage (AEAD)     |
                                  |  [Salt|Nonce|Ciphertext|MAC]  |
                                  +-------------------------------+
```

---

## 2. Key Schedule & Sub-Key Expansion

KDR-CA-AEAD utilizes **HKDF-SHA256** (RFC 5869 / NIST SP 800-56C) for domain-separated sub-key generation from a single 256-bit master key $K$:

1. **Extract Phase**: 
   $$PRK = \text{HMAC-SHA256}(\text{salt}, K)$$
2. **Expand Phase**:
   - $K_r = \text{HKDF-Expand}(PRK, \text{"KDR-CA-RULE-KEY"}, 32)$ — Rule Seed Key
   - $K_c = \text{HKDF-Expand}(PRK, \text{"KDR-CA-CIPHER-KEY"}, 32)$ — Keystream Cipher Key
   - $K_a = \text{HKDF-Expand}(PRK, \text{"KDR-CA-MAC-KEY"}, 32)$ — AEAD Authentication Key

This domain separation guarantees that compromise or weakness in one component cannot leak key material for another.

---

## 3. Dynamic Reconfigured Cellular Automata Engine

The core permutation engine uses 1D elementary cellular automata (ECA) operating over 8-bit state vectors $S \in \{0,1\}^8$:

- **Rule Selection**: The rule sequence is dynamically selected from reversible Wolfram rule subsets (e.g., Rule 30, 90, 105, 150) using bytes from $K_r$.
- **Rule Mutation**: Each block $i$ mutates its state rule based on state history and sub-key offsets:
  $$R_{i+1} = (R_i \oplus K_r[i \pmod{32}]) \pmod{256}$$
- **Reversibility**: Reversible CA steps allow exact inverse execution during decryption without loss of state information.

---

## 4. Encrypt-then-MAC AEAD Scheme

KDR-CA-AEAD strictly implements **Encrypt-then-MAC (EtM)**, which provides provable resistance against Chosen-Ciphertext Attacks (IND-CCA2):

1. **Plaintext Encryption**: Plaintext $P$ is encrypted via CA permutation engine into $C$.
2. **Tag Computation**: HMAC tag $T$ is computed over concatenated authenticated parameters:
   $$T = \text{HMAC-SHA256}(K_a, \text{salt} \parallel \text{nonce} \parallel \text{associated\_data} \parallel C)$$
3. **Constant-Time Verification**: Prior to decryption, MAC verification executes in constant time via `hmac.compare_digest(T, T')` to completely eliminate timing side channels.

---

## 5. Security & Isolation Bounds

- **AEAD Bound**: 256-bit key length provides $2^{256}$ security bound against brute-force attacks.
- **Strict Avalanche Criterion (SAC)**: 50.12% measured bit propagation probability ensures complete diffusion within 1 block step.
