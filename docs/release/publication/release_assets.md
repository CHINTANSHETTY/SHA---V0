# Release Asset Verification Report

**Framework:** KDR-CA-AEAD v1.0.0  
**Phase:** 5.5 Repository Publication & Release  
**Date:** 2026-08-05  
**Release Asset Status:** ✅ **PASSED**  

---

## 1. Executive Summary

This report documents the physical integrity, manifest accounting (`release_manifest.json`), archive extraction testing, file permissions check, and SHA-256 / SHA-512 cryptographic hash checksum verification for all official publication release packages under `release/`.

---

## 2. Publication Asset Inventory & Cryptographic Hashes

| Release Asset File | Category | Size (KB) | SHA-256 Checksum Digest | Manifest Match & Permissions |
| :--- | :--- | :---: | :--- | :---: |
| `kdr-ca-aead-v1.0.0.zip` | Source & Distribution Package | 7,768.03 KB | `ad3944c003e26c36bda53d5034716f10511d6e34bc3b8c8101a233b2238f017d` | ✅ 1-to-1 Match / Valid Permissions |
| `kdr-ca-aead-v1.0.0.tar.gz` | Source Tarball Package | 7,525.53 KB | `8e5a42d0951dbdadc9d920d16f428b9346ad1a13d0ef81c5ceb55ddc19edf22d` | ✅ 1-to-1 Match / Valid Permissions |
| `documentation-v1.0.0.zip` | Documentation Package | 6,441.20 KB | `073830d4f4a40a2da77e65b8dceeb82319defc3c51d82a2d2783b6f81f99222d` | ✅ 1-to-1 Match / Valid Permissions |
| `paper-v1.0.0.zip` | IEEE Paper & LaTeX Bundle | 991.05 KB | `c867226f6d13d04c9e6aba1dddaa803951b2f71bad7441bb32485d4f2e8b65da` | ✅ 1-to-1 Match / Valid Permissions |
| `benchmarks-v1.0.0.zip` | Benchmark Datasets Bundle | 1,005.49 KB | `505c59a41e1fde180494cfc57eceb78aa92e2b2fe9a7d781073a973489c2aa98` | ✅ 1-to-1 Match / Valid Permissions |
| `complete-release-v1.0.0.zip` | Monolithic Release Package | 8,710.80 KB | `36a827b16c20554966b6822978c827c62472ff6cba8cf51fb2a3bb7a4dc0b0be` | ✅ 1-to-1 Match / Valid Permissions |

---

## 3. Verification Findings & Summary

- **Total Distribution Packages Verified:** 6
- **Manifest Listing vs Physical Files:** 100% 1-to-1 correspondence with `release_manifest.json`.
- **Extraction Test Errors:** 0
- **Extracted File Permissions Audit:** Valid read/execute flags across Python modules and scripts.
- **Checksum Hash Mismatches:** 0

---

## 4. Conclusion

All publication release packages are verified as complete, uncorrupted, extractable with valid permissions, and cryptographically signed with matching SHA-256 and SHA-512 digests.

**Release Asset Validation Result:** ✅ **PASSED**
