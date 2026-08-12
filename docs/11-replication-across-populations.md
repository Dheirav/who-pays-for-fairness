# 11 — Replication: which findings are about the method, and which about Adult?

**Not in the initiation document, and beyond the course submission.** Documents 01–10
are all measurements on a single dataset. This document tests whether they generalise.

## Why this had to be done

Every finding in documents 05–10 is a statement about **UCI Adult**, a 1994 census
extract with a fixed $50K threshold and known idiosyncrasies. Ding et al. (2021)
published *Retiring Adult* specifically to argue the field should stop drawing
conclusions from it. Until a finding survives a population it was not derived from,
"the constraint causes X" and "Adult has property X" are indistinguishable.

So three predictions were **stated in advance**, derived from the Adult results, and
tested on nine US states from ACS Income (folktables) — 10 populations, 160 runs.

The populations were chosen to span the two quantities the predictions depend on:

| | range across the 10 populations |
|---|---|
| base-rate gap, P(y=1\|priv) − P(y=1\|unpriv) | 0.101 (VT) → 0.279 (UT), a 2.8× spread |
| group ratio, N_priv / N_unpriv | 1.02 (MS) → 2.08 (Adult) |
| population size | 3,064 (WY) → 45,222 (Adult) |

**Result: one prediction confirmed, one confirmed only under a condition that had to be
discovered, one not confirmed.** Two failures out of three is the useful outcome. A
clean sweep would suggest the predictions had been fitted to the data they came from.

---

## P3 — CONFIRMED. Proxy relocation needs a proxy worth relocating onto.

**The prediction.** Document 06 found that the demographic-parity constraint moves
attribution onto `relationship`, whose Husband/Wife levels determine sex outright for
45.9% of Adult. The stated mechanism was that the constrained model *searches for the
best available reconstruction of the protected attribute*. If that is right, a
population with no such feature should leak much less sex.

ACS supplies the control for free: it records the same relation as a single `RELP`
code for "husband/wife", which is 50.2% male. No level of `RELP` exceeds P(Male)=0.64.

**The result**, measured by `FairnessDataset.attribute_leakage()` — the ROC AUC of a
probe predicting sex from the remaining features:

| population | leakage AUC | | population | leakage AUC |
|---|---|---|---|---|
| **Adult** | **0.9364** | | WV | 0.7935 |
| ND | 0.8444 | | NM | 0.7794 |
| MS | 0.8316 | | UT | 0.7748 |
| AL | 0.8075 | | VT | 0.7647 |
| WY | 0.7982 | | OR | 0.7604 |

**The distributions do not overlap.** Adult is the only population containing a
sex-determining feature and the only one above 0.85; every ACS population sits between
0.76 and 0.84. The mechanism proposed in document 06 survived nine independent tests
on populations it was not derived from.

This is the project's strongest finding, and it is now the best-supported one.

---

## P1 — CONFIRMED, but only under a condition that had to be discovered.

**The prediction.** Document 05 found the burden looks near-even in *rates*
(0.50–0.58 borne by the privileged group) but lopsided in *people* (0.66–0.74),
because Adult's privileged group is 2.08× larger. The claim was that this divergence
is not a property of Adult but pure population arithmetic:

```
people_share = s·N_priv / (s·N_priv + (1 − s)·N_unpriv)
```

for a rate-level share `s`. On Adult it predicts the observed value to within **0.014**.

**The result.** Across the nine states the mean absolute error is **0.066**, with
single runs off by up to 0.287, and 22 of 160 runs (14%) falling outside [0, 1]
entirely — meaning *both* groups lost ground, which the formula has no way to express.
As a universal law, it fails.

**Why it fails, which is the useful part.** The formula assumes a clean transfer:
privileged lose, unprivileged gain, nobody moves the other way. Define the cross-flow
share as the fraction of movement going the "wrong" way,
`(priv_gained + unpriv_lost) / (priv_lost + unpriv_gained)`. Sorting the populations by
size makes the pattern unmistakable:

