# STEP 15 — FINAL PAPER–CODE CONSISTENCY AUDIT REPORT

**Date:** 2026-09-23  
**Project:** SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)  
**Status:** Audit Complete — No Paper or Production Application Files Modified  

---

## EXECUTIVE SUMMARY

This audit systematically evaluates the current paper files (`paper/ieee_paper.tex`, `paper/sections/*.tex`, `paper/appendix/appendix.tex`, `paper/supplementary/supplementary.tex`, `paper/tables/*.tex`, `paper/figures/*`) against the final production research encryption architecture validated in Step 14.

### Final Implemented Architecture (Step 14 Baseline):
1. **Key Generation:** SHA-512 applied to user password string; the first 256 bits of the 512-bit digest form key $K_{256}$.
2. **Payload Framing:** UTF-8 text encoding $\rightarrow$ 32-bit length header $\rightarrow$ zero-padding to 256-bit block boundaries.
3. **Block Size & Matrix Representation:** 256 bits per block, represented as a $16 \times 16$ binary matrix.
4. **CA Rounds ($R=10$):** Exactly 10 reversible cellular automata rounds.
5. **Partition Alternation:**
   - **Odd rounds ($r=1, 3, 5, 7, 9$):** Standard non-overlapping $2 \times 2$ Margolus partition.
   - **Even rounds ($r=2, 4, 6, 8, 10$):** Shifted $2 \times 2$ Margolus partition (offset by 1 cell in both dimensions, periodic boundary wrapping).
6. **Circular Matrix Shift:** After **EVERY** CA round, a 2D circular matrix shift **DOWN 2** and **RIGHT 2** is applied (`shifted[r][c] = matrix[(r-2)%16][(c-2)%16]`).
7. **Key Mixing:** The transformed 256-bit block is XORed with $K_{256}$.
8. **Decryption Pipeline:** Exact inverse sequence (XOR $K_{256} \rightarrow$ reverse 10 rounds: circular shift **UP 2** and **LEFT 2** ($[r+2 \pmod{16}, c+2 \pmod{16}]$) $\rightarrow$ corresponding inverse Margolus partition $\rightarrow$ 32-bit length header extraction $\rightarrow$ UTF-8 text string).
9. **Ciphertext Format:** Base64 application string prefixed with `REV-CA-V1:`.
10. **Reversibility:** 100% loss-less exact reconstruction ($P = \text{decrypt}(\text{encrypt}(P))$).

### Prohibited in Active Core Algorithm:
HKDF, HKDF-SHA256, HMAC, AES, AEAD, Nonce, Salt, Dynamic Keyed CA, KDR-CA-AEAD, 2-bit FBCA rules, 1D byte-oriented CA, and Candidate A (DOWN 1 / RIGHT 1 shift).

---

## SECTION 1 — PAPER STRUCTURE AUDIT

