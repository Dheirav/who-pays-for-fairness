# Meeting folder

Everything needed to discuss this work, in one place. Self-contained — nothing here depends
on the rest of the repository, though it points at it.

## Read in this order

**Everything is a PDF.** The `.md` files beside them are the editable sources; rebuild all
PDFs with `python make_pdfs.py`.

| # | file | what it is | time |
|---|---|---|---|
| 0 | **`00-plain-english.pdf`** | The whole thing with no jargon, and a glossary | 6 min |
| 1 | **`02-findings.pdf`** | The findings, technical | 10 min |
| 2 | `03-the-ask.pdf` | The one decision I need | 2 min |
| 3 | `papers/01-mittelstadt-2023-*.pdf`, section 6 only | The closest prior work | 15 min |
| 4 | `04-paper-draft.pdf` | The full paper draft | 40 min |
| 5 | `05-reading-notes.pdf` | What each cited paper was checked for | 10 min |

`01-start-here.pdf` is this document. **Start at 00 if any of the terminology is
unfamiliar** — it defines everything the other documents assume.

## The one-sentence version

> Levelling down is not what fairness constraints do — it is what they do below a selection
> rate of about 0.3. Above it, the same constraint hands decisions out instead of taking
> them away. And nearly every real deployment sits below it.

## The papers, and why each is here

| file | why it matters to this work |
|---|---|
| **01 Mittelstadt et al. (2023)** | **The closest prior work.** Established levelling down *and* proposed the remedy (§6, "minimum rate constraints"). Read §6. |
| 02 Corbett-Davies et al. (2017) | The optimal fair classifier is group-specific thresholds — makes our comparison arm a *bound*, not a rival. |
| 03 Diana et al. (2021) | Minimax group fairness: the established levelling-down remedy we benchmark against. |
| 04 Kearns et al. (2018) | Fairness gerrymandering — our subgroup finding is an empirical replication. |
| **05 Goethals et al. (2024)** | **The nearest miss.** Studies the selection-rate axis, calls it "overlooked" — and two of its four authors also wrote 01. They fix the pool as a budget, so direction cannot move. |
| 06 Menon & Williamson (2018) | Thresholding characterisation; supporting cite for 02. |
| 07 Ustun et al. (2019) | Decoupled classifiers with preference guarantees. |
| 08 Black et al. (2022) | Model multiplicity — supports our arbitrariness caution. |
| 09 Agarwal et al. (2018) | The base paper. Everything is built on this reduction. |
| 10 Ding et al. (2021) | Retiring Adult — the ACS datasets, and the argument for not trusting Adult alone. |

## Where the work lives

- `../docs/11`–`26` — 16 research documents, one per finding, each with its limits stated
- `../../docs/01`–`10` — the course-side work (Adult only)
- `../results/` — every number, as CSV
- `../../tests/test_documented_claims.py` — re-derives every headline figure and fails if a
  document and its data disagree
- `git log --oneline 28bc8d1..HEAD` — the full record, including pre-registrations committed
  before their experiments ran

## Two things to raise before they are asked

**1. The remedy is not novel.** I originally believed the selection-rate floor was new. It
is a variant of Mittelstadt et al.'s minimum rate constraints (paper 01, §6). I found this
myself by reading the paper, corrected the write-up in place, and demoted it to a supporting
result. What survives: ours is in-processing rather than post-processing, so it needs no
protected attribute at prediction time; it stacks with parity rather than replacing it; and
it is evaluated on held-out data across 26 populations where they report Adult's training
set.

**2. The mechanism failed.** I derived a candidate explanation for the crossover,
pre-registered it with numerical thresholds, and tested it on fourteen populations run
afterwards. It cleared its bars and was beaten by a trivial constant rule. It is reported as
a failure. I can say *when* the direction flips, not *why*.

## Scale, for reference

26 populations · 61 experimental arms · 3 source datasets · 2 domains · 2 protected
attributes · 5 seeds throughout
