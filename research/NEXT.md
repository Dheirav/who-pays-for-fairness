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

**DONE — and it FAILED.** See [document 33](docs/33-the-rule-does-not-survive-equalized-odds.md).
Pre-registered at `e658ed1` before any arm ran. E1 came in at **r = +0.644** against a bar of
+0.70, and a 12-seed precision check moved it only to +0.679. E0's binding half also failed.
The relationship is present (it beats the "predicts nothing" constant at 0.30) but weaker
than parity's +0.775 on the same eight arms, with magnitudes ~8x smaller.

**Alabama alone would have been a false positive** at +0.822 with everything holding; Oregon
took it below the bar. The pre-registration covered both, and the interim Alabama figures
were never treated as the answer.

**Consequence for the paper.** The claim is about **criteria that constrain selection rates**,
not fairness constraints in general. That is the scope condition this item said would be
publishable either way.

---

## 3. A second base learner

**Weakness.** Almost everything is logistic regression. "This is a property of linear
models" is a cheap objection with no answer currently.

**DONE** — see [document 36](docs/36-not-a-property-of-linear-models.md). T0–T3 all hold under
boosted trees: r = +0.902, partial +1.000, and the crossover sits at **0.255–0.601** against
the linear model's **0.252–0.598** on the same four arms. It does not move. The stronger
learner also starts off *more* unfair, not less, so no arm was excluded where two were before.
Four cutoffs rather than six; the two omitted are the extremes the exclusion rule discards.

**Time.** ~30 minutes compute on an idle machine; the first attempt took 33 minutes for a
single arm because the box was oversubscribed 2x. Cap `OMP_NUM_THREADS` when running it
beside anything else.

---

## 4. The bridge from finding to recommendation

**Weakness.** The paper says *check your selection rate* and never says what to do about
the answer. A finding that changes no decision is weaker than one that does — and the
evidence for the recommendation already exists in documents 21 and 23.

**DONE** — see [document 35](docs/35-what-to-do-about-it.md). Everything below was written
into it, and the middle item turned out to be answerable rather than a caveat.

- [x] Write the decision procedure into the discussion:
      **below the crossover**, expect withdrawal — add a selection-rate floor, ~0.12
      accuracy points, and the benefit scales with the damage (r ≈ −0.99);
      **above it**, the constraint is likely safe unconstrained
- [x] State the residual honestly: **the crossover does not transfer between domains.**
      0.25–0.60 on ACS income, 0.64–0.77 on HMDA lending (document 31). It *is* stable
      within a domain — two routes agree (document 32) and three tolerances agree
      (document 34) — so it is measurable, just not a constant
- [x] **Give the procedure for measuring it**, which document 32 supplies as a by-product:
      sweep your own model's decision threshold, run the constraint at each point, find where
      the sign changes. No new data, no relabelling. This is the strongest available bridge
      from finding to recommendation and it did not exist when this item was written
- [x] Scope it: the rule is for **rate-constraining criteria** (document 33)
- [x] No new experiments. Writing only.

**Time.** An hour of writing.

---

## 5. Housekeeping the audit exposed

- [x] **Document 05 must cite FRAME** (Ferry et al. 2023) — done. Named as prior art for
      the decomposition in `docs/05`, `docs/README`, PAPER.md (claims table and framing
      corrections), the paper draft (§2, §4.1, references) and both supervisor write-ups
- [x] **Claim (ii) must cite Maheshwari et al. (2023)** alongside Kearns — done in
      `paper/draft.md` (§2 and the reference list), `PAPER.md` (claims table and framing
      corrections), research doc 12, `research/README.md`, `prof-meet/README.md` and
      `02-findings.tex`, course `docs/07` and `scripts/build_report.py`. The split to keep:
      Kearns is the failure mode, Maheshwari is why an aggregate audit misses it
- [ ] **Stop presenting the thesis sentence as a finding.** "The metric reports the same
      success either way" is Maheshwari's observation for intersectional fairness and
      FRAME's for individual impact. It is the organising frame, not a result
- [x] **Document 26 said "fourteen held-out populations"**; it is fourteen arms from four
      populations — KY, SC, CT at four income cutoffs each, and Louisiana in two
      protected-attribute arms. Corrected in docs 26 and 28, `research/paper/draft.md`,
      `research/prof-meet/02-findings.tex` and `PLAIN-ENGLISH.md`, and the docs test

---

---

## Work done beyond the five items

These were not on the list. They were added because the list's own results exposed them.

**The route confound (document 32).** Document 23 reaches a selection rate by moving the
*label*, so it could never separate "the rate sets the direction" from "task difficulty does".
Pre-registered at `a73e1e0`, then tested by holding the label fixed and moving only the
model's decision line. The rate wins, on two states, and the crossover lands in the same place
both times. **This also resolved document 31's non-overlapping band**, which had been disclosed
without an explanation for four documents.

**The tolerance confound (document 34).** Every result sat at ε = 0.01 — an objection the
project had raised against itself in the plan deck and never tested. The crossover is identical
across a 25× range.

**A seed-noise crack in document 33.** Under equalized odds three arms flipped sign between
seeds at five seeds. A 12-seed re-run was commissioned *before* the full verdict was known and
reported whichever way it fell; it moved r from +0.644 to +0.679 and did not rescue the
failure. `analyse_eo` now reads its pre-registered archive **by signature**, so a later re-run
cannot silently restate a recorded verdict.

---

## Still open

- [x] **Extend every robustness test beyond one or two populations.** Done — 84 arms across
      CT, KY, SC and pooled HMDA. Two of the five tests had rested on Alabama alone, and
      Alabama appeared in every test, so a single unusual population would have moved several
      conclusions together. It did not, but the extension **changed three of the four
      documents it touched**, and one of them substantially
- [x] **Locate the crossover on HMDA by the operating-point route.** Done, pre-registered as
      H1 at `ed788bd`. **Undecidable** — the relationship on lending is non-monotone, so no
      crossover can be bracketed. Document 35's central recommendation is therefore *not*
      validated on the domain it is aimed at, and now says so

- [ ] **Fix document 23's T1 by adding a minimum-spread guard**, as document 33's E0 has.
      Connecticut returns r = −0.924 on a spread of 0.34 percentage points and T1 scores that
      as a refutation. The guard has to be applied *retrospectively and stated*, not slipped
      in — every arm set already scored under T1 must be re-reported with its spread
- [ ] **Decide what to do about mis-calibrated arms in the operating-point sweep.** On ACS
      data extreme thresholds are filtered automatically because the parity gap collapses; on
      HMDA the gap stays large, so a model approving 35% where 72.5% are approved (accuracy
      0.594) counts as a valid arm and breaks monotonicity. Needs a stated accuracy-based
      exclusion, pre-registered before re-running
- [ ] **A sixth population that is neither ACS nor HMDA**, if the crossover claim is to be
      about domains rather than about two instruments
- [ ] **Nothing is committed past the pre-registrations.** ~30 files of literature
      housekeeping, five new documents, six new tests and the rebuilt PDF/PPTX are uncommitted

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
