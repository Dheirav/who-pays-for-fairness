"""Invariants for the fairness metrics.

The governing rule in :mod:`src.metrics` is that **an undefined rate must never
masquerade as a defined one**. ``_rates`` returns NaN rather than 0 for an empty
denominator precisely so that a group with no positive labels cannot be reported as
having a perfect true-positive rate.

That guarantee has to hold at every level, not just the lowest one. It did not:
``equalized_odds_difference`` combined its two components with a bare ``max``, and
Python's ``max`` resolves NaN by argument *order* — ``max(nan, 0.5)`` is nan but
``max(0.5, nan)`` is 0.5, because every comparison against NaN is False. So whenever a
group had no negative labels, the FPR gap was undefined, the TPR gap won the ``max``,
and a TPR-only gap was reported as the full equalized-odds difference. Silently.

These tests pin the guarantee at the level where it broke, and check the orientation
conventions that are the other classic source of silently-wrong fairness numbers.

Run:  python -m tests.test_metrics
"""

from __future__ import annotations

import numpy as np

from src.metrics import (
    _rates,
    demographic_parity_difference,
    disparate_impact,
    equalized_odds_difference,
    evaluate,
    group_breakdown,
)

KW = {"privileged": "M", "unprivileged": "F"}


def test_empty_denominators_give_nan_not_zero() -> None:
    """A rate with no denominator is unknown, not perfect."""
    y_true = np.array([1, 1, 1, 1])          # no negatives at all
    y_pred = np.array([1, 0, 1, 0])
    rates = _rates(y_true, y_pred)
    print(f"  all-positive labels -> fpr={rates['fpr']}, tpr={rates['tpr']:.2f}")
    assert np.isnan(rates["fpr"]), "FPR with no negatives must be NaN, not 0"
    assert not np.isnan(rates["tpr"])

    rates = _rates(np.array([0, 0, 0]), np.array([0, 1, 0]))
    print(f"  all-negative labels -> tpr={rates['tpr']}, fpr={rates['fpr']:.2f}")
    assert np.isnan(rates["tpr"]), "TPR with no positives must be NaN, not 0"


def test_equalized_odds_is_nan_when_either_component_is_undefined() -> None:
    """Both orders, because the bug was that only one of them was caught.

    The first case has no positives in the unprivileged group (TPR undefined), the
    second has no negatives (FPR undefined). A bare ``max`` returns NaN for one and a
    plausible number for the other purely because of argument order.
    """
    a = np.array(["F"] * 4 + ["M"] * 4)
    y_pred = np.array([1, 1, 0, 0, 1, 1, 1, 0])

    no_positives = np.array([0, 0, 0, 0, 1, 1, 0, 0])
    no_negatives = np.array([1, 1, 1, 1, 1, 1, 0, 0])

    for label, y_true in (("TPR undefined", no_positives), ("FPR undefined", no_negatives)):
        value = equalized_odds_difference(y_true, y_pred, a, **KW)
        print(f"  {label}: equalized_odds_difference = {value}")
        assert np.isnan(value), (
            f"{label}: an undefined component must produce NaN, not a partial gap"
        )


def test_equalized_odds_is_the_larger_of_the_two_gaps_when_both_defined() -> None:
    """The NaN guard must not change the ordinary case."""
    y_true = np.array([1, 1, 0, 0, 1, 1, 0, 0])
    y_pred = np.array([1, 0, 0, 0, 1, 1, 1, 0])
    a = np.array(["F"] * 4 + ["M"] * 4)

    table = group_breakdown(y_true, y_pred, a, **KW)
    tpr_gap = abs(table.loc["privileged", "tpr"] - table.loc["unprivileged", "tpr"])
    fpr_gap = abs(table.loc["privileged", "fpr"] - table.loc["unprivileged", "fpr"])
    value = equalized_odds_difference(y_true, y_pred, a, **KW)
    print(f"  tpr gap {tpr_gap:.3f}, fpr gap {fpr_gap:.3f} -> {value:.3f}")
    assert value == max(tpr_gap, fpr_gap)


def test_disparate_impact_is_nan_when_the_privileged_rate_is_zero() -> None:
    """0/0 is undefined, not infinitely unfair."""
    y_pred = np.array([0, 0, 0, 0, 0, 0])
    a = np.array(["M", "M", "M", "F", "F", "F"])
    value = disparate_impact(y_pred, a, **KW)
    print(f"  nobody selected -> disparate impact = {value}")
    assert np.isnan(value)


def test_group_orientation_is_not_silently_reversible() -> None:
    """Swapping the groups must change disparate impact, or the labels mean nothing.

    A privileged/unprivileged mix-up is the most common way to get plausible but wrong
    fairness numbers. Demographic parity is an absolute difference so it is invariant
    by construction; disparate impact is a ratio and must invert.
    """
    y_pred = np.array([1, 1, 1, 0, 1, 0, 0, 0])
    a = np.array(["M"] * 4 + ["F"] * 4)

    forward = disparate_impact(y_pred, a, privileged="M", unprivileged="F")
    reversed_ = disparate_impact(y_pred, a, privileged="F", unprivileged="M")
    dp_forward = demographic_parity_difference(y_pred, a, privileged="M", unprivileged="F")
    dp_reversed = demographic_parity_difference(y_pred, a, privileged="F", unprivileged="M")

    print(f"  DI  M/F={forward:.3f}  F/M={reversed_:.3f}")
    print(f"  DP  M/F={dp_forward:.3f}  F/M={dp_reversed:.3f} (absolute, so invariant)")
    assert abs(forward * reversed_ - 1.0) < 1e-12, "DI must invert when groups swap"
    assert dp_forward == dp_reversed


def test_evaluate_propagates_nan_rather_than_inventing_a_number() -> None:
    """One undefined metric must not be quietly filled in by the row builder."""
    y_true = np.array([1, 1, 1, 1, 1, 1, 0, 0])
    y_pred = np.array([1, 1, 0, 0, 1, 1, 1, 0])
    a = np.array(["F"] * 4 + ["M"] * 4)
    row = evaluate(y_true, y_pred, a, label="t", **KW)
    print(f"  {{k: round(v,3) if isinstance(v,float) else v for k,v in row.items()}}")
    assert np.isnan(row["equalized_odds_diff"])
    assert not np.isnan(row["accuracy"]), "the defined metrics must still be reported"


def main() -> None:
    tests = [
        test_empty_denominators_give_nan_not_zero,
        test_equalized_odds_is_nan_when_either_component_is_undefined,
        test_equalized_odds_is_the_larger_of_the_two_gaps_when_both_defined,
        test_disparate_impact_is_nan_when_the_privileged_rate_is_zero,
        test_group_orientation_is_not_silently_reversible,
        test_evaluate_propagates_nan_rather_than_inventing_a_number,
    ]
    failures = 0
    for test in tests:
        print(f"\n{test.__name__}")
        try:
            test()
            print("  PASS")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL: {exc}")
        except Exception as exc:
            failures += 1
            print(f"  ERROR: {type(exc).__name__}: {exc}")

    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
