# Design for the fourth direction seal — probabilities, not signs

> **SUPERSEDED, 26 Aug, by the fork of document 71 — do not seal against this.**
>
> The calibration table below pools populations whose landscapes do not support a
> directional rule with populations whose do. Of the six near-boundary arms it treats as a
> single "within 0.05" bucket, five turned out to be non-monotone or inverted, **including
> the one the rule scored correct**. Every row of that table is therefore a mixture, and the
> "19 of 19 beyond 0.30" row in particular is not a clean measurement of anything.
>
> The power analysis inherits the flaw: it simulates from those band accuracies, so its
> "40 arms, 97% power" is power to detect a mixture, not power to test the rule.
>
> What survives: the argument that a proper scoring rule beats sign-scoring (documents 69
> and 70), and the requirement that a seal state expected yield before running. What does
> not: the calibration, the committed probabilities, and the sample size.
>
> A fourth seal, if there is one, must first decide whether it is testing the
> transported-prior claim or the sweep-conditional one. Document 71 argues those are now
> very different tests, and that the second is the one worth sealing.

**Not a seal.** This is the protocol a fourth direction seal should commit. Nothing here is
registered until it is written into an analyser and committed before its arms exist.

Written 26 Aug, after documents 69 and 70 established that the sign-scoring route is
self-defeating.

## Why the sign route cannot work

Document 69: a paired sign test needs discordant arms; discordant arms sit near the
crossover; effect size grows with distance from the crossover (r = +0.648); and the
magnitude guard document 49 requires deletes small effects. So the guard removes exactly
the arms the test needs, and scaling the cohort scales both sides. The third direction
cohort had 24 arms, lost 10 to the guard, kept 4 discordant, won all 4, and still could not
clear p < 0.05 — because four of four **is** 0.0625.

**The route out is to stop deleting arms.** A proper scoring rule weights a near-zero arm
down instead of discarding it, so it contributes information at the confidence it was
predicted with.

## The calibration, measured on every sealed arm ever run

All 58 arms from the four direction cohorts (seal 1, the re-seal, third direction, lending),
each scored against its own cohort's crossover:

| \|rate − crossover\| | n | correct | accuracy | median \|effect\| |
|---|---|---|---|---|
| 0.00 – 0.05 | 6 | 1 | **17%** | 0.60 pts |
| 0.05 – 0.15 | 6 | 5 | 83% | 0.78 pts |
| 0.15 – 0.30 | 27 | 23 | 85% | 0.96 pts |
| 0.30 – 1.00 | 19 | 19 | **100%** | 7.24 pts |

Two things to take from this, and the second is uncomfortable.

**The rule is perfect far from the crossover and useless near it**, which is what Algorithm
1's INDETERMINATE verdict already assumes and what document 69 measured as 95% against 61%.

**Within 0.05 of the crossover the rule scores 1 of 6 — worse than a coin.** On n = 6 that
is not significant. But inspecting the arms rules out the first explanation that comes to
mind, and points at a better one:

| arm | rate | side of prior | predicted | actual |
|---|---|---|---|---|
| MD 2018 | 0.508 | below | down | **up** |
| IN 2014 | 0.553 | above | up | **down** |
| MO 2014 | 0.555 | above | up | **down** |
| NY improvement | 0.653 | below | down | **up** |
| MD improvement | 0.668 | above | up | **down** |

A *systematically misplaced* prior would push every miss the same way. These go both ways:
Maryland needs a crossover below 0.508, Indiana and Missouri need one above 0.555. So the
prior is not shifted — it has **no resolution at this scale**, which is what one should
expect when located crossovers span 0.28 to 0.65. Being within 0.05 of 0.54 tells you almost
nothing about which side of your *own* crossover you sit.

That reading is consistent with the data but **not confirmed by it**: none of these six
populations has a stored sweep, so their own crossovers are unknown. Sweeping those six
would test it directly and is the cheapest open experiment this project has — see
"What to test first" below.

## The protocol to commit

1. **Commit a probability per arm, not a sign.** From the calibration: 0.95 beyond 0.30 from
   the crossover, 0.85 between 0.15 and 0.30, 0.80 between 0.05 and 0.15, and 0.50 within
   0.05 — an explicit refusal to predict, which costs nothing under a proper scoring rule
   and is honest about the row above.
2. **Score with `brier_skill()`** (`src/skill.py`) against a base-rate reference of 0.5.
   S1 holds if the bootstrap 95% interval on the skill score excludes zero.
3. **No magnitude guard, and none is needed.** A near-zero arm predicted at 0.50 contributes
   almost nothing either way; it is neither deleted nor able to distort. This is the whole
   point, and it is why the guard/discordance conflict does not arise.
4. **Keep the named nulls**: the cutoff-only reading and a 0.50-prior reading, scored the
   same way, since neither previous cohort could separate them.

## The power analysis, which the standing rule now requires before sealing

Simulating cohorts drawn from the measured band distribution above, with the committed
probabilities of item 1, and bootstrapping the skill interval:

| arms | power (95% interval excludes 0) | median skill |
|---|---|---|
| 20 | 76% | 0.65 |
| **30** | **93%** | 0.66 |
| **40** | **97%** | 0.66 |
| 60 | 100% | 0.65 |

**Register 40 arms and a floor of 30.** Every arm scores, so unlike the sign route there is
no attrition between the registered n and the scored n — which is precisely what killed the
third cohort, where 24 registered became 14 scored and 4 informative.

## Populations available

ACS has 50 states at each of 2014 and 2019; 16 and 14 respectively are now measured, leaving
roughly 70 unmeasured state-years — comfortably more than 40. 2022 stays excluded until
labels are quantile-anchored, per the vintage finding.

## What to test first, and it is cheap

Sweep the six near-boundary arms above to locate their own crossovers, then ask whether each
miss is explained by the arm sitting on the other side of its own crossover than the prior
implied. Six populations, twelve points each, on data already downloaded — one to two hours.

Two outcomes, both useful. If the misses are explained, the boundary behaviour is the
transported prior's resolution limit and nothing more, which is a clean quantification of a
weakness the paper already concedes qualitatively. If they are **not** explained — if a
population sits on the side of its own measured crossover that the rule predicted, and still
moves the other way — then something is wrong with the within-population claim at small
effect sizes, and that is a far more serious finding than a fallible prior.

**Run this before sealing the fourth cohort**, because the answer changes what the fourth
cohort should commit within 0.05 of the prior.

## What this cannot fix

Nothing here addresses the transported prior. Both previous cohorts scored the 0.50-prior
null identically to 0.54 with zero discordant arms, and a Brier-scored cohort will separate
them only if it deliberately samples the band where they disagree — 0.50 to 0.54 — which is
also the band where the table above says the rule scores 1 of 6. **Those two facts should be
faced together in the design, not discovered afterwards.**