| population | n | cross-flow | formula error |
|---|---|---|---|
| WY | 3,064 | 0.330 | 0.096 |
| VT | 3,767 | 0.292 | 0.063 |
| ND | 4,455 | 0.316 | 0.093 |
| WV | 8,103 | 0.255 | 0.044 |
| NM | 8,711 | 0.398 | 0.104 |
| MS | 13,189 | 0.268 | 0.054 |
| UT | 16,337 | 0.272 | 0.070 |
| OR | 21,919 | 0.299 | 0.078 |
| AL | 22,268 | 0.273 | 0.044 |
| **Adult** | **45,222** | **0.045** | **0.014** |

```
error vs cross-flow share   r = +0.885
error vs population size    r = −0.719
error vs group ratio        r = −0.587   ← confounded, see below
group ratio vs population n r = +0.794   ← the confound itself
```

These are now produced by `python -m src.experiments.analyse_sweep`, which prints them
and writes `results/sweep/sweep_p1_formula_fit.csv`. An earlier draft of this document
quoted `r = +0.881` and slightly different per-population cross-flow values, because
that version was computed by hand over *all* runs while the pipeline restricts to the
runs the formula is defined on (share within [0, 1]). The difference changes nothing in
the argument, but the hand-computed version was not reproducible from anything in the
repository, which for the number the whole restatement rests on is not acceptable.

**A correction worth recording.** On the nine states alone, error appeared to *rise*
with the group ratio (r = +0.366), which would have suggested the formula degrades as
groups become more unequal — the opposite of its premise. Adding Adult reversed the
sign to −0.587. Adult happens to be both the largest population *and* the one with the
most unequal groups, so group ratio was standing in for size. Cross-flow is the actual
driver at r = 0.885, and group ratio is a confound. Reading nine points without the
tenth would have produced a confident and wrong mechanism.

The confound is now quantified rather than asserted: across these ten populations
**group ratio and sample size correlate at r = +0.794**, so neither one's relationship
with the error is interpretable on this data alone. Separating them requires
populations where the two do *not* move together, which is what the race arm described
below was built to supply.

**The claim, restated to what the evidence supports:**

> The rate-to-people conversion is exact arithmetic **when the mitigation performs a
> clean transfer between groups**. Cross-flows break it, cross-flows are driven by
> population size, and below roughly 10,000 rows the approximation degrades badly.

That is narrower than the original claim and considerably more useful, because it comes
with a diagnostic: compute the cross-flow share, and you know whether to trust the
conversion.

It also connects to an existing finding. Document 04 reported that GridSearch is the
least stable method, and attributed it to selection over a coarse grid. The
cross-flow result is the same phenomenon seen from another angle: small effective
sample sizes make these methods jitter, and here that jitter is directly measurable as
groups moving in the same direction rather than trading.

---

## P2 — NOT CONFIRMED.

**The prediction.** The impossibility results (Kleinberg et al. 2016; Chouldechova
2017) establish that demographic parity and equalized odds cannot both hold unless base
rates are equal. That is a claim about *whether* the conflict exists. The stronger
quantitative claim tested here is that **the size of the conflict tracks the base-rate
gap**: the further apart two groups' base rates, the more constraining DP should cost
EO.

**The result:**

| population | base-rate gap | baseline EO | EO after DP constraint | cost |
|---|---|---|---|---|
| VT | 0.1008 | 0.0479 | 0.0608 | +0.0129 |
| NM | 0.1158 | 0.0270 | 0.0299 | +0.0029 |
| OR | 0.1309 | 0.0343 | 0.0569 | +0.0226 |
| MS | 0.1770 | 0.0311 | 0.1131 | +0.0820 |
| WV | 0.1831 | 0.0419 | 0.1371 | +0.0952 |
| AL | 0.1957 | 0.0822 | 0.0833 | **+0.0011** |
| Adult | 0.1989 | 0.0949 | 0.2802 | +0.1853 |
| WY | 0.2363 | 0.0885 | 0.1799 | +0.0913 |
| ND | 0.2416 | 0.0508 | 0.1649 | +0.1141 |
| **UT** | **0.2786** | 0.1158 | 0.0968 | **−0.0190** |

