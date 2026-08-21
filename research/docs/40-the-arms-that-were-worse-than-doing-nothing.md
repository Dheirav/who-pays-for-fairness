# 40 — The arms that were worse than doing nothing, and what removing them costs

**Individual work, beyond the course submission.** The rule and both tests were fixed in
`src/experiments/analyse_calibration.py` and committed at `e23841b`, before any of the
out-of-sample arms were run. The re-scoring in A1a is **post-hoc and labelled so**: that data
had been seen.

## The defect

[Document 32](32-the-rate-not-the-task.md) varies the selection rate by moving the
classifier's decision threshold. That holds the task exactly fixed — which was the point —
but it also **degrades the classifier, and nothing in the design bounded how far**.

Counting arms whose baseline accuracy falls below its own **majority-class baseline** — what
always predicting the more common label achieves, i.e. what doing nothing achieves:

| instrument | base rate | arms beaten by doing nothing |
|---|---|---|
| COMPAS | 0.53 | 0 of 6 |
| Dutch | 0.48 | 0 of 6 |
| ACS Alabama | 0.31 | **3 of 6** |
| HMDA pooled | 0.73 | **2 of 6** |
| **LSAC** | **0.89** | **5 of 6** |

This is structural. Pushing the selection rate *down* on a task where most people already
qualify requires a classifier that refuses qualified people, and past a point that is worse
than a constant. **It is worst exactly where the base rate is highest** — which is why LSAC is
almost all bad arms, and why HMDA's sweep failed in
[document 32](32-the-rate-not-the-task.md). The same cause, found twice without being
recognised either time.

Document 23's exclusion rule does not catch it. That rule drops arms with little *parity gap*
left to remove; on high-base-rate data the parity gap stays large while the model falls apart.

**The rule, with no tuning constant:** an arm is excluded if its baseline accuracy is below
`max(p, 1 − p)` on its own test labels. The comparison is to the trivial predictor, which is
the weakest defensible standard — not a threshold chosen to produce a result.

## A1a — re-scoring everything. Post-hoc, and it withdraws two headlines

| population | as published | after the rule | arms left |
|---|---|---|---|
| **ACS Alabama** | **r = +0.979 HOLDS** | **VOID** | 2 |
| ACS Oregon | +0.855 HOLDS | **+0.778 HOLDS** | 3 |
| ACS Connecticut | — | **−0.737 FAILS** | 4 |
| ACS Kentucky | HOLDS | **VOID** | 2 |
| ACS South Carolina | HOLDS | **VOID** | 2 |
| **HMDA pooled** | **+0.633 FAILS** | **+0.858 HOLDS** | 4 |
| COMPAS | +0.870 HOLDS | **+0.870 HOLDS** | 5 |
| **LSAC** | **r = +0.968 HOLDS** | **VOID** | 1 |

**Two headline numbers are withdrawn.** Alabama's +0.979 was document 32's central result and
the strongest correlation in the project; LSAC's +0.968 was reported in
[document 39](39-three-more-instruments.md) and to the supervisor. Both rested on arms where
the model was beaten by a constant.

**And the rule rescues lending.** HMDA, which failed at +0.633 with no locatable crossover,
comes back at **+0.858 with a crossover between 0.620 and 0.700** — which **overlaps
[document 31](31-the-crossover-on-natural-data.md)'s independent natural-split estimate of
0.643–0.773**, arrived at by comparing five real loan products and manipulating nothing.

## A1b — the pre-registered half, on four HMDA populations the route had never touched

| population | r | spread | crossover | verdict |
|---|---|---|---|---|
| HMDA Louisiana | **+0.929** | 3.84 | **0.620 – 0.697** | HOLDS |
| HMDA refinance | **+0.995** | 4.79 | **0.709 – 0.807** | HOLDS |
| HMDA improvement | +0.855 | 8.73 | none — no sign flip | FAILS |
| HMDA Mississippi | +0.800 | **1.86** | none | VOID — under doc 37's guard |

