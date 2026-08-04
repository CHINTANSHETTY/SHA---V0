# `crypto.analysis` API Reference

**Subsystem:** Security Analysis, Statistical Testing, Benchmarking & Final Validation  
**IEEE Mapping:** Section V, VI, VII  

---

## Overview

The `crypto.analysis` package provides automated statistical randomness testing, cryptographic security assessment, performance benchmarking, camera-ready figure plotting, and reproducibility data exports.

---

## Public Functions

### 1. `crypto.analysis.security_analysis.run_full_security_analysis`

```python
def run_full_security_analysis() -> Dict[str, Any]
```

Executes complete statistical and security suite covering:
- NIST SP 800-22 Monobit and Runs Tests
- Shannon Entropy Profile ($H(X) \ge 7.90$ bits/byte)
- Plaintext and Key Strict Avalanche Criterion (SAC) Bit Flip Ratios (~50.0%)
- Pearson Correlation Coefficient ($r \sim 0.00$)
- Brute-force complexity ($2^{256}$ operations), differential, linear, and related-key attack bounds
- Comparative baseline analysis against AES-256-GCM and ChaCha20-Poly1305

---

### 2. `crypto.analysis.benchmark_runner.run_full_benchmark_suite`

```python
def run_full_benchmark_suite(
    payload_sizes_kb: List[float] = [0.064, 1.0, 10.0, 100.0, 1024.0]
) -> Dict[str, Any]
```

Measures performance metrics across buffer sizes:
- Encryption and Decryption Latency (mean ms, 95% Confidence Intervals)
- Throughput (MB/s)
- Peak Memory Allocation Footprint (KB)
- CPU Microseconds per Byte ($\mu s / B$)
- Scalability Curve

---

### 3. `crypto.analysis.final_validation.verify_end_to_end_pipeline`

```python
def verify_end_to_end_pipeline(master_key: bytes = ...) -> Dict[str, Any]
```

Verifies round-trip encryption correctness, AEAD tag verification, determinism, nonce freshness, and forgery rejection.

---

### 4. `crypto.analysis.final_validation.generate_consolidated_tables`

```python
def generate_consolidated_tables(
    master_results: Dict[str, Any],
    tables_dir: str
) -> Dict[str, str]
```

Exports consolidated IEEE CSV and Markdown tables:
- `master_results_table.csv`
- `security_summary.csv`
- `benchmark_summary.csv`
- `cipher_comparison.csv`
- `cipher_comparison.md`

---

### 5. `crypto.analysis.visualization.generate_all_security_plots` / `generate_all_benchmark_plots`

```python
def generate_all_security_plots(output_dir: str) -> Dict[str, str]: ...
def generate_all_benchmark_plots(output_dir: str, master_results: Dict[str, Any]) -> Dict[str, str]: ...
```

Generates 300 DPI camera-ready PNG and vector SVG publication figures in `results/security_graphs/`.
