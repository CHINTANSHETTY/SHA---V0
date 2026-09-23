"""Avalanche Effect and Strict Avalanche Criterion (SAC) Analysis.

This module provides `AvalancheAnalyzer` and `SACAnalyzer` for empirical security evaluation
of plaintext, key, and nonce diffusion in KDR-CA-AEAD.

Target IEEE Criteria:
    - Key & Nonce Avalanche Effect: ~50% output bit change per 1-bit input flip across ciphertext and tag.
    - Plaintext Tag Avalanche: ~50% authentication tag bit change per 1-bit plaintext flip.
    - Strict Avalanche Criterion (SAC): Each output bit changes with probability P_ij ≈ 0.5.
"""

import math
from typing import Any, Dict, List, Optional, Union


def count_bit_flips(buf1: bytes, buf2: bytes) -> int:
    """Count differing bits (Hamming distance) between two byte sequences.

    Args:
        buf1: First byte sequence.
        buf2: Second byte sequence.

    Returns:
        int: Number of differing bits.
    """
    return sum(bin(a ^ b).count("1") for a, b in zip(buf1, buf2))


def calculate_statistics(ratios: List[float]) -> Dict[str, float]:
    """Calculate summary statistics (mean, min, max, variance, std dev) for a list of ratios.

    Args:
        ratios: List of float values in range [0.0, 1.0].

    Returns:
        Dict[str, float]: Dictionary containing summary statistics.
    """
    if not ratios:
        return {"mean": 0.0, "mean_percent": 0.0, "min": 0.0, "max": 0.0, "variance": 0.0, "std_dev": 0.0}

    n = len(ratios)
    mean_val = sum(ratios) / n
    min_val = min(ratios)
    max_val = max(ratios)

    if n > 1:
        var_val = sum((r - mean_val) ** 2 for r in ratios) / (n - 1)
    else:
        var_val = 0.0
    std_val = math.sqrt(var_val)

    return {
        "mean": round(mean_val, 6),
        "mean_percent": round(mean_val * 100.0, 2),
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "variance": round(var_val, 6),
        "std_dev": round(std_val, 6),
    }


