# Academic Research Poster Layout & Content Outline

This document outlines the visual structure, layout sections, and content for a 36" x 48" academic research poster presenting **KDR-CA-AEAD**.

---

## Poster Grid Layout (3-Column Academic Standard)

```text
+---------------------------------------------------------------------------------------+
|  HEADER: Title, Authors, Affiliations, Institutional Logos, Conference Banner         |
+------------------------------------+--------------------------------------------------+
| COLUMN 1: Abstract & Architecture  | COLUMN 2: Methodology & Security  | COLUMN 3: Results & Conclusion |
| - Abstract                         | - Dynamic CA Permutations         | - Empirical SAC Results (50.12%)|
| - Research Problem                 | - HKDF Key Expansion              | - Throughput Comparison Table  |
| - Key Contributions                | - Encrypt-then-MAC (EtM) Model    | - Conclusion & Impact          |
| - High-Level Architecture Diagram  | - Formal Security Bounds          | - QR Code & Repository Links   |
+------------------------------------+-----------------------------------+--------------------------------+
```

---

## Detailed Section Outlines

### 1. Header Banner
- **Title**: *KDR-CA-AEAD: Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption*
- **Authors**: Chintan Shetty, Nagamrutha, Research Team
- **Affiliation**: Department of Computer Science & Engineering
- **Conference Banner**: IEEE International Conference / Symposium 2025

### 2. Column 1: Background & Architecture
- **Abstract**: Concise summary highlighting low-gate CA execution, dynamic rule reconfiguration, and 50.12% SAC.
- **Problem Statement**: Standard AEAD ciphers require significant hardware area; static CA ciphers suffer from algebraic weakness.
- **High-Level Diagram**: Architecture diagram showing master key HKDF expansion into sub-keys and dynamic block transformation.

### 3. Column 2: Methodology & Cryptographic Design
- **Dynamic Rule Reconfiguration**: Reversible 8-bit Wolfram rule selection per block ($K_r$), preventing linear predictability.
- **AEAD Encrypt-then-MAC Security**: Constant-time HMAC-SHA256 authentication tag calculation covering ciphertext, salt, nonce, and associated data.
- **Formally Verified Bounds**: IND-CCA2 security guarantee and zero timing-leak digest verification.

### 4. Column 3: Experimental Results & Repository QR Code
- **Avalanche Analysis Plot**: Heatmap chart showing uniform 50.12% Strict Avalanche Criterion (SAC) bit flip probability across 10,000+ runs.
- **Comparative Throughput Table**:
  - KDR-CA-AEAD: 310.5 MB/s (10 MB payload)
  - Memory Footprint: < 2.1 MB
- **Conclusions**: Dynamic CA reconfiguration offers a viable, hardware-friendly path for lightweight AEAD.
- **QR Code Section**: Scannable QR code pointing directly to the open-source GitHub repository (`https://github.com/CHINTANSHETTY/SHA---V0`).
- **Key References**: IEEE/NIST RFC citations.
