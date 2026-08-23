# 59 — The deployable form preserves the verdict

**Individual work, beyond the course submission. Post-hoc tests, labelled as such.**
The four items the third council rated cheapest-per-answer, all run 25 Aug; the first is
the bank examiner's deployment objection, answered with data.

## 1. Derandomization: 10 of 10 (`analyse_derandomized.py`)

Every direction result in this project is measured on ExpGrad's randomized mixture, but
a US lender under adverse-action duties deploys a deterministic model. Thresholding the
mixture's per-person probability at 0.5 on ten natural arms spanning both directions:
**the extracted model agrees with the mixture's pool direction on 10/10**, with the
parity repair largely intact (extracted gaps 0.009–0.034 vs baselines 0.08–0.19).

Two side-findings:

* **Rate-matched extraction is not generally possible.** The mixture's probability takes
  few discrete values; thresholding at the quantile that targets the mixture's own rate
  lands off it because of ties — on OR/KY/SC far enough off to flip the measured pool
  change's sign. The 0.5 extraction is the well-defined one.
* **Composes with document 58's natural-arm control:** natural-point mixtures are graded,
  so they extract safely; a flat-lottery arm has no score-respecting extraction and
  derandomizing it undoes the parity it bought (the paper's existing Cotter point). The
  two results bound each other.

## 2. The domain table is not a property of the floor (`analyse_floor_sensitivity.py`)

Every row of tab:domains re-scored at gap floors 0.02/0.05/0.08/0.10, using each row's
original arm set and loaders — provenance verified by exact reproduction of the
published values at 0.05 (+0.801/4, +0.858/4, +0.870/5, +0.915/6). Across all floors
every correlation stays in **+0.80 to +0.92 with no sign change**; HMDA is
floor-invariant outright; Alabama only thins below scoreability at 0.10. The floor
dependence of the exploratory states (SC +0.905 → +0.012) does not reach the domain
table.

## 3. Seed-level sign stability: the near-zero arms are the whole story

16 of the 19 sealed arms (both cohorts) are unanimous in sign across their five seeds.
The three splits are exactly the near-zero effects: **Minnesota (−0.04%, the miss)
splits 3/5 — and Iowa (+0.04%, scored correct) splits 3/5 identically.** Two
statistically indistinguishable arms, one counted for the rule and one against it. This
is the sharpest form of the minimum-magnitude lesson and the direct justification for
Algorithm 1's INDETERMINATE verdict. Arkansas (−2.55%) splits 4/5; everything at ≥1% is
unanimous. (`analyse_verdicts.py --seed-stability`)

## 4. Two worked traces, in the paper

Oregon 2018 traced line-by-line to WITHDRAWAL (floor 0.636; 18 arms → 14 kept spanning
0.111–0.653; spread 7.14; one rising sign change; bracket 0.528–0.589; r0 = 0.353;
observed −3.0%), and LSAC to UNSWEEPABLE at line 8 before any fit (band 0.056), with
the counterfactual VOID shown had the guard been ignored. Appendix of the paper.

## Paper state

14 pages, builds clean; the derandomization paragraph joins the Procedure section, the
floor sentence joins §V-D, the seed accounting joins §resealed. Remaining computes are
unchanged from document 58 minus these four: blind-mixture optimality, nested bootstrap,
multi-market HMDA, ACSEmployment/Coverage loaders — and the IPUMS third cohort, still
the binding design.
