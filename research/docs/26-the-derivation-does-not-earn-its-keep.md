# 26 — The derivation passes its tests and fails to earn its keep

**Individual work, beyond the course submission.** Tests the derivation committed in
`src/experiments/analyse_mechanism.py` at **17:30:14**, against fourteen arms from four
populations whose
first result was written at **18:15:52** — genuinely held out, and the ordering is
verifiable in the git log and the file timestamps.

**Verdict: M0 holds, M1 and M3 pass their pre-registered bars, M2 fails — and the
derivation is nonetheless not supported.** A trivial baseline does better. The
pre-registration was too weak to discriminate, and that is the finding.

## What was predicted

Document 23 showed the direction of levelling down flips with the selection rate and gave
no reason. The derivation supplied one: under group-wise thresholding, calibration, a
location shift and a unimodal score density, levelling down is a *curvature* effect, the
sign of which follows the curvature of the quantile function, so

    sign(lambda - p) = sign(rbar - m)

with `m` the selection rate at the **mode** of the score density, and the crossover at the
mode.

## What happened

Three ACS states never previously used (KY, SC, CT) at four cutoffs each, plus a second
HMDA state (Louisiana) in both its protected-attribute arms. No failed runs.

That is **fourteen arms from four populations**, not fourteen populations. Arms of the same
ACS state share rows, features and groups and differ only in the income cutoff, so they are
not independent evidence; the count that governs any interval is four, which is why
[document 28](28-how-uncertain-are-the-correlations.md) resamples populations rather than
arms. Every `n/14` below is a count of arms.

| | result | bar | verdict |
|---|---|---|---|
| **M0** identity holds | max error 0.0758 pts | 0.5 | **HOLDS** |
| **M1** sign prediction | 12/14 = 0.86 | 0.75 | **HOLDS** |
| **M2** crossover at the mode | gap 0.189 | 0.15 | **FAILS** |
| **M3** curvature predicts size | r = −0.756 | 0.30 | **HOLDS** |

Both M1 misses are Connecticut, and they are the two smallest effects in the set:
|λ − p| of 0.021 and 0.028, against a mean of 0.086 where the prediction hit. The sign
prediction fails exactly where the effect is near zero, which is where a sign prediction
should be fragile.

## Why it is not supported anyway

A check the pre-registration did not include, run afterwards and therefore **post-hoc**:

| rule | held-out accuracy |
|---|---|
| **derived**: levelling up iff `rbar > mode` | **12/14 = 0.86** |
| naive: levelling up iff `rbar > 0.5` | **13/14 = 0.93** |
| naive: levelling up iff `rbar > 0.4` | 13/14 = 0.93 |

**A constant beats the derivation.** And the reason is visible in the data:

* `r(rbar, mode_rate) = −0.802`. The measured mode moves inversely with the selection rate,
  so `sign(rbar − m)` is largely determined by `rbar` alone. The mode carries almost no
  independent information.
* M3 is the same story. `r(curvature, λ−p) = −0.756` looks strong, but
  `r(rbar, λ−p) = +0.901` is stronger, and the **partial correlation controlling for the
  selection rate is −0.182**. Once you know the selection rate, the curvature tells you
  almost nothing more.

So both surviving predictions pass *through* the selection rate rather than beyond it. The
derivation reproduces what document 23 already knew and adds no explanatory power on this
test set.

## The methodological failure is mine

The bars were fixed in advance, which is necessary, and they were **not sufficient**. I
pre-registered thresholds without pre-registering a **baseline to beat**. A prediction that
clears 0.75 while a constant clears 0.93 has told us nothing, and the pre-registration as
written could not detect that.

This is the same class of error as document 21's L2 — a test specified so that passing it
did not mean what it appeared to mean — and it is recorded rather than repaired. Any future
pre-registration in this project should name the naive alternative its prediction must
outperform, not just the threshold it must clear.

## What survives

**The identity, and it is worth keeping.** `pie preserved ⟺ λ = p` needs no assumptions,
held to 0.0758 percentage points across all fourteen held-out arms, and reframes
levelling down as the optimiser choosing a compromise below the size-weighted one. Nothing
in the reading found it stated anywhere. It is a definition, not a discovery, but it is a
clarifying one.

**Document 23 is untouched.** The empirical finding — direction tracks the selection rate,
crossover between 0.25 and 0.60 — is not only unaffected but **replicated on fourteen more
arms, from four populations it had not seen**, including a second lending state. `r(rbar, λ−p) = +0.901` across the held-out
set.

**The curvature account is not refuted, only unsupported.** Curvature and selection rate are
collinear in this design (that is what made the design cheap), so it cannot separate them. A
test that could would need populations where the two come apart — score distributions with
the same operating rate and different shapes. That is a harder experiment and is not run.

## Where this leaves the paper

The paper reports the flip as an **empirical regularity with an identity that clarifies it
and a mechanism it does not have**. That is where document 23 already stood; the attempt to
go further is recorded as an attempt that did not succeed.

The honest framing for §4.4 is that the identity localises the question — everything reduces
to where the optimiser places the common rate relative to the size-weighted point — and that
why it places it there remains open.

## Limits

* **Four populations, not fourteen.** Twelve of the fourteen arms are three ACS states at
  four cutoffs each; the other two are one lending state under two protected attributes.
  The collinearity between curvature and selection rate may be a property of these four
  populations rather than of the phenomenon, and fourteen arms give four chances to catch
  that, not fourteen.
* **The mode is estimated by a fixed-bandwidth KDE.** The bandwidth was fixed in advance to
  avoid tuning it to the answer, which was right, but a poor estimator would look exactly
  like a refuted theory. The estimates are not obviously degenerate — they span 0.178 to
  0.874 — but they were not independently validated.
* **A3, the location-shift assumption, was flagged in advance as the weakest** and is a
  live candidate for why the derivation underperforms.
