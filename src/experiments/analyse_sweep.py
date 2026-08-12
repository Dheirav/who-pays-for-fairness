"""Test the three predictions across populations.

Adult produced observations. Observations become results when they predict something
about a population they were not derived from, and that prediction can fail. This
analyses a multi-state sweep against three claims stated in advance:

**P1 — the rate/people divergence follows group sizes.** :mod:`src.incidence` reports
the share of a closed gap borne by the privileged group twice: once in rates, once in
people. On Adult they differ substantially. The claim is that the difference is not a
property of Adult but pure population arithmetic —

    people_share = s·N_priv / (s·N_priv + (1−s)·N_unpriv)

for a rate-level share ``s``. If that holds across populations whose group ratio spans
1.02 to 2.08, it is a law rather than an observation. It is tested here as a *fit*, not
a direction: predicted against observed, per method, per population.

**P2 — the DP/EO conflict scales with the base-rate gap.** The impossibility results
(Kleinberg et al. 2016; Chouldechova 2017) say demographic parity and equalized odds
are incompatible unless base rates are equal. That is a statement about *whether* the
conflict exists. The quantitative claim is stronger: the further apart the base rates,
the more constraining DP should cost EO. States span a 2.8x range in that gap, so this
is directly testable.

**P3 — proxy relocation needs a proxy worth relocating onto.** On Adult, constraining
DP moved attribution onto ``relationship``, whose Husband/Wife levels fix sex outright
for 46% of rows. ACS records the same relation as one husband/wife code that is 50.2%
male, so there is no comparable target. Sex should be correspondingly harder to
recover. Measured by :meth:`FairnessDataset.attribute_leakage`.

``--protected RAC1P`` re-runs the same analysis over the race-protected arm. That arm
exists for P1 alone: on sex the group ratio spans only 1.02-1.24 across every state and
is confounded with population size at r = +0.794, so neither can be read on its own. On
race it spans 1.94-24.98 with the confound *inverted* (r = -0.567), and the two arms
agreeing or disagreeing is what identifies which quantity is doing the work.

P3 is not evaluated there -- it is a contrast between Adult and ACS, and Adult protects
sex -- and P2's meaning changes with the groups, so it is descriptive rather than a test
of the original prediction.

Usage:
    python -m src.experiments.analyse_sweep
    python -m src.experiments.analyse_sweep --states VT NM MS WV WY ND UT AL OR
    python -m src.experiments.analyse_sweep --protected RAC1P
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..datasets import build as build_dataset
from ..results_io import RESULTS_DIR, output_dir

DEFAULT_STATES = ["VT", "NM", "MS", "WV", "WY", "ND", "UT", "AL", "OR"]

# The arm whose outputs keep the unsuffixed filenames, matching the convention in
# `ACSIncomeLoader.name` and `results_io.FLAT_DATASET`: the configuration that was
# there first keeps its paths so committed results are not orphaned.
SEX_ARM = "SEX"

# Runs where the unprivileged group also lost ground leave the share outside [0, 1];
# the arithmetic in P1 assumes a transfer between the groups, so those are reported
# separately rather than silently averaged in.
VALID_SHARE = (0.0, 1.0)


def predicted_people_share(s: float, n_priv: float, n_unpriv: float) -> float:
    """The P1 formula: a rate-level split re-expressed as a headcount split."""
    numerator = s * n_priv
    denominator = numerator + (1.0 - s) * n_unpriv
    return numerator / denominator if denominator else np.nan


def cross_flow_share(runs: pd.DataFrame) -> pd.Series:
    """Fraction of individual movement running *against* the intended transfer.

    P1's arithmetic assumes the mitigation takes favourable decisions from the
    privileged group and hands them to the unprivileged one. Real fits also move people
    the other way -- privileged individuals who gain, unprivileged who lose -- and those
    movements are invisible to a formula written in terms of two group rates.

    This quantifies how far each run departs from that assumption, and it is the
    diagnostic P1's restated form depends on, so it is computed here rather than by
    hand. Every input is already recorded per run by ``run_who_pays``; no refit is
    needed to obtain it for results already on disk.
    """
    intended = runs["priv_lost"] + runs["unpriv_gained"]
    against = runs["priv_gained"] + runs["unpriv_lost"]
    return (against / intended).replace([np.inf, -np.inf], np.nan)


def load_population(key: str, label: str) -> pd.DataFrame | None:
    """Load one population's who-pays runs, tagged with its own group statistics."""
    dataset = build_dataset(key).load()
    path = output_dir(dataset.name) / "who_pays_runs.csv"
    if not path.exists():
        return None

    frame = pd.read_csv(path)
    rates = dataset.base_rates().set_index("group")
    frame["population"] = label
    frame["group_ratio"] = rates.loc["privileged", "n"] / rates.loc["unprivileged", "n"]
    frame["base_rate_gap"] = rates.loc["privileged", "P(y=1)"] - rates.loc["unprivileged", "P(y=1)"]
    frame["leakage_auc"] = dataset.attribute_leakage()["leakage_auc"]
    frame["n_total"] = dataset.n_samples
    return frame


