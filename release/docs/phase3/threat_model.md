# KDR-CA-AEAD Threat Model & Attacker Capabilities Specification (Phase 3.2 Task 1 & 2)

**Author:** Nagamrutha (Security Analysis & Cryptographic Validation Lead)  
**Algorithm:** KDR-CA-AEAD  
**Date:** August 2026  
**Status:** Completed & Formally Modeled  

---

## 1. Overview & Security Objectives

This document defines the formal threat model for the **KDR-CA-AEAD** authenticated encryption algorithm. It specifies adversary taxonomy, explicit attacker capabilities, non-capabilities, protected assets, trust boundaries, and threat mitigation strategies.

### Core Security Objectives
1. **Confidentiality (IND-CPA & IND-CCA2):** Prevent adversaries from recovering plaintext or deriving key material from ciphertexts.
2. **Integrity (INT-CTXT):** Guarantee that any unauthorized modification to ciphertext or headers is detected and rejected.
3. **Message Origin Authenticity (SUF-CMA):** Ensure only valid master key holders can generate authentic payload packages.
4. **Replay Protection & Freshness:** Prevent adversaries from replaying past valid packages or forcing duplicate nonces.

---

## 2. Adversary Taxonomy (Threat Actors)

### ACTOR-01: Passive Eavesdropper
- **Profile:** Adversary monitoring public network links or inspecting persistent storage media.
- **Capabilities:**
  - Intercept all transmitted encrypted packages ($N \parallel S \parallel C \parallel T$).
  - Store unlimited historical ciphertexts for offline cryptanalysis.
  - Perform statistical analysis (entropy, byte distribution, avalanche tests).
- **Limits (Non-Capabilities):** Cannot read endpoint memory or master key; cannot invert SHA-256 or HKDF sub-keys.
- **Mitigation:** IND-CPA stream cipher encryption (HMAC CTR-PRNG + Keyed Dynamic CA permutation).

### ACTOR-02: Active Network Intermediary (Man-in-the-Middle)
- **Profile:** Adversary capable of intercepting, modifying, dropping, or injecting packets in transit.
- **Capabilities:**
  - Modify ciphertext bytes, salt, nonce, or protocol version fields.
  - Inject fake or forged encrypted packages.
  - Re-order or delay packet delivery.
- **Limits (Non-Capabilities):** Cannot forge valid 256-bit HMAC-SHA256 AEAD tags without master key; cannot bypass constant-time tag verification.
- **Mitigation:** Encrypt-then-MAC AEAD architecture (HMAC-SHA256 over $N \parallel S \parallel C$).

### ACTOR-03: Replay Attacker
- **Profile:** Adversary capturing valid transmitted packages and re-transmitting them to endpoints at a later time.
- **Capabilities:**
  - Intercept valid `EncryptedPackage` instances.
  - Re-send identical packages to the receiver.
  - Combine header fields (salts/nonces) from past sessions with new ciphertexts.
- **Limits (Non-Capabilities):** Cannot alter payload without failing AEAD tag verification; cannot force duplicate CSPRNG nonce generation.
- **Mitigation:** CSPRNG 96-bit unique nonces per message + HMAC tag binding.

### ACTOR-04: Ciphertext Modification & Malleability Attacker
- **Profile:** Adversary attempting chosen-ciphertext attacks (CCA / IND-CCA2) or bit-flipping to manipulate plaintext.
- **Capabilities:**
  - Construct arbitrarily modified ciphertexts (chosen-ciphertext queries).
  - Target specific byte offsets (flipping header bits or payload data).
  - Observe decryption oracle error responses.
- **Limits (Non-Capabilities):** Cannot decrypt unauthenticated payloads; cannot exploit timing side-channels due to `hmac.compare_digest`.
- **Mitigation:** IND-CCA2 compliance; 100% rejection of unauthenticated payloads prior to decryption.

### ACTOR-05: Compromised System Insider (Limited Privileges)
- **Profile:** Adversary with low-privilege access to local host operating system or storage layers.
- **Capabilities:**
  - Inspect serialized datastores and encrypted file artifacts.
  - Observe public API input/output parameters.
- **Limits (Non-Capabilities):** Cannot access master keys stored in secure key vaults or hardware modules; cannot invert HKDF sub-keys.
- **Mitigation:** HKDF-SHA256 sub-key isolation and secure key material memory handling.

---

## 3. Attacker Capabilities vs Non-Capabilities

| Attacker CAN Do | Attacker CANNOT Do |
| :--- | :--- |
| Sniff full encrypted network streams ($N \parallel S \parallel C \parallel T$) | Invert SHA-256 pre-images or compute HMAC tags without secret key ($2^{256}$) |
| Submit chosen-plaintext queries (CPA) up to $2^{64}$ bytes | Recover master key $K$ or sub-keys ($K_c, K_m, K_r$) from ciphertexts or keystream |
| Submit chosen-ciphertext queries (CCA) to decryption oracle | Predict CSPRNG random nonces (96-bit space, Birthday bound $\le 2^{-97}$) |
| Flip bits, truncate, or alter payload bytes & headers | Bypass constant-time `hmac.compare_digest` to perform timing oracle attacks |
| Replay historical packages or re-order transmission streams | Modify ciphertext or associated data without triggering 100% `AuthenticationError` |

---

## 4. Protected Assets & Trust Boundaries

```
┌────────────────────────────────────────────────────────────────────────┐
│                      TRUSTED ENDPOINT BOUNDARY                         │
│  [Master Key K] ──> [HKDF-SHA256] ──> Sub-Keys (Kc, Km, Kr)            │
│  [Plaintext P]  ──> [K-DCA + CTR-PRNG] ──> [Ciphertext C]              │
│  [Nonce N] + [Salt S] + [Ciphertext C] ──> [HMAC-SHA256] ──> [Tag T]   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Package: N || S || C || T)
===================================▼======================================
                     UN-TRUSTED NETWORK & STORAGE BOUNDARY
       (Threat Actors: Passive Eavesdropper, Active MitM, Replay)
==========================================================================
```

1. **Master Secret Key Material ($K$):** 256-bit secret key; protected via HKDF expansion & secure memory handling.
2. **Plaintext Payload Data ($P$):** Sensitive electronic health records (EHR); protected via K-DCA + HMAC CTR-PRNG.
3. **Ciphertext & Associated Data Integrity:** $N \parallel S \parallel C \parallel T$; protected via HMAC-SHA256 AEAD tag.
4. **Session Nonce Uniqueness ($N$):** 96-bit CSPRNG buffer; protected via OS CSPRNG kernel entropy.
