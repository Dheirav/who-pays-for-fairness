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
    assert len(pooled) == 19, f"docs/13 claims 19 arms, file has {len(pooled)}"
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
    assert len(combined) == 19, f"docs/21 claims 19 arms, got {len(combined)}"
    assert int((combined["exchange_floor"] < 1).sum()) == 16, "docs/21 states 16 of 19 under 1.0"
    assert int((combined["exchange_plain"] < 1).sum()) == 1, "docs/21 states 1 of 19 under 1.0 plain"
    assert int((combined["pie_floor"] < 0).sum()) == 1, "docs/21 states only Adult still shrinks"
    assert combined.loc["Adult", "pie_plain"].mean() < combined[
        combined.index != "Adult"]["pie_plain"].mean(), "docs/21 claims Adult is the extreme case"
    print(f"  19 arms from 10 populations; L3 unanimous, L2 failed as documented; "
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
    _quotes(text, "12/14", "13/14", "-0.802", "-0.182", "+0.901",
            "fourteen arms from four populations")
    frame = pd.read_csv(RESEARCH / "mechanism" / "mechanism_heldout.csv")
    assert len(frame) == 14, f"docs/26 reports 14 held-out arms, found {len(frame)}"
    populations = frame["name"].str.extract(r"^((?:acs_income|hmda)_[a-z]{2})")[0].nunique()
    assert populations == 4, (
        f"docs/26's 14 arms come from 4 populations, found {populations}; the document's "
        "wording about independence depends on that")

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
    _quotes(text, "+0.935", "24 / 26", "25 / 26")
    frame = pd.read_csv(RESEARCH / "zeta" / "zeta_correspondence.csv")
    assert len(frame) == 26, f"docs/27 reports 26 arms, found {len(frame)}"
    # docs/27's headline count is arms, not populations: nine rows are income-cutoff variants
    # and four are two HMDA states under two attributes each. Arms of one population share
    # their rows, so fifteen is the number that governs independence.
    import re as _re
    _pops = {_re.sub(r"_(race|sex)$", "", _re.sub(r"_t\d+$", "", n))
             for n in frame.iloc[:, 0]}
    assert len(_pops) == 15, (
        f"docs/27 says its 26 arms come from 15 populations, found {len(_pops)}: "
        f"{sorted(_pops)}")

    obs = frame["pie"] > 0
    zeta_rule = frame["A_max_q"] > frame["B_max_q"]
    rate_rule = frame["rate"] > 0.5
    assert int((zeta_rule == obs).sum()) == 24, "docs/27 says the relaxed rule gets 24/26"
    assert int((zeta_rule == rate_rule).sum()) == 25, "docs/27 says the two rules agree 25/26"

    r = float(np.corrcoef(frame["rate"], frame["A_max_q"] - frame["B_max_q"])[0, 1])
    assert abs(r - 0.935) < 0.005, f"docs/27 says r = +0.935, data gives {r:+.3f}"
    print(f"  relaxed rule 24/26, agrees with rate rule 25/26, r = {r:+.3f}")


def test_doc31_natural_split() -> None:
    """docs/31: the crossover on a natural split, and the discrepancy it exposes."""
    from src.experiments.analyse_purpose import PURPOSES, load
    from scipy import stats

    text = _doc(31)
    _quotes(text, "+0.803", "+0.900", "-1.57%", "+2.95%", "0.555", "0.871")
    frame = load(PURPOSES)
    assert len(frame) == 5, f"docs/31 reports five purpose arms, found {len(frame)}"
    frame["rate"] = frame["positives_base"] / frame["n_test"]

    r = float(np.corrcoef(frame["rate"], frame["pie_plain"])[0, 1])
    rho = float(stats.spearmanr(frame["rate"], frame["pie_plain"]).statistic)
    assert abs(r - 0.803) < 0.005, f"docs/31 says r = +0.803, data gives {r:+.3f}"
    assert abs(rho - 0.900) < 0.005, f"docs/31 says rho = +0.900, data gives {rho:+.3f}"

    # The load-bearing observation: a natural population that levels DOWN, which is what
    # makes the crossover observed rather than manufactured. If it ever turns positive the
    # document is describing something that did not happen.
    low = frame.loc[frame["rate"].idxmin()]
    high = frame.loc[frame["rate"].idxmax()]
    assert low["pie_plain"] < 0, (
        f"docs/31 rests on the lowest-rate natural arm levelling DOWN; "
        f"it is now {low['pie_plain']:+.2f}%")
    assert high["pie_plain"] > 0, "docs/31 rests on the highest-rate arm levelling up"

    # The discrepancy docs/31 reports: this crossover does NOT fall inside docs/23's band.
    negative = frame[frame["pie_plain"] < 0]["rate"].max()
    positive = frame[frame["pie_plain"] > 0]["rate"].min()
    assert negative > 0.60, (
        "docs/31 reports its crossover sitting ABOVE docs/23's 0.25-0.60 band; it no longer "
        f"does (last negative arm at {negative:.3f})")
    print(f"  natural crossover between {negative:.3f} and {positive:.3f}; "
          f"r={r:+.3f} rho={rho:+.3f}; lowest arm {low['pie_plain']:+.2f}%")


def test_doc32_rate_not_task() -> None:
    """docs/32: moving only the decision rule reproduces direction AND crossover location."""
    from src.experiments.analyse_operating_point import (
        OPERATING_POINTS, crossover_bracket, load_cutoffs, load_operating_points)
    from src.experiments.analyse_threshold import MIN_BASELINE_GAP, MIN_R

    text = _doc(32)
    _quotes(text, "+0.979", "+0.996", "-6.63%", "+2.98%", "-22.05%")

    ops = load_operating_points("AL", OPERATING_POINTS)
    cuts = load_cutoffs("AL")
    assert len(ops) == 6, f"docs/32 reports six operating-point arms, found {len(ops)}"
    for frame in (ops, cuts):
        frame["selection_rate"] = frame["positives_base"] / frame["n_test"]

    # The denominator bug this document records: if the cutoff rates come back NaN the
    # crossover comparison silently reports "disjoint" for a bracket it never computed.
    assert cuts["selection_rate"].notna().all(), (
        "docs/32's O3 needs selection rates for the income-cutoff arms; they are NaN again, "
        "which is the exact failure the document's methods note describes")

    kept = ops[ops["dp_base"] >= MIN_BASELINE_GAP]
    assert len(kept) == 4, f"docs/32 retains four arms under docs/23's rule, found {len(kept)}"

    r = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
    assert abs(r - 0.979) < 0.005, f"docs/32 says r = +0.979, data gives {r:+.3f}"

    # O3, the load-bearing claim: the two routes must still bracket the crossover together.
    op_band = crossover_bracket(kept)
    cut_band = crossover_bracket(cuts[cuts["dp_base"] >= MIN_BASELINE_GAP])
    assert op_band is not None and cut_band is not None, "a route stopped bracketing a flip"
    assert op_band[0] <= cut_band[1] and cut_band[0] <= op_band[1], (
        f"docs/32 rests on the two routes AGREEING on where the crossover sits; "
        f"operating point {op_band} no longer overlaps income cutoff {cut_band}")

    # And the honest half: direction transfers, magnitude does not.
    low_op = kept.loc[kept["selection_rate"].idxmin(), "pie"]
    low_cut = cuts.loc[cuts["selection_rate"].sub(0.099).abs().idxmin(), "pie"]
    assert low_op < 0 and low_cut < 0, "docs/32's lowest retained arms both level down"
    assert abs(low_cut) > 2 * abs(low_op), (
        "docs/32 reports the cutoff route producing a far larger effect at the low end "
        f"({low_cut:+.2f}% against {low_op:+.2f}%); that gap has closed")
    # Oregon replicates it, and the two states do NOT share a crossover -- which is the
    # claim that stops "0.25 to 0.60" being quoted as a constant.
    or_ops = load_operating_points("OR", OPERATING_POINTS)
    or_cuts = load_cutoffs("OR")
    for f in (or_ops, or_cuts):
        f["selection_rate"] = f["positives_base"] / f["n_test"]
    or_kept = or_ops[or_ops["dp_base"] >= MIN_BASELINE_GAP]
    r_or = float(np.corrcoef(or_kept["selection_rate"], or_kept["pie"])[0, 1])
    assert abs(r_or - 0.855) < 0.005, f"docs/32 says Oregon r = +0.855, got {r_or:+.3f}"

    or_op_band = crossover_bracket(or_kept)
    or_cut_band = crossover_bracket(or_cuts[or_cuts["dp_base"] >= MIN_BASELINE_GAP])
    assert or_op_band is not None and or_cut_band is not None
    assert or_op_band[0] <= or_cut_band[1] and or_cut_band[0] <= or_op_band[1], (
        f"docs/32 rests on the routes agreeing within Oregon too; "
        f"{or_op_band} no longer overlaps {or_cut_band}")

    # Route-invariant but population-specific: Oregon's crossover must sit ABOVE Alabama's.
    assert or_op_band[0] > op_band[0], (
        f"docs/32 reports Oregon's crossover sitting higher than Alabama's "
        f"({or_op_band} against {op_band}); that difference is why the band is not a constant")
    # Five populations, and the document now claims 4/5 on direction and 3/5 on location.
    # The exceptions are pinned: if Kentucky starts agreeing or Connecticut starts flipping,
    # the document is describing outcomes that no longer happened.
    outcomes = {}
    for state in ["AL", "OR", "CT", "KY", "SC"]:
        o = load_operating_points(state, OPERATING_POINTS)
        c = load_cutoffs(state)
        if c["n_test"].isna().any() and o["n_test"].notna().any():
            c["n_test"] = c["n_test"].fillna(o["n_test"].dropna().iloc[0])
        for f in (o, c):
            f["selection_rate"] = f["positives_base"] / f["n_test"]
        ok = o[o["dp_base"] >= MIN_BASELINE_GAP]
        ck = c[c["dp_base"] >= MIN_BASELINE_GAP]
        ob, cb = crossover_bracket(ok), crossover_bracket(ck)
        agree = None if ob is None or cb is None else (ob[0] <= cb[1] and cb[0] <= ob[1])
        outcomes[state] = (float(np.corrcoef(ok["selection_rate"], ok["pie"])[0, 1]), agree)

    assert outcomes["CT"][1] is None, (
        "docs/32 reports Connecticut having no sign change to bracket; it now has one")
    assert outcomes["KY"][1] is False, (
        f"docs/32 reports Kentucky's two routes DISAGREEING; they now agree. The document "
        f"claims 3/5, and turning a recorded failure into a pass is what the "
        f"pre-registration exists to prevent")
    assert sum(1 for r, a in outcomes.values() if a is True) == 3, (
        f"docs/32 claims the routes agree in three populations of five: {outcomes}")
    assert outcomes["CT"][0] < MIN_R, "docs/32 reports O1 failing on Connecticut"
    _quotes(text, "three of five", "DISJOINT", "+0.633")
    print(f"  AL {r:+.3f}, OR {r_or:+.3f}; agree 3/5, KY disjoint, CT no flip")


def test_doc33_eo_scope_condition() -> None:
    """docs/33: the rule FAILS its primary bar under equalized odds, and must keep failing."""
    from src.experiments.analyse_eo import MIN_BINDING, MIN_SPAN_PIE, load
    from src.experiments.analyse_threshold import MIN_BASELINE_GAP, MIN_R, THRESHOLDS

    text = _doc(33)
    _quotes(text, "+0.644", "+0.775", "-0.748", "+0.160", "+0.822", "+0.03%")

    frame = load(["AL", "OR"], THRESHOLDS)          # pinned to the pre-registered archive
    assert len(frame) == 12, f"docs/33 reports twelve arms, found {len(frame)}"
    kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
    assert len(kept) == 8, f"docs/33 retains eight arms, found {len(kept)}"

    r_eo = float(np.corrcoef(kept["selection_rate"], kept["pie_eo"])[0, 1])
    assert abs(r_eo - 0.644) < 0.005, f"docs/33 says r = +0.644, data gives {r_eo:+.3f}"

    # The load-bearing claim is a FAILURE. If a later re-run pushes this over the bar, the
    # document is describing an outcome that no longer happened -- and quietly turning a
    # reported failure into a pass is exactly what the pre-registration exists to prevent.
    assert r_eo < MIN_R, (
        f"docs/33 reports E1 FAILING at a bar of {MIN_R}; r is now {r_eo:+.3f}. The "
        "document must be rewritten rather than left claiming a failure that has gone away")

    binding = float(kept["eo_reduction"].median())
    assert binding < MIN_BINDING, (
        f"docs/33 reports E0's binding half failing; median reduction is now {binding:+.3f}")
    assert float(kept["pie_eo"].max() - kept["pie_eo"].min()) >= MIN_SPAN_PIE, \
        "docs/33 reports the spread half of E0 HOLDING"

    # And the comparison that gives the failure its meaning: present but weaker than parity.
    paired = kept.dropna(subset=["pie_dp"])
    r_dp = float(np.corrcoef(paired["selection_rate"], paired["pie_dp"])[0, 1])
    assert r_dp > r_eo, (
        f"docs/33 rests on parity predicting BETTER than equalized odds on the same arms; "
        f"parity {r_dp:+.3f} against {r_eo:+.3f}")
    assert r_eo > 0.30, (
        "docs/33 says the naive 'predicts nothing' alternative is still beaten at 0.30")
    print(f"  E1 fails at {r_eo:+.3f} (bar {MIN_R}); parity {r_dp:+.3f} on the same "
          f"{len(paired)} arms; binding {binding:+.3f}")


def test_doc34_epsilon_robustness() -> None:
    """docs/34: the crossover bracket must stay put across a 25x range of epsilon."""
    from src.experiments.analyse_threshold import (
        MIN_BASELINE_GAP, MIN_R, THRESHOLDS, attach_selection_rate, load)

    text = _doc(34)
    _quotes(text, "+0.944", "+0.801", "+0.784", "-4.97%", "-22.16%", "0.252")

    brackets = {}
    for suffix, label in [("_eps005", 0.05), ("", 0.01), ("_eps0002", 0.002)]:
        frame = attach_selection_rate(load(["AL"], THRESHOLDS, suffix), ["AL"])
        assert len(frame) == 6, f"docs/34 needs six arms at eps={label}, found {len(frame)}"
        kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
        assert len(kept) == 4, f"docs/34 retains four arms at eps={label}, got {len(kept)}"
        r = float(np.corrcoef(kept["selection_rate"], kept["pie_plain"])[0, 1])
        assert r >= MIN_R, f"docs/34 reports T1 holding at eps={label}; r is {r:+.3f}"
        below = kept[kept["pie_plain"] < 0]["selection_rate"].max()
        above = kept[kept["pie_plain"] > 0]["selection_rate"].min()
        assert below < above, f"docs/34 needs a sign flip at eps={label}"
        brackets[label] = (round(below, 4), round(above, 4))

    # The load-bearing claim: the bracket does not move with the tolerance. If it ever does,
    # the direction result IS partly a property of the hyperparameter and docs/23, 31 and 32
    # all need the caveat added.
    assert len(set(brackets.values())) == 1, (
        f"docs/34 rests on the crossover bracket being identical across epsilon; "
        f"it now differs: {brackets}")

    # Four of five states hold at every tolerance; Connecticut fails all three on a spread
    # of 0.34 points. Both halves are pinned.
    _quotes(text, "Four of five hold at every tolerance", "0.34")
    verdicts = {}
    for state in ["OR", "CT", "KY", "SC"]:
        rs, spread = [], None
        for suffix in ("_eps005", "", "_eps0002"):
            f = attach_selection_rate(load([state], THRESHOLDS, suffix), [state])
            if f["n_test"].isna().any():
                ref = attach_selection_rate(load([state], THRESHOLDS, "_eps005"), [state])
                f["n_test"] = f["n_test"].fillna(ref["n_test"].dropna().iloc[0])
                f["selection_rate"] = f["positives_base"] / f["n_test"]
            k = f[f["dp_base"] >= MIN_BASELINE_GAP]
            rs.append(float(np.corrcoef(k["selection_rate"], k["pie_plain"])[0, 1]))
            spread = float(k["pie_plain"].max() - k["pie_plain"].min())
        verdicts[state] = (all(x >= MIN_R for x in rs), spread)

    assert verdicts["CT"][0] is False and verdicts["CT"][1] < 2.0, (
        f"docs/34 reports Connecticut failing on a spread under 2 points: {verdicts['CT']}")
    holding = [s for s, (ok, _) in verdicts.items() if ok] + ["AL"]
    assert sorted(holding) == ["AL", "KY", "OR", "SC"], (
        f"docs/34 claims four of five populations hold at every tolerance; got {verdicts}")
    print(f"  bracket {brackets[0.01]} identical across eps; AL/OR/KY/SC hold, "
          f"CT fails on a {verdicts['CT'][1]:.2f}-point spread")


def test_doc36_second_learner() -> None:
    """docs/36: the crossover must not move when the base learner changes."""
    from src.experiments.analyse_threshold import (
        MIN_BASELINE_GAP, MIN_R, THRESHOLDS, attach_selection_rate, load)

    text = _doc(36)
    _quotes(text, "+0.902", "+1.000", "-21.14%", "+0.92%", "-7.00%")

    hgb = attach_selection_rate(load(["AL"], THRESHOLDS, "_hgb"), ["AL"])
    assert len(hgb) == 4, f"docs/36 reports four boosted-tree arms, found {len(hgb)}"
    r = float(np.corrcoef(hgb["selection_rate"], hgb["pie_plain"])[0, 1])
    assert abs(r - 0.902) < 0.005, f"docs/36 says r = +0.902, data gives {r:+.3f}"
    assert r >= MIN_R, "docs/36 reports T1 holding under the boosted learner"

    def bracket(frame):
        below = frame[frame["pie_plain"] < 0]["selection_rate"].max()
        above = frame[frame["pie_plain"] > 0]["selection_rate"].min()
        assert below < above, "no sign flip"
        return below, above

    # The load-bearing claim: same crossover as the linear model on the same four arms.
    lr = attach_selection_rate(load(["AL"], THRESHOLDS), ["AL"])
    lr = lr[lr["threshold"].isin(hgb["threshold"])]
    assert lr["dp_base"].min() >= MIN_BASELINE_GAP, "the compared arms should all be retained"
    b_hgb, b_lr = bracket(hgb), bracket(lr)
    assert b_hgb[0] <= b_lr[1] and b_lr[0] <= b_hgb[1], (
        f"docs/36 rests on the crossover NOT moving with the learner; boosted {b_hgb} no "
        f"longer overlaps linear {b_lr}")

    # And the stated surprise: the stronger learner starts off MORE unfair, not less.
    assert hgb["dp_base"].mean() > lr["dp_base"].mean(), (
        "docs/36 reports the boosted learner producing larger baseline parity gaps")
    # The document's strongest claim: this is the one test that holds in every population.
    _quotes(text, "Five of five")
    per_state = {}
    for state in ["OR", "CT", "KY", "SC"]:
        f = attach_selection_rate(load([state], THRESHOLDS, "_hgb"), [state])
        k = f[f["dp_base"] >= MIN_BASELINE_GAP]
        rr = float(np.corrcoef(k["selection_rate"], k["pie_plain"])[0, 1])
        flip = k[k["pie_plain"] < 0]["selection_rate"].max() < \
            k[k["pie_plain"] > 0]["selection_rate"].min()
        per_state[state] = (rr, bool(flip))
    assert all(rr >= MIN_R and flip for rr, flip in per_state.values()), (
        f"docs/36 claims five of five; the boosted learner now fails somewhere: {per_state}")
    # Connecticut is the point of the section: it flips here where the linear model does not.
    assert per_state["CT"][1], (
        "docs/36 rests on Connecticut flipping under boosted trees where it does not "
        "under logistic regression")
    print(f"  r = {r:+.3f}; boosted crossover {b_hgb[0]:.3f}-{b_hgb[1]:.3f} vs "
          f"linear {b_lr[0]:.3f}-{b_lr[1]:.3f}; 5/5 states hold incl. CT")


def test_doc37_spread_guard_audit() -> None:
    """docs/37: no arm set may ever PASS T1 on a spread below the guard."""
    from src.experiments.analyse_threshold import (
        MIN_BASELINE_GAP, MIN_R, MIN_SPAN_PIE, THRESHOLDS, attach_selection_rate, load)

    text = _doc(37)
    _quotes(text, "2.0-point spread", "-0.924", "0.10", "2.03", "Twenty arm sets")
    assert MIN_SPAN_PIE == 2.0, "docs/37 documents a 2.0-point guard"

    scored, void, passed_on_noise = 0, [], []
    for suffix in ("", "_eps005", "_eps0002", "_hgb"):
        for state in ["AL", "OR", "CT", "KY", "SC"]:
            frame = load([state], THRESHOLDS, suffix)
            if len(frame) < 3:
                continue
            frame = attach_selection_rate(frame, [state])
            kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
            if len(kept) < 3 or kept["selection_rate"].isna().any():
                continue
            scored += 1
            r = float(np.corrcoef(kept["selection_rate"], kept["pie_plain"])[0, 1])
            spread = float(kept["pie_plain"].max() - kept["pie_plain"].min())
            if spread < MIN_SPAN_PIE:
                void.append((state, suffix or "_eps001", round(r, 3), round(spread, 2)))
                if r >= MIN_R:
                    passed_on_noise.append((state, suffix, r, spread))

    # The load-bearing assertion. A conclusion resting on a correlation fitted to a
    # sub-threshold spread is the failure mode T1's missing guard allowed, and docs/37's
    # whole finding is that it never happened. If one appears, something is now wrong.
    assert not passed_on_noise, (
        f"docs/37 reports that NO arm set ever passed T1 on a spread under "
        f"{MIN_SPAN_PIE} points; these now do: {passed_on_noise}")
    assert scored == 20, f"docs/37 audits twenty arm sets, found {scored}"
    assert len(void) == 3 and {v[0] for v in void} == {"CT"}, (
        f"docs/37 reports three void arm sets, all Connecticut: {void}")
    print(f"  {scored} arm sets audited; {len(void)} void (all CT); none passed on noise")


def test_doc38_population_counts_are_recomputed() -> None:
    """docs/38: every 'N populations' claim must match the file it comes from.

    Three counts in this project were arm counts wearing a population label, and each was
    found only when something else forced a look at the underlying file. Reading the
    documents never caught it -- they are internally consistent and all repeat the same
    wrong number. So the counts are recomputed here rather than checked against prose.
    """
    import re as _re

    text = _doc(38)
    _quotes(text, "19 arms from 10 populations", "26 arms from 15 populations")

    def populations(names) -> int:
        """Distinct sets of *people*: strip the label and the grouping, keep the source."""
        return len({_re.sub(r"_(rac1p|race|sex)$", "", _re.sub(r"_t\d+", "", str(n)))
                    for n in names})

    pooled = pd.read_csv(RESEARCH / "sweep" / "arms_p1_pooled.csv")
    assert len(pooled) == 19, f"docs/38's nineteen is 19 arms, found {len(pooled)}"
    per_arm = pooled.groupby("arm")["population"].nunique().to_dict()
    assert populations(pooled["population"]) == 10, (
        f"docs/38 says the 19 arms come from 10 populations, found "
        f"{populations(pooled['population'])}")
    assert per_arm == {"SEX": 10, "RAC1P": 9}, (
        f"docs/38 describes nine ACS states under both attributes plus Adult under one; "
        f"the split is now {per_arm}")

    zeta = pd.read_csv(RESEARCH / "zeta" / "zeta_correspondence.csv")
    assert len(zeta) == 26, f"docs/38's twenty-six is 26 arms, found {len(zeta)}"
    assert populations(zeta.iloc[:, 0]) == 15, (
        f"docs/38 says the 26 arms come from 15 populations, found "
        f"{populations(zeta.iloc[:, 0])}")

    # The tell docs/38 records: the abstract cannot claim the nineteen AND both arms.
    frame = (ROOT / "research" / "PAPER.md").read_text()
    assert "19 populations and in both protected-attribute arms" not in frame, (
        "PAPER.md's abstract double-counts again: the nineteen ARE the two attribute arms")
    print(f"  19 arms/10 populations and 26 arms/15 populations, recomputed from source")


def test_doc40_accuracy_rule_and_its_withdrawals() -> None:
    """docs/40: the exclusion must keep withdrawing what it withdrew and rescuing lending."""
    from src.experiments.analyse_calibration import apply_rules, majority_baseline
    from src.experiments.analyse_operating_point import (
        HMDA_POINTS, OPERATING_POINTS, crossover_bracket, load_points_for)
    from src.experiments.analyse_threshold import MIN_R

    text = _doc(40)
    _quotes(text, "+0.979", "VOID", "+0.858", "0.620", "+0.995", "worse than doing nothing")

    def scored(spec, name, points):
        ops = load_points_for(name, points)
        kept, counts = apply_rules(ops, majority_baseline(spec))
        if len(kept) < 3:
            return None, counts
        r = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
        return (r, crossover_bracket(kept)), counts

    # The two withdrawals. If either comes back, docs/32 and docs/39 are describing results
    # that no longer hold, and a withdrawn number quietly returning is the worse failure.
    for spec, name, pts, label in [
        ("acs:AL", "acs_income_al_2018", OPERATING_POINTS, "Alabama"),
        ("lawschool", "lawschool_race",
         [0.60, 0.90, 0.95, 0.975, 0.99, 0.995], "LSAC")]:
        got, counts = scored(spec, name, pts)
        assert got is None, (
            f"docs/40 withdraws {label} as VOID under the accuracy rule; it now scores "
            f"{got} with {counts['n_kept']} arms retained")

    # The rescue: lending fails without the rule and holds with it.
    got, counts = scored("hmda:MS,LA:derived_race", "hmda_ms_la_2018_race", HMDA_POINTS)
    assert got is not None, "docs/40 reports pooled HMDA HOLDING under the rule"
    r, band = got
    assert r >= MIN_R and band is not None, f"docs/40 says HMDA holds at +0.858; got {r:+.3f}"

    # And the convergence that makes it worth something: the operating-point band must
    # overlap document 31's natural-split estimate, which used no manipulation at all.
    natural = (0.643, 0.773)
    assert band[0] <= natural[1] and natural[0] <= band[1], (
        f"docs/40 rests on the swept band {band} overlapping docs/31's natural {natural}")

    # The out-of-sample half scored 2 of 4 and is reported as a FAILURE. Pin the count.
    held = {}
    for spec in ["hmda:MS:derived_race", "hmda:LA:derived_race",
                 "hmda:MS,LA:derived_race:improvement", "hmda:MS,LA:derived_race:refinance"]:
        from src.datasets import build as _build
        got, _ = scored(spec, _build(spec).name, HMDA_POINTS)
        held[spec] = bool(got and got[0] >= MIN_R and got[1] is not None)
    assert sum(held.values()) == 2, (
        f"docs/40 reports A1b passing on two of four populations and scores that a failure; "
        f"it is now {sum(held.values())}: {held}")
    print(f"  AL and LSAC still void; HMDA holds at {r:+.3f}, band {band[0]:.3f}-{band[1]:.3f} "
          f"overlaps docs/31; A1b still 2/4")


def test_doc41_postprocessing_arm_is_void() -> None:
    """docs/41: the post-processing sweep measured a constant, and must keep saying so."""
    from src.experiments.run_levelling_up import model_code
    from src.results_io import RESEARCH_RESULTS_DIR

    text = _doc(41)
    _quotes(text, "1,722", "void", "+0.900")

    positives = []
    for point in [0.02, 0.06, 0.16, 0.49, 0.72, 0.87]:
        path = (RESEARCH_RESULTS_DIR
                / f"acs_income_al_2018_levelling_up_"
                  f"{model_code(f'logistic_regression@{point}')}_post"
                / "levelling_up_runs.csv")
        frame = pd.read_csv(path).groupby("arm").mean(numeric_only=True)
        arm = next(a for a in frame.index if a.startswith("postprocess"))
        positives.append(float(frame.loc[arm, "positives"]))

    # The whole point of docs/41: the post-processed model ignores the operating point, so
    # its output is identical everywhere and the apparent reversal is arithmetic.
    assert max(positives) - min(positives) < 1.0, (
        f"docs/41 reports the post-processed model producing an identical number of "
        f"favourable decisions at every operating point; it now varies: {positives}")
    print(f"  post-processed output constant at {positives[0]:.0f} across all six points")


def _paper_text() -> str | None:
    path = ROOT / "research" / "paper" / "ieee" / "paper.tex"
    return " ".join(path.read_text().split()) if path.exists() else None


def test_paper_ablation_table_matches_results() -> None:
    """tab:ablation is the paper's opening evidence; every cell must follow from Adult.

    Tolerance rather than rounding: two cells sit exactly on a half (0.8265, 0.8365) where
    the paper rounds half up and Python's round() rounds half to even, so an equality test
    on round(x, 3) reports a disagreement that is not there.
    """
    text = _paper_text()
    path = COURSE / "ablation_summary.csv"
    if text is None or not path.exists():
        print("  ablation summary or paper absent; skipping")
        return
    means = pd.read_csv(path, header=[0, 1], index_col=0).xs("mean", axis=1, level=1)
    documented = {
        "baseline": (0.847, 0.186), "expgrad_dp": (0.828, 0.018),
        "gridsearch_dp": (0.827, 0.015), "adversarial_debiasing": (0.826, 0.020),
        "prejudice_remover": (0.837, 0.065), "expgrad_eo": (0.836, 0.107),
    }
    for method, (acc, dp) in documented.items():
        got_acc = float(means.loc[method, "accuracy"])
        got_dp = float(means.loc[method, "demographic_parity_diff"])
        assert abs(got_acc - acc) < 0.001, f"{method}: paper {acc}, data {got_acc:.4f}"
        assert abs(got_dp - dp) < 0.001, f"{method}: paper DP {dp}, data {got_dp:.4f}"
        assert f"${acc:.3f}$" in text or f" {acc:.3f} " in text, \
            f"the paper no longer states {method}'s accuracy {acc}"
    print(f"  {len(documented)} methods re-derived from ablation_summary")


def test_paper_who_pays_figures_match_results() -> None:
    """The rate/people divergence and the exchange rate, which carry Section IV-A."""
    text = _paper_text()
    path = COURSE / "who_pays_summary.csv"
    if text is None or not path.exists():
        print("  who-pays summary or paper absent; skipping")
        return
    frame = pd.read_csv(path).set_index("method")
    rate = frame["dp_share_levelling_down"]
    people = frame["people_share_levelling_down"]
    pool = frame["positives_pct_change"].abs()

    # The paper states these as ranges rounded to two places -- "0.50 to 0.58" is the
    # rounding of 0.498 to 0.575 -- so they are checked to that precision, not tighter.
    assert abs(rate.min() - 0.50) < 0.01 and abs(rate.max() - 0.58) < 0.01, \
        f"rate shares now {rate.min():.3f}-{rate.max():.3f}, paper rounds them to 0.50-0.58"
    assert abs(people.min() - 0.66) < 0.01 and abs(people.max() - 0.74) < 0.01, \
        f"people shares now {people.min():.3f}-{people.max():.3f}, paper rounds them to 0.66-0.74"
    assert abs(pool.min() - 7.9) < 0.1 and abs(pool.max() - 22.1) < 0.1, \
        f"pool shrink range now {pool.min():.1f}-{pool.max():.1f}, paper says 7.9--22.1"
    assert "7.9--22.1" in text, "the paper no longer states the 7.9--22.1% pool range"

    exchange = float(frame.loc["expgrad_dp", "lost_per_gained"])
    assert abs(exchange - 2.68) < 0.005, f"ExpGrad-DP exchange rate is {exchange:.3f}, paper says 2.68"
    assert "2.68" in text, "the paper no longer states the 2.68 exchange rate"
    print(f"  shares {rate.min():.2f}-{rate.max():.2f} (rates) vs {people.min():.2f}-{people.max():.2f} "
          f"(people); exchange {exchange:.2f}")


def test_paper_sealed_cohort_scores_match_results() -> None:
    """Every sealed cohort's score, re-counted from its own stored arms.

    These are the numbers a reader weighs the paper by, and they are exactly the numbers
    that go stale when a cohort is re-run or extended.
    """
    text = _paper_text()
    if text is None:
        print("  paper absent; skipping")
        return
    checks = []

    reseal = RESEARCH / "resealed" / "resealed.csv"
    if reseal.exists():
        f = pd.read_csv(reseal)
        correct = int((f["predicted"] == f["actual"]).sum())
        constant = max(int((f["actual"] == v).sum()) for v in f["actual"].unique())
        checks.append(("re-seal", correct, len(f), constant, "9 of 10"))
        assert (correct, constant) == (9, 6), f"re-seal now {correct}/{len(f)}, constant {constant}"

    seal1 = RESEARCH / "sealed" / "sealed.csv"
    if seal1.exists():
        f = pd.read_csv(seal1)
        f = f[f["held_out"]]
        correct = int((f["predicted"] == f["actual"]).sum())
        checks.append(("seal 1", correct, len(f), None, "four of eight"))
        assert correct == 4 and len(f) == 8, f"seal 1 now {correct}/{len(f)}"

    third = RESEARCH / "third_direction" / "third_direction.csv"
    if third.exists():
        f = pd.read_csv(third)
        s = f[~f["indeterminate"]]
        correct = int((s["predicted"] == s["actual"]).sum())
        constant = max(int((s["actual"] == v).sum()) for v in s["actual"].unique())
        checks.append(("third direction", correct, len(s), constant, "13"))
        assert (correct, len(s), constant) == (13, 14, 9), \
            f"third direction now {correct}/{len(s)}, constant {constant}"

    lending = RESEARCH / "lending_direction" / "lending_direction.csv"
    if lending.exists():
        f = pd.read_csv(lending)
        s = f[~f["indeterminate"]]
        correct = int((s["predicted"] == s["actual"]).sum())
        null = int((s["null_purpose"] == s["actual"]).sum())
        checks.append(("lending", correct, len(s), null, "8 vs 5"))
        assert (correct, null, len(s)) == (8, 5, 8), \
            f"lending now {correct}/{len(s)}, purpose-only null {null}"

    for label, correct, n, other, phrase in checks:
        assert phrase in text, f"the paper no longer states {label}'s score ({phrase!r})"
    print("  " + "; ".join(f"{l} {c}/{n}" for l, c, n, _, _ in checks))


def test_paper_effect_size_split_matches_results() -> None:
    """The 95%/61% split, which turned Algorithm 1's magnitude threshold from assumed to measured."""
    text = _paper_text()
    a = RESEARCH / "third_direction" / "third_direction.csv"
    b = RESEARCH / "lending_direction" / "lending_direction.csv"
    if text is None or not (a.exists() and b.exists()):
        print("  cohorts or paper absent; skipping")
        return
    frame = pd.concat([pd.read_csv(a), pd.read_csv(b)])
    frame["correct"] = frame["predicted"] == frame["actual"]
    above = frame[~frame["indeterminate"]]
    below = frame[frame["indeterminate"]]
    hi = (int(above["correct"].sum()), len(above))
    lo = (int(below["correct"].sum()), len(below))
    assert hi == (21, 22), f"above the guard now {hi[0]}/{hi[1]}, paper says 21 of 22"
    assert lo == (11, 18), f"below the guard now {lo[0]}/{lo[1]}, paper says 11 of 18"
    assert "21 of 22" in text and "11 of 18" in text, \
        "the paper no longer states the effect-size split"
    print(f"  above 1.0 pt: {hi[0]}/{hi[1]}; below: {lo[0]}/{lo[1]}")


def test_paper_denominator_table_matches_computed_independence() -> None:
    """tab:denominators must match what scripts/independence.py computes.

    This table exists because four counts in this project turned out to be arm counts
    presented as population counts. A hand-maintained table of denominators would be the
    fifth, so it is checked against the computed file rather than trusted.
    """
    path = RESEARCH / "independence" / "independence.csv"
    paper = ROOT / "research" / "paper" / "ieee" / "paper.tex"
    if not path.exists() or not paper.exists():
        print("  independence.csv or paper.tex absent; skipping")
        return
    frame = pd.read_csv(path)
    text = " ".join(paper.read_text().split())
    table = text[text.find("label{tab:denominators}"):]
    table = table[:table.find("end{tabular}")]

    rows = {
        "re-seal, unrefined rule": "Re-seal, 9 of 10",
        "third direction cohort": "Third direction, 13 of 14",
        "sealed lending cohort": "Sealed lending, 8 of 8",
        "race cohort S1": "Race cohort, 8 of 10",
        "audit verdict distribution": "Audit verdicts, 29 of 52",
        "landscape survey": "Landscape survey, 78\\%",
    }
    checked = 0
    for what, label in rows.items():
        hit = frame[frame["what"] == what]
        if hit.empty:
            continue
        arms, pops = int(hit.iloc[0]["arms"]), int(hit.iloc[0]["populations"])
        # Parse the row into cells rather than searching the text. An earlier version
        # asserted `str(pops) in segment`, which passed on a deliberately wrong population
        # count because the digit also appeared in the sources column -- a guard that holds
        # for the wrong reason is worse than none.
        assert label in table, f"tab:denominators no longer has a row for {what!r}"
        row = table[table.find(label):]
        row = row[:row.find("\\\\")]                       # up to the row terminator
        cells = [c.strip().replace("\\textbf{", "").replace("}", "")
                 for c in row.split("&")]
        assert len(cells) >= 4, f"{what}: could not parse four cells from {row!r}"
        got_arms, got_pops = cells[1], cells[2]
        assert got_arms == str(arms), (
            f"{what}: table says {got_arms} arms, independence.csv computes {arms}. "
            f"Re-run scripts/independence.py and update tab:denominators.")
        assert got_pops == str(pops), (
            f"{what}: table says {got_pops} populations, independence.csv computes {pops}.")
        checked += 1
    assert checked >= 5, f"only {checked} denominator rows could be checked"
    print(f"  {checked} denominator rows re-derived from independence.csv")


def test_paper_verdict_distribution_matches_the_audit() -> None:
    """Section IX's verdict totals must follow from verdicts.csv.

    This figure drifts silently: every new sweep changes it, and nothing in the paper
    recomputes it. It was already stale once --- the text claimed 27 directional verdicts
    over 45 pairs while the audit returned 29 over 52, because the IPUMS and six-market
    sweeps landed after the paragraph was written. A reader cannot tell a stale total from a
    current one, and the refusal rate is a load-bearing claim about what the procedure is
    worth, so it is asserted rather than trusted.
    """
    path = RESEARCH / "verdicts" / "verdicts.csv"
    paper = ROOT / "research" / "paper" / "ieee" / "paper.tex"
    if not path.exists() or not paper.exists():
        print("  verdicts.csv or paper.tex absent; skipping")
        return
    frame = pd.read_csv(path)
    text = " ".join(paper.read_text().split())      # newline-insensitive matching

    mapped = frame[frame["verdict"] != "UNMAPPED"]
    n_withdrawal = int((mapped["verdict"] == "WITHDRAWAL").sum())
    n_extension = int((mapped["verdict"] == "EXTENSION").sum())
    counts = {
        "mapped pairs": len(mapped),
        "withdrawal": n_withdrawal,
        "extension": n_extension,
        "directional": n_withdrawal + n_extension,
        "non-monotone": int((mapped["verdict"] == "NON-MONOTONE").sum()),
        "void": int(mapped["verdict"].str.startswith("VOID").sum()),
    }

    # Anchored to their actual sites. An earlier version asserted the bare phrase
    # "N directional verdicts", which the paper contains *twice* -- so changing one of them
    # left the other satisfying the assertion, and the guard passed on a stale paper. Each
    # entry below is pinned to surrounding text that occurs once.
    required = [
        (f"the {counts['mapped pairs']} population-label pairs", "mapped-pair count"),
        (f"distribution is: {counts['directional']} directional verdicts "
         f"({counts['withdrawal']} \\textsc{{withdrawal}}, {counts['extension']} "
         f"\\textsc{{extension}}), {counts['non-monotone']} \\textsc{{non-monotone}}, "
         f"{counts['void']} \\textsc{{void}}", "the distribution sentence"),
        (f"Every one of the {counts['directional']} directional verdicts matches",
         "consistency-check total"),
    ]
    for phrase, what in required:
        assert phrase in text, (
            f"the paper's {what} disagrees with verdicts.csv; expected {phrase!r}. "
            f"Re-run  python -m src.experiments.analyse_verdicts  and update Section IX."
        )
    print(f"  {counts['directional']} directional ({counts['withdrawal']}W/"
          f"{counts['extension']}E), {counts['non-monotone']} non-monotone, "
          f"{counts['void']} void, over {counts['mapped pairs']} mapped pairs")


def test_paper_draft_population_count_is_recomputed() -> None:
    """The paper's own scale claim must match the results on disk.

    Three population counts in this project turned out to be arm counts (docs/38), and each
    was found only when something forced a look at the underlying files. The paper is the one
    document where that error is unrecoverable, so its count is recomputed here rather than
    read.
    """
    import re as _re

    # The typeset paper is the live claim; draft-v2.md is superseded and deliberately
    # frozen, so checking it would enforce a number the record has moved past.
    paper = ROOT / "research" / "paper" / "ieee" / "paper.tex"
    if not paper.exists():
        print("  paper.tex absent; skipping")
        return
    text = paper.read_text()

    # `_aware` is the attribute-aware in-processing configuration (doc 63): the same
    # persons under a different model input, a method suffix like the others here.
    method = _re.compile(r"_(eo|hgb|eps\d+|op[\d]+|post|aware|s60k)$")
    purpose = _re.compile(r"_(purchase|refinance|cashout|improvement|other)$")
    names = set()
    for directory in RESEARCH.glob("*"):
        if directory.is_dir() and (directory / "levelling_up_runs.csv").exists():
            stem = directory.name.replace("_levelling_up", "")
            while method.search(stem):
                stem = method.sub("", stem)
            names.add(stem)

    def population(stem: str) -> str:
        stem = purpose.sub("", _re.sub(r"_t\d+", "", stem))
        # The employment and coverage task arms draw from the same PUMS person
        # samples as the income arms of the same state-year (an employment row set
        # contains the income row set's workers), so by the paper's definition ---
        # independent means disjoint person samples --- they are new *arms* of
        # already-counted populations, never new populations (doc 60's accounting
        # note, stated in the paper's accounting table).
        stem = _re.sub(r"^acs_(employment|coverage)_", "acs_income_", stem)
        return _re.sub(r"_(rac1p|race|sex)$", "", stem)

    pops = {population(n) for n in names}
    # hmda_ms_la pools two populations already counted, so it is not independent of them.
    independent = {p for p in pops if p != "hmda_ms_la_2018"}

    # Read the claim rather than hardcode it. A test that pins a number has to be edited
    # every time the evidence grows, and an edit is exactly where a stale claim survives;
    # this one recomputes from the results and checks the document against that.
    # \s+ between every word: LaTeX source wraps lines freely, and the guard's subject is
    # the number, not the layout. A literal space here has already produced two false
    # alarms, one per wrap position.
    claimed = _re.search(r"(\d+)\s+independent\s+populations", text)
    assert claimed, "the paper no longer states an independent-population count"
    assert int(claimed.group(1)) == len(independent), (
        f"the paper claims {claimed.group(1)} independent populations; the results give "
        f"{len(independent)}: {sorted(independent)}")
    print(f"  paper claims {claimed.group(1)}; results give {len(independent)} "
          f"independent populations")


def test_doc42_and_43_dense_and_regime() -> None:
    """docs/42-43: the two reversals, the crossover cluster, and the regime split."""
    from src.experiments.analyse_dense import DENSE, dense_mode  # noqa: F401
    from src.experiments.analyse_calibration import apply_rules, majority_baseline
    from src.experiments.analyse_operating_point import crossover_bracket, load_points_for
    from src.experiments.viable_points import points_for
    from src.results_io import RESEARCH_RESULTS_DIR as RR

    _quotes(_doc(42), "-0.368", "-0.654", "+0.946", "0.507", "0.587")
    _quotes(_doc(43), "-0.024", "+0.585", "18 of 18")

    scored = {}
    for spec in ["acs:AL", "acs:KY", "acs:SC", "acs:OR", "dutch", "compas"]:
        info = points_for(spec)
        kept, counts = apply_rules(load_points_for(info["dataset"], info["points"]),
                                   majority_baseline(spec))
        assert counts["n_kept"] >= 6, (
            f"docs/42's D1 needs at least six arms retained on {spec}; got "
            f"{counts['n_kept']}. The twelve-point redesign is what makes the rest readable")
        scored[info["dataset"]] = (
            float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1]),
            crossover_bracket(kept))

    # The two reversals are load-bearing: docs/42 withdraws the claim that the relationship
    # holds WITHIN one side of the crossover on the strength of them.
    for name in ["acs_income_al_2018", "acs_income_ky_2018"]:
        assert scored[name][0] < 0, (
            f"docs/42 reports {name} REVERSING under the dense sweep; it is now "
            f"{scored[name][0]:+.3f}, and the withdrawal it justifies no longer follows")

    # The cluster: three domains, two countries, inside a tenth of each other.
    mids = [sum(b) / 2 for r, b in scored.values() if b is not None]
    assert len(mids) >= 4, f"docs/42 needs at least four located crossovers, got {len(mids)}"
    assert max(mids) - min(mids) < 0.12, (
        f"docs/42 rests on the non-lending crossovers clustering; their mid-points now span "
        f"{max(mids) - min(mids):.3f}")

    # docs/43: the attribute-aware regime, where the theory says the direction is determined.
    both = 0
    total = 0
    for directory in sorted(RR.glob("*_levelling_up_post")):
        frame = pd.read_csv(directory / "levelling_up_runs.csv").groupby("arm").mean(
            numeric_only=True)
        arm = next((a for a in frame.index if a.startswith("postprocess")), None)
        if arm is None or "priv_lost" not in frame.columns:
            continue
        total += 1
        both += int(frame.loc[arm, "priv_lost"] > 0 and frame.loc[arm, "unpriv_gained"] > 0)
    assert total >= 15 and both == total, (
        f"docs/43 reports the advantaged group losing AND the disadvantaged gaining in every "
        f"post-processed population; it is now {both}/{total}")
    print(f"  D1 >= 6 arms everywhere; AL {scored['acs_income_al_2018'][0]:+.3f} and KY "
          f"{scored['acs_income_ky_2018'][0]:+.3f} reversed; crossovers span "
          f"{max(mids) - min(mids):.3f}; attribute-aware {both}/{total}")


