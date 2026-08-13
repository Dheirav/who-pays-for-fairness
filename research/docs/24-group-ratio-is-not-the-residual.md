# 24 — Group ratio is not the missing explanation

**Individual work, beyond the course submission.** Tests the candidate
[document 23](23-the-selection-rate-sets-the-direction.md) named for the magnitude it could
not explain. Predictions and thresholds were fixed in `src/experiments/analyse_ratio.py`
and committed before any arm was run. **G2, the prediction this document existed to test,
failed — and failed with the opposite sign.**

## What was predicted

Document 23 established that the selection rate sets the *direction* of levelling down and
recorded that it does not set the magnitude: Alabama loses 2.34% of favourable decisions at
a selection rate of 0.252 where Adult loses 20.5% at 0.205.

Group ratio was the candidate, and not an idle one — documents 11 and 13 found it a genuine
cause of the rate-versus-people divergence, acting through cross-flow. Adult's sex arm sits
at 2.08 privileged per unprivileged and Alabama's at 1.09, so the prediction was that **a
larger ratio means more levelling down**.

Four states spread across the race arm's ratio range, crossed with five income cutoffs.
Ratio varies between states, selection rate within. States were chosen so that sample size
is not monotone in ratio.

## The result

| state | ratio | cutoff | selection rate | change in favourable decisions | destroyed per created |
|---|---|---|---|---|---|
| MS | 1.94 | $70,000 | 0.070 | **−62.13%** | 17.61 |
| MS | 1.94 | $50,000 | 0.198 | −28.05% | 2.65 |
| AL | 3.20 | $70,000 | 0.110 | −19.83% | 2.17 |
| AL | 3.20 | $50,000 | 0.257 | −15.21% | 1.81 |
| UT | 8.52 | $70,000 | 0.153 | −4.68% | 1.45 |
| OR | 6.36 | $50,000 | 0.351 | −2.89% | 1.51 |
| UT | 8.52 | $50,000 | 0.314 | −0.80% | 1.10 |
| MS | 1.94 | $20,000 | 0.748 | **+4.50%** | 0.41 |
| AL | 3.20 | $20,000 | 0.762 | +8.14% | 0.25 |

Six of twenty arms were excluded by the pre-registered degeneracy rule (baseline parity gap
under 0.05); the fourteen that remain carry the analysis.

**G0 — both factors moved.** HOLDS. Ratio 1.94 to 8.52 (4.4×); selection rate spans
0.67–0.74 within every state.

**G1 — document 23 replicates in the race arm.** HOLDS, and strongly. Within-state
correlations between selection rate and pie change are **+0.969 (AL), +0.933 (MS), +0.874
(OR), +0.991 (UT)** — every one above the sex arm's Alabama figure of +0.801.

**G2 — a larger ratio means more levelling down.** **FAILS.** Partial r = **+0.535**
holding the selection rate fixed, against a bar of −0.40. The sign is the opposite of the
prediction: in this design a *larger* group ratio goes with *less* levelling down.

**G3 — and it is not sample size.** FAILS in the same direction (+0.484).

**G4 — the floor still tracks the damage.** HOLDS. r = **−0.990** across all twenty arms,
including Mississippi at $70,000 where the plain constraint destroys 62% of all favourable
decisions and the floor brings it back to −2.2%.

## What this means, and what it does not

**The prediction is refuted.** Group ratio does not explain the magnitude residual in the
direction documents 11 and 13 made plausible. Document 23's "something else" remains
unidentified, and this document does not identify it.

**The reverse is not established.** The association runs the other way, but log-ratio takes
only **four distinct values** here, one per state, so after adjusting for selection rate the
comparison is effectively between four points. That is enough to refute a predicted sign; it
is not enough to assert the opposite one. Documents 11 and 13 record what happens when this
project reads a confident direction off a small number of populations, and the correction
cost a retraction. The honest reading is: **candidate eliminated, replacement not found.**

**The Adult–Alabama puzzle is untouched**, and it should be noted that it lives in a
different arm. The observation that motivated this test — 2.08 against 1.09, 20.5% against
2.34% — is from the *sex* arm, while ratio can only be varied in the *race* arm. If ratio
acts differently across protected attributes, as the DP/EO conflict does
([document 14](14-why-the-conflict-is-unpredictable.md)), this design could not have seen
it. That is a limitation of the only design available, not a defence of the hypothesis.

## What this adds anyway

Two things, neither of which was the point of the experiment.

**Document 23 now spans two protected attributes.** Its selection-rate result was two states
of the sex arm; it now holds in four states of the race arm at correlations from +0.874 to
+0.991. Six populations, two attributes, same direction, crossover in the same region. That
is a materially stronger claim than document 23 could make on its own.

**The floor's behaviour extends to the extreme.** Mississippi at $70,000 is the worst
levelling down measured anywhere in this project: −62% of favourable decisions destroyed,
17.6 for every one created. The floor takes it to −2.2%. The r = −0.990 tracking now covers
a range from −62% to +8%.

## Limits

* **Four distinct ratios**, one per state, so the ratio factor has four levels regardless of
  how many cells are computed.
* **Race arm only**, for the structural reason that the sex arm has no ratio spread.
* **The White vs non-White split** is coarse, as document 11 states where the arm was
  introduced: it exists to vary counts, and is not a claim about racial fairness.
* **Ratio and selection rate are not fully crossed in practice.** Mississippi has both the
  lowest ratio and the lowest selection rates, which is why the partial correlation rather
  than the raw one carries the verdict.
