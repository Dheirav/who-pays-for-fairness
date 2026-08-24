# 62 — The quantile is the anchor

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**
The fourth council's cheap-compute batch (25 Aug), following the text fixes committed at
`0303c01`.

## 1. CPI-anchoring and base-rate-anchoring disagree, and the quantile wins

The economist's demand: separate the two anchorings doc 57 conflated. At the strict CPI
deflation of 2018's $50k — $58,275 (CPI-U 251.107→292.655) — Ohio 2022 re-sweeps
**inverted** (`++------` by rising rate, spread 5.6 points, gaps 0.072–0.114, all
accuracies above the 0.645 trivial floor, 9 arms), while at the base-rate-matched
$60,000 it was classic. Natural arms at $58,275: AL +0.42 and NV +0.86 (both below the
1.0-point magnitude guard), SC −2.33. Real incomes grew beyond CPI 2018–2022, so even a
price-fixed label slides down the distribution. Doc 57 is refined in place: the
operative anchor is the label's **quantile**, the time-independence claim holds *at
matched base rate*, and the design lesson — quantile-anchor outcome definitions — is
exactly what the IPUMS stage-A protocol already committed to. (`acs:OH:SEX:58275:2022`
sweeps in `research/results/`.)

## 2. The lottery's structure, observed member by member (`--probe-support`)

On the cut arms the fitted mixture's dominant-weight members grant almost nothing:
COMPAS carries members at weights 0.86–0.88 with positive rates ≤ 1e-4; LSAC one at
0.876 weight and 3e-4; Dutch@0.965 a near-zero member. Every lift arm's members all
grant at graded rates (0.026–0.20). The corrected paper sentence ("a two-member blind
mixture is flat when one member grants nothing") is now direct observation.

## 3. No lottery on the lending natural arms either

The natural-arm control extended to HMDA MS and LA (the adverse-action argument is a
lending argument): both graded — granted-below 0.63, keep-score correlations +0.36 and
+0.47, both arms levelling up (+4.3%, +2.3%). Nine of nine natural arms across survey
and lending instruments show no lottery.

## 4. The prior without Dutch: no call changes

Recomputed from the three surviving located crossovers (0.511, 0.530, 0.558) the
midpoint is 0.53; checked against both sealed cohorts' measured rates, no arm sits
between 0.5345 and 0.54, so no sealed or post-hoc call changes. The committed 0.54
stands as sealed; its provenance is thinner and the paper now says so.

## Still queued from round four (the two majors' experiments)

Attribute-aware **in-processing** on the 17 regime populations (the confound fix — the
regime contrast currently changes optimizer family along with attribute access), the
PERWT-weighted crossover replication, the allocation-flag exclusion rerun, and the
household-clustered bootstrap for sex arms.