def test_doc44_magnitude_and_crossover_prior() -> None:
    """docs/44: the magnitude model must keep failing across populations, and C2 keep meaning nothing."""
    from scipy import stats

    from src.experiments.analyse_magnitude import MAX_SD, MIN_NAIVE, collect
    from src.experiments.analyse_threshold import MIN_R

    text = _doc(44)
    _quotes(text, "+0.487", "+0.964", "0.029", "0.544", "+0.947", "0.277")

    arms = collect()
    located = arms.dropna(subset=["crossover"]).copy()
    located["distance"] = located["selection_rate"] - located["crossover"]

    # M1 holds within populations, M2 fails across them. Both halves are load-bearing: the
    # document's whole point is that the concession is now partial rather than total.
    per_population = {
        str(name): float(stats.spearmanr(rows["distance"], rows["pie"]).statistic)
        for name, rows in located.groupby("population") if len(rows) >= 4}
    passing = sum(1 for rho in per_population.values() if rho >= 0.70)
    assert passing > len(per_population) / 2, (
        f"docs/44 reports the distance ordering the effect within most populations; "
        f"it is now {passing}/{len(per_population)}: {per_population}")

    pooled = float(np.corrcoef(located["distance"], located["pie"])[0, 1])
    assert pooled < MIN_R, (
        f"docs/44 reports M2 FAILING at {MIN_R} -- no single slope across populations. "
        f"It is now {pooled:+.3f}, and the limitation the paper states no longer holds")
    assert pooled >= MIN_NAIVE, "docs/44 reports the naive 'unpredictable' alternative beaten"

    # C1: the cluster that licenses "expect about 0.54".
    crossovers = (located.groupby("population")["crossover"].first())
    non_lending = crossovers[~crossovers.index.str.startswith("hmda")]
    assert float(non_lending.std()) < MAX_SD, (
        f"docs/44 rests on the non-lending crossovers clustering; sd is now "
        f"{float(non_lending.std()):.4f}")

    # C2 must stay uninterpretable. If it ever becomes a formula, that needs many more
    # populations -- not a re-reading of these four.
    from src.datasets import build as _build
    specs = {"acs_income_sc_2018": "acs:SC", "acs_income_or_2018": "acs:OR",
             "dutch_2001_sex": "dutch", "compas_2016_race": "compas"}
    gaps, sizes = [], []
    for name in non_lending.index:
        dataset = _build(specs[str(name)]).load()
        rates = dataset.base_rates().set_index("group")["P(y=1)"]
        gaps.append(float(rates["privileged"] - rates["unprivileged"]))
        sizes.append(dataset.n_samples)
    collinear = float(np.corrcoef(gaps, sizes)[0, 1])
    assert collinear > 0.9, (
        f"docs/44 reports C2's two predictors collinear at +0.947, which is why neither can "
        f"be modelled; it is now {collinear:+.3f}")
    _, p_gap = stats.pearsonr(gaps, non_lending.to_numpy())
    assert p_gap > 0.05, "docs/44 reports C2 indistinguishable from chance at four populations"
    print(f"  M1 {passing}/{len(per_population)}; M2 fails at {pooled:+.3f}; crossover sd "
          f"{float(non_lending.std()):.4f}; C2 predictors collinear {collinear:+.3f}")


