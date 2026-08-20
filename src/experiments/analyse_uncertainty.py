"""Confidence intervals for the headline correlations, clustered by population.

**Individual work, beyond the course submission.**

Every correlation in this project has been reported as a point estimate. That is not good
enough for the load-bearing ones, and the reason is specific rather than generic: the
populations are **not independent**. Arms of the same ACS state share a survey instrument,
an encoding and a sampling design, and the threshold sweeps produce several arms from one
state. Bootstrapping rows would resample those as though they were independent draws and
report an interval that is too narrow.

So the resampling unit is the **population**, not the arm — a cluster bootstrap. Alabama
either appears in a draw with all of its cutoffs or not at all.

This matters most for the held-out set of document 26, which is fourteen arms drawn from
only **four** populations. Fourteen is the number of measurements; four is the number of
independent things measured, and the interval should reflect the smaller one.

Run:  python -m src.experiments.analyse_uncertainty
"""

from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

DRAWS = 5000


def cluster_of(name: str) -> str:
    """The independent unit a row belongs to: a state, or a lending population."""
    match = re.match(r"acs_income_([a-z]{2})_", name)
    if match:
        return f"ACS-{match.group(1)}"
    if name.startswith("hmda_la"):
        return "HMDA-LA"
    if name.startswith("hmda_ms"):
        return "HMDA-MS"
    return "adult"


def cluster_bootstrap(x, y, clusters, draws: int = DRAWS, seed: int = 0):
    """Percentile interval for Pearson r, resampling clusters with replacement."""
    rng = np.random.default_rng(seed)
    x, y, clusters = np.asarray(x, float), np.asarray(y, float), np.asarray(clusters)
    unique = np.unique(clusters)
    estimates = []
    for _ in range(draws):
        picked = rng.choice(unique, len(unique), replace=True)
        index = np.concatenate([np.where(clusters == c)[0] for c in picked])
        if len(np.unique(x[index])) < 3:
            continue
        estimates.append(np.corrcoef(x[index], y[index])[0, 1])
    estimates = np.asarray(estimates)
    return (float(np.percentile(estimates, 2.5)),
            float(np.percentile(estimates, 97.5)), len(unique))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--states", nargs="+", default=None,
                        help="restrict to these clusters, e.g. --states ACS-al ACS-or; "
                             "default is every population present")
    args = parser.parse_args()

    def keep(frame: pd.DataFrame) -> pd.DataFrame:
        """Optionally restrict to a subset of clusters, for sensitivity checks."""
        if not args.states:
            return frame
        wanted = {s.lower() for s in args.states}
        return frame[frame["cluster"].str.lower().isin(wanted)]

    rows = []

    zeta = pd.read_csv(RESEARCH_RESULTS_DIR / "zeta" / "zeta_correspondence.csv")
    zeta["cluster"] = zeta["pop"].map(cluster_of)
    zeta = keep(zeta)
    separation = zeta["A_max_q"] - zeta["B_max_q"]
    for label, a, b in (("docs/27 selection rate vs zeta separation", zeta["rate"], separation),
                        ("docs/23 selection rate vs pie change", zeta["rate"], zeta["pie"])):
        lo, hi, k = cluster_bootstrap(a, b, zeta["cluster"], args.draws)
        rows.append({"claim": label, "r": float(np.corrcoef(a, b)[0, 1]),
                     "lo": lo, "hi": hi, "clusters": k, "rows": len(zeta)})

    mech = pd.read_csv(RESEARCH_RESULTS_DIR / "mechanism" / "mechanism_heldout.csv")
    mech["cluster"] = mech["name"].map(cluster_of)
    mech = keep(mech)
    lo, hi, k = cluster_bootstrap(mech["rbar"], mech["lambda_minus_p"],
                                  mech["cluster"], args.draws)
    rows.append({"claim": "docs/26 held-out rbar vs lambda-p",
                 "r": float(np.corrcoef(mech["rbar"], mech["lambda_minus_p"])[0, 1]),
                 "lo": lo, "hi": hi, "clusters": k, "rows": len(mech)})

    fit = pd.read_csv(RESEARCH_RESULTS_DIR / "sweep" / "sweep_p1_formula_fit.csv")
    lo, hi, k = cluster_bootstrap(fit["cross_flow"], fit["mean_abs_error"],
                                  np.arange(len(fit)), args.draws)
    rows.append({"claim": "docs/11 cross-flow vs error",
                 "r": float(np.corrcoef(fit["cross_flow"], fit["mean_abs_error"])[0, 1]),
                 "lo": lo, "hi": hi, "clusters": k, "rows": len(fit)})

    frame = pd.DataFrame(rows)
    print(frame.round(3).to_string(index=False))
    print("\n  `clusters` is the number of independent populations; `rows` the number of")
    print("  measurements. Where they differ, the interval follows the smaller one.")

    out = research_dir("uncertainty")
    frame.to_csv(out / "correlation_intervals.csv", index=False)
    print(f"\nwrote {out}/correlation_intervals.csv")


if __name__ == "__main__":
    main()
