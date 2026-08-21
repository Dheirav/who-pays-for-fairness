# 46 — The relationship turns back up at the very bottom, and that is what the exclusion was hiding

**Individual work, beyond the course submission.** **Post-hoc**, and it began as a
robustness check rather than a hypothesis: external review asked why the parity-gap exclusion
was set at 0.05, [document 45](45-intervals-and-what-the-exclusion-threshold-was-doing.md)
showed the answer mattered, and this is what was underneath.

## What document 45 found, and why it was not the whole story

Re-scoring across exclusion thresholds, South Carolina fell from **r = +0.905 at a 0.05 parity
bar to +0.012 at 0.01**, and Oregon from +0.664 to +0.095. Only COMPAS and the Dutch census
held at every threshold. The obvious reading was that the ACS results were created by an
inherited threshold.

The obvious remedy was more seeds: the arms entering at the looser bar have only 331--371
baseline positives, which is
[document 15](15-arbitrariness-at-small-scale.md)'s regime. Re-running all three at **20 seeds**
was expected to show them collapsing into noise around zero.

**They did not.**

| population | positives | mean at 20 seeds | sd | sign flips across seeds |
|---|---|---|---|---|
| S. Carolina | 369 | **+8.73** | 5.58 | yes |
| Oregon | 343 | **+6.85** | 5.91 | yes |
| Kentucky | 352 | **+9.09** | 3.48 | no |

Individual seeds straddle zero, but the means are consistently and substantially **positive**,
at roughly six standard errors from it. These arms are noisy; they are not noise.

## The pattern, once looked for

The lowest three arms of every densely swept population:

| population | rate 0.05 | rate 0.10 | rate 0.15 |
|---|---|---|---|
| ACS Alabama | **+14.85** | −6.17 | −1.99 |
| ACS Kentucky | **+9.09** | −1.76 | −0.84 |
| ACS S. Carolina | **+8.73** | −4.60 | −3.34 |
| ACS Oregon | **+6.85** | −0.80 | −2.27 |
| Dutch census | −27.75 | −45.86 | −24.12 |
| COMPAS | — | −87.12 (at 0.093) | −75.64 |

**All four ACS populations turn positive at their lowest arm and negative immediately above
it.** The relationship is not monotone: it runs up at the extreme bottom, down through the
low-middle, and up again across the crossover.

Dutch and COMPAS do not do this, and it is not a sample-size effect --- COMPAS's arm at 0.093
has **147** baseline positives, fewer than any ACS arm here, and goes to −87.12 without
wavering.

## Why this resolves document 45 completely

Those ACS arms carry baseline parity gaps of **0.032 to 0.043** --- just below the inherited
0.05 exclusion. So they are dropped at 0.05 and admitted at 0.01, and admitting a strongly
positive point at the extreme left of the x-axis is what collapses the correlation.

**The exclusion was not manufacturing a result. It was concealing a second regime**, and the
sensitivity analysis was the right question with the wrong first answer. Document 45's
conclusion --- that the ACS results "depend on the exclusion" --- stands as arithmetic and is
wrong as an interpretation, which is recorded here rather than edited there.

## What can and cannot be said about why

A candidate mechanism, offered as such: at a selection rate near 0.05 the disadvantaged group's
rate is already close to zero and cannot fall much further, so a parity constraint has little
to take and equalises mostly by adding. That would predict the effect appearing wherever the
*disadvantaged* group's rate approaches zero, which on ACS data happens around 0.05 and on
Dutch and COMPAS data does not, because their base rates are 0.48 and 0.53 against ACS's 0.31.

**This is a conjecture and is not tested here.** This project has already had one derivation
beaten by a constant ([document 26](26-the-derivation-does-not-earn-its-keep.md)), and the
pattern rests on four populations of one instrument.

## What changes

* The claim is now bounded on **both** sides: the relationship holds between roughly **0.10 and
  the crossover**, turns back up below 0.10 on survey data, and holds again above the crossover.
  Previously only the upper bound was stated.
* [Document 42](42-denser-sweeps-and-where-the-crossover-sits.md)'s finding that Alabama and
  Kentucky "reverse" now has its cause: their dense sweeps reach down to 0.05 and include the
  turn-up, while their viable bands stop at 0.566 so they cannot reach across the crossover to
  compensate. Both facts are properties of where those populations can be measured, not of the
  relationship.
* The paper reports the sensitivity sweep **and** this explanation. A reviewer who runs the
  sweep and finds +0.012 must find the reason here rather than concluding the result is an
  artifact.
* The exclusion rule stays at 0.05 and is now justified by evidence rather than by inheritance.
