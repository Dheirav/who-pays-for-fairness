"""Intervals on the crossover, and whether the exclusion thresholds made the result.

**Individual work, beyond the course submission.** **Post-hoc and labelled so**: both analyses
answer questions a reviewer raised after the results existed. Neither uses new data.

Two things the paper asserts without quantifying them.

**Intervals.** Every crossover is reported as a bracket between two arms and given no
uncertainty at all, so "0.511" and "0.576" read as measurements of equal precision. They are
not: each arm is a mean over seeds, and the bracket moves when the seeds move. Resampling
seeds *within* arms and recomputing the bracket gives an interval that reflects the actual
stability of the estimate.

**Sensitivity.** Two exclusion rules do a great deal of work here -- a baseline parity gap
below ``0.05`` and an accuracy below the trivial predictor -- and the second withdrew two
headline results. The parity threshold of 0.05 was inherited from document 12, where it was
chosen to exclude one degenerate population, and has never been varied. If the finding only
survives at 0.05 it is an artifact of that choice, and a reviewer is entitled to see the sweep
rather than the assurance.

Run:  python -m src.experiments.analyse_uncertainty_crossover --mode intervals
      python -m src.experiments.analyse_uncertainty_crossover --mode sensitivity
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from .analyse_calibration import majority_baseline
from .analyse_operating_point import op_arm_name_for
from .analyse_threshold import MIN_R
from .viable_points import points_for

SWEPT = {"acs:AL": "ACS Alabama", "acs:KY": "ACS Kentucky", "acs:SC": "ACS S. Carolina",
         "acs:OR": "ACS Oregon", "dutch": "Dutch census", "compas": "COMPAS"}

BOOTSTRAP = 2000
PARITY_GRID = [0.01, 0.02, 0.05, 0.10]


def per_seed(spec: str) -> pd.DataFrame:
    """Every arm of a population, one row per (arm, seed), so seeds can be resampled."""
    info = points_for(spec)
    rows = []
    for point in info["points"]:
        path = (RESEARCH_RESULTS_DIR / op_arm_name_for(info["dataset"], point)
                / "levelling_up_runs.csv")
        if not path.exists():
            continue
        runs = pd.read_csv(path)
        base = runs[runs["arm"] == "baseline"].set_index("seed")
        plain = runs[runs["arm"] == "expgrad_dp"].set_index("seed")
        for seed in base.index.intersection(plain.index):
            rows.append({
                "point": point, "seed": int(seed),
                "rate": float(base.loc[seed, "positives"] / base.loc[seed, "n_test"]),
                "pie": float(plain.loc[seed, "positives_pct_change"]),
                "dp_base": float(base.loc[seed, "dp_diff"]),
                "acc_base": float(base.loc[seed, "accuracy"]),
            })
    return pd.DataFrame(rows)


def bracket(arms: pd.DataFrame) -> tuple[float, float] | None:
    below = arms[arms["pie"] < 0]["rate"]
    above = arms[arms["pie"] > 0]["rate"]
    if below.empty or above.empty or below.max() >= above.min():
        return None
    return float(below.max()), float(above.min())


def intervals_mode() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for spec, label in SWEPT.items():
        frame = per_seed(spec)
        if frame.empty:
            continue
        floor = majority_baseline(spec)
        seeds = sorted(frame["seed"].unique())

        def collapse(chosen) -> pd.DataFrame:
            picked = pd.concat([frame[frame["seed"] == s] for s in chosen])
            arms = picked.groupby("point")[["rate", "pie", "dp_base", "acc_base"]].mean()
            return arms[(arms["dp_base"] >= 0.05) & (arms["acc_base"] >= floor)]

        point_estimate = bracket(collapse(seeds))
        mids = []
        for _ in range(BOOTSTRAP):
            drawn = rng.choice(seeds, size=len(seeds), replace=True)
            band = bracket(collapse(drawn))
            if band is not None:
                mids.append((band[0] + band[1]) / 2)

        located = len(mids) / BOOTSTRAP
        rows.append({
            "population": label,
            "crossover": np.nan if point_estimate is None
            else (point_estimate[0] + point_estimate[1]) / 2,
            "ci_low": np.percentile(mids, 2.5) if mids else np.nan,
            "ci_high": np.percentile(mids, 97.5) if mids else np.nan,
            "located_in": located,
            "n_seeds": len(seeds),
        })

    out = pd.DataFrame(rows)
    print("Bootstrap over seeds within arms, "
          f"{BOOTSTRAP} resamples. 'located' is the fraction of resamples in which a\n"
          "crossover could be bracketed at all -- a low value means the bracket itself is "
          "fragile.\n")
    print(out.round(3).to_string(index=False))
    return out


def sensitivity_mode() -> pd.DataFrame:
    rows = []
    for spec, label in SWEPT.items():
        frame = per_seed(spec)
        if frame.empty:
            continue
        floor = majority_baseline(spec)
        arms = frame.groupby("point")[["rate", "pie", "dp_base", "acc_base"]].mean()
        for threshold in PARITY_GRID:
            kept = arms[(arms["dp_base"] >= threshold) & (arms["acc_base"] >= floor)]
            if len(kept) < 3:
                rows.append({"population": label, "parity_bar": threshold,
                             "n": len(kept), "r": np.nan, "crossover": np.nan})
                continue
            r = float(np.corrcoef(kept["rate"], kept["pie"])[0, 1])
            band = bracket(kept)
            rows.append({"population": label, "parity_bar": threshold, "n": len(kept),
                         "r": r, "crossover": np.nan if band is None
                         else (band[0] + band[1]) / 2})

    out = pd.DataFrame(rows)
    print("Re-scoring every population across parity-gap exclusion thresholds. The accuracy\n"
          "rule is held fixed; only the inherited 0.05 is varied.\n")
    print(out.pivot(index="population", columns="parity_bar",
                    values="r").round(3).to_string())
    print("\ncrossover mid-point by threshold:")
    print(out.pivot(index="population", columns="parity_bar",
                    values="crossover").round(3).to_string())

    holds = out.dropna(subset=["r"]).groupby("parity_bar")["r"].apply(
        lambda s: int((s >= MIN_R).sum()))
    print(f"\npopulations clearing r >= {MIN_R} at each threshold:")
    print(holds.to_string())
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["intervals", "sensitivity"], default="intervals")
    args = parser.parse_args()

    out = intervals_mode() if args.mode == "intervals" else sensitivity_mode()
    path = research_dir("uncertainty") / f"crossover_{args.mode}.csv"
    out.to_csv(path, index=False)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
