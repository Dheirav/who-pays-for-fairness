# 14 — Why the size of the DP/EO conflict resisted prediction

**Individual work, beyond the course submission.** Closes the loose end left by P2 in
[document 11](11-replication-across-populations.md).

## The loose end

Constraining demographic parity makes equalized odds worse. That much was established on
Adult (document 04) and replicated in 9 of 10 populations (document 11). What nothing
predicted was **how much**. Three candidates were tested and all failed:

| predictor of the EO cost | r |
|---|---|
| base-rate gap | +0.241 |
| amount of DP actually removed | +0.111 |
| baseline DP gap | +0.044 |

Utah held the largest base-rate gap in the study and equalized odds *improved* there.
A conflict that is near-universal in direction and unpredictable in magnitude is an
unsatisfying place to stop.

## What I predicted, and it was wrong

`src/experiments/analyse_conflict.py` was written and committed (`eed2ebb`) before
anything was computed, with three predictions and their thresholds fixed.

The reasoning: base rates describe the *labels* and say nothing about the classifier's
ability to act on them. Under demographic parity both groups are held to one selection
rate, so a group whose base rate sits far from it must have people pushed across the
decision boundary — and what that costs in TPR and FPR should depend on how well the
model separates positives from negatives **inside** that group. Well-separated scores let
the selection rate travel while touching mostly borderline cases; poorly separated scores
mean the same movement cuts through the middle of the distribution.

| | pooled, 19 populations |
|---|---|
| r(EO cost, within-group AUC) | +0.203 |
| r(EO cost, worst group AUC) | +0.246 |
| r(EO cost, base-rate gap ÷ AUC) | +0.311 |
| r(EO cost, base-rate gap) | +0.340 |

**C1 FAILS** — separability reaches |r| = 0.246 against a bar of 0.5.
**C2 FAILS** — the composite (0.311) does not beat the base-rate gap alone (0.340).
**C3 FAILS** — nothing survives inside each arm.

Separability is not the answer. The prediction was specific enough to be wrong, and it
was wrong.

## What the data turned out to say

**This section was found exploratorily** — by looking at the results of a failed
prediction rather than by testing a stated one. It was reported at that lower
standard until the confirmation below, which was pre-registered and which it passed.

The race arm reverses the direction of the effect entirely:

| arm | EO worsened in | mean baseline EO | mean EO after |
|---|---|---|---|
| **sex** | **9 of 10** | 0.0614 | 0.1203 |
| **race** | **1 of 9** | 0.1289 | 0.0641 |

Same nine states, same task, same year, same algorithm. Only the protected attribute
differs, and constraining demographic parity *improves* equalized odds in eight of nine.

That looks like a contradiction of document 11's "the conflict is near-universal". It is
not. The two arms differ in where they **start**:

```
r(baseline EO, EO after the constraint)  = −0.106     ← essentially independent
```

**The EO the constrained model ends up at is unrelated to the EO it began with.** The
constraint pins selection rates equal across groups; whatever equalized-odds violation
that implies is a property of the constrained solution, not of the unconstrained model it
replaced. The sex arm starts low (0.061) and rises; the race arm starts high (0.129) and
falls. Both land in the same region.

That is why the cost resisted prediction. If the endpoint is independent of the start,
then

```
cost = end − start ≈ (something unrelated to the population) − baseline EO
```

and the cost is dominated by the baseline. Every candidate P2 tested — base-rate gap, DP
removed, baseline DP gap — was a property of the population. None of them was the
baseline EO, and the baseline EO is most of the answer.

**An arithmetic trap worth naming.** `r(baseline EO, cost) = −0.700` looks like strong
confirmation and is *not* independent evidence: cost is defined as `after − baseline`, so
a correlation between baseline and cost follows partly from the definition alone. The
load-bearing number is `r(baseline, after) = −0.106`, which has no such dependency. Had
this document led with −0.700 it would have been the same error as the normalised-cost
artifact in document 11's first draft, dressed differently.

## What can and cannot be claimed

**Can:** the post-constraint EO violation is statistically independent of the
pre-constraint one across 19 populations, and this accounts for the failure of every
predictor P2 tried.

**Cannot:** that the constrained model converges to a *fixed* EO level. Pooled standard
deviation is 0.054 before and 0.062 after — no tightening. Excluding Adult (whose 0.280
is a clear outlier) gives 0.044 after against 0.054 before, which is a modest narrowing
at best and is arrived at by dropping the inconvenient point, so it is not claimed.

**Cannot:** that this is a fact about fairness constraints in general. One algorithm
(ExponentiatedGradient), one constraint (demographic parity at ε = 0.01), one task.

## What it changes

| document | status |
|---|---|
| 11 (P2) | The failure to predict the magnitude now has an explanation. Its statement that the conflict is "near-universal in direction" needs qualifying: that held across populations, but **not across protected attributes** — the direction reverses in the race arm |
| 04 (ablation) | Unaffected on Adult, where the cost is real and large (+0.185) |

## The confirmation — and it survived

The test above was written into this document and **committed before it was run**
(`528da3e`), with its thresholds fixed in the code rather than chosen afterwards. If
post-constraint EO belongs to the constrained *solution*, two different mitigations
satisfying the same DP bound on one population should land at similar EO.
`expgrad_dp` and `gridsearch_dp` both target DP ≤ 0.01 and both already existed in all
nineteen populations, so it cost no refits.

| | result | bar | |
|---|---|---|---|
| **D0** precondition — do both actually reach comparable DP? | mean \|ΔDP\| = **0.0113** | < 0.02 | HOLDS |
| **D1** do the methods agree across populations? | r = **+0.922** | > 0.7 | HOLDS |
| **D2** do they agree more than populations differ? | \|ΔEO\| = **0.0205** vs sd **0.0622** | < | HOLDS |

Two independently-derived algorithms — one playing a Lagrangian game to equilibrium, the
other sweeping a fixed grid of multipliers — land within 0.02 EO of each other, while EO
varies three times as much *between populations*. And that endpoint remains uncorrelated
with where each population started (r = −0.106).

**The endpoint is a property of the constrained problem, not of the method that solves it
and not of the model it replaced.** This is the strongest form the claim can take on this
evidence, and it came from a test that could have failed: had the two methods disagreed,
the explanation would have been refuted.

The claim is therefore no longer exploratory. It was *found* exploratorily — that history
is left standing above rather than tidied away — and then confirmed by a prediction made
in advance.

## What is still not claimed

That the constrained model converges to a *fixed* EO level, and that any of this extends
past one constraint (demographic parity at ε = 0.01) and one task. D1 and D2 establish
that two solvers of the same constrained problem agree; they say nothing about a
different constraint.
