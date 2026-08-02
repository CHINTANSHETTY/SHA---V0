# IEEE-Level Cryptographic Project Audit Report

**Project Name:** SHA---V0 (Healthcare Security Application)  
**Target Repository:** `https://github.com/CHINTANSHETTY/SHA---V0`  
**Auditor Role:** Senior Cryptography Researcher, IEEE Transactions Reviewer, & Security Auditor  
**Evaluation Standard:** IEEE Transactions on Information Forensics and Security (TIFS) / IEEE Security & Privacy  

---

## Executive Summary

This document presents a rigorous, research-grade cryptographic and architectural audit of the **SHA---V0** project. The target codebase implements a custom encryption scheme combining Flip-Bit Cellular Automata (FBCA), block circular right shift, Margolus block permutation, and SHA-512 key stream generation for protecting electronic health records (EHR) within a Flask web interface backed by SQLite.

### Audit Summary Matrix

| Metric | Score | Classification |
| :--- | :---: | :--- |
| **System Architecture Score** | 35 / 100 | Prototype |
| **Cryptographic Soundness Score** | 12 / 100 | Insecure / Flawed |
| **Mathematical Validation Score** | 05 / 100 | Missing |
| **Code Quality & Security Score** | 40 / 100 | Basic / Vulnerable |
| **Experimental Validation Score** | 10 / 100 | Missing |
| **IEEE Publication Readiness** | **18 / 100** | **Academic Prototype (Not IEEE Ready)** |

---

## 1. Project Architecture Audit

### 1.1 Overall Architecture & Data Flow
The architecture consists of a 3-tier web application:
1. **Presentation Layer (`templates/`, `static/`, `app.py`)**: Flask web routing handling doctor authentication, patient record entry, viewing, editing, and deletion.
2. **Cryptographic Processing Layer (`encrypt.py`, `decrypt.py`, `shaModule.py`, `utils.py`)**: Custom cipher pipeline performing text-to-binary conversion, FBCA transformation, circular shifting, Margolus block swapping, and SHA-512 XOR stream encryption.
3. **Persistence Layer (`database.py`, `records.db`)**: SQLite storage storing doctor credentials and encrypted patient records (`id`, `patientId`, `patientName`, `cipherText`).

```
[ Plaintext EHR ] 
       │
       ▼
 [ textToBinary ] ──► [ 8-bit Blocks ] ──► [ FBCA Flip ] ──► [ Right Shift ] ──► [ Margolus Swap ]
                                                                                         │
 [ Password ] ──► [ SHA-512 Hash ] ──► [ Repeating 512-bit Key Stream ] ◄────────────────┘
                                                       │
                                                       ▼
                                            [ Bitwise XOR (Ciphertext) ]
```

### 1.2 Architecture Weaknesses & Gap Analysis

- **State Management & Session Vulnerability**:
  - `app.py` stores unencrypted plaintext passwords in Flask session (`session["editPassword"]`) during patient record edits.
  - Flask `secret_key` is hardcoded as `"sha_healthcare_secret_key"`, allowing session forgery if leaked.
- **Unauthenticated Key Lifecycle**:
  - Keys are derived directly from user passwords per transaction without salt or Initialization Vector (IV).
  - No master keying, key rotation, or Public Key Infrastructure (PKI) for multi-doctor access control.
