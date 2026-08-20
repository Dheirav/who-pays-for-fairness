# 31 — The crossover appears without manufacturing it

**Individual work, beyond the course submission.** Predictions and thresholds were fixed in
`src/experiments/analyse_purpose.py` and committed at `3931d83`, before any arm was run.

## The weakness this closes

Every natural population in this project sat at a selection rate of ≤0.353 or ≥0.758. **Zero**
sat in the band where [document 23](23-the-selection-rate-sets-the-direction.md) puts the
crossover. The transition had only ever been produced by moving an arbitrary income cutoff,
and the obvious review comment was that it had been engineered.

## The design: a natural split of real decisions

Lenders record *why* a loan was sought, and approval rates differ sharply by purpose because
home-improvement lending and refinancing are different businesses. Pooling Mississippi and
Louisiana, race arm, five seeds. Nothing is manipulated — one instrument, two states, one
year, real decisions.

| purpose | selection rate | baseline parity gap | change in favourable decisions | destroyed per created |
|---|---|---|---|---|
| home improvement | 0.555 | 0.354 | **−1.57%** | 1.10 |
| other | 0.643 | 0.325 | **−1.46%** | 1.12 |
| cash-out refinance | 0.773 | 0.215 | **+2.28%** | 0.74 |
| home purchase | 0.818 | 0.193 | **+7.41%** | 0.30 |
| refinance | 0.871 | 0.165 | **+2.95%** | 0.43 |

**P0 — the arms differ and each has something to fix.** HOLDS. Rates span 0.555 to 0.871;
smallest test set 2,581 against a floor of 2,500; smallest parity gap 0.165.

**P1 — the relationship holds on natural data.** HOLDS. **r = +0.803**, against a bar of
+0.70 and a naive "no relationship" alternative of |r| < 0.30.

**P2 — the ordering holds.** HOLDS. Spearman **ρ = +0.900**.

**P3 — lowest arm below highest.** HOLDS. Home improvement −1.57% against refinance +2.95%.

## The part that was deliberately not predicted

The pre-registration refused to predict the *sign* at the lowest arm, on the grounds that it
sits inside the crossover band where the rule does not determine direction.

**It came out negative.** Home improvement, a real lending product, at a selection rate of
0.555, **levels down** — while refinancing in the same two states in the same year levels up.

That is the crossover **observed** rather than constructed. Two lending products, one market,
opposite effects from the identical constraint, with nothing manipulated to produce it.

It is also the sharpest available version of the paper's practical claim: a bank running one
fairness constraint across its loan book would take opportunities away in home improvement
and hand them out in refinancing, and its fairness report would show success in both.

## The discrepancy, which must be reported

**The crossover here sits between 0.643 and 0.773. Document 23 put it between 0.25 and 0.60.**

These do not overlap. The *relationship* replicates — direction tracks the selection rate, at
r = +0.803 — but the *location* of the transition does not transfer from the ACS
threshold sweeps to natural lending data.

Three readings, and this document does not choose between them:

* the crossover point genuinely depends on the domain, so it is a property of a task rather
  than a constant;
* the ACS sweeps move the label's cutoff, which changes the difficulty of the prediction
  problem as well as the rate, and the two may not be equivalent ways of reaching the same
  selection rate;
* one or both estimates are imprecise, given five arms here and six per state there.

**What this costs the paper.** Document 23's "crossover between 0.25 and 0.60" cannot be
quoted as a general threshold. The defensible claim is the *direction relationship*, which
now holds on manufactured and natural variation alike, plus a per-domain crossover that has
to be measured rather than assumed. That is weaker than a universal number and stronger than
a result that only appears when you move a cutoff yourself.

## The floor, incidentally

It rescues both negative arms — home improvement from −1.57% to +1.29%, other from −1.46% to
+0.04% — and leaves the already-positive arms essentially untouched (+7.41% to +7.42% on
purchase). Consistent with [document 23](23-the-selection-rate-sets-the-direction.md)'s
finding that the remedy scales with the damage and is inert without it.

## Limits

* **One domain, two states, one year.** The natural variation is across loan purposes within
  US mortgage lending, not across domains.
* **Five arms** carry the correlation.
* **Purpose is not randomly assigned.** Loan purposes differ in applicant population, loan
  size and risk as well as approval rate, so this is natural variation rather than a
  controlled manipulation. It is the complement to document 23's single-factor sweep, not a
  replacement: that design controls everything and manufactures the rate, this one changes
  nothing and accepts confounding. **Both together are the argument**; either alone is open
  to the objection the other answers.
