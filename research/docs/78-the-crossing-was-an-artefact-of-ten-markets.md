# 78 — Experiment 7.2 fails, and it corrects document 77

**Individual work, beyond the course submission. Sealed at `b60fae9`, before any of its six
arms existed.** Reproduce: `.venv/bin/python -m src.experiments.analyse_located_seal`

---

## The verdict, and it goes against the crossover this project located

**S1 FAILS.** The located crossover of 0.405 scores 1 of 3 retained arms; the transported
0.660 — the paper's published lending value — scores 3 of 3. The bar required the located rule
to beat the transported one, and it lost to it. Unguarded: 2 of 4 against 3 of 4.

| | located 0.405 | transported 0.660 | constant |
|---|---:|---:|---:|
| S1, guarded (3 arms) | **1** | 3 | 3 |
| S2, unguarded (4 arms) | **2** | 3 | 3 |

## First, a correction to document 77

Document 77 reported that on ten manufactured-housing arms the pool change was monotone in
the selection rate with a single sign change, and called that a confirmation of the paper's
central claim. **Six more markets destroy the ordering.**

```
LA .349  AR .365  SC .367  AL .388  GA .390  KY .420  MS .423  TX .448
 −        +        −        −        −        +        −        −
NC .527  TN .527  FL .575  MI .588  OH .628  IN .717  AZ .815  WA .885
 +        +        +        +        +        +        +        +
```

`-+---+--++++++++` — **five sign changes**, where ten arms gave one.

I over-read that result, and the error is a specific one worth naming. The paper's
monotonicity claim is **within a population, across operating points**. Document 77 applied it
**across populations, at their natural rates** — a different object, and one the paper
explicitly says does not hold: *no pooled slope transfers between populations*. That ten
markets happened to sort was luck, and it did not survive sixteen. The correction is
consistent with the paper; document 77 is not.

## What survives, and it is not nothing

The cross-population **correlation** is real and is now significant, which it was not before:
**Spearman ρ = +0.747, p = 0.001, n = 16.** The rate carries information about the direction
across manufactured-housing markets. What it does not do is separate them at a single
threshold.

Over all sixteen arms:

| threshold | correct |
|---|---:|
| best possible (0.450) | 14 of 16 |
| **0.405** (located in 7.1b) | **13 of 16** |
| 0.540 (survey prior) | 12 of 16 |
| best constant | 10 of 16 |
| **0.660** (the paper's lending value) | **9 of 16** |

The transported lending crossover is **worse than a constant** over the full set. The located
one is well ahead of both. **None of that rescues the seal**, and it is not offered as though
it does: 0.405 was located from ten of these sixteen arms, so scoring it on them is the
circularity this project refuses. It is reported because the sealed cohort is three arms and
the fuller picture is the honest context for a result that size.

## Why the seal failed where it did, which is a design failure of mine

Both sealed misses sit inside the located crossover's dead band:

| market | rate | distance from 0.405 | | outcome |
|---|---|---|---|---|
| MS | 0.423 | **0.018** | dead band | miss |
| TX | 0.448 | **0.043** | dead band | miss |
| IN | 0.717 | 0.312 | clear | correct |

The paper's own calibration says the rule is correct on **1 of 6** arms within 0.05 of a
crossover. This cohort had two separating arms and both were within 0.05. **The seal tested
the rule precisely where the paper says it does not work**, and got the result the paper
predicts.

That is not an excuse and it does not change the verdict. It is a design error: with six
markets and a crossover at 0.405, arms clustering near 0.405 was foreseeable, and a protocol
that cared about the answer would have required separating arms *outside* the dead band. I did
not write that condition, having written a void condition for a different failure mode one
experiment earlier.

## Where the lending record now stands

Four sealed attempts on real approvals, none passing, each failing differently:

1. **six-market sweep** — the sweep protocol is unreliable on mortgage data;
2. **sealed lending cohort** — every arm went up, a constant tied;
3. **7.1, purpose split** — built to reach below the crossover, returned 0 of 8 below it;
4. **7.1b, dwelling split** — reached below at last, but the transported 0.660 was badly
   placed and the rule lost to a constant;
5. **7.2, located against transported** — the located crossover lost to the transported one on
   three arms, both misses inside its own dead band.

What has been learned across them is real: manufactured housing supplies real-allocation arms
below a crossover; the rate correlates with direction across sixteen such markets at
ρ = +0.747; and neither 0.405 nor 0.660 is the right boundary for all of them. What has not
been established, after five attempts, is that **any** transported crossover predicts
direction on real approvals. The paper should say that.

## What would test it, and it is not another cohort of this shape

A **within-population sweep** on one manufactured-housing market: hold the market fixed, move
the operating point, and check whether *that* population's own response is monotone and
crosses once. Every result above compares populations at their natural rates, which is the
weaker cross-population object. The paper's actual claim has never been tested on real
allocations at all, because no lending sweep has ever been run that the audit accepts — and
document 71 already found that the sweep is unreliable here. That is the gap, and it is not
closed by more markets.
