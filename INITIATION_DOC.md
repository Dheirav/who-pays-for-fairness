# Project: Algorithmic (In-Processing) Bias Mitigation on Adult Census Income

## 1. Goal

Demonstrate detection and mitigation of algorithmic bias in an income-prediction
classifier, using **purely algorithmic (in-processing)** fairness methods — i.e.
the training data is never modified. Only the training objective / procedure
changes. Structure: (a) implement one base paper end-to-end with full results,
(b) run an ablation study comparing other in-processing methods against it,
all under identical data/model/metric conditions.

## 2. Dataset

- **Name:** UCI Adult Census Income Dataset
- **Source:** https://archive.ics.uci.edu/dataset/2/adult
- **Task:** Binary classification — predict whether income is `>50K` or `<=50K`
- **Protected attribute:** `sex` (Male/Female)
- **Reference implementation to draw pipeline structure from:** GitHub project
  "Adult Census Income Project" by JcFreya (load data → clean/preprocess →
  encode categoricals → train/test split → train Decision Tree → predict →
  evaluate accuracy). This is a baseline scaffold only — the actual project
  goal is the fairness layer added on top of it.

## 3. Problem formulation

Dataset: `D = {(x_i, a_i, y_i)}` for i = 1..n, where:
- `x_i` = feature vector (age, education, occupation, hours-per-week, etc.)
- `a_i` ∈ {0,1} = protected attribute (sex)
- `y_i` ∈ {0,1} = label (income >50K or not)

**Unconstrained baseline (standard ERM):**

```
min_h  E[(x,y)~D] [ 1{h(x) != y} ]
```

No reference to `a` — but since P(y=1 | a=Male) >> P(y=1 | a=Female) in this
dataset historically, the model can pick up `a` (or proxies for it, e.g.
relationship/marital-status) as a predictive shortcut. This correlation is the
entire source of the bias; nothing "malicious" in the algorithm, just ERM on
data with unequal base rates across groups.

**Fairness metrics φ(h) to compute (protected attribute a, prediction h(x), label y):**
- Demographic Parity Difference: `| P(h(x)=1 | a=1) - P(h(x)=1 | a=0) |`
- Equalized Odds Difference: max gap in TPR and FPR between groups
- Disparate Impact (ratio form): `P(h(x)=1 | a=0) / P(h(x)=1 | a=1)`

**Reframed, constrained problem (what this project actually implements):**

```
min_h  E[1{h(x) != y}]   subject to   φ(h) <= epsilon
```

Data D is never edited. Only the optimization problem given to the learner
changes — a constraint region is added and the search is for the best
classifier inside it, not the best classifier anywhere.

## 4. Base paper (primary track — implement fully, report full results)

**Agarwal, A., Beygelzimer, A., Dudík, M., Langford, J., & Wallach, H. (2018).
"A Reductions Approach to Fair Classification." ICML 2018.**

- Solves the constrained problem above via Lagrangian relaxation: a two-player
  zero-sum game between a **learner** (picks h to minimize error − fairness
  penalty) and a **regulator** (picks Lagrange multipliers λ, penalizing
  violation harder as h gets more unfair):

  ```
  min_h max_λ   error(h) + λ^T (φ(h) - epsilon)
  ```

- Practically reduces to iteratively reweighting training examples and
  retraining the base classifier — so it wraps around any base classifier
  (Decision Tree here) without modifying the dataset.
- Reference implementation: `fairlearn.reductions.ExponentiatedGradient` and
  `fairlearn.reductions.GridSearch` (Python package `fairlearn`).

### Base-paper deliverables
1. Baseline Decision Tree: accuracy + all 3 fairness metrics above.
2. Decision Tree wrapped in `ExponentiatedGradient` with a Demographic Parity
   constraint: same metrics.
3. Same wrapped with an Equalized Odds constraint: same metrics.
4. `GridSearch` sweep producing an accuracy-vs-fairness Pareto frontier plot.

## 5. Ablation study (secondary track — same data/model/metrics, swap only the mitigation algorithm)

All methods below are in-processing (algorithmic) — data is not touched in
any of them. Hold dataset, base classifier, and evaluation metrics fixed;
vary only the mitigation mechanism.

| Method | Paper | Mechanism |
|---|---|---|
| Baseline | — | No mitigation |
| Exponentiated Gradient | Agarwal et al. 2018 (base paper) | Lagrangian game, reweight-and-retrain loop |
| GridSearch | Agarwal et al. 2018 (alt. algorithm, same paper) | Sweep fixed λ values, select resulting Pareto-frontier model |
| Prejudice Remover Regularizer | Kamishima et al. 2012, "Fairness-Aware Classifier with Prejudice Remover Regularizer" | Adds `λ·φ(h)` directly into the loss as a regularization term |
| Adversarial Debiasing | Zhang, Lemoine & Mitchell 2018, "Mitigating Unwanted Biases with Adversarial Learning" | Adversary network tries to predict `a` from h(x); predictor penalized when adversary succeeds |

Optional single reference row (non-algorithmic, for context only — not part
of the "purely algorithmic" claim): Reweighing (Kamiran & Calders 2012),
a pre-processing method, included only to show algorithmic methods aren't
the only lever, if in scope.

### Ablation questions to answer explicitly in the report
- Which method gets closest to zero bias for the smallest accuracy cost?
- Which method is most stable across repeated runs (adversarial training is
  typically higher-variance than convex/Lagrangian approaches)?
- Does the ranking of methods change depending on which fairness metric
  (Demographic Parity vs Equalized Odds) is being optimized/reported?

## 6. Tooling

- `fairlearn` — ExponentiatedGradient, GridSearch, MetricFrame for metric
  reporting/plots.
- `aif360` (IBM) — has Prejudice Remover and Adversarial Debiasing
  implementations if not building them from scratch.
- `scikit-learn` — base Decision Tree classifier, train/test split, encoding.
- `shap` (optional, stretch goal) — before/after feature-importance
  comparison, to visually show reliance on `sex` and its proxies shrinking
  post-mitigation.

## 7. Definition of done

- One results table: rows = {Baseline, Exponentiated Gradient (DP),
  Exponentiated Gradient (EO), GridSearch, Prejudice Remover, Adversarial
  Debiasing}, columns = {Accuracy, Demographic Parity Diff, Equalized Odds
  Diff, Disparate Impact}.
- One Pareto frontier plot (accuracy vs. fairness) from the GridSearch sweep.
- Written comparison answering the three ablation questions in Section 5.

