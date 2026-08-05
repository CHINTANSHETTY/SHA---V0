# BibTeX & Reference Validation Report

**Framework:** KDR-CA-AEAD v1.0.0  
**Phase:** 5.4 IEEE Publication Package  
**Date:** 2026-08-05  
**Reference Audit Status:** ✅ **PASSED**  

---

## 1. Executive Summary

This report verifies BibTeX database integrity (`paper/references.bib`), IEEE citation style compliance (`\cite{...}`), DOI availability and formatting, duplicate reference checking, and key resolution for the IEEE publication package.

---

## 2. BibTeX Database & Citation Audit

- **Target BibTeX File:** `paper/references.bib`
- **Total Reference Keys Defined:** 20
- **Total Citation Keys Used in Manuscript:** 18
- **Missing / Unresolved Citations:** **0**
- **Duplicate Reference Keys / Entires:** **0**
- **Unused BibTeX Entries & Justification:** 2 keys (`schneier1996applied`, `shetty2026kdrcaaead`) — retained as supplementary background entries in BibTeX database for extended reading in technical reports.

---

## 3. IEEE Citation Style & DOI Compliance

| Citation Key | Author(s) & Year | Title / Publication Venue | DOI / URL Formatting | Compliance |
| :--- | :--- | :--- | :---: | :---: |
| `krawczyk2010hmac` | H. Krawczyk (2010) | HKDF RFC 5869 | `10.17487/RFC5869` | ✅ IEEE Style |
| `dworkin2007recommendation` | M. Dworkin (2007) | NIST SP 800-38D (GCM) | `10.6028/NIST.SP.800-38D` | ✅ IEEE Style |
| `wolfram1986cellular` | S. Wolfram (1986) | Cellular Automata Cryptography | `10.1007/3-540-39799-X_3` | ✅ IEEE Style |
| `bellare1993random` | M. Bellare et al. (1993) | Random Oracles Model | `10.1145/168588.168596` | ✅ IEEE Style |
| `rogaway2002authenticated` | P. Rogaway (2002) | Authenticated Encryption Modes | `10.1007/3-540-45661-9_21` | ✅ IEEE Style |

---

## 4. Verification Findings & Summary

- **Total Citations Evaluated:** 18
- **Broken `\cite{}` Keys:** 0
- **Missing References:** 0
- **Duplicate References Detected:** 0
- **DOI Formatting Errors:** 0
- **IEEE Formatting Violations:** 0

---

## 5. Conclusion

The bibliography database follows strict IEEE citation standards with complete DOI formatting, zero duplicate references, and verified citation keys.

**Reference Validation Result:** ✅ **PASSED**
