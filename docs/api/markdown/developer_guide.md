# KDR-CA-AEAD Developer Guide & Reproducibility Reference

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  
**Authors:** Chintan Shetty, Amrutha Nagamrutha, Ashwitha  

---

## 1. Environment Setup & Installation

### Requirements
- **Python**: Version 3.10+ (tested on Python 3.13.5 64-bit).
- **Core Dependencies**: `pytest`, `reportlab`, `fpdf2`, `matplotlib`, `pyyaml`, `pillow`, `jinja2`.

### Installation Steps
```powershell
# Clone repository
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0-main

# Set PYTHONPATH environment variable
$env:PYTHONPATH="."

# Install required dependencies
python -m pip install pytest reportlab fpdf2 matplotlib pyyaml pillow jinja2
```

---

## 2. Directory Architecture

```text
c:\Users\shett\Downloads\SHA---V0-main/
├── crypto/
│   ├── ca/                    # Cellular Automata Engine & Wolfram Rule Mapping
│   ├── engine/                # Encrypt, Decrypt, Dynamic CA & Key Schedule
│   ├── models/                # EncryptedPackage & Custom Exception Classes
│   ├── primitives/            # HKDF-SHA256, HMAC-SHA256, CSPRNG Randomness
│   └── analysis/              # Security Validation & Benchmark Framework
├── docs/
│   ├── api/                   # HTML, PDF, Markdown & API Build Tools
│   ├── figures/               # Architecture Vector Graphics & Diagrams
│   └── graphs/                # Benchmark Visualizations & Performance Analytics
├── paper/                     # Master IEEE LaTeX Manuscript & Compiler
├── scripts/                   # Figure & Graph Generation Tooling
└── tests/                     # Unit, Integration, & End-to-End Test Suite
```

---

## 3. Extending the Framework

To extend KDR-CA-AEAD with additional cellular automata rules or alternative AEAD MAC schemes:
1. Extend `crypto/ca/rules.py` by registering custom 8-bit Wolfram rule mappings.
2. Extend `crypto/engine/dynamic_ca.py` by implementing a new forward/inverse permutation chain class implementing `DynamicCAEngine`.
3. Register the new engine variant in `crypto/__init__.py` and add unit test cases under `tests/unit/`.

---

## 4. Running Verification & Benchmarks

### Executing Full Pytest Suite
```powershell
$env:PYTHONPATH="."
python -m pytest
```

### Running Security Analysis & Randomness Suite
```powershell
$env:PYTHONPATH="."
python -c "from crypto.analysis.final_validation import run_full_security_analysis; run_full_security_analysis()"
```

### Building IEEE LaTeX Paper
```powershell
$env:PYTHONPATH="."
python paper/build_paper.py
```

### Regenerating Figures & Graphs
```powershell
$env:PYTHONPATH="."
python scripts/generate_architecture_figures.py
python scripts/generate_benchmark_graphs.py
python docs/api/build_api_docs.py
```
