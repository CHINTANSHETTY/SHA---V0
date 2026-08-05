# Educational Frequently Asked Questions (FAQ)

Frequently asked questions regarding the theory, implementation, security properties, and usage of the **KDR-CA-AEAD** framework.

---

## 1. Theoretical Concepts

### Q1: What is KDR-CA-AEAD?
**A:** KDR-CA-AEAD stands for **Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption**. It is a lightweight authenticated encryption scheme that uses 1D reversible cellular automata for encryption stream generation and HMAC-SHA256 Encrypt-then-MAC for authentication.

### Q2: Why use Cellular Automata for encryption?
**A:** Cellular automata rely on simple bitwise neighbor operations, making them exceptionally hardware-efficient (low gate count in ASIC/FPGA designs). Reversible rules provide simple decryption paths without requiring complex mathematical inversion tables.

### Q3: How does dynamic reconfiguration improve security over traditional CA ciphers?
**A:** Traditional CA ciphers use fixed rule tables, allowing attackers to solve system equations algebraically. KDR-CA-AEAD continuously changes the active Wolfram rule set per block based on HKDF sub-keys, destroying linear patterns and static state transition cycles.

---

## 2. Implementation & Usage

### Q4: Which Python version is required?
**A:** Python 3.10 or higher is required.

### Q5: What dependencies does KDR-CA-AEAD require?
**A:** Standard cryptographic primitives use Python's `cryptography` library (`HKDF`, `HMAC`, `SHA256`). Visualization and testing use `numpy`, `matplotlib`, `pytest`, and `flask`.

### Q6: Can I run KDR-CA-AEAD on Windows, Linux, and macOS?
**A:** Yes! The repository is cross-platform and fully validated on Windows 10/11, Linux (Ubuntu/Debian/Fedora), and macOS (Intel & Apple Silicon).

---

## 3. Security & Cryptanalysis

### Q7: Is KDR-CA-AEAD resistant to ciphertext tampering?
**A:** Yes. Because it uses Encrypt-then-MAC (EtM), any modified bit in the ciphertext, salt, nonce, or associated data triggers an immediate MAC verification failure, preventing unauthenticated decryption attempts.

### Q8: Does KDR-CA-AEAD protect against timing side-channel attacks?
**A:** Yes. All MAC tag comparisons use constant-time digest comparison (`hmac.compare_digest`), preventing timing leak vulnerabilities during verification.
