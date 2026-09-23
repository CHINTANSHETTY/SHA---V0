"""Consolidated Security Metrics Collector.

This module provides `SecurityMetrics` to aggregate statistical security evaluations from
Avalanche, SAC, BIC, Entropy, Randomness, and Differential analyzers into a single metrics object.
"""

from typing import Any, Dict, Optional

from .avalanche import AvalancheAnalyzer, SACAnalyzer
from .differential import BICAnalyzer, DifferentialAnalyzer
from .entropy import EntropyAnalyzer
from .randomness import RandomnessAnalyzer


class SecurityMetrics:
    """Consolidated Security Metrics Object."""

    def __init__(self) -> None:
        """Initialize SecurityMetrics."""
        self.avalanche_results: Dict[str, Any] = {}
        self.sac_results: Dict[str, Any] = {}
        self.bic_results: Dict[str, Any] = {}
        self.entropy_results: Dict[str, Any] = {}
        self.randomness_results: Dict[str, Any] = {}
        self.differential_results: Dict[str, Any] = {}
        self._is_collected: bool = False

    def collect(
        self,
        master_key: bytes,
        plaintext: bytes,
        nonce: Optional[bytes] = None,
        samples: int = 50,
    ) -> Dict[str, Any]:
        """Collect all security metrics for the given key and plaintext payload.

        Args:
            master_key: Secret master key bytes.
            plaintext: Plaintext payload bytes.
            nonce: Optional nonce bytes.
            samples: Sample count for bit flip trials.

        Returns:
            Dict[str, Any]: Consolidated metrics dictionary.
        """
        from crypto.primitives.aead import AEADEngine

        aead = AEADEngine()
        m_key = bytes(master_key)
        pt_bytes = bytes(plaintext)

        # Baseline encryption for payload analyses
        base_res = aead.encrypt(pt_bytes, master_key=m_key, nonce=nonce, check_nonce_reuse=False)
        base_ct = base_res["ciphertext"] + base_res["tag"]

        # 1. Avalanche Analysis
        avalanche = AvalancheAnalyzer(aead_engine=aead)
        self.avalanche_results = {
            "plaintext": avalanche.analyze_plaintext(m_key, pt_bytes, nonce=base_res["nonce"], samples=samples),
            "key": avalanche.analyze_key(m_key, pt_bytes, nonce=base_res["nonce"], samples=samples),
            "nonce": avalanche.analyze_nonce(m_key, pt_bytes, nonce=base_res["nonce"], samples=samples),
        }

        # 2. SAC Analysis
        sac = SACAnalyzer(aead_engine=aead)
        self.sac_results = sac.analyze(m_key, pt_bytes, nonce=base_res["nonce"], samples=samples)

        # 3. BIC Analysis
        bic = BICAnalyzer(aead_engine=aead)
        self.bic_results = bic.analyze(m_key, pt_bytes, nonce=base_res["nonce"], samples=samples)

        # 4. Entropy Analysis
        entropy = EntropyAnalyzer()
        self.entropy_results = entropy.analyze(base_ct)

        # 5. Randomness Analysis
        randomness = RandomnessAnalyzer()
        self.randomness_results = randomness.analyze(base_ct)

        # 6. Differential Analysis
        differential = DifferentialAnalyzer(aead_engine=aead)
        delta_bytes = b"\x01" + b"\x00" * (len(m_key) - 1)
        self.differential_results = differential.analyze(m_key, pt_bytes, delta_bytes=delta_bytes, target="key", samples=samples)

        self._is_collected = True
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """Export consolidated metrics as dictionary.

        Returns:
            Dict[str, Any]: Consolidated metrics dictionary.
        """
        return {
            "avalanche": self.avalanche_results,
            "sac": self.sac_results,
            "bic": self.bic_results,
            "entropy": self.entropy_results,
            "randomness": self.randomness_results,
            "differential": self.differential_results,
            "is_collected": self._is_collected,
        }

    def summary(self) -> str:
        """Generate formatted summary string of security metrics.

        Returns:
            str: Human-readable summary string.
        """
        if not self._is_collected:
            return "SecurityMetrics: No data collected yet."

        key_av = self.avalanche_results.get("key", {}).get("mean_percent", 0.0)
        sac_p = self.sac_results.get("mean_sac_probability", 0.0)
        bic_score = self.bic_results.get("independence_score", 0.0)
        h_shannon = self.entropy_results.get("shannon_entropy", 0.0)
        rand_status = self.randomness_results.get("summary", "N/A")

        return (
            f"=== KDR-CA-AEAD Security Metrics Summary ===\n"
            f"Key Avalanche Effect: {key_av:.2f}%\n"
            f"SAC Mean Probability: {sac_p:.6f} (Ideal: 0.50)\n"
            f"BIC Independence Score: {bic_score:.6f} (Ideal: 1.00)\n"
            f"Shannon Entropy: {h_shannon:.6f} bits/byte\n"
            f"Randomness Suite Status: {rand_status}"
        )
