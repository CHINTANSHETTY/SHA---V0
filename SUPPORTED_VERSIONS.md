# Supported Versions & Maintenance Lifecycle Policy

**Project:** KDR-CA-AEAD (Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption)  
**Effective Date:** August 5, 2026  
**Status:** Active Governance Policy  

---

## 1. Supported Releases Matrix

The KDR-CA-AEAD core development team maintains a strict version support lifecycle to ensure cryptographic safety and software reliability.

| Release Version | Initial Release Date | Maintenance Status | Security Support End | Bug Fix Support End |
| :--- | :--- | :--- | :--- | :--- |
| **v1.0.0 (LTS)** | **August 2026** | **Active Long-Term Support (LTS)** | **August 2029** | **August 2028** |
| `< 1.0.0` (Development) | Pre-release | Deprecated / Unsupported | End of Life (EOL) | End of Life (EOL) |

---

## 2. Support Lifecycles & Definitions

* **Active Long-Term Support (LTS):** The primary production release (`v1.0.0`). Receives critical security patches, bug fixes, performance optimizations, and documentation updates.
* **Security Patch Window:** Security vulnerabilities reported in `v1.0.0` will be remediated via patch releases (e.g. `v1.0.1`) for a minimum of 36 months following major release.
* **Deprecation Notice:** Any future release that deprecates an existing API endpoint or cryptographic parameter will provide a minimum 12-month deprecation period.

---

## 3. Versioning Scheme

KDR-CA-AEAD strictly adheres to **Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH`)**:
* **MAJOR (`1.x.x`):** Backwards-incompatible API changes or cryptographic format changes.
* **MINOR (`x.1.x`):** Backwards-compatible new features or performance extensions.
* **PATCH (`x.x.1`):** Backwards-compatible bug fixes and security hotfixes.

---

## 4. Upgrade & Migration Guidance

All users, integrators, and researchers are strongly advised to deploy **`v1.0.0`**.  
For guidance on upgrading or integrating the high-level Python API, refer to the [User Guide](docs/user_guide.md) and [Installation Guide](docs/installation.md).
