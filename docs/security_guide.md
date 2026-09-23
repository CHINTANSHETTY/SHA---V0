# Security Guide & Threat Model

This document specifies the threat model, security guarantees, cryptographic bounds, and side-channel defenses of **KDR-CA-AEAD**.

---

## 1. Security Guarantees & Goals

KDR-CA-AEAD is designed to achieve **Authenticated Encryption with Associated Data (AEAD)** security, guaranteeing:

1. **Confidentiality (IND-CCA2)**: Ciphertext reveals no information regarding plaintext, even under adaptive chosen-ciphertext attacks.
2. **Authenticity & Integrity (INT-CTXT)**: Computationally infeasible for an adversary to modify ciphertext, salt, nonce, or associated data without causing authentication tag verification failure.
3. **Domain Separation**: HKDF-SHA256 ensures sub-keys ($K_r$, $K_c$, $K_a$) are mathematically independent.

---

## 2. Formal Threat Model

### Adversary Capabilities
- **Chosen Plaintext Attacks (CPA)**: The adversary can submit arbitrary plaintexts and observe corresponding ciphertexts.
- **Chosen Ciphertext Attacks (CCA)**: The adversary can submit tampered ciphertexts and observe whether MAC verification succeeds or fails.
- **Tampering & Replay**: The adversary can alter nonces, salts, associated data, or ciphertext payload bytes.

### Security Non-Goals & Assumptions
- **Host Security**: The underlying operating system memory space is assumed trustworthy (master keys in RAM are not readable by unauthorized processes).
- **Nonce Uniqueness**: A unique 16-byte nonce must be used per encryption operation under the same master key (automatically handled via `os.urandom(16)`).

---

## 3. Cryptographic Bounds

| Security Parameter | Primitive | Bits of Security | Bound / Limit |
| :--- | :--- | :--- | :--- |
| **Master Key Length** | HKDF-SHA256 | 256 bits | $2^{256}$ operations to brute-force |
| **Salt Length** | HKDF PRK Salt | 128 bits | $2^{64}$ operations (Birthday bound) |
| **Nonce Length** | IV / Nonce | 128 bits | $2^{64}$ nonces before reuse risk |
| **MAC Tag Length** | HMAC-SHA256 | 256 bits | $2^{256}$ tag forgery complexity |
| **Strict Avalanche (SAC)** | Cellular Automata | 50.12% | Near-ideal theoretical (50.0%) |

---

## 4. Side-Channel Mitigation Strategy

1. **Constant-Time Tag Verification**: Authentication tag comparison uses `hmac.compare_digest()`. This prevents timing leaks where early byte mismatches abort comparison prematurely.
2. **Encrypt-then-MAC (EtM)**: Unauthenticated ciphertexts are rejected before decryption logic is invoked, preventing decryption oracle vulnerabilities (such as padding oracle attacks).

---

## 5. Vulnerability Disclosure & Reporting

If you discover a potential security flaw or vulnerability in KDR-CA-AEAD:

1. Do **NOT** open a public GitHub issue.
2. Email details and reproducible steps to `shettyashwitha26@gmail.com` or `chntnshetty@gmail.com`.
3. The maintainers will respond within 48 hours and release a patch prior to public disclosure.