| Paper Section | File Location | Current Purpose | Compatibility with Final Implementation | Status | Required Action |
|---|---|---|---|---|---|
| **Title & Header** | `ieee_paper.tex` | Defines title as "KDR-CA-AEAD" and running header | Refers to old 1D AEAD cipher | `[OBSOLETE]` | Update title to "SHA-512-Based 256-Bit Block Cellular Automata Cryptosystem for Secure Healthcare Telemetry" |
| **Abstract** | `abstract.tex` | Summarizes KDR-CA-AEAD, HKDF-SHA256, HMAC, 13.37 MB/s, SAC 50.12% | Refers entirely to old 1D byte stream cipher | `[OBSOLETE]` | Rewrite abstract to describe 256-bit block CA, SHA-512 K256, 10-round Candidate C, and Step 13 measured metrics |
| **Section I: Introduction** | `introduction.tex` | Background on healthcare IoT, AES-GCM, 1D ECA, and KDR-CA-AEAD contributions | Refers to 1D ECA and HKDF key expansion | `[OBSOLETE]` | Rewrite motivation and contributions to reflect 256-bit reversible 2D Margolus CA block cipher |
| **Section II: Literature Review** | `literature_review.tex` | Reviews CA ciphers (Rule 30/45) and AEAD schemes | Reviews 1D CA and AEAD primitives | `[NEEDS UPDATE]` | Update review to cover 2D block CA, Margolus partitioning, and SHA-512 key schedules |
| **Section III: Mathematical Model & Primitives** | `methodology.tex` | Details HKDF pipeline, 1D Wolfram ECA rules ($\delta=13$), Candidate A-Chain | Describes obsolete 1D byte-level operations | `[OBSOLETE]` | Replace with SHA-512 $K_{256}$ derivation, 32-bit length header, $16 \times 16$ matrix, 4-bit local rule, and Candidate C equations |
| **Section IV: System Architecture** | `architecture.tex` | Details KDR-CA-AEAD 5-layer system, Algorithms 1 & 2, CTR keystream | Describes obsolete 1D stream AEAD pipeline | `[OBSOLETE]` | Replace with Candidate C 10-round pipeline algorithms, framing diagrams, and matrix transition figures |
| **Section V: Security Analysis** | `security_analysis.tex` | Reports NIST SP 800-22, Shannon entropy 7.998, SAC 50.12% for 1D cipher | Contains old hardcoded 1D cipher numbers | `[OBSOLETE]` | Replace with Step 13 empirical Candidate C round-count diffusion metrics ($R=2 \dots 10$) |
| **Section VI: Performance Evaluation** | `benchmarks.tex` | Reports 64B–1MB micro-benchmarks (13.37 MB/s) and comparison vs AES | Contains old stream benchmark data | `[OBSOLETE]` | Replace with Candidate C 256-bit block execution latencies ($1.899\text{ ms/block}$ at $R=10$) |
| **Section VII: Discussion & Trade-Offs** | `discussion.tex` | Analyzes KDR-CA-AEAD strengths, S-boxes, and IND-CCA2 security | Analyzes obsolete 1D stream cipher | `[NEEDS UPDATE]` | Rewrite to analyze trade-offs between CA round count $R$, spatial diffusion growth, and execution latency |
| **Section VIII: Future Work** | `future_work.tex` | Proposes SystemVerilog cores for Candidate A-Chain and HKDF expansion | Refers to obsolete 1D candidate A-chain | `[NEEDS UPDATE]` | Update to FPGA/ASIC prototyping of 2D Margolus partitions and post-quantum hybrid key exchange |
| **Section IX: Conclusion** | `conclusion.tex` | Summarizes KDR-CA-AEAD, HKDF, HMAC, and 13.37 MB/s throughput | Summarizes obsolete cipher scheme | `[OBSOLETE]` | Rewrite conclusion to summarize final SHA-512 + 10-round Candidate C Margolus CA architecture |
| **Appendix A & B** | `appendix/appendix.tex` | Proofs for 1D ECA byte permutation and HKDF domain separation | Proofs belong to obsolete 1D cipher | `[OBSOLETE]` | Replace with formal proof of loss-less reversibility for 10-round Candidate C 2D Margolus CA |
| **Supplementary Material** | `supplementary/supplementary.tex` | References `results/master_results.json` and `run_phase2_5_reproducibility.py` | References obsolete scripts/files | `[NEEDS UPDATE]` | Update file paths to `step13_final_round_results.csv` and `tests/test_step14_integration.py` |

---

## SECTION 2 — ALGORITHM CONSISTENCY

