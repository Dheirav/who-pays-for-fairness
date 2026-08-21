#!/bin/bash
# Two passes so cross-references and the section numbering settle.
# IEEEtran.cls is vendored here because it is not in this machine's texlive.
cd "$(dirname "$0")"
for i in 1 2; do pdflatex -interaction=nonstopmode paper.tex >/dev/null 2>&1; done
grep -c Overfull paper.log | sed 's/^/overfull boxes: /'
grep -oP "Output written on paper.pdf \(\K[0-9]+" paper.log | sed 's/^/pages: /'
grep -A 3 "^!" paper.log | head -10
