"""COMPAS and LSAC must be the datasets everyone else means, and oriented correctly.

**Individual work, beyond the course submission.**

Two failure modes, both silent, both fatal to the numbers rather than to the run.

1. **A cleaning choice nobody else made.** COMPAS is a benchmark only because ProPublica's
   filtered population is the one every paper argues about. A defensible-but-different filter
   would give a dataset that is internally valid and comparable to nothing, and the row count
   is the only available check.

2. **An inverted convention.** This project defines ``y == 1`` as the favourable outcome and
   ``privileged`` as the advantaged group. COMPAS records the *unfavourable* outcome
   (``two_year_recid``), and on its sex arm the advantaged group is **Female**, which is the
   reverse of the usual reading. Getting either backwards produces every who-pays number with
   its sign flipped, and nothing raises: the tables still look plausible.

Run:  python -m tests.test_new_instruments
"""

from __future__ import annotations

import pandas as pd

from src.datasets import build

# ProPublica's own notebook reports this after their documented filter.
PROPUBLICA_ROWS = 6172


def test_compas_reproduces_propublicas_population() -> None:
    """The filtered row count must match the analysis this dataset is famous for."""
    from src.datasets.compas import CompasLoader

    loader = CompasLoader()
    raw = pd.read_csv(loader._download())
    filtered = CompasLoader._propublica_filter(raw)
    assert len(filtered) == PROPUBLICA_ROWS, (
        f"ProPublica's filter gives {PROPUBLICA_ROWS} rows; this gives {len(filtered)}. "
        "A different population is not comparable to the literature on this dataset")

    # The race arm keeps only the two groups ProPublica compare.
    race = build("compas").load()
    assert set(race.a.unique()) == {"Caucasian", "African-American"}
    assert race.n_samples == len(
        filtered[filtered["race"].isin(["Caucasian", "African-American"])])
    print(f"  ProPublica filter reproduces {len(filtered):,} rows; "
          f"race arm keeps {race.n_samples:,}")


def test_compas_label_is_the_favourable_outcome() -> None:
    """y == 1 must mean 'predicted not to reoffend', not the recorded target."""
    from src.datasets.compas import CompasLoader

    loader = CompasLoader()
    raw = CompasLoader._propublica_filter(pd.read_csv(loader._download()))
    raw = raw[raw["race"].isin(["Caucasian", "African-American"])]
    dataset = build("compas").load()

    assert abs(dataset.y.mean() - (1 - raw["two_year_recid"].mean())) < 1e-9, (
        "the COMPAS label is not inverted; y=1 currently means the person REOFFENDED, "
        "which flips the sign of every direction this project reports")
    assert dataset.y.mean() > 0.5, "most defendants do not reoffend, so y=1 should be common"

    # The instrument's own output must not be a feature, or the task is circular.
    banned = {"decile_score", "score_text", "v_decile_score", "v_score_text",
              "two_year_recid", "is_recid"}
    leaked = banned & set(dataset.X.columns)
    assert not leaked, f"COMPAS's own score or the target leaked into the features: {leaked}"
    print(f"  y=1 is the favourable outcome ({dataset.y.mean():.3f}); "
          f"no score or target columns in X")


def test_privileged_group_follows_the_data_everywhere() -> None:
    """The declared privileged group must actually have the higher favourable rate.

    Not a tautology and not a social claim -- it is the convention `base.py` documents, and
    the COMPAS sex arm is the case that breaks intuition: women in this cohort reoffend less,
    so they are the advantaged group on this outcome.
    """
    for spec in ["compas", "compas:sex", "lawschool", "lawschool:male"]:
        dataset = build(spec).load()
        rates = dataset.base_rates().set_index("group")["P(y=1)"]
        assert rates["privileged"] > rates["unprivileged"], (
            f"{spec}: declared privileged group has the LOWER favourable rate "
            f"({rates['privileged']:.3f} against {rates['unprivileged']:.3f}); every "
            f"who-pays number from this dataset would come out sign-inverted")
        print(f"  {dataset.name:22} {rates['privileged']:.3f} > {rates['unprivileged']:.3f}")


def test_lawschool_is_the_high_selection_rate_instrument() -> None:
    """LSAC exists here to populate the top of the range; check that it does."""
    dataset = build("lawschool").load()
    assert dataset.y.mean() > 0.75, (
        f"lawschool is carried because bar passage is naturally generous; its base rate is "
        f"now {dataset.y.mean():.3f}, which is not the top of the selection-rate range")
    # Document 15's floor, which this dataset clears and COMPAS does not.
    assert int(dataset.n_samples * 0.3) > 2500, "lawschool should clear docs/15's floor"
    assert int(build("compas").load().n_samples * 0.3) < 2500, (
        "COMPAS is documented as sitting BELOW docs/15's floor; if it no longer does, the "
        "power warning attached to its results is wrong")
    print(f"  lawschool base rate {dataset.y.mean():.3f}, test split "
          f"{int(dataset.n_samples * 0.3):,} (clears 2,500); COMPAS "
          f"{int(build('compas').load().n_samples * 0.3):,} (below it, as documented)")


def test_no_nulls_reach_the_estimator() -> None:
    """A NaN in X reaches fairlearn as a crash three layers down; catch it here."""
    for spec in ["compas", "compas:sex", "lawschool", "lawschool:male"]:
        dataset = build(spec).load()
        assert not dataset.X.isna().any().any(), f"{spec}: nulls in X"
        assert not dataset.y.isna().any(), f"{spec}: nulls in y"
        assert not dataset.a.isna().any(), f"{spec}: nulls in a"
    print("  no nulls in X, y or a for either instrument")


def main() -> None:
    tests = [
        test_compas_reproduces_propublicas_population,
        test_compas_label_is_the_favourable_outcome,
        test_privileged_group_follows_the_data_everywhere,
        test_lawschool_is_the_high_selection_rate_instrument,
        test_no_nulls_reach_the_estimator,
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
        except Exception as exc:                                  # noqa: BLE001
            failures += 1
            print(f"  ERROR: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
