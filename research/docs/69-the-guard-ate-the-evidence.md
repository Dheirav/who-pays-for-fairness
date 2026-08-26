# 69 — The guard ate the evidence

**Individual work, beyond the course submission. Sealed test, scored against its own bar.**
Seal `2904dda`, anchored `b93fe73`; scored `analyse_third_direction.py`, 26 Aug.

## What this test was for

The re-seal's 9 of 10 has a weak paired statistic — p ≈ 0.19 — and the paper says so. The
cause is structural, not a shortfall of the rule: rule and constant agreed on five of the
ten arms, so only five discriminated, and five arms cannot produce a small p at any level
of performance. Five of five is 0.031; four of five is 0.19.

So this cohort was built for **discordance**: twenty-four never-measured ACS state-years,
twelve at 2014 and twelve at 2019, cutoffs assigned so the expected rates spread evenly
either side of 0.54 and the best constant would be weak. Twelve discordant arms would give
p < 0.01 if the rule held.

A minimum-magnitude guard of 1.0 points was pre-stated, because document 49 requires one:
Minnesota was charged a miss at −0.04% while Iowa scored correct at +0.04%, two
statistically indistinguishable arms counted opposite ways.

## The result: S1 FAILS

| condition | outcome |
|---|---|
| at least 11 of 14 correct | **PASS** — 13 of 14 |
| strictly beats the best constant | **PASS** — 13 against 9 |
| paired sign test p < 0.05 | **FAIL** — p = 0.062 |

Skill margin **+4 arms, 95% CI [+1, +6]**. The rule got **every discordant arm right, 4 of
4**, and still failed, because four of four is p = 0.0625. **The bar was arithmetically
unreachable once the guard bit.**

Both named nulls scored 13 of 14 with **zero discordant arms**: the cutoff-only reading and
the 0.50-prior reading made identical calls to the rule on every scored arm. This cohort
therefore discriminates neither the rate from the cutoff nor 0.54 from 0.50, exactly as the
re-seal could not.

## Why it failed, and this is the finding

The guard removed 10 of 24 arms, and not at random:

```
corr(|rate − crossover|, |effect|) = +0.648, p = 0.0006, n = 24
  arms kept       mean |rate − crossover| = 0.305
  arms guard-cut  mean |rate − crossover| = 0.195
```

Effects are large far from the crossover and small near it — necessarily, since the pool
change passes through zero there. And arms near the crossover are precisely the arms where
the rule and the constant disagree. Far from it, everything agrees and nothing is learned.

**So the magnitude guard and statistical power are in direct conflict.** The guard removes
exactly the arms that carry the discrimination. Scaling the cohort scales both sides
equally, so this is not fixed by more populations.

The removal was also asymmetric: 8 of the 12 at-or-above arms were cut against 2 of 12
below, because the extension side has smaller effects at these rates.

## What the cohort does establish

Splitting all 40 arms measured on 26 Aug (this cohort and document 70's) by effect size:

| | correct |
|---|---|
| effect ≥ 1.0 pt | **21 / 22 = 95%** |
| effect < 1.0 pt | 11 / 18 = 61% |

Where there is a sign to predict, the rule is near-perfect; where the effect sits inside
seed noise, it is a coin flip. **This is document 49's magnitude argument measured rather
than argued** — it previously rested on Minnesota and Iowa alone. It also retroactively
justifies treating Minnesota's miss as a rubric gap rather than evidence against the rule.

The claim this sharpens: *the rule predicts direction wherever the constraint moves the pool
by more than about a point, and has nothing to grip below that.*

## What it settles

The direction rule's paired statistic is **not** fixable by a larger balanced cohort under a
hard magnitude guard, because the two requirements are anti-correlated by construction. A
future seal must either drop the guard — reintroducing the Minnesota/Iowa artifact — or
replace sign-scoring with a proper scoring rule that weights arms by pre-committed
confidence instead of deleting them. `brier_skill()` in `src/skill.py` implements the
second, and no seal has yet used it.

**Design provenance, since it is the point of the document:** this was my design error. The
guard threshold was chosen without checking what fraction of arms it would remove or which
ones. A power calculation before sealing would have caught it, and the absence of power
calculation before sealing is a weakness this project had already recorded against itself.
