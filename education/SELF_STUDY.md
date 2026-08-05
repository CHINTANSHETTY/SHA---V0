# Self-Study Roadmap & Reference Guide

This document provides a structured learning path, recommended textbooks, seminal research papers, and self-study exercises for students and researchers exploring cellular automata cryptography and AEAD designs.

---

## 1. Learning Roadmap

```text
[Phase 1: Foundations]
   └── Wolfram Rules & 1D Elementary Cellular Automata
   └── Symmetric Cipher Models & Stream Ciphers

[Phase 2: Modern AEAD Security]
   └── HKDF (RFC 5869) Key Derivation & Domain Separation
   └── Encrypt-then-MAC (EtM) vs. GCM / CCM Authenticated Encryption

[Phase 3: Advanced Cryptanalysis & Implementation]
   └── Strict Avalanche Criterion (SAC) & Cryptographic Randomness
   └── Constant-Time Programming & Timing Side-Channel Defense
```

---

## 2. Key Recommended Textbooks

1. **A New Kind of Science** by Stephen Wolfram (Wolfram Media, 2002).
   - *Key Focus*: Cellular automata rules, complex systems, reversibility, Rule 30.
2. **Applied Cryptography** by Bruce Schneier (John Wiley & Sons, 2nd ed., 1996).
   - *Key Focus*: Stream ciphers, key schedules, pseudo-random sequence generators.
3. **Introduction to Modern Cryptography** by Jonathan Katz and Yehuda Lindell (CRC Press, 3rd ed., 2020).
   - *Key Focus*: Formal security definitions (IND-CPA, IND-CCA2, INT-CTXT), authenticated encryption.

---

## 3. Essential Research Papers

1. S. Wolfram, *"Cryptography with Cellular Automata,"* in *Advances in Cryptology – CRYPTO '85*, Springer, 1985.
2. H. Krawczyk, *"HMAC: Keyed-Hashing for Message Authentication,"* RFC 2104, 1997.
3. H. Krawczyk and P. Eronen, *"HMAC-based Extract-and-Expand Key Derivation Function (HKDF),"* RFC 5869, 2010.
4. M. Bellare and C. Namprempre, *"Authenticated Encryption: Relations among Notions and Analysis of the Generic Composition Paradigms,"* *Journal of Cryptology*, vol. 21, no. 4, 2008.

---

## 4. Self-Study Practice Questions

1. Why are static elementary cellular automata (e.g., static Rule 30 stream generators) susceptible to algebraic and state-reconstruction cryptanalysis?
2. How does dynamic per-block rule selection driven by HKDF sub-keys eliminate predictable state transition cycles?
3. What is the fundamental security advantage of Encrypt-then-MAC (EtM) over Encrypt-and-MAC or MAC-then-Encrypt?
4. Explain why constant-time comparison algorithms (`hmac.compare_digest`) are essential for preventing timing side-channel attacks during authentication tag verification.
