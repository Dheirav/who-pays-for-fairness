# 45 — Intervals on the crossover, and how much work the 0.05 threshold was doing

**Individual work, beyond the course submission.** **Post-hoc and labelled so.** Both analyses
answer questions raised by external review after the results existed. Neither uses new data.

Two things this project asserted without quantifying: that the crossover estimates are precise,
and that the exclusion rules are not doing the work.

---

## Intervals: the cluster is real, and looser than reported

Every crossover has been quoted as a bracket between two arms, with no uncertainty attached, so
"0.511" and "0.576" read as measurements of equal precision. Resampling seeds *within* arms
(2,000 draws) and recomputing the bracket each time:

| population | crossover | 95% interval | bracket exists in |
|---|---|---|---|
| Dutch census | 0.576 | 0.572 – 0.580 | **100%** |
| ACS S. Carolina | 0.530 | 0.526 – 0.533 | 98.6% |
| ACS Oregon | 0.558 | 0.556 – 0.560 | **77.4%** |
| COMPAS | 0.511 | **0.434 – 0.524** | 82.8% |
| ACS Alabama | — | — | **0%** |
| ACS Kentucky | — | — | **0%** |

**Two corrections follow, and both weaken what was written.**

**COMPAS's interval is six times wider than the others** — 0.434 to 0.524 against Dutch's
0.572 to 0.580. [Document 44](44-how-much-and-where-two-concessions-tested.md) reported the
cluster as 0.511–0.576 with a standard deviation of 0.029, computed over four *point
estimates*. Carrying the intervals, the cluster spans roughly **0.43 to 0.58**. It is still a
cluster — four populations across three domains and two countries whose intervals overlap — but
it is not as tight as a standard deviation of 0.029 implies, and that figure should not be
quoted without the intervals beside it.

**Oregon's bracket does not exist in 23% of resamples.** Its crossover is reported as a
measurement; in nearly a quarter of seed draws there is no sign change to bracket at all. That
is a fact about how close its arms sit to zero, and it belongs next to the estimate.

Alabama and Kentucky never bracket, in any resample, which is consistent with document 42:
their viable bands stop at 0.566 and 0.561, so they cannot reach above the crossover.

---

## Sensitivity: the 0.05 threshold was doing more work than acknowledged

Arms are excluded when the baseline parity gap falls below **0.05**. That number was inherited
from [document 12](12-intersectional-across-populations.md), where it was chosen to drop one
degenerate population, and has never been varied. Re-scoring every population across a grid,
holding the accuracy rule fixed:

| population | 0.01 | 0.02 | **0.05** | 0.10 |
|---|---|---|---|---|
| Dutch census | +0.851 | +0.908 | **+0.946** | +0.938 |
| COMPAS | +0.844 | +0.844 | **+0.844** | +0.871 |
| ACS S. Carolina | **+0.012** | **+0.012** | **+0.905** | +0.849 |
| ACS Oregon | **+0.095** | **+0.095** | **+0.664** | — |
| ACS Alabama | −0.368 | −0.368 | −0.368 | +0.296 |
| ACS Kentucky | −0.590 | −0.590 | −0.654 | — |
| **populations clearing r ≥ 0.70** | **2** | **2** | **3** | **3** |

**South Carolina moves from +0.012 to +0.905 between a threshold of 0.02 and 0.05.** Oregon
moves from +0.095 to +0.664. On the two ACS populations that hold at the inherited threshold,
the correlation is **created by the exclusion**.

**This has to be said plainly: at a more inclusive threshold, only COMPAS and the Dutch census
clear the bar.** The ACS results depend on excluding arms whose baseline parity gap is between
0.01 and 0.05.

### Whether that is a defect or the rule working

There is a real reason for the threshold, and it is the reason document 12 gave: an arm with a
parity gap of 0.02 has almost nothing for the constraint to remove, so its change in the pool
is near zero and dominated by seed noise. Including such arms adds points clustered at the
origin, which flattens any correlation regardless of whether the underlying relationship holds.
That is the same argument as document 37's minimum-spread guard, applied to the other axis.

So the exclusion is defensible on its face. **But "defensible" is not "shown not to matter",
and this project has been reporting it as though it were.** The honest statement is:

> The relationship holds on all six populations at the inherited threshold of 0.05 in the sense
> the paper claims; on two of six it survives a threshold of 0.01; and the ACS populations in
> particular depend on the exclusion. COMPAS and the Dutch census hold at every threshold
> tested.

**COMPAS and Dutch are therefore the load-bearing populations** — they are also the two with
the widest viable bands and the largest spreads, which is consistent rather than coincidental.
The ACS populations should be presented as supporting evidence conditional on a stated
exclusion, not as independent confirmations.

---

## What changes

* The paper reports intervals on every crossover, and stops quoting a standard deviation of
  0.029 without them.
* The sensitivity table goes in. A reviewer asking "why 0.05?" gets the sweep rather than an
  assurance.
* The claim is re-weighted toward COMPAS and the Dutch census, which survive every threshold,
  and away from treating six populations as six independent confirmations.
* Document 44's cluster figure is amended: the interval-carrying range is **0.43–0.58**, not
  0.511–0.576.

Neither of these was found by re-reading the documents. Both came from being asked a question
the documents did not answer, which is the third time in this project that an assumption
survived until something forced it to be computed.
