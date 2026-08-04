# Documentation Navigation Map

This navigation map provides a structured overview of all documentation, research specifications, API references, user manuals, and reproducibility assets in the **KDR-CA-AEAD** repository.

---

## Role-Based Quick Paths

```text
┌────────────────────────┐    ┌────────────────────────┐    ┌────────────────────────┐
│     End User Path      │    │     Developer Path     │    │     Reviewer Path      │
├────────────────────────┤    ├────────────────────────┤    ├────────────────────────┤
│ 1. installation.md     │    │ 1. developer_guide.md  │    │ 1. reproducibility.md  │
│ 2. user_guide.md       │    │ 2. api_reference.md    │    │ 2. benchmark_guide.md  │
│ 3. troubleshooting.md  │    │ 3. architecture.md     │    │ 3. security_guide.md   │
└────────────────────────┘    └────────────────────────┘    └────────────────────────┘
```

---

## Primary Deliverables (`docs/`)

| Document | Purpose |
| :--- | :--- |
| **[index.md](index.md)** | Main Documentation Hub and project overview |
| **[navigation.md](navigation.md)** | Role-based reading paths and file directory map |
| **[installation.md](installation.md)** | Installation, prerequisites, environment setup, and verification |
| **[developer_guide.md](developer_guide.md)** | Codebase layout, testing standards, and development guidelines |
| **[user_guide.md](user_guide.md)** | End-to-end Python API, CLI, and Web Application user guide |
| **[api_reference.md](api_reference.md)** | Detailed API module specifications and HTTP endpoints |
| **[architecture.md](architecture.md)** | Cryptographic architecture, pipeline components, and state models |
| **[benchmark_guide.md](benchmark_guide.md)** | Performance benchmarking suite, metrics, and comparative analysis |
| **[security_guide.md](security_guide.md)** | Threat model, cryptographic security bounds, and SAC validation |
| **[reproducibility.md](reproducibility.md)** | Automated reproducibility pipeline and IEEE publication artifact generation |
| **[troubleshooting.md](troubleshooting.md)** | Common issues, environment diagnostics, and FAQs |

---

## Complete Repository Documentation Inventory

### Core & Root Files
- **[README.md](../README.md)**: Main GitHub landing page and quick-start guide.
- **[CONTRIBUTING.md](../CONTRIBUTING.md)**: Open-source contribution guidelines.
- **[CHANGELOG.md](../CHANGELOG.md)**: Release version history (v1.0.0).
- **[LICENSE](../LICENSE)**: Apache 2.0 open-source license.
- **[CITATION.cff](../CITATION.cff)**: Machine-readable academic citation metadata.

### API & Modules (`docs/api/`)
- **[overview.md](api/overview.md)**: High-level API overview and integration guide.
- **[crypto_engine.md](api/crypto_engine.md)**: API docs for `crypto.engine`.
- **[crypto_ca.md](api/crypto_ca.md)**: API docs for 1D Cellular Automata engine.
- **[crypto_analysis.md](api/crypto_analysis.md)**: API docs for security analysis and benchmarking tools.
- **[api_manifest.md](api/api_manifest.md)**: Structured API manifest listing all functions and signatures.

### Architecture & Specs (`docs/architecture/`, `docs/algorithms/`)
- **[system_architecture.md](architecture/system_architecture.md)**: Complete system design spec.
- **[pseudocode.md](algorithms/pseudocode.md)**: Mathematical pseudocode for KDR-CA-AEAD.

### Manuals & User Guides (`docs/manual/`)
- **[user_manual.md](manual/user_manual.md)**: Manual covering CLI and Web App.
- **[installation_guide.md](manual/installation_guide.md)**: Standalone installation manual.
- **[configuration_guide.md](manual/configuration_guide.md)**: Configuration flags and environment variables.
- **[operations_guide.md](manual/operations_guide.md)**: Operational security and deployment manual.
- **[quick_reference.md](manual/quick_reference.md)**: Quick syntax reference sheet.

### Phase 3 & Benchmarking (`docs/phase3/`)
- **[benchmark_framework.md](phase3/benchmark_framework.md)**: Benchmarking framework architecture.
- **[performance.md](phase3/performance.md)**: Performance evaluation results.
- **[statistical_validation.md](phase3/statistical_validation.md)**: Statistical battery and SAC validation.

### Research & IEEE Publication Package (`docs/research/`)
- **[PROJECT_MASTER_DOCUMENT.md](research/PROJECT_MASTER_DOCUMENT.md)**: Comprehensive master project doc.
- **[ieee_paper_draft_phase2_6.md](research/ieee_paper_draft_phase2_6.md)**: Camera-ready paper draft.
- **[ieee_cryptographic_audit.md](research/ieee_cryptographic_audit.md)**: IEEE cryptographic audit report.
- **[ieee_peer_review_audit.md](research/ieee_peer_review_audit.md)**: Formal peer review response and resolution log.
- **[threat_model.md](research/threat_model.md)**: Formal threat model and adversary security levels.
- **[slr_verification_and_validation.md](research/slr_verification_and_validation.md)**: Systematic literature review V&V.

### Release & Publication Readiness (`docs/release/`)
- **[publication_readiness.md](release/publication_readiness.md)**: IEEE publication readiness check.
- **[release_manifest.md](release/release_manifest.md)**: Complete release file manifest.
- **[reproducibility_report.md](release/reproducibility_report.md)**: Automated reproducibility verification report.
