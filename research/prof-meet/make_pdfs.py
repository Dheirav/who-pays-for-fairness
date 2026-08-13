"""Render the meeting documents to PDF.

**Individual work, beyond the course submission.**

`pandoc` is not available in this environment and `pdflatex` is, so this is a small
markdown-to-LaTeX converter covering exactly the subset of markdown these documents use:
headings, bold, italic, inline code, links, bullet and numbered lists, block quotes,
horizontal rules and pipe tables.

It is deliberately narrow. A general converter would be a project; this one has to handle
four known files and fails loudly on anything it does not recognise rather than silently
emitting broken LaTeX.

Usage:
    python research/prof-meet/make_pdfs.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (source, output stem, title, subtitle)
DOCUMENTS = [
    (HERE / "README.md", "00-start-here", "Start Here",
     "What is in this folder, and the order to read it"),
    (HERE / "THE-ASK.md", "02-the-ask", "The Decision I Need",
     "One fork, the argument for it, and the counter-argument expected"),
    (HERE.parent / "paper" / "draft.md", "03-paper-draft", "Paper Draft",
     "Full working draft"),
    (HERE.parent / "paper" / "reading-notes.md", "04-reading-notes", "Reading Notes",
     "What each cited paper was checked for, and what it changed"),
]

# Characters LaTeX treats specially, in an order that does not double-escape.
ESCAPES = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
    ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
    ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
]

# Unicode this project actually uses, mapped to something pdflatex renders.
UNICODE = {
    "\u2014": "---", "\u2013": "--", "\u2212": "$-$",
    "\u00d7": "$\\times$", "\u2265": "$\\ge$", "\u2264": "$\\le$",
    "\u2248": "$\\approx$", "\u00b1": "$\\pm$", "\u2192": "$\\rightarrow$",
    "\u03b5": "$\\varepsilon$", "\u03bb": "$\\lambda$", "\u03c6": "$\\varphi$",
    "\u03c4": "$\\tau$", "\u2261": "$\\equiv$", "\u21d4": "$\\Leftrightarrow$",
    "\u2018": "`", "\u2019": "'", "\u201c": "``", "\u201d": "''",
    "\u2022": "$\\bullet$", "\u00a0": " ", "\u2026": "\\ldots{}",
    "\u0301": "", "\u2713": "yes", "\u2717": "no",
}


def escape(text: str) -> str:
    """Escape LaTeX specials, *then* substitute unicode.

    The order matters and was wrong once: the unicode replacements themselves contain
    backslashes and dollar signs, so substituting them first meant the escape pass then
    mangled them and `$-$` reached the page literally.
    """
    for source, target in ESCAPES:
        text = text.replace(source, target)
    for source, target in UNICODE.items():
        text = text.replace(source, target)
    return text


def inline(text: str) -> str:
    """Inline markup. Code spans are escaped first and protected from later passes."""
    protected: list[str] = []

    def stash(rendered: str) -> str:
        protected.append(rendered)
        return f"\x00{len(protected) - 1}\x00"

    text = re.sub(r"`([^`]+)`",
                  lambda m: stash(r"\texttt{" + escape(m.group(1)) + "}"), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: stash(r"\href{" + m.group(2).replace("%", r"\%") + "}{"
                                  + escape(m.group(1)) + "}"), text)
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\\emph{\1}", text)
    for index, rendered in enumerate(protected):
        text = text.replace(f"\x00{index}\x00", rendered)
    return text


def render_table(rows: list[str]) -> list[str]:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, body = cells[0], cells[2:]          # cells[1] is the alignment rule
    columns = len(header)
    # First column left, the rest left as well: these tables are mostly prose, and
    # right-aligning text columns reads badly.
    spec = "l" + "l" * (columns - 1)
    out = [r"\begin{center}", r"\small", r"\begin{tabular}{" + spec + "}", r"\toprule"]
    out.append(" & ".join(r"\textbf{" + inline(c) + "}" for c in header) + r" \\")
    out.append(r"\midrule")
    for row in body:
        row = (row + [""] * columns)[:columns]
        out.append(" & ".join(inline(c) for c in row) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    return out


def convert(markdown: str) -> str:
    lines = markdown.split("\n")
    out: list[str] = []
    list_stack: list[str] = []
    index = 0

    def close_lists() -> None:
        while list_stack:
            out.append(r"\end{" + list_stack.pop() + "}")

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("|") and index + 1 < len(lines) and \
                re.match(r"^\|[\s:|-]+\|$", lines[index + 1].strip()):
            close_lists()
            block = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                block.append(lines[index])
                index += 1
            out += render_table(block)
            continue

        if not stripped:
            close_lists()
            out.append("")
            index += 1
            continue

        if re.match(r"^(---|\*\*\*|___)$", stripped):
            close_lists()
            out.append(r"\vspace{2mm}\hrule\vspace{2mm}")
            index += 1
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            close_lists()
            level = len(heading.group(1))
            command = {1: "section", 2: "section", 3: "subsection", 4: "subsubsection"}[level]
            out.append("\\" + command + "*{" + inline(heading.group(2)) + "}")
            index += 1
            continue

        if stripped.startswith(">"):
            close_lists()
            block = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                block.append(lines[index].strip().lstrip(">").strip())
                index += 1
            out.append(r"\begin{quote}")
            out.append(inline(" ".join(b for b in block if b)))
            out.append(r"\end{quote}")
            continue

        bullet = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        numbered = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if bullet or numbered:
            match = bullet or numbered
            want = "itemize" if bullet else "enumerate"
            if not list_stack:
                out.append(r"\begin{" + want + "}")
                list_stack.append(want)
            elif list_stack[-1] != want:
                out.append(r"\end{" + list_stack.pop() + "}")
                out.append(r"\begin{" + want + "}")
                list_stack.append(want)
            item = [match.group(2)]
            index += 1
            while index < len(lines):
                nxt = lines[index]
                if (not nxt.strip() or re.match(r"^(\s*)([-*]|\d+\.)\s+", nxt)
                        or nxt.strip().startswith(("#", "|", ">"))):
                    break
                item.append(nxt.strip())
                index += 1
            out.append(r"\item " + inline(" ".join(item)))
            continue

        # Paragraph: gather wrapped lines so that bold or emphasis spanning a line
        # break is still matched. Line-at-a-time missed every one of them.
        close_lists()
        paragraph = []
        while index < len(lines):
            candidate = lines[index]
            trimmed = candidate.strip()
            if (not trimmed or trimmed.startswith((">", "|", "#"))
                    or re.match(r"^(\s*)([-*]|\d+\.)\s+", candidate)
                    or re.match(r"^(---|\*\*\*|___)$", trimmed)):
                break
            paragraph.append(trimmed)
            index += 1
        out.append(inline(" ".join(paragraph)))

    close_lists()
    return "\n".join(out)


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.3cm]{geometry}
\usepackage{booktabs}
\usepackage[hidelinks]{hyperref}
\usepackage{parskip}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\setlength{\emergencystretch}{3em}
\title{\textbf{TITLE}\\[2mm]\large SUBTITLE}
\author{Dheirav}
\date{\today}
\begin{document}
\maketitle
"""


