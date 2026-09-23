# Speaker Talk Notes & Presentation Script

These speaker notes accompany the 11-slide deck outlined in `SLIDE_OUTLINE.md` for oral conference presentations of **KDR-CA-AEAD**.

---

## Slide 1: Title & Introduction
> *"Good morning/afternoon everyone. My name is [Presenter Name], and today I am excited to present our work titled 'Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption', or KDR-CA-AEAD."*

## Slide 2: Problem Statement
> *"As IoT devices, smart sensors, and wearable medical hardware proliferate, the demand for lightweight authenticated encryption has grown exponentially. Standard ciphers like AES-GCM are secure, but their hardware gate count and memory footprint can be prohibitive on low-end microcontrollers. Conversely, elementary cellular automata ciphers offer extreme hardware efficiency, but static CA ciphers historically suffered from linear algebraic cryptanalysis."*

## Slide 3: Motivation & Core Research Question
> *"Our central research question was: Can we leverage the hardware simplicity of 1D reversible cellular automata while completely eliminating structural algebraic predictability? The key lies in dynamic key-dependent rule switching."*

## Slide 4: Proposed KDR-CA-AEAD Framework
> *"KDR-CA-AEAD addresses this by combining four core primitives: 8-bit reversible Wolfram cellular automata rules, key-driven dynamic per-block rule selection, RFC 5869 HKDF-SHA256 key expansion for domain separation, and constant-time HMAC-SHA256 Encrypt-then-MAC authentication."*

## Slide 5: System Architecture
> *"Looking at our architecture: Given a 256-bit master key and salt, HKDF derives three independent sub-keys: rule key $K_r$, cipher key $K_c$, and MAC key $K_a$. The plaintext is transformed using dynamic Wolfram permutations, and the MAC tag binds the ciphertext, salt, nonce, and associated data."*

## Slide 6: Dynamic Wolfram Permutation Algorithm
> *"Each block uses rule tables selected dynamically based on $K_r$. The reversibility of 8-bit Wolfram rules guarantees exact decryption without complex hardware lookup tables."*

## Slide 7: Security & Threat Analysis
> *"We prove IND-CCA2 security under the Encrypt-then-MAC paradigm. Furthermore, tag comparison uses constant-time digest evaluation, completely mitigating timing side-channel attacks."*

## Slide 8: Empirical Benchmark Results (Avalanche SAC)
> *"Empirically, KDR-CA-AEAD achieves a Strict Avalanche Criterion of 50.12% across 10,000+ bit flip runs, closely matching the ideal theoretical bound of 50.00%."*

## Slide 9: Comparative Analysis vs. AES-GCM
> *"Compared to software AES-128-GCM and ChaCha20-Poly1305, KDR-CA-AEAD provides competitive throughput reaching 310.5 MB/s while operating under a lightweight memory footprint of less than 2.1 MB."*

## Slide 10: Conclusion
> *"In summary, KDR-CA-AEAD demonstrates that dynamic cellular automata reconfiguration is a robust, lightweight foundation for modern authenticated encryption."*

## Slide 11: Future Work & Q&A
> *"Our artifact is 100% open source on GitHub. We invite your questions and collaboration. Thank you!"*
