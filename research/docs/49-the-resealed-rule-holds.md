# 49 — The re-sealed monotone rule holds: 9 of 10, committed first, constant beaten

**Individual work, beyond the course submission.** The rule, the ten populations, the bar and
the constant to beat were fixed in `src/experiments/analyse_resealed.py` and committed at
`356bfa5`, **before any of the ten arms existed**. The populations are ten ACS states this
project had never measured, swept, viability-checked or downloaded — one arm per state, so the
arm count is the population count by construction.

## The result

**9 of 10. The bar was 9, and the best constant scores 6. It holds, and the constant is
beaten.**

| population | rate | change in pool | predicted | actual | |
|---|---|---|---|---|---|
| NE, $100k | 0.014 | −6.35% | down | down | ✓ |
| AR, $50k | 0.195 | −2.55% | down | down | ✓ |
| OK, $50k | 0.220 | −12.78% | down | down | ✓ |
| WA, $70k | 0.233 | −5.52% | down | down | ✓ |
| NV, $50k | 0.297 | −1.57% | down | down | ✓ |
| MN, $30k | 0.699 | −0.04% | up | down | ✗ |
| CO, $30k | 0.701 | +0.63% | up | up | ✓ |
| KS, $20k | 0.767 | +0.58% | up | up | ✓ |
| WI, $20k | 0.814 | +0.69% | up | up | ✓ |
| IA, $10k | 0.896 | +0.04% | up | up | ✓ |

The rule sealed was exactly the one [document 47](47-the-sealed-prediction-failed-and-took-document-46-with-it.md)
scored post-hoc at 7 of 8: **down below 0.54, up at or above** — no low-rate clause, no
refinement of any kind. Below 0.10 it says down, which is where document 46's clause said up
and lost by three arms; Nebraska at 0.014 came out down (−6.35%), as it predicts.

## The miss, scored by the criterion sealed with it

S2, fixed in advance, classifies any miss further than 0.05 from the crossover as evidence
**against the rule**, not against the placement of its boundary. Minnesota is at 0.699 —
0.159 from the crossover — so it is not a boundary call and is not excused as one.

What can be said about it, and this is **post-hoc**: Minnesota's effect is the smallest in
the set by an order of magnitude, and its sign flips across seeds (−0.12, +0.11, +0.19,
−0.32, −0.03; mean −0.04%). The rule called the wrong side of zero on an arm whose distance
from zero is indistinguishable from seed noise — while Colorado, two thousandths of a rate
away at 0.701, moved +0.63% and was called correctly. A rule predicting the sign of a
quantity has nothing to grip on an arm whose true value may not have one. The seal did not
anticipate near-zero *magnitudes* away from the crossover, so this stands as the recorded
miss; a future seal should state a minimum-magnitude guard in advance, the way document 37
added one for correlations, rather than discover it here.

## What this converts

Document 47 left the project's central claim in its weakest evidence format: the 7-of-8 was a
rule chosen *after* the outcomes were known, from a menu of two. This test is the same rule
chosen **before** ten outcomes existed, on populations with no history in this repository —
committed rule, committed bar, committed constant.

* **The claim "you can know in advance" is now demonstrated in advance**: baseline selection
  rate plus the fixed 0.54 prior from [document 44](44-how-much-and-where-two-concessions-tested.md),
  no sweep, no per-population characterisation, on ten unseen populations.
* **The constant comparison did real work.** The cutoffs were assigned to spread expected
  rates across both sides of the crossover; the outcomes split six down, four up, so the best
  constant reaches 6 and the rule's 9 beats it outright — the failure mode of document 26,
  a bar cleared by something a constant outperforms, is excluded by construction.
* **The population count moves from 27 to 37**, all ten new ones held out in the strict
  sense: no prior measurement of any kind.

## What this does not show

It does not locate any new crossover — every prediction used the 0.54 prior, so this is
evidence the *prior* transfers, not that 0.54 is a constant; the cluster's carried span
remains 0.43–0.58 ([document 45](45-intervals-and-what-the-exclusion-threshold-was-doing.md)).
It says nothing about magnitude, which still does not transfer
([document 44](44-how-much-and-where-two-concessions-tested.md)). All ten populations share
one instrument and one country, deliberately — held-out ACS states are the right source for
fresh populations precisely because they are cheap and clean — so this adds depth, not
breadth; the non-Western gap stands. And one miss at 9 of 10 is one miss: the rule is a
strong prior, not a law, which is what a 0.9 bar claims and no more.

## Why the bar was 9 and not 7

Document 47's sealed bar was 7 of 8 over a design whose constant was expected at 5. Repeating
that arithmetic here would have set 8 of 10. The bar was set at 9 instead because this test
existed to convert the project's weakest evidence into its strongest, and a rule that only
just clears a constant is not that. Passing at exactly the bar, with the single miss flagged
by the sealed criterion itself as against the rule, is the result — reported whole.
