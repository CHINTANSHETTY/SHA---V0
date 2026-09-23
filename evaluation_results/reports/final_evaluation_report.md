# Phase 4.2 Comprehensive Evaluation Report: KDR-CA-AEAD

## I. Benchmarking & Scalability Performance Summary

Performance benchmarks evaluated execution latency, throughput scaling, memory allocation, and CPU computation across target payload buffer sizes.

| Payload Size | Enc Latency Mean (ms) | 95% CI Margin (ms) | Enc Throughput (MB/s) | Dec Throughput (MB/s) | Peak Memory (KB) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.0 KB** | `13.6306 ms` | `±0.7970 ms` | **`0.07 MB/s`** | **`0.07 MB/s`** | `8.03 KB` |
| **10.0 KB** | `177.1270 ms` | `±8.7910 ms` | **`0.06 MB/s`** | **`0.05 MB/s`** | `62.08 KB` |
| **100.0 KB** | `1674.6880 ms` | `±146.3396 ms` | **`0.06 MB/s`** | **`0.06 MB/s`** | `601.94 KB` |

---

## II. Comparative Benchmark Evaluation

| Cipher Algorithm | Payload Size | Enc Throughput (MB/s) | Dec Throughput (MB/s) | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **AES-128-GCM** | `100.0 KB` | `1643.39 MB/s` | `1931.66 MB/s` | `0.0689 ms` |
| **ChaCha20-Poly1305** | `100.0 KB` | `1033.26 MB/s` | `1053.02 MB/s` | `0.0964 ms` |
| **AES-CTR+HMAC-SHA256** | `100.0 KB` | `4.41 MB/s` | `4.36 MB/s` | `22.2919 ms` |
