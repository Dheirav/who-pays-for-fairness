# 28 — How uncertain the headline correlations actually are

**Individual work, beyond the course submission.** Every correlation in this folder has been
reported as a point estimate. This attaches intervals to the load-bearing ones, and answers
the objection a reader is most likely to raise about them.

## Why a plain bootstrap would be wrong

The populations are **not independent**. Arms of the same ACS state share a survey
instrument, an encoding and a sampling design, and the threshold sweeps of
[document 23](23-the-selection-rate-sets-the-direction.md) produce five arms from a single
state. Resampling *arms* would treat those as independent draws and report an interval that
is too narrow.

So the resampling unit is the **population**: Alabama enters a bootstrap draw with all of
its cutoffs or not at all. 5,000 draws, percentile interval.

## The intervals

| claim | r | 95% CI | independent populations | measurements |
|---|---|---|---|---|
| docs/27 — selection rate vs the theory's structural quantity | **+0.935** | [+0.858, +0.984] | 15 | 26 |
| docs/23 — selection rate vs change in favourable decisions | **+0.727** | [+0.588, +0.821] | 15 | 26 |
| docs/26 — held-out selection rate vs λ − p | **+0.901** | [+0.752, +0.974] | **4** | 14 |
| docs/11 — cross-flow vs conversion error | **+0.885** | [+0.808, +0.975] | 10 | 10 |

All four are comfortably clear of zero. **Nothing here is overturned.**

## The caveat this exposes

**Document 26's held-out set is fourteen measurements from four populations.** Fourteen is
the number of arms; four is the number of independent things measured, and the interval
follows the smaller number. That document originally reported "fourteen held-out
populations", which overstated the independence available; it now says *fourteen arms from
four populations*, and so does everything downstream of it.

The interval is still clear of zero, so the conclusion stands. The description of the
evidence does not.

## The objection this answers

A reader will reasonably ask: *is the selection-rate relationship simply an artifact of two
lending datasets sitting at 0.8 while everything else clusters near 0.25?* Two clumps and a
line through them is not much of a finding.

Re-running with **every lending population removed** — survey data only, where the range is
produced by the income-cutoff sweeps rather than by domain:

| claim | all populations | survey only |
|---|---|---|
| docs/27 selection rate vs structural quantity | +0.935 | **+0.957** |
| docs/23 selection rate vs pie change | +0.727 | **+0.686** |

The relationship is **not** carried by the lending populations. Dropping them entirely
*strengthens* the docs/27 correspondence and leaves docs/23 essentially unchanged. The
within-survey variation created by moving the cutoff is doing the work on its own, which is
what the single-factor design was for.

## Limits

* **Percentile bootstrap**, which is the simplest interval and not the most accurate for
  correlations near the boundary. Nothing here is near ±1 tightly enough for that to bite.
* **Clusters are defined by state or lending population.** ACS states arguably still share
  more than that treats them as sharing, since they come from one survey; a stricter
  clustering would treat all of ACS as one unit, which would leave too few clusters to
  bootstrap at all. The intervals should be read as lower bounds on the true uncertainty.
* **This quantifies sampling variability only.** It says nothing about whether the measured
  quantity is the right one, which is what documents 26 and 27 are about.