def test_paper_circularity_answer_matches_the_sweeps() -> None:
    """The reply to the circularity objection must stay a measurement, not an assertion.

    This is the only objection the paper answers with numbers it computed for that purpose,
    so the numbers are the answer. If a re-run moves them, the paragraph in the audit
    section is wrong before anyone notices the prose still reads well.
    """
    from src.experiments.analyse_circularity import (
        distances, load_sweeps, locality, stability, MIN_MAGNITUDE)
    from scripts.independence import population

    text = _paper_text()
    doc = _doc(74)
    sweeps = load_sweeps()

    pairs = locality(sweeps)
    flipped = int(pairs.flipped.sum())
    share = flipped / len(pairs)
    assert (len(pairs), flipped) == (639, 69), (
        f"the paper reports 69 of 639 adjacent pairs flipping sign; recomputed "
        f"{flipped} of {len(pairs)}")
    assert 0.105 <= share <= 0.115, f"the paper rounds that to 11%; it is {share:.1%}"

    d = distances(sweeps)
    samples = d.loc[d.gap.abs().groupby(d["sample"]).idxmin()]
    within = {lim: int((samples.gap.abs() <= lim).sum()) for lim in (0.05, 0.10, 0.20)}
    assert len(samples) == 21, (
        f"the paper reports 21 disjoint person samples with both a located crossover and "
        f"a natural arm; recomputed {len(samples)}")
    assert within[0.10] == 11 and within[0.05] == 6, (
        f"the paper reports 11 samples within 0.10 of their crossover and 6 within 0.05; "
        f"recomputed {within[0.10]} and {within[0.05]}")
    assert len(samples) - within[0.20] == 5, (
        "the paper concedes 5 of 21 samples sit beyond 0.20 and would not have needed the "
        f"sweep; recomputed {len(samples) - within[0.20]}")

    closest = float(d.gap.abs().min())
    assert abs(closest - 0.004) < 0.0005, (
        f"the paper names Florida 2018 as 0.004 from its own crossover; it is {closest:.4f}")

    # Florida's two attributes must keep disagreeing -- it is the paper's evidence that a
    # crossover cannot be looked up rather than measured, and one number would kill it.
    fl = d[d["sample"] == population("acs_income_fl_2018_levelling_up")]
    assert len(fl) == 2, f"the paper reads Florida 2018 twice, once per attribute; got {len(fl)}"
    assert {round(v, 3) for v in fl.crossover} == {0.284, 0.439}, (
        f"the paper quotes Florida's two crossovers as 0.284 and 0.439; they are "
        f"{sorted(round(v, 3) for v in fl.crossover)}")

    small = stability(sweeps)
    small = small[small.pie.abs() < MIN_MAGNITUDE]
    unanimous = float(small.unanimous.mean())
    assert 0.53 <= unanimous <= 0.57, (
        f"the paper concedes sub-{MIN_MAGNITUDE}-point arms agree on their sign across "
        f"seeds only 55% of the time; recomputed {unanimous:.0%}")

    for value in ("639", "11\\%", "0.284", "0.439", "0.004", "55\\%"):
        assert value in text, f"the paper's circularity paragraph no longer quotes {value}"
    _quotes(doc, "639", "11%", "0.284", "0.439", "52%", "55%")
    print(f"  {flipped}/{len(pairs)} pairs flip ({share:.0%}); {within[0.10]}/{len(samples)} "
          f"samples within 0.10; sub-point unanimity {unanimous:.0%}")