class AvalancheAnalyzer:
    """Avalanche Effect Analyzer for plaintext, key, and nonce diffusion."""

    def __init__(self, aead_engine: Optional[Any] = None) -> None:
        """Initialize AvalancheAnalyzer."""
        self._aead_engine = aead_engine

    def _get_engine(self) -> Any:
        if self._aead_engine is None:
            from crypto.primitives.aead import AEADEngine
            self._aead_engine = AEADEngine()
        return self._aead_engine

    def generate_statistics(self, avalanche_ratios: List[float]) -> Dict[str, float]:
        """Generate summary statistics for avalanche ratios."""
        return calculate_statistics(avalanche_ratios)

    def analyze_plaintext(
        self,
        master_key: bytes,
        plaintext: bytes,
        nonce: Optional[bytes] = None,
        samples: int = 100,
    ) -> Dict[str, Any]:
        """Analyze avalanche effect on AEAD Authentication Tag when single plaintext bits are flipped.

        In stream cipher AEAD (Encrypt-then-MAC), flipping 1 plaintext bit inverts 1 ciphertext bit,
        while diffusing pseudorandomly across ~50% of the AEAD Authentication Tag bits.

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext bytes payload.
            nonce: Optional nonce bytes.
            samples: Number of 1-bit flip trials.

        Returns:
            Dict[str, Any]: Avalanche metrics dictionary.
        """
        engine = self._get_engine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)
        if len(pt_bytes) == 0:
            return {"samples_evaluated": 0, "status": "Empty Plaintext", **calculate_statistics([])}

        base_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)
        base_tag = base_res["tag"]
        total_tag_bits = len(base_tag) * 8

        total_pt_bits = len(pt_bytes) * 8
        num_trials = min(samples, total_pt_bits)
        ratios: List[float] = []

        for bit_idx in range(num_trials):
            byte_i = bit_idx // 8
            bit_i = bit_idx % 8

            mod_pt = bytearray(pt_bytes)
            mod_pt[byte_i] ^= (1 << (7 - bit_i))

            mod_res = engine.encrypt(bytes(mod_pt), master_key=m_key, nonce=base_res["nonce"], check_nonce_reuse=False)
            flips = count_bit_flips(base_tag, mod_res["tag"])
            ratios.append(flips / total_tag_bits if total_tag_bits > 0 else 0.0)

        stats = calculate_statistics(ratios)
        return {
            "samples_evaluated": num_trials,
            "total_output_bits": total_tag_bits,
            "ratios": ratios,
            "passed": stats["mean"] >= 0.45,
            **stats,
        }

    def analyze_key(
        self,
        master_key: bytes,
        plaintext: bytes,
        nonce: Optional[bytes] = None,
        samples: int = 100,
    ) -> Dict[str, Any]:
        """Analyze key avalanche effect when single master key bits are flipped.

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext bytes payload.
            nonce: Optional nonce bytes.
            samples: Number of 1-bit key flip trials.

        Returns:
            Dict[str, Any]: Key avalanche metrics dictionary.
        """
        engine = self._get_engine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)

        base_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)
        base_ct = base_res["ciphertext"] + base_res["tag"]
        total_bits = len(base_ct) * 8

        total_key_bits = len(m_key) * 8
        num_trials = min(samples, total_key_bits)
        ratios: List[float] = []

        for bit_idx in range(num_trials):
            byte_i = bit_idx // 8
            bit_i = bit_idx % 8

            mod_key = bytearray(m_key)
            mod_key[byte_i] ^= (1 << (7 - bit_i))

            mod_res = engine.encrypt(pt_bytes, master_key=bytes(mod_key), nonce=base_res["nonce"], check_nonce_reuse=False)
            mod_ct = mod_res["ciphertext"] + mod_res["tag"]
            flips = count_bit_flips(base_ct, mod_ct)
            ratios.append(flips / total_bits if total_bits > 0 else 0.0)

        stats = calculate_statistics(ratios)
        return {
            "samples_evaluated": num_trials,
            "total_output_bits": total_bits,
            "ratios": ratios,
            "passed": stats["mean"] >= 0.45,
            **stats,
        }

    def analyze_nonce(
        self,
        master_key: bytes,
        plaintext: bytes,
        nonce: Optional[bytes] = None,
        samples: int = 100,
    ) -> Dict[str, Any]:
        """Analyze nonce avalanche effect when single nonce bits are flipped.

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext bytes payload.
            nonce: Optional nonce bytes (12 bytes).
            samples: Number of 1-bit nonce flip trials.

        Returns:
            Dict[str, Any]: Nonce avalanche metrics dictionary.
        """
        engine = self._get_engine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)

        base_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)
        base_ct = base_res["ciphertext"] + base_res["tag"]
        base_nonce = base_res["nonce"]
        total_bits = len(base_ct) * 8

        total_nonce_bits = len(base_nonce) * 8
        num_trials = min(samples, total_nonce_bits)
        ratios: List[float] = []

        for bit_idx in range(num_trials):
            byte_i = bit_idx // 8
            bit_i = bit_idx % 8

            mod_nonce = bytearray(base_nonce)
            mod_nonce[byte_i] ^= (1 << (7 - bit_i))

            mod_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=bytes(mod_nonce), check_nonce_reuse=False)
            mod_ct = mod_res["ciphertext"] + mod_res["tag"]
            flips = count_bit_flips(base_ct, mod_ct)
            ratios.append(flips / total_bits if total_bits > 0 else 0.0)

        stats = calculate_statistics(ratios)
        return {
            "samples_evaluated": num_trials,
            "total_output_bits": total_bits,
            "ratios": ratios,
            "passed": stats["mean"] >= 0.45,
            **stats,
        }