| Component | Paper Location | Current Paper Claim | Actual Implementation | Status | Required Action |
|---|---|---|---|---|---|
| **A. Key Generation** | `methodology.tex` L6-12 | HKDF-Extract-and-Expand with HMAC-SHA256, 16B salt, 12B nonce | SHA-512 hash applied to secret password string | `[OBSOLETE]` | Replace HKDF pipeline with SHA-512 key generation |
| **B. 512-bit Digest** | `methodology.tex` | Not mentioned (uses 256-bit SHA-256 HKDF PRK) | SHA-512 produces a full 512-bit digest | `[NEEDS UPDATE]` | Explicitly specify creation of 512-bit SHA-512 digest |
| **C. Key K256** | `methodology.tex` L9-11 | Derives 32-byte sub-keys $K_r, K_c, K_a$ via HKDF-Expand | First 256 bits (32 bytes) of SHA-512 digest extracted as $K_{256}$ | `[OBSOLETE]` | Update key material specification to SHA-512 first 256 bits |
| **D. Block Size** | `architecture.tex` L40 | Variable length byte stream buffer ($M$ bytes) | Fixed 256-bit block size ($16 \times 16$ binary matrix) | `[NEEDS UPDATE]` | Update cipher model from stream cipher to 256-bit block cipher |
| **E. Length Header** | `architecture.tex` | Not mentioned | 32-bit binary length header prepended to UTF-8 binary payload | `[NEEDS UPDATE]` | Document 32-bit length header payload framing |
| **F. Zero Padding** | `architecture.tex` | Not mentioned | Zero-padding appended to align framed payload to 256-bit block boundary | `[NEEDS UPDATE]` | Document zero-padding to 256-bit block boundary |
| **G. Matrix Mapping** | `methodology.tex` L18 | 1D byte array $P_i$ ($i \in [0, M-1]$) | 256-bit block mapped to $16 \times 16$ binary matrix ($R \times C$) | `[OBSOLETE]` | Replace 1D byte array description with $16 \times 16$ binary matrix mapping |
| **H. Neighborhood** | `methodology.tex` L29-34 | 1D 3-cell Wolfram neighborhood (left, self, right) | 2D $2 \times 2$ Margolus spatial neighborhood (4 cells) | `[OBSOLETE]` | Update neighborhood topology to $2 \times 2$ Margolus blocks |
| **I. Local State** | `methodology.tex` L37 | 3-bit Wolfram neighborhood index $\eta \in [0, 7]$ | 4-bit local neighborhood state integer $s \in [0, 15]$ | `[OBSOLETE]` | Update local state encoding to 4-bit integer |
| **J. Local Rule** | `methodology.tex` L39-43 | Dual Wolfram 8-bit rule lookup tables ($R_1, R_2$) with $\delta=13$ | 4-bit bijective local permutation lookup table | `[OBSOLETE]` | Replace Wolfram 8-bit rules with 4-bit bijective lookup table |
| **K. Standard Partition** | `architecture.tex` | Not mentioned | Non-overlapping $2 \times 2$ Margolus partition starting at grid origin (0,0) | `[NEEDS UPDATE]` | Document standard Margolus partition |
| **L. Shifted Partition** | `architecture.tex` | Not mentioned | Shifted $2 \times 2$ Margolus partition offset by 1 cell in row/col with wrapping | `[NEEDS UPDATE]` | Document shifted Margolus partition with periodic wrapping |
| **M. Circular Shift** | `methodology.tex` L57-63 | Keyed byte-level circular right rotation $\text{ROTR}_8(y_1, \alpha)$ | 2D circular matrix shift **DOWN 2** and **RIGHT 2** after EVERY round | `[OBSOLETE]` | Update shift specification to 2D circular matrix shift (DOWN 2, RIGHT 2) |
| **N. Round Count** | `architecture.tex` L39 | Single-pass byte iteration | Exactly 10 reversible CA rounds ($R = 10$) | `[OBSOLETE]` | Update round parameter to $R = 10$ |
| **O. Key Mixing** | `architecture.tex` L41 | CTR mode keystream XOR ($CT = T \oplus KS$) | Direct block XOR of 256-bit CA-transformed block with $K_{256}$ | `[OBSOLETE]` | Update key mixing description to $K_{256}$ XOR |
| **P. Ciphertext Format** | `architecture.tex` L43 | JSON EncryptedPackage (Version, Salt, Nonce, CT, Tag) | Base64 string prefixed with `REV-CA-V1:` | `[OBSOLETE]` | Update ciphertext representation to Base64 string with `REV-CA-V1:` prefix |
| **Q. Decryption** | `architecture.tex` L59-74 | HMAC tag check, CTR keystream XOR, inverse byte permutation | Reverse XOR $K_{256}$, 10 reverse rounds (shift UP 2/LEFT 2, inv Margolus), length extract | `[OBSOLETE]` | Replace decryption pipeline with Candidate C 10-round inverse sequence |

---

## SECTION 3 — OLD ALGORITHM MATERIAL AUDIT

All occurrences of obsolete components in the paper latex sources:

