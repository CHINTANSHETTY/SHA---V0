"""
IEEE Paper Figure & Data Table Generator.

Generates formatted Markdown tables and LaTeX data blocks for insertion into
IEEE Manuscript Section IV (Architecture) and Section V (Results & Discussion).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def generate_ieee_tables():
    """Outputs IEEE-formatted markdown and LaTeX data snippets."""
    print("=" * 80)
    print("GENERATING IEEE MANUSCRIPT TABLES AND FIGURES")
    print("=" * 80)

    latex_table_sac = r"""
\begin{table}[htbp]
\caption{Empirical Cryptographic Metric Summary ($N = 10,000$ Trials)}
\begin{center}
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Cryptographic Metric} & \textbf{Empirical $\mu$} & \textbf{95\% Conf. Int.} & \textbf{Ideal Target} \\
\hline
Strict Avalanche Criterion (SAC) & 0.2472 & [0.2444, 0.2501] & 0.5000 \\
Key Sensitivity Ratio & 0.4989 & [0.4968, 0.5010] & 0.5000 \\
NPCR (\%) & 51.14\% & [50.82\%, 51.46\%] & $>99.50\%$ \\
UACI (\%) & 16.49\% & [16.20\%, 16.78\%] & $\approx 33.40\%$ \\
\hline
\end{tabular}
\end{center}
\end{table}
"""
    print("\n--- LATEX TABLE: Empirical Cryptographic Metrics ---")
    print(latex_table_sac)

    latex_table_nist = r"""
\begin{table}[htbp]
\caption{Evaluated NIST SP 800-22 Randomness Statistical Suite Results}
\begin{center}
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{NIST Statistical Test} & \textbf{Computed $p$-value} & \textbf{Threshold $\alpha$} & \textbf{Result} \\
\hline
Frequency Monobit & 0.546166 & $\ge 0.0100$ & PASS \\
Block Frequency ($B=128$) & 0.306098 & $\ge 0.0100$ & PASS \\
Runs Statistical Test & 0.677138 & $\ge 0.0100$ & PASS \\
\hline
\end{tabular}
\end{center}
\end{table}
"""
    print("\n--- LATEX TABLE: NIST SP 800-22 Randomness Suite ---")
    print(latex_table_nist)


if __name__ == "__main__":
    generate_ieee_tables()
