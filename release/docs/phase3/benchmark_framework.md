# Phase 3.2 – Large-Scale Benchmark Framework Documentation

## Executive Overview

The **Large-Scale Benchmark Framework** (`crypto/benchmark/`) provides a reproducible, publication-ready benchmarking system for evaluating the **Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)** cryptographic system.

It evaluates throughput (MB/s), execution latency (ms), memory footprint (peak RSS & heap allocations), CPU utilization, and payload scalability across 9 standard message sizes ranging from **1 KB to 100 MB**, while generating fair comparative evaluations against reference ciphers (**AES-128-GCM**, **ChaCha20-Poly1305**, **AES-CTR + HMAC-SHA256**).

---

## 1. Architecture & Execution Sequence

```text
Config Initialization & Metadata Collection
                │
                ▼
Deterministic PRNG Payload Generation (Fixed Seed)
                │
                ▼
    ┌───────────────────────┐
    │ Warm-up Iterations    │ (Discarded from statistics)
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │ Measured Iterations   │ (Latency, Throughput, RSS, Heap, CPU %)
    └───────────┬───────────┘
                │
                ▼
Statistical Aggregation (Mean, Median, P50, P95, P99, Std Dev, 95% CI)
                │
                ▼
Multi-Format Export (CSV, JSON, Markdown, Environment Metadata)
```

---

## 2. Standardized Output Directory Layout

All generated benchmark datasets and reports are exported into a clean, reproducible directory structure:

```text
benchmark_results/
├── csv/
│   └── benchmark_scalability.csv
├── json/
│   └── benchmark_suite_full.json
├── markdown/
│   └── benchmark_tables.md
└── metadata/
    └── environment_metadata.json
```

---

## 3. Statistical Methodology & Metric Definitions

1. **Arithmetic Mean ($\bar{x}$)**:
   $$\bar{x} = \frac{1}{n} \sum_{i=1}^n x_i$$
2. **Standard Deviation ($s$) & Sample Variance ($s^2$)**:
   $$s = \sqrt{\frac{1}{n-1} \sum_{i=1}^n (x_i - \bar{x})^2}$$
3. **95% Confidence Interval (CI)**:
   $$\text{95\% CI} = \bar{x} \pm 1.96 \frac{s}{\sqrt{n}}$$
4. **Latency Percentiles (`p50`, `p95`, `p99`)**: Nearest-rank linear interpolation across sorted trial measurements.
5. **Encryption & Decryption Throughput ($T$)**:
   $$T = \frac{\text{Message Size (Bytes)}}{1024 \times 1024 \times \Delta t \text{ (seconds)}} \quad \text{[MB/s]}$$

---

## 4. Scalability Dimensions & Evaluated Payload Sizes

| Dimension | Payload Size | Bytes |
| :--- | :--- | :--- |
| **Micro-Payload** | 1 KB | `1,024 B` |
| **Small Payload** | 10 KB | `10,240 B` |
| **Medium Payload** | 100 KB | `1024,00 B` |
| **Standard Stream** | 1 MB | `1,048,576 B` |
| **File Block** | 5 MB | `5,242,880 B` |
| **Large Stream** | 10 MB | `10,485,760 B` |
| **High Capacity** | 25 MB | `26,214,400 B` |
| **Enterprise Payload** | 50 MB | `52,428,800 B` |
| **Maximum Benchmark** | 100 MB | `104,857,600 B` |

---

## 5. Fair Comparative Evaluation Rules

All algorithm evaluations enforce strict equality:
- **Identical Payloads**: Generated via deterministic PRNG (`random.Random(seed)`).
- **Identical AAD & Nonce Lengths**: Fixed 12-byte nonces and header metadata.
- **Identical Iterations & Warm-up Steps**: Same trial counts executed in the same process environment.
- **Explicit Engine Labelling**: Native C OpenSSL bindings vs Pure Python CA Engine explicitly documented in all exported reports.

---

## 6. Reproducibility Guide

To run the large-scale benchmark framework and generate IEEE publication outputs:

```bash
# 1. Run new Phase 3.2 benchmark tests
.\venv\Scripts\python.exe -m pytest tests/test_benchmark_runner.py tests/test_benchmark_export.py tests/test_benchmark_metrics.py

# 2. Programmatic execution snippet
python -c "from crypto.benchmark import LargeScaleBenchmarkRunner, BenchmarkExporter; runner = LargeScaleBenchmarkRunner(); suite = runner.run_suite(); BenchmarkExporter().export_all(suite)"
```

---

## 7. Limitations & Recommendations

1. **Execution Time for 100 MB Payloads**: In pure Python, benchmarking 50 MB–100 MB payloads over multiple iterations requires ~15–30 seconds per trial.
2. **Future C Extension Integration**: Compiling CA evolution loops into C/CFFI extensions will enable >1 GB/s throughput benchmarking for multi-gigabyte files.
