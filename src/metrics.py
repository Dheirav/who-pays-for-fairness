"""Fairness and performance metrics.

Implemented directly from the definitions rather than called out of a library, so
the report can state exactly what was computed. ``crosscheck_against_fairlearn``
verifies these against ``fairlearn``'s implementations; the test exists because a
group-orientation slip (privileged/unprivileged swapped) produces plausible-looking
numbers that are silently wrong.

Definitions, for protected attribute ``a``, prediction ``yhat`` and label ``y``:

* Demographic Parity Difference -- ``|P(yhat=1|priv) - P(yhat=1|unpriv)|``
* Equalized Odds Difference     -- ``max(|TPR gap|, |FPR gap|)``
* Disparate Impact              -- ``P(yhat=1|unpriv) / P(yhat=1|priv)``

Note the different targets: the two differences are fair at **0**, disparate impact
is fair at **1**. They are not interchangeable and should not be averaged.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rates(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Selection rate, TPR, FPR and accuracy for one group.

    Returns NaN for a rate whose denominator is empty (e.g. TPR when a group has no
    positive labels) rather than 0, so that an undefined rate cannot masquerade as a
    perfectly fair one.
    """
    positives = y_true == 1
    negatives = ~positives
    return {
        "n": int(y_true.size),
        "selection_rate": float(np.mean(y_pred)) if y_pred.size else np.nan,
        "tpr": float(np.mean(y_pred[positives])) if positives.any() else np.nan,
        "fpr": float(np.mean(y_pred[negatives])) if negatives.any() else np.nan,
        "accuracy": float(np.mean(y_pred == y_true)) if y_true.size else np.nan,
    }


def group_breakdown(
    y_true, y_pred, sensitive, *, privileged, unprivileged
) -> pd.DataFrame:
    """Per-group rate table.

    This is the raw material for both the fairness metrics and the "who pays for the
    constraint" analysis -- a mitigation that equalises selection rates by lowering
    the privileged group's TPR looks identical, at the aggregate metric, to one that
    raises the unprivileged group's. Only this table distinguishes them.
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    sensitive = np.asarray(sensitive)

    rows = []
    for label, value in (("privileged", privileged), ("unprivileged", unprivileged)):
        mask = sensitive == value
        rows.append({"group": label, "value": value, **_rates(y_true[mask], y_pred[mask])})
    return pd.DataFrame(rows).set_index("group")


def demographic_parity_difference(
    y_pred, sensitive, *, privileged, unprivileged
) -> float:
    y_pred = np.asarray(y_pred).astype(int)
    sensitive = np.asarray(sensitive)
    return abs(
        float(np.mean(y_pred[sensitive == privileged]))
        - float(np.mean(y_pred[sensitive == unprivileged]))
    )


def equalized_odds_difference(
    y_true, y_pred, sensitive, *, privileged, unprivileged
) -> float:
    """max(|TPR gap|, |FPR gap|), or NaN if either component is undefined.

    The NaN check is explicit because Python's ``max`` handles NaN by argument
    *order*: ``max(nan, 0.5)`` is nan but ``max(0.5, nan)`` is 0.5, since every
    comparison against NaN is False. Written as a bare ``max`` this silently reported
    a TPR-only gap as the full equalized-odds difference whenever a group had no
    negative labels — an undefined quantity masquerading as a defined one, which is
    exactly what ``_rates`` returning NaN rather than 0 exists to prevent. The
    guarantee has to hold at this level too, not only one function down.
    """
    table = group_breakdown(
        y_true, y_pred, sensitive, privileged=privileged, unprivileged=unprivileged
    )
    tpr_gap = abs(table.loc["privileged", "tpr"] - table.loc["unprivileged", "tpr"])
    fpr_gap = abs(table.loc["privileged", "fpr"] - table.loc["unprivileged", "fpr"])
    if np.isnan(tpr_gap) or np.isnan(fpr_gap):
        return float("nan")
    return float(max(tpr_gap, fpr_gap))


def disparate_impact(y_pred, sensitive, *, privileged, unprivileged) -> float:
    """Ratio form. Fair at 1.0; the "80% rule" flags values below 0.8.

    Returns NaN when the privileged selection rate is 0, which is undefined rather
    than infinitely unfair.
    """
    y_pred = np.asarray(y_pred).astype(int)
    sensitive = np.asarray(sensitive)
    priv_rate = float(np.mean(y_pred[sensitive == privileged]))
    unpriv_rate = float(np.mean(y_pred[sensitive == unprivileged]))
    if priv_rate == 0:
        return float("nan")
    return unpriv_rate / priv_rate


def evaluate(
    y_true, y_pred, sensitive, *, privileged, unprivileged, label: str = ""
) -> dict[str, float | str]:
    """One row of the results table: accuracy plus all three fairness metrics."""
    y_true_arr = np.asarray(y_true).astype(int)
    y_pred_arr = np.asarray(y_pred).astype(int)
    kw = {"privileged": privileged, "unprivileged": unprivileged}
    return {
        "method": label,
        "accuracy": float(np.mean(y_pred_arr == y_true_arr)),
        "demographic_parity_diff": demographic_parity_difference(y_pred_arr, sensitive, **kw),
        "equalized_odds_diff": equalized_odds_difference(y_true_arr, y_pred_arr, sensitive, **kw),
        "disparate_impact": disparate_impact(y_pred_arr, sensitive, **kw),
    }


def crosscheck_against_fairlearn(
    y_true, y_pred, sensitive, *, privileged, unprivileged, tol: float = 1e-9
) -> None:
    """Assert this module agrees with ``fairlearn``. Raises AssertionError on drift."""
    from fairlearn.metrics import (
        demographic_parity_difference as fl_dp,
        equalized_odds_difference as fl_eo,
    )

    kw = {"privileged": privileged, "unprivileged": unprivileged}
    mine_dp = demographic_parity_difference(y_pred, sensitive, **kw)
    mine_eo = equalized_odds_difference(y_true, y_pred, sensitive, **kw)
    theirs_dp = fl_dp(y_true, y_pred, sensitive_features=sensitive)
    theirs_eo = fl_eo(y_true, y_pred, sensitive_features=sensitive)

    assert abs(mine_dp - theirs_dp) < tol, f"DP mismatch: {mine_dp} vs {theirs_dp}"
    assert abs(mine_eo - theirs_eo) < tol, f"EO mismatch: {mine_eo} vs {theirs_eo}"