**As written, A1b fails.** It predicted the correlation, the spread and a locatable crossover
**on each** of the four. It got two of four, and it is scored as a failure rather than
reinterpreted.

**But the alternative it was written against loses decisively.** That alternative was *"the
exclusion does not help — lending is simply a domain where this route does not work"*, and it
predicted continued non-monotonicity or arm sets too small to say anything. Instead the
correlation clears +0.80 on **all four**, reaching +0.995 on refinance.

**And three independent estimates of the lending crossover now agree:**

| estimate | method | band |
|---|---|---|
| document 31 | comparing five real loan products, nothing manipulated | 0.643 – 0.773 |
| HMDA pooled | operating point, after the rule | 0.620 – 0.700 |
| HMDA Louisiana | operating point, held out | 0.620 – 0.697 |
| HMDA refinance | operating point, held out | 0.709 – 0.807 |

Four routes, one domain, overlapping bands. That is the validation
[document 35](35-what-to-do-about-it.md)'s recommendation needed and did not have.

## A2 — the crossover belongs to the population, not to the protected attribute

On COMPAS the two attribute arms disagree at their natural operating points, which suggested a
practitioner would have to measure a *separate* crossover per attribute — and document 35 says
nothing about that.

Sweeping Alabama and Oregon on **race**, where every previous sweep used sex:

| state | sex | race | |
|---|---|---|---|
| Oregon | 0.362 – 0.653 | **0.358 – 0.652** | **overlap, as predicted** |
| Alabama | 2 arms survive | 2 arms survive | undecidable |

The prediction was written down as a coin-flip with COMPAS pointing the other way. Oregon's two
bands are nearly identical. The crossover is a property of where the task sits on the
selection-rate scale, and that scale belongs to the population rather than to how it is
partitioned.

COMPAS's disagreement is not thereby explained away, and it is not the same measurement: its
race arm drops defendants outside the two groups ProPublica compare, so the two arms are not
the same population. The tension is recorded, not resolved.

## The structural lesson, which is bigger than any of the above

**A six-point sweep is too coarse to survive two exclusion rules.** After the parity-gap rule
and the accuracy rule, five of the eight re-scored populations are left with two to four arms,
and three are void for having too few. The relationship is not what failed there — the
*design* was.

Every future operating-point sweep should use **ten to twelve points**, not six, chosen to
leave at least six arms after exclusion. The sweeps in documents 32 and 39 were designed before
the accuracy rule existed and cannot be salvaged by re-analysis; they would have to be re-run.

## What this forces elsewhere

* **Document 32** must report Alabama as void and rest its claim on Oregon, which survives at
  +0.778, and on COMPAS and Dutch from document 39. Its central sentence — that moving only the
  decision line reproduces the crossover — is still supported, on fewer populations and with a
  weaker correlation.
* **Document 35** gains the accuracy rule as a required step, and finally gains its lending
  validation.
* **Document 39** must carry LSAC as void.
* Nothing that used the **income-cutoff** route is affected. Those arms change the label rather
  than the decision rule, so the classifier stays well-specified and this failure mode cannot
  arise. [Document 23](23-the-selection-rate-sets-the-direction.md) and everything resting on
  it stand unchanged.

## Why this was not caught earlier

Document 32 named the confound in its own text — *"a confound was traded, not eliminated"* —
and observed that the classifier at a threshold of 0.02 scored 0.443 accuracy against a base
rate of 0.311. It then argued the damage was limited because the extreme arms were excluded by
the parity-gap rule.

**That argument was checked on Alabama and generalised without being checked anywhere else.**
On high-base-rate data the parity gap does not collapse at the extremes, so the rule that was
doing the work on ACS does nothing on LSAC and HMDA. The observation was right, the reasoning
from it was wrong, and it took a dataset where 89% of people pass to make that visible.
