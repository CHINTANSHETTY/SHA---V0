# DEPENDENCY PRESERVATION MANIFEST — KDR-CA-AEAD v1.0.0

**Project Name:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Release Tag:** `v1.0.0`  
**Baseline Python Interpreter:** CPython 3.12.5 (64-bit)  
**Document Purpose:** Complete dependency preservation specification and environment snapshot for long-term build reproducibility.

---

## 1. Environment Snapshot (`pip freeze`)

Below is the complete, pinned dependency graph captured from the verified release build environment:

```text
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
blinker==1.9.0
cffi==2.1.1
click==8.4.2
colorama==0.4.6
contourpy==1.3.3
cryptography==50.0.0
cycler==0.12.1
Flask==3.1.3
fonttools==4.63.0
iniconfig==2.3.0
itsdangerous==2.2.0
Jinja2==3.1.6
kiwisolver==1.5.0
MarkupSafe==3.0.3
matplotlib==3.11.1
numpy==2.5.1
packaging==26.3
pandas==3.0.5
pillow==12.3.0
pluggy==1.6.0
pycparser==3.0
Pygments==2.20.0
pyparsing==3.3.2
pytest==9.1.1
python-dateutil==2.9.0.post0
scipy==1.18.0
six==1.17.0
tzdata==2026.3
Werkzeug==3.1.8
```

---

## 2. Python Runtime Compatibility Matrix

| Python Version | Status | Notes |
| :--- | :--- | :--- |
| **Python 3.10** | ✅ Supported | Tested with `cryptography >= 41.0.0` |
| **Python 3.11** | ✅ Supported | Full bytecode optimization enabled |
| **Python 3.12** | 🌟 Primary Baseline | **CPython 3.12.5 (64-bit)** |
| **Python 3.13** | ✅ Supported | Tested with `cffi >= 2.1.1` |

---

## 3. Platform & Operating System Compatibility

| Operating System | Compiler / Build Tool | Compatibility Status |
| :--- | :--- | :--- |
| **Windows 11 (64-bit)** | MSVC 2022 / Windows SDK | 🌟 Primary Build Target |
| **Ubuntu 22.04 LTS** | GCC 11.4 / Clang 14 | ✅ Tested & Certified |
| **macOS 14 (Sonoma)** | Apple Clang 15 (ARM64 & x86_64) | ✅ Tested & Certified |

---

## 4. Hardware & C-Extension Requirements

- **CPU Architecture**: x86_64 or AArch64 (ARM64).
- **Instruction Sets**: Standard SSE2 / AVX2 (Optional for NumPy / SciPy acceleration).
- **C-Compiler Requirements**: Required only if building `cffi` or `cryptography` from source (`gcc`, `clang`, or MSVC Build Tools).

---

## 5. Offline Package Archival & Reinstallation

To guarantee buildability even if PyPI is unavailable in the future, pre-download all wheel packages into a local cache directory:

### Step 5.1: Download Local Wheel Cache
```bash
pip download -r requirements.txt pytest flask argon2-cffi cffi cryptography matplotlib numpy scipy pandas -d ./wheels_cache
```

### Step 5.2: Install from Offline Cache
```bash
pip install --no-index --find-links=./wheels_cache -r requirements.txt pytest flask argon2-cffi cffi cryptography matplotlib numpy scipy pandas
```
