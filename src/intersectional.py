"""Intersectional fairness: measuring subgroups the single-attribute view averages away.

Every method in the ablation table is constrained on ``sex`` alone, and every metric in
:mod:`src.metrics` compares exactly two groups. That is the standard setup, and it has
a known blind spot: a model can satisfy a constraint on sex, and separately satisfy one
on race, while being badly unfair to a subgroup defined by both. Kearns et al. (2018)
call this *fairness gerrymandering* -- the marginals look fine because the violations
sit inside cells that no marginal ever inspects.

**The hard part here is not the metric, it is the sample size.** Sex x Race on Adult
produces ten subgroups whose sizes span three orders of magnitude. In a 30% test split
the smallest has a few dozen people, and its true-positive rate is computed over a
handful of positive labels. A TPR estimated from five people is not a measurement, and
reporting it beside a TPR estimated from six thousand as though they were comparable is
the actual methodological error -- worse than not reporting it at all, because it
manufactures a finding.

So every rate here is reported with its denominator and a Wilson confidence interval,
and :func:`reliability_report` names the subgroups that are too small to support a
claim. A gap that vanishes inside overlapping confidence intervals is not evidence of
unfairness; a gap that survives them is. This module is built to be able to tell the
difference and to say so out loud.

Wilson intervals rather than normal-approximation ones specifically because the normal
interval collapses to zero width at p=0 or p=1 -- exactly the situation a tiny subgroup
produces, and exactly where a false claim of certainty would be most damaging.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Below this many subjects in the relevant denominator, a rate is reported but flagged
# as unreliable. 30 is the conventional rule-of-thumb floor for a proportion estimate;
# the flag matters more than the exact cutoff, and the interval is reported regardless.
MIN_RELIABLE_DENOMINATOR = 30

# 1.96 -> 95% Wilson interval.
Z = 1.959964


def combine(*attributes: np.ndarray, separator: str = " x ") -> np.ndarray:
    """Build intersectional subgroup labels from two or more attributes."""
    columns = [pd.Series(np.asarray(a)).astype(str) for a in attributes]
    if len({len(c) for c in columns}) != 1:
        raise ValueError("attributes must be the same length")
    combined = columns[0]
    for column in columns[1:]:
        combined = combined + separator + column
    return combined.to_numpy()


def wilson_interval(successes: int, trials: int, z: float = Z) -> tuple[float, float]:
    """95% Wilson score interval for a proportion.

    Returns ``(nan, nan)`` for an empty denominator rather than a degenerate interval,
    matching the NaN convention in :mod:`src.metrics`.
    """
    if trials == 0:
        return (np.nan, np.nan)
    p = successes / trials
    denominator = 1 + z**2 / trials
    centre = (p + z**2 / (2 * trials)) / denominator
    half = (z / denominator) * np.sqrt(p * (1 - p) / trials + z**2 / (4 * trials**2))
    return (float(max(0.0, centre - half)), float(min(1.0, centre + half)))


def subgroup_table(y_true, y_pred, subgroups) -> pd.DataFrame:
    """Per-subgroup rates with denominators and confidence intervals.

    The ``n_*`` columns are the point of the table as much as the rates are: they are
    what tells a reader whether a rate below it means anything. ``reliable`` is False
    when the selection-rate or TPR denominator falls under
    :data:`MIN_RELIABLE_DENOMINATOR`.
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    subgroups = np.asarray(subgroups)

    rows = []
    for name in sorted(np.unique(subgroups)):
        mask = subgroups == name
        yt, yp = y_true[mask], y_pred[mask]
        positives, negatives = yt == 1, yt == 0
        n, n_pos, n_neg = int(mask.sum()), int(positives.sum()), int(negatives.sum())

        selected = int(yp.sum())
        true_positive = int(yp[positives].sum()) if n_pos else 0
        false_positive = int(yp[negatives].sum()) if n_neg else 0

        sr_low, sr_high = wilson_interval(selected, n)
        tpr_low, tpr_high = wilson_interval(true_positive, n_pos)

        rows.append({
            "subgroup": name,
            "n": n,
            "n_positive_label": n_pos,
            "selection_rate": selected / n if n else np.nan,
            "sr_ci_low": sr_low,
            "sr_ci_high": sr_high,
            "tpr": true_positive / n_pos if n_pos else np.nan,
            "tpr_ci_low": tpr_low,
            "tpr_ci_high": tpr_high,
            "fpr": false_positive / n_neg if n_neg else np.nan,
            "accuracy": float(np.mean(yp == yt)) if n else np.nan,
            "reliable": n >= MIN_RELIABLE_DENOMINATOR
            and n_pos >= MIN_RELIABLE_DENOMINATOR,
        })
    return pd.DataFrame(rows).set_index("subgroup")


def max_gap(table: pd.DataFrame, column: str, *, reliable_only: bool = False) -> dict:
    """Largest spread across subgroups, with the two subgroups responsible.

    This is the multi-group generalisation of the two-group differences in
    :mod:`src.metrics`: max minus min over subgroups, which reduces to the absolute
    difference when there are exactly two. ``reliable_only`` restricts the comparison
    to subgroups big enough to support the claim, which is what should be quoted --
    the unrestricted number is reported alongside it precisely to show how much of an
    apparent intersectional gap is driven by subgroups too small to measure.
    """
    subset = table[table["reliable"]] if reliable_only else table
    values = subset[column].dropna()
    if len(values) < 2:
        return {"gap": np.nan, "best": None, "worst": None, "n_subgroups": len(values)}
    return {
        "gap": float(values.max() - values.min()),
        "best": str(values.idxmax()),
        "worst": str(values.idxmin()),
        "n_subgroups": int(len(values)),
    }


def gaps_overlap(table: pd.DataFrame, low: str, high: str, a: str, b: str) -> bool:
    """Do two subgroups' confidence intervals overlap?

    If they do, the difference between their point estimates is not evidence of a real
    difference, however large it looks in a heatmap.
    """
    return not (
        table.loc[a, low] > table.loc[b, high] or table.loc[b, low] > table.loc[a, high]
    )


def reliability_report(table: pd.DataFrame) -> pd.DataFrame:
    """The subgroups whose numbers should not be quoted, and why."""
    unreliable = table[~table["reliable"]].copy()
    unreliable["reason"] = np.where(
        unreliable["n"] < MIN_RELIABLE_DENOMINATOR,
        "subgroup too small",
        "too few positive labels for a TPR",
    )
    return unreliable[["n", "n_positive_label", "selection_rate", "tpr", "reason"]]


def worst_off(table: pd.DataFrame, column: str = "selection_rate", *, reliable_only: bool = True):
    """The subgroup receiving the fewest favourable decisions.

    Reported per method so that "the gap closed" can be checked against "and this
    particular subgroup still ended up at the bottom".
    """
    subset = table[table["reliable"]] if reliable_only else table
    values = subset[column].dropna()
    return (str(values.idxmin()), float(values.min())) if len(values) else (None, np.nan)
