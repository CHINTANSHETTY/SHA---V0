# Security Disclosure & Vulnerability Handling Policy

**Project:** KDR-CA-AEAD (Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption)  
**Effective Date:** August 5, 2026  
**Status:** Active Security Policy  

---

## 1. Responsible Vulnerability Disclosure

The KDR-CA-AEAD project team takes cryptographic security, software integrity, and data confidentiality seriously. If you discover a security vulnerability, side-channel leakage issue, MAC tag verification bug, or potential vulnerability in KDR-CA-AEAD v1.0.0, we appreciate your help in disclosing it to us responsibly.

> [!CAUTION]
> **DO NOT create public GitHub issues or public forum discussions for unpatched security vulnerabilities.**

---

## 2. Reporting Channels & Contact Details

Please report security issues directly to the core maintainers via encrypted or direct email:

* **Primary Security Contact:** `shettyashwitha26@gmail.com`
* **Lead Cryptography Architect:** `chntnshetty@gmail.com`

### Please Include in Your Security Report:
1. **Description:** Clear summary of the issue, affected module(s), and security impact.
2. **Reproduction Steps:** Minimal proof-of-concept (PoC) script or step-by-step instructions.
3. **Environment:** Python version, operating system, dependency versions.
4. **Suggested Mitigation:** Proposed patch or fix (if available).

---

## 3. Security Response Timeline & SLAs

| Response Phase | Target SLA | Action Taken |
| :--- | :--- | :--- |
| **Initial Acknowledgement** | **Within 24 Hours** | Maintainers verify receipt and confirm initial investigation. |
| **Triage & Impact Assessment** | **Within 72 Hours** | Issue severity evaluated; CVSS v3.1 score determined. |
| **Patch Development** | **Within 7 Days** | Security patch developed, tested against test suite, and verified. |
| **Coordinated Release & Advisory**| **Within 14 Days** | Patch release published with security advisory and credit. |

---

## 4. Severity Classification

* **Critical (CVSS 9.0–10.0):** Key recovery, authentication bypass, unauthenticated remote code execution.
* **High (CVSS 7.0–8.9):** Partial plaintext recovery, forgery of MAC tags, side-channel timing leaks.
* **Medium (CVSS 4.0–6.9):** Algorithmic denial-of-service, state leakage without key exposure.
* **Low (CVSS 0.1–3.9):** Minor non-exploitable edge cases or informational security warnings.

---

## 5. Security Best Practices for Users

1. **Master Key Confidentiality:** Ensure master keys (32 bytes / 256 bits) are generated using cryptographically secure random number generators (`secrets.token_bytes(32)`).
2. **Nonce Uniqueness:** Never reuse nonces with the same key context.
3. **Associated Data (AD) Validation:** Always supply relevant contextual headers in AD for binding authentication.
