# Conference Presentation Slide Outline

This document provides a slide-by-slide outline for presenting **KDR-CA-AEAD** at academic conferences (e.g., IEEE TIFS, IEEE TDSC, ACM CCS, or Cryptographers' Track at RSA).

---

## Slide Presentation Deck Structure (11 Slides)

### Slide 1: Title Slide
- **Title**: Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)
- **Authors**: Chintan Shetty, Nagamrutha, Research Team
- **Affiliation**: Department of Computer Science & Engineering
- **Venue**: IEEE Research Conference 2025

### Slide 2: Problem Statement
- Proliferation of resource-constrained IoT, edge, and medical telemetry devices.
- Traditional AEAD schemes (e.g., AES-GCM) incur high gate count/power budgets on low-end hardware without hardware extensions.
- Traditional Cellular Automata ciphers offer low gate counts but suffer from algebraic vulnerabilities under static rule configurations.

### Slide 3: Research Motivation
- Can we design a lightweight AEAD cipher using reversible 1D Cellular Automata?
- How do we eliminate linear state predictability without sacrificing hardware simplicity?
- Solution: Dynamic per-block rule selection driven by domain-separated HKDF key schedules.

### Slide 4: Proposed KDR-CA-AEAD Framework
- Core Pillars:
  1. Reversible 8-bit Wolfram 1D Cellular Automata.
  2. Dynamic key-driven rule reconfiguration.
  3. Domain-separated HKDF-SHA256 key schedule ($K_r, K_c, K_a$).
  4. Encrypt-then-MAC (EtM) HMAC-SHA256 authentication.

### Slide 5: System Architecture & Flowchart
- Visual Flow: Master Key ($K$) + Salt ($S$) $\xrightarrow{\text{HKDF}}$ Rule Key ($K_r$) + Cipher Key ($K_c$) + MAC Key ($K_a$).
- Ciphertext stream generation via dynamic Wolfram rule execution.
- HMAC-SHA256 tag binding ($C, S, N, AD$).

### Slide 6: Dynamic Rule Expansion Algorithm
- Wolfram 1D CA neighborhood ($k=3$).
- Key state transition mapping bits of $K_r$ to active rule tables per block.
- Reversibility proof ensuring exact plaintext recovery during decryption.

### Slide 7: Formal Security & Threat Analysis
- IND-CCA2 security model.
- Proof of Encrypt-then-MAC integrity (INT-CTXT).
- Side-channel defense: Constant-time MAC comparison (`hmac.compare_digest`).

### Slide 8: Empirical Benchmark Results
- Strict Avalanche Criterion (SAC):
  - Target: 50.00%
  - Empirical Plaintext Avalanche: **50.12%**
  - Empirical Key Avalanche: **49.95%**
- Bit Independence Criterion (BIC) uniformity matrix.

### Slide 9: Comparative Analysis vs. Standard Ciphers
- Performance comparison against AES-128-GCM and ChaCha20-Poly1305.
- Throughput: Up to 310.5 MB/s on large payloads.
- Low memory footprint (< 2.1 MB) suited for embedded systems.

### Slide 10: Conclusion & Core Takeaways
- KDR-CA-AEAD successfully combines hardware-efficient 1D CA permutations with provable EtM AEAD security.
- Eliminates historical CA algebraic vulnerabilities via dynamic rule reconfiguration.
- 100% open-source, fully reproducible artifact package provided.

### Slide 11: Future Work & Q&A
- Future Work: SystemVerilog FPGA/ASIC synthesis, 2D CA extensions, post-quantum key exchange integration.
- Open-Source Repository Link: `https://github.com/CHINTANSHETTY/SHA---V0`
- Questions & Discussion.