| Paper File | Text / Concept Found | Why Inconsistent | Replacement Needed? |
|---|---|---|---|
| `abstract.tex` L2 | `KDR-CA-AEAD` | Obsolete cipher name | YES — Replace title/name |
| `abstract.tex` L2 | `HKDF-SHA256` | Active scheme uses SHA-512 digest, no HKDF | YES — Remove HKDF |
| `abstract.tex` L2 | `HMAC-SHA256 Encrypt-then-MAC` | Active scheme uses SHA-512 K256 + 256b CA + XOR | YES — Remove HMAC |
| `abstract.tex` L3 | `Candidate A-Chain` | Active scheme uses Candidate C ($R=10$, shift (2,2)) | YES — Replace with Candidate C |
| `abstract.tex` L3 | `Wolfram 8-bit lookup coupling` | Active scheme uses 4-bit bijective local rule | YES — Replace rule description |
| `abstract.tex` L3 | `delta = 13` | Obsolete 1D offset index | YES — Remove delta index |
| `abstract.tex` L4 | `inter-byte feedback state chaining` | Active scheme uses 2D spatial block CA | YES — Remove inter-byte chaining |
| `abstract.tex` L4 | `keyed circular bit rotations` | Active scheme uses 2D matrix shift (2,2) | YES — Replace with matrix shift |
| `abstract.tex` L4 | `13.37 MB/s` | Obsolete stream throughput measurement | YES — Replace with block execution latency |
| `abstract.tex` L4 | `SAC ratios of 50.12%` | Obsolete 1D cipher SAC value | YES — Replace with Step 13 Candidate C values |
| `introduction.tex` L10 | `KDR-CA-AEAD` | Obsolete cipher name | YES — Replace |
| `introduction.tex` L8 | `Wolfram 8-bit rule numbers (0-255)` | Active scheme uses 4-bit bijective local rule | YES — Replace |
| `introduction.tex` L25 | `Candidate A-Chain` | Active scheme uses Candidate C | YES — Replace |
| `introduction.tex` L26 | `HKDF-SHA256` | Active scheme uses SHA-512 | YES — Replace |
| `methodology.tex` L4-14 | HKDF-Expand & HKDF-Extract equations | Active scheme uses SHA-512 first 256 bits | YES — Replace equations |
| `methodology.tex` L16-44 | 1D ECA Evaluation equations ($S_{\text{ECA}}$, $\delta=13$) | Active scheme uses 2D $16 \times 16$ binary matrix | YES — Replace equations |
| `methodology.tex` L45-74 | Candidate A-Chain byte state permutation & $\text{ROTR}_8$ | Active scheme uses 10-round Candidate C | YES — Replace equations |
| `methodology.tex` L75-86 | Reversible inverse byte permutation & $\text{ROTL}_8$ | Active scheme uses Candidate C inverse | YES — Replace equations |
| `architecture.tex` L6 | 5 modular subsystems (HKDF, Dynamic Rule, etc.) | Active architecture uses SHA-512 + 256b CA + XOR | YES — Replace architecture |
| `architecture.tex` L26-45 | Algorithm 1 (EncryptedPackage, HKDF, HMAC CTR) | Active scheme uses Candidate C 10-round CA | YES — Replace Algorithm 1 |
| `architecture.tex` L58-74 | Algorithm 2 (HMAC tag check, CTR decrypt) | Active scheme uses Candidate C 10-round inverse | YES — Replace Algorithm 2 |
| `security_analysis.tex` L23-25 | NIST Monobit (0.5210), Runs (0.4890), Chi-Square (248.50) | Belongs to obsolete 1D stream cipher | YES — Replace with Step 13 data |
| `security_analysis.tex` L35 | Shannon entropy = 7.998 bits/byte | Belongs to obsolete 1D stream cipher | YES — Replace with Step 13 data |
| `security_analysis.tex` L55-56 | SAC Plaintext = 50.12%, Key SAC = 49.88% | Belongs to obsolete 1D stream cipher | YES — Replace with Step 13 data |
| `security_analysis.tex` L67 | Pearson correlation = 0.0018 | Belongs to obsolete 1D stream cipher | YES — Replace with Step 13 data |
| `security_analysis.tex` L72-76 | Attack bounds referencing HKDF, HMAC, inter-byte | Belongs to obsolete 1D stream cipher | YES — Rewrite attack bounds |
| `security_analysis.tex` L82-97 | Table I (Master Security Summary with old values) | Belongs to obsolete 1D stream cipher | YES — Replace Table I |
| `benchmarks.tex` L33-46 | Table II (Benchmark Summary: 13.37 MB/s) | Belongs to obsolete 1D stream cipher | YES — Replace Table II |
| `benchmarks.tex` L75-86 | Table III (Comparative Performance vs AES-GCM) | Belongs to obsolete 1D stream cipher | YES — Replace Table III |
| `discussion.tex` L6-26 | Strengths & trade-offs referencing HKDF, EtM, S-boxes | Belongs to obsolete 1D stream cipher | YES — Rewrite discussion |
| `future_work.tex` L7 | SystemVerilog cores for Candidate A-Chain | Belongs to obsolete Candidate A-Chain | YES — Update future work |
| `conclusion.tex` L1-7 | Conclusion summarizing KDR-CA-AEAD, HKDF, HMAC | Belongs to obsolete 1D stream cipher | YES — Rewrite conclusion |
| `appendix/appendix.tex` L1-24 | Appendix A & B proofs for 1D ECA and HKDF | Belongs to obsolete 1D stream cipher | YES — Replace Appendix proofs |

---

## SECTION 4 — FINAL CA RULE AUDIT

