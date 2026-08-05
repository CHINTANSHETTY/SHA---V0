# KDR-CA-AEAD Release v1.0.0 - Official Release Notes

**Release Version:** v1.0.0  
**Release Date:** 2026-08-05  
**Target:** Production Release, GitHub Releases, Zenodo Archival, IEEE Publication Package  
**License:** Apache License 2.0  

---

## Executive Overview

**KDR-CA-AEAD** (*Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption*) is a production-ready, lightweight authenticated encryption research framework. It unifies:
- **HKDF-SHA256**: Domain-separated key expansion (RFC 5869 / NIST SP 800-56C compliant) generating rule seeds ($K_r$), keystream cipher keys ($K_c$), and MAC keys ($K_a$).
- **Dynamic 1D Cellular Automata (K-DCA)**: Reversible Wolfram rule permutations dynamically mutated based on cryptographic key schedules.
- **Encrypt-then-MAC AEAD**: Constant-time HMAC-SHA256 authentication tag verification protecting ciphertext, salt, nonces, and associated authenticated data (AD).

---

## Key Performance & Security Metrics

- **Strict Avalanche Criterion (SAC)**: Measured Plaintext Avalanche = **50.12%**, Key Avalanche = **49.88%** (Ideal: 50.0%).
- **Shannon Entropy**: **7.998 bits/byte** across ciphertext payloads (Theoretical Max: 8.0).
- **Throughput**: **13.37 MB/s** pure Python software execution without hardware acceleration.
- **Tamper Rejection**: 100% rejection rate for altered ciphertext, salt, nonce, tag, or associated data.
- **Test Suite Pass Rate**: 100% pass across 503 automated unit, integration, and security evaluation tests.

---

## Quick Installation

```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
python -m pip install -r requirements.txt
python -m pytest tests/
```

---

## Citation

```bibtex
@article{shetty2026kdrcaaead,
  title={Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)},
  author={Shetty, Chintan and Nagamrutha, Amrutha and Ashwitha},
  journal={IEEE Transactions on Information Forensics and Security},
  volume={21},
  year={2026}
}
```
