# KDR-CA-AEAD Installation Guide

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  

---

## 1. Prerequisites

### Python Environment
- **Python Version**: Python 3.10+ (tested on Python 3.13.5 64-bit).
- **Package Manager**: `pip` (Python package installer).

### Operating System Support
- **Windows**: Windows 10 / Windows 11 (PowerShell or Command Prompt).
- **Linux**: Ubuntu 20.04+ / Debian 11+ / RHEL 8+ (bash / zsh).
- **macOS**: macOS Monterey (12.0+) / Ventura / Sonoma (zsh / bash).

---

## 2. Project Cloning & Virtual Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0-main
```

### 2. Set PYTHONPATH Variable
- **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="."
  ```
- **Windows (CMD)**:
  ```cmd
  set PYTHONPATH=.
  ```
- **Linux / macOS**:
  ```bash
  export PYTHONPATH="."
  ```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install pytest reportlab fpdf2 matplotlib pyyaml pillow jinja2
```

---

## 3. Installation Verification

Verify the installation by running the full test suite:
```powershell
$env:PYTHONPATH="."
python -m pytest
```

Expected output: `18 passed in 15.00s`.
