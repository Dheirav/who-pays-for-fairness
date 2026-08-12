"""A demographic-parity constraint that is not allowed to shrink the pie.

Document 05's third finding is that every mitigation in the ablation closed the gap
partly by *withdrawing* favourable decisions -- the total number of positive predictions
fell by 7.9% to 22.1%, and not one method closed the gap primarily by extending
favourable decisions to the disadvantaged group. That document ends:

    "If you want the gap closed by levelling up, **that has to be part of the
    objective** -- it will not happen by accident."

That is a claim about what is *expressible*, and it was never tested. This module tests
it, and the honest framing matters: **this is not a new method.** Agarwal et al. (2018)
define constraints as linear in the classifier's conditional moments, and a floor on the
overall selection rate is exactly that -- a linear constraint on a moment whose
conditioning event is the whole population. So it sits inside the base paper's framework
rather than beyond it. What is new is the question, not the machinery.

The construction
----------------
``SelectionRateFloor`` adds one constraint, ``P(h(x) = 1) >= target``, written in
fairlearn's ``gamma <= bound`` form as ``-P(h = 1) <= -target``.

``Composite`` stacks it with ``DemographicParity`` so the reduction sees both at once and
plays the same game against their combined multiplier vector. Two outcomes are worth
having:

* it works -- demographic parity is satisfied at the same epsilon without the pie
  shrinking, at some accuracy cost, and the levelling-down share falls; or
* it is **infeasible** -- no classifier satisfies both at once, which is a sharper and
  more interesting result than the complaint that motivated it, because it would mean
  levelling down is not an implementation choice but a consequence of the constraint.

Both classes subclass ``ClassificationMoment``, not the bare ``Moment``. That is not
cosmetic. ``Lagrangian._call_oracle`` branches on it: a ``ClassificationMoment`` gets
``redY = 1 * (signed_weights > 0)``, so the oracle is free to flip labels toward
satisfying the constraint, while anything else is refit against the original labels with
reweighting only. Subclassing ``Moment`` produced a model that fit happily, reported a
converged gap of 0.0, and left demographic parity untouched at 0.1844 against a baseline
of 0.1867.

On the signed-weights convention
--------------------------------
``ExponentiatedGradient`` calls ``signed_weights`` and turns the result into a
cost-sensitive problem via ``redY = 1 * (weights > 0)`` and ``redW = |weights|``, so a
positive weight is the *benefit* of predicting 1, unnormalised by the sample count --
``ErrorRate`` returns ``fn_cost`` for a positive example, not ``fn_cost / n``. For a
constraint whose gamma is ``-mean(h)``, the benefit of predicting 1 is the multiplier
itself, uniformly across samples.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from fairlearn.reductions import DemographicParity, ErrorRate
from fairlearn.reductions._moments.moment import ClassificationMoment

FLOOR = "selection_rate_floor"


def _as_series(y) -> pd.Series:
    return y if isinstance(y, pd.Series) else pd.Series(np.asarray(y).ravel())


class SelectionRateFloor(ClassificationMoment):
    """``P(h(x) = 1) >= target``, as one linear constraint on a conditional moment."""

    short_name = "SelectionRateFloor"

    def __init__(self, target: float):
        super().__init__()
        self.target = float(target)

    def load_data(self, X, y, *, sensitive_features=None, control_features=None):
        # Coerced to a Series because fairlearn 0.14 calls `.abs()` on whatever
        # `_y_as_series` returns and that property hands back its input unchanged, so an
        # ndarray reaching here fails inside the reduction rather than here.
        super().load_data(X, _as_series(y))
        self._index = pd.Index([FLOOR])
        return self

    @property
    def index(self):
        return self._index

    def default_objective(self):
        return ErrorRate()

    def gamma(self, predictor):
        rate = float(np.mean(np.asarray(predictor(self.X)).astype(float)))
        # Negated so the "<= bound" form expresses a floor rather than a ceiling.
        return pd.Series([-rate], index=self._index)

    def bound(self):
        return pd.Series([-self.target], index=self._index)

    def project_lambda(self, lambda_vec):
        """One-sided constraint, so the multiplier is clipped at zero."""
        return lambda_vec.clip(lower=0.0)

    def signed_weights(self, lambda_vec):
        weight = float(lambda_vec[FLOOR]) if FLOOR in lambda_vec.index else 0.0
        # `self.tags` is what the sibling moments index their weights by, so using it
        # keeps the two Series alignable when Composite adds them. `_y_as_series` is a
        # bare ndarray in fairlearn 0.14 despite the name, and has no index at all.
        return pd.Series(weight, index=self.tags.index)


class Composite(ClassificationMoment):
    """Several moments enforced together, with their indices kept distinct.

    The reduction plays one game against the stacked multiplier vector, which is the
    point: constraining demographic parity and then separately patching the total
    afterwards would be two sequential fixes, and the question is what happens when the
    learner has to satisfy both at once.
    """

    short_name = "Composite"

    def __init__(self, *moments: ClassificationMoment):
        super().__init__()
        self.moments = moments

    def load_data(self, X, y, *, sensitive_features=None, control_features=None):
        y = _as_series(y)
        super().load_data(X, y)
        for moment in self.moments:
            if isinstance(moment, SelectionRateFloor):
                moment.load_data(X, y)
            else:
                moment.load_data(X, y, sensitive_features=sensitive_features)
        # Prefixed so two moments cannot collide on a shared label, and so a multiplier
        # can always be traced back to the constraint that produced it.
        self._index = pd.Index(
            [f"{i}:{key}" for i, moment in enumerate(self.moments) for key in moment.index]
        )
        return self

    @property
    def index(self):
        return self._index

    def default_objective(self):
        return ErrorRate()

    def _slice(self, vector: pd.Series, position: int, moment) -> pd.Series:
        keys = [f"{position}:{key}" for key in moment.index]
        part = vector.reindex(keys).fillna(0.0)
        part.index = moment.index
        return part

    def _stack(self, parts: list[pd.Series]) -> pd.Series:
        """Recombine per-moment vectors, aligning by label rather than by position.

        Each part is reindexed onto its own moment's index first. Skipping that is a
        real bug and not a defensive nicety: ``UtilityParity.project_lambda`` rebuilds
        its result with ``pd.concat(..., keys=["+", "-"])``, which need not preserve the
        order of ``moment.index``, so a positional zip can silently attach a multiplier
        to the wrong constraint. That is what made demographic parity stop binding here
        -- it was not that the constraint was ignored, it was that its multiplier was
        being delivered to the wrong row.
        """
        pieces = []
        for position, part in enumerate(parts):
            moment_index = self.moments[position].index
            aligned = part.reindex(moment_index)
            pieces.append(pd.Series(
                aligned.to_numpy(),
                index=[f"{position}:{key}" for key in moment_index],
            ))
        return pd.concat(pieces).reindex(self._index)

    def gamma(self, predictor):
        return self._stack([m.gamma(predictor) for m in self.moments])

    def bound(self):
        return self._stack([m.bound() for m in self.moments])

    def project_lambda(self, lambda_vec):
        return self._stack([
            m.project_lambda(self._slice(lambda_vec, i, m))
            for i, m in enumerate(self.moments)
        ])

    def signed_weights(self, lambda_vec):
        total = None
        for position, moment in enumerate(self.moments):
            part = moment.signed_weights(self._slice(lambda_vec, position, moment))
            total = part if total is None else total.add(part, fill_value=0.0)
        return total


def demographic_parity_without_shrinking(target_rate: float, *, eps: float) -> Composite:
    """Demographic parity at ``eps``, plus a floor on the overall selection rate."""
    return Composite(DemographicParity(difference_bound=eps),
                     SelectionRateFloor(target_rate))
