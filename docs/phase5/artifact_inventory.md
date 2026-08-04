# KDR-CA-AEAD Phase 5.6: Complete Research Artifact Inventory

**Author:** Nagamrutha (Security Analysis & Cryptographic Validation Lead)  
**Date:** August 4, 2026  
**Status:** Completed  
**Version:** 1.0.0  

---

## 1. Overview

This document provides a comprehensive inventory of all research code, proof assets, statistical datasets, camera-ready manuscripts, release packages, and FAIR metadata associated with the **KDR-CA-AEAD** framework.

---

## 2. Source Code & Primitives Inventory

| Artifact Name | Path / Location | Description & Role | Verification Status |
| :--- | :--- | :--- | :---: |
| **`crypto/` Engine** | `crypto/` | Core package: HKDF key schedule, 1D Dynamic CA engine, EtM AEAD | **Verified** |
| **`crypto/__init__.py`** | `crypto/__init__.py` | Unified public API export surface (24 symbols) | **Verified** |
| **Web GUI Application** | `app.py` | Production Flask web interface & record management | **Verified** |
| **SQLite DB Manager** | `database/` | Patient record database with Argon2id password hashing | **Verified** |
| **Standalone CLI Tools** | `encrypt.py`, `decrypt.py` | High-level CLI encryption and decryption entry points | **Verified** |
| **Legacy Utilities** | `shaModule.py`, `utils.py` | Bit-level manipulation and legacy hash utilities | **Verified** |

---

## 3. Test & Security Validation Inventory

| Artifact Name | Path / Location | Description & Role | Verification Status |
| :--- | :--- | :--- | :---: |
| **Unit Test Suite** | `tests/unit/` | 42 unit tests for engine, HKDF, HMAC, CA, DB, and App | **42 / 42 Passed** |
| **Integration Suite** | `tests/integration/` | 18 end-to-end integration tests across 8 payload types | **18 / 18 Passed** |
| **Security & SAC Suite**| `tests/test_*.py` | 385 tests covering avalanche (>40%), SAC, BIC, NIST SP 800-22 | **385 / 385 Passed** |
| **Benchmark Suite** | `crypto/analysis/tests/` | 20 benchmark timer and statistical calculation tests | **20 / 20 Passed** |
| **Unified Runner** | `scripts/run_all_tests.py` | Master automated test execution script | **465 / 465 Passed** |

---

## 4. Academic Research & Manuscript Assets

| Artifact Name | Path / Location | Description & Role | Verification Status |
| :--- | :--- | :--- | :---: |
| **IEEE Manuscript PDF** | `paper/IEEE_Paper.pdf` | Camera-ready double-column IEEE research paper | **Verified** |
| **BibTeX Citations** | `paper/references.bib`, `citation.bib` | Standard BibTeX reference file for citations | **Verified** |
| **300 DPI Figures** | `paper/avalanche.png`, `docs/figures/` | High-resolution publication diagrams & avalanche plots | **Verified** |
| **Security Reports** | `docs/phase3/`, `reports/` | Formal verification, NIST compliance, OWASP reports | **Verified** |

---

## 5. Release Packages & Archival Bundles (`release/`)

| Release Archive | Size (KB) | SHA-256 Checksum | Purpose / Target | Audit Status |
| :--- | :---: | :--- | :--- | :---: |
| `kdr-ca-aead-v1.0.0.zip` | 7,768 KB | `ad3944c003e26c36...` | Primary source distribution archive | **PASS** |
| `kdr-ca-aead-v1.0.0.tar.gz` | 7,525 KB | `8e5a42d0951dbdad...` | POSIX gzipped tarball distribution | **PASS** |
| `documentation-v1.0.0.zip` | 6,441 KB | `073830d4f4a40a2d...` | Complete documentation bundle | **PASS** |
| `paper-v1.0.0.zip` | 991 KB | `c867226f6d13d04c...` | IEEE manuscript & figures bundle | **PASS** |
| `benchmarks-v1.0.0.zip` | 1,005 KB | `505c59a41e1fde18...` | Benchmark tools & results bundle | **PASS** |
| `complete-release-v1.0.0.zip` | 8,710 KB | `36a827b16c205549...` | Complete monorepo release archive | **PASS** |

---

## 6. FAIR Metadata & Citation Files

| Metadata File | Location | Content & Purpose | Status |
| :--- | :--- | :--- | :---: |
| **`CITATION.cff`** | Root | Citation File Format v1.2.0 metadata (Apache-2.0 license) | **Synchronized** |
| **`citation.bib`** | Root | BibTeX entry for IEEE Transactions citation | **Synchronized** |
| **`citation.txt`** | Root | Plaintext academic citation string | **Synchronized** |
| **`LICENSE`** | Root | Apache License 2.0 full legal text | **Synchronized** |
| **`environment_snapshot.json`** | `release/` | CPython executable, OS architecture, pip metadata | **Synchronized** |