def test_paper_guard_provenance_matches_the_code() -> None:
    """The provenance claims are about the code, so the code is what checks them.

    Two of them were wrong when first written -- the paper dated the noise floor from the
    constant that carries it today rather than from its value, and claimed every sealed test
    from the re-seal onward froze both exclusion rules when three of the four freeze
    neither. Both are the sort of claim that reads fine forever unless something re-derives
    it, so this re-derives it.
    """
    import inspect

    from src.experiments import (analyse_ipums_race, analyse_lending_direction,
                                 analyse_resealed, analyse_third_direction)
    from src.experiments.analyse_verdicts import magnitude_sensitivity

    text = _paper_text()

    # Which sealed analysers actually apply the parity-gap and accuracy exclusions.
    def applies(module) -> bool:
        src = inspect.getsource(module)
        return any(k in src for k in ("GAP_FLOOR", "MIN_BASELINE_GAP", "majority_baseline"))

    assert not applies(analyse_resealed), (
        "the paper says the re-seal applies neither exclusion rule and scores all ten raw; "
        "its analyser now references one")
    assert not applies(analyse_third_direction) and not applies(analyse_lending_direction), (
        "the paper says the third-direction and lending cohorts apply neither of the two "
        "exclusion rules; one of them now does")
    assert applies(analyse_ipums_race), (
        "the paper names the screen-gated race cohort as the one carrying both rules")

    # The magnitude guard's value must stay operational: if some floor ever separates far
    # better than its neighbours, "1.0 is a round number" stops being the honest reading.
    table = magnitude_sensitivity()
    at_one = float(table.loc[table["floor"] == 1.00, "separation"].iloc[0])
    assert (table["separation"] > 0).all(), (
        "the paper claims every floor from 0.25 to 5.00 separates; one no longer does:\n"
        f"{table.to_string(index=False)}")
    lo, hi = table["separation"].min(), table["separation"].max()
    assert 0.12 <= lo <= 0.14 and 0.34 <= hi <= 0.36, (
        f"the paper quotes the separation running 13% to 35%; it is now "
        f"{lo:.0%} to {hi:.0%}")
    assert abs(at_one - 0.343) < 0.005, (
        f"the paper quotes +34 at the committed 1.0 floor; it is {at_one:+.0%}")
    assert at_one < hi, (
        "the paper's concession is that 1.0 is not the best separator. It now is, which "
        "would make the guard look chosen for the value rather than the round number")

    # Site-anchored, not bare words: "operational" alone also matches "operationalizes"
    # and "operationally" elsewhere in the paper, so a bare check passes after the sentence
    # it is meant to protect has been deleted. That failure mode has bitten this file twice.
    for value in ("every\\emph{value} is operational --- a round number".replace("every", ""),
                  "from 0.25 to 5.00 points separates",
                  "by between 13 and 35 percentage points",
                  "existence} is therefore measured"):
        assert value in text, f"the paper's magnitude-provenance paragraph no longer says {value!r}"
    _quotes(_doc(75), "+35%", "+34%", "0.75", "Three Connecticut arm sets", "4 of 8")
    print(f"  separation {lo:.0%}-{hi:.0%}, committed floor {at_one:+.0%}; "
          f"exclusion rules applied by 1 of 4 sealed analysers")


