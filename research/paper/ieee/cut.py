"""Structural edits on paper-submission.tex, done so they cannot silently overreach.

Written after an earlier attempt at this: a non-greedy match from the first \\begin{table}
to a labelled one deleted half the paper and compiled at zero overfull boxes, so nothing
caught it but reading the output. Every operation here is bounded by construction, reports
what it removed, and refuses rather than guessing when the boundary is ambiguous.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

PAPER = pathlib.Path("paper-submission.tex")


def load() -> str:
    return PAPER.read_text()


def save(text: str) -> None:
    PAPER.write_text(text)


def words(text: str) -> int:
    return len(re.sub(r"\\[a-zA-Z]+|[{}$&\\]", " ", text).split())


def _env_spans(text: str, env: str) -> list[tuple[int, int]]:
    """Every \\begin{env}...\\end{env} span, matched individually rather than by one regex."""
    spans, pos = [], 0
    begin, end = f"\\begin{{{env}}}", f"\\end{{{env}}}"
    while (i := text.find(begin, pos)) != -1:
        j = text.find(end, i)
        if j == -1:
            raise ValueError(f"unclosed {env} at {i}")
        spans.append((i, j + len(end)))
        pos = j + len(end)
    return spans


def drop_float(text: str, label: str, env: str = "table") -> str:
    """Remove the one float carrying this label. Refuses if zero or many match."""
    hits = [(a, b) for a, b in _env_spans(text, env) if label in text[a:b]]
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} {env}s carry {label!r}; refusing")
    a, b = hits[0]
    print(f"  drop {env} {label}: {words(text[a:b])} words")
    return text[:a] + text[b:].lstrip("\n")


def section_end(text: str, start: int, level: str = "section") -> int:
    """Where a heading's block ends. Never \\end{document}: the bibliography lives between
    the last section and it, and using \\end{document} as the fallback once deleted all 29
    references while still compiling to 17 clean pages."""
    stops = ["\\section{", "\\section*{", "\\begin{thebibliography}"]
    if level == "subsection":
        stops.append("\\subsection{")
    ends = [text.find(s, start + 1) for s in stops]
    ends = [e for e in ends if e != -1]
    if not ends:
        raise ValueError("no heading or bibliography terminates this block; refusing")
    return min(ends)


def drop_section(text: str, title: str, level: str = "subsection") -> str:
    """Remove a (sub)section from its heading to the next heading at the same or higher level."""
    start = text.find(f"\\{level}{{{title}}}")
    if start == -1:
        raise ValueError(f"no \\{level}{{{title}}}")
    stops = ["\\section{"] + (["\\subsection{"] if level == "subsection" else [])
    ends = [text.find(s, start + 1) for s in stops]
    ends = [e for e in ends if e != -1]
    if not ends:
        raise ValueError(f"no heading terminates \\{level}{{{title}}}")
    end = min(ends)
    print(f"  drop {level} '{title}': {words(text[start:end])} words")
    return text[:start] + text[end:]


def replace(text: str, old: str, new: str, *, count: int = 1) -> str:
    """Whitespace-insensitive replace, because LaTeX wraps and literal matches keep failing."""
    pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
    found = pat.findall(text)
    if len(found) != count:
        raise ValueError(f"{len(found)} matches (wanted {count}) for {old[:60]!r}")
    delta = words(old) - words(new)
    print(f"  replace {old[:48]!r}...: -{delta} words")
    return pat.sub(lambda m: new, text)


def build() -> tuple[int, int]:
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", PAPER.name],
                       capture_output=True)
    pages = subprocess.run(["pdfinfo", PAPER.with_suffix(".pdf").name],
                           capture_output=True, text=True).stdout
    pages = int(re.search(r"^Pages:\s+(\d+)", pages, re.M).group(1))
    log = PAPER.with_suffix(".log").read_text()
    return pages, log.count("Overfull")
