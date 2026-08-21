# 38 — Every population count in this project was an arm count

**Individual work, beyond the course submission.** **An audit of this project's own
arithmetic**, not a new result. No experiment was run. Every count of "populations" in every
document was checked against the file it is derived from, and the numbers below are what
those files actually contain.

## Why this was checked

Document 26 reported "fourteen held-out populations" where it had fourteen **arms** from four
populations. That was corrected. Document 27 then turned out to say "26 populations" for 26
arms from fifteen. Two instances of one mistake is a pattern, so every remaining count was
checked rather than assumed.

The mistake matters because arms of one population **share their people**. Alabama under a
$20,000 cutoff and Alabama under $70,000 are the same 22,268 residents with a different label.
Alabama's sex arm and Alabama's race arm are the same residents grouped differently. Counting
those as separate populations inflates the apparent independence of the evidence, which is
exactly the quantity a reader uses to judge how much to believe.

## The ledger

Each row was recomputed from the named file.

| claimed | file it comes from | actually |
|---|---|---|
| "19 populations" | `sweep/arms_p1_pooled.csv` | **19 arms from 10 populations** |
| "26 populations" | `zeta/zeta_correspondence.csv` | **26 arms from 15 populations** |
| "26 populations" (paper) | the default-cutoff arm set | **26 arms from 15 populations** |
| "fourteen populations" | `mechanism/mechanism_heldout.csv` | 14 arms from 4 — *already corrected, doc 26* |

**The nineteen.** Ten rows carry the `SEX` arm — nine ACS states plus Adult — and nine carry
the `RAC1P` arm, the same nine ACS states without Adult. So it is **nine ACS populations
counted twice each, plus Adult counted once**: nineteen arms, ten populations.

**The twenty-six.** Adult, twelve ACS states and two HMDA states. In document 27's set the
extra rows are nine income-cutoff variants of Alabama, Oregon and Kentucky plus four HMDA
rows that are two states under two attributes. In the paper's set the extra rows are
protected-attribute variants. **Different arms, the same fifteen populations underneath.**

## The tell that was sitting in plain sight

`PAPER.md`'s abstract says the exchange rate falls

> **in all 19 populations and in both protected-attribute arms**

That sentence double-counts and cannot be true as written: the nineteen *are* the two
attribute arms, so "and in both arms" adds a dimension the nineteen already contains. Document
19 carries the same construction — "19 populations, two protected-attribute arms and five
seeds". Neither was noticed for the life of the project.

## What this does and does not change

**No measurement changes. No correlation, exchange rate or sign changes.** Every number
computed *over* these sets is unaffected, because the arithmetic was always done over arms and
only the label on the count was wrong.

**What changes is how much independence the evidence has.** "The floor replicates across 19
populations" becomes "across 19 arms from 10 populations". "18 of 19 shrink the pie" is a
correct tally of arms and stays, but it is nine states rather than eighteen. The claim is
still unanimous and still replicated; it is replicated across ten populations, not nineteen.

Document 28's cluster bootstrap was already right about this and said so: it resamples
populations rather than arms precisely because arms are not independent. The correction brings
the prose in line with what the interval estimates already assumed.

## Where the counts were corrected

Documents 13, 14, 15, 19, 21, 22, 27 and 35; `PAPER.md`, `research/README.md`,
`research/paper/draft.md`, and the four supervisor-pack files. `tests/test_documented_claims.py`
now recomputes both population counts from the source files and fails if either drifts, in the
same way it already pins document 26's four.

## The lesson

Three separate counts were inflated the same way, and each was found only when something else
forced a look at the underlying file. None of them was caught by reading the documents,
because the documents are internally consistent — they all repeat the same wrong number.

The check that works is recomputing a claim from the file it came from, which is what
`tests/test_documented_claims.py` exists to do and what it was not yet doing for counts.