def test_paper_ledger_and_coverage_counts_are_derived_not_narrated() -> None:
    """Counts that appear in more than one place must be derived from one source.

    A panel review found the failure ledger described four different ways in the same
    paper -- nine, "sixteen of which two", "five failures one pass", against a table of
    eighteen rows -- and the two accounting tables disagreeing on lending coverage. Neither
    was caught by any existing guard, because every guard checked a number against the data
    and none checked the paper against itself. This one does that.
    """
    import re

    from src.experiments.analyse_lending_coverage import coverage, load_arms

    text = _paper_text()
    raw = (ROOT / "research" / "paper" / "ieee" / "paper.tex").read_text()

    # --- the ledger, counted from its own rows
    i = raw.find("EO transfer &")
    table = raw[raw.rfind("\\begin{table", 0, i):raw.find("\\end{table", i)]
    body = table[table.find("\\midrule"):table.find("\\bottomrule")]
    rows = [r for r in body.split("\\\\") if "&" in r]
    holds = sum("holds" in r.split("&")[1] for r in rows if len(r.split("&")) > 1)
    assert len(rows) == 18, f"the ledger has {len(rows)} rows; the paper says eighteen"
    assert holds == 3, f"{holds} rows record a hold; the paper says three"
    for phrase in ("holds \\textbf{eighteen} rows", "twelve fail, three",
                   "nine that test a \\emph{direction} rule"):
        assert phrase.replace("\\\\", "\\") in text, \
            f"the ledger's canonical count no longer says {phrase!r}"
    # The stale descriptions must not come back.
    for stale in ("sixteen attempts at one claim, of which two succeeded",
                  "The sealed record is five failures, one pass"):
        assert stale not in text, f"a superseded ledger count has returned: {stale!r}"

    # --- lending coverage: both accounting tables, from one computation
    table2 = coverage(load_arms())
    race = table2[table2.attribute == "race"].iloc[0]
    total_arms = int(table2.arms.sum())
    states = int(table2.states.max())
    assert (total_arms, states) == (66, 40), (
        f"lending coverage recomputes to {total_arms} arms over {states} states; "
        f"the paper's two accounting tables both say 66 over 40")
    assert (int(race.clears_both), int(race.both_up)) == (12, 12)
    assert f"Lending coverage & {total_arms} & {states} & 1" in text, \
        "the independence table no longer carries the recomputed lending denominators"
    assert "40 race + 26 sex arms (66)" in text, \
        "the accounting table no longer carries the recomputed lending arm count"
    assert "all fifty markets" not in text and "all fifty\nstates" not in raw, \
        "the overstated fifty-market coverage claim has returned"

    # --- the crossover span, from the located brackets themselves
    from src.experiments.analyse_circularity import distances, load_sweeps
    span = distances(load_sweeps()).crossover
    lo, hi = round(float(span.min()), 2), round(float(span.max()), 2)
    assert (lo, hi) == (0.22, 0.81), f"located crossovers now span {lo}-{hi}"
    assert "0.28 to 0.65" not in text, \
        "the understated 0.28-0.65 crossover span has returned to the prose"
    print(f"  ledger 18 rows / {holds} hold; lending {total_arms} arms / {states} states; "
          f"crossovers {lo}-{hi}")


