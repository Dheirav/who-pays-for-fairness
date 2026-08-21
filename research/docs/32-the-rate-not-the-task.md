# 32 — It is the selection rate, not how hard the task is

> **Correction, [document 40](40-the-arms-that-were-worse-than-doing-nothing.md).** The
> Alabama result below — r = +0.979, this document's headline and the strongest correlation
> in the project — is **VOID**. Two of its retained arms were models beaten by always
> predicting the majority label, and only two arms survive once those are removed. Kentucky
> and South Carolina are void for the same reason. **The claim now rests on Oregon
> (r = +0.778 after exclusion), on COMPAS (+0.870) and on the Dutch census (+0.915) from
> [document 39](39-three-more-instruments.md).** It survives, on fewer populations and with a
> weaker correlation than stated here. The numbers below are left as they were computed, with
> this notice, rather than silently restated.

**Individual work, beyond the course submission.** Predictions and thresholds were fixed in
`src/experiments/analyse_operating_point.py` and committed at `a73e1e0`, before any arm was
run.

## The crack this closes

[Document 23](23-the-selection-rate-sets-the-direction.md) reaches a selection rate by
**moving the income cutoff**. Rows, features and groups are provably identical across its
arms — `tests/test_acs_threshold.py` asserts exactly that — but the thing it moves is the
**label**. "Earns over $100,000" is not a rarer version of "earns over $20,000"; it is a
*harder* problem, with a different Bayes error and a different score distribution.

So document 23 could not separate two explanations:

1. the **selection rate** sets the direction of levelling down, or
2. the **difficulty of the task** sets it, and the selection rate merely travels alongside.

Both predict everything document 23 observed. And explanation 2 would also have explained
[document 31](31-the-crossover-on-natural-data.md), which found the crossover at 0.64–0.77
where the cutoff sweep put it at 0.25–0.60, and offered three readings without choosing
between them.

## The design: change nothing but where the model draws its line

One state, one income cutoff, one feature set, one label, one population — and the *same
fitted scores*. Only the decision threshold moves
(`src.models.ThresholdedClassifier`). This is a strictly stronger single-factor manipulation
than document 23's, because document 23 changes the label and this changes nothing except
the decision rule.

The six thresholds were chosen from the score distribution **measured before any arm ran**,
to reproduce document 23's Alabama selection rates over the same range rather than a
convenient one.

## The result

| selection rate | **operating point** | **income cutoff** (doc 23) |
|---|---|---|
| 0.866 / 0.890 | +4.19% | +0.08% | *(both excluded)* |
| 0.765 / 0.760 | **+2.98%** | **+0.80%** |
| 0.607 / 0.598 | **+1.16%** | **+0.98%** |
| 0.260 / 0.252 | **−2.42%** | **−2.34%** |
| 0.100 / 0.099 | **−6.63%** | **−22.05%** |
| 0.031 / 0.029 | +12.53% | −29.71% | *(both excluded)* |

**O0 — the knob works.** HOLDS. Selection rate spans 0.031–0.866, monotone in the threshold.

**O1 — the prediction.** HOLDS. **r = +0.979** over four retained arms, against a bar of
+0.70 and a naive alternative that needed |r| < 0.30 to win. Partial **r = +0.996** holding
the baseline parity gap fixed.

**O2 — the sign flips.** HOLDS. −6.63% at a rate of 0.100, +2.98% at 0.764. Every seed
agrees on the sign in both arms.

**O3 — the decisive one: do the two routes agree on *where*?** HOLDS.

* operating point: crossover between **0.260 and 0.607**
* income cutoff: crossover between **0.252 and 0.597**

Those brackets very nearly coincide.

## Extended to five populations, and to lending — where it partly breaks

The two-state version above was written first. Running the same test on three further ACS
states and on pooled mortgage data changes what can be claimed.

| population | O1 (r) | O2 sign flip | O3 routes agree on *where* |
|---|---|---|---|
| Alabama | +0.979 | yes | **OVERLAP** 0.260–0.607 / 0.252–0.597 |
| Oregon | +0.855 | yes | **OVERLAP** 0.362–0.653 / 0.353–0.637 |
| South Carolina | holds | yes | **OVERLAP** 0.264–0.596 / ~0.26–0.60 |
| **Kentucky** | holds | yes | **DISJOINT** 0.610–0.758 / 0.260–0.605 |
| **Connecticut** | **FAILS** | **FAILS** | undecidable — no sign change to bracket |
| **HMDA lending** | **FAILS** (+0.633) | non-monotone | H1 undecidable |

**O1 and O2 hold in four of five ACS populations. O3 holds in three of five.** The claim in the
two-state version — that the routes agree on the location — is now **three for five**, and
must be stated that way.

### Kentucky: an adjacent, narrow disagreement

The cutoff route puts the flip between **0.260 and 0.605**; the operating-point route puts it
between **0.610 and 0.758**. The brackets are adjacent rather than distant, and the
disagreement is one arm wide: at a selection rate of about 0.61 the cutoff route reports
**+0.69%** and the operating-point route **−0.91%**. Both are small, and either would round to
"no movement", but they have opposite signs and the pre-registered test scores that as
disagreement. It is reported as a failure, not as a near-miss.

### Connecticut: the arms never cross

Connecticut's cutoff arms span selection rates **0.306 to 0.821** and every one of them levels
**up** (+0.46% to +0.80%, a spread of **0.34 percentage points**). Its operating-point arms are
likewise all positive. There is no sign change because no arm sits below the crossover.

By *sign*, the rule predicts all four arms correctly: rates above the crossover, pool grows.
What fails is the correlation, and a correlation fitted to a 0.34-point spread — against 16.4
points in Kentucky and 14.5 in South Carolina — carries no information in either direction.

