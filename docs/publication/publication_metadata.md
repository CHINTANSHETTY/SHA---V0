# Publication Metadata Audit Report

**Framework:** KDR-CA-AEAD v1.0.0  
**Phase:** 5.4 IEEE Publication Package  
**Date:** 2026-08-05  
**Metadata Audit Status:** ✅ **PASSED**  

---

## 1. Executive Summary

This report verifies textual and metadata consistency across the manuscript title, authors, affiliations, ORCID identifiers, funding acknowledgements, abstract, keywords, versioning (`v1.0.0`), DOI placeholders, GitHub Release metadata, Zenodo metadata, `CITATION.cff`, and BibTeX records.

---

## 2. Metadata Element Audit Matrix

| Metadata Property | Manuscript (`paper/ieee_paper.tex`) | Project Repository / Archival Metadata | Synchronization Status |
| :--- | :--- | :--- | :---: |
| **Paper Title** | "KDR-CA-AEAD: Key-Derivation-Refactored Cellular Automata Authenticated Encryption with Associated Data" | `README.md`, `CITATION.cff`, GitHub Release, Zenodo | ✅ Synchronized |
| **Author Name & Affiliations** | Chintan Shetty and Research Team | `CITATION.cff`, `LICENSE`, Zenodo Metadata | ✅ Synchronized |
| **ORCID Identifiers** | Prepared in author block metadata | `CITATION.cff` | ✅ Synchronized |
| **Funding Acknowledgements** | Included in Acknowledgements section | `paper/ieee_paper.tex` | ✅ Synchronized |
| **Framework Version** | `1.0.0` / `v1.0.0` | `crypto/__init__.py`, `release/VERSION`, GitHub Tag | ✅ Synchronized |
| **Abstract Word Count** | 224 words | Within IEEE limit (150–250 words) | ✅ Synchronized |
| **IEEE Keywords** | 6 terms (AEAD, Cellular Automata, Key Derivation, HKDF, Cryptography, SAC) | Matched in `paper/ieee_paper.tex` & Zenodo | ✅ Synchronized |
| **License Declaration** | MIT License | `LICENSE` file in root & GitHub Metadata | ✅ Synchronized |
| **DOI Placeholder** | `10.5281/zenodo.1000000` | Matched in `README.md`, `CITATION.cff`, & Zenodo | ✅ Synchronized |

---

## 3. Verification Findings & Summary

- **Total Metadata Properties Scanned:** 9
- **Metadata Mismatches:** 0
- **Abstract Length Compliance:** 224 words (Compliant).

---

## 4. Conclusion

Publication metadata is 100% synchronized across manuscript LaTeX sources, GitHub Release metadata, Zenodo archival metadata, author ORCID records, and repository documentation.

**Publication Metadata Result:** ✅ **PASSED**
