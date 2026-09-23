# THREAT MODEL & SECURITY ASSUMPTIONS SPECIFICATION

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Document Target:** `docs/research/threat_model.md`  
**IEEE Paper Mapping:** Section III (*Threat Model, Security Goals & Adversary Capabilities*)  
**Status:** ✅ **FROZEN RESEARCH SPECIFICATION**  

---

## 1. Asset Classification & Protection Targets

The primary objective of KDR-CA-AEAD is to protect high-sensitivity Electronic Health Records (EHR), personal health data, and structured payload fields during network transmission and storage.

- **Confidentiality Asset ($P$)**: Plaintext health payloads (patient IDs, diagnoses, vitals, prescriptions).
- **Integrity & Authenticity Asset ($T$)**: HMAC-SHA256 authentication tag verifying payload origin and prohibiting unauthorized modification.
- **Keying Material Asset ($K$)**: Master key / password, 32-byte rule key ($K_r$), 32-byte cipher key ($K_c$), and 32-byte MAC key ($K_a$).

---

## 2. Adversary Model & Capabilities (Dolev-Yao / IND-CCA2)

We evaluate security under the standard **Dolev-Yao Network Adversary Model** and **IND-CCA2 (Indistinguishability under Chosen-Ciphertext Attack)** security framework:

### Adversary Capabilities:
1. **Full Network Control**: The adversary $\mathcal{A}$ can eavesdrop, intercept, modify, replay, insert, or delete encrypted packages transmitted over public networks.
2. **Chosen-Plaintext Queries (CPA)**: $\mathcal{A}$ can obtain ciphertexts for plaintexts of their choice.
3. **Chosen-Ciphertext Queries (CCA2)**: $\mathcal{A}$ can submit arbitrary package tuples $(v, S, N, C, T)$ to the decryption oracle and observe whether authentication succeeds or fails.
4. **Offline Dictionary Attacks**: $\mathcal{A}$ can attempt offline brute-force or dictionary attacks on weak user passwords if salt $S$ is known.

---

## 3. Cryptographic Security Goals

- **Goal G1: Confidentiality under Chosen-Ciphertext Attack (IND-CCA2)**: Ciphertext $C$ must convey zero information regarding plaintext $P$ to $\mathcal{A}$ without master key $K$.
- **Goal G2: Ciphertext Integrity & Authenticity (INT-CTXT)**: It must be computationally infeasible for $\mathcal{A}$ to forge a valid tuple $(v, S, N, C, T)$ that passes tag verification without $K_a$.
- **Goal G3: Replay Attack Resistance**: Every encryption event generates a unique 12-byte CSPRNG nonce $N$ and 16-byte salt $S$. Replayed packages are uniquely identified and invalidated.
- **Goal G4: Domain Separation**: Sub-keys $K_r, K_c, K_a$ are derived via independent HKDF expansion labels, preventing cross-primitive key leakage.

---

## 4. Cryptographic Assumptions

1. **HMAC-SHA256 Pseudo-Random Function (PRF) Assumption**: SHA-256 and HMAC-SHA256 behave as ideal PRFs.
2. **HKDF Extract-and-Expand Randomness**: HKDF outputs $K_r, K_c, K_a$ are computationally indistinguishable from uniform random byte strings.
3. **CSPRNG Unpredictability**: System CSPRNG (`crypto.primitives.random`) outputs cryptographically uniform salt (16B) and nonce (12B) buffers.

---

## 5. Out-of-Scope Security Bounds & Threats

- **Side-Channel Hardware Attacks**: Power analysis (DPA/SPA), acoustic leakage, or EM probing on target hardware.
- **Endpoint Compromise**: Keylogging, malware, or OS memory inspection on client endpoints prior to encryption.
- **Low-Entropy Master Passwords**: Master keys with $< 64$ bits of entropy are vulnerable to offline brute-force attacks unless wrapped in PBKDF2/Argon2 password hashing layers.
