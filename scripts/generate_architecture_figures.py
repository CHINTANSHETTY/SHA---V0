"""
Master Architecture Figures & Publication Graphics Generator for Phase 3.2.2.

Generates 8 high-quality, publication-ready vector and raster architecture figures:
1. system_architecture (.svg, .pdf, .png 300 DPI)
2. encryption_workflow (.svg, .pdf, .png 300 DPI)
3. decryption_workflow (.svg, .pdf, .png 300 DPI)
4. dynamic_ca_engine (.svg, .pdf, .png 300 DPI)
5. key_schedule (.svg, .pdf, .png 300 DPI)
6. authenticated_encryption_pipeline (.svg, .pdf, .png 300 DPI)
7. security_validation_flow (.svg, .pdf, .png 300 DPI)
8. benchmark_pipeline (.svg, .pdf, .png 300 DPI)

Usage:
    python scripts/generate_architecture_figures.py
"""

from __future__ import annotations

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Set global font family for consistent typography
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'

# IEEE Color Palette & Design Tokens
COLOR_PRIMARY = "#002B49"       # IEEE Dark Navy
COLOR_SECONDARY = "#1F77B4"     # IEEE Blue
COLOR_ACCENT = "#2CA02C"        # Emerald Green
COLOR_WARNING = "#FF7F0E"       # Warm Amber
COLOR_HIGHLIGHT = "#9467BD"     # Royal Purple
COLOR_BG_BOX = "#F8FAFC"        # Light Slate Blue
COLOR_BORDER = "#475569"        # Slate Gray Border
COLOR_TEXT = "#0F172A"          # Dark Slate Charcoal


def verify_image_resolution(path_png: str):
    """Verifies PNG resolution, pixel dimensions, and image size."""
    from PIL import Image
    with Image.open(path_png) as img:
        width, height = img.size
        dpi = img.info.get('dpi', (300, 300))
        if width < 1500 or height < 750:
            raise ValueError(f"Image {path_png} dimensions ({width}x{height}) below 300 DPI threshold.")
        print(f"  [VALIDATED PNG] {os.path.basename(path_png)} ({width}x{height} px, DPI: {dpi})")


def draw_rounded_box(ax, x, y, width, height, text, bg_color=COLOR_BG_BOX, border_color=COLOR_BORDER, fontsize=9, fontweight="bold", text_color=COLOR_TEXT, linestyle="-"):
    """Draws a styled rounded rectangle box with centered multi-line text."""
    rect = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        edgecolor=border_color,
        facecolor=bg_color,
        linestyle=linestyle
    )
    ax.add_patch(rect)
    cx = x + width / 2.0
    cy = y + height / 2.0
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize, fontweight=fontweight, color=text_color, multialignment="center")


def draw_arrow(ax, start, end, label="", color=COLOR_BORDER, linestyle="-", lw=1.2):
    """Draws a sleek arrow connection with optional label."""
    ax.annotate(
        "",
        xy=end, xycoords="data",
        xytext=start, textcoords="data",
        arrowprops=dict(arrowstyle="->", color=color, lw=lw, linestyle=linestyle, shrinkA=2, shrinkB=2)
    )
    if label:
        mx = (start[0] + end[0]) / 2.0
        my = (start[1] + end[1]) / 2.0
        ax.text(mx, my + 0.03, label, ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=color)


