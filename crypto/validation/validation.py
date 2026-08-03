"""Unified Validation Engine Subsystem (`crypto.validation.validation`).

Provides `ValidationRunner` for unified execution of Avalanche, SAC, BIC, Entropy,
Differential, Correlation, and NIST SP 800-22 statistical security evaluations.
"""

import math
import random
from typing import Any, Dict, List, Optional

from crypto.analysis.avalanche import AvalancheAnalyzer, SACAnalyzer
from crypto.analysis.differential import BICAnalyzer, DifferentialAnalyzer
from crypto.analysis.entropy import EntropyAnalyzer
from crypto.analysis.randomness import RandomnessAnalyzer
from crypto.primitives.aead import AEADEngine
from crypto.validation.statistics import StatisticalEngine


class ValidationRunner:
    """Unified Cryptographic Research Validation Runner."""

    def __init__(self, aead_engine: Optional[AEADEngine] = None) -> None:
        """Initialize ValidationRunner."""
        self.aead_engine: AEADEngine = aead_engine if aead_engine is not None else AEADEngine()
        self.stats_engine: StatisticalEngine = StatisticalEngine()
        self.avalanche_analyzer: AvalancheAnalyzer = AvalancheAnalyzer(aead_engine=self.aead_engine)
        self.sac_analyzer: SACAnalyzer = SACAnalyzer(aead_engine=self.aead_engine)
        self.bic_analyzer: BICAnalyzer = BICAnalyzer()
        self.differential_analyzer: DifferentialAnalyzer = DifferentialAnalyzer(aead_engine=self.aead_engine)
        self.entropy_analyzer: EntropyAnalyzer = EntropyAnalyzer()
        self.randomness_analyzer: RandomnessAnalyzer = RandomnessAnalyzer()

    def run_full_validation(
        self,
        master_key: bytes = b"master_key_bytes_validation_32",
        plaintext: bytes = b"IEEE Research Cryptographic Validation Payload 2026",
        trials: int = 30,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Execute full statistical research validation suite.

        Args:
            master_key: Input master key bytes.
            plaintext: Input plaintext payload bytes.
            trials: Number of trial iterations for statistical aggregation.
            seed: PRNG seed for deterministic trial generation.

        Returns:
            Dict[str, Any]: Comprehensive statistical validation dataset.
        """
        rng = random.Random(seed)
        pkg = self.aead_engine.encrypt(plaintext, master_key=master_key, check_nonce_reuse=False)
        ct, tag, nonce = pkg["ciphertext"], pkg["tag"], pkg["nonce"]

        # 1. Avalanche Effect Analysis
        av_key = self.avalanche_analyzer.analyze_key(master_key, plaintext, samples=trials)
        av_pt = self.avalanche_analyzer.analyze_plaintext(master_key, plaintext, samples=trials)

        # 2. Strict Avalanche Criterion (SAC)
        sac_res = self.sac_analyzer.analyze(master_key, plaintext, samples=trials)

        # 3. Bit Independence Criterion (BIC)
        bic_res = self.bic_analyzer.analyze(master_key, plaintext, samples=trials)

        # 4. Entropy & Uniformity Analysis
        shannon_h = self.stats_engine.shannon_entropy(ct + tag)
        min_h = self.stats_engine.min_entropy(ct + tag)
        max_h = self.stats_engine.max_entropy()
        chi2_res = self.stats_engine.chi_square_statistic(ct + tag)
        bit_hist = self.stats_engine.bit_frequency_histogram(ct + tag)

        # 5. Differential Analysis
        delta_k = b"\x01" + (b"\x00" * (len(master_key) - 1))
        diff_res = self.differential_analyzer.analyze(master_key, plaintext, delta_bytes=delta_k, samples=trials)

        # 6. Correlation Analysis (Pearson, Spearman, Kendall Tau, Autocorrelation, Cross-correlation)
        ct_ints = [float(b) for b in ct]
        tag_ints = [float(b) for b in tag]
        pearson_r = self.stats_engine.pearson_correlation(ct_ints, tag_ints)
        spearman_rho = self.stats_engine.spearman_correlation(ct_ints, tag_ints)
        kendall_tau = self.stats_engine.kendall_tau(ct_ints[:16], tag_ints[:16])
        autocorr_1 = self.stats_engine.autocorrelation(ct_ints, lag=1)
        autocorr_4 = self.stats_engine.autocorrelation(ct_ints, lag=4)
        cross_corr = self.stats_engine.cross_correlation(ct_ints, tag_ints, lag=0)

        # 7. NIST SP 800-22 Test Results Parser / Summarizer
        nist_res = self.randomness_analyzer.analyze(ct + tag)

        # Reproducibility Metadata
        reproducibility = {
            "seed": seed,
            "trials": trials,
            "payload_size_bytes": len(plaintext),
            "key_size_bytes": len(master_key),
            "nonce_size_bytes": len(nonce),
            "aad_length_bytes": 0,
        }

        return {
            "reproducibility": reproducibility,
            "avalanche": {
                "key_avalanche": av_key,
                "plaintext_avalanche": av_pt,
            },
            "sac": sac_res,
            "bic": bic_res,
            "entropy": {
                "shannon_entropy": shannon_h,
                "min_entropy": min_h,
                "max_entropy": max_h,
                "chi_square": chi2_res,
                "bit_frequency": bit_hist,
            },
            "differential": diff_res,
            "correlation": {
                "pearson_correlation": round(pearson_r, 6),
                "spearman_correlation": round(spearman_rho, 6),
                "kendall_tau": round(kendall_tau, 6),
                "autocorrelation_lag1": round(autocorr_1, 6),
                "autocorrelation_lag4": round(autocorr_4, 6),
                "cross_correlation": round(cross_corr, 6),
            },
            "nist_sp_800_22": nist_res,
        }
