# Digital Preservation Manifest - KDR-CA-AEAD v1.0.0

**Status:** **ARCHIVAL PRESERVED**  
**Preservation Date:** 2026-08-04  
**Next Preservation Review Date:** 2027-08-04 (Annual Review Schedule)  
**Character Encoding Standard:** UTF-8 (Strict Plain-Text Standard)  
**Fixity Algorithms Used:** SHA-256 & SHA-512 Cryptographic Hashing  

---

## Compression & Packaging Formats

1. `.zip`: DEFLATE compression algorithm (RFC 1951 / ZIP Specification 6.3.9).
2. `.tar.gz`: GZIP compression algorithm (RFC 1952) wrapping TAR POSIX ustar stream.

---

## Archival Storage Guidelines

1. **Replication Factor**: Minimum 3 geographic mirrors (GitHub, Zenodo, University Repository).
2. **Fixity Verification**: Run `python scripts/build_distribution.py` or verify hashes in `release/checksums_sha256.txt`.
3. **Format Stability**: Uses standard open non-proprietary file formats.
