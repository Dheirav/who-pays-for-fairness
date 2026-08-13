# 21 — The floor replicates, and one of my predictions does not

**Individual work, beyond the course submission.** Tests [document 19](19-levelling-up-is-expressible.md)
across every population in this folder. Predictions and thresholds were fixed in
`src/experiments/analyse_levelling_up.py` before the sweep finished; the disclosure about
Wyoming is repeated below.

## What was run

`run_levelling_up` on nine ACS states in both protected-attribute arms, five seeds each,
ε = 0.01, plus Adult from document 19. **19 populations, no failed runs.**

Three arms per population: unconstrained, `expgrad_dp`, and `expgrad_dp` stacked with a
floor on the overall selection rate set at the unconstrained model's own rate.

**Disclosure.** Wyoming's sex arm was run first as a timing probe and its result was seen
before the predictions were written. One of eighteen ACS cells was therefore not blind. It
is kept in the analysis and named rather than dropped, because dropping a population after
seeing it is the larger sin.

## The verdict

| | sex arm (10) | race arm (9) |
|---|---|---|
| **L1** parity is not sacrificed | **HOLDS** — mean \|Δ DP\| 0.0020 | **HOLDS** — 0.0037 |
| **L2** the pie survives | **FAILS** — 6/10 | **FAILS** — 4/9 |
| **L3** who pays changes | **HOLDS** — 10/10 | **HOLDS** — 9/9 |
| **L4** it stays cheap | **HOLDS** — +0.12 pts | **HOLDS** — +0.15 pts |
| **L5** noisier when small | **HOLDS** — r = −0.708 | **HOLDS** — r = −0.567 |

**The two arms agree on all five predictions.** Unlike the DP/EO conflict of
[document 14](14-why-the-conflict-is-unpredictable.md), this does not reverse across
protected attributes.

## L2 failed, and the fault is in the prediction

L2 required that the floored arm's loss of favourable decisions be *smaller in absolute
value* than the plain arm's in **every** population. It is not, in 4 of 10 sex-arm
populations and 5 of 9 race-arm ones.

The reason is that the floored arm does not land near zero — it overshoots **upward**:

| | plain | floored |
|---|---|---|
| mean change in favourable decisions, sex arm | −6.4% | **+2.1%** |
| mean change, race arm | −7.4% | **+3.1%** |
| mean *absolute* change, all 19 | 6.88% | **2.65%** |
| populations still shrinking the pie | 18/19 | **1/19** (Adult) |

The construction is `P(h(x) = 1) ≥ target`, an inequality. Nothing stops the optimiser
exceeding the floor, and it does. My test treated any departure from zero as failure, so a
population where the plain constraint barely shrank the pie (Alabama, −2.3%) counts as a
failure when the floor grows it (+4.3%).

**This is recorded as a failed prediction, not repaired into a passing one.** The
threshold was fixed in advance and the result is what it is. Two things follow, and they
should be weighed separately:

* **L3 tests the same substantive claim without the flaw, and was also fixed in advance.**
  The exchange rate — favourable decisions destroyed per one created — fell in **19 of 19
  populations**, from 1.47 to 0.88 in the sex arm and 1.59 to 0.79 in the race arm. Under
  1.0 means more decisions created than destroyed. It goes from **1 of 19** populations
  under 1.0 to **16 of 19**. On the substance, the finding replicates and does so
  unanimously.
* **There is a real caveat inside L2's failure, and it is not a technicality.** The floored
  model hands out *more* favourable decisions than the unconstrained model it replaced, in
  18 of 19 populations. That is a more permissive classifier, with whatever false-positive
  cost that carries. Document 19 framed the floor as protecting the pie; it does more than
  protect it. Whether that is desirable is a question about the deployment and not one this
  measurement answers.

Setting the floor as an equality rather than an inequality would test the narrower claim.
That is a different experiment and is not run here.

## Adult is the extreme case, not the typical one

Document 19's headline numbers are the most dramatic in the study:

| | Adult | mean of the other 18 |
|---|---|---|
| plain constraint's pie change | **−20.5%** | −6.1% |
| plain constraint's exchange rate | **2.68** | 1.46 |

Adult is also the only population where the floored arm still shrinks the pie at all
(−0.6%), because it starts from so much further down.

**This is a correction to how document 19 should be read.** Its measurements stand and were
re-verified. But "−20.5% to −0.6%, exchange 2.68 to 1.03" describes the population with the
worst levelling-down problem in the study, and quoting it as representative overstates the
typical case by roughly a factor of three. The typical case is −6.1% to +2.6%, exchange 1.46
to 0.85 — smaller, in the same direction, and still worth having.

## L5: document 15's caution reaches this construction

Predicted in advance: below roughly 2,500 test subjects the method's own randomness should
make the effect noisier. It does, in both arms.

| | sex arm | race arm |
|---|---|---|
| r(test size, across-seed spread of the floored pie change) | −0.708 | −0.567 |
| spread, under 2,500 test subjects (WV, ND, VT, WY) | 5.25 | 4.76 |
| spread, at or above 2,500 | 3.44 | 2.64 |

The four smallest populations show roughly 1.6× the across-seed spread of the larger ones.
A single-seed run on any of them could report almost anything.

## Two populations that should carry a caveat

* **Vermont, sex arm.** Baseline DP difference is **0.0125** — there is essentially no
  disparity to close. [Document 12](12-intersectional-across-populations.md) excluded
  Vermont on exactly this ground, at a baseline gap of 0.0124. It is retained here because
  excluding it *after* seeing that it is one of L2's failures would be the post-hoc move
  [document 13](13-separating-ratio-from-size.md) records going wrong. The exclusion ground
  is stated so a reader can apply it; it does not rescue L2 either way, since Alabama, West
  Virginia and New Mexico also fail.
* **North Dakota, race arm.** The constraint did not bind: DP lands at **0.0871** against a
  requested ε of 0.01. Whatever else that row measures, it is not a satisfied constraint.

## What this changes

| claim | status |
|---|---|
| Document 19's Adult measurements | **Stand.** Re-verified exactly (0.0178/0.0179, −20.5%/−0.6%, 2.68/1.03) |
| "Levelling up is expressible" | **Replicated**, 19 populations, both protected-attribute arms |
| Parity is not traded away for the pie (L1) | **Confirmed** across all 19 |
| The floor is cheap (L4) | **Confirmed**, and cheaper than Adult suggests: +0.12–0.15 pts against Adult's 0.38 |
| Document 19's numbers as representative | **Corrected.** Adult is the extreme; the typical effect is about a third the size |
| The floor merely *protects* the pie | **Corrected.** It grows it, in 18 of 19 populations |
| L2 as I specified it | **Failed.** Recorded, not repaired |

## Limits

* **Still one survey.** Nineteen populations, eighteen of which are ACS state slices
  sharing an instrument, an encoding and a threshold construction. This replication
  addresses *population*, not *domain*, and the distinction matters — see
  [PAPER.md](../PAPER.md).
* **One base learner, one ε, one constraint pairing.** Logistic regression, ε = 0.01,
  demographic parity plus a selection-rate floor.
* **Five seeds**, which L5 itself suggests is too few on the four smallest populations.
* **The floor target is still a choice.** Set at the unconstrained model's own selection
  rate throughout, as in document 19. Nothing here explores setting it elsewhere.
