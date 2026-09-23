"""
Module:
    benchmark_export.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Data Serialization and Export Subsystem for Phase 2.4 Performance Benchmarking.
    Exports master benchmark metrics into JSON and CSV file formats.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)

IEEE Mapping:
    Section VI-D – Raw Benchmark Datasets & Data Artifacts
"""

from __future__ import annotations

import csv
import json
import os
from typing import Any, Dict, List


def export_results_to_json(master_results: Dict[str, Any], output_path: str) -> str:
    """Exports master benchmark results dictionary to JSON format.

    Args:
        master_results: Benchmark metrics dictionary.
        output_path: Target file path for the JSON output.

    Returns:
        Absolute filepath of created JSON file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(master_results, f, indent=2)
    return os.path.abspath(output_path)


def export_results_to_csv(master_results: Dict[str, Any], output_path: str) -> str:
    """Exports cipher benchmark metrics to a tabular CSV dataset.

    Args:
        master_results: Benchmark metrics dictionary.
        output_path: Target file path for the CSV output.

    Returns:
        Absolute filepath of created CSV file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    headers = [
        "Algorithm",
        "Payload_Size_Bytes",
        "Payload_Size_KB",
        "Payload_Size_MB",
        "Enc_Mean_ms",
        "Enc_StdDev_ms",
        "Enc_Min_ms",
        "Enc_Max_ms",
        "Enc_Throughput_MBps",
        "Enc_us_per_byte",
        "Enc_Peak_Memory_KB",
        "Dec_Mean_ms",
        "Dec_StdDev_ms",
        "Dec_Min_ms",
        "Dec_Max_ms",
        "Dec_Throughput_MBps",
        "Dec_us_per_byte",
        "Dec_Peak_Memory_KB",
    ]

    rows: List[List[Any]] = []
    ciphers_dict = master_results.get("ciphers", {})

    for cipher_key, cipher_evals in ciphers_dict.items():
        for entry in cipher_evals:
            alg = entry.get("algorithm", cipher_key)
            sz_bytes = entry.get("payload_size_bytes", 0)
            sz_kb = entry.get("payload_size_kb", 0.0)
            sz_mb = entry.get("payload_size_mb", 0.0)

            enc = entry.get("encryption", {})
            dec = entry.get("decryption", {})

            rows.append(
                [
                    alg,
                    sz_bytes,
                    sz_kb,
                    sz_mb,
                    enc.get("mean_ms", 0.0),
                    enc.get("std_dev_ms", 0.0),
                    enc.get("min_ms", 0.0),
                    enc.get("max_ms", 0.0),
                    enc.get("throughput_mb_per_sec", 0.0),
                    enc.get("us_per_byte", 0.0),
                    enc.get("peak_memory_kb", 0.0),
                    dec.get("mean_ms", 0.0),
                    dec.get("std_dev_ms", 0.0),
                    dec.get("min_ms", 0.0),
                    dec.get("max_ms", 0.0),
                    dec.get("throughput_mb_per_sec", 0.0),
                    dec.get("us_per_byte", 0.0),
                    dec.get("peak_memory_kb", 0.0),
                ]
            )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return os.path.abspath(output_path)
