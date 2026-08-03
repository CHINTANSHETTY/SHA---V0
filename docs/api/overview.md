# KDR-CA-AEAD API Reference & Package Overview

**Package:** `crypto`  
**Version:** 1.0.0  
**IEEE Standard Mapping:** Section IV (Software Architecture & API Specifications)  

---

## Executive Overview

The `crypto` package implements the **Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)** cryptographic research framework.

It provides a unified, production-ready interface for authenticated encryption, non-linear Cellular Automata state permutations, HKDF-SHA256 key scheduling, constant-time HMAC-SHA256 authentication, and comprehensive security analysis and benchmarking.

---

## Package Structure & Module Mapping

```
crypto/
├── __init__.py           # Unified top-level public API exports
├── constants.py          # Protocol constants, version labels, buffer lengths
├── engine/
│   ├── encrypt.py        # High-level authenticated encryption (encrypt_bytes, encrypt_payload)
│   ├── decrypt.py        # High-level authenticated decryption (decrypt_bytes, decrypt_payload)
│   ├── key_schedule.py   # HKDF-SHA256 sub-key expansion & domain separation
│   └── dynamic_ca.py     # Candidate A-Chain Dynamic CA non-linear permutation engine
├── ca/
│   ├── engine.py         # 1D Wolfram Elementary Cellular Automata evolution engine
│   ├── rules.py          # Rule parsing, Wolfram 8-bit lookup table construction
│   ├── mapping.py        # Byte-to-CA bit sequence mapping utilities
│   └── utils.py          # Entropy, Hamming weight, and validation helpers
├── primitives/
│   ├── hkdf.py           # NIST SP 800-56C / RFC 5869 HKDF-SHA256 implementation
│   ├── hmac.py           # Constant-time HMAC-SHA256 authentication tag primitive
│   └── random.py         # CSPRNG salt & nonce generation wrappers
├── models/
│   ├── package.py        # EncryptedPackage dataclass model
│   └── exceptions.py     # CryptoError, KeyDerivationError, AuthenticationError
└── analysis/
    ├── security_analysis.py # Full statistical & security analysis suite
    ├── randomness.py        # NIST SP 800-22 randomness test suite (Monobit, Runs, Chi-Square)
    ├── statistics.py        # Avalanche, entropy, correlation, and cipher comparison
    ├── attack_analysis.py   # Brute-force, differential, linear, related-key resistance
    ├── benchmark_runner.py  # Benchmark suite (throughput, latency, memory, CPU)
    ├── benchmark_utils.py   # System metadata, high-precision timing, memory tracing
    ├── final_validation.py  # Master pipeline verification & IEEE CSV/MD table export
    └── visualization.py     # 300 DPI PNG & SVG camera-ready figure generation
```

---

## Top-Level Public API Usage

```python
from crypto import (
    encrypt_bytes,
    decrypt_bytes,
    encrypt_payload,
    decrypt_payload,
    EncryptedPackage,
    CryptoError,
    AuthenticationError
)

# 1. Binary Data AEAD Encryption
master_key = b"Nagamrutha_Research_Master_Key_32B"
payload = b"Healthcare EHR Critical Vitals: Patient ID=9901"
associated_data = b"Header: Hospital-ID=H-44"

# Encrypt
pkg = encrypt_bytes(payload, master_key, associated_data=associated_data)

# Decrypt
decrypted_payload = decrypt_bytes(pkg, master_key, associated_data=associated_data)
assert decrypted_payload == payload
```

---

## Exception Hierarchy

```
Exception
 └── CryptoError
      ├── KeyDerivationError
      └── AuthenticationError
```

- `CryptoError`: Base exception for invalid parameters, payload formatting errors, or buffer size mismatches.
- `KeyDerivationError`: Raised when key derivation parameters (master key length, salt, nonce) fail RFC 5869 / NIST requirements.
- `AuthenticationError`: Raised when constant-time HMAC-SHA256 tag verification fails due to ciphertext, nonce, tag, or associated data tampering.