- **Database Security**:
  - Doctor authentication passwords are stored in **plaintext** inside the SQLite `doctors` table ([database.py:L11-L14](file:///c:/Users/chntn/OneDrive/Desktop/SHA/database.py#L11-L14)).
  - Patient names are stored unencrypted (`patientName TEXT`), leaking PII alongside the encrypted payload.

---

## 2. Algorithm Audit

### 2.1 Component-by-Component Review

#### A. Flip-Bit Cellular Automaton (`applyFbca` in `encrypt.py`)
- **Purpose**: Non-linear block modification based on parity of initial bits.
- **Input**: List of 8-bit binary strings.
- **Operation**: Computes `bitSum = int(block[0]) + int(block[1])`. If `bitSum % 2 == 1`, bitwise flips all bits in the 8-bit block.
- **Mathematical Paradox**: Bitwise negation of an 8-bit block $B$ yields $\bar{B}_i = 1 - B_i$. The sum of the first two bits becomes:
  $$\bar{B}_0 + \bar{B}_1 = (1 - B_0) + (1 - B_1) = 2 - (B_0 + B_1)$$
  Taking modulo 2: $(2 - \text{bitSum}) \pmod 2 \equiv \text{bitSum} \pmod 2$.
- **Critical Flaw**: Parity is **invariant under bitwise inversion**! Thus, FBCA is **completely self-inverse** and key-independent. An attacker can invert FBCA without knowing the password.

#### B. Right Shift (`rightShift` in `encrypt.py`)
- **Purpose**: Diffusion across 8-bit block boundaries.
- **Operation**: Single circular right shift on block array: `[blocks[-1]] + blocks[:-1]`.
- **Complexity**: $O(N)$ time and space.
- **Cryptographic Value**: Zero key dependence. It is a linear permutation $P_{shift}$.

#### C. Margolus Block Transformation (`applyMorgolus` in `encrypt.py`)
- **Purpose**: Block pair swapping.
- **Operation**: Swaps adjacent 8-bit blocks: $(B_{2i}, B_{2i+1}) \mapsto (B_{2i+1}, B_{2i})$.
- **Cryptographic Value**: Self-inverse block permutation ($P_{margolus} \circ P_{margolus} = I$). Zero key dependence.

#### D. Key Derivation & Stream XOR (`createBinaryKey` and `xorWithKey`)
- **Operation**: Hashes password using single-pass SHA-512 to produce 512 bits. Repeats 512 bits to match data length $L$, then bitwise XORs.
- **Critical Flaw**: For data length $L > 512$ bits (64 bytes), the key repeats periodically every 64 bytes. This creates a **periodic key stream cipher**, vulnerable to standard polyalphabetic reduction and reused key stream attacks.

---

## 3. Cryptographic Audit

### 3.1 CIA Triad & Security Principles

```
+-------------------+----------------------------------------------------+-----------------------+
| Security Property | Current Implementation Status                      | Evaluation            |
+-------------------+----------------------------------------------------+-----------------------+
| Confidentiality   | Deterministic XOR with repeated 512-bit key stream | FAILED                |
| Integrity         | No MAC / HMAC / GCM tag attached                   | FAILED (Malleable)    |
| Authentication    | Plaintext passwords in DB; no signature scheme     | FAILED                |
| Availability      | Single SQLite file lock; no error recovery          | PARTIAL               |
| Non-repudiation   | No digital signatures or audit logs                | FAILED                |
+-------------------+----------------------------------------------------+-----------------------+
```

### 3.2 Cryptanalysis & Attack Resistance Matrix

1. **Reused Key Stream Attack (CPA / KPA)**:
   - **Vulnerability**: Encrypting two records $P_1, P_2$ under the same password $K_{pass}$ yields $C_1 = T(P_1) \oplus K$ and $C_2 = T(P_2) \oplus K$.
   - **Exploit**: $C_1 \oplus C_2 = T(P_1) \oplus T(P_2)$. Since $T$ is an unkeyed deterministic transformation, $P_1 \oplus P_2 = T^{-1}(C_1 \oplus C_2)$. **All encryption is stripped without knowing the password.**
2. **Bit-Flipping & Ciphertext Malleability (CCA)**:
   - **Vulnerability**: Lacks authenticated encryption (AEAD).
   - **Exploit**: Flipping bit $k$ in `cipherText` flips bit $k$ in $T(P)$. The application accepts modified ciphertext without detection.
3. **Brute Force & Dictionary Attack**:
   - **Vulnerability**: Uses raw `SHA-512(password)` with zero salt and zero memory work factor.
   - **Exploit**: Modern GPUs can compute $>10^9$ SHA-512 hashes per second. Short passwords (e.g., `"hospital123"`) are cracked in milliseconds.
4. **Frequency & Structural Leakage**:
   - **Vulnerability**: Patient record header format (`patientId|name|...`) combined with deterministic encryption leaks record identity and length.

---

## 4. Mathematical Validation Audit

| Required Mathematical Proof | Present in Project? | Academic Expectation for IEEE |
| :--- | :---: | :--- |
| **Provable Security (IND-CPA / IND-CCA2)** | ❌ No | Game-based reduction proof to standard hard problems. |
| **Strict Avalanche Criterion (SAC)** | ❌ No | Demonstration that 1-bit input flip alters 50% output bits. |
| **Confusion & Diffusion Quantifier** | ❌ No | Differential branch number and linear approximation probability. |
| **Entropy & Randomness Tests** | ❌ No | NIST SP 800-22 statistical test suite report over $10^6$ bit samples. |
| **Key Space Entropy** | ❌ Low | Minimum 128-bit uniform entropy source (CSPRNG). |

---

## 5. Code Quality & Security Audit

### 5.1 File-by-File Technical Inspection

#### 1. [app.py](file:///c:/Users/chntn/OneDrive/Desktop/SHA/app.py)
- **Critical Issues**:
  - Hardcoded secret key ([app.py:L23](file:///c:/Users/chntn/OneDrive/Desktop/SHA/app.py#L23)).
  - Weak input validation; relies on string splitting by `|` ([app.py:L146-L154](file:///c:/Users/chntn/OneDrive/Desktop/SHA/app.py#L146-L154)). If patient name or disease contains `|`, decryption logic fails or corrupts fields.
  - Storing plaintext password in session during edit workflow ([app.py:L351](file:///c:/Users/chntn/OneDrive/Desktop/SHA/app.py#L351)).

#### 2. [database.py](file:///c:/Users/chntn/OneDrive/Desktop/SHA/database.py)
- **Critical Issues**:
  - Passwords stored in plaintext ([database.py:L34-L37](file:///c:/Users/chntn/OneDrive/Desktop/SHA/database.py#L34-L37)).
  - Unsalted authentication queries ([database.py:L47-L50](file:///c:/Users/chntn/OneDrive/Desktop/SHA/database.py#L47-L50)).
  - Patient names stored unencrypted in `patientRecords` table ([database.py:L63-L67](file:///c:/Users/chntn/OneDrive/Desktop/SHA/database.py#L63-L67)).

#### 3. [encrypt.py](file:///c:/Users/chntn/OneDrive/Desktop/SHA/encrypt.py) & [decrypt.py](file:///c:/Users/chntn/OneDrive/Desktop/SHA/decrypt.py)
- **Critical Issues**:
  - Transformations ($T$) are completely unkeyed and deterministic.
  - Inefficient string-based bit operations (`"0"` and `"1"` character arrays instead of integer byte manipulations/C-types), leading to massive memory allocation overhead ($8\times$ explosion).

#### 4. [utils.py](file:///c:/Users/chntn/OneDrive/Desktop/SHA/utils.py) & [shaModule.py](file:///c:/Users/chntn/OneDrive/Desktop/SHA/shaModule.py)
- **Critical Issues**:
  - `binaryToText` throws unhandled `ValueError` on malformed bit lengths without graceful recovery.

---

## 6. Experimental Validation Audit

The project currently provides **zero empirical experimental benchmarks**:
- No performance benchmarks (throughput in MB/s, execution latency vs. payload size).
- No memory utilization or CPU cycle analysis.
- No comparison against standard ciphers (AES-256-GCM, ChaCha20-Poly1305).
- No randomness testing (NIST SP 800-22, Dieharder test suites).

---

## 7. Standards Compliance Audit

```
+-----------------------+----------------------------------+--------------------------------------+
| Standard              | Requirement                      | Project Compliance Status            |
+-----------------------+----------------------------------+--------------------------------------+
| NIST SP 800-132       | Password-Based Key Derivation    | NON-COMPLIANT (Uses raw SHA-512)     |
| NIST SP 800-38D       | Authenticated Encryption (AEAD)  | NON-COMPLIANT (Unauthenticated XOR)  |
| FIPS 140-3            | Cryptographic Module Security    | NON-COMPLIANT (Plaintext key storage)|
| HIPAA Security Rule   | EHR Encryption & Access Control  | NON-COMPLIANT (Unencrypted PII)      |
+-----------------------+----------------------------------+--------------------------------------+
```

---

## 8. Research Contribution Audit

- **Novelty Assessment**: Combining Cellular Automata, Margolus swapping, and XOR is a known concept in introductory academic literature. However, because the pre-processing transformation $T$ is unkeyed, it adds **zero cryptographic security** over simple repeated XOR.
- **Justification of Claims**: The claim of a secure custom cryptographic scheme for healthcare records cannot be justified under modern cryptanalysis.

---

## 9. IEEE Publication Readiness Assessment

An IEEE paper requires a complete manuscript structure. Below is the readiness evaluation for publication:

```
[1] Problem Statement & Threat Model ──► MISSING (No formal adversary model)
[2] Related Work Comparison         ──► MISSING (No comparison with state-of-the-art)
[3] Rigorous Mathematical Proofs    ──► MISSING (No formal security reduction)
[4] Empirical Benchmarking          ──► MISSING (No NIST SP 800-22 or throughput metrics)
[5] Code/Data Reproducibility       ──► PARTIAL (Code exists, but lacks formal test harness)
```

---

## 10. Comprehensive Gap Analysis Table

| # | Gap Description | Current State | Expected IEEE Standard | Severity | Priority |
| :-: | :--- | :--- | :--- | :-: | :-: |
| **1** | **Deterministic & Reused Key Stream** | Identical ciphertext for same input/password; repeated 512-bit key stream | Random IV/Nonce per encryption (e.g. AES-GCM or ChaCha20) | **CRITICAL** | P0 |
| **2** | **Unkeyed Pre-processing Transformation** | FBCA, Shift, and Margolus do not depend on key material | All cipher operations must be key-dependent or cryptographically proven | **CRITICAL** | P0 |
| **3** | **Plaintext Passwords in DB** | SQLite stores doctor passwords in plaintext | Argon2id or PBKDF2 hashing with random salt | **CRITICAL** | P0 |
| **4** | **Lack of AEAD / Integrity Tag** | Raw XOR cipher; malleable ciphertext | HMAC-SHA256 or GCM authentication tag | **CRITICAL** | P1 |
| **5** | **Delimiter Injection Vulnerability** | Pipe `|` used for data serialization | JSON / Protocol Buffers / Structured Binary encoding | **HIGH** | P1 |
| **6** | **Lack of Statistical & NIST Testing** | Manual test scripts (`test.py`) with 1 test case | Full NIST SP 800-22 test suite evaluation across $10^6$ bits | **HIGH** | P2 |
| **7** | **Performance & Complexity Benchmarks** | No timing or throughput metrics | Comparative benchmarks (cycles/byte, throughput vs AES) | **MEDIUM** | P2 |

---

## 11. Final Assessment & Roadmap to IEEE Quality

### 11.1 Score Summary
- **Overall Technical Score:** `28 / 100`
- **Security Score:** `12 / 100`
- **Code Quality Score:** `40 / 100`
- **Research Quality Score:** `15 / 100`
- **Publication Readiness Score:** `18 / 100`

**Classification:** **Academic Prototype / Proof of Concept**

---

### 11.2 Required Engineering & Research Roadmap

To elevate this project to **IEEE Conference / Journal Quality**, the following redesign steps are required:

1. **Adopt Standard AEAD or Keyed Cellular Automata**:
   - Incorporate the secret key $K$ directly into the cellular automata update rules (Keyed CA).
   - Use **Argon2id** or **PBKDF2-HMAC-SHA256** with a unique 128-bit salt per user/record for key derivation.
   - Attach an **HMAC-SHA256** tag or use standard **AES-256-GCM** / **ChaCha20-Poly1305**.

2. **Implement Random Initialization Vectors (IV)**:
   - Generate a fresh 96-bit or 128-bit random IV (using `secrets` or `os.urandom`) for every encryption operation to ensure IND-CPA security.

3. **Secure Authentication & DB Storage**:
   - Hash doctor passwords using `bcrypt` or `Argon2id` before storing in SQLite.
   - Encrypt all PII fields (including patient name) in the database.

4. **Conduct Mathematical & Experimental Validation**:
   - Calculate Strict Avalanche Criterion (SAC), Differential Branch Number, and Shannon Entropy.
   - Run the **NIST SP 800-22** statistical battery on generated ciphertexts.
   - Benchmark throughput (MB/s) and memory usage across payload sizes ranging from 1 KB to 10 MB.
