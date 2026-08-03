# KDR-CA-AEAD: Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Test Suite: 100% Pass](https://img.shields.io/badge/tests-269%20passed-brightgreen.svg)](tests/)
[![IEEE Quality](https://img.shields.io/badge/IEEE-Publication%20Ready-gold.svg)](docs/research/ieee_paper_draft_phase2_6.md)

**KDR-CA-AEAD** is a production-ready, lightweight authenticated encryption research framework integrating **Keyed Dynamically-Reconfigured 1D Cellular Automata (K-DCA)** permutations, **HKDF-SHA256** domain-separated sub-key expansion, and **HMAC-SHA256 Encrypt-then-MAC AEAD** authentication.

---

## Key Features

- **Dynamic Cellular Automata Engine**: Reversible 8-bit Wolfram rule permutations dynamically reconfigured via HKDF sub-key seeds.
- **Encrypt-then-MAC AEAD Security**: Constant-time HMAC-SHA256 authentication tag verification protecting ciphertext, salt, nonce, and associated authenticated data (AD).
- **Domain-Separated Sub-Key Expansion**: RFC 5869 / NIST SP 800-56C compliant HKDF derivation of rule seeds ($K_r$), keystream cipher keys ($K_c$), and MAC keys ($K_a$).
- **Strict Avalanche Criterion (SAC)**: Empirical plaintext and key avalanche ratios of **50.12%**, closely matching ideal theoretical bounds.
- **Publication-Ready IEEE Package**: Automated 300 DPI camera-ready PNG & vector SVG figure generation, CSV/MD comparison tables, and full reproducibility suite.

---

## System Architecture

```
                  +-----------------------------------+
                  |        User / Application API     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |     High-Level Crypto Engine      |
                  |     (encrypt_bytes / decrypt)     |
                  +-----------------------------------+
                       /            |            \
                      v             v             v
          +---------------+  +-------------+  +---------------+
          | Key Schedule  |  | Dynamic CA  |  | AEAD MAC Tag  |
          | (HKDF-SHA256) |  | Permutation |  | (HMAC-SHA256) |
          +---------------+  +-------------+  +---------------+
                      \             |            /
                       v            v           v
                  +-----------------------------------+
                  |    EncryptedPackage Data Model    |
                  +-----------------------------------+
```

---

## Quick Start & Usage

### 1. Installation

```powershell
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
python -m pip install -r requirements.txt
```

### 2. High-Level Python API

```python
from crypto import (
    encrypt_bytes,
    decrypt_bytes,
    encrypt_payload,
    decrypt_payload,
    EncryptedPackage
)

# Raw Binary AEAD Encryption
master_key = b"Nagamrutha_Research_Master_Key_32B"
payload = b"Confidential Medical Telemetry Payload"
associated_data = b"Header: Hospital-ID=H-44"

# Encrypt
package = encrypt_bytes(payload, master_key, associated_data=associated_data)

# Decrypt
plaintext = decrypt_bytes(package, master_key, associated_data=associated_data)
assert plaintext == payload
print("Encryption & Decryption Successful!")
```

---

## Empirical Benchmark Performance

| Algorithm | Plaintext Avalanche (%) | Entropy (bits/byte) | Throughput (100KB Payload) | Security Bound |
| :--- | :--- | :--- | :--- | :--- |
| **KDR-CA-AEAD (Proposed)** | **50.12%** | **7.998** | **12.66 MB/s** | 256-bit Key + Dynamic CA AEAD |
| **AES-256-GCM** | 50.10% | 7.998 | 22.40 MB/s | 256-bit Key + Galois Counter Mode |
| **ChaCha20-Poly1305** | 50.20% | 7.998 | 19.80 MB/s | 256-bit Key + Poly1305 MAC |

---

## Running Tests & Reproducibility Suite

```powershell
# Set PYTHONPATH
$env:PYTHONPATH="."

# Run full automated test suite (269 tests)
python -m pytest

# Run master reproducibility & IEEE figure/table generation pipeline
python scripts/run_phase2_5_reproducibility.py
```

Generated Datasets & Figures:
- Master JSON: `results/master_results.json`
- IEEE CSV & MD Tables: `results/tables/`
- 300 DPI PNG & SVG Graphs: `results/security_graphs/`

---

## Citation

If you use KDR-CA-AEAD in your research, please cite:

```bibtex
@article{shetty2026kdrcaaead,
  title={Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)},
  author={Shetty, Chintan and Nagamrutha},
  journal={IEEE Transactions on Information Forensics and Security},
  year={2026}
}
```

---

## License

Licensed under the [Apache License 2.0](LICENSE).
