# 57 — The inversion was (mostly) the label sliding: the real-threshold diagnostic

**Individual work, beyond the course submission. Post-hoc diagnostic, labelled as such.**
Second of the three candidate mechanisms from the review council; the first (pandemic
nonresponse weighting) was exculpated at label level the same day (`weight_audit.py`:
PERWT moves 2022's rates and gaps no more than 2018's). Sweeps in
`research/results/acs_income_*_2022_t60000_levelling_up*`.

## The design

The four inverted 2022 populations were re-swept with the income label at **$60,000**, the
approximate 2018-real-equivalent of the original $50,000 (CPI-U 2018→2022 ≈ +18%). The
choice was confirmed on target before sweeping: at $60k the 2022 base rates (0.29–0.33)
land exactly where the same states' 2018 base rates sat at $50k (0.31–0.34).

## The result

| state | 2022 @ $50k | 2022 @ $60k (retained arms, low→high rate) |
|---|---|---|
| OH | inverted (`+------`) | **classic: `------++`, crossover 0.55–0.61, spread 6.2** |
| AL | inverted (`+++-----`) | all-negative, spread 1.2 (below guard) — the positive limb is gone |
| SC | inverted (`++------`, flat) | all-negative, spread 0.7 (below guard) — limb gone |
| NV | inverted | `+++-` at spread 1.6, 4 arms after the gap floor — unresolved noise |

Ohio, the signal-rich lineage (classic 2018, classic 2019, inverted 2022-at-$50k), is
**cleanly classic at the real threshold**, its crossover back where its 2018/2019 values
sat. Alabama and South Carolina lose their inverted limbs entirely, reverting to
monotone-family behaviour consistent with their 2018 mid-ranges, though at spreads below
the void guard. Nevada — smallest sample, sex gaps at the exclusion floor in every recent
vintage — remains a noise-level residual that neither confirms nor denies anything.

## What this settles, and what it does not

* **The "2020s inversion" is substantially an artifact of a fixed nominal label.** Between
  2019 and 2022 the $50k threshold slid down an inflated, bottom-compressed earnings
  distribution; measured at constant real value, three of four states behave like their
  2018 selves and the phenomenon shows no detected time-dependence from 2014 through 2022.
  Document 54's "the relationship's first sign-flip" is hereby superseded: the sign
  flipped because the task changed under the label, not because the world changed the
  relationship.
* **The practitioner warning sharpens rather than vanishes**: any deployment whose
  favourable-outcome definition is a fixed nominal quantity is silently running a
  different task each year, and the deformation this produces is exactly what the 2022
  arms recorded. Re-anchor labels in real terms, or re-run the audit per vintage.
* **The sealed shape test's failure (document 54) stands as scored** — it was sealed on
  nominal thresholds and failed on nominal thresholds. A post-hoc observation follows and
  is *not* a resurrection: at real-anchored thresholds the 2022 base rates fall below the
  0.365 boundary and three of four shapes are monotone-family, which is what the boundary
  would have called. Whether the base-rate boundary holds under real anchoring is a
  hypothesis for the IPUMS cohort, not a claim.
* **The composition-reweighting diagnostic (third candidate) is recorded as unnecessary**
  for the main question: the threshold mechanism accounts for the recoverable signal, and
  the only residual (NV) sits below the spread guard in both labelings, where no
  diagnostic can grip.

## Changes carried into the paper

The abstract's "for reasons not yet identified" becomes the identified mechanism; the
limitations' unattributed-shift paragraph is rewritten around nominal-label drift with the
weighting exculpation noted; and the vintage instruction is replaced by the sharper, more
useful one: measure your own current data, and anchor labels in real terms.
