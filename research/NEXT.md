# What to do next, and why each item exists

Live handover document. Each item names the weakness it closes, what has to be done, what
would count as a failure, and whether it needs pre-registering.

**Pre-registration rule for this list:** anything whose outcome could go either way gets its
predictions and numerical thresholds committed *before* the run. Anything that is
re-aggregation of existing results is labelled post-hoc. Both are fine; mislabelling is not.
And after document 26, every pre-registration must also name **the naive baseline it has to
beat**, not just the threshold it has to clear.

---

## 1. A natural population inside the crossover band

**Weakness.** All 21 natural populations sit at a selection rate of ≤0.353 or ≥0.758.
**Zero** sit in 0.36–0.74. The crossover — the centre of the paper's claim — has only ever
been observed by *manufacturing* it with an income cutoff. The obvious review comment is
that the transition was engineered.

**The fix.** HMDA splits naturally by `loan_purpose`, and three purposes land inside the
band, in real lending decisions with no manipulation:

| purpose | approval | race gap |
|---|---|---|
| home improvement | 0.534 | 0.301 |
| other | 0.599 | 0.315 |
| cash-out refinance | 0.608 | 0.244 |
| home purchase | 0.754 | 0.229 |
| refinance | 0.800 | 0.192 |

- [ ] Add a `purpose` argument to `HMDALoader`, reaching the dataset name so arms cannot
      collide on disk (same rule as the threshold knob, `tests/test_acs_threshold.py`)
- [ ] Pool Mississippi and Louisiana, and add a third state if needed, so every purpose arm
      clears **2,500 test subjects** — Mississippi alone gives ~1,100–2,300 for the
      mid-range purposes, below document 15's floor
- [ ] **Pre-register**, naming the baseline to beat: at 0.534 the pie change should be
      *small in magnitude* and *smaller than* at 0.800; the within-HMDA correlation between
      approval rate and pie change should be positive. Naive alternative it must beat:
      "purpose has no effect, all HMDA arms behave alike"
- [ ] Run `run_levelling_up` per purpose arm, five seeds
- [ ] Write up; if the mid-range arms do **not** sit between the extremes, that is a
      failure of document 23's rule on natural data and is reported as one

**Time.** ~40 minutes compute, plus loader work. **Highest value item on this list.**

**DONE** — see [document 31](docs/31-the-crossover-on-natural-data.md). All four predictions
held; home improvement at a selection rate of 0.555 levels **down** while refinancing at
0.871 levels up, in the same market. One complication surfaced and is recorded there: the
natural crossover sits at 0.64–0.77, which does **not** overlap document 23's 0.25–0.60. The
direction relationship replicates; the crossover *location* does not transfer.

---

## 2. Does the flip hold for a second fairness criterion?

**Weakness.** Everything is demographic parity. As it stands the claim is about one
constraint, not about fairness constraints.

- [ ] Add an equalized-odds arm to `run_levelling_up` (`fit_exponentiated_gradient` already
      accepts `constraint="equalized_odds"`)
- [ ] Note the conceptual difference in the write-up: EO does not constrain selection rates
      directly, so any change in the pool is incidental rather than mechanical — which makes
      it a *harder* test, not an easier one
- [ ] **Pre-register**: does the selection rate still predict the direction under EO?
      Baseline to beat: "the rate predicts nothing under EO", i.e. correlation
      indistinguishable from zero
- [ ] Run across the threshold sweep arms already on disk for Alabama and Oregon
- [ ] Either outcome is publishable — generalisation, or a scope condition on the scope
      condition

**Time.** ~1 hour compute. **Best value per hour after item 1.**

---

## 3. A second base learner

**Weakness.** Almost everything is logistic regression. "This is a property of linear
models" is a cheap objection with no answer currently.

- [ ] Add gradient boosting as an alternative `BASE_MODEL`
- [ ] Re-run one full threshold sweep (Alabama, six cutoffs, five seeds) under it
- [ ] Post-hoc, and labelled so — this is a robustness check, not a prediction
- [ ] Report whether the crossover moves

**Time.** ~30 minutes compute.

---

## 4. The bridge from finding to recommendation

**Weakness.** The paper says *check your selection rate* and never says what to do about
the answer. A finding that changes no decision is weaker than one that does — and the
evidence for the recommendation already exists in documents 21 and 23.

- [ ] Write the decision procedure into the discussion:
      **below the crossover**, expect withdrawal — add a selection-rate floor, ~0.12
      accuracy points, and the benefit scales with the damage (r ≈ −0.99);
      **above it**, the constraint is likely safe unconstrained
- [ ] State the residual honestly: the crossover is a *range*, 0.25–0.60, so between those
      values the answer is "measure it, do not assume"
- [ ] No new experiments. Writing only.

**Time.** An hour of writing.

---

## 5. Housekeeping the audit exposed

- [ ] **Document 05 must cite FRAME** (Ferry et al. 2023). Its dimensions D1–D3 are the
      who-pays decomposition, published February 2023
- [ ] **Claim (ii) must cite Maheshwari et al. (2023)** alongside Kearns
- [ ] **Stop presenting the thesis sentence as a finding.** "The metric reports the same
      success either way" is Maheshwari's observation for intersectional fairness and
      FRAME's for individual impact. It is the organising frame, not a result
- [ ] **Document 26 says "fourteen held-out populations"**; it is fourteen arms from four
      populations. Fix the wording wherever it appears

---

## Explicitly not doing

**Chasing the mechanism again.** *Backfire* has it, and document 27 shows its conditions do
not survive contact with data — which is this project's contribution *against* the theory.
Re-deriving would duplicate published work and abandon the better position.

---

## Blocked on the supervisor

- [ ] **Venue and deadline** — sets the page limit, which decides what survives from 20
      research documents
- [ ] **Is the empirical half a paper on its own**, given the theory exists? See
      `prof-meet/03-the-ask.pdf`
- [ ] **How to disclose AI assistance**, and whether the commit trailer should be added