`r(cost, base-rate gap) = +0.241` — weak, and driven largely by Adult. **Utah has the
largest base-rate gap in the study and equalized odds *improved* there.** Alabama has
the third largest and paid essentially nothing. Nothing else predicts the cost either:
against the amount of DP actually removed, r = +0.111; against the baseline DP gap,
r = +0.044.

**What does hold:** the conflict itself is near-universal. Constraining demographic
parity made equalized odds worse in **9 of 10 populations**. The direction from
document 04 replicates comfortably; only the proposed magnitude relationship fails.

**An analysis error of mine, recorded rather than quietly fixed.** The first version
normalised the cost by the amount of DP removed. Vermont's baseline was already nearly
fair (DP 0.0102, so only 0.0016 was removed), and dividing by that produced a ratio of
8.81 which dominated the correlation and pushed it negative (r = −0.499). That number
was an artifact of a small denominator, not a finding. The raw cost is reported above
instead.

---

## What this changes in documents 01–10

**Nothing is retracted.** The Adult measurements were correct and have been
re-verified. What changes is the scope claimed for two of them:

| document | status after replication |
|---|---|
| 02–04 (baseline, base paper, ablation) | Untouched — reproduction of the base paper on Adult |
| 05 (who pays) | The Adult observation stands. The general formula gains the cross-flow condition — see the note added to that document |
| 06 (proxy reliance) | **Strengthened.** Its proposed mechanism now has out-of-sample support from nine populations |
| 07 (intersectional) | Untouched; not tested here |
| 09 (proxy removal) | Untouched; the leakage probe it introduced is what made P3 measurable |
| 10 (epsilon sweep) | Untouched; not tested here |

**The course submission is unaffected.** `bias_mitigation_report.pdf` and
`bias_mitigation_plan.pptx` contain no claim this work undermines: the P1 formula
appears in neither, and their who-pays section is explicitly scoped to Adult ("the
privileged group *here* is 2.1× larger"). The PDF's Limitations section already named
ACS replication as the next step, which this is.

## Limits of the replication itself

* **One survey year (2018), one task (ACSIncome), one protected attribute (sex).**
* **Group ratio is poorly spanned by the states, and confounded with size.** ACS
  populations sit between 1.02 and 1.24 on sex; Adult at 2.08 is a lone outlier and
  carries the whole high-ratio end of P1 by itself. Ratio and sample size correlate at
  r = +0.794 here, so this design cannot say which of them drives the error.

  **This is being addressed.** Protecting `RAC1P` instead of `SEX` on the same nine
  states (`--dataset acs:AL:RAC1P`) spans a group ratio of 1.94 to 24.98 and *inverts*
  the confound — r(ratio, n) = **−0.567** there, against +0.794 on sex. AL (n = 22,268,
  ratio 3.20) and OR (n = 21,919, ratio 6.35) supply the high-ratio-at-large-sample cell
  this study has never had. If ratio were the real driver the two arms would disagree in
  sign; if size is, they will agree. Results pending.

  That arm splits White against everyone else. It is **not** evidence about racial
  fairness and is not offered as any: it exists to vary two counts in a formula whose
  only inputs are counts. The alternative split, White against Black, is self-defeating
  for this purpose — the states with a large Black population are the ones nearest 1:1,
  and the high-ratio states would have an unprivileged group of a few dozen people.
* **Three seeds per state against five for Adult**, so the state estimates are noisier
  — which is part of what the cross-flow result is measuring.
* **P2's failure is a failure to find a relationship, not evidence that none exists.**
  Ten populations is a small sample for a correlation, and the base-rate gap may not be
  the right axis. What can be said is that the obvious candidate does not predict it.
