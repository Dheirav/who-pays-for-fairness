# Meeting folder

Everything needed to discuss this work, in one place.

## Read in this order

Everything is a PDF. The `.md` files beside them are the editable sources; run
`python make_pdfs.py` to rebuild.

| # | file | what it is | time |
|---|---|---|---|
| 0 | **`00-plain-english.pdf`** | The whole thing with no jargon, plus a glossary | 6 min |
| 1 | **`02-findings.pdf`** | The findings, with the numbers | 12 min |
| 2 | `03-the-ask.pdf` | The one decision I need from you | 2 min |
| 3 | `papers/01-mittelstadt-2023-*.pdf`, section 6 only | The closest competing work | 15 min |
| 4 | `04-paper-draft.pdf` | The full paper draft, in academic style | 40 min |
| 5 | `05-reading-notes.pdf` | What I checked in each cited paper, and what changed | 10 min |

`01-start-here.pdf` is this document. **If any wording is unfamiliar, start at 00** — it
defines every term the others use.

## In one sentence

> These fairness fixes make two groups equal either by approving more from the group being
> turned down, or by rejecting more from the group getting through — and the certifying
> score cannot tell which happened. Theory published in March 2026 proves it can go either
> way. **I measured which way, on 26 runs across 15 populations: it depends on how generous the system already
> is.** And the domains these tools are deployed in sit at opposite ends of that scale — CV
> screening approves 2–3%, mortgage lending approves 84% — so two organisations can apply
> the identical tool in good faith and get opposite effects, with identical fairness reports.
> Their conditions hold on none of my datasets; my rule needs only a historical approval
> rate, and the two agree at 0.93.

## The papers, and why each is here

| file | why it matters |
|---|---|
| **01 Mittelstadt et al. (2023)** | **The closest competing work.** Showed these fixes mostly harm rather than help, *and* proposed the remedy I thought was mine. Read section 6. |
| 02 Corbett-Davies et al. (2017) | Proves what the mathematically best possible fair program looks like — which makes one of my comparisons a ceiling rather than a rival. |
| 03 Diana et al. (2021) | The alternative method the field recommends for this problem. I test it and it performs badly. |
| 04 Kearns et al. (2018) | Showed fixes can look fine per group while failing for combinations of groups. I reproduce this. |
| **13 Maheshwari et al. (2023)** | The other half of paper 04. Showed that these fixes harm combined groups *more*, and that it "often goes unnoticed in the overall performance". My intersectional finding replicates the two of them together; what is mine is ten populations and the condition that it needs a sizeable minority to appear. |
| **11 Backfire (2026)** | **The closest work to my main claim.** Proves the effect can go either way when the model cannot see the group — my exact setting. No experiments in it at all. Read the abstract and Theorem 3. |
| **05 Goethals et al. (2024)** | **The near miss.** Studies the same dimension I do, calls it "overlooked" — and two of its four authors also wrote paper 01. Their setup fixes the number of approvals in advance, so my effect cannot appear in it. |
| 06 Menon & Williamson (2018) | Supporting theory for paper 02. |
| 07 Ustun et al. (2019) | Another "avoid harm" method from the literature. |
| 08 Black et al. (2022) | On models that score equally well but disagree about individuals. Supports one of my cautions. |
| 09 Agarwal et al. (2018) | The method everything here is built on. |
| 10 Ding et al. (2021) | Argues the field over-relies on one old dataset, and supplies replacements. I use them. |

## Where the underlying work is

- `../docs/11`–`26` — 16 documents, one per finding, each stating its own limits
- `../../docs/01`–`10` — the coursework this grew out of
- `../results/` — every number as a spreadsheet
- `../../tests/test_documented_claims.py` — regenerates every headline figure and fails if a
  document disagrees with its data
- `git log` — the full record, including predictions committed before the experiments that
  tested them

## Three things I would rather say than be asked

**1. My remedy is not new.** I believed the fix I proposed was original. It is a variation
on one already published (paper 01, section 6). I found this myself by reading their paper,
corrected my write-up, and demoted it to a supporting result. What survives: mine works
without the program ever seeing which group someone belongs to, and it is tested far more
widely.

**2. My explanation failed.** I tried to derive *why* the flip happens, wrote the prediction
down in advance, and tested it on new data. It passed my own test and was then beaten by a
much cruder rule, so it explains nothing. It is written up as a failure. I can say when the
flip happens, not why.

**3. The conditionality itself was published five months before I got to it.** A March 2026
theory paper (paper 11) proves the effect can go either way in exactly my setting. I found
it by running a novelty check, not before starting. What survives is the empirical half:
they have no experiments, their conditions hold on **none** of my 26 runs because the
quantity they use diverges on real data, and my rule needs only an approval rate. The two
agree at 0.93 — independent theory and independent measurement converging.

## Scale

16 populations · 191 experimental runs · 1,011 model fits · 2 data sources · 2 kinds of
decision · 5 repeats of everything, 12 where the effects were small enough to need them

Four separate attempts to break the finding, on five populations each: a different learner
(survived 5/5), a 25× range of constraint strength (4/5), a different route to the same
approval rate (4/5), and a different fairness definition (**failed**).
