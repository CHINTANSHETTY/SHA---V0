# Educational Curriculum: Lecture Outline

This document outlines a 7-module academic lecture curriculum based on the **KDR-CA-AEAD** research framework, designed for undergraduate and graduate courses in Applied Cryptography, Cybersecurity, and Complex Systems.

---

## Course Overview & Prerequisites

- **Course Title**: Applied Lightweight Cryptography with Cellular Automata
- **Target Audience**: Upper-level Computer Science & Electrical Engineering Students.
- **Prerequisites**: Linear Algebra, Discrete Mathematics, Basic Python Programming, Introduction to Cryptography.

---

## Syllabus & Module Breakdown

### Module 1: Introduction to Cellular Automata (CA)
- Definition of Elementary Cellular Automata (ECA) and Wolfram rules.
- 1D state transition functions, neighborhood topologies ($k=3$), and rule tables.
- Reversibility properties in 8-bit block state spaces.
- Historical cryptographic uses of Rule 30/Rule 90 and past algebraic vulnerabilities.

### Module 2: Modern Authenticated Encryption (AEAD) Concepts
- Confidentiality vs. Integrity vs. Authenticity.
- AEAD paradigms: Encrypt-and-MAC, MAC-then-Encrypt, and **Encrypt-then-MAC (EtM)**.
- Associated Authenticated Data (AD) binding and nonce misuse resistance.
- IND-CCA2 security definition and INT-CTXT bounds.

### Module 3: Dynamic Reconfiguration Engine Design
- Limitations of static rule ciphers.
- Deriving key-dependent Wolfram rule sequences per block using key state derivation.
- HKDF-SHA256 (RFC 5869 / NIST SP 800-56C) domain separation ($K_r, K_c, K_a$).
- Eliminating fixed periodicity in CA state trajectories.

### Module 4: Security Analysis & Threat Modeling
- Side-channel attack surface and constant-time programming principles.
- Timing attack prevention in MAC tag verification (`hmac.compare_digest`).
- Statistical randomness testing: NIST SP 800-22 suite overview.
- Cryptanalysis resistance: Linear, differential, and algebraic cryptanalysis.

### Module 5: Performance & Avalanche Analysis
- The Strict Avalanche Criterion (SAC): Mathematical formulation and ideal 50% target.
- Bit Independence Criterion (BIC).
- Measuring execution latency, memory footprint, and throughput across variable message sizes.
- Hardware gate equivalence ($GE$) estimation for ASIC targets.

### Module 6: Benchmarking & Comparative Cryptography
- Benchmarking methodology: Warm-up runs, CPU isolation, clock cycle counting.
- Comparing KDR-CA-AEAD with NIST standards (AES-128-GCM, ChaCha20-Poly1305).
- Hardware vs. Software trade-offs in resource-constrained IoT environments.

### Module 7: Case Study & Hands-on Implementation
- Review of the KDR-CA-AEAD codebase architecture (`crypto/`, `tests/`, `benchmarks/`).
- Deploying the Flask Web GUI (`app.py`) for live encryption inspection.
- Building custom evaluation pipelines and interpreting benchmark charts.
