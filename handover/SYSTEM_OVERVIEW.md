# KDR-CA-AEAD Cryptographic System Architecture

**Framework Version:** v1.0.0  

---

## Architectural Breakdown

### 1. Key Expansion & Domain Separation (HKDF-SHA256)
- Derives 256-bit rule mutation keys ($K_r$), 256-bit keystream keys ($K_c$), and 256-bit MAC authentication keys ($K_a$) using HKDF-SHA256 (RFC 5869 / NIST SP 800-56C).

### 2. Keyed Dynamically-Reconfigured 1D Cellular Automata (K-DCA)
- Utilizes reversible Wolfram CA rule permutations mutated dynamically per 64-byte block based on HKDF rule schedule $K_r$.

### 3. Encrypt-then-MAC AEAD Payload Formatting
- Payload layout: `[Salt (16B) || Nonce (12B) || Ciphertext (N B) || Tag (32B)]`.
- Tag verification uses constant-time `hmac.compare_digest()` to prevent timing side-channel attacks.