class SACAnalyzer:
    """Strict Avalanche Criterion (SAC) Analyzer."""

    def __init__(self, aead_engine: Optional[Any] = None) -> None:
        """Initialize SACAnalyzer."""
        self._aead_engine = aead_engine
        self._sac_matrix: List[List[float]] = []

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
        samples: int = 100,
        target: str = "key",
    ) -> Dict[str, Any]:
        """Compute empirical Strict Avalanche Criterion (SAC) probability matrix P_ij.

        For each input bit i (key or nonce) and output bit j (ciphertext + tag), P_ij represents
        the probability that output bit j flips when input bit i is inverted. Ideal value P_ij = 0.5.

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext bytes payload.
            nonce: Optional nonce bytes.
            samples: Number of input bits to sample.
            target: Input component to flip ("key", "nonce", or "plaintext").

        Returns:
            Dict[str, Any]: SAC matrix statistics and empirical mean probability.
        """
        engine = self._get_engine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)

        base_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)
        base_ct = base_res["ciphertext"] + base_res["tag"]
        out_bits_count = len(base_ct) * 8

        if target.lower() == "plaintext":
            input_bytes = pt_bytes
        elif target.lower() == "nonce":
            input_bytes = base_res["nonce"]
        else:
            input_bytes = m_key

        if len(input_bytes) == 0:
            return {"mean_sac_probability": 0.0, "sac_matrix": [], "status": "Empty Input"}

        in_bits_count = min(samples, len(input_bytes) * 8)
        matrix: List[List[float]] = []

        for bit_i in range(in_bits_count):
            byte_idx = bit_i // 8
            bit_idx = bit_i % 8

            if target.lower() == "plaintext":
                mod_pt = bytearray(pt_bytes)
                mod_pt[byte_idx] ^= (1 << (7 - bit_idx))
                mod_res = engine.encrypt(bytes(mod_pt), master_key=m_key, nonce=base_res["nonce"], check_nonce_reuse=False)
            elif target.lower() == "nonce":
                mod_nonce = bytearray(base_res["nonce"])
                mod_nonce[byte_idx] ^= (1 << (7 - bit_idx))
                mod_res = engine.encrypt(pt_bytes, master_key=m_key, nonce=bytes(mod_nonce), check_nonce_reuse=False)
            else:
                mod_key = bytearray(m_key)
                mod_key[byte_idx] ^= (1 << (7 - bit_idx))
                mod_res = engine.encrypt(pt_bytes, master_key=bytes(mod_key), nonce=base_res["nonce"], check_nonce_reuse=False)

            mod_ct = mod_res["ciphertext"] + mod_res["tag"]
            row_probs: List[float] = []

            for bit_j in range(out_bits_count):
                out_byte_j = bit_j // 8
                out_bit_j = bit_j % 8

                b1 = (base_ct[out_byte_j] >> (7 - out_bit_j)) & 1
                b2 = (mod_ct[out_byte_j] >> (7 - out_bit_j)) & 1
                row_probs.append(1.0 if b1 != b2 else 0.0)

            matrix.append(row_probs)

        self._sac_matrix = matrix

        # Compute empirical mean probability across all P_ij entries
        all_vals = [p for row in matrix for p in row]
        stats = calculate_statistics(all_vals)

        return {
            "input_bits_evaluated": in_bits_count,
            "output_bits": out_bits_count,
            "mean_sac_probability": stats["mean"],
            "std_dev": stats["std_dev"],
            "variance": stats["variance"],
            "min_probability": stats["min"],
            "max_probability": stats["max"],
            "sac_matrix": matrix,
            "passed": stats["mean"] >= 0.40,
        }

    def export_matrix(self, format: str = "dict") -> Any:
        """Export calculated SAC probability matrix."""
        if format.lower() == "matrix":
            return self._sac_matrix
        return {"rows": len(self._sac_matrix), "cols": len(self._sac_matrix[0]) if self._sac_matrix else 0, "matrix": self._sac_matrix}
