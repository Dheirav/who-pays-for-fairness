"""Existing remedies for levelling down, so the selection-rate floor is not compared only
to the thing it was built to beat.

**Individual work, beyond the course submission.**

Document 19 proposed adding a floor on the overall selection rate, and documents 21 and 23
showed it works and scales with the damage. Every one of those comparisons is against plain
``ExponentiatedGradient`` -- the method whose behaviour motivated the floor in the first
place. That is the weakest possible baseline, and the first question any reviewer asks is
why not use a method already designed for this.

Two are implemented here, chosen because they answer *different* questions.

Group-wise thresholds (the decoupled classifier)
------------------------------------------------
Dwork, Immorlica, Kalai & Leiserson (2018), *Decoupled Classifiers for Group-Fair and
Efficient Machine Learning*; the demographic-parity case is characterised by
Corbett-Davies, Pierson, Feller, Goel & Huq (2017) and Menon & Williamson (2018), who show
the optimal DP-constrained classifier is a **group-specific threshold on the unconstrained
score**.

That makes it the right upper bound rather than merely another method: if the reduction is
leaving accuracy or favourable decisions on the table, this is what it is leaving them
against. Any gap between the two is the price of the reduction's search, not of the
constraint.

**It requires the protected attribute at prediction time**, and the rest of this project
deliberately does not have it -- ``include_protected_in_features`` is False throughout, so
``ExponentiatedGradient`` must reach parity through proxies. Group-wise thresholding is
therefore not a drop-in alternative; in many jurisdictions it is disparate treatment on its
face. It is carried as a **bound**, and the asymmetry is the point rather than a flaw in
the comparison.

Minimax group fairness
----------------------
Martinez, Bertran & Sapiro (2020), *Minimax Pareto Fairness*; Diana, Gill, Kearns, Kenthapadi
& Roth (2021), *Minimax Group Fairness*. Instead of equalising anything, minimise the
error of the **worst-off group**. This is the established answer to levelling down: it can
never make a group worse off in order to satisfy a parity condition, because no parity
condition is imposed.

It therefore does *not* target demographic parity and will not satisfy it. Reporting it in
a parity table without saying so would be a category error. What it answers is the
question the floor actually raises -- if you want to avoid levelling down, is stating a
selection-rate floor better or worse than abandoning parity for a minimax objective? -- and
the answer has to be read on both axes at once.

The implementation is the standard reweighting scheme rather than either paper's exact
algorithm: fit, find the worst group, shift weight toward it, repeat. Simplified
deliberately and labelled as such; a faithful reimplementation of either paper is a larger
undertaking than this comparison needs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Candidate common selection rates for the decoupled classifier. The grid is over the
# *shared* rate, which is what demographic parity fixes; each group's threshold is then
# whatever quantile of its own score distribution achieves it.
RATE_GRID = np.linspace(0.02, 0.98, 97)

MINIMAX_ROUNDS = 30
MINIMAX_STEP = 0.5


class GroupThresholdClassifier:
    """Per-group thresholds on one shared score, equalising selection rates exactly.

    The decision rule needs the group label, so ``predict`` takes it explicitly rather
    than reading it from the feature matrix -- the feature matrix does not contain it.
    """

    def __init__(self, model, thresholds: dict, rate: float, groups: list) -> None:
        self.model = model
        self.thresholds = thresholds
        self.rate = rate
        self.groups = groups

    def predict(self, X, a) -> np.ndarray:
        scores = self.model.predict_proba(X)[:, 1]
        a = np.asarray(a)
        out = np.zeros(len(scores), dtype=int)
        for group, threshold in self.thresholds.items():
            mask = a == group
            out[mask] = (scores[mask] >= threshold).astype(int)
        return out


def fit_group_thresholds(model, X_train, y_train, a_train) -> GroupThresholdClassifier:
    """Fit the score, then choose the shared selection rate that maximises accuracy.

    Thresholds come from each group's own score quantiles, so both groups end up selected
    at the same rate by construction and the demographic parity difference is zero up to
    ties in the score. The only free parameter is the rate they share.
    """
    model.fit(X_train, y_train)
    scores = model.predict_proba(X_train)[:, 1]
    a = np.asarray(a_train)
    y = np.asarray(y_train)
    groups = list(pd.unique(a))

    best_rate, best_accuracy, best_thresholds = None, -np.inf, None
    for rate in RATE_GRID:
        thresholds, predictions = {}, np.zeros(len(scores), dtype=int)
        for group in groups:
            mask = a == group
            # The threshold that selects exactly `rate` of this group.
            thresholds[group] = float(np.quantile(scores[mask], 1.0 - rate))
            predictions[mask] = (scores[mask] >= thresholds[group]).astype(int)
        accuracy = float(np.mean(predictions == y))
        if accuracy > best_accuracy:
            best_rate, best_accuracy, best_thresholds = rate, accuracy, thresholds

    return GroupThresholdClassifier(model, best_thresholds, float(best_rate), groups)


def fit_minimax(model_factory, X_train, y_train, a_train, *,
                rounds: int = MINIMAX_ROUNDS, step: float = MINIMAX_STEP):
    """Minimise the worst group's error by shifting sample weight toward it.

    Standard reweighting scheme, not either paper's exact algorithm. Each round fits with
    the current per-group weights, measures each group's error, and multiplies the worst
    group's weight up. The returned model is the iterate with the **lowest maximum group
    error**, which is the quantity being minimised -- returning the last iterate instead
    would report wherever the oscillation happened to stop.
    """
    a = np.asarray(a_train)
    y = np.asarray(y_train)
    groups = list(pd.unique(a))
    weights = {group: 1.0 for group in groups}

    best_model, best_worst, history = None, np.inf, []
    for _ in range(rounds):
        sample_weight = np.array([weights[group] for group in a], dtype=float)
        sample_weight *= len(sample_weight) / sample_weight.sum()

        model = model_factory()
        model.fit(X_train, y_train, sample_weight=sample_weight)
        predictions = model.predict(X_train)

        errors = {group: float(np.mean(predictions[a == group] != y[a == group]))
                  for group in groups}
        worst_group = max(errors, key=errors.get)
        worst = errors[worst_group]
        history.append(worst)

        if worst < best_worst:
            best_model, best_worst = model, worst

        weights[worst_group] *= 1.0 + step
        total = sum(weights.values())
        weights = {group: value * len(groups) / total for group, value in weights.items()}

    return best_model, {"worst_group_error": best_worst, "history": history}
