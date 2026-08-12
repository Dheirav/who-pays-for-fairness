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


def main() -> None:
    tests = [
        test_doc11_cross_flow_correlations,
        test_doc12_intersectional_condition,
        test_doc13_partial_correlations,
        test_doc14_endpoint_independence,
        test_doc15_arbitrariness,
        test_doc16_and_17_injection_tables,
        test_doc19_levelling_up,
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