def test_p1(runs: pd.DataFrame) -> pd.DataFrame:
    """Predicted vs observed people-level share, per population."""
    usable = runs[
        runs["dp_share_levelling_down"].between(*VALID_SHARE)
        & runs["people_share_levelling_down"].notna()
    ].copy()
    usable["predicted"] = [
        predicted_people_share(row.dp_share_levelling_down, row.n_priv, row.n_unpriv)
        for row in usable.itertuples()
    ]
    usable["error"] = (usable["predicted"] - usable["people_share_levelling_down"]).abs()
    usable["cross_flow"] = cross_flow_share(usable)

    dropped = len(runs) - len(usable)
    if dropped:
        print(f"  ({dropped} runs excluded: share outside [0,1], i.e. both groups lost)")

    return (
        usable.groupby("population")
        .agg(n=("n_total", "first"),
             group_ratio=("group_ratio", "first"),
             n_runs=("error", "size"),
             cross_flow=("cross_flow", "mean"),
             mean_abs_error=("error", "mean"),
             max_abs_error=("error", "max"))
        .sort_values("group_ratio")
    )


def test_p2(runs: pd.DataFrame) -> pd.DataFrame:
    """How much constraining demographic parity costs equalized odds."""
    dp_rows = runs[runs["method"] == "expgrad_dp"].copy()
    dp_rows["eo_cost"] = dp_rows["eo_diff"] - dp_rows["baseline_eo_diff"]
    dp_rows["dp_gain"] = dp_rows["baseline_dp_diff"] - dp_rows["dp_diff"]
    # Normalised so populations with different amounts of bias to remove are comparable.
    dp_rows["eo_cost_per_dp_point"] = dp_rows["eo_cost"] / dp_rows["dp_gain"]
    return (
        dp_rows.groupby("population")
        .agg(base_rate_gap=("base_rate_gap", "first"),
             baseline_eo=("baseline_eo_diff", "mean"),
             mitigated_eo=("eo_diff", "mean"),
             eo_cost=("eo_cost", "mean"),
             eo_cost_per_dp_point=("eo_cost_per_dp_point", "mean"))
        .sort_values("base_rate_gap")
    )