def save_figure(fig, fig_name):
    """Saves figure in SVG, PDF, and 300 DPI PNG formats."""
    path_svg = os.path.join(FIGURES_DIR, f"{fig_name}.svg")
    path_pdf = os.path.join(FIGURES_DIR, f"{fig_name}.pdf")
    path_png = os.path.join(FIGURES_DIR, f"{fig_name}.png")

    fig.savefig(path_svg, format="svg", bbox_inches="tight")
    fig.savefig(path_pdf, format="pdf", bbox_inches="tight")
    fig.savefig(path_png, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    verify_image_resolution(path_png)
    print(f"[EXPORTED FIGURE] {fig_name} -> .svg (Master), .pdf, .png (300 DPI)")


# =========================================================
# FIGURE 1: OVERALL SYSTEM ARCHITECTURE
# =========================================================
def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5, 5.7, "KDR-CA-AEAD Overall System Architecture", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    # Layers
    draw_rounded_box(ax, 0.5, 4.6, 9.0, 0.7, "User / Application Layer\n(EHR Diagnostics, Medical Telemetry, IoT Edge Sensors)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 0.5, 3.5, 9.0, 0.7, "Public API Layer (crypto)\n[encrypt_bytes() | decrypt_bytes() | encrypt_payload() | decrypt_payload()]", bg_color="#DBEAFE")

    # Core Engine Components
    draw_rounded_box(ax, 0.5, 2.0, 2.6, 1.0, "Key Management &\nHKDF Subkey Engine\n(K_r, K_c, K_a)", bg_color="#FEF3C7", border_color="#D97706")
    draw_rounded_box(ax, 3.7, 2.0, 2.6, 1.0, "Dynamic CA Engine &\nRule Scheduler (R1, R2)\n(Candidate A-Chain)", bg_color="#DCFCE7", border_color="#16A34A")
    draw_rounded_box(ax, 6.9, 2.0, 2.6, 1.0, "AEAD Integrity &\nHMAC-SHA256 Module\n(Tag Verification)", bg_color="#F3E8FF", border_color="#9333EA")

    # Output & Verification Layer
    draw_rounded_box(ax, 0.5, 0.5, 4.2, 0.8, "EncryptedPackage Output\n(Version, Salt, Nonce, CT, Tag)", bg_color="#E0F2FE")
    draw_rounded_box(ax, 5.3, 0.5, 4.2, 0.8, "Security Analysis & Benchmarking Subsystem\n(NIST SP 800-22, SAC Avalanche, Throughput)", bg_color="#FFEDD5")

    # Connectors
    draw_arrow(ax, (5.0, 4.6), (5.0, 4.2))
    draw_arrow(ax, (1.8, 3.5), (1.8, 3.0))
    draw_arrow(ax, (5.0, 3.5), (5.0, 3.0))
    draw_arrow(ax, (8.2, 3.5), (8.2, 3.0))
    draw_arrow(ax, (3.1, 2.5), (3.7, 2.5))
    draw_arrow(ax, (6.3, 2.5), (6.9, 2.5))
    draw_arrow(ax, (2.6, 2.0), (2.6, 1.3))
    draw_arrow(ax, (7.4, 2.0), (7.4, 1.3))

    save_figure(fig, "system_architecture")


# =========================================================
# FIGURE 2: ENCRYPTION WORKFLOW
# =========================================================
def generate_encryption_workflow():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "KDR-CA-AEAD Authenticated Encryption Workflow", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.4, 3.4, 1.8, 0.8, "Plaintext Input (P)\n+ Master Key (K)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 2.7, 3.4, 2.0, 0.8, "HKDF-SHA256\nSubkey Expansion", bg_color="#FEF3C7")
    draw_rounded_box(ax, 5.2, 3.4, 2.1, 0.8, "Dynamic Rule Selection\nR1, R2 (delta=13)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 7.8, 3.4, 1.8, 0.8, "Forward CA Permutation\n(Candidate A-Chain)", bg_color="#E0F2FE")

    draw_rounded_box(ax, 7.8, 1.8, 1.8, 0.8, "Transformed State\nVector (T)", bg_color="#F3E8FF")
    draw_rounded_box(ax, 5.2, 1.8, 2.1, 0.8, "CTR-PRNG Keystream\nGeneration (KS)", bg_color="#FEF3C7")
    draw_rounded_box(ax, 2.7, 1.8, 2.0, 0.8, "XOR Stream Encryption\nCT = T ^ KS", bg_color="#DCFCE7")
    draw_rounded_box(ax, 0.4, 1.8, 1.8, 0.8, "HMAC-SHA256 AEAD\nTag Computation", bg_color="#FFEDD5")

    draw_rounded_box(ax, 3.5, 0.4, 3.0, 0.8, "EncryptedPackage Deliverable\n(Salt || Nonce || CT || Tag)", bg_color="#DBEAFE")

    draw_arrow(ax, (2.2, 3.8), (2.7, 3.8))
    draw_arrow(ax, (4.7, 3.8), (5.2, 3.8))
    draw_arrow(ax, (7.3, 3.8), (7.8, 3.8))
    draw_arrow(ax, (8.7, 3.4), (8.7, 2.6))
    draw_arrow(ax, (7.8, 2.2), (7.3, 2.2))
    draw_arrow(ax, (5.2, 2.2), (4.7, 2.2))
    draw_arrow(ax, (2.7, 2.2), (2.2, 2.2))
    draw_arrow(ax, (1.3, 1.8), (1.3, 0.8))
    draw_arrow(ax, (1.3, 0.8), (3.5, 0.8))

    save_figure(fig, "encryption_workflow")


# =========================================================
# FIGURE 3: DECRYPTION WORKFLOW
# =========================================================
def generate_decryption_workflow():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "KDR-CA-AEAD Authenticated Decryption & Verification Workflow", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.4, 3.4, 1.8, 0.8, "EncryptedPackage\nInput (CT, Tag)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 2.7, 3.4, 2.0, 0.8, "HMAC Tag Check\n(Constant-Time)", bg_color="#FFEDD5")
    draw_rounded_box(ax, 5.2, 3.4, 2.1, 0.8, "HKDF Subkey Re-Deriv.\n(K_r, K_c, K_a)", bg_color="#FEF3C7")
    draw_rounded_box(ax, 7.8, 3.4, 1.8, 0.8, "CTR Keystream\nRegeneration (KS)", bg_color="#DCFCE7")

    draw_rounded_box(ax, 7.8, 1.8, 1.8, 0.8, "XOR Decryption\nT = CT ^ KS", bg_color="#E0F2FE")
    draw_rounded_box(ax, 5.2, 1.8, 2.1, 0.8, "Rule Table Reconstruct.\nR1, R2 (delta=13)", bg_color="#F3E8FF")
    draw_rounded_box(ax, 2.7, 1.8, 2.0, 0.8, "Inverse CA Permut.\n(Candidate A-Chain)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 0.4, 1.8, 1.8, 0.8, "Plaintext Payload\nRecovery (P)", bg_color="#DBEAFE")

    draw_rounded_box(ax, 2.7, 0.4, 4.6, 0.8, "Verification Result: PASS (Authentic) / FAIL (Abort)", bg_color="#E0F2FE")

    draw_arrow(ax, (2.2, 3.8), (2.7, 3.8))
    draw_arrow(ax, (4.7, 3.8), (5.2, 3.8))
    draw_arrow(ax, (7.3, 3.8), (7.8, 3.8))
    draw_arrow(ax, (8.7, 3.4), (8.7, 2.6))
    draw_arrow(ax, (7.8, 2.2), (7.3, 2.2))
    draw_arrow(ax, (5.2, 2.2), (4.7, 2.2))
    draw_arrow(ax, (2.7, 2.2), (2.2, 2.2))
    draw_arrow(ax, (1.3, 1.8), (1.3, 0.8))
    draw_arrow(ax, (1.3, 0.8), (2.7, 0.8))

    save_figure(fig, "decryption_workflow")


# =========================================================
# FIGURE 4: DYNAMIC CELLULAR AUTOMATA ENGINE
# =========================================================
def generate_dynamic_ca_engine():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis("off")

    ax.text(5, 5.2, "Candidate A-Chain Dynamic Cellular Automata Permutation Engine", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.5, 3.8, 2.2, 0.9, "Plaintext Byte (P_i)\n+ Feedback IV (prev_state)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 3.2, 3.8, 2.4, 0.9, "32 uint8 Rule Table (R)\n[r_0, r_1, ..., r_31]", bg_color="#FEF3C7")
    draw_rounded_box(ax, 6.1, 3.8, 3.4, 0.9, "Dynamic Dual-Rule Selection\nR1 = R[i % 32], R2 = R[(i+13) % 32]", bg_color="#DCFCE7")

    draw_rounded_box(ax, 0.5, 2.2, 2.8, 1.0, "Step 1: State Chaining & Mod\ny1 = ((P_i ^ prev_state) + S_ECA) % 256", bg_color="#E0F2FE")
    draw_rounded_box(ax, 3.6, 2.2, 2.8, 1.0, "Step 2: Keyed Circular Shift\ny2 = ROTR_8(y1, (R1 % 7) + 1)", bg_color="#F3E8FF")
    draw_rounded_box(ax, 6.7, 2.2, 2.8, 1.0, "Step 3: XOR Rule Mixing\nT_i = y2 ^ R2", bg_color="#FFEDD5")

    draw_rounded_box(ax, 2.5, 0.6, 5.0, 0.9, "Transformed State Output (T_i) -> Update Feedback Vector (prev_state = T_i)", bg_color="#DBEAFE")

    draw_arrow(ax, (2.7, 4.25), (3.2, 4.25))
    draw_arrow(ax, (5.6, 4.25), (6.1, 4.25))
    draw_arrow(ax, (1.9, 3.8), (1.9, 3.2))
    draw_arrow(ax, (3.3, 2.7), (3.6, 2.7))
    draw_arrow(ax, (6.4, 2.7), (6.7, 2.7))
    draw_arrow(ax, (8.1, 2.2), (8.1, 1.5))
    draw_arrow(ax, (8.1, 1.5), (7.5, 1.5))

    save_figure(fig, "dynamic_ca_engine")


# =========================================================
# FIGURE 5: KEY SCHEDULE DIAGRAM
# =========================================================
def generate_key_schedule():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "HKDF-SHA256 Domain-Separated Key Schedule Architecture", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.5, 3.4, 2.5, 0.8, "Master Key (K: 256 bits)\n+ CSPRNG Salt (S: 16B)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 3.6, 3.4, 2.8, 0.8, "HKDF-Extract(Salt, IKM=K)\n-> PRK (32 Bytes)", bg_color="#FEF3C7")
    draw_rounded_box(ax, 7.0, 3.4, 2.5, 0.8, "Nonce Context (N: 12B)\nPer-Message Freshness", bg_color="#E0F2FE")

    draw_rounded_box(ax, 0.5, 1.8, 2.7, 1.0, "Rule Seed Subkey (K_r)\nHKDF-Expand(PRK, 'ca-rules|' || N)\n-> 32 uint8 CA Rules", bg_color="#DCFCE7")
    draw_rounded_box(ax, 3.65, 1.8, 2.7, 1.0, "Cipher Keystream Key (K_c)\nHKDF-Expand(PRK, 'cipher-key|' || N)\n-> HMAC CTR PRNG", bg_color="#F3E8FF")
    draw_rounded_box(ax, 6.8, 1.8, 2.7, 1.0, "MAC Authentication Key (K_a)\nHKDF-Expand(PRK, 'mac-key|' || N)\n-> HMAC AEAD Tag", bg_color="#FFEDD5")

    draw_rounded_box(ax, 2.0, 0.4, 6.0, 0.8, "Cryptographically Independent Subkeys (K_r, K_c, K_a) Domain Separation", bg_color="#DBEAFE")

    draw_arrow(ax, (3.0, 3.8), (3.6, 3.8))
    draw_arrow(ax, (7.0, 3.8), (6.4, 3.8))
    draw_arrow(ax, (5.0, 3.4), (1.85, 2.8))
    draw_arrow(ax, (5.0, 3.4), (5.0, 2.8))
    draw_arrow(ax, (5.0, 3.4), (8.15, 2.8))
    draw_arrow(ax, (1.85, 1.8), (3.0, 1.2))
    draw_arrow(ax, (5.0, 1.8), (5.0, 1.2))
    draw_arrow(ax, (8.15, 1.8), (7.0, 1.2))

    save_figure(fig, "key_schedule")


# =========================================================
# FIGURE 6: AUTHENTICATED ENCRYPTION PIPELINE
# =========================================================
def generate_authenticated_encryption_pipeline():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "Encrypt-then-MAC (EtM) Authenticated Encryption Pipeline", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.5, 3.4, 2.5, 0.8, "Inputs: Plaintext (P)\n+ Associated Data (AD)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 3.5, 3.4, 3.0, 0.8, "Dynamic CA Permutation (T)\n+ HMAC-SHA256 CTR Keystream (KS)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 7.0, 3.4, 2.5, 0.8, "Stream Ciphertext Output\nCT = T ^ KS", bg_color="#E0F2FE")

    draw_rounded_box(ax, 2.0, 1.8, 6.0, 1.0, "HMAC-SHA256 Tag Computation Core\nTag = HMAC(K_a, Nonce || Salt || AssociatedData || Ciphertext)", bg_color="#FFEDD5", border_color="#D97706")

    draw_rounded_box(ax, 1.5, 0.4, 7.0, 0.8, "EncryptedPackage: [Version='KDR-CA-AEAD-v1' | Salt | Nonce | CT | 32B Tag]", bg_color="#DBEAFE")

    draw_arrow(ax, (3.0, 3.8), (3.5, 3.8))
    draw_arrow(ax, (6.5, 3.8), (7.0, 3.8))
    draw_arrow(ax, (8.25, 3.4), (8.25, 2.3))
    draw_arrow(ax, (8.25, 2.3), (8.0, 2.3))
    draw_arrow(ax, (5.0, 1.8), (5.0, 1.2))

    save_figure(fig, "authenticated_encryption_pipeline")


# =========================================================
# FIGURE 7: SECURITY VALIDATION FLOW
# =========================================================
def generate_security_validation_flow():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "Statistical Randomness & Security Validation Workflow", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.4, 3.4, 1.8, 0.8, "Ciphertext Stream\nSample Collection", bg_color="#E2E8F0")
    draw_rounded_box(ax, 2.7, 3.4, 2.0, 0.8, "NIST SP 800-22\nMonobit & Runs Tests", bg_color="#FEF3C7")
    draw_rounded_box(ax, 5.2, 3.4, 2.1, 0.8, "Shannon Entropy\nAnalysis (H >= 7.90)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 7.8, 3.4, 1.8, 0.8, "SAC Avalanche Test\n(50.0% Bit Flip)", bg_color="#E0F2FE")

    draw_rounded_box(ax, 7.8, 1.8, 1.8, 0.8, "Pearson Correlation\nScatter (r ~ 0.00)", bg_color="#F3E8FF")
    draw_rounded_box(ax, 5.2, 1.8, 2.1, 0.8, "Cryptanalytic Bounds\n(Brute-force 2^256)", bg_color="#FFEDD5")
    draw_rounded_box(ax, 2.7, 1.8, 2.0, 0.8, "Tamper Rejection\n(100% Forgery Rejection)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 0.4, 1.8, 1.8, 0.8, "Statistical Validation\nPassed (All p >= 0.01)", bg_color="#DBEAFE")

    draw_rounded_box(ax, 2.7, 0.4, 4.6, 0.8, "Master Security Dataset (master_results.json & CSV Tables)", bg_color="#FEF3C7")

    draw_arrow(ax, (2.2, 3.8), (2.7, 3.8))
    draw_arrow(ax, (4.7, 3.8), (5.2, 3.8))
    draw_arrow(ax, (7.3, 3.8), (7.8, 3.8))
    draw_arrow(ax, (8.7, 3.4), (8.7, 2.6))
    draw_arrow(ax, (7.8, 2.2), (7.3, 2.2))
    draw_arrow(ax, (5.2, 2.2), (4.7, 2.2))
    draw_arrow(ax, (2.7, 2.2), (2.2, 2.2))
    draw_arrow(ax, (1.3, 1.8), (1.3, 0.8))
    draw_arrow(ax, (1.3, 0.8), (2.7, 0.8))

    save_figure(fig, "security_validation_flow")


# =========================================================
# FIGURE 8: BENCHMARK PIPELINE
# =========================================================
def generate_benchmark_pipeline():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "Empirical Micro-Benchmarking & Performance Evaluation Pipeline", ha="center", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)

    draw_rounded_box(ax, 0.4, 3.4, 1.8, 0.8, "Test Datasets\n(64B to 1MB)", bg_color="#E2E8F0")
    draw_rounded_box(ax, 2.7, 3.4, 2.0, 0.8, "Encryption Benchmark\n(100 Iterations)", bg_color="#FEF3C7")
    draw_rounded_box(ax, 5.2, 3.4, 2.1, 0.8, "Decryption Benchmark\n(95% CI Margins)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 7.8, 3.4, 1.8, 0.8, "Throughput Metrics\n(MB/s Scaling)", bg_color="#E0F2FE")

    draw_rounded_box(ax, 7.8, 1.8, 1.8, 0.8, "Latency Metrics\n(Execution ms)", bg_color="#F3E8FF")
    draw_rounded_box(ax, 5.2, 1.8, 2.1, 0.8, "Memory Allocation\nTracing (Peak KB)", bg_color="#FFEDD5")
    draw_rounded_box(ax, 2.7, 1.8, 2.0, 0.8, "CPU Overhead\n(us / Byte Cost)", bg_color="#DCFCE7")
    draw_rounded_box(ax, 0.4, 1.8, 1.8, 0.8, "Comparative Analysis\n(AES-GCM / ChaCha)", bg_color="#DBEAFE")

    draw_rounded_box(ax, 2.7, 0.4, 4.6, 0.8, "Consolidated Benchmark Dataset (benchmark_summary.csv & IEEE Plots)", bg_color="#FEF3C7")

    draw_arrow(ax, (2.2, 3.8), (2.7, 3.8))
    draw_arrow(ax, (4.7, 3.8), (5.2, 3.8))
    draw_arrow(ax, (7.3, 3.8), (7.8, 3.8))
    draw_arrow(ax, (8.7, 3.4), (8.7, 2.6))
    draw_arrow(ax, (7.8, 2.2), (7.3, 2.2))
    draw_arrow(ax, (5.2, 2.2), (4.7, 2.2))
    draw_arrow(ax, (2.7, 2.2), (2.2, 2.2))
    draw_arrow(ax, (1.3, 1.8), (1.3, 0.8))
    draw_arrow(ax, (1.3, 0.8), (2.7, 0.8))

    save_figure(fig, "benchmark_pipeline")


def main():
    print("=" * 70)
    print("GENERATING KDR-CA-AEAD PHASE 3.2.2 PUBLICATION FIGURES")
    print("=" * 70)

    generate_system_architecture()
    generate_encryption_workflow()
    generate_decryption_workflow()
    generate_dynamic_ca_engine()
    generate_key_schedule()
    generate_authenticated_encryption_pipeline()
    generate_security_validation_flow()
    generate_benchmark_pipeline()

    print("\n[SUCCESS] All 8 architecture figures generated in SVG, PDF, and 300 DPI PNG formats.")
    print("=" * 70)


if __name__ == "__main__":
    main()
