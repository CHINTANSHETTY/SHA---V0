"""Bit Independence Criterion (BIC) and Differential Cryptanalysis Analysis.

This module provides `BICAnalyzer` and `DifferentialAnalyzer` for evaluating output bit pair correlation
independence and differential propagation behavior.
"""

import math
from typing import Any, Dict, List, Optional, Tuple


class BICAnalyzer:
    """Bit Independence Criterion (BIC) Analyzer."""

    def __init__(self, aead_engine: Optional[Any] = None) -> None:
        """Initialize BICAnalyzer."""
        self._aead_engine = aead_engine
        self._bic_matrix: List[List[float]] = []

    def _get_engine(self) -> Any:
        if self._aead_engine is None:
            from crypto.primitives.aead import AEADEngine
            self._aead_engine = AEADEngine()
        return self._aead_engine

    def analyze(
        self,
        master_key: bytes,
        plaintext: bytes,
        nonce: Optional[bytes] = None,
        samples: int = 50,
    ) -> Dict[str, Any]:
        """Compute pairwise Bit Independence Criterion (BIC) correlation matrix.

        Measures Pearson correlation coefficients r_ij between changes in output bits i and j.
        Ideal target: r_ij ≈ 0.0 (independent bit changes).

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext bytes payload.
            nonce: Optional nonce bytes.
            samples: Number of 1-bit input flip trials.

        Returns:
            Dict[str, Any]: BIC correlation matrix and independence score.
        """
        engine = self._get_engine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)

        base_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)
        base_ct = base_res["ciphertext"] + base_res["tag"]
        out_bits_count = min(64, len(base_ct) * 8)  # Sample up to 64 output bits for efficiency

        num_trials = min(samples, len(m_key) * 8)
        change_vectors: List[List[int]] = [[] for _ in range(out_bits_count)]

        for bit_i in range(num_trials):
            byte_idx = bit_i // 8
            bit_idx = bit_i % 8

            mod_key = bytearray(m_key)
            mod_key[byte_idx] ^= (1 << (7 - bit_idx))

            mod_res = engine.encrypt(pt_bytes, master_key=bytes(mod_key), nonce=base_res["nonce"], check_nonce_reuse=False)
            mod_ct = mod_res["ciphertext"] + mod_res["tag"]

            for out_j in range(out_bits_count):
                out_byte = out_j // 8
                out_bit = out_j % 8
                b1 = (base_ct[out_byte] >> (7 - out_bit)) & 1
                b2 = (mod_ct[out_byte] >> (7 - out_bit)) & 1
                change_vectors[out_j].append(1 if b1 != b2 else 0)

        matrix: List[List[float]] = []
        sum_corr = 0.0
        pair_count = 0

        for i in range(out_bits_count):
            row: List[float] = []
            v_i = change_vectors[i]
            mean_i = sum(v_i) / len(v_i) if v_i else 0.0

            for j in range(out_bits_count):
                if i == j:
                    row.append(1.0)
                    continue

                v_j = change_vectors[j]
                mean_j = sum(v_j) / len(v_j) if v_j else 0.0

                num = sum((v_i[k] - mean_i) * (v_j[k] - mean_j) for k in range(len(v_i)))
                den_i = sum((v_i[k] - mean_i) ** 2 for k in range(len(v_i)))
                den_j = sum((v_j[k] - mean_j) ** 2 for k in range(len(v_j)))
                den = math.sqrt(den_i * den_j)

                r = num / den if den > 0 else 0.0
                row.append(round(r, 6))

                if i < j:
                    sum_corr += abs(r)
                    pair_count += 1

            matrix.append(row)

        self._bic_matrix = matrix
        avg_corr = (sum_corr / pair_count) if pair_count > 0 else 0.0
        independence_score = max(0.0, 1.0 - avg_corr)

        return {
            "output_bits_evaluated": out_bits_count,
            "trials": num_trials,
            "average_correlation": round(avg_corr, 6),
            "independence_score": round(independence_score, 6),
            "correlation_matrix": matrix,
            "passed": avg_corr < 0.20,
        }

    def export_results(self, format: str = "dict") -> Any:
        """Export BIC correlation matrix."""
        if format.lower() == "matrix":
            return self._bic_matrix
        return {"size": len(self._bic_matrix), "matrix": self._bic_matrix}


