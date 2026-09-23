# Installation & Setup Guide

This document provides step-by-step installation instructions for setting up **KDR-CA-AEAD** on Windows, Linux, and macOS environments.

---

## System Prerequisites

| Requirement | Minimum Version | Recommended |
| :--- | :--- | :--- |
| **Python** | 3.10+ | Python 3.11 / 3.12 / 3.13 |
| **Git** | 2.25+ | Latest |
| **Package Manager** | `pip` 22.0+ | Latest `pip` |
| **RAM** | 512 MB | 2 GB+ |
| **OS** | Windows 10/11, Ubuntu 20.04+, macOS 12+ | Any 64-bit OS |

---

## Quick Start Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CHINTANSHETTY/SHA---V0.git
cd SHA---V0
```

### 2. Create & Activate Virtual Environment (Recommended)

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### On Linux / macOS (Bash):
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the minimal production dependencies:
```bash
pip install -r requirements.txt
```

Optionally install the package in editable mode:
```bash
pip install -e .
```

---

## Post-Installation Verification

To verify that the installation was successful and all cryptographic modules function correctly:

### 1. Set `PYTHONPATH`

#### On Windows (PowerShell):
```powershell
$env:PYTHONPATH="."
```

#### On Linux / macOS:
```bash
export PYTHONPATH="."
```

### 2. Execute Automated Test Suite

Run the full pytest suite (over 400 unit and integration tests):
```bash
python -m pytest
```

Expected output:
```text
============================= 401 passed in 12.45s =============================
```

### 3. Run Python Smoke Test

```python
from crypto import encrypt_bytes, decrypt_bytes

key = b"0123456789abcdef0123456789abcdef"  # 32-byte key
msg = b"Hello, KDR-CA-AEAD!"

package = encrypt_bytes(msg, key)
decrypted = decrypt_bytes(package, key)

assert decrypted == msg
print("SUCCESS: KDR-CA-AEAD installation verified!")
```

---

## Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `PYTHONPATH` | `.` | Module resolution path for local execution |
| `FLASK_ENV` | `production` | Environment mode for web application (`app.py`) |
| `DATABASE_PATH` | `records.db` | SQLite database file location for Web UI |

---

## Troubleshooting Installation Issues

- **Python Binary Not Found**: Ensure Python is added to your system `PATH`. On Windows, try using `py -m pip install -r requirements.txt`.
- **Permission Errors**: Avoid installing globally without virtual environments. Use `python -m venv venv`.
- **Import Error `No module named crypto`**: Set `PYTHONPATH=.` in your terminal prior to running python scripts.
