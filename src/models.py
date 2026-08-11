"""Base classifiers held fixed across mitigation methods.

Every estimator here supports ``sample_weight`` in ``fit``, which is a hard
requirement: the base paper's reduction mitigates bias precisely by reweighting
examples and refitting, so an estimator that ignores weights would silently produce
an unmitigated model rather than an error.

**Design decision -- why two base classifiers.** The initiation document specifies a
Decision Tree, and the base-paper track uses it. But two of the planned ablation
methods cannot wrap one: Prejudice Remover adds a regularisation term to a
likelihood, and Adversarial Debiasing needs gradients to flow from an adversary into
the predictor. Both are inherently linear/differentiable-model methods. Reporting a
Decision Tree for some rows and a logistic model for others would vary two things at
once -- the mitigation *and* the hypothesis class -- so the ablation table would not
isolate what it claims to. Logistic regression is therefore carried alongside as the
comparable-across-all-methods base, and the choice is stated in the results rather
than hidden.
"""

from __future__ import annotations

from typing import Callable

from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

# max_depth is set rather than left unbounded: a fully grown tree on Adult reaches
# ~100% training accuracy and generalises poorly, which would confound the accuracy
# cost of mitigation with the accuracy cost of overfitting.
DEFAULT_TREE_DEPTH = 8


def decision_tree(random_state: int = 42, max_depth: int = DEFAULT_TREE_DEPTH):
    return DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)


def logistic_regression(random_state: int = 42, max_iter: int = 2000):
    return LogisticRegression(max_iter=max_iter, random_state=random_state)


MODELS: dict[str, Callable[..., BaseEstimator]] = {
    "decision_tree": decision_tree,
    "logistic_regression": logistic_regression,
}


def build(name: str, random_state: int = 42) -> BaseEstimator:
    if name not in MODELS:
        raise KeyError(f"unknown model '{name}'; available: {sorted(MODELS)}")
    return MODELS[name](random_state=random_state)