def test_paper_block1_claims_stay_narrowed() -> None:
    """Four claims a panel said were stronger than the evidence. They must stay narrowed.

    Each of these reads perfectly well in its overclaimed form -- that is why all four
    survived three prior audits -- so the guard pins the narrowing language rather than a
    number, and asserts the withdrawn form has not returned.
    """
    from math import comb

    from src.experiments.analyse_lending_coverage import (GAP_FLOOR, MAGNITUDE_GUARD,
                                                          load_arms)

    text = _paper_text()

    # 1. The central claim is scoped to in-processing and says the crossover costs a sweep.
    for phrase in ("rather than by which in-processing method is chosen",
                   "the rate a team already has, the crossover it must measure",
                   "the crossover is not --- it costs a sweep"):
        assert phrase in text, f"the central claim no longer says {phrase!r}"
    assert "rather than of the fairness method ---" not in text, \
        "the unscoped 'not the fairness method' claim has returned"

    # 2. The floor defence must keep conceding South Carolina's dense sweep.
    assert "an earlier version of this paper claimed otherwise" in text and "$+0.012$" in text, \
        "the floor-robustness passage no longer concedes the dense-sweep dependence"
    assert "does not reach the domain table" not in text, \
        "the false floor-robustness claim has returned"

    # 3. Both lending counts must be reported with the constant that ties them, and the
    #    constant must genuinely still tie -- if a future arm went down, the concession
    #    would be wrong in the other direction and the sentence would need rewriting.
    arms = load_arms()
    race = arms[arms.attribute == "race"]
    floor = race[race.gap.abs() >= GAP_FLOOR]
    both = floor[floor.pie.abs() >= MAGNITUDE_GUARD]
    up_floor, up_both = int((floor.pie > 0).sum()), int((both.pie > 0).sum())
    assert (up_both, len(both)) == (12, 12) and (up_floor, len(floor)) == (25, 31)
    assert up_both == len(both), (
        "a lending arm now goes down, so a constant no longer ties the rule and the "
        "paper's concession is out of date in the paper's favour")
    assert "a constant ``up'' scores 25 of 31 and 12 of 12 identically" in text, \
        "the lending counts no longer report the constant that ties them"

    # 4. The within-sweep p-values must stay withdrawn, with the population-level number.
    assert "$p < 0.001$" not in text.replace("attached $p < 0.001$ to those coefficients", ""), \
        "a within-sweep p-value has returned outside the sentence withdrawing it"
    n, k = 6, 4
    expected = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    assert abs(expected - 0.34) < 0.005
    assert "a sign test at $p = 0.34$" in text, \
        "the population-level sign test is no longer reported"
    print("  claim scoped; floor conceded; lending constants reported; p-values withdrawn")


