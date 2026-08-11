# 01 — Setup and method

Everything downstream depends on these choices, so they are stated before any result.

## The data

UCI Adult Census Income, fetched via `sklearn.datasets.fetch_openml(name="adult",
version=2)` and cached to `data/adult.csv`. Task: predict whether income exceeds
$50K. Protected attribute: `sex`.

After listwise deletion of rows with missing values (`?` or NaN), **45,222 rows**
remain, with these base rates:

| group | value | n | share | P(income > 50K) |
|---|---|---|---|---|
| privileged | Male | 30,527 | 67.5% | **31.25%** |
| unprivileged | Female | 14,695 | 32.5% | **11.36%** |

**That 2.75× ratio in base rates is the entire source of the problem.** Nothing in the
algorithm is malicious. Empirical risk minimisation on data where one group earns
above the threshold far more often will reproduce that difference, because
reproducing it is what minimises error.

This also sets a hard limit that matters for document 04: because the base rates are
unequal, demographic parity and equalized odds **cannot both be satisfied** by any
classifier better than chance. That is a theorem, not a tuning problem, and the
ablation table is a demonstration of it.

### Two columns dropped, deliberately

| column | why |
|---|---|
| `fnlwgt` | A census sampling weight describing how many people the row represents. It is metadata about the survey, not a property of the person. Leaving it in lets the model fit the sampling design. |
| `education` | An exact duplicate of `education-num` in string form. Keeping both double-counts education in any attribution analysis, which would corrupt document 06. |

### `sex` is removed from the feature matrix

The default is `include_protected_in_features=False`, so no model here can read `sex`
directly. This is **fairness through unawareness**, and it is included precisely
because it does not work — the proxies survive. Document 06 measures exactly how much.

## The split

`train_test_split` at 30% test, stratified on the **`(sex, income)` interaction**
rather than on the label alone.

This is not a cosmetic choice. Fairness metrics are computed from four cells —
(privileged, y=1), (privileged, y=0), (unprivileged, y=1), (unprivileged, y=0) — and
the smallest, (Female, >50K), holds about 1,670 test rows. Stratifying on the label
only lets that cell's size drift between seeds, which shows up as fairness-metric
variance that looks like model instability but is really sampling noise. Since
document 04 makes claims about which methods are stable, that confound had to be
removed first.

## Encoding

One-hot for categoricals (`handle_unknown="ignore"`), standardised numerics; the
encoder is fitted on the training split only. 85 encoded columns from 11 source
features.

The encoder is fitted **separately** from the estimator rather than bundled into an
`sklearn.Pipeline`. The reason is the mitigation stage:
`ExponentiatedGradient` refits its base estimator with `sample_weight`, and a
`Pipeline` will not route that keyword to its final step without extra plumbing.
Handing the reduction a bare estimator over pre-encoded arrays keeps the base paper's
reweight-and-retrain loop working unmodified.

**Encoding is not a bias intervention.** No row, label, or class balance is altered.
The project's "the training data is never modified" claim is about the mitigation
stage, and it holds: all six methods change only the objective handed to the learner.

## The metrics

Implemented from their definitions in `src/metrics.py`, not called out of a library,
so the report can state exactly what was computed:

| metric | definition | fair at |
|---|---|---|
| Demographic parity difference | \|P(ŷ=1\|priv) − P(ŷ=1\|unpriv)\| | 0 |
| Equalized odds difference | max(\|TPR gap\|, \|FPR gap\|) | 0 |
| Disparate impact | P(ŷ=1\|unpriv) / P(ŷ=1\|priv) | 1 |

`crosscheck_against_fairlearn()` asserts agreement with `fairlearn.metrics` on every
run. That check exists because a privileged/unprivileged orientation slip produces
numbers that look entirely plausible and are silently wrong.

Rates with an empty denominator return **NaN, not 0**, so that an undefined rate can
never masquerade as a perfectly fair one. Document 07 depends on this: one
intersectional subgroup has zero positive labels, and its TPR must come back
undefined rather than as a confident zero.

## Two base classifiers

| model | why it is carried |
|---|---|
| Decision tree (depth 8) | What the initiation document specifies for the base-paper track. Non-linear, and the reduction wraps it as a black box — which is the base paper's central claim. |
| Logistic regression (max_iter=2000) | Required for the ablation. Prejudice Remover adds a term to a likelihood; Adversarial Debiasing needs gradients to flow from an adversary into the predictor. Neither can wrap a tree. |

**The ablation table uses logistic regression for all six rows**, including the
reductions rows that the base-paper track runs on a tree. Reporting a tree for some
rows and a linear model for others would vary the hypothesis class *and* the
mitigation simultaneously, so the table would not isolate what it claims to. The
base-paper track (document 03) keeps the tree, as specified.

## What "in-processing" means here, precisely

All six methods modify only the objective or the training procedure. None resamples,
reweights-on-disk, relabels, or edits a single row. Note that
`ExponentiatedGradient`'s reweighting happens *inside the optimisation* — it changes
how much each example counts in the objective on each iteration, and no row is
duplicated or dropped. That distinction is what keeps it an in-processing method.

This is also why Reweighing (Kamiran & Calders 2012), offered as an optional row in
the initiation document, was **left out**: it is pre-processing. Adding it would break
the single property that unifies the other six rows and make the table's framing
weaker, not stronger.