class DifferentialAnalyzer:
    """Differential Cryptanalysis and Differences Propagation Analyzer."""

    def __init__(self, aead_engine: Optional[Any] = None) -> None:
        """Initialize DifferentialAnalyzer."""
        self._aead_engine = aead_engine

    def _get_engine(self) -> Any:
        if self._aead_engine is None:
            from crypto.primitives.aead import AEADEngine
            self._aead_engine = AEADEngine()
        return self._aead_engine

    def compare(self, ct1: bytes, ct2: bytes) -> Dict[str, Any]:
        """Compare two ciphertexts and calculate XOR difference statistics.

        Args:
            ct1: First ciphertext bytes.
            ct2: Second ciphertext bytes.

        Returns:
            Dict[str, Any]: XOR difference statistics.
        """
        diff_bytes = bytes(a ^ b for a, b in zip(ct1, ct2))
        changed_bits = sum(bin(b).count("1") for b in diff_bytes)
        total_bits = min(len(ct1), len(ct2)) * 8
        ratio = changed_bits / total_bits if total_bits > 0 else 0.0

        return {
            "total_bits": total_bits,
            "changed_bits": changed_bits,
            "difference_ratio": round(ratio, 6),
            "difference_percent": round(ratio * 100.0, 2),
            "diff_bytes": diff_bytes,
        }

    def analyze(
        self,
        master_key: bytes,
        plaintext: bytes,
        delta_bytes: bytes,
        nonce: Optional[bytes] = None,
        target: str = "key",
        samples: int = 50,
    ) -> Dict[str, Any]:
        """Analyze differential propagation ΔC for controlled input difference Δ.

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext bytes payload.
            delta_bytes: Controlled XOR input difference bytes (Δ).
            nonce: Optional nonce bytes.
            target: Difference target ("key", "nonce", or "plaintext").
            samples: Number of sample evaluations.

        Returns:
            Dict[str, Any]: Differential analysis metrics.
        """
        engine = self._get_engine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)
        d_bytes = bytes(delta_bytes)

        # Baseline encryption
        base_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)

        if target.lower() == "plaintext":
            mod_pt = bytes(a ^ b for a, b in zip(pt_bytes, d_bytes + b"\x00" * max(0, len(pt_bytes) - len(d_bytes))))
            mod_res = engine.encrypt(mod_pt, master_key=m_key, nonce=base_res["nonce"], check_nonce_reuse=False)
            # Evaluate tag differential propagation for plaintext difference
            comp = self.compare(base_res["tag"], mod_res["tag"])
        elif target.lower() == "nonce":
            base_nonce = base_res["nonce"]
            mod_nonce = bytes(a ^ b for a, b in zip(base_nonce, d_bytes + b"\x00" * max(0, len(base_nonce) - len(d_bytes))))
            mod_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=mod_nonce, check_nonce_reuse=False)
            comp = self.compare(base_res["ciphertext"] + base_res["tag"], mod_res["ciphertext"] + mod_res["tag"])
        else:
            mod_key = bytes(a ^ b for a, b in zip(m_key, d_bytes + b"\x00" * max(0, len(m_key) - len(d_bytes))))
            mod_res = engine.encrypt(pt_bytes, master_key=mod_key, nonce=base_res["nonce"], check_nonce_reuse=False)
            comp = self.compare(base_res["ciphertext"] + base_res["tag"], mod_res["ciphertext"] + mod_res["tag"])

        return {
            "target": target,
            "input_difference_bits": sum(bin(b).count("1") for b in d_bytes),
            "output_difference_bits": comp["changed_bits"],
            "total_output_bits": comp["total_bits"],
            "differential_probability": comp["difference_ratio"],
            "differential_percent": comp["difference_percent"],
            "passed": comp["difference_ratio"] >= 0.40,
        }

    def statistics(self) -> Dict[str, Any]:
        """Return general differential metrics parameters summary."""
        return {
            "description": "XOR Differential Propagation & Probability Analyzer",
            "ideal_differential_probability": 0.50,
        }
