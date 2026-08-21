# 33 — The rule does not survive a change of criterion, at the bar it was given

**Individual work, beyond the course submission.** Predictions and thresholds were fixed in
`src/experiments/analyse_eo.py` and committed at `e658ed1`, before any Alabama or Oregon
equalized-odds arm was run.

## What was being tested

Everything in documents 05, 11–13, 21–23 and 31–32 is **demographic parity**, which is
defined in terms of the selection rates it moves. So levelling down under it can be dismissed
as mechanical, and the project's claim is about one criterion rather than about fairness
constraints.

Equalized odds never mentions selection rates. It equalises true- and false-positive rates
*within* each true-outcome stratum, and any change to the total number of favourable
decisions is a side effect. That makes this the harder test.

The same twelve arms as document 23 — Alabama and Oregon, six income cutoffs each, five
seeds — re-run under `--constraint equalized_odds`. The baseline is the same unconstrained
model in both, so the baseline selection rate is identical across the two analyses by
construction. Arms were excluded by **document 23's rule**, not a new one, so the two sweeps
cover the same populations.

## The result: E1 fails

| | prediction | outcome | |
|---|---|---|---|
| **E0** | EO gap reduction ≥ 0.20 (median) | **+0.160** | **FAILS** |
| **E0** | pie-change spread ≥ 2.0 points | 3.44 | HOLDS |
| **E1** | rate vs pie change, r ≥ +0.70 | **+0.644** | **FAILS** |
| **E2** | rate vs exchange rate, r ≤ −0.70 | −0.748 | HOLDS |
| **E3** | sign flips across the range | −2.75% → +0.03% | HOLDS, *see below* |

**The primary prediction failed.** The selection rate does not predict the direction under
equalized odds at the bar this test was given.

## Why Alabama alone would have been a false positive

On Alabama's four retained arms the correlation is **+0.822** and every prediction holds.
Adding Oregon takes it to **+0.644**. The pre-registration was written over both states, and
the interim Alabama numbers were explicitly not treated as the answer; had they been, this
document would report a success that the full data does not support.

## What survives, stated without inflation

The relationship is **not absent**. The pre-registration named the constant it had to beat —
"the rate predicts nothing under EO", |r| < 0.30 — and +0.644 clears that comfortably. On the
same eight arms:

* demographic parity: **r = +0.775**, pie change spanning −22.0% to +1.2%
* equalized odds: **r = +0.644**, pie change spanning −2.8% to +0.7%

So the direction relationship is *present but weaker*, and the magnitude is roughly an order
of magnitude smaller. That is the mechanistically sensible outcome: a criterion that does not
constrain selection rates moves them much less.

## Three honest qualifications

**E3 holds on a technicality.** The highest-rate retained arm is Oregon at $20,000, whose pie
change is **+0.03%** — a value indistinguishable from zero, and far inside the seed spread.
The sign flip is satisfied by the letter of the prediction and is not meaningfully
established. Alabama's own highest retained arm, +0.69%, is the strongest positive anywhere
in the sweep, and it is small.

**The constraint frequently does not bind.** E0's binding half failed at +0.160 against a bar
of 0.20. Several Oregon arms have baseline equalized-odds gaps of 0.015–0.03 against a
constraint bound of 0.01 — there is almost nothing to remove, so almost nothing moves. The
exclusion rule was deliberately imported from document 23 and keys on the *parity* gap, which
is the right choice for comparability and the wrong one for detecting "nothing to fix" under
a different criterion. That mismatch was recorded before the run, not after.

**Five seeds is thin for effects this small.** Under demographic parity the signs are stable
across every seed. Under equalized odds three Alabama arms flip sign between seeds: the
$70,000 arm's five seeds run from −5.35% to +1.34%. A 12-seed re-run was done as a **precision
check**, decided on before the full verdict was known and reported whichever way it fell,
because changing the seed count after seeing a failure and then reporting a pass is the
practice this project's pre-registration discipline exists to prevent.

**It came back +0.679**, against +0.644 at five seeds — still under the +0.70 bar, with the
binding half also still failing at +0.181 against 0.20. So E1's failure is **not** a
precision artifact: 2.4 times the seeds moves the correlation by 0.035 and does not rescue
it. The five-seed verdict above stands as the pre-registered result, and the twelve-seed run
supports rather than overturns it. `analyse_eo` reads the five-seed archive by signature so
the recorded verdict cannot drift under a later re-run; pass `--signature canonical` for the
latest.

## Extended to five populations: the failure deepens

Connecticut, Kentucky and South Carolina were added afterwards, four cutoffs each. On the
resulting **20 arms**:

| | two states | **five states** |
|---|---|---|
| E1 — rate vs pie change | +0.644 **FAILS** | **+0.334 FAILS** |
| E2 — rate vs exchange rate | −0.748 HOLDS | **−0.439 FAILS** |
| E0 — binding (median) | +0.160 FAILS | **+0.146 FAILS** |
| parity on the same arms | +0.775 | **+0.762** |

**More data made this worse, not better.** E1 halves, and E2 — which held on two states —
now fails as well. Demographic parity on the identical 20 arms is unmoved at +0.762, so the
divergence is not a property of the extra populations; it is a property of the criterion.

This is the outcome that should raise confidence in the reported failure rather than lower it.
A weak-but-real effect would have firmed up with 2.5 times the arms. This did the opposite,
which is what a near-absent relationship looks like when you stop being able to fit it to four
convenient points.

**The scope condition is therefore stronger than first written**: under equalized odds the
selection rate does not usefully predict the direction at all, rather than predicting it
weakly. It still beats "predicts nothing" at 0.30 by a slim margin, and nothing more should be
claimed for it.

## What this costs, and what it is worth

The paper can no longer say the rule is about fairness constraints in general. It is a claim
about **criteria that constrain selection rates**, and equalized odds is outside its scope.

That is a smaller claim and a better-defended one. It also sharpens the mechanism: the
direction of levelling down tracks the selection rate precisely *because* the constraint acts
on selection rates, which is why the effect shrinks by an order of magnitude when the
criterion stops mentioning them. Document 32 showed the rate is the operative variable rather
than the task; this shows the constraint has to act on the rate for that to matter.

The checklist item that commissioned this test said either outcome was publishable —
generalisation, or a scope condition on the scope condition. This is the second one.
