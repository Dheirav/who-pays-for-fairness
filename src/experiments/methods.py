"""Shared method registry: one place where each ablation row is defined.

Every experiment that compares mitigations needs the same six models fitted the same
way on the same split. Defining them twice -- once in the ablation table, once in the
who-pays analysis -- is how the two end up silently disagreeing about, say, which base
classifier ``expgrad_dp`` used. They are defined here once and imported.

All six use **logistic regression** as the base hypothesis class, including the
reductions rows. Prejudice Remover and Adversarial Debiasing cannot wrap a decision
tree: one adds a term to a likelihood, the other needs gradients to flow from an
adversary into the predictor. Reporting a tree for some rows and a linear model for
others would vary the hypothesis class *and* the mitigation at once, so the table
would not isolate what it claims to.

:func:`fit` returns a *predict function* rather than predictions, because the
randomized classifiers can be sampled more than once from a single fit -- which is how
the arbitrariness floor in :mod:`src.experiments.run_who_pays` is measured without
paying for a second training run.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np

from ..inprocessing import AdversarialDebiasing, PrejudiceRemover
from ..mitigation import fit_exponentiated_gradient, fit_grid_search
from ..models import build
from ..preprocessing import SplitData

BASE_MODEL = "logistic_regression"

METHOD_ORDER = [
    "baseline",
    "expgrad_dp",
    "expgrad_eo",
    "gridsearch_dp",
    "prejudice_remover",
    "adversarial_debiasing",
]

# Methods whose predictions are not a deterministic function of the fitted model.
# ExponentiatedGradient returns a distribution over classifiers and samples from it at
# predict time, so two calls on identical inputs can disagree.
STOCHASTIC_AT_PREDICT = {"expgrad_dp", "expgrad_eo"}

PredictFn = Callable[[int], np.ndarray]


@dataclass(frozen=True)
class MethodParams:
    """Hyperparameters shared across experiments, so rows stay comparable."""

    eps: float = 0.01       # ExpGrad constraint slack
    eta: float = 5.0        # Prejudice Remover penalty strength
    alpha: float = 1.0      # adversary weight
    epochs: int = 30        # adversarial training epochs
    grid_size: int = 15     # GridSearch lambda grid


def fit_model(name: str, split: SplitData, seed: int, params: MethodParams):
    """Fit one method and return the fitted estimator itself.

    Exposed separately from :func:`fit` because the SHAP analysis needs the model's
    parameters, not just its decisions -- five of the six are linear underneath and
    can be explained exactly instead of by sampling.
    """
    if name == "baseline":
        model = build(BASE_MODEL, random_state=seed)
        return model.fit(split.X_train, split.y_train)

    if name in ("expgrad_dp", "expgrad_eo"):
        return fit_exponentiated_gradient(
            build(BASE_MODEL, random_state=seed),
            split.X_train, split.y_train, split.a_train,
            constraint="demographic_parity" if name.endswith("_dp") else "equalized_odds",
            eps=params.eps,
        )

    if name == "gridsearch_dp":
        return fit_grid_search(
            build(BASE_MODEL, random_state=seed),
            split.X_train, split.y_train, split.a_train,
            constraint="demographic_parity", grid_size=params.grid_size,
        )

    if name == "prejudice_remover":
        return PrejudiceRemover(eta=params.eta, random_state=seed).fit(
            split.X_train, split.y_train, split.a_train
        )

    if name == "adversarial_debiasing":
        return AdversarialDebiasing(
            adversary_weight=params.alpha, epochs=params.epochs, random_state=seed
        ).fit(split.X_train, split.y_train, split.a_train)

    raise KeyError(f"unknown method '{name}'; available: {METHOD_ORDER}")


def predict_fn(name: str, model, split: SplitData, seed: int) -> PredictFn:
    """Wrap a fitted model as ``predict(predict_seed) -> test predictions``.

    ``predict_seed`` is ignored by every deterministic method. For the two in
    :data:`STOCHASTIC_AT_PREDICT` it selects which classifier is drawn from the
    learned distribution, so calling the returned function twice with different values
    measures the method's own arbitrariness rather than any effect of the constraint.
    """
    if name in STOCHASTIC_AT_PREDICT:
        return lambda ps=seed: model.predict(split.X_test, random_state=ps)
    if name == "prejudice_remover":
        # Requires the protected attribute at inference -- see the module docstring.
        return lambda _=seed: model.predict(split.X_test, split.a_test)
    return lambda _=seed: model.predict(split.X_test)


def fit(name: str, split: SplitData, seed: int, params: MethodParams) -> PredictFn:
    """Fit one method and return its predict function."""
    return predict_fn(name, fit_model(name, split, seed, params), split, seed)


def fit_all(
    split: SplitData,
    seed: int,
    params: MethodParams,
    *,
    methods: list[str] | None = None,
    verbose: bool = True,
    return_models: bool = False,
) -> tuple[dict[str, PredictFn], dict[str, float]]:
    """Fit every method on one split. Returns predict functions and fit seconds.

    With ``return_models`` the fitted estimators are returned as a third element, for
    callers that need to look inside them.
    """
    predictors, seconds, models = {}, {}, {}
    for name in methods or METHOD_ORDER:
        start = time.perf_counter()
        models[name] = fit_model(name, split, seed, params)
        predictors[name] = predict_fn(name, models[name], split, seed)
        seconds[name] = time.perf_counter() - start
        if verbose:
            print(f"    {name:<24} {seconds[name]:6.1f}s", flush=True)
    if return_models:
        return predictors, seconds, models
    return predictors, seconds
