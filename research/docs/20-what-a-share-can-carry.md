# 20 — What a share can carry

**Individual work, beyond the course submission.** **Post-hoc, and not pre-registered.**
Everything below is recomputed from results already committed to `results/`, by
`src/experiments/analyse_attribution.py`, and the analysis was written after looking at
them. Documents 13 and 18 both record what happens when a quantity chosen after seeing the
data is then reported as a test, so none of this is offered as one. It decomposes a number
the documents already quote, and its only claim is about what that number can bear.

```
python -m src.experiments.analyse_attribution --pair relationship marital-status
```

## The estimand, and what it cannot identify

`explain.aggregate_attributions` ends with `series / series.sum()`. Every attribution
figure in documents 06, 16 and 17 is a **share of the model's total attribution mass**.

That choice is defended in `src/explain.py` and the defence is sound — six methods emit
scores on different scales and raw mean-|SHAP| is not comparable across them. But shares
are compositional. They sum to one, so no feature's share can move without another's
moving to pay for it, and a rise in one feature's share is equally consistent with:

1. that feature's absolute attribution rising while the others hold still;
2. that feature holding still while others fall, so its share rises mechanically;
3. total mass changing while the feature holds its absolute position.

Document 06's headline — `relationship` **+151%** under a demographic parity constraint —
cannot distinguish these. Neither can document 17's excess, which is built from the same
quantity. **"Which features the model leans on" is not identified by share movements
alone.** That is a limit of the measure, not an error in the measurement.

## The collinear pair as one coalition

`relationship` and `marital-status` are Adult's two most redundant features (Cramér's V
0.487, against 0.217 for the next-closest pair). If the constraint reallocates credit
between them, refusing to divide that credit should absorb the effect. Document 18 already
records the aggregate signature — the pair moves 0.183 in magnitude while its combined
share moves 0.045. What was missing is the per-seed spread, which decides whether the
residual is an effect or noise.

Adult, five seeds, `expgrad_dp` against baseline:

| seed | `relationship` | pair, combined |
|---|---|---|
| 0 | +112.4% | +5.1% |
| 1 | +198.1% | +13.6% |
| 2 | +110.6% | +11.3% |
| 3 | +149.0% | +8.7% |
| 4 | +204.7% | +19.3% |
| **mean** | **+155.0%** (sd 45.1) | **+11.6%** (sd 5.4) |

**Scoring the two redundant features as one coalition takes the headline from roughly
+150% to roughly +12%** — better than an order of magnitude smaller. Most of document 06's
number is credit moving *within* a pair of features that are near-substitutes for each
other.

The residual is not nothing. It is positive in **5 of 5 seeds** with a spread well clear of
zero, so something survives the correction, and any collinearity account has to explain it
rather than absorb it.

## The residual is constraint-specific, which an artifact should not be

Holding the algorithm fixed at exponentiated gradient and changing only the constraint:

| method | `relationship` | pair, combined |
|---|---|---|
| `expgrad_dp` | +150.9% | **+11.7%** |
| `expgrad_eo` | +9.5% | **−26.4%** |
| `gridsearch_dp` | +109.7% | **+14.2%** |
| `prejudice_remover [Female]` | +137.6% | +20.5% |
| `prejudice_remover [Male]` | −5.1% | −12.5% |
| `adversarial_debiasing` | +29.8% | −30.1% |

Same reduction, same base learner, same data: **demographic parity raises the pair's
combined share and equalized odds lowers it.** `gridsearch_dp`, the other Agarwal
algorithm under the same constraint, moves the same way as `expgrad_dp`.

This matters for the reading document 18 leaves open. If the pair-level movement were
purely an artifact of how Shapley divides credit between collinear features, it should not
care which constraint was imposed — the collinearity of `relationship` and
`marital-status` is a property of the dataset, identical in every row of that table. It
does care. That is weak evidence that the residual is a real, constraint-specific effect
and not a measurement artifact.

`prejudice_remover` is explained once per protected group and its two columns disagree in
sign, so it supports nothing either way and is shown rather than dropped.

## The swap account is at best partial

Share is zero-sum, so which loss *became* which gain is not identifiable. What is
identifiable is how concentrated the losses were. A pure swap inside the collinear pair
predicts `marital-status` funds nearly all of `relationship`'s gain:

| feature | share given up | of all share released |
|---|---|---|
| `marital-status` | −0.0694 | **44.9%** |
| `capital-gain` | −0.0469 | **30.3%** |
| `age` | −0.0125 | 8.1% |
| `native-country` | −0.0101 | 6.5% |
| `hours-per-week` | −0.0070 | 4.5% |
| `race` | −0.0046 | 3.0% |
| `workclass` | −0.0042 | 2.7% |

`marital-status` supplies **under half**. The next largest donor is `capital-gain`, which
is neither a sex proxy nor redundant with `relationship`. Collinear reallocation is a
partial account of the shift, not a complete one.

## What this changes

| claim | status |
|---|---|
| Document 06's measurement, `relationship` +151% of share | **Stands.** Correct as a share, and re-verified. It should be quoted alongside the coalition figure |
| Document 06's mechanism (reconstruction-seeking) | Refuted in document 16, unaffected here |
| Document 16's replacement (outcome-signal-seeking) | Refuted in document 17, unaffected here |
| Collinear reallocation (document 17's third candidate) | **Partially supported.** It accounts for most of the headline number and not for the seed-consistent, constraint-specific residual. Document 18 called it untested; it is now bounded, though by re-aggregation rather than by intervention |
| Document 17's general claim — the DP constraint does not systematically change which features the model leans on | **Narrowed.** See below |

## Narrowing document 17

Document 17 concluded, in bold, that *the demographic-parity constraint does not
systematically change which features the model leans on*. Its evidence is six cells on one
**planted** column in Alabama, where the excess never exceeded 0.03 share while the share
itself ranged over an order of magnitude.

Three things that evidence does not carry:

* **It observed one column, not a profile.** The planted column's share being stable under
  the constraint says nothing about whether the other eleven features churned.
* **Adult is a counterexample under the same constraint.** `relationship` moves +0.114 of
  share — nearly four times the 0.03 that document 17 treats as "tracking almost exactly."
  Document 18 sets this aside as "a question about SHAP on one dataset," which is a
  reasonable hypothesis and is not a tested one.
* **The estimand cannot support the general form.** Shares do not identify which features
  a model leans on, so no share-based result can establish that the constraint leaves that
  unchanged.

What the evidence does carry, and what document 17 should say: *on a planted column, under
demographic parity at ε = 0.01, on one population, the constrained model's attribution
share tracks the unconstrained model's to within 0.03 across six cells spanning an
order of magnitude in that share.* That is still a useful and somewhat surprising result.
It is not a statement about feature use in general.

## Limits

* **Post-hoc.** The coalition and the donor split were chosen after seeing the shift, in a
  project that has twice recorded that move going wrong. Nothing here should be treated as
  a test that could have failed.
* **Re-aggregation, not intervention.** Documents 16 and 17 refuted their candidates by
  planting a column and watching the model. This re-expresses existing numbers. It bounds
  the collinearity account; it does not establish it.
* **Adult only, one base learner.** Five seeds, logistic regression, ε = 0.01.
* **The absolute magnitudes are still not measured.** The three stories in the first
  section remain unseparated, because the raw mean-|SHAP| totals are normalised away
  before anything is written to disk and are not recoverable from the committed files.
  Separating them needs `aggregate_attributions` to return the unnormalised totals as
  well, and a re-run. That is the honest next step and it has not been taken here.
