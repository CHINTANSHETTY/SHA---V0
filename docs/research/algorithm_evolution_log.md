# KDR-CA-AEAD ALGORITHM EVOLUTION LOG

**Project Title:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Document Path:** `docs/research/algorithm_evolution_log.md`  
**Purpose:** Permanent historical log tracking all candidate algorithm iterations, empirical design trade-offs, and architectural evolution for IEEE publication traceability.  

---

## Evolution History

### Record 001: Phase 1.1 HKDF Primitive Selection
- **Date**: 2026-08-01
- **Candidate Design**: RFC 5869 HKDF-SHA256 Extract-and-Expand.
- **Decision**: **ACCEPTED & FROZEN**.
- **Rationale**: Standardized key derivation methodology ensuring full entropy extraction from master key buffers per NIST SP 800-56C Rev. 2.

### Record 002: Phase 1.2 Key Schedule Sub-Key Derivation
- **Date**: 2026-08-01
- **Candidate Design**: Single 96-byte OKM HKDF slicing vs. 3 independent HKDF expansions with explicit `info` labels.
- **Decision**: **ACCEPTED & FROZEN (3 Independent HKDF Expansions)**.
- **Rationale**: Domain separation labels (`...-ca-rules|`, `...-cipher-key|`, `...-mac-key|`) bind sub-keys $K_r, K_c, K_a$ independently per NIST SP 800-56C Rev. 2.

### Record 003: Phase 2.1 Candidate A (Local Byte S-Box Transformation)
- **Date**: 2026-08-02
- **Candidate Design**: Byte-by-byte non-linear cellular automata substitution ($p_i \to t_i$) without inter-byte feedback.
- **Decision**: **REJECTED AS STANDALONE CIPHER STATE**.
- **Rationale**: While providing local S-box substitution behavior, single-byte transformation confines bit flip diffusion to the modified position (NPCR = $0.56\%$, SAC = $0.0012$).

### Record 004: Phase 2.1A Candidate A-Chain (Inter-Byte Diffusion + Reversible Pipeline)
- **Date**: 2026-08-02
- **Candidate Design**: Feedback vector state chaining $(p_i \oplus \text{prev\_state}) \to \text{Modulo Addition} \to \text{Bit Rotation} \to \text{XOR Rule Mixing}$.
- **Decision**: **ACCEPTED FOR PRODUCTION IMPLEMENTATION (PHASE 2.2)**.
- **Rationale**: Elevates Strict Avalanche Criterion (SAC) from $0.0012$ to $\mu = 0.2336$ (95% CI $[0.2243, 0.2428]$) and NPCR from $0.56\%$ to $48.28\%$ while retaining 100% loss-free bijectivity ($D_{\text{CA}}(E_{\text{CA}}(P)) \equiv P$).
- **Future Validation Disclaimer**: The chosen candidate will undergo additional empirical validation using the full project benchmark suite (SAC, BIC, NIST SP 800-22 randomness batteries, throughput profiling, and comparative cryptanalysis) in Phase 3 before final paper claims are claimed.