def correlate(frame: pd.DataFrame, x: str, y: str) -> tuple[float, float]:
    """Pearson r and slope, computed directly so the dependency stays light."""
    a, b = frame[x].to_numpy(float), frame[y].to_numpy(float)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    if len(a) < 3:
        return np.nan, np.nan
    r = float(np.corrcoef(a, b)[0, 1])
    slope = float(np.polyfit(a, b, 1)[0])
    return r, slope


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=DEFAULT_STATES)
    parser.add_argument("--protected", default=SEX_ARM,
                        help="attribute the sweep was run on (SEX | RAC1P)")
    args = parser.parse_args()
    arm = args.protected.strip().upper()

    # Adult belongs to the sex arm only: its loader protects sex, so including it in a
    # race sweep would silently mix two different constraints into one correlation.
    populations = [("adult", "Adult")] if arm == SEX_ARM else []
    suffix = "" if arm == SEX_ARM else f":{arm}"
    populations += [(f"acs:{s}{suffix}", s) for s in args.states]
    frames = []
    for key, label in populations:
        frame = load_population(key, label)
        if frame is None:
            print(f"  skipped {label}: no who-pays results")
            continue
        frames.append(frame)
    runs = pd.concat(frames, ignore_index=True)
    print(f"loaded {len(runs)} runs across {runs['population'].nunique()} populations\n")

    print("=" * 78)
    print("P1  the rate/people divergence is population arithmetic, not an Adult quirk")
    print("=" * 78)
    p1 = test_p1(runs)
    print(p1.round(4).to_string())
    r, _ = correlate(p1.reset_index(), "group_ratio", "mean_abs_error")
    flat = p1.reset_index()
    r_flow, _ = correlate(flat, "cross_flow", "mean_abs_error")
    r_n, _ = correlate(flat, "n", "mean_abs_error")
    r_ratio_n, _ = correlate(flat, "group_ratio", "n")
    print(f"\n  mean absolute error overall : {p1['mean_abs_error'].mean():.4f}")
    print(f"  worst single population     : {p1['mean_abs_error'].max():.4f}")
    print(f"  error vs cross-flow share, r: {r_flow:+.3f}  <- the proposed mechanism")
    print(f"  error vs population size, r : {r_n:+.3f}")
    print(f"  error vs group ratio, r     : {r:+.3f}")
    print(f"  group ratio vs size, r      : {r_ratio_n:+.3f}  <- read the line above")
    print( "                                 only against this one; where ratio and")
    print( "                                 size covary, either can stand in for the")
    print( "                                 other and the sign is not interpretable.")

    print()
    print("=" * 78)
    print("P2  constraining demographic parity costs more equalized odds where the")
    print("    base rates are further apart")
    print("=" * 78)
    p2 = test_p2(runs)
    print(p2.round(4).to_string())
    r_cost, slope = correlate(p2.reset_index(), "base_rate_gap", "eo_cost")
    r_norm, _ = correlate(p2.reset_index(), "base_rate_gap", "eo_cost_per_dp_point")
    print(f"\n  eo_cost vs base_rate_gap        r = {r_cost:+.3f}  slope = {slope:+.3f}")
    print(f"  normalised cost vs gap          r = {r_norm:+.3f}")

    print()
    print("=" * 78)
    print(f"P3  {arm} is harder to recover where no feature determines it")
    print("=" * 78)
    leakage = (
        runs.groupby("population")
        .agg(leakage_auc=("leakage_auc", "first"), n=("n_total", "first"))
        .sort_values("leakage_auc", ascending=False)
    )
    print(leakage.round(4).to_string())

    # P3 is a contrast between Adult and everything else, so it is only defined on the
    # arm Adult belongs to. On any other arm the ACS populations are all that exist and
    # there is no comparison to draw; the leakage figures are still worth printing as a
    # description of the populations, but calling the prediction from them would be
    # inventing a test the design does not support.
    if "Adult" in leakage.index:
        adult = leakage.loc["Adult", "leakage_auc"]
        acs = leakage.drop(index="Adult")["leakage_auc"]
        print(f"\n  Adult (relationship fixes sex for 46% of rows) : {adult:.4f}")
        print(f"  ACS   (husband/wife is one code, 50.2% male)   : "
              f"{acs.mean():.4f} mean, {acs.min():.4f}-{acs.max():.4f}")
        verdict = "CONFIRMED" if acs.max() < adult else "NOT CONFIRMED"
        print(f"  -> {verdict}: every ACS population leaks less than Adult"
              if acs.max() < adult
              else f"  -> {verdict}: {(acs >= adult).sum()} ACS populations leak at "
                   f"least as much as Adult")
    else:
        print(f"\n  P3 not evaluated: it contrasts Adult against ACS, and Adult is not"
              f"\n  in the {arm} arm. Leakage above describes these populations only.")

    # The arm has to reach the filename for the same reason it has to reach the dataset
    # name: both arms analyse the same states in the same year, so without it a race
    # sweep overwrites the committed sex sweep and nothing reports an error.
    out = RESULTS_DIR / "sweep"
    out.mkdir(parents=True, exist_ok=True)
    stem = "sweep" if arm == SEX_ARM else f"sweep_{arm.lower()}"
    runs.to_csv(out / f"{stem}_runs.csv", index=False)
    p1.to_csv(out / f"{stem}_p1_formula_fit.csv")
    p2.to_csv(out / f"{stem}_p2_metric_conflict.csv")
    leakage.to_csv(out / f"{stem}_p3_leakage.csv")
    print(f"\nwrote {out}/{stem}_*.csv")


if __name__ == "__main__":
    main()
