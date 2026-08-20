"""The income threshold is an experimental knob, and it must not disturb anything else.

**Individual work, beyond the course submission.**

``ACSIncomeLoader`` takes a ``threshold`` so that document 22's conjecture -- that
levelling down reverses on high-base-rate tasks -- can be tested by varying the base rate
and nothing else. Two ways that could go wrong silently, both checked here:

1. **The reconstruction could differ from the benchmark.** Non-default thresholds rebuild
   ``ACSIncome`` from its own parts with one substitution. If that reconstruction filters
   or postprocesses differently, every threshold arm would be measured on a subtly
   different population and the sweep would confound the cutoff with the pipeline. The
   check is that the rebuilt problem, at the default cutoff, reproduces ``ACSIncome``
   exactly -- same rows, same features, same labels.

2. **Two thresholds could collide on disk.** The threshold changes the label, so runs that
   differ in it are different datasets. This project has shipped four separate silent
   overwrite bugs, so the naming rule is asserted rather than trusted.

Run:  python -m tests.test_acs_threshold
"""

from __future__ import annotations

import numpy as np

from src.datasets import build
from src.datasets.acs import DEFAULT_THRESHOLD, ACSIncomeLoader

STATE = "WY"          # the smallest population, so the check is quick


def test_reconstruction_matches_the_benchmark_at_the_default() -> None:
    """The rebuilt problem must be indistinguishable from ACSIncome at $50,000."""
    from folktables import ACSDataSource, ACSIncome, BasicProblem

    from src.datasets.acs import DATA_DIR

    source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person",
                           root_dir=str(DATA_DIR))
    frame = source.get_data(states=[STATE], download=True)

    X_bench, y_bench, g_bench = ACSIncome.df_to_pandas(frame)
    rebuilt = BasicProblem(
        features=ACSIncome.features,
        target=ACSIncome.target,
        target_transform=lambda income: income > DEFAULT_THRESHOLD,
        group=ACSIncome.group,
        preprocess=ACSIncome._preprocess,
        postprocess=ACSIncome._postprocess,
    )
    X_new, y_new, g_new = rebuilt.df_to_pandas(frame)

    assert X_new.shape == X_bench.shape, f"{X_new.shape} against {X_bench.shape}"
    assert list(X_new.columns) == list(X_bench.columns), "feature list differs"
    assert np.array_equal(X_new.to_numpy(), X_bench.to_numpy()), "feature values differ"
    assert np.array_equal(np.asarray(y_new).ravel(), np.asarray(y_bench).ravel()), \
        "labels differ at the default threshold"
    assert np.array_equal(np.asarray(g_new).ravel(), np.asarray(g_bench).ravel()), \
        "groups differ"
    print(f"  rebuilt problem reproduces ACSIncome exactly on {STATE}: "
          f"{len(X_new):,} rows, {X_new.shape[1]} features, "
          f"{int(np.asarray(y_bench).sum()):,} positives")


def test_threshold_moves_the_base_rate_and_only_that() -> None:
    """A lower cutoff must label more people positive, on the same rows."""
    low = ACSIncomeLoader([STATE], threshold=20_000).load()
    default = ACSIncomeLoader([STATE]).load()
    high = ACSIncomeLoader([STATE], threshold=100_000).load()

    rates = [d.y.mean() for d in (high, default, low)]
    assert rates[0] < rates[1] < rates[2], f"base rate is not monotone in the cutoff: {rates}"

    # Same population throughout -- only the label may move.
    assert low.n_samples == default.n_samples == high.n_samples, "row count changed"
    assert list(low.X.columns) == list(default.X.columns), "feature set changed"
    assert np.array_equal(low.a.to_numpy(), default.a.to_numpy()), "protected groups changed"
    assert np.array_equal(low.X["AGEP"].to_numpy(), default.X["AGEP"].to_numpy()), \
        "features changed with the cutoff"
    print(f"  base rate {rates[0]:.3f} ($100k) -> {rates[1]:.3f} ($50k) -> "
          f"{rates[2]:.3f} ($20k) on {default.n_samples:,} fixed rows")


def test_threshold_reaches_the_output_path() -> None:
    """Two cutoffs must not share a results directory; the default must not move."""
    assert ACSIncomeLoader([STATE]).name == f"acs_income_{STATE.lower()}_2018", \
        "the default threshold changed the committed path"
    assert ACSIncomeLoader([STATE], threshold=20_000).name != ACSIncomeLoader([STATE]).name, \
        "two thresholds share one output directory"
    assert ACSIncomeLoader([STATE], threshold=20_000).name.endswith("_t20000")

    # And the same through the spec string, which is what the experiments are given.
    assert build(f"acs:{STATE}:SEX:20000").name.endswith("_t20000")
    assert build(f"acs:{STATE}").name == f"acs_income_{STATE.lower()}_2018"
    assert build(f"acs:{STATE}:RAC1P:20000").name.endswith("_rac1p_t20000")
    print("  paths separate by threshold; the default path is unchanged")


def test_constraint_and_learner_reach_the_output_path() -> None:
    """The same population under a different constraint or learner is a different result.

    The signature in the filename separates the *archived* copy, but both runs would still
    write the same canonical ``levelling_up_summary.csv`` and the second would win. That is
    bug three from ``src/results_io`` wearing new clothes, so the isolation is asserted at
    the directory level and the defaults are pinned so no existing arm moves.
    """
    from src.experiments.run_levelling_up import DEFAULT_CONSTRAINT, arms_for, output_stem
    from src.experiments.methods import BASE_MODEL

    base = "acs_income_al_2018_t20000"
    default = output_stem(base, DEFAULT_CONSTRAINT, BASE_MODEL)
    assert default == f"{base}_levelling_up", \
        f"the default output path moved to {default}; every committed arm is now orphaned"

    variants = {
        default,
        output_stem(base, "equalized_odds", BASE_MODEL),
        output_stem(base, DEFAULT_CONSTRAINT, "hist_gradient_boosting"),
        output_stem(base, "equalized_odds", "hist_gradient_boosting"),
    }
    assert len(variants) == 4, f"configurations share a directory: {sorted(variants)}"

    # The floor is a demographic-parity object and must not silently appear elsewhere,
    # where it would be scored against a criterion it does not implement.
    assert "expgrad_dp_floor" in arms_for(DEFAULT_CONSTRAINT)
    assert "expgrad_dp_floor" not in arms_for("equalized_odds")
    assert arms_for("equalized_odds") == ["baseline", "expgrad_eo"]

    # The sweep analyser must look where the runner writes, or it silently reads zero arms
    # and reports "no threshold arms found" as though the run had never happened.
    from src.experiments.analyse_threshold import arm_name
    assert arm_name("AL", 20_000, "_hgb") == output_stem(base, DEFAULT_CONSTRAINT,
                                                         "hist_gradient_boosting")
    from src.experiments.analyse_eo import eo_arm_name
    assert eo_arm_name("AL", 20_000) == output_stem(base, "equalized_odds", BASE_MODEL)
    print("  constraint and learner separate on disk; runner and analysers agree")


def main() -> None:
    tests = [
        test_reconstruction_matches_the_benchmark_at_the_default,
        test_threshold_moves_the_base_rate_and_only_that,
        test_threshold_reaches_the_output_path,
        test_constraint_and_learner_reach_the_output_path,
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
