# Digital Preservation & Archival Strategy

**Framework:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD v1.0.0)  
**Document Version:** 1.0.0  

---

## Executive Overview

This document specifies the **Digital Preservation & Archival Strategy** for **KDR-CA-AEAD v1.0.0**. It outlines procedures for long-term open-science preservation, persistent DOI metadata harvesting, Software Heritage directory indexing, license preservation, and cryptographic integrity verification.

---

## 1. Archival Repositories & Indexing Protocols

To guarantee permanent accessibility beyond GitHub platform boundaries, KDR-CA-AEAD is archived across two primary open-science platforms:

```text
+-----------------------+-----------------------+-----------------------+
|  GitHub Repository    |    Zenodo Archive     |   Software Heritage   |
|   (Primary Source)    |    (DOI Archival)     |    (SWHID Index)      |
+-----------------------+-----------------------+-----------------------+
| Active development,   | Persistent Zenodo DOI | Permanent source code |
| issues & governance   | for release tags      | directory snapshot    |
+-----------------------+-----------------------+-----------------------+
```

1. **Zenodo Open-Science Repository**:
   - Webhook integration automatically archives snapshot zip archives for release tags (e.g., `v1.0.0`).
   - Mints a persistent Digital Object Identifier (DOI): `10.5281/zenodo.<reserved-doi>`.
2. **Software Heritage Foundation**:
   - Archives raw source code trees under persistent SWHID identifiers (`swh:1:dir:ebfa1b308199f4f61c0dac6a7fc7ada5c1f22fdd`).

---

## 2. Metadata & Documentation Preservation

- **Citation Metadata**: Standard `CITATION.cff` (YAML v1.2.0) and `codemeta.json` (CodeMeta 2.0 Schema) are embedded directly in the repository root.
- **License Preservation**: Standard Apache License 2.0 (`LICENSE`) is preserved alongside all source headers.
- **Data Preservation**: Raw NIST SP 800-22 p-value logs (`evaluation_results/nist_pvalues.json`) and SAC matrices (`evaluation_results/sac_matrix.json`) are version-controlled.

---

## 3. Integrity Verification & Backup Recommendations

1. **Git Commit Signing**: Maintainers are encouraged to GPG-sign all release tags (`git tag -s v1.0.0`).
2. **Checksum Verification**: Release packages published on GitHub Releases include SHA-256 checksum manifests for independent download verification.
