# KDR-CA-AEAD Phase 5.7: Long-Term Maintenance Roadmap

**Author:** Nagamrutha (Security Analysis & Cryptographic Validation Lead)  
**Date:** August 4, 2026  
**Status:** Completed  
**Version:** 1.0.0  

---

## 1. Executive Overview

This document outlines the long-term maintenance strategy, versioning policy, security response workflow, quality assurance schedule, platform support lifecycle, and risk register for the **KDR-CA-AEAD** (Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption) framework following its official v1.0.0 release.

---

## 2. Maintenance Strategy & Governance Model

### 2.1 Governance Roles & Responsibilities

| Role | Primary Responsibility | Assigned Lead |
| :--- | :--- | :--- |
| **Cryptography Architect** | HKDF key schedule, 1D Dynamic CA state engine, AEAD construction | Chintan Shetty |
| **Security & Validation Lead** | Statistical security validation (SAC/BIC), CVE response, regression QA | Nagamrutha |
| **Publication & Release Lead** | IEEE paper synchronization, release packaging, FAIR metadata, documentation | Ashwitha |

### 2.2 Support Scope
- **Core Cryptographic Engine (`crypto/`):** Full LTS support. Security patches and bug fixes prioritized immediately.
- **Web Application & CLI (`app.py`, `encrypt.py`, `decrypt.py`):** Maintenance support for standard HTTP workflows and CLI execution.
- **Benchmark & Research Suite (`crypto/analysis/`):** Maintenance support for performance monitoring and graph generation tools.

---

## 3. Semantic Versioning Policy (SemVer 2.0.0)

The project strictly follows [Semantic Versioning 2.0.0](https://semver.org/):

$$\text{Format: } \text{MAJOR}.\text{MINOR}.\text{PATCH}$$

### 3.1 Version Progression Rules:
1. **MAJOR (e.g. v1.0.0 $\rightarrow$ v2.0.0):**
   - Triggered by incompatible API changes or changes to core cryptographic state permutations.
   - Requires full formal re-verification and NIST SP 800-22 statistical re-validation.
2. **MINOR (e.g. v1.0.0 $\rightarrow$ v1.1.0):**
   - Triggered by new backward-compatible functionality, additional statistical analysis tools, or performance optimizations.
3. **PATCH (e.g. v1.0.0 $\rightarrow$ v1.0.1):**
   - Triggered by non-breaking bug fixes, security patches, documentation enhancements, or CI configuration updates.

---

## 4. Security Vulnerability & Disclosure Policy

### 4.1 Responsible Disclosure Timeline
- **Private Reporting:** Security vulnerabilities should be reported privately to the maintenance team via security contact emails.
- **Initial Response SLA:** Initial acknowledgment within **24 hours**.
- **Assessment & Triage:** Severity classification (CVSS v3.1) within **72 hours**.
- **Patch Execution & Disclosure:** Security patch release published within **14 business days** (or 90-day embargo for complex vulnerabilities).

### 4.2 Security Review Schedule

| Review Activity | Frequency | Responsible Lead |
| :--- | :---: | :---: |
| **Automated Dependency Vulnerability Audit** | Monthly | Security Lead |
| **Static Code Analysis & Security Scan** | Per Pull Request | CI Automated |
| **Full Cryptographic Primitive Audit** | Bi-annually | Cryptography Architect |
| **NIST SP 800-22 Statistical Re-verification** | Annually | Validation Lead |

---

## 5. Quality Assurance (QA) & Platform Support Roadmap

### 5.1 QA Activity Cadence

```text
[Per Commit / PR]  ---> Automated Pytest & Code Coverage (465 Tests)
[Monthly]          ---> Dependency Health & Vulnerability Scan
[Quarterly]        ---> Benchmark Performance & Latency Regression Audit
[Annually]         ---> Full Multi-Platform Matrix & Research Metadata Synchronization
```

### 5.2 Supported Platforms & Environment Support Window

| Platform Category | Target Environment | Support Policy | EOL Policy |
| :--- | :--- | :---: | :--- |
| **Operating Systems** | Windows 10/11 x64, Ubuntu 22.04+ LTS, macOS 14+ | **Active** | Supported while vendor LTS is active |
| **Python Runtimes** | CPython 3.10, 3.11, 3.12, 3.13 | **Active** | Deprecated 6 months after CPython EOL |
| **Dependencies** | `Flask>=3.0.0`, `argon2-cffi>=23.1.0` | **Active** | Maintained to latest stable minor releases |

---

## 6. Risk Register & Future Recommendations

### 6.1 Current Risk Register

| Risk ID | Category | Description | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **RSK-01** | Performance | Pure Python Cellular Automata throughput (~13 MB/s) is slower than hardware-accelerated AES-NI. | Maintain clear benchmarks; document pure-software lightweight use case. |
| **RSK-02** | Dependency | Upstream breaking changes in Flask or Argon2 CFFI bindings. | Pin dependency upper bounds (`Flask>=3.0.0,<4.0.0`) in distribution packages. |
| **RSK-03** | Portability | Platform-specific CFFI compilation errors on non-standard architectures. | Rely on official pre-built wheel distributions from PyPI. |

### 6.2 Future Optimization Recommendations (Non-Implemented Roadmap)
- **Recommendation A (C-Extension Acceleration):** Optional Cython / C extension for `apply_keyed_ca_forward` state permutations to boost throughput beyond 100 MB/s.
- **Recommendation B (Hardware Acceleration):** Explore SHA256 hardware instruction set bindings (`sha256armv8` / `sha256ni`).
- **Recommendation C (PyPI Package Publishing):** Publish official `kdr-ca-aead` PyPI wheel package to PyPI index.

---

## 7. Conclusion

Phase 5.7: Long-Term Maintenance Roadmap is **FULLY PASSED**. The governance structure, versioning policy, security SLA, and risk register establish a sustainable foundation for post-release support.

The framework is now ready to proceed to **Phase 5.8: Final Phase 5 Consolidation & Sign-off**.
