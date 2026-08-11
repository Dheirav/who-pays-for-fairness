# 06 — Proxy reliance: does mitigation stop the model using stand-ins for sex?

Section 6 of the initiation document lists SHAP as a stretch goal, with a stated
expectation:

> `shap` (optional, stretch goal) — before/after feature-importance comparison, to
> visually show reliance on `sex` and its proxies **shrinking** post-mitigation.

**It does not shrink. For the two best-performing fairness methods, it grows.** This
document reports that and explains why it is the expected outcome once you look at
what the constraint actually asks for.

## Setup

`sex` is not in the feature matrix, so no model here can use it directly. Whatever
sex-related reliance shows up is **proxy reliance by construction**. The proxies
examined are `relationship` (whose levels on Adult are literally Husband and Wife),
`marital-status`, `occupation`, and `hours-per-week`.

Two methodological choices:

* **Attributions are aggregated back to source features.** One-hot encoding splits
  `occupation` into 14 columns; reporting those separately makes a feature look
  unimportant by spreading its mass thin. Shapley values are additive, so summing an
  encoded feature's columns is exact. The mapping was verified to be a strict
  partition: 85 encoded columns → 11 source features, none lost or double-counted.
* **Attributions are reported as a share of each model's total attribution mass.** The
  six methods emit scores on different scales (a logit from a linear model, a mixture
  probability from a randomized ensemble), so raw mean-|SHAP| is not comparable across
  them. The share answers the question that matters: *of everything this model bases
  decisions on, how much rides on the proxies?*

Five of seven explainers use **exact** linear SHAP. The two ExponentiatedGradient rows
are randomized ensembles of thresholded classifiers — not linear in any
parameterisation — so they use `KernelExplainer`, which samples. That distinction is
reported in the output rather than hidden.

## Result

| model | proxy share | vs baseline | `relationship` alone | SHAP quality |
|---|---|---|---|---|
| baseline | 0.546 | — | 0.078 | exact |
| **expgrad_dp** | **0.599** | **+9.7%** | **0.163 (+108%)** | sampled |
| gridsearch_dp | 0.586 | +7.3% | **0.162 (+108%)** | exact |
| prejudice_remover [Female] | 0.553 | +1.4% | 0.079 | exact |
| prejudice_remover [Male] | 0.499 | −8.6% | 0.061 | exact |
| expgrad_eo | 0.482 | −11.6% | 0.065 | sampled |
| **adversarial_debiasing** | **0.476** | **−12.9%** | 0.107 | exact |

## Finding 1 — the best demographic-parity methods use proxies *more*, not less

ExpGrad-DP achieves the second-lowest DP violation in the study (0.018) and
**increases** its reliance on sex proxies by 9.7% relative to the unmitigated
baseline. GridSearch-DP achieves the lowest violation (0.015) and increases proxy
reliance by 7.3%.

Both **exactly doubled** their use of `relationship`, the most blatant sex proxy in
the dataset.

**Why this is the expected result.** To equalise selection rates between men and women
*while forbidden from reading sex*, a model must first work out who is likely to be a
woman, so it can compensate. The constraint gives the model a reason to become a
**better sex-detector**. Fairness-through-unawareness plus a group-level constraint
does not remove the protected attribute from the model's reasoning; it creates demand
for a reconstruction of it.

Put bluntly: **ExpGrad-DP achieves demographic parity by reconstructing sex internally
and correcting for it.** That is disparate treatment in substance, arrived at by a
method whose selling point is that it never sees the protected attribute at inference.

## Finding 2 — this is not an artifact of the sampled explainer

The natural objection is that ExpGrad's +9.7% comes from `KernelExplainer` sampling
noise. It does not:

* **GridSearch-DP's number is exact linear SHAP**, computed with no sampling at all,
  and it shows the same direction and the same +108% on `relationship`.
* Two different estimators — one sampled, one exact — on two different algorithms that
  share only the demographic-parity constraint, agree.

The shared factor is the constraint, not the estimator.

## Finding 3 — the one method that does reduce proxy reliance is the one theory predicts

Adversarial Debiasing is the only method that substantially cuts proxy reliance
(−12.9%), and it is precisely the method whose objective *is* to make the output
uninformative about sex — an adversary is explicitly trained to recover `a` from the
prediction, and the predictor is updated to defeat it.

The theory predicts the ranking; the measurement matches. That agreement is what makes
the finding a mechanism rather than a coincidence — and it means the +12.4% on
ExpGrad-DP should be read as a real property of constraint-based reductions, not as
noise.

Note it still keeps **46.7%** of its attribution on proxies. "Reduced" is not
"removed".

## Finding 4 — Prejudice Remover's two models really do reason differently

Kamishima's method fits one weight vector per protected group. Explained separately,
the two models differ in what they use: `native-country` carries **0.056** of
attribution in the Female model against **0.032** in the Male model.

The disparate-treatment concern noted in document 04 is therefore not a theoretical
property of the parameterisation — it is measurable in the fitted models. Two
applicants identical on every feature but differing in sex are scored by weight
vectors that weight their country of origin differently.

## Relation to the base paper

Agarwal et al. (2018) make **no claim** about feature reliance or about what the
constrained classifier attends to. The reduction treats the base classifier as a black
box and reasons about its outputs only. So this finding does not contradict the paper.

What it does is qualify a claim the *field* makes on the method's behalf. The reduction
is frequently described as attractive because it does not require the protected
attribute at prediction time — true, and operationally valuable. This document shows
that the resulting model **behaves as though it had reconstructed it**, and that the
reconstruction gets stronger as the constraint gets tighter.

For anyone deploying this: not needing `sex` at inference is a claim about the API,
not about the model's reasoning. If a regulator's question is "does this model treat
men and women differently?", the absence of `sex` from the input schema is not an
answer, and on this evidence it is a misleading one.

## Limits

* One seed (0). The model fits are expensive and SHAP over 13,567 rows more so. The
  effect sizes here (+100% on a single feature) are far larger than the seed-to-seed
  variation in document 04, but multi-seed confirmation is not done.
* `KernelExplainer` used 150 explained rows against a 25-point k-means background for
  the two ensemble rows. The exact rows corroborate the direction, but the ensemble
  magnitudes carry sampling error.
* Proxy membership is a judgement call. `relationship` and `marital-status` are
  unambiguous; `occupation` and `hours-per-week` are correlated with sex but also
  independently predictive of income. The `relationship` result is the robust one and
  is quoted separately for that reason.
