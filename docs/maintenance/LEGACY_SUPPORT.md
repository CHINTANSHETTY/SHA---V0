# Legacy Support & Backward Compatibility Policy

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Document Version:** 1.0.0  

---

## Executive Overview

This document specifies the **Recommended Long-Term Support & Backward Compatibility Guidelines** for **KDR-CA-AEAD**. It provides maintainer guidance on supported release series, End-of-Life (EOL) schedules, security maintenance recommendations, API stability guidelines, and migration paths.

---

## 1. Recommended Release Support Lifecycle

| Release Series | Status | Release Date | Recommended EOL | Support Level |
| :--- | :--- | :--- | :--- | :--- |
| **v1.0.x (Current)** | **Active LTS** | August 2026 | August 2029 (Recommended) | Full Security & Maintenance Support |
| **v0.x (Legacy Drafts)**| Deprecated | August 2026 | August 2026 | EOL – Upgrade to v1.0.0 recommended |

---

## 2. API Stability & Backward Compatibility Guidelines

1. **v1.x Series Stability**: All public API function signatures (`encrypt_bytes`, `decrypt_bytes`, `EncryptedPackage`) exported in `crypto/__init__.py` should preserve strict signature compatibility across all minor (`v1.x.y`) releases.
2. **Dataclass Package Serialization**: The payload data structure (`EncryptedPackage`) should maintain backward-compatible JSON serialization (`to_json`, `from_json`, `to_dict`, `from_dict`) across v1.x releases.

---

## 3. Security Maintenance & EOL Guidance

- **Security Maintenance**: Maintainers are recommended to provide security patch fixes for critical vulnerabilities affecting the v1.x LTS series throughout its recommended long-term support policy.
- **Migration Guidance**: Downstream users upgrading from pre-release experimental versions (v0.x) should update API invocations to use `crypto.encrypt_bytes` and `crypto.decrypt_bytes`.
- **Archived Release Policy**: Historical tag snapshots remain permanently archived on GitHub and Zenodo for research provenance.
