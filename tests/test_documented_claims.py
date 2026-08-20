"""Re-derive every headline number in the research documents from the stored results.

This exists because this project has repeatedly shipped code that ran, produced plausible
numbers and was wrong -- the epsilon bug, two guards structurally unable to report the
outcome they existed to detect, and a constraint that converged to a duality gap of 0.0
while doing nothing. Each was caught by chance rather than by a check.

A document quoting a number that no longer follows from the data on disk is the same class
of failure and is currently invisible. This recomputes the load-bearing figures from the
result files and asserts the documents match, so a stale claim fails loudly.

**What this cannot do.** It checks that the documents agree with the results, not that the
results are correct. A wrong experiment faithfully reported passes every assertion here.
It is a consistency check, not a validation.

Run:  python -m tests.test_documented_claims
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "results"
COURSE = ROOT / "results"
DOCS = ROOT / "research" / "docs"

STATES = ["AL", "OR", "UT", "MS", "WV", "NM", "ND", "VT", "WY"]

# How close a recomputed value must be to the documented one. Correlations and shares are
# quoted to three or four decimals throughout, so this is tight enough to catch a real
# discrepancy and loose enough to tolerate the last printed digit.
TOLERANCE = 0.002


def _doc(number: int) -> str:
    matches = list(DOCS.glob(f"{number}-*.md"))
    assert len(matches) == 1, f"expected one doc {number}, found {matches}"
    return matches[0].read_text()


def _claims(text: str, pattern: str) -> list[float]:
    return [float(m) for m in re.findall(pattern, text)]


def _quotes(text: str, *values: str) -> None:
    """Assert the document actually states these figures.

    Recomputing a number and comparing it to a constant inside this file proves the data
    is unchanged; it proves nothing about the document. The first version of this suite
    made exactly that mistake -- editing docs/14's headline from +0.922 to +0.985 left it
    passing 8/8, because no assertion ever read the document. Every check now does both.
    """
    normalised = text.replace("\u2212", "-")
    missing = [v for v in values if v not in normalised]
    assert not missing, f"the document no longer states: {missing}"


def _corr(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    mask = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[mask], b[mask])[0, 1])


def _who_pays(arm: str) -> pd.DataFrame:
    """Per-population expgrad_dp runs, for one protected-attribute arm."""
    frames = []
    sources = [("Adult", COURSE / "who_pays_runs.csv")] if arm == "sex" else []
    suffix = "" if arm == "sex" else "_rac1p"
    for state in STATES:
        sources.append((state, RESEARCH / f"acs_income_{state.lower()}_2018{suffix}"
                        / "who_pays_runs.csv"))
    for label, path in sources:
        frame = pd.read_csv(path)
        frame["population"] = label
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def test_doc11_cross_flow_correlations() -> None:
    """docs/11: the P1 diagnostic and the confound beneath it."""
    fit = pd.read_csv(RESEARCH / "sweep" / "sweep_p1_formula_fit.csv")
    text = _doc(11)

    recomputed = {
        "error vs cross-flow": _corr(fit["cross_flow"], fit["mean_abs_error"]),
        "error vs size": _corr(fit["n"], fit["mean_abs_error"]),
        "error vs group ratio": _corr(fit["group_ratio"], fit["mean_abs_error"]),
        "ratio vs size": _corr(fit["group_ratio"], fit["n"]),
    }
    documented = {
        "error vs cross-flow": 0.885,
        "error vs size": -0.719,
        "error vs group ratio": -0.587,
        "ratio vs size": 0.794,
    }
    for key, value in documented.items():
        assert f"{value:+.3f}".lstrip("+") in text or f"{abs(value):.3f}" in text, (
            f"docs/11 no longer states {key} = {value}"
        )
        assert abs(recomputed[key] - value) < TOLERANCE, (
            f"docs/11 says {key} = {value:+.3f}, data gives {recomputed[key]:+.3f}"
        )
    print(f"  4 correlations re-derived from {len(fit)} populations")


def test_doc12_intersectional_condition() -> None:
    """docs/12: the minority-share relationship, and that it is unconfounded."""
    rows = []
    for state in STATES:
        runs = pd.read_csv(RESEARCH / f"acs_income_{state.lower()}_2018"
                           / "intersectional_runs.csv")
        base = runs[runs.arm == "baseline"]["intersectional_gap_reliable"].mean()
        after = runs[runs.arm == "expgrad_dp_sex"]["intersectional_gap_reliable"].mean()
        rows.append({"pop": state, "base": base, "after": after,
                     "removed": 100 * (base - after) / base})
    adult = pd.read_csv(COURSE / "intersectional_runs.csv")
    a_base = adult[adult.arm == "baseline"]["intersectional_gap_reliable"].mean()
    a_after = adult[adult.arm == "expgrad_dp_sex"]["intersectional_gap_reliable"].mean()
    rows.append({"pop": "Adult", "base": a_base, "after": a_after,
                 "removed": 100 * (a_base - a_after) / a_base})

    frame = pd.DataFrame(rows)
    # Minority shares and sizes are properties of the datasets, quoted in the document.
    text = _doc(12)
    assert "−0.671" in text or "-0.671" in text, "docs/12 no longer states r = -0.671"
    assert "+0.101" in text, "docs/12 no longer states r(minority, n) = +0.101"
    assert "85%" in text and "22%" in text, "docs/12 no longer states the 85/22 split"

    # VT is excluded on the stated ground of a degenerate baseline; check that ground.
    vt = frame[frame["pop"] == "VT"].iloc[0]
    assert vt["base"] < 0.05, (
        f"docs/12 excludes VT because its baseline gap is under 0.05; it is {vt['base']:.4f}"
    )
    kept = frame[frame["base"] > 0.05]
    assert len(kept) == 9, f"expected 9 populations after the VT exclusion, got {len(kept)}"
    print(f"  VT baseline gap {vt['base']:.4f} (< 0.05, exclusion ground holds); "
          f"{len(kept)} populations retained")


def test_doc13_partial_correlations() -> None:
    """docs/13: pooling breaks the confound, and cross-flow mediates."""
    pooled = pd.read_csv(RESEARCH / "sweep" / "arms_p1_pooled.csv")
    pooled["log_ratio"] = np.log(pooled["group_ratio"])

    def partial(x, y, control):
        r_xy, r_xc, r_yc = _corr(pooled[x], pooled[y]), _corr(pooled[x], pooled[control]), \
            _corr(pooled[y], pooled[control])
        return (r_xy - r_xc * r_yc) / np.sqrt((1 - r_xc**2) * (1 - r_yc**2))

    _quotes(_doc(13), "-0.180", "+0.548", "-0.683", "-0.038", "+0.787")
    checks = {
        "A1 pooled ratio vs n": (_corr(pooled["log_ratio"], pooled["n"]), -0.180),
        "A2 ratio partial": (partial("log_ratio", "mean_abs_error", "n"), 0.548),
        "A2 size partial": (partial("n", "mean_abs_error", "log_ratio"), -0.683),
        "mediation: ratio | cross-flow":
            (partial("log_ratio", "mean_abs_error", "cross_flow"), -0.038),
        "ratio -> cross-flow | n": (partial("log_ratio", "cross_flow", "n"), 0.787),
    }
    for name, (got, documented) in checks.items():
        assert abs(got - documented) < TOLERANCE, (
            f"docs/13 says {name} = {documented:+.3f}, data gives {got:+.3f}"
        )
    assert len(pooled) == 19, f"docs/13 claims 19 populations, file has {len(pooled)}"
    print(f"  5 partial correlations re-derived from {len(pooled)} pooled populations")


def test_doc14_endpoint_independence() -> None:
    """docs/14: the endpoint is independent of the start, and the two solvers agree."""
    rows = []
    for arm in ("sex", "race"):
        runs = _who_pays(arm)
        for population, group in runs.groupby("population"):
            dp = group[group.method == "expgrad_dp"]
            grid = group[group.method == "gridsearch_dp"]
            rows.append({
                "arm": arm, "population": population,
                "baseline_eo": dp.baseline_eo_diff.mean(),
                "eo_expgrad": dp.eo_diff.mean(),
                "eo_gridsearch": grid.eo_diff.mean(),
                "dp_expgrad": dp.dp_diff.mean(),
                "dp_gridsearch": grid.dp_diff.mean(),
                "cost": (dp.eo_diff - dp.baseline_eo_diff).mean(),
            })
    frame = pd.DataFrame(rows)

    independence = _corr(frame["baseline_eo"], frame["eo_expgrad"])
    assert abs(independence - (-0.106)) < TOLERANCE, (
        f"docs/14 says r(baseline EO, EO after) = -0.106, data gives {independence:+.3f}"
    )
    agreement = _corr(frame["eo_expgrad"], frame["eo_gridsearch"])
    assert abs(agreement - 0.922) < TOLERANCE, (
        f"docs/14 says D1 r = +0.922, data gives {agreement:+.3f}"
    )
    d0 = (frame["dp_expgrad"] - frame["dp_gridsearch"]).abs().mean()
    assert abs(d0 - 0.0113) < TOLERANCE, f"docs/14 says D0 = 0.0113, data gives {d0:.4f}"
    d2_methods = (frame["eo_expgrad"] - frame["eo_gridsearch"]).abs().mean()
    d2_spread = frame["eo_expgrad"].std()
    assert abs(d2_methods - 0.0205) < TOLERANCE and abs(d2_spread - 0.0622) < TOLERANCE, (
        f"docs/14 says D2 is 0.0205 vs 0.0622, data gives {d2_methods:.4f} vs {d2_spread:.4f}"
    )

    # The direction reversal between arms, which is the document's opening claim.
    sex = frame[frame.arm == "sex"]
    race = frame[frame.arm == "race"]
    assert (sex.cost > 0).sum() == 9 and len(sex) == 10, (
        f"docs/14 says EO worsened in 9 of 10 on sex; data gives "
        f"{(sex.cost > 0).sum()} of {len(sex)}"
    )
    assert (race.cost > 0).sum() == 1 and len(race) == 9, (
        f"docs/14 says EO worsened in 1 of 9 on race; data gives "
        f"{(race.cost > 0).sum()} of {len(race)}"
    )
    _quotes(_doc(14), "-0.106", "+0.922", "0.0113", "0.0205", "0.0622",
            "9 of 10", "1 of 9")
    print(f"  independence {independence:+.3f}, agreement {agreement:+.3f}, "
          f"9/10 sex and 1/9 race confirmed; document quotes all seven")


def test_doc15_arbitrariness() -> None:
    """docs/15: the floor exceeds churn in 5 of 38 runs, all on small test sets."""
    rows = []
    for arm in ("sex", "race"):
        runs = _who_pays(arm)
        runs = runs[runs.method.isin(["expgrad_dp", "expgrad_eo"])]
        for (population, method), group in runs.groupby(["population", "method"]):
            rows.append({
                "n_test": int(group.n_priv.iloc[0] + group.n_unpriv.iloc[0]),
                "ratio": (group.arbitrariness_floor / group.total_churn).mean(),
            })
    frame = pd.DataFrame(rows)
    exceed = int((frame["ratio"] > 1).sum())
    assert len(frame) == 38, f"docs/15 says 38 runs, data gives {len(frame)}"
    assert exceed == 5, f"docs/15 says 5 exceedances, data gives {exceed}"
    r = _corr(frame["n_test"], frame["ratio"])
    assert abs(r - (-0.360)) < TOLERANCE, (
        f"docs/15 says r = -0.360, data gives {r:+.3f}"
    )
    bands = {
        "< 1,500": frame[frame.n_test < 1500]["ratio"].mean(),
        "1,500-3,000": frame[(frame.n_test >= 1500) & (frame.n_test < 3000)]["ratio"].mean(),
        "> 3,000": frame[frame.n_test >= 3000]["ratio"].mean(),
    }
    documented = {"< 1,500": 0.79, "1,500-3,000": 0.46, "> 3,000": 0.35}
    for band, value in documented.items():
        assert abs(bands[band] - value) < 0.01, (
            f"docs/15 says the {band} band means {value}, data gives {bands[band]:.2f}"
        )
    assert all(frame[frame.ratio > 1]["n_test"] < 2500), (
        "docs/15 claims every exceedance is on a small test set"
    )
    _quotes(_doc(15), "5 of 38", "-0.360", "0.79", "0.46", "0.35")
    print(f"  {exceed}/{len(frame)} exceedances, r = {r:+.3f}, three bands match; "
          f"document quotes all five")


def test_doc16_and_17_injection_tables() -> None:
    """docs/16 and 17: the planted-proxy tables, as run."""
    one = pd.read_csv(RESEARCH / "acs_income_al_2018_injection" / "injection_summary.csv")
    text16 = _doc(16)
    for _, row in one.iterrows():
        assert f"{row['excess']:+.4f}".replace("+", "") in text16.replace("−", "-") or \
               f"{abs(row['excess']):.4f}" in text16, (
            f"docs/16 does not quote the excess {row['excess']:+.4f} "
            f"at strength {row['strength']}"
        )
    # The document's central claim is that the excess declines monotonically.
    excesses = one.sort_values("strength")["excess"].to_numpy()
    assert all(np.diff(excesses) < 0), (
        f"docs/16 claims a monotone decline; data gives {excesses.round(4)}"
    )

    two = pd.read_csv(RESEARCH / "acs_income_al_2018_injection2" / "injection2_summary.csv")
    assert len(two) == 6, f"docs/17 shows 6 cells, file has {len(two)}"
    assert two["excess"].abs().max() < 0.03, (
        f"docs/17 claims |excess| never exceeds 0.03; max is {two['excess'].abs().max():.4f}"
    )
    span = two["synth_baseline"].max() / two["synth_baseline"].min()
    assert span > 8, f"docs/17 claims the share moves ~ninefold; it moves {span:.1f}x"
    print(f"  docs/16 monotone decline {excesses.round(4)}; "
          f"docs/17 max |excess| {two['excess'].abs().max():.4f}, share span {span:.1f}x")


def test_doc19_levelling_up() -> None:
    """docs/19: parity held, pie preserved, incidence changed."""
    summary = pd.read_csv(RESEARCH / "adult_levelling_up" / "levelling_up_summary.csv"
                          ).set_index("arm")
    plain, floored = summary.loc["expgrad_dp"], summary.loc["expgrad_dp_floor"]

    assert abs(plain["dp_diff"] - 0.0178) < TOLERANCE
    assert abs(floored["dp_diff"] - 0.0179) < TOLERANCE, (
        "docs/19 claims parity is satisfied to the same tolerance"
    )
    assert abs(plain["positives_pct_change"] - (-20.45)) < 0.1
    assert abs(floored["positives_pct_change"] - (-0.617)) < 0.1, (
        f"docs/19 says -0.6% with the floor, data gives "
        f"{floored['positives_pct_change']:.2f}%"
    )
    assert abs(plain["lost_per_gained"] - 2.68) < 0.01
    assert abs(floored["lost_per_gained"] - 1.03) < 0.01, (
        f"docs/19 says 1.03 lost per gained, data gives {floored['lost_per_gained']:.2f}"
    )
    assert floored["share_levelling_down"] < 0.5, (
        "docs/19 claims the rate-level share drops below 0.5"
    )
    _quotes(_doc(19), "0.0178", "0.0179", "-20.5%", "-0.6%", "2.68", "1.03",
            "0.333", "0.545")
    print(f"  DP {plain['dp_diff']:.4f} vs {floored['dp_diff']:.4f}, "
          f"pie {plain['positives_pct_change']:.1f}% vs "
          f"{floored['positives_pct_change']:.1f}%, "
          f"exchange {plain['lost_per_gained']:.2f} vs {floored['lost_per_gained']:.2f}; "
          f"document quotes all eight")


def test_course_documents_still_match_their_results() -> None:
    """The submitted documents must agree with the submitted results.

    Everything else here checks research claims. This checks the deliverable, which is
    the part that gets handed in.
    """
    # Written by `DataFrame.agg(["mean", "std"])`, so the header is two rows and the
    # metric/statistic pair is a column MultiIndex. Read as a flat frame it yields a
    # stray "method" row and no usable column names -- which is how the first version of
    # this check failed, on the file format rather than on the numbers.
    ablation = pd.read_csv(COURSE / "ablation_summary.csv", header=[0, 1], index_col=0)
    ablation = ablation[ablation.index.notna()]
    text = (ROOT / "docs" / "04-ablation.md").read_text()

    for method, expected in [("baseline", 0.1861), ("expgrad_dp", 0.0178),
                             ("gridsearch_dp", 0.0150)]:
        got = float(ablation.loc[method, ("demographic_parity_diff", "mean")])
        assert abs(got - expected) < TOLERANCE, (
            f"docs/04 quotes DP {expected} for {method}; results give {got:.4f}"
        )
        assert f"{expected:.4f}" in text, f"docs/04 no longer quotes {expected} for {method}"

    # And the deliverables themselves, which are what actually gets handed in.
    import pymupdf
    report = "\n".join(page.get_text() for page in
                        pymupdf.open(ROOT / "bias_mitigation_report.pdf"))
    for value in ("0.0150", "0.0197", "0.1897"):
        assert value in report, f"the report no longer quotes {value}"
    print(f"  ablation table matches results for {len(ablation)} methods; "
          f"report quotes them too")


def test_doc20_share_decomposition() -> None:
    """docs/20: the coalition figure, its seed consistency, and the donor split.

    Recomputed through the analysis module's own functions rather than reimplemented
    here, so that a change to how the decomposition is defined fails this test instead
    of silently leaving the document describing an older definition.
    """
    from src.experiments.analyse_attribution import (
        donors, load_seed_shares, pair_across_methods, pair_by_seed,
    )

    # The pair is an argument to the module, so the document's subject is named here
    # rather than inherited from a constant that could change underneath it.
    pair = ["relationship", "marital-status"]
    text = _doc(20)
    per_seed = pair_by_seed(load_seed_shares(COURSE, list(range(5))), "expgrad_dp", pair)
    mean_shares = pd.read_csv(COURSE / "shap_feature_shares.csv", index_col=0)
    across = pair_across_methods(mean_shares, pair)
    given_up = donors(mean_shares, "expgrad_dp")

    documented = {
        "relationship, mean over seeds": (per_seed["first_pct"].mean(), "+155.0%"),
        "the pair, mean over seeds": (per_seed["pair_pct"].mean(), "+11.6%"),
        "expgrad_dp pair, from mean shares": (across.loc["expgrad_dp", "pair_pct"], "+11.7%"),
        "expgrad_eo pair, from mean shares": (across.loc["expgrad_eo", "pair_pct"], "−26.4%"),
        "marital-status share of losses": (
            given_up.loc["marital-status", "pct_of_all_given_up"], "44.9%"),
    }
    for label, (value, quoted) in documented.items():
        assert quoted in text, f"docs/20 no longer states {label} = {quoted}"
        assert abs(value - float(quoted.replace("−", "-").strip("+%"))) < 0.05, (
            f"docs/20 says {label} = {quoted}, data gives {value:+.1f}%"
        )

    # The document's argument rests on the residual being present in every split, not on
    # its size, so that is asserted rather than the mean alone.
    positive = int((per_seed["pair_pct"] > 0).sum())
    assert positive == len(per_seed), (
        f"docs/20 claims the coalition residual is positive in every seed; "
        f"it is positive in {positive}/{len(per_seed)}"
    )
    assert "5 of 5 seeds" in text, "docs/20 no longer states the 5-of-5 seed consistency"

    # The constraint-specific reading in docs/18's amendment needs the signs to differ.
    assert across.loc["expgrad_dp", "pair_pct"] > 0 > across.loc["expgrad_eo", "pair_pct"], (
        "docs/18's amendment claims DP raises the pair while EO lowers it; the signs no "
        "longer differ"
    )
    print(f"  coalition {per_seed['pair_pct'].mean():+.1f}% against "
          f"{per_seed['first_pct'].mean():+.1f}% for the single feature, "
          f"positive in {positive}/{len(per_seed)} seeds")


def test_doc21_floor_replication() -> None:
    """docs/21: the replication verdict, including the prediction that failed.

    The failed prediction is asserted *as failing*. A later change that quietly made L2
    pass would leave the document describing a failure that no longer exists, which is
    the same staleness this suite exists to catch.
    """
    from src.experiments.analyse_levelling_up import DEFAULT_STATES, RACE_ARM, SEX_ARM, load_arm

    text = _doc(21)
    arms = {SEX_ARM: load_arm(DEFAULT_STATES, SEX_ARM), RACE_ARM: load_arm(DEFAULT_STATES, RACE_ARM)}
    assert len(arms[SEX_ARM]) == 10, f"docs/21 claims 10 sex-arm populations, got {len(arms[SEX_ARM])}"
    assert len(arms[RACE_ARM]) == 9, f"docs/21 claims 9 race-arm populations, got {len(arms[RACE_ARM])}"

    # `_quotes` folds the document's U+2212 minus to ASCII, so these must be ASCII too.
    _quotes(text, "0.0020", "0.0037", "-6.4%", "+2.1%", "-7.4%", "+3.1%",
            "1.47", "0.88", "1.59", "0.79", "+0.12", "+0.15", "-0.708", "-0.567",
            "6.88%", "2.65%", "-20.5%", "-6.1%", "2.68", "1.46")

    for arm, expected in ((SEX_ARM, {"parity": 0.0020, "pie_plain": -6.4, "pie_floor": 2.1,
                                     "ex_plain": 1.47, "ex_floor": 0.88, "cost": 0.12}),
                          (RACE_ARM, {"parity": 0.0037, "pie_plain": -7.4, "pie_floor": 3.1,
                                      "ex_plain": 1.59, "ex_floor": 0.79, "cost": 0.15})):
        frame = arms[arm]
        got = {
            "parity": (frame["dp_floor"] - frame["dp_plain"]).abs().mean(),
            "pie_plain": frame["pie_plain"].mean(),
            "pie_floor": frame["pie_floor"].mean(),
            "ex_plain": frame["exchange_plain"].mean(),
            "ex_floor": frame["exchange_floor"].mean(),
            "cost": frame["extra_cost_pts"].mean(),
        }
        for key, value in expected.items():
            assert abs(got[key] - value) < 0.05, (
                f"docs/21 says {arm} {key} = {value}, data gives {got[key]:.4f}"
            )
        # L3 held unanimously; that is what carries the finding after L2 failed.
        assert (frame["exchange_floor"] < frame["exchange_plain"]).all(), (
            f"docs/21 claims the exchange rate fell in every {arm} population; it did not"
        )
        # L2 failed. If this ever passes, the document is stale.
        improved = frame["pie_floor"].abs() < frame["pie_plain"].abs()
        assert not improved.all(), (
            f"docs/21 records L2 as FAILING in the {arm} arm; it now passes, so the "
            "document must be rewritten rather than left describing a failure"
        )

    combined = pd.concat(arms.values())
    assert len(combined) == 19, f"docs/21 claims 19 populations, got {len(combined)}"
    assert int((combined["exchange_floor"] < 1).sum()) == 16, "docs/21 states 16 of 19 under 1.0"
    assert int((combined["exchange_plain"] < 1).sum()) == 1, "docs/21 states 1 of 19 under 1.0 plain"
    assert int((combined["pie_floor"] < 0).sum()) == 1, "docs/21 states only Adult still shrinks"
    assert combined.loc["Adult", "pie_plain"].mean() < combined[
        combined.index != "Adult"]["pie_plain"].mean(), "docs/21 claims Adult is the extreme case"
    print(f"  19 populations; L3 unanimous, L2 failed as documented; "
          f"exchange under 1.0 in {int((combined['exchange_floor'] < 1).sum())}/19")


def test_doc22_hmda_levels_up() -> None:
    """docs/22: the second domain reverses the levelling-down direction.

    The sign is asserted, not just the magnitude. The document's whole claim is that the
    pie *grows* here, so a change that flipped it back would make the document wrong in a
    way a tolerance check on the number alone would not catch.
    """
    text = _doc(22)
    _quotes(text, "0.1774", "0.0103", "+4.26%", "0.496", "0.0747", "0.0280",
            "+1.05%", "0.779", "0.808", "0.758", "+0.510", "-0.493")

    for arm, expected in (("race", {"dp_base": 0.1774, "dp_plain": 0.0103,
                                    "pie": 4.26, "exchange": 0.496}),
                          ("sex", {"dp_base": 0.0747, "dp_plain": 0.0280,
                                   "pie": 1.05, "exchange": 0.779})):
        runs = pd.read_csv(RESEARCH / f"hmda_ms_2018_{arm}_levelling_up"
                           / "levelling_up_runs.csv")
        mean = runs.groupby("arm").mean(numeric_only=True)
        got = {
            "dp_base": mean.loc["baseline", "dp_diff"],
            "dp_plain": mean.loc["expgrad_dp", "dp_diff"],
            "pie": mean.loc["expgrad_dp", "positives_pct_change"],
            "exchange": mean.loc["expgrad_dp", "lost_per_gained"],
        }
        for key, value in expected.items():
            assert abs(got[key] - value) < 0.01, (
                f"docs/22 says {arm} {key} = {value}, data gives {got[key]:.4f}"
            )
        # The direction is the finding. Both must hold, in both arms.
        assert got["pie"] > 0, (
            f"docs/22 claims the {arm} arm GROWS the pie; it now shrinks it ({got['pie']:+.2f}%)"
        )
        assert got["exchange"] < 1, (
            f"docs/22 claims the {arm} arm creates more than it destroys; "
            f"exchange is now {got['exchange']:.3f}"
        )
        # Not noise: the effect must clear the across-seed spread.
        spread = runs.groupby("arm")["positives_pct_change"].std()["expgrad_dp"]
        assert abs(got["pie"]) > 2 * spread, (
            f"docs/22 rests on the {arm} effect ({got['pie']:+.2f}%) clearing its "
            f"across-seed spread ({spread:.2f}); it no longer does"
        )
    print("  both HMDA arms level up, effects clear 2x their seed spread")


def test_doc23_threshold_sweep() -> None:
    """docs/23: the single-factor sweep, recomputed through the analysis module."""
    from src.experiments.analyse_threshold import (
        MIN_BASELINE_GAP, attach_selection_rate, load, partial_corr,
    )

    text = _doc(23)
    _quotes(text, "+0.801", "+0.980", "-0.874", "-0.408", "-29.71%", "+0.08%",
            "22.03", "0.75", "-0.994", "+30.93", "0.890", "0.030")

    cutoffs = [10_000, 20_000, 30_000, 50_000, 70_000, 100_000]
    frame = attach_selection_rate(load(["AL"], cutoffs), ["AL"])
    assert len(frame) == 6, f"docs/23 reports six arms per state, found {len(frame)}"
    kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
    assert len(kept) == 4, f"docs/23 reports four non-degenerate arms, found {len(kept)}"

    # Oregon replicates it, and is the stronger of the two despite starting nearer the
    # crossover. Asserted separately so a regression in either state is attributable.
    oregon = attach_selection_rate(load(["OR"], cutoffs), ["OR"])
    or_kept = oregon[oregon["dp_base"] >= MIN_BASELINE_GAP]
    assert len(or_kept) == 4, f"docs/23 reports four Oregon arms, found {len(or_kept)}"
    _quotes(text, "+0.964", "+0.994", "-0.993", "-0.995")
    for name, got, documented in (
        ("OR T1", np.corrcoef(or_kept["selection_rate"], or_kept["pie_plain"])[0, 1], 0.964),
        ("OR T2", partial_corr(or_kept["selection_rate"], or_kept["pie_plain"],
                               or_kept["dp_base"]), 0.994),
        ("OR T3", np.corrcoef(or_kept["selection_rate"],
                              or_kept["exchange_plain"])[0, 1], -0.993),
        ("OR floor", np.corrcoef(oregon["pie_plain"],
                                 oregon["pie_floor"] - oregon["pie_plain"])[0, 1], -0.995),
    ):
        assert abs(got - documented) < 0.005, (
            f"docs/23 says {name} = {documented:+.3f}, data gives {got:+.3f}")
    or_low = oregon.loc[or_kept["selection_rate"].idxmin()]
    or_high = oregon.loc[or_kept["selection_rate"].idxmax()]
    assert or_low["pie_plain"] < 0 < or_high["pie_plain"], (
        "docs/23 claims the direction flips in Oregon too; it no longer does")

    checks = {
        "T1 r(rate, pie)": (np.corrcoef(kept["selection_rate"], kept["pie_plain"])[0, 1], 0.801),
        "T2 partial r": (partial_corr(kept["selection_rate"], kept["pie_plain"],
                                      kept["dp_base"]), 0.980),
        "T3 r(rate, exchange)": (np.corrcoef(kept["selection_rate"],
                                             kept["exchange_plain"])[0, 1], -0.874),
        "confound r(rate, gap)": (np.corrcoef(kept["selection_rate"],
                                              kept["dp_base"])[0, 1], -0.408),
        "floor tracks the damage": (np.corrcoef(frame["pie_plain"],
                                                frame["pie_floor"] - frame["pie_plain"])[0, 1],
                                    -0.994),
    }
    for name, (got, documented) in checks.items():
        assert abs(got - documented) < 0.005, (
            f"docs/23 says {name} = {documented:+.3f}, data gives {got:+.3f}"
        )

    # The sign change is the finding; a correlation without it is a much weaker claim.
    low = frame.loc[kept["selection_rate"].idxmin()]
    high = frame.loc[kept["selection_rate"].idxmax()]
    assert low["pie_plain"] < 0 < high["pie_plain"], (
        "docs/23 rests on the direction flipping across the selection-rate range; "
        f"it no longer does ({low['pie_plain']:+.2f} to {high['pie_plain']:+.2f})"
    )
    # Every arm must be the same population -- that is what makes it single-factor.
    assert frame["n_test"].nunique() == 1, (
        "docs/23 claims the arms differ only in the label; the test sizes now differ"
    )
    print(f"  6 arms, selection rate {frame['selection_rate'].min():.3f}-"
          f"{frame['selection_rate'].max():.3f}, sign flips, partial r "
          f"{checks['T2 partial r'][0]:+.3f}")


def test_doc24_group_ratio_refuted() -> None:
    """docs/24: G2 failed, with the opposite sign, and G1/G4 held."""
    from src.experiments.analyse_ratio import (
        MIN_BASELINE_GAP, DEFAULT_STATES, THRESHOLDS, load, partial_corr)

    text = _doc(24)
    _quotes(text, "+0.535", "+0.484", "-0.990", "+0.969", "+0.933", "+0.874", "+0.991")
    frame = load(DEFAULT_STATES, THRESHOLDS)
    assert len(frame) == 20, f"docs/24 reports 20 arms, found {len(frame)}"
    kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
    assert len(kept) == 14, f"docs/24 reports 14 non-degenerate arms, found {len(kept)}"

    g2 = partial_corr(kept["log_ratio"], kept["pie_plain"], kept["selection_rate"])
    assert abs(g2 - 0.535) < 0.005, f"docs/24 says G2 partial r = +0.535, data gives {g2:+.3f}"
    # The finding is that it failed *with the wrong sign*. If it ever comes out negative the
    # document is describing a refutation that no longer happened.
    assert g2 > 0, f"docs/24 records G2 failing with the opposite sign; it is now {g2:+.3f}"

    rescued = frame["pie_floor"] - frame["pie_plain"]
    g4 = float(np.corrcoef(frame["pie_plain"], rescued)[0, 1])
    assert abs(g4 - (-0.990)) < 0.005, f"docs/24 says G4 r = -0.990, data gives {g4:+.3f}"
    print(f"  G2 {g2:+.3f} (failed, wrong sign as documented); G4 {g4:+.3f}")


def test_doc25_baseline_comparison() -> None:
    """docs/25: the optimal DP classifier levels down too, and minimax is worse."""
    text = _doc(25)
    _quotes(text, "-18.83%", "2.48", "0.0050", "-10.01%", "46.71", "+33.66%", "+4.26%")
    expected = {
        "adult_baselines": {"group_thresholds": (-18.83, 2.48), "minimax": (1.45, 0.49)},
        "hmda_ms_2018_race_baselines": {"group_thresholds": (0.84, 0.82),
                                        "minimax": (-10.01, 46.71)},
        "acs_income_al_2018_baselines": {"minimax": (33.66, 0.03)},
    }
    for name, arms in expected.items():
        runs = pd.read_csv(RESEARCH / name / "baselines_runs.csv")
        mean = runs.groupby("arm").mean(numeric_only=True)
        for arm, (pie, exchange) in arms.items():
            got_pie = mean.loc[arm, "positives_pct_change"]
            got_ex = mean.loc[arm, "lost_per_gained"]
            assert abs(got_pie - pie) < 0.05, (
                f"docs/25 says {name}/{arm} pie = {pie}, data gives {got_pie:.2f}")
            assert abs(got_ex - exchange) < 0.05, (
                f"docs/25 says {name}/{arm} exchange = {exchange}, data gives {got_ex:.2f}")
    # The load-bearing claim: on Adult the *optimal* classifier levels down too.
    adult = pd.read_csv(RESEARCH / "adult_baselines" / "baselines_runs.csv") \
        .groupby("arm").mean(numeric_only=True)
    assert adult.loc["group_thresholds", "positives_pct_change"] < -10, (
        "docs/25 rests on the optimal DP classifier also levelling down substantially")
    print("  optimal classifier levels down; minimax destroys 10% on HMDA at 46.7")


def test_doc26_derivation_beaten_by_a_constant() -> None:
    """docs/26: M1 passes its bar and is beaten by a constant. Both must stay true."""
    text = _doc(26)
    _quotes(text, "12/14", "13/14", "-0.802", "-0.182", "+0.901")
    frame = pd.read_csv(RESEARCH / "mechanism" / "mechanism_heldout.csv")
    assert len(frame) == 14, f"docs/26 reports 14 held-out populations, found {len(frame)}"

    derived = (frame["rbar"] > frame["mode_rate"]) == (frame["lambda_minus_p"] > 0)
    naive = (frame["rbar"] > 0.5) == (frame["lambda_minus_p"] > 0)
    assert int(derived.sum()) == 12, f"docs/26 says the derived rule gets 12/14, got {int(derived.sum())}"
    assert int(naive.sum()) == 13, f"docs/26 says the constant gets 13/14, got {int(naive.sum())}"
    # The whole point is that the constant WINS. If that ever flips, the document is wrong.
    assert naive.sum() > derived.sum(), (
        "docs/26 records the derivation being beaten by a constant rule; it no longer is")

    r_mode = float(np.corrcoef(frame["rbar"], frame["mode_rate"])[0, 1])
    assert abs(r_mode - (-0.802)) < 0.005, (
        f"docs/26 says r(rbar, mode) = -0.802, data gives {r_mode:+.3f}")
    print(f"  derived {int(derived.sum())}/14 beaten by constant {int(naive.sum())}/14")


def test_doc27_theory_correspondence() -> None:
    """docs/27: their conditions never hold, and the selection rate proxies theirs."""
    text = _doc(27)
    _quotes(text, "+0.927", "24 / 26", "25 / 26")
    frame = pd.read_csv(RESEARCH / "zeta" / "zeta_correspondence.csv")
    assert len(frame) == 26, f"docs/27 reports 26 populations, found {len(frame)}"

    obs = frame["pie"] > 0
    zeta_rule = frame["A_max_q"] > frame["B_max_q"]
    rate_rule = frame["rate"] > 0.5
    assert int((zeta_rule == obs).sum()) == 24, "docs/27 says the relaxed rule gets 24/26"
    assert int((zeta_rule == rate_rule).sum()) == 25, "docs/27 says the two rules agree 25/26"

    r = float(np.corrcoef(frame["rate"], frame["A_max_q"] - frame["B_max_q"])[0, 1])
    assert abs(r - 0.927) < 0.005, f"docs/27 says r = +0.927, data gives {r:+.3f}"
    print(f"  relaxed rule 24/26, agrees with rate rule 25/26, r = {r:+.3f}")


def main() -> None:
    tests = [
        test_doc11_cross_flow_correlations,
        test_doc12_intersectional_condition,
        test_doc13_partial_correlations,
        test_doc14_endpoint_independence,
        test_doc15_arbitrariness,
        test_doc16_and_17_injection_tables,
        test_doc19_levelling_up,
        test_doc20_share_decomposition,
        test_doc21_floor_replication,
        test_doc22_hmda_levels_up,
        test_doc23_threshold_sweep,
        test_doc24_group_ratio_refuted,
        test_doc25_baseline_comparison,
        test_doc26_derivation_beaten_by_a_constant,
        test_doc27_theory_correspondence,
        test_course_documents_still_match_their_results,
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
