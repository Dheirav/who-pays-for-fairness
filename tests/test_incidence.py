"""Correctness checks for the who-pays decomposition.

The decomposition in :mod:`src.incidence` is the project's own contribution rather
than something taken from a paper, so it needs evidence it is right. Unlike the
in-processing tests these use hand-built synthetic cases: the decomposition is exact
arithmetic, so its behaviour can be specified completely and checked against
hand-computed answers rather than against a reference implementation.

The cases are chosen to pin down the parts that are easy to get subtly wrong:

* the two contributions must sum to the closure *identically*, for every rate, or the
  "share" being reported is not a share of anything;
* a gap closed purely by raising the unprivileged group and one closed purely by
  lowering the privileged group must not produce the same answer -- that confusion is
  the entire reason the module exists;
* a gap that got *wider* must refuse to report a share rather than emitting a
  plausible-looking number;
* the rate-level and people-level answers must diverge when the groups differ in
  size, since that divergence is a reported finding.

Run:  python -m tests.test_incidence
"""

from __future__ import annotations

import numpy as np

from src.incidence import (
    churn_attribution,
    decompose_gap,
    disagreement,
    flip_counts,
    outcome_total,
    people_incidence,
)

KW = {"privileged": "M", "unprivileged": "F"}


def _case(priv_true, priv_base, priv_mit, unp_true, unp_base, unp_mit):
    """Assemble (y_true, a, y_base, y_mit) from per-group lists."""
    y_true = np.array(priv_true + unp_true)
    y_base = np.array(priv_base + unp_base)
    y_mit = np.array(priv_mit + unp_mit)
    a = np.array(["M"] * len(priv_true) + ["F"] * len(unp_true))
    return y_true, a, y_base, y_mit


def test_contributions_sum_to_closure() -> None:
    """The identity that makes 'share of the closure' a meaningful quantity."""
    rng = np.random.default_rng(0)
    for trial in range(200):
        n = 60
        y_true = rng.integers(0, 2, n)
        a = rng.choice(["M", "F"], n)
        y_base = rng.integers(0, 2, n)
        y_mit = rng.integers(0, 2, n)
        table = decompose_gap(y_true, a, y_base, y_mit, **KW)
        total = table["from_privileged_loss"] + table["from_unprivileged_gain"]
        assert np.allclose(total, table["closure"], equal_nan=True), (
            f"trial {trial}: contributions do not sum to closure\n{table}"
        )
    print("  200 random cases: privileged loss + unprivileged gain == closure")


def test_pure_levelling_up() -> None:
    """Unprivileged group gains, privileged group untouched -> share 0."""
    # Privileged: 2 of 4 selected, unchanged. Unprivileged: 0 of 4 -> 2 of 4.
    y_true, a, y_base, y_mit = _case(
        [1, 1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0],
        [1, 1, 0, 0], [0, 0, 0, 0], [1, 1, 0, 0],
    )
    row = decompose_gap(y_true, a, y_base, y_mit, **KW).loc["selection_rate"]
    print(f"  closure={row['closure']:.3f}  share_down={row['share_levelling_down']:.3f}"
          f"  verdict={row['verdict']}")
    assert row["closure"] == 0.5, row["closure"]
    assert row["from_privileged_loss"] == 0.0
    assert row["share_levelling_down"] == 0.0
    assert row["verdict"] == "levelling up"