**This exposes a defect in document 23's pre-registration, not in Connecticut.** T1 requires
r >= 0.70 but sets **no minimum spread**. Document 33's E0, written months later, does exactly
that: it demands a 2.0-point spread before any correlation is allowed to count, precisely so a
constant cannot be beaten by noise. The later pre-registration is better designed than the
earlier one, and the earlier one is the project's headline.

**The guard has since been added and applied backwards over every arm set ever scored under
T1** ([document 37](37-the-guard-that-should-have-been-there.md)). Three of twenty are void,
all three Connecticut under a linear model; **none ever passed T1 on noise**, so nothing this
project has claimed is overturned. Connecticut is therefore *void*, not a refutation, and the
O1/O2 entries for it above should be read that way.

### Lending: the pre-registered H1 is undecidable

**H1**, committed at `ed788bd` before any arm ran, predicted that the operating-point crossover
on pooled Mississippi and Louisiana would overlap document 31's natural band of 0.643–0.773.

| selection rate | 0.350 | 0.510 | 0.620 | 0.700 | 0.768 | 0.827 |
|---|---|---|---|---|---|---|
| change in pool | **+0.56%** | −4.58% | −0.21% | +2.94% | +3.38% | +3.28% |

O1 fails at **r = +0.633**. The relationship is **not monotone**: the lowest-rate arm is
positive, the middle two negative, the top three positive. There is no single sign change to
bracket, so H1 cannot be evaluated — **undecidable, not passed and not failed.**

Two things are worth saying about it. The upper transition, from −0.21% at 0.620 to +2.94% at
0.700, falls **inside document 31's 0.643–0.773 band**, which is the agreement H1 was looking
for. But the positive arm at 0.350 breaks the pattern, and **document 23's exclusion rule
removed nothing here**: every HMDA arm has a baseline parity gap between 0.177 and 0.220, so
the rule that discards degenerate arms on ACS data — where extreme thresholds drive the parity
gap toward zero — does not fire on lending at all. The arm at 0.350 comes from a classifier
approving 35% of applicants where 72.5% are actually approved, with accuracy 0.594 against
0.838 at its best threshold. It is exactly the mis-calibrated regime this document already
flagged as the confound it traded, and here nothing filters it out.

**Consequence for [document 35](35-what-to-do-about-it.md).** Its central recommendation —
locate your own crossover by sweeping your deployed model's threshold — is **not validated on
lending**, which is the domain it is aimed at. It works on four of five ACS populations and
agrees with the cutoff route on three. That is not nothing, and it is not what document 35
currently claims.

## What this settles

**The selection rate is the operative variable, on ACS data.** Holding the task fixed and
moving only the decision rule reproduces the relationship and the sign change in four
populations of five, and the location of the crossover in three of five. Explanation 2 —
that task difficulty was doing the work — is refuted where the test is informative:
difficulty is held exactly fixed here and the effect survives.

It is refuted less completely than the two-state version of this document claimed, and not
at all on lending.

**Document 31's discrepancy is a population difference, not an artifact.** The natural
crossover at 0.64–0.77 cannot now be blamed on the way document 23 manufactured its selection
rates, because a second, independent route lands where the cutoff route did — on both states
tested. What remains is that populations differ, and Oregon's 0.35–0.65 sits between
Alabama's and the lending data's, which is what a population effect looks like rather than
an instrument artifact.

**And it yields a usable procedure.** Because the operating-point route agrees with the
cutoff route within a population, an analyst can locate *their own* crossover by sweeping
their model's decision threshold and running the constraint at each point. That needs no new
data, no relabelling, and no second population. It converts "the crossover is
population-specific, so measure it" from a caveat into an instruction.

## What it does not settle, and must be said

**The magnitudes do not transfer.** At the lowest retained arm the two routes differ by more
than three times: **−6.63% against −22.05%** at essentially the same selection rate. The
direction and the crossover agree; the size of the effect does not. That is consistent with
the cutoff route compounding two changes — the task gets both harder and rarer — where the
operating-point route only makes predictions rarer. **The rate predicts which way, not how
much.**

**The two extreme arms disagree outright**, +12.53% against −29.71% at a rate of about 0.03.
Both are excluded by document 23's rule, and the exclusion is earned rather than convenient:
the operating-point arm there has 206 baseline positives and its five seeds run from +3.4% to
+27.9%, standard deviation 11.67. That is [document 15](15-arbitrariness-at-small-scale.md)'s
regime exactly, and no claim should rest on it. The four retained arms are sign-stable across
every seed.

**A confound was traded, not eliminated.** Moving the operating point isolates the selection
rate from task difficulty, but the baseline is then no longer the accuracy-optimal decision
rule — at a threshold of 0.02 the classifier approves 87% of applicants and scores 0.443
accuracy against a base rate of 0.311. So the two routes are still not matched on everything:
one produces a well-calibrated model for a *different* task, the other a deliberately
mis-calibrated model for the *same* task. What limits the damage is that both extreme arms
are excluded, so the comparison rests on thresholds where the classifier is not degenerate —
and that moving a decision threshold is what deployed systems actually do, since lenders
approve at different rates without redefining default.

## A methods note worth keeping

The first run of this analysis printed **"DISJOINT: the routes disagree"** — the opposite of
the finding above. It was a bug, not a result. The cutoff arms predate the recorded test-set
denominator, so their selection rates came out `NaN`; the guard checked for `None` and a
tuple of `NaN`s slipped past it, comparing false against everything. A missing denominator
therefore presented itself as a substantive scientific conclusion, and a plausible one, since
it was the outcome document 31 had made likely.

It was caught because the bracket printed as `(nan, nan)` beside a verdict asserting
disagreement. Had the analysis reported only the verdict, this document would have said the
opposite of what the data show.
