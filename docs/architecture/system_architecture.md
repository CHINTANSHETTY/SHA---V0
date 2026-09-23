# KDR-CA-AEAD System Architecture & Workflow Specifications

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**IEEE Mapping:** Section IV – System Architecture & Module Integration  
**Version:** 1.0.0 (Publication Candidate)  

---

## 1. Executive Architecture Overview

The **KDR-CA-AEAD** cryptographic framework is built on a modular, domain-separated architecture combining HKDF key derivation, Candidate A-Chain Dynamic Cellular Automata permutations, HMAC-SHA256 CTR-PRNG keystream generation, and Encrypt-then-MAC AEAD authentication.

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
                                    |
                                    v
                  +-----------------------------------+
                  | Security Analysis & Benchmarking  |
                  +-----------------------------------+
```

---

## 2. Component Responsibilities

1. **User / Application API Layer (`crypto`)**: Exposes clean, typed interfaces for binary and string encryption/decryption (`encrypt_bytes`, `decrypt_bytes`).
2. **Key Derivation Subsystem (`crypto.engine.key_schedule`)**: Derives domain-separated sub-keys $K_r$ (rule seed), $K_c$ (cipher key), and $K_a$ (MAC key) using HKDF-SHA256 with CSPRNG salt and nonce context.
3. **Keyed Dynamic CA Engine (`crypto.engine.dynamic_ca`)**: Applies reversible Candidate A-Chain non-linear state transformations using Wolfram uint8 rule tables derived from $K_r$.
4. **Keystream PRNG Subsystem (`crypto.engine.encrypt`)**: Generates arbitrary-length keystream using HMAC-SHA256 Counter Mode (CTR-PRNG) parameterized by $K_c$ and Nonce.
5. **Authenticated Encryption Subsystem (`crypto.engine.encrypt` / `decrypt`)**: Combines CA non-linear permutation, CTR stream encryption, and constant-time HMAC-SHA256 AEAD tag calculation over `Nonce || Salt || AssociatedData || Ciphertext`.
6. **Security & Benchmark Framework (`crypto.analysis`)**: Provides statistical randomness evaluation (NIST SP 800-22), avalanche effect measurement, performance benchmarks, and automated IEEE visualization generation.

---

## 3. Workflow Diagrams

### 3.1 Encryption Workflow Diagram

```mermaid
graph TD
    A["Master Key (K) + Salt + Nonce"] --> B["HKDF-SHA256 Key Schedule"]
    B --> C1["Rule Seed (K_r)"]
    B --> C2["Cipher Key (K_c)"]
    B --> C3["MAC Key (K_a)"]
    
    C1 --> D["32-Element CA Rule Table Expansion"]
    D --> E["Candidate A-Chain Non-Linear CA Permutation"]
    
    Plaintext["Plaintext Input (P)"] --> E
    E --> Transformed["Transformed CA State Vector (T)"]
    
    C2 --> F["HMAC-SHA256 CTR-PRNG Keystream Generator"]
    F --> Keystream["Keystream Bytes (KS)"]
    
    Transformed --> G["Bitwise XOR Stream Encryption: CT = T ⊕ KS"]
    Keystream --> G
    
    G --> Ciphertext["Ciphertext (CT)"]
    
    Ciphertext --> H["HMAC-SHA256 AEAD Tag Computation"]
    C3 --> H
    AD["Associated Authenticated Data (AD)"] --> H
    
    H --> Tag["Authentication Tag (32 Bytes)"]
    Tag --> Package["EncryptedPackage (Salt, Nonce, CT, Tag)"]
    Ciphertext --> Package
```

---

### 3.2 Decryption Workflow Diagram

```mermaid
graph TD
    Package["EncryptedPackage (Salt, Nonce, CT, Tag)"] --> A["Extract Nonce, Salt, CT, Tag"]
    
    MasterKey["Master Key (K)"] --> B["HKDF-SHA256 Key Schedule"]
    A --> B
    
    B --> C1["Rule Seed (K_r)"]
    B --> C2["Cipher Key (K_c)"]
    B --> C3["MAC Key (K_a)"]
    
    C3 --> D["Re-compute HMAC-SHA256 Tag over Nonce || Salt || AD || CT"]
    AD["Associated Authenticated Data (AD)"] --> D
    
    D --> E{"Constant-Time Tag Verification"}
    E -- "Mismatch" --> F["Raise AuthenticationError (Abort)"]
    E -- "Match (PASS)" --> G["Expand HMAC-SHA256 CTR Keystream"]
    
    C2 --> G
    G --> Keystream["Keystream Bytes (KS)"]
    
    A --> H["Bitwise XOR Stream Decryption: T = CT ⊕ KS"]
    Keystream --> H
    H --> Transformed["Transformed State Vector (T)"]
    
    C1 --> I["Construct 32-Element CA Rule Table"]
    I --> J["Candidate A-Chain Inverse CA Transformation"]
    Transformed --> J
    
    J --> Plaintext["Recovered Original Plaintext (P)"]
```

---

### 3.3 Complete System Interaction Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as Public API (crypto)
    participant Engine as Crypto Engine
    participant KS as HKDF KeySchedule
    participant CA as Dynamic CA Engine
    participant AEAD as HMAC AEAD Tag
    participant Analysis as Security & Benchmark Analysis

    User->>API: encrypt_bytes(payload, master_key, AD)
    API->>Engine: Forward Payload & Key Parameters
    Engine->>KS: Derive Sub-Keys (K_r, K_c, K_a) via HKDF
    KS-->>Engine: Return KeyMaterial (rule_table, K_c, K_a)
    Engine->>CA: Apply Forward CA Permutation (payload, rule_table)
    CA-->>Engine: Return Transformed State Vector
    Engine->>Engine: XOR Transformed State with CTR Keystream
    Engine->>AEAD: Generate HMAC-SHA256 Tag (K_a, Nonce||Salt||AD||CT)
    AEAD-->>Engine: Return 32-Byte Tag
    Engine-->>API: EncryptedPackage(salt, nonce, CT, tag)
    API-->>User: EncryptedPackage Output

    User->>Analysis: run_full_security_analysis()
    Analysis->>Engine: Run End-to-End Test Suite
    Analysis->>Analysis: Execute Entropy, SAC, Monobit & Benchmark Suites
    Analysis-->>User: Export Master JSON, IEEE CSV Tables & 300 DPI Figures
```