def test_paper_two_answer_rates_stay_distinguished() -> None:
    """78% and 29-of-52 measure different things, and two referees confused them.

    The survey's 78% applies one gate to a random draw; the audit's 29 of 52 applies every
    gate to the stored sweeps. Both are correct and the abstract used to quote only the
    higher one, which reads as the procedure's answer rate when it is not. This checks that
    both numbers are still derivable, that they still differ, and that the paper still says
    which is which in both the record and the cut.
    """
    import sys

    import pandas as pd

    sys.path.insert(0, str(ROOT))
    from scripts.independence import population

    survey = pd.read_csv(RESEARCH / "survey" / "survey_verdicts.csv")
    shape = survey["verdict"].str.split(" (", regex=False).str[0]
    admits = int(shape.isin(["CLASSIC", "MONOTONE"]).sum())
    assert (admits, len(survey)) == (39, 50), (
        f"the survey's monotonicity gate now passes {admits} of {len(survey)}, "
        f"not the 39 of 50 the paper quotes as 78%")

    samples = survey["population"].map(lambda x: population(x + "_levelling_up")).nunique()
    assert samples == 48, (
        f"the fifty draws now resolve to {samples} disjoint person samples, not 48; the "
        f"paper explains the gap as two state-years drawn under both attributes")

    for name in ("paper.tex", "paper-submission.tex"):
        text = " ".join((ROOT / "research" / "paper" / "ieee" / name).read_text().split())
        assert "Two rates, and they are not the same rate" in text, \
            f"{name} no longer reconciles the survey rate against the audit's answer rate"
        assert "a little under\nsix times in ten".replace("\n", " ") in text or \
               "a little under six times in ten" in text, \
            f"{name}'s abstract no longer gives the end-to-end answer rate beside the 78%"
        assert "That is the monotonicity gate alone" in text, \
            f"{name}'s abstract no longer says which gate the 78% applies"
    print(f"  survey {admits}/{len(survey)} = {admits/len(survey):.0%} on one gate; "
          f"audit 29/52 = 56% on all gates; {samples} disjoint samples")


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
        test_doc31_natural_split,
        test_doc32_rate_not_task,
        test_doc33_eo_scope_condition,
        test_doc34_epsilon_robustness,
        test_doc36_second_learner,
        test_doc37_spread_guard_audit,
        test_doc38_population_counts_are_recomputed,
        test_doc40_accuracy_rule_and_its_withdrawals,
        test_doc41_postprocessing_arm_is_void,
        test_doc42_and_43_dense_and_regime,
        test_doc44_magnitude_and_crossover_prior,
        test_paper_ablation_table_matches_results,
        test_paper_who_pays_figures_match_results,
        test_paper_sealed_cohort_scores_match_results,
        test_paper_effect_size_split_matches_results,
        test_paper_denominator_table_matches_computed_independence,
        test_paper_verdict_distribution_matches_the_audit,
        test_paper_draft_population_count_is_recomputed,
        test_paper_circularity_answer_matches_the_sweeps,
        test_paper_guard_provenance_matches_the_code,
        test_paper_ledger_and_coverage_counts_are_derived_not_narrated,
        test_paper_block1_claims_stay_narrowed,
        test_paper_two_answer_rates_stay_distinguished,
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
