# Design for the fourth direction seal — probabilities, not signs

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
is not significant, and it may be noise. But if it is real it is not a failure of the rule:
it would mean the transported crossover is systematically misplaced for those populations,
which is testable and is the sharpest open question this table raises. **The fourth seal
should register it as a named hypothesis rather than letting it pass as noise.**

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

## What this cannot fix

Nothing here addresses the transported prior. Both previous cohorts scored the 0.50-prior
null identically to 0.54 with zero discordant arms, and a Brier-scored cohort will separate
them only if it deliberately samples the band where they disagree — 0.50 to 0.54 — which is
also the band where the table above says the rule scores 1 of 6. **Those two facts should be
faced together in the design, not discovered afterwards.**
