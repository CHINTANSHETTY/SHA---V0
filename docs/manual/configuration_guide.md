# KDR-CA-AEAD Configuration Guide

**Project:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Version:** 1.0.0  

---

## 1. Project Configuration Schemas

### 1. Benchmark Plotting Configuration (`scripts/benchmark_config.yaml`)
Configures graph export resolutions, color palettes, DPI, and typography:
```yaml
output_dir: "docs/graphs"
dpi: 300
vector_format: "pdf"
raster_format: "png"
source_format: "svg"

colors:
  primary: "#002B49"       # IEEE Navy
  secondary: "#1F77B4"     # IEEE Blue
  success: "#2CA02C"       # Emerald Green
  warning: "#FF7F0E"       # Amber
  purple: "#9467BD"        # Royal Purple

fonts:
  sans_serif: ["DejaVu Sans", "Arial", "Helvetica"]
```

### 2. API Documentation Configuration (`docs/api/config/docs_config.json`)
Configures API doc generator metadata:
```json
{
  "project_name": "KDR-CA-AEAD Cryptographic Research Framework",
  "version": "1.0.0",
  "authors": ["Chintan Shetty", "Amrutha Nagamrutha", "Ashwitha"],
  "license": "MIT",
  "repository": "https://github.com/CHINTANSHETTY/SHA---V0"
}
```

---

## 2. Environment Variables

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `PYTHONPATH` | `.` | Python module search path. Must include project root. |
| `PAGER` | `cat` | Terminal pagination override for non-interactive execution. |

---

## 3. Cryptographic Default Constants

Defined in `crypto/constants.py`:
- **Master Key Length**: 32 bytes (256 bits).
- **Default Salt Length**: 16 bytes (128 bits).
- **Default Nonce Length**: 12 bytes (96 bits).
- **HMAC Tag Length**: 32 bytes (256 bits).
- **Default CA Rule Offset ($\delta$)**: 13 (dual-rule prime offset).
- **Initial Feedback IV**: `0xC5` (256-bit feedback initialization vector).
