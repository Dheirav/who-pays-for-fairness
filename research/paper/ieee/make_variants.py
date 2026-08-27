#!/usr/bin/env python3
"""Derive shorter builds of paper.tex that drop no content.

**Individual work, beyond the course submission.**

The point of these variants is a page limit, and the constraint is that **nothing is left
out**: every section, subsection, table, figure, ledger row, citation and sentence of
``paper.tex`` appears in both. What changes is only how densely it is set --- type size,
margins, leading, float separation. ``assert_parity`` below checks that claim on every run
rather than trusting it, because a silently dropped float is exactly the failure a page-limit
edit produces.

Why a generator rather than three hand-kept copies: paper.tex is still moving, and forked
copies drift silently. Here a variant is a function of the source, so it cannot go stale.

The cost, stated plainly
------------------------
Neither variant is submissible to a venue that specifies the IEEE format. IEEE conference
templates require 10pt body text; these set 8pt and 7.5pt. They are for reading the whole
argument in fewer pages --- a reviewer, a supervisor, a printout --- not for submission.
For an actual page-limited submission the content has to come out, and
``../COMPRESSION-PLAN.md`` is where that decision is worked out.

Run:  python research/paper/ieee/make_variants.py
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The frontier, measured rather than guessed: for each limit, the largest type size that
# fits it with no overfull boxes. Dropping below these gains nothing; going above overruns.
VARIANTS = {
    # Retuned again after the claim-hierarchy pass put the central claim and its four
    # scope conditions in the Introduction (~450 words), pushing both variants a page over.
    # Margins narrowed rather than type shrunk as the body grew: 8.0pt at 0.40in and 7.8pt
    # at 0.45in both fit 10 pages, and the larger type reads better.
    "paper-10p": dict(limit=10, font="7.9pt", margin="0.32in", leading="0.89", colsep="0.13in"),
    # Retuned twice as the body grew: 7.5pt -> 7.4pt after the Setup clarification, then
    # tighter margins after the 107-population update and the two new ledger rows. Margins
    # were narrowed before the type was, since 7.4pt at 0.32in beats 7.2pt at 0.35in for
    # readability at the same page count.
    "paper-8p":  dict(limit=8,  font="7.0pt", margin="0.25in", leading="0.85", colsep="0.10in"),
}

PREAMBLE = r"""
%% ---- density settings, injected by make_variants.py; edit that, not this file ----
\usepackage[margin=%(margin)s]{geometry}
\linespread{%(leading)s}
\setlength{\parskip}{0pt}
\setlength{\columnsep}{%(colsep)s}
\setlength{\textfloatsep}{3pt}
\setlength{\floatsep}{3pt}
\setlength{\intextsep}{3pt}
\setlength{\abovedisplayskip}{3pt}
\setlength{\belowdisplayskip}{3pt}
\setlength{\abovecaptionskip}{3pt}
\setlength{\belowcaptionskip}{3pt}
\usepackage{microtype}
\usepackage[compact]{titlesec}
\titlespacing*{\section}{0pt}{3pt}{2pt}
\titlespacing*{\subsection}{0pt}{3pt}{1pt}
\usepackage{enumitem}
\setlist{nosep,leftmargin=*}
%% fontsize rescales the whole ladder -- \small, \footnotesize and the tables with it --
%% which a bare \fontsize does not, and which would leave table text larger than body text.
\usepackage[fontsize=%(font)s]{fontsize}
%% ---------------------------------------------------------------------------------
"""


def densify(src: str, spec: dict) -> str:
    text = src.replace("\\documentclass[conference]{IEEEtran}",
                       "\\documentclass[9pt,conference]{IEEEtran}")
    assert "9pt,conference" in text, "document class line not found"
    text = text.replace("\\begin{document}", PREAMBLE % spec + "\n\\begin{document}", 1)
    # The two full-width figures are the only elements resized; their content is unchanged.
    text = text.replace("\\includegraphics[width=\\textwidth]",
                        "\\includegraphics[width=0.84\\textwidth]")
    return text


def census(text: str) -> dict:
    """Everything that must survive. Compared source-to-variant on every run."""
    body = text.split("\\begin{document}", 1)[-1]
    return {
        "sections": len(re.findall(r"\\section\*?\{", body)),
        "subsections": len(re.findall(r"\\subsection\{", body)),
        "tables": len(re.findall(r"\\begin\{table\*?\}", body)),
        "figures": len(re.findall(r"\\begin\{figure\*?\}", body)),
        "algorithms": len(re.findall(r"\\begin\{algorithm\}", body)),
        "labels": len(re.findall(r"\\label\{", body)),
        "refs": len(re.findall(r"\\ref\{", body)),
        "bibitems": len(re.findall(r"\\bibitem\{", body)),
        "citations": len(re.findall(r"\\cite\{", body)),
        "tabular_rows": body.count("\\\\\n"),
        "words": len(re.sub(r"\\[a-zA-Z]+|[{}$&\\]", " ", body).split()),
    }


def assert_parity(src: str, variant: str, name: str) -> dict:
    a, b = census(src), census(variant)
    diffs = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
    assert not diffs, f"[{name}] content lost or added: {diffs}"
    return a


def build(stem: str) -> tuple[int, int]:
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{stem}.tex"],
                       cwd=HERE, capture_output=True)
    log = (HERE / f"{stem}.log").read_text(errors="ignore")
    m = re.search(rf"Output written on {stem}\.pdf \((\d+)", log)
    return (int(m.group(1)) if m else -1, log.count("Overfull"))


def main() -> None:
    src = (HERE / "paper.tex").read_text()
    full_pages, _ = build("paper")
    counts = census(src)
    print(f"paper.tex        {full_pages:>3} pages   "
          + "  ".join(f"{k} {v}" for k, v in counts.items() if k != "tabular_rows"))
    print("-" * 78)
    for stem, spec in VARIANTS.items():
        text = densify(src, spec)
        assert_parity(src, text, stem)
        (HERE / f"{stem}.tex").write_text(text)
        pages, overfull = build(stem)
        verdict = ("BUILD FAILED" if pages < 0
                   else "OK" if pages <= spec["limit"] else f"OVER by {pages - spec['limit']}")
        print(f"{stem:<16} {pages:>3} pages   limit {spec['limit']}, {spec['font']} type, "
              f"{spec['margin']} margins, {overfull} overfull   {verdict}")
    print("-" * 78)
    print("content parity asserted: same sections, floats, rows, citations and words as paper.tex")


if __name__ == "__main__":
    main()