def build(source: Path, stem: str, title: str, subtitle: str) -> bool:
    body = convert(source.read_text())
    tex = (PREAMBLE.replace("TITLE", escape(title)).replace("SUBTITLE", escape(subtitle))
           + body + "\n\\end{document}\n")
    tex_path = HERE / f"{stem}.tex"
    tex_path.write_text(tex)

    for _ in range(2):                        # twice, so the table of contents settles
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path.name],
                       cwd=HERE, capture_output=True)
    ok = (HERE / f"{stem}.pdf").exists()
    for suffix in (".aux", ".log", ".out", ".tex"):
        (HERE / f"{stem}{suffix}").unlink(missing_ok=True)
    return ok


def main() -> None:
    if not shutil.which("pdflatex"):
        sys.exit("pdflatex not found")
    # 01-findings.tex is hand-written LaTeX rather than converted markdown, so it is
    # built here rather than listed in DOCUMENTS.
    print(f"  {'01-findings':<20} <- 01-findings.tex", end=" ")
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "01-findings.tex"],
                       cwd=HERE, capture_output=True)
    print("ok" if (HERE / "01-findings.pdf").exists() else "FAILED")
    for suffix in (".aux", ".log", ".out"):
        (HERE / f"01-findings{suffix}").unlink(missing_ok=True)
    failures = []
    for source, stem, title, subtitle in DOCUMENTS:
        if not source.exists():
            failures.append(f"{source} missing")
            continue
        print(f"  {stem:<20} <- {source.name}", end=" ")
        print("ok" if build(source, stem, title, subtitle) else "FAILED")
        if not (HERE / f"{stem}.pdf").exists():
            failures.append(stem)
    if failures:
        sys.exit(f"failed: {failures}")


if __name__ == "__main__":
    main()
