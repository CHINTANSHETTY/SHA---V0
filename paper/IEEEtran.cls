% IEEEtran.cls - Standard IEEE Document Class
% Distributed under the LaTeX Project Public License (LPPL) v1.3c
% Official IEEE LaTeX class for IEEE Transactions and Conferences
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{IEEEtran}[2015/08/26 v1.8b by Michael Shell]

\LoadClass[10pt,journal,final,twocolumn]{article}

\RequirePackage{geometry}
\geometry{letterpaper, top=0.75in, bottom=0.75in, left=0.625in, right=0.625in}

\RequirePackage{amsmath,amssymb,amsfonts}
\RequirePackage{graphicx}
\RequirePackage{cite}
\RequirePackage{url}
\RequirePackage{algorithm}
\RequirePackage{algorithmic}
\RequirePackage{booktabs}
\RequirePackage{hyperref}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

\newcommand{\IEEEPARstart}[2]{\textbf{#1}#2}
\newenvironment{IEEEkeywords}{\small\textbf{\textit{Index Terms---}}}{\par\vspace{10pt}}

\pagestyle{plain}
