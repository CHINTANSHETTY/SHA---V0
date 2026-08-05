# Long-Term Archival Manifest - KDR-CA-AEAD v1.0.0

This manifest details the archival package inventory, checksum references, metadata schemas, and preservation paths for long-term storage of **KDR-CA-AEAD v1.0.0** on Zenodo, Software Heritage, and institutional repositories.

---

## 1. Primary Release Bundles & Inventory

| Archive File Name | Size (KB) | Purpose & Contents |
| :--- | :--- | :--- |
| **`SHA---V0-v1.0.0.zip`** | ~8,845 KB | Master release bundle containing full source code, docs, tests, and benchmarks. |
| **`complete-release-v1.0.0.zip`** | ~8,845 KB | Complete release snapshot including all dataset reports and LaTeX paper files. |
| **`kdr-ca-aead-v1.0.0.zip`** | ~7,903 KB | Standard software source code archive for pip / manual installation. |
| **`kdr-ca-aead-v1.0.0.tar.gz`** | ~7,620 KB | POSIX gzipped tarball source archive. |
| **`documentation-v1.0.0.zip`** | ~6,551 KB | Complete documentation hub (`docs/`), specifications, and user guides. |
| **`paper-v1.0.0.zip`** | ~991 KB | IEEE paper LaTeX source, vector figures (`.svg`/`.pdf`), and reference `.bib`. |
| **`benchmarks-v1.0.0.zip`** | ~1,005 KB | Benchmark code, SAC evaluator, raw CSV reports, and visualization scripts. |

---

## 2. Archival Metadata Standards

1. **`CITATION.cff`**: Schema Version 1.2.0 for automated academic citation extraction.
2. **`codemeta.json`**: Schema Version 2.0 (CodeMeta standard compliant) for Software Heritage cataloging.
3. **`release_manifest.json`**: Machine-readable JSON manifest containing file trees, build environment snapshots, and cryptographic hashes.

---

## 3. Preservation & Reproducibility Guarantees

- **Permanent DOI Binding**: Zenodo integration guarantees permanent storage with DOI `10.5281/zenodo.1000000`.
- **Software Heritage SWHID**: Complete repository git tree archived under Software Heritage persistent identifiers.
- **Environment Snapshot**: Python runtime (Python 3.10+), OS metadata, dependency lock files (`requirements.txt`), and PRNG seeds ($42$) frozen in `release/environment_snapshot.json`.
- **Hash Integrity**: All archives validated against SHA-256 and SHA-512 master checksum lists (`CHECKSUMS.sha256`, `checksums_sha256.txt`, `checksums_sha512.txt`).
