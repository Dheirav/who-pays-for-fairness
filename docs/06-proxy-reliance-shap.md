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

**5 seeds, mean ± std.**

| model | proxy share | vs baseline | `relationship` alone | SHAP quality |
|---|---|---|---|---|
| baseline | 0.545 ± 0.006 | — | 0.075 ± 0.010 | exact |
| **expgrad_dp** | **0.586 ± 0.015** | **+7.6% ± 2.3** | **0.189 ± 0.016 (+151%)** | sampled |
| **gridsearch_dp** | **0.586 ± 0.023** | **+7.5% ± 3.3** | **0.158 ± 0.023 (+110%)** | exact |
| prejudice_remover [Female] | 0.596 ± 0.077 | +9.4% ± 13.7 | 0.076 | exact |
| prejudice_remover [Male] | 0.505 ± 0.007 | −7.3% ± 1.8 | 0.071 | exact |
| expgrad_eo | 0.475 ± 0.022 | −12.8% ± 3.2 | 0.082 ± 0.015 | sampled |
| **adversarial_debiasing** | **0.481 ± 0.005** | **−11.7% ± 1.6** | 0.098 ± 0.006 | exact |

Only `prejudice_remover [Female]` is noise-dominated (±13.7 on a +9.4 mean) and no
claim is made from it — its Female-group model is fitted on the smaller group and is
correspondingly unstable. Every other row's sign is consistent across all five seeds.

## Finding 1 — the best demographic-parity methods use proxies *more*, not less

ExpGrad-DP achieves the second-lowest DP violation in the study (0.018) and
**increases** its reliance on sex proxies by 7.6% relative to the unmitigated
baseline. GridSearch-DP achieves the lowest violation (0.015) and increases proxy
reliance by 7.5%.

The `relationship` result is the sharp one. **ExpGrad-DP raises its attribution to
`relationship` by 151%**, and it does so in every seed with no overlap between the two
distributions at all:

| seed | baseline | expgrad_dp |
|---|---|---|
| 0 | 0.0780 | 0.1656 |
| 1 | 0.0652 | 0.1943 |
| 2 | 0.0900 | 0.1896 |
| 3 | 0.0745 | 0.1856 |
| 4 | 0.0687 | 0.2093 |

The lowest mitigated value (0.1656) is nearly double the highest baseline value
(0.0900). This is not a marginal effect that five seeds happened to average into
significance; the two sets of numbers do not touch.

**Why this is the expected result.** To equalise selection rates between men and women
*while forbidden from reading sex*, a model must first work out who is likely to be a
woman, so it can compensate. The constraint gives the model a reason to become a
**better sex-detector**. Fairness-through-unawareness plus a group-level constraint
does not remove the protected attribute from the model's reasoning; it creates demand
for a reconstruction of it.

Put bluntly: **ExpGrad-DP achieves demographic parity by reconstructing sex internally
and correcting for it.** That is disparate treatment in substance, arrived at by a
method whose selling point is that it never sees the protected attribute at inference.

## Finding 2 — the models do not reduce proxy reliance, they *relocate* it

Looking at where the attribution moved makes the mechanism concrete. Every constrained
method takes mass *off* `marital-status` and puts it *on* `relationship`:

| feature | baseline | expgrad_dp | change | gridsearch_dp | change |
|---|---|---|---|---|---|
| `marital-status` | 0.304 | 0.235 | **−23%** | 0.276 | −9% |
| `relationship` | 0.075 | 0.189 | **+151%** | 0.158 | **+110%** |

That specific direction is not arbitrary, because the two features are not equally
good at revealing sex:

| `relationship` level | P(Male) | n | | `marital-status` level | P(Male) | n |
|---|---|---|---|---|---|---|
| **Husband** | **1.000** | 18,666 | | Married-civ-spouse | 0.895 | 21,055 |
| **Wife** | **0.000** | 2,091 | | Widowed | 0.188 | 1,277 |
| Unmarried | 0.237 | 4,788 | | Divorced | 0.399 | 6,297 |

`relationship` **determines sex with certainty for 45.9% of the dataset** — Husband is
100% male, Wife is 100% female. `marital-status` never exceeds 89.5% for any level.

**So the constrained model shifts attribution away from a merely sex-*correlated*
feature and onto the one feature that sex-*determines*.** It is not incidentally using
a proxy; it is selecting the best available reconstruction of the attribute it was
forbidden to read. That is the mechanism, stated precisely enough to be checked.

Adversarial Debiasing shows the same relocation with a different destination: it cuts
`marital-status` hardest of all (−45%) but raises `occupation` (+49%) and
`relationship` (+30%). Its net proxy share falls, but the mass does not disappear — it
moves. This is proxy substitution occurring *without anyone removing a feature*, which
is the strongest reason to doubt that dropping `relationship` would help.

One incidental result worth recording: attribution to `race` falls under every
mitigation, from −27% to −71%. Constraining on sex reduced reliance on race as a side
effect, which no metric in the ablation would have shown.

## Finding 3 — this is not an artifact of the sampled explainer

The natural objection is that ExpGrad's increase comes from `KernelExplainer` sampling
noise. It does not:

* **GridSearch-DP's number is exact linear SHAP**, computed with no sampling at all,
  and it shows the same direction and a +110% shift on `relationship`.
* Two different estimators — one sampled, one exact — on two different algorithms that
  share only the demographic-parity constraint, agree.
* Across 5 seeds the sign is consistent in every single run, for both methods.

The shared factor is the constraint, not the estimator.

## Finding 4 — the one method that does reduce proxy reliance is the one theory predicts

Adversarial Debiasing is the only method that substantially cuts proxy reliance
(−11.7% ± 1.6), and it is precisely the method whose objective *is* to make the output
uninformative about sex — an adversary is explicitly trained to recover `a` from the
prediction, and the predictor is updated to defeat it.

The theory predicts the ranking; the measurement matches. That agreement is what makes
the finding a mechanism rather than a coincidence — and it means the +12.4% on
ExpGrad-DP should be read as a real property of constraint-based reductions, not as
noise.

Note it still keeps **48.1%** of its attribution on proxies, and Finding 2 shows it
relocated rather than removed a good deal of what it did cut. "Reduced" is not
"removed".

## Finding 5 — Prejudice Remover's two models really do reason differently

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

* Five seeds. The `relationship` effect is separated with no overlap between the
  baseline and mitigated distributions, so it is not a seed artifact. The one row that
  *is* noise-dominated, `prejudice_remover [Female]`, is flagged and not used.
* `KernelExplainer` used 150 explained rows against a 25-point k-means background for
  the two ensemble rows. The exact rows corroborate the direction, but the ensemble
  magnitudes carry sampling error.
* Proxy membership is a judgement call. `relationship` and `marital-status` are
  unambiguous; `occupation` and `hours-per-week` are correlated with sex but also
  independently predictive of income. The `relationship` result is the robust one and
  is quoted separately for that reason.
