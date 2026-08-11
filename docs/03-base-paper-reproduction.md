# 03 — Base-paper reproduction: Agarwal et al. (2018)

**A Reductions Approach to Fair Classification**, ICML 2018.
Agarwal, Beygelzimer, Dudík, Langford & Wallach.

Deliverables 1–4 of the initiation document. Decision tree base classifier, as
specified. 5 seeds, mean ± std.

## What the paper claims

The paper takes the constrained problem

```
min_h  E[1{h(x) ≠ y}]    subject to    φ(h) ≤ ε
```

and rewrites it as a two-player zero-sum game via Lagrangian relaxation:

```
min_h max_λ   error(h) + λᵀ(φ(h) − ε)
```

A **learner** picks a classifier; a **regulator** picks multipliers λ that penalise
violation harder as the classifier gets less fair. Running the game to equilibrium
reduces, in practice, to *repeatedly reweighting the training examples and refitting
the base classifier*. Three consequences the paper emphasises:

1. **The base classifier is a black box.** Any cost-sensitive learner works; the
   method never inspects or modifies it.
2. **The training data is never modified.** Reweighting changes the objective, not
   the dataset.
3. **The output is a randomized classifier** — a distribution over the models visited
   during the game, not a single model.

`GridSearch` is the paper's alternative: instead of playing the game, sweep a fixed
grid of λ values, fit one model per λ, and keep them all so a frontier can be traced.

## Results

| method | Accuracy | DP diff | EO diff | Disparate impact |
|---|---|---|---|---|
| baseline (tree) | 0.8517 ± 0.0030 | 0.1613 ± 0.0125 | 0.0831 ± 0.0234 | 0.3086 ± 0.0315 |
| ExpGrad (DP), ε=0.01 | 0.8364 ± 0.0018 | **0.0187** ± 0.0069 | 0.2773 ± 0.0171 | **0.8834** ± 0.0423 |
| ExpGrad (EO), ε=0.01 | 0.8471 ± 0.0030 | 0.1125 ± 0.0139 | **0.0355** ± 0.0242 | 0.4573 ± 0.0486 |

## Verdict: the method works, and works well

**Under the demographic parity constraint**, the violation falls from 0.161 to 0.019
— an **88% reduction** — for **1.5 accuracy points** (0.8517 → 0.8364). Disparate
impact goes from 0.31 to 0.88, i.e. from failing the four-fifths rule by a factor of
nearly three to comfortably passing it.

**Under the equalized odds constraint**, EO difference falls from 0.083 to 0.036
(57% reduction) for **0.5 accuracy points**. This is close to free.

**Each constraint improves the metric it was given and only that one.** ExpGrad-DP
leaves EO *worse* than the baseline (0.277 vs 0.083); ExpGrad-EO leaves DP largely
intact (0.113 vs 0.161). The algorithm is doing precisely what it was asked and
nothing more — which is correct behaviour, and is the seed of the finding in
document 04.

**The black-box claim holds.** The identical wrapper was applied to a decision tree
here and to logistic regression in document 04, with no modification to either the
wrapper or the classifiers, and it worked in both cases. This is the paper's most
practically valuable claim and it survived contact with the data.

## The Pareto frontier (deliverable 4)

`results/pareto_demographic_parity.png` and `pareto_equalized_odds.png`, from a
15-point GridSearch sweep with every fitted model evaluated, not just the one
fairlearn's selection rule prefers.

The plots report the **full sweep alongside the frontier**, which is deliberate: a
grid producing many dominated points is evidence that the trade-off is not as smooth
as a frontier-only plot implies. That turns out to matter — see the stability finding
in document 04, where GridSearch is the least stable method in the study.

## Where the reproduction is honest about its limits

* **Absolute numbers are not comparable to the paper's.** Different preprocessing
  (listwise deletion, two dropped columns), a different split, and a depth-8 tree
  rather than the paper's setup. What is being checked is whether the *claims* hold
  in shape and magnitude — they do — not whether a specific decimal matches.
* **ε = 0.01 is a choice, not a result.** It is the constraint slack, not a
  convergence tolerance. Shrinking it demands a fairer model and costs more accuracy;
  it is the knob that traces the trade-off curve, and one value of it is one point.
* **`predict` is stochastic.** `ExponentiatedGradient.predict` samples a classifier
  from the learned distribution on every call, so two identical applicants can receive
  different decisions. A `random_state` is threaded through for reproducibility, but
  **fixing the seed hides this behaviour rather than removing it.** The paper is
  explicit that the output is randomized; what it does not quantify is how much
  individual-level churn that randomness causes. Document 05 measures it, and the
  answer is not small.

## Summary

| Paper's claim | Held? | Evidence |
|---|---|---|
| Drives violation toward ε for modest accuracy cost | **Yes** | DP 0.161 → 0.019 for 1.5 acc points |
| Works with any base classifier as a black box | **Yes** | Same wrapper on a tree and on logistic regression |
| Training data never modified | **Yes** | Reweighting is internal to the objective |
| Output is a randomized classifier | **Yes** | And it has a measurable cost — see doc 05 |
| GridSearch traces a usable frontier | **Yes, with a caveat** | It does, but it is the least stable method here — doc 04 |
