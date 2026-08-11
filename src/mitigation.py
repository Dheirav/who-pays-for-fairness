"""In-processing mitigation via the reductions approach (Agarwal et al., 2018).

Implements the base paper's two algorithms through ``fairlearn.reductions``:

* :func:`fit_exponentiated_gradient` -- the main algorithm. Solves
  ``min_h max_λ error(h) + λᵀ(φ(h) - ε)`` as a two-player zero-sum game. In practice
  it repeatedly reweights the training examples according to the current λ and refits
  the base classifier, returning a *randomized* classifier: a distribution over the
  models it visited.
* :func:`fit_grid_search` -- the alternative from the same paper. Instead of playing
  the game, it sweeps a fixed grid of λ values, fits one model per λ, and hands back
  the whole set so an accuracy-vs-fairness frontier can be traced.

Neither touches the training data. Reweighting changes how much each example counts
in the *objective*; no row, label, or feature is altered, and no row is duplicated or
dropped. That distinction is what makes this an in-processing method.

Two consequences of the reduction worth carrying into the writeup:

1. ``ExponentiatedGradient.predict`` is **stochastic**. It samples a classifier from
   the learned distribution on each call, so identical feature vectors can receive
   different decisions. A ``random_state`` is threaded through everywhere here for
   reproducibility, but fixing the seed hides the behaviour rather than removing it.
2. ``eps`` is the constraint slack ε, not a convergence tolerance. Shrinking it
   demands a fairer model and generally costs accuracy -- it is the knob that traces
   the trade-off curve.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from fairlearn.reductions import (
    DemographicParity,
    EqualizedOdds,
    ExponentiatedGradient,
    GridSearch,
)
from sklearn.base import BaseEstimator

# Constraint name -> factory. Both are "difference" forms, matching the metrics in
# src.metrics: fair at 0, and bounded by eps during optimisation.
CONSTRAINTS = {
    "demographic_parity": DemographicParity,
    "equalized_odds": EqualizedOdds,
}


def build_constraint(name: str, *, difference_bound: float = 0.01):
    """Build a fairness moment with its violation bound set explicitly.

    **The bound must be set here, not on the reduction.** ``DemographicParity()``
    constructed with no arguments silently pins its bound at fairlearn's
    ``_DEFAULT_DIFFERENCE_BOUND`` of 0.01, and nothing passed to
    ``ExponentiatedGradient`` changes it -- see :func:`fit_exponentiated_gradient` for
    what that parameter actually does. Leaving this implicit produced a constraint
    sweep in which every value of "epsilon" returned the same model, because the real
    constraint never moved.
    """
    if name not in CONSTRAINTS:
        raise KeyError(f"unknown constraint '{name}'; available: {sorted(CONSTRAINTS)}")
    return CONSTRAINTS[name](difference_bound=difference_bound)


def fit_exponentiated_gradient(
    estimator: BaseEstimator,
    X_train: np.ndarray,
    y_train: np.ndarray,
    a_train: np.ndarray,
    *,
    constraint: str,
    eps: float = 0.01,
    max_iter: int = 50,
) -> ExponentiatedGradient:
    """Fit the reduction with ``eps`` as the fairness slack ε.

    ``eps`` is passed to **both** the moment and the reduction, and they are not the
    same knob:

    * on the moment it is ``difference_bound`` -- the actual constraint, φ(h) ≤ ε;
    * on ``ExponentiatedGradient`` it only sets ``B = 1/eps``, the bound on the
      Lagrange multipliers the regulator may play.

    Passing it to the reduction alone leaves the constraint pinned at fairlearn's
    default of 0.01 while appearing to have been set, which is the failure this
    signature exists to prevent.
    """
    model = ExponentiatedGradient(
        estimator=estimator,
        constraints=build_constraint(constraint, difference_bound=eps),
        eps=eps,
        max_iter=max_iter,
    )
    model.fit(X_train, y_train, sensitive_features=a_train)
    return model


def fit_grid_search(
    estimator: BaseEstimator,
    X_train: np.ndarray,
    y_train: np.ndarray,
    a_train: np.ndarray,
    *,
    constraint: str,
    grid_size: int = 15,
    difference_bound: float = 0.01,
) -> GridSearch:
    """Fit one model per λ on a fixed grid.

    Unlike the exponentiated-gradient run, every fitted model is retained on
    ``.predictors_``; the frontier is traced by evaluating all of them, not just the
    one fairlearn's selection rule prefers.

    ``difference_bound`` is the moment's constraint, carried explicitly for the same
    reason as in :func:`fit_exponentiated_gradient`.
    """
    model = GridSearch(
        estimator=estimator,
        constraints=build_constraint(constraint, difference_bound=difference_bound),
        grid_size=grid_size,
    )
    model.fit(X_train, y_train, sensitive_features=a_train)
    return model


@dataclass(frozen=True)
class ParetoPoint:
    """One (fairness violation, accuracy) pair from a grid sweep."""

    index: int
    accuracy: float
    violation: float
    on_frontier: bool


def pareto_frontier(accuracies, violations) -> list[ParetoPoint]:
    """Mark the non-dominated points.

    A model is dominated when another achieves both lower fairness violation *and*
    higher accuracy; the frontier is what remains. Reporting the full sweep alongside
    the frontier matters -- a grid that produces many dominated points is evidence the
    trade-off is not as smooth as a frontier-only plot implies.
    """
    accuracies = np.asarray(accuracies, dtype=float)
    violations = np.asarray(violations, dtype=float)

    points = []
    for i, (acc, vio) in enumerate(zip(accuracies, violations)):
        dominated = np.any(
            (violations <= vio) & (accuracies >= acc)
            & ((violations < vio) | (accuracies > acc))
        )
        points.append(
            ParetoPoint(index=i, accuracy=float(acc), violation=float(vio), on_frontier=not dominated)
        )
    return points
