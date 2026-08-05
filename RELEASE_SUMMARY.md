# KDR-CA-AEAD v1.0.0 Release Summary

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Release Version:** `v1.0.0`  
**Release Date:** August 5, 2026  
**License:** Apache License 2.0  
**Authors:** Chintan Shetty, Amrutha Nagamrutha, Ashwitha  

---

## Executive Overview

**KDR-CA-AEAD v1.0.0** is the official production-ready open-source release of the **Keyed Dynamically-Reconfigured Cellular Automata Authenticated Encryption** research framework.

This release represents the culmination of Phases 1 through 6, delivering a complete, lightweight, provably secure AEAD cipher scheme, a 500+ test validation suite, raw statistical randomness evaluation logs (NIST SP 800-22 and SAC evaluation), IEEE publication artifacts, open-science metadata manifests, and long-term repository governance policies.

---

## Key Features & Highlights

- **Dynamic Cellular Automata Engine**: Reversible 8-bit Wolfram rule permutations dynamically reconfigured via HKDF sub-key seeds per block execution.
- **Encrypt-then-MAC AEAD Security**: Constant-time HMAC-SHA256 authentication tag verification (`hmac.compare_digest`) protecting ciphertext, salt, nonce, and associated authenticated data (AD).
- **Domain-Separated Sub-Key Expansion**: RFC 5869 / NIST SP 800-56C compliant HKDF derivation of rule seeds ($K_r$), keystream cipher keys ($K_c$), and MAC keys ($K_a$).
- **Strict Avalanche Criterion (SAC)**: Empirical plaintext and key avalanche ratios evaluated against theoretical ideal bounds (50.0%) as documented in `docs/benchmark_guide.md`.
- **Open-Science Metadata Infrastructure**: Fully compliant `CITATION.cff` (v1.2.0) and `codemeta.json` (CodeMeta 2.0) files for Zenodo DOI registration and Software Heritage indexing.
- **Repository Governance Policies**: Formal BDFL governance model ([`GOVERNANCE.md`](GOVERNANCE.md)), 3-year LTS policy ([`MAINTENANCE.md`](MAINTENANCE.md)), Contributor Code of Conduct ([`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)), Support policy ([`SUPPORT.md`](SUPPORT.md)), and Security policy ([`SECURITY.md`](SECURITY.md)).

---

## System Architecture & Repository Layout

```text
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

## Empirical Benchmark Performance Overview

Benchmark performance and statistical randomness metrics are fully documented in the completed project documentation:
- **Benchmark & Avalanche Analysis**: Refer to [`docs/benchmark_guide.md`](docs/benchmark_guide.md) and [`evaluation_results/sac_matrix.json`](evaluation_results/sac_matrix.json).
- **NIST SP 800-22 Randomness Evaluation**: Refer to [`evaluation_results/nist_pvalues.json`](evaluation_results/nist_pvalues.json).
- **Throughput & Comparative Results**: Refer to [`results/tables/benchmark_summary.csv`](results/tables/benchmark_summary.csv).

---

## Quick Start & Usage

```powershell
# Clone repository & install requirements
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
pip install -r requirements.txt

# Run automated test suite (500+ tests)
$env:PYTHONPATH="."
python -m pytest

# Run master reproducibility & IEEE benchmark pipeline
python scripts/run_phase2_5_reproducibility.py
```

```python
from crypto import encrypt_bytes, decrypt_bytes

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

## Citation Information

If you use **KDR-CA-AEAD** in your research or software, please cite our project as follows:

```bibtex
@article{shetty2026kdrcaaead,
  title={Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)},
  author={Shetty, Chintan and Nagamrutha, Amrutha and Ashwitha},
  journal={IEEE Transactions on Information Forensics and Security},
  year={2026},
  publisher={IEEE}
}
```

---

## License & Support

- **License**: Distributed under the [Apache License 2.0](LICENSE).
- **Governance**: Governed by the [Governance Policy](GOVERNANCE.md) and [Maintenance Guide](MAINTENANCE.md).
- **Community**: Adheres to the [Code of Conduct](CODE_OF_CONDUCT.md) and [Support Policy](SUPPORT.md).
- **Security**: Confidential security reports managed under [SECURITY.md](SECURITY.md) (48-hour SLA).
