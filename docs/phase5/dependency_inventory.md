# KDR-CA-AEAD Phase 5.3: Complete Dependency Inventory

**Author:** Nagamrutha (Security Analysis & Cryptographic Validation Lead)  
**Date:** August 4, 2026  
**Status:** Completed  
**Version:** 1.0.0  

---

## 1. Overview

This document provides a comprehensive inventory of all runtime, development, testing, research, visualization, and build dependencies used in the **KDR-CA-AEAD** cryptographic framework.

---

## 2. Mandatory Runtime Dependencies (`requirements.txt`)

| Package Name | Installed Version | Latest Stable | Purpose / Role | License | Status |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **Flask** | `3.1.3` | `3.1.3` | Web application interface & API routing | BSD-3-Clause | **Compliant** |
| **argon2-cffi** | `25.1.0` | `25.1.0` | Argon2id key derivation & password hashing | MIT | **Compliant** |
| **argon2-cffi-bindings** | `25.1.0` | `25.1.0` | CFFI bindings for Argon2 C implementation | MIT | **Compliant** |
| **cffi** | `2.1.1` | `2.1.1` | Foreign Function Interface for Python | MIT | **Compliant** |

---

## 3. Development, Testing & Code Coverage

| Package Name | Installed Version | Latest Stable | Purpose / Role | License | Status |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **pytest** | `9.1.1` | `9.1.1` | Primary test runner and assertion framework | MIT | **Compliant** |
| **pytest-cov** | `7.1.0` | `7.1.0` | Code coverage measurement plugin | MIT | **Compliant** |
| **coverage** | `7.15.3` | `7.15.3` | Code coverage analysis engine | Apache-2.0 | **Compliant** |
| **pluggy** | `1.6.0` | `1.6.0` | Plugin management framework for pytest | MIT | **Compliant** |

---

## 4. Statistical Analysis & Data Science Subsystems

| Package Name | Installed Version | Latest Stable | Purpose / Role | License | Status |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **numpy** | `2.4.4` | `2.4.4` | Matrix computations & bit vector manipulation | BSD-3-Clause | **Compliant** |
| **scipy** | `1.17.1` | `1.17.1` | NIST SP 800-22 chi-square & statistical tests | BSD-3-Clause | **Compliant** |
| **pandas** | `3.0.2` | `3.0.2` | Benchmark dataset management & CSV exports | BSD-3-Clause | **Compliant** |
| **matplotlib** | `3.10.9` | `3.10.9` | Security graphs, avalanche plots, SAC heatmaps | PSF / BSD | **Compliant** |
| **seaborn** | `0.13.2` | `0.13.2` | Heatmap visualization for correlation matrices | BSD-3-Clause | **Compliant** |

---

## 5. Configuration & Utility Infrastructure

| Package Name | Installed Version | Latest Stable | Purpose / Role | License | Status |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **PyYAML** | `6.0.3` | `6.0.3` | Benchmark configuration parsing (`.yaml`) | MIT | **Compliant** |
| **requests** | `2.33.1` | `2.33.1` | HTTP client for external verification | Apache-2.0 | **Compliant** |
| **certifi** | `2026.4.22` | `2026.4.22` | Root TLS certificates bundle | MPL-2.0 | **Compliant** |
| **click** | `8.3.3` | `8.3.3` | CLI command line parser dependency | BSD-3-Clause | **Compliant** |
| **Werkzeug** | `3.1.8` | `3.1.8` | WSGI utility library for Flask | BSD-3-Clause | **Compliant** |
| **Jinja2** | `3.1.6` | `3.1.6` | Template engine for web dashboard rendering | BSD-3-Clause | **Compliant** |
| **MarkupSafe** | `3.0.3` | `3.0.3` | HTML string sanitization for Jinja2 | BSD-3-Clause | **Compliant** |
| **itsdangerous** | `2.2.0` | `2.2.0` | Cryptographic signing for Flask sessions | BSD-3-Clause | **Compliant** |

---

## 6. Standard Library Cryptographic & System Modules

The core cryptographic algorithms (HKDF-SHA256, Cellular Automata state permutations, HMAC-SHA256 CTR-PRNG) execute strictly using CPython standard library modules:

| Standard Module | Purpose | Status |
| :--- | :--- | :---: |
| **`hashlib`** | Cryptographic hash primitives (`hashlib.sha256`, `hashlib.sha512`) | Built-in |
| **`hmac`** | Keyed-hash message authentication code (`hmac.new`, `compare_digest`) | Built-in |
| **`secrets` / `os.urandom`** | Cryptographically secure pseudo-random number generator (CSPRNG) | Built-in |
| **`struct`** | Binary byte packing and unpacking | Built-in |
| **`pathlib` / `os.path`** | Cross-platform file path resolution | Built-in |
| **`json` / `dataclasses`** | Schema serialization and structured data modeling | Built-in |