### Implementation Verification:
- **Module Path:** [`margolus_ca.py`](file:///c:/Users/chntn/Downloads/SHA---V0-main/SHA---V0-main/margolus_ca.py)
- **Forward 4-bit Bijective Lookup Rule:**
  ```python
  FORWARD_RULE = [
      0xE, 0x4, 0xB, 0x2, 0x3, 0x8, 0x0, 0x9,
      0x1, 0xA, 0x7, 0xF, 0x6, 0xC, 0x5, 0xD
  ]
  ```
- **Inverse 4-bit Bijective Lookup Rule:**
  ```python
  INVERSE_RULE = [
      0x6, 0x8, 0x3, 0x4, 0x1, 0xE, 0xC, 0xA,
      0x5, 0x7, 0x9, 0x2, 0xD, 0xF, 0x0, 0xB
  ]
  ```

### Current Paper Status:
- The current paper does **NOT** contain this 4-bit rule table. It describes 1D Wolfram 8-bit lookup rules ($R_1, R_2$).
- Status: `[REQUIRES VERIFICATION]`  
  *Rule attribution:* The 4-bit lookup table is a validated bijective permutation on 4-bit states ($0 \dots 15$). The revised paper must explicitly present this exact lookup table without adding unverified promotional tags (such as "PICCOLO", "optimal", "best", or "superior").

---

## SECTION 5 — MARGOLUS PARTITION AUDIT

### Implementation Verification:
- **Standard Partition (`apply_margolus_forward` in `margolus_ca.py`):**
  - Non-overlapping $2 \times 2$ blocks starting at row 0, col 0.
  - Matrix dimensions: $16 \times 16$ (256 bits).
  - Neighborhood count: 64 distinct $2 \times 2$ neighborhoods per round.
  - Every cell covered exactly once per partition.
- **Shifted Partition (`apply_shifted_margolus_forward` in `margolus_shifted.py`):**
  - Shifted by 1 cell in both row and column directions (top-left at $(15, 15)$ with periodic modulo-16 wrapping).
  - Neighborhood count: 64 distinct $2 \times 2$ neighborhoods per round.
  - Every cell covered exactly once per partition.

### Current Paper Status:
- The current paper does **NOT** describe Margolus partitioning. It describes 1D ECA 3-cell Wolfram neighborhoods.
- Status: `[NEEDS UPDATE]` — The paper requires a new dedicated subsection and visual diagram illustrating standard and shifted $2 \times 2$ Margolus partitioning on a $16 \times 16$ grid.

---

## SECTION 6 — CIRCULAR SHIFT AUDIT

### Implementation Verification:
- **Forward Circular Matrix Shift (`circular_shift_matrix` in `ca_transform.py`):**
  - Shift amount: **DOWN 2** rows, **RIGHT 2** columns.
  - Formula: `shifted[r][c] = matrix[(r - 2) % 16][(c - 2) % 16]`
  - Applied: **After EVERY CA round** (all 10 rounds).
- **Inverse Circular Matrix Shift (`inverse_circular_shift_matrix` in `ca_transform.py`):**
  - Shift amount: **UP 2** rows, **LEFT 2** columns.
  - Formula: `restored[r][c] = shifted[(r + 2) % 16][(c + 2) % 16]`
  - Applied: **Before EVERY inverse CA round** (reverse order 10..1).

### Current Paper Status:
- Current paper describes a byte-level circular right rotation $\text{ROTR}_8(y_1, \alpha)$.
- Status: `[OBSOLETE]` — Paper must be updated to specify the 2D circular matrix shift (DOWN 2, RIGHT 2) per round.

---

## SECTION 7 — ROUND COUNT AUDIT

### Implementation Verification:
- **Fixed Engineering Selection:** $R = 10$ rounds.

### Empirical Measurements from Step 13 (`step13_final_round_results.csv`):

| Round Count ($R$) | Evaluated Role | Changed Bits Mean | Bit Avalanche (%) | Byte NPCR (%) | Byte UACI (%) | Enc Time / Block (ms) | Reversibility Pass |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2** | Selection Candidate | 4.12 bits | 1.61% | 9.47% | 1.40% | 0.390 ms | 100% |
| **4** | Selection Candidate | 12.25 bits | 4.79% | 22.00% | 3.57% | 0.752 ms | 100% |
| **6** | Selection Candidate | 27.08 bits | 10.58% | 41.22% | 8.68% | 1.145 ms | 100% |
| **8** | Selection Candidate | 53.09 bits | 20.74% | 64.50% | 15.27% | 1.509 ms | 100% |
| **10** | **Selected Production Configuration** | **81.92 bits** | **32.00%** | **84.62%** | **22.83%** | **1.899 ms** | **100%** |
| **16** | Observation Only | 125.71 bits | 49.11% | 99.16% | 33.06% | 2.960 ms | 100% |

### Current Paper Status:
- Current paper contains no round-count specification for 2D block CA.
- Status: `[OBSOLETE]` — Paper must be updated to present $R = 10$ as the selected architecture, backed by the Step 13 round-count trade-off table.

---

## SECTION 8 — EXPERIMENTAL RESULTS AUDIT

| Metric / Table in Current Paper | Current Paper Value | Source / Step 13-14 Value | Consistent? | Required Action |
|---|---|---|---|---|
| **Entropy** (`security_analysis.tex` L35) | 7.998 bits/byte | Evaluated per 256-bit block | NO | Mark for replacement with Step 13 block diffusion metrics |
| **Bit Avalanche** (`security_analysis.tex` L55) | 50.12% | 32.00% ($81.92\text{ bits}$) at $R=10$ | NO | Replace with empirical Step 13 Candidate C avalanche table |
| **Key Avalanche** (`security_analysis.tex` L56) | 49.88% | Evaluated via K256 XOR | NO | Replace with Step 13 Candidate C key mixing evaluation |
| **Pearson Correlation** (`security_analysis.tex` L67) | 0.0018 | Measured across Candidate C blocks | NO | Replace with Candidate C block correlation analysis |
| **Encryption Throughput** (`benchmarks.tex` L44) | 13.37 MB/s | $1.899\text{ ms / 256b block}$ ($0.526\text{ MB/s}$ Python) | NO | Replace with Candidate C block execution latency table |
| **Table I** (`security_analysis.tex` L82-97) | Old KDR-CA-AEAD master summary | Step 13 Candidate C round-count summary table | NO | Replace Table I with Step 13 Candidate C results table |
| **Table II** (`benchmarks.tex` L33-46) | Old micro-benchmark table | Step 13 Candidate C execution latency vs $R$ | NO | Replace Table II with Step 13 round latency table |
| **Table III** (`benchmarks.tex` L75-86) | Old comparison vs AES-GCM | Comparative round scaling table | NO | Replace Table III with Candidate C round scaling table |

---

## SECTION 9 — SECURITY ANALYSIS AUDIT

### Subjective & Overstated Claims in Current Paper:
1. `"ultra-secure"` (`introduction.tex` L4) $\rightarrow$ `[REMOVE/REPLACE]`  
   *Action:* Replace with objective engineering description of encryption strength.
2. `"robust non-linear cryptographic security"` (`abstract.tex` L2) $\rightarrow$ `[REQUIRES QUALIFICATION]`  
   *Action:* Qualify by referencing measured non-linear bit diffusion and loss-less reversibility.
3. `"IND-CCA2 security"` (`discussion.tex` L10) $\rightarrow$ `[UNSUPPORTED]`  
   *Action:* Remove IND-CCA2 claim, as active research algorithm is SHA-512 + 256-bit CA + XOR without an AEAD tag.
4. `"unbreakable" / "optimal" / "superior"` $\rightarrow$ `[REMOVE/REPLACE]`  
   *Action:* Enforce strict non-promotional, neutral language throughout.

### Classification of Empirical vs Formal Security:
- **Measured Diffusion & Reversibility:** Supported by Step 13 empirical measurements ($32.00\%$ avalanche, $84.62\%$ byte NPCR, 100/100 reversibility).
- **Formal Cryptanalytic Proofs:** The revised paper must explicitly distinguish measured statistical properties from formal proofs of resistance against differential/linear cryptanalysis.

---

## SECTION 10 — FIGURE AUDIT

| Figure # | Current Paper Figure | Current Content | Required Status | Action for Paper Update Phase |
|:---:|---|---|---|---|
| **Fig. 1** | `fig:system_arch` | KDR-CA-AEAD 5-Layer Subsystem Architecture | `[OBSOLETE]` | Replace with SHA-512 + 256-bit CA + XOR system diagram |
| **Fig. 2** | `fig:encryption_flow` | KDR-CA-AEAD Encryption Workflow | `[OBSOLETE]` | Replace with Candidate C 10-round encryption workflow |
| **Fig. 3** | `fig:decryption_flow` | KDR-CA-AEAD Decryption Workflow | `[OBSOLETE]` | Replace with Candidate C 10-round decryption workflow |
| **Fig. 4** | `fig:dynamic_ca_engine` | Candidate A-Chain Dynamic CA Engine | `[OBSOLETE]` | Replace with $16 \times 16$ Matrix & 2D Margolus Partition diagram |
| **Fig. 5** | `fig:key_schedule` | HKDF-SHA256 Domain Key Schedule | `[OBSOLETE]` | Replace with SHA-512 $K_{256}$ Key Derivation diagram |
| **Fig. 6** | `fig:auth_enc_pipeline` | Encrypt-then-MAC Core Pipeline | `[OBSOLETE]` | Replace with 4-bit Bijective Local Rule transition diagram |
| **Fig. 7** | `fig:sec_val_flow` | Security Validation Workflow | `[OBSOLETE]` | Replace with Step 13 Round-Count Diffusion Plot |
| **Fig. 8** | `fig:nist_summary` | NIST SP 800-22 Test Results | `[OBSOLETE]` | Replace with Step 13 Avalanche & NPCR Scaling Plot |
| **Fig. 9** | `fig:avalanche` | SAC Bit Flip Ratios Plot | `[OBSOLETE]` | Replace with Candidate C Bit Avalanche vs Round Count plot |
| **Fig. 10** | `fig:bm_pipeline` | Benchmarking Pipeline | `[OBSOLETE]` | Replace with Healthcare EHR Telemetry Application UI figure |

---

## SECTION 11 — TABLE AUDIT

| Table # | Location | Current Caption / Purpose | Current Status | Action |
|:---:|---|---|---|---|
| **Table I** | `security_analysis.tex` L82-97 | Master Security & Randomness Empirical Summary | `[OBSOLETE]` | Replace with Step 13 Candidate C summary table ($R=2 \dots 10$) |
| **Table II** | `benchmarks.tex` L33-46 | Performance Benchmark Summary (64B to 1MB) | `[OBSOLETE]` | Replace with Candidate C block execution latency table |
| **Table III** | `benchmarks.tex` L75-86 | Comparative Performance & Security Bounds | `[OBSOLETE]` | Replace with Candidate C round-count scaling & metrics table |
| **Table** | `tables/comparative_table.tex` | Legacy standalone comparative table | `[OBSOLETE]` | Replace with Candidate C comparative table |
| **Table** | `tables/master_security_table.tex` | Legacy standalone master security table | `[OBSOLETE]` | Replace with Candidate C master security table |
| **Table** | `tables/performance_scaling_table.tex` | Legacy standalone performance scaling table | `[OBSOLETE]` | Replace with Candidate C performance scaling table |

---

## SECTION 12 — REFERENCE AUDIT

### Reference Categories in `references.bib`:
1. **Cellular Automata Foundation:**  
   - Wolfram (1983, 1986), Gutowitz (1993), Nandi et al. (1994) $\rightarrow$ `[RETAIN]`
2. **Cryptographic Evaluation Metrics:**  
   - Webster & Tavares (1985 SAC), Shannon (1949 Entropy), Biham & Shamir (1991 Differential), Matsui (1993 Linear) $\rightarrow$ `[RETAIN]`
3. **Reference Ciphers & Standards:**  
   - Daemen & Rijmen (2002 AES), Bernstein (2008 ChaCha20) $\rightarrow$ `[RETAIN]`
4. **Obsolete AEAD & HKDF References:**  
   - Krawczyk (RFC 5869 HKDF), Rogaway (2011 AEAD), Bellare (2000 EtM), Dworkin (NIST SP 800-38D AES-GCM), Nir (RFC 8439 ChaCha20) $\rightarrow$ `[MARK FOR AUDIT]` (To be revised or removed during paper rewrite).
5. **Missing Essential References:**  
   - **SHA-512 Standard:** NIST FIPS 180-4 (Secure Hash Standard).
   - **Margolus Cellular Automata:** Margolus (1984, 1987) block cellular automata partitioning.

---

## SECTION 13 — CODE–PAPER GAP LIST

### PRIORITY 1 — MUST CHANGE (Core Algorithm Realignment)
1. Title, Abstract, Introduction, and Methodology must be updated to remove KDR-CA-AEAD, HKDF, HMAC, AES, nonces, and 1D ECA rules.
2. Core encryption equations must be rewritten to describe SHA-512 $K_{256}$ derivation, 32-bit length header, 256-bit block framing, $16 \times 16$ binary matrix mapping, 10-round Candidate C Margolus CA, and XOR key mixing.
3. Rotation equations ($\text{ROTR}_8$) must be replaced with 2D circular matrix shift (DOWN 2, RIGHT 2).

### PRIORITY 2 — MUST UPDATE (Empirical Results & Diagrams)
1. Replace all tables and figures in `paper/sections/` and `paper/tables/` with empirical data from `step13_final_round_results.csv` and Step 14 validation tests.
2. Update security analysis to reflect measured bit avalanche ($32.00\%$), byte NPCR ($84.62\%$), byte UACI ($22.83\%$), and 100/100 block reversibility at $R=10$.
3. Add explicit Margolus partitioning diagrams and $2 \times 2$ neighborhood state transition equations.

### PRIORITY 3 — SHOULD UPDATE (Background & Discussion)
1. Update Literature Review to focus on reversible block cellular automata, Margolus partitioning, and SHA-512 key schedules.
2. Update Discussion section to analyze trade-offs between round count $R$, spatial bit diffusion, reversibility, and computational latency.

### PRIORITY 4 — OPTIONAL (Formatting & Style)
1. Refine LaTeX captions, cross-references, and bibtex entry formatting.

---

## SECTION 14 — FINAL RECOMMENDED PAPER ARCHITECTURE

Proposed section-by-section rewrite map for the paper update phase:

```
Paper Title: SHA-512-Based 256-Bit Block Cellular Automata Cryptosystem for Secure Healthcare Telemetry

Abstract (sections/abstract.tex)
  ├── Remove: KDR-CA-AEAD, HKDF-SHA256, HMAC-SHA256, 1D Wolfram rules, 13.37 MB/s
  └── Insert: SHA-512 K256 key derivation, 256-bit block framing, 10-round Candidate C Margolus CA, (2,2) shift, 100% loss-less reversibility, R=10 diffusion metrics (32.00% avalanche, 84.62% byte NPCR)

Section I: Introduction (sections/introduction.tex)
  ├── Subsection I-A: Research Motivation (EHR telemetry security, low memory bounds)
  └── Subsection I-B: Contributions (SHA-512 + 256b 2D Margolus CA block cipher, loss-less reversibility, empirical round-count analysis)

Section II: Literature Review (sections/literature_review.tex)
  ├── Retain: CA cryptographic history (Wolfram, Gutowitz, Nandi)
  └── Add: Reversible block CA (Margolus partitioning) and SHA-512 key schedules

Section III: Mathematical Model & Primitives (sections/methodology.tex)
  ├── Subsection III-A: SHA-512 Key Generation & K256 Derivation
  ├── Subsection III-B: 256-Bit Block Framing & 16x16 Binary Matrix Mapping
  ├── Subsection III-C: 4-Bit Bijective Local Transition Rule
  ├── Subsection III-D: Standard & Shifted 2x2 Margolus Partitioning
  └── Subsection III-E: 2D Circular Matrix Shift (DOWN 2, RIGHT 2)

Section IV: Proposed System Architecture (sections/architecture.tex)
  ├── Subsection IV-A: Overall 10-Round Candidate C System Pipeline
  ├── Subsection IV-B: Forward Encryption Algorithm & Flowchart
  └── Subsection IV-C: Inverse Decryption Algorithm & Flowchart

Section V: Security Analysis & Statistical Validation (sections/security_analysis.tex)
  ├── Subsection V-A: Reversibility & Loss-Less Reconstruction Proof
  ├── Subsection V-B: Bit Avalanche & NPCR/UACI Round-Count Analysis (R=2..10)
  └── Subsection V-C: Key Mixing & Differential Propagation Bounds

Section VI: Performance Evaluation & Benchmarks (sections/benchmarks.tex)
  ├── Subsection VI-A: Block Execution Latency & Round-Count Scaling (R=2..10)
  └── Subsection VI-B: Healthcare EHR Record Telemetry Case Study

Section VII: Discussion & Trade-Off Analysis (sections/discussion.tex)
  └── Analysis of diffusion growth vs. execution latency across R=2..10

Section VIII: Future Work (sections/future_work.tex)
  └── Hardware FPGA prototyping of 2D Margolus partitions & post-quantum key exchange

Section IX: Conclusion (sections/conclusion.tex)
  └── Final summary of Candidate C 10-round reversible CA block cryptosystem

Appendices (appendix/appendix.tex)
  └── Formal mathematical proof of 100% loss-less reversibility for Candidate C
```

---

## SECTION 15 — INTEGRITY CHECK

### Integrity Confirmations:
- **No `.tex` files modified:** **CONFIRMED (0 files touched)**
- **No `.pdf` files modified:** **CONFIRMED (0 files touched)**
- **No production source files modified:** **CONFIRMED (0 files touched)**
- **No experimental CSV files modified:** **CONFIRMED (0 files touched)**
- **Only audit files created:** `step15_paper_code_audit.md` and `step15_paper_code_audit.csv`.

---

### Step 14 Integration & Cryptosystem Verification:
- Command 1: `py -m unittest tests/test_step14_integration.py`
- Command 2: `py -m unittest tests/test_research_crypto.py`