def test_pure_levelling_down() -> None:
    """Privileged group loses, unprivileged group untouched -> share 1."""
    y_true, a, y_base, y_mit = _case(
        [1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0],
        [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
    )
    row = decompose_gap(y_true, a, y_base, y_mit, **KW).loc["selection_rate"]
    print(f"  closure={row['closure']:.3f}  share_down={row['share_levelling_down']:.3f}"
          f"  verdict={row['verdict']}")
    assert row["closure"] == 0.5
    assert row["from_unprivileged_gain"] == 0.0
    assert row["share_levelling_down"] == 1.0
    assert row["verdict"] == "levelling down"


def test_widened_gap_refuses_to_report_a_share() -> None:
    """A gap that grew must not produce a share -- there is no closure to divide."""
    y_true, a, y_base, y_mit = _case(
        [1, 1, 0, 0], [1, 0, 0, 0], [1, 1, 1, 0],
        [1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0],
    )
    row = decompose_gap(y_true, a, y_base, y_mit, **KW).loc["selection_rate"]
    print(f"  closure={row['closure']:.3f}  share_down={row['share_levelling_down']}"
          f"  verdict={row['verdict']}")
    assert row["closure"] < 0, "this case should widen the gap"
    assert np.isnan(row["share_levelling_down"])
    assert row["verdict"] == "gap widened"


def test_identical_predictions_are_a_no_op() -> None:
    """No change in, no change out -- guards against a spurious nonzero closure."""
    y_true, a, y_base, y_mit = _case(
        [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 1, 0],
        [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0],
    )
    table = decompose_gap(y_true, a, y_base, y_mit, **KW)
    flips = flip_counts(a, y_base, y_mit, **KW)
    print(f"  closures={table['closure'].tolist()}  churn={int(flips['churn'].sum())}")
    assert (table["closure"] == 0).all()
    assert flips["churn"].sum() == 0
    assert disagreement(y_base, y_mit) == 0.0
    assert outcome_total(y_base, y_mit)["delta"] == 0


def test_rate_and_people_shares_diverge_when_groups_differ_in_size() -> None:
    """Equal rate movement is unequal headcount -- the reason both are reported.

    Privileged group is 4x larger. Both groups move by the same 0.25 selection rate,
    so the rate-level split is exactly 50/50, while in people it is 4 lost per 1
    gained. Reporting only the rate answer would call this even-handed.
    """
    y_true, a, y_base, y_mit = _case(
        [1] * 8 + [0] * 8, [1] * 8 + [0] * 8, [1] * 4 + [0] * 12,
        [1, 1, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0],
    )
    row = decompose_gap(y_true, a, y_base, y_mit, **KW).loc["selection_rate"]
    flips = flip_counts(a, y_base, y_mit, **KW)
    people = people_incidence(flips)
    print(f"  rate share={row['share_levelling_down']:.3f}   "
          f"people share={people['people_share_levelling_down']:.3f}   "
          f"lost per gained={people['lost_per_gained']:.2f}")
    assert row["share_levelling_down"] == 0.5, "rates moved equally"
    assert people["people_share_levelling_down"] == 0.8, "4 lost vs 1 gained"
    assert people["lost_per_gained"] == 4.0
    assert people["net_favourable_change"] == -3


def test_flip_counts_reconcile_with_selection_rates() -> None:
    """Net flips divided by group size must equal the change in selection rate."""
    rng = np.random.default_rng(1)
    for _ in range(100):
        n = 80
        y_true = rng.integers(0, 2, n)
        a = rng.choice(["M", "F"], n)
        y_base = rng.integers(0, 2, n)
        y_mit = rng.integers(0, 2, n)
        table = decompose_gap(y_true, a, y_base, y_mit, **KW)
        flips = flip_counts(a, y_base, y_mit, **KW)
        for group, column in (("privileged", "priv"), ("unprivileged", "unpriv")):
            observed = flips.loc[group, "net"] / flips.loc[group, "n"]
            expected = table.loc["selection_rate", f"{column}_after"] - table.loc[
                "selection_rate", f"{column}_before"
            ]
            assert abs(observed - expected) < 1e-12
    print("  100 random cases: net flips / n == change in selection rate")


def test_churn_attribution_bounds() -> None:
    """Noise share is a fraction, capped at 1, and zero for deterministic methods."""
    assert churn_attribution(0.045, 0.038) == 0.038 / 0.045
    assert churn_attribution(0.045, 0.0) == 0.0
    assert churn_attribution(0.0, 0.0) == 0.0
    # A floor above the observed churn means all of it is noise, not more than all.
    assert churn_attribution(0.01, 0.05) == 1.0
    print("  bounded in [0, 1]; 0 when deterministic; capped when floor exceeds churn")


def main() -> None:
    tests = [
        test_contributions_sum_to_closure,
        test_pure_levelling_up,
        test_pure_levelling_down,
        test_widened_gap_refuses_to_report_a_share,
        test_identical_predictions_are_a_no_op,
        test_rate_and_people_shares_diverge_when_groups_differ_in_size,
        test_flip_counts_reconcile_with_selection_rates,
        test_churn_attribution_bounds,
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

    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
