# Cryptographic Security Assumptions Specification (Phase 3.2 Task 8)

**Author:** Nagamrutha (Security Analysis & Cryptographic Validation Lead)  
**Algorithm:** KDR-CA-AEAD  
**Date:** August 2026  
**Status:** Completed & Documented  

---

## 1. Cryptographic Security Assumptions Taxonomy

The security proof and operational safety of the **KDR-CA-AEAD** algorithm rely on seven explicit foundational assumptions.

---

## 2. Detailed Assumptions Breakdown

### Assumption 1: Trusted Cryptographically Secure Pseudorandom Number Generator (CSPRNG)
- **Specification:** The underlying operating system provides an uncompromised, entropy-rich CSPRNG (e.g., Python `secrets` module, `os.urandom`, Linux `/dev/urandom`, Windows `BCryptGenRandom`).
- **Cryptographic Reliance:** Master key generation, 128-bit salts, and 96-bit nonces rely on uniform CSPRNG output distribution.
- **Risk if Broken:** Predictable salts or nonces expose the cipher to keystream reuse (two-time pad attacks) and precomputation rainbow table attacks.

### Assumption 2: Secure Key Generation & Entropy Standards
- **Specification:** Master keys $K$ are generated with at least 256 bits of true physical entropy or derived from user passphrases using high-work-factor Password-Based Key Derivation Functions (PBKDF2-HMAC-SHA256 with $\ge 600,000$ iterations or Argon2id).
- **Cryptographic Reliance:** Classical $2^{256}$ and Grover quantum $2^{128}$ brute-force search bounds assume full 256-bit entropy.
- **Risk if Broken:** Low-entropy passphrases allow dictionary or targeted offline brute-force attacks.

### Assumption 3: Secure Key Storage & Memory Handling
- **Specification:** Master keys and expanded sub-keys ($K_c, K_m, K_r$) are stored in protected process memory, secure hardware security modules (HSM), or secure enclaves, and are zeroized upon session termination.
- **Cryptographic Reliance:** Confidentiality and integrity guarantees hold only as long as the endpoints maintain key confidentiality.
- **Risk if Broken:** Endpoint memory dumps or unauthorized process reading compromise master keys.

### Assumption 4: Nonce Uniqueness & Lifecycle Management
- **Specification:** A unique 96-bit nonce $N$ is generated for every message encrypted under the same master key $K$. The number of messages encrypted under a single key does not exceed $2^{48}$ (NIST SP 800-38D bound).
- **Cryptographic Reliance:** Nonce uniqueness guarantees keystream freshness and prevents CTR mode reuse.
- **Risk if Broken:** Nonce reuse exposes plaintexts to XOR cancellation attacks ($C_1 \oplus C_2 = P_1 \oplus P_2$).

### Assumption 5: Constant-Time Side-Channel Execution
- **Specification:** The HMAC tag verification logic utilizes constant-time string comparison (`hmac.compare_digest`), taking uniform execution time regardless of byte match position.
- **Cryptographic Reliance:** Prevents timing oracle attacks during chosen-ciphertext queries.
- **Risk if Broken:** Variable-time comparison leaks tag bytes to network timing adversaries.

### Assumption 6: Hardness of Cryptographic Primitives
- **SHA-256 Pre-image & Collision Resistance:** Assuming SHA-256 is collision-resistant ($2^{128}$) and pre-image resistant ($2^{256}$).
- **HMAC-SHA256 PRF & SUF-CMA Hardness:** Assuming HMAC-SHA256 acts as a secure Pseudorandom Function (PRF) and achieves Strong Unforgeability under Chosen-Message Attack (SUF-CMA).
- **HKDF-SHA256 Extract-and-Expand Safety:** Assuming HKDF (RFC 5869) extracts independent, pseudorandom sub-keys ($K_c, K_m, K_r$).

### Assumption 7: Integrity-First Decryption Control Flow
- **Specification:** The decryption engine executes Encrypt-then-MAC tag verification *before* executing stream XOR or dynamic CA state inverse operations.
- **Cryptographic Reliance:** Ensures zero unauthenticated data processing.
- **Risk if Broken:** Processing unauthenticated ciphertext opens side-channels or CA state manipulation vulnerabilities.

---

## 3. Assumptions Verification Matrix

| Assumption | Primitive / Layer | Status | Automated Test Verification |
| :--- | :--- | :--- | :--- |
| **CSPRNG Entropy** | OS Kernel / Python `secrets` | **VERIFIED** | `test_nonce_uniqueness` |
| **Key Length (256-bit)** | KeySchedule / HKDF | **VERIFIED** | `test_key_space_analysis` |
| **Nonce Uniqueness (96-bit)**| Encrypt Engine | **VERIFIED** | `test_replay_protection_verification` |
| **Constant-Time HMAC** | Decrypt Engine | **VERIFIED** | `test_integrity_verification` |
| **HMAC-SHA256 PRF** | HKDF / Tag Engine | **VERIFIED** | `test_authenticity_verification` |
| **Integrity-First Control** | Decrypt Engine | **VERIFIED** | `test_chosen_ciphertext_attack` |
