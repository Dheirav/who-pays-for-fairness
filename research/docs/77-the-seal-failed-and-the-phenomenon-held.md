# 77 — Experiment 7.1b: the seal fails, and the phenomenon it was testing holds perfectly

**Individual work, beyond the course submission. Sealed at `e5fbd85`, before any of the
fourteen arms existed.** Reproduce: `.venv/bin/python -m src.experiments.analyse_dwelling_seal`

---

## Both halves, and they point opposite ways

**S1 FAILS.** The rule, transported at the published lending crossover of 0.660, scores 5 of 8
against a bar of 6 and a constant's 6 of 8. It beats the dwelling-only null (5 against 4), so
it is not merely reading the loan's dwelling category, but it loses to a constant and the
sealed bar is not met. Unguarded: 7 of 10 against a constant's 8 of 10. Fails both ways.

**And the phenomenon the rule describes holds on every arm.** Sorted by baseline selection
rate, the ten manufactured-housing arms give a sign sequence of

```
rate   0.367  0.388  0.390  0.420  0.527  0.527  0.588  0.628  0.815  0.885
pool     −      −      −      +      +      +      +      +      +      +
```

written compactly, `---+++++++`. **One sign change. No exceptions.** Spearman ρ = +0.624 (p = 0.054, n = 10), the crossover
bracketed at 0.390–0.420.

## What separates those two statements

The paper distinguishes a **sweep-conditional** claim — measure your own crossover, then the
rate predicts direction against it — from a weaker **transported-prior** claim, which is the
only one testable before any measurement. This cohort is the sharpest test either has had, and
it separates them cleanly on real allocative decisions for the first time:

| | score |
|---|---|
| transported prior at 0.660 | **5 of 10** |
| crossover measured on these arms, ≈ 0.405 | **10 of 10** |

**The 10 of 10 is not a score and we do not claim it.** The crossover was located from these
same arms, so scoring them against it is circular — the identical objection this project
raised against its own "seven of eight" rescue in document 47.

**What is not post-hoc is the monotone single crossing.** That the pool change rises with the
selection rate and changes sign exactly once is a property of the arm set, independent of
where any boundary is drawn. It would have been visible had the crossover been placed
anywhere. That structure is the paper's central empirical claim, and here it holds on ten real
mortgage-approval populations spanning 0.367 to 0.885.

## Why this is the most informative result in the lending record

Every previous lending test failed for the same non-reason: US mortgage approval sits above
the crossover, so the rule predicted extension everywhere and could not be distinguished from
a constant. That happened at state level, across fifty markets, and in experiment 7.1's
purpose split, which was built to reach lower and returned 0 of 8 below the line.

Manufactured housing reaches. It approves at 0.505 against site-built's 0.850, and it supplies
the first real-allocation arms this project has ever had *below* a crossover. On those arms
the direction question has a real answer, the rule's structure is confirmed, and the published
lending crossover is shown to be badly placed for this population: **0.405 against 0.660**.

That is the paper's own thesis turned on the paper. Crossovers are population-specific;
nothing yet predicts their location; a prior read off a dashboard will be wrong. The lending
crossover was located on site-built purchase and refinance lending, and it does not transport
to manufactured housing — a different product, a different applicant population, and, it turns
out, a different boundary.

## What it costs the paper, stated plainly

The transported-prior claim is now weaker on real allocations than it was. Its record reads:
9 of 10 sealed on ACS, 5 of 10 post-hoc on larger ACS states, and now **5 of 10 sealed on
mortgage approvals**. Three cohorts, one pass. The paper already demotes the prior and calls
it a fallible substitute with a measured failure rate; this adds a third measurement and the
rate is worse than the paper currently implies.

Against that, the sweep-conditional claim gains its first confirmation on decisions that
were actually made about people, rather than on predicted labels.

## What would settle it

A sealed test using a crossover **measured on held-out arms of the same population** rather
than transported from another one — sweep four markets, locate the boundary, then predict the
remaining markets against it. That is the sweep-conditional claim's own protocol and it has
never been run prospectively. It is now clearly the most valuable experiment left, and unlike
7.1 it does not need a new instrument: manufactured housing supplies the range.
