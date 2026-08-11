# 04 — Ablation: six mitigations, one table

Hold data, base classifier, and metrics fixed; vary only the mitigation. All six rows
use **logistic regression** (see document 01 for why). 5 seeds, mean ± std.

Two of the six are implemented from their papers rather than from a library —
see [Implementation notes](#implementation-notes) at the end.

## The table

| Method | Accuracy | DP diff | EO diff | Disparate impact |
|---|---|---|---|---|
| baseline | **0.8469** ± 0.0033 | 0.1861 ± 0.0083 | 0.0949 ± 0.0295 | 0.2996 ± 0.0296 |
| expgrad_dp | 0.8282 ± 0.0023 | 0.0178 ± 0.0091 | 0.2802 ± 0.0190 | 0.8951 ± 0.0516 |
| expgrad_eo | 0.8361 ± 0.0012 | 0.1072 ± 0.0101 | **0.0320** ± 0.0144 | 0.5214 ± 0.0389 |
| gridsearch_dp | 0.8265 ± 0.0070 | **0.0150** ± 0.0190 | 0.3040 ± 0.0460 | **0.9859** ± 0.1377 |
| prejudice_remover | 0.8365 ± 0.0020 | 0.0645 ± 0.0085 | 0.1884 ± 0.0247 | 0.6860 ± 0.0372 |
| adversarial_debiasing | 0.8260 ± 0.0011 | 0.0202 ± 0.0093 | 0.2504 ± 0.0148 | 0.8894 ± 0.0498 |

## Question 1 — closest to zero bias for the smallest accuracy cost?

The answer depends on whether you want the *lowest* violation or the *best exchange
rate*, and those give different winners.

**Lowest absolute DP violation:** GridSearch-DP (0.0150), then ExpGrad-DP (0.0178),
then Adversarial Debiasing (0.0202). All three effectively solve demographic parity.

**Best exchange rate** — parity points bought per accuracy point spent:

| method | DP reduction | accuracy cost | points per point |
|---|---|---|---|
| **prejudice_remover** | 0.1216 | 0.0104 | **11.7** |
| expgrad_dp | 0.1683 | 0.0187 | 9.0 |
| gridsearch_dp | 0.1711 | 0.0204 | 8.4 |
| adversarial_debiasing | 0.1659 | 0.0209 | 7.9 |

**Prejudice Remover is the most efficient method and does not win on either headline
number.** It buys 11.7 parity points per accuracy point, ~30% better than ExpGrad-DP,
but stops at DP = 0.065 rather than pushing to 0.015. That is a property of η being a
penalty weight rather than a constraint: it trades against log-likelihood
continuously, with no target it is obliged to hit. If the requirement is "below the
four-fifths rule", it does not get you there. If the requirement is "as much fairness
as possible per unit of accuracy", it is the best method in the table.

**A caveat that belongs with its win.** Prejudice Remover parameterises one weight
vector *per protected group*, so it needs `sex` at **prediction** time. Two applicants
identical on every feature but differing in sex are scored by different weight
vectors. That is disparate treatment in the legal sense, even though the intent is to
reduce disparate impact. Its `predict()` signature requires `a` so this cannot be
overlooked. It is not comparable to the ExpGrad rows on this axis, and its efficiency
win should be quoted with the caveat attached.

## Question 2 — which method is most stable? (The initiation document's prediction was wrong.)

The document predicts "adversarial training is typically higher-variance than
convex/Lagrangian approaches." The data says the opposite:

| method | accuracy std | DP std | DI std |
|---|---|---|---|
| **adversarial_debiasing** | **0.0011** | 0.0093 | 0.0498 |
| expgrad_eo | 0.0012 | 0.0101 | 0.0389 |
| prejudice_remover | 0.0020 | 0.0085 | 0.0372 |
| expgrad_dp | 0.0023 | 0.0091 | 0.0516 |
| **gridsearch_dp** | **0.0070** | **0.0190** | **0.1377** |

**Adversarial Debiasing is the *most* stable method in the study. GridSearch — a
deterministic sweep with no adversary, no minibatching, and no randomness in the
procedure — is the least, by 6× on accuracy and 3× on disparate impact.**

Why the intuition fails: the instability being measured is across *seeds*, and a seed
changes the train/test split. GridSearch fits one model per λ and then **selects**
one; that selection is a discrete argmax over a coarse 15-point grid, and a small
change in the data can flip which grid point wins, moving the answer discontinuously.
Adversarial Debiasing has no such selection step — it optimises continuously and lands
in the same place. The variance came from **model selection over a coarse grid**, not
from stochastic training.

This connects back to document 03: the dominated points visible in the Pareto sweep
are the same phenomenon. A grid that produces many dominated points is a grid whose
argmax is fragile.

## Question 3 — does the ranking change with the metric? Yes, catastrophically.

| method | rank by DP | rank by EO |
|---|---|---|
| gridsearch_dp | **1** | **6** |
| expgrad_dp | 2 | 5 |
| adversarial_debiasing | 3 | 4 |
| prejudice_remover | 4 | 3 |
| expgrad_eo | 5 | **1** |
| baseline | **6** | **2** |

The ranking does not merely shift, it **inverts**. The best DP method is the worst EO
method. And the headline:

> **Four of the five mitigations are worse than doing nothing on equalized odds. The
> unmitigated baseline ranks 2nd of 6.**

An engineer who deployed GridSearch-DP because it scored best on the fairness metric
they were monitoring would have taken equalized odds from 0.095 to 0.304 — **3.2×
worse than no mitigation at all** — while their dashboard showed a green light.

**This is not a defect in any of these methods.** It is the impossibility result
(Kleinberg et al. 2016; Chouldechova 2017) appearing in practice: when base rates
differ across groups — 31.2% vs 11.4% here — demographic parity and equalized odds
cannot both hold. Forcing equal selection rates on groups with genuinely different
label rates necessarily equalises across people who differ in outcome, which is
exactly what wrecks TPR/FPR parity.

The practical lesson is that **"we made the model fair" is not a well-formed claim.**
"We reduced demographic parity difference to 0.015, at the cost of tripling the
equalized odds difference" is.

## Relation to the base paper

* **Confirms** the reduction works on a second base classifier (logistic regression,
  not just the tree in document 03) — the black-box claim again.
* **Confirms** GridSearch and ExpGrad reach comparable fairness on the metric they
  target.
* **Extends** the paper with methods it does not consider (Kamishima's regulariser,
  Zhang et al.'s adversary) under identical conditions. The paper compares against
  Zafar et al.; this table adds two other families.
* **Adds a caution the paper does not raise:** GridSearch's frontier is attractive to
  present but its *selection* is unstable across resamples. The paper presents
  GridSearch as the practical alternative for binary protected attributes; this
  result suggests reporting its variance, not just its frontier.

## Implementation notes

Prejudice Remover and Adversarial Debiasing were implemented from their papers in
PyTorch (~90 and ~120 lines) rather than taken from `aif360`. The reasons were
concrete: aif360's `PrejudiceRemover` shells out to Kamishima's original script
through temporary files, and its `AdversarialDebiasing` requires a
`tensorflow.compat.v1` dependency chain. Neither is a good foundation, and neither
makes the objective visible in the source.

The cost of implementing from scratch is that the implementations could be wrong, so
they are tested against degenerate cases in `tests/test_inprocessing.py` (4/4
passing):

* Prejudice Remover with **η = 0** removes the penalty and must reduce to per-group
  logistic regression — it reproduces it to **99.88%** prediction agreement.
* Raising η and raising the adversary weight α must each move fairness monotonically
  in the right direction. This is the check that catches a **sign error** — the
  failure mode where a "mitigation" quietly increases disparity while the metrics
  still look plausible.
* Adversarial training must not collapse to a constant predictor. Predicting all-zero
  trivially defeats the adversary and scores ~76% on Adult's class imbalance while
  being useless, so the positive-prediction rate is checked, not just accuracy.
