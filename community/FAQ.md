# Community Frequently Asked Questions (FAQ)

This FAQ addresses common community inquiries regarding open-source contribution, licensing, security disclosure, and development support for **KDR-CA-AEAD**.

---

## 1. Open Source & Licensing

### Q1: Under what license is KDR-CA-AEAD distributed?
**A:** KDR-CA-AEAD is licensed under the **Apache License 2.0**. You are free to use, modify, distribute, and embed the code in both commercial and academic projects provided the license notice is preserved.

### Q2: How can I contribute to the project?
**A:** We welcome contributions! You can submit bug reports, documentation improvements, unit tests, or feature pull requests. Please review `CONTRIBUTING.md` and `community/CONTRIBUTION_EXAMPLES.md` before submitting.

---

## 2. Security Disclosures & Vulnerability Reporting

### Q3: How should I report a suspected security vulnerability?
**A:** Do NOT create a public GitHub issue for security vulnerabilities. Please follow the instructions in `SECURITY.md` or email the maintainers directly at `security@kdrca-research.org`.

### Q4: Has KDR-CA-AEAD undergone formal security evaluation?
**A:** Yes. The framework includes formal proofs of IND-CCA2 security and constant-time HMAC tag comparison verification (`docs/phase3/formal_verification.md`).

---

## 3. Integration & Hardware Support

### Q5: Can I integrate KDR-CA-AEAD into C/C++ or Rust projects?
**A:** Yes. C-bindings and shared library wrappers (`.so` / `.dll`) are planned for Version 1.1. In the meantime, standard CFFI or Python embedding can be used.

### Q6: How do I report build or execution bugs?
**A:** Open a GitHub Issue using our issue template, specifying your Operating System, Python version, error traceback, and step-by-step reproduction steps.
