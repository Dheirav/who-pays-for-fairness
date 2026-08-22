"""The crossover residual, pre-registered: can anything predict where a population crosses?

**Individual work, beyond the course submission.**

**This file is committed before any of the arms it scores exist.** The states, every
threshold, the two candidates, their predicted directions, the bars, the guards and the
naive baseline are all fixed here.

What is being converted
-----------------------
[Document 44](../../research/docs/44-how-much-and-where-two-concessions-tested.md)'s C2
screen returned two correlations with the crossover's location — between-group gap at
+0.724 and sample size at +0.865 — and refused to report them as findings, because at four
populations they are collinear at +0.947 and neither is distinguishable from chance. The
screen's own verdict: *a hypothesis worth testing when there are fifteen.* This is that
test.

The design, and why ACS states
------------------------------
Ten never-swept states, chosen by a viable-band prescreen (one seed-0 baseline fit each; no
mitigated arm existed when they were chosen): TX, NY, FL, IL, PA, OH, NJ, VA, MA, LA.
Held at one instrument deliberately: state size and group gap vary **independently** across
states, which is what breaks the +0.947 collinearity — the Dutch census could not be big
without also being unequal; Texas can. FL, OH and LA are marginal (bands top out at
0.62–0.64), and a crossover they fail to bracket is recorded as *unlocated*, never imputed.

Every threshold below was fixed from the seed-0 baseline's scores — the same information
``points_for`` uses — restricted to the transition window (seed-0 rate in [0.22, 0.72]),
because [document 50](../../research/docs/50-the-divergence-is-who-moves.md) showed the
deep-tail arms are direction-unreliable and the low arms locate nothing.

The candidates, with their directions
-------------------------------------
* **R1 — the between-group gap**, measured as the baseline demographic-parity difference at
  the population's natural operating point. Predicted direction: **positive** (larger gap,
  higher crossover), as in C2.
* **R2 — sample size**, measured as the test-split size. Predicted direction: **positive**,
  as in C2. It is carried although no mechanism recommends it, because killing it cleanly
  is worth as much as confirming the gap.

**A candidate holds only if BOTH:** Spearman rho with the located crossover mid-points is at
least ``MIN_RHO = +0.70`` (C2's own screen bar), across the old four populations plus every
newly located crossover, **and** it beats the naive baseline below.

**The naive baseline, named in advance:** the constant prior **0.54** (document 44). A
candidate's leave-one-out linear fit must have lower mean absolute error than predicting
0.54 for every population. A predictor that correlates but cannot out-predict the constant
is document 26's failure mode and will be reported as such.

**R3 — the design check.** |r(gap, size)| across the scored populations is reported; the
decorrelation the design exists for has failed if it exceeds 0.5, and that is reported
before either verdict.

Guards, all fixed now
---------------------
* Arms are retained under the standing exclusions: baseline parity gap >= 0.05 and baseline
  accuracy >= max(p, 1-p) computed from the population's own label.
* A population's sweep is **void** if its retained arms' pool changes span less than
  ``SPREAD_GUARD = 2.0`` points (document 37).
* The crossover is the midpoint of ``crossover_bracket`` over retained arms; no bracket
  means **unlocated** and the population contributes nothing.
* Fewer than ``MIN_NEW = 6`` newly located crossovers voids the test as underpowered — no
  verdict is claimed either way.
* Five seeds per arm, eps = 0.01, the default learner; the old four populations' crossovers
  and predictors are **recomputed from their stored arms under these same rules**, not
  quoted from prose.

Run:  python -m src.experiments.analyse_residual
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

MIN_RHO = 0.70
SPREAD_GUARD = 2.0
MIN_NEW = 6
CONSTANT_PRIOR = 0.54

# state -> thresholds, fixed from seed-0 scores before any mitigated arm existed.
SWEEP = {
    "TX": [0.115, 0.17, 0.23, 0.295, 0.365, 0.435, 0.5, 0.57, 0.635],
    "NY": [0.2, 0.275, 0.36, 0.44, 0.52, 0.595, 0.67],
    "FL": [0.165, 0.21, 0.26, 0.305, 0.36, 0.42, 0.475, 0.535],
    "IL": [0.145, 0.21, 0.285, 0.36, 0.435, 0.51, 0.58, 0.65],
    "PA": [0.14, 0.19, 0.245, 0.305, 0.365, 0.43, 0.495, 0.555, 0.62],
    "OH": [0.155, 0.205, 0.26, 0.315, 0.37, 0.43, 0.49, 0.55],
    "NJ": [0.23, 0.35, 0.47, 0.575, 0.67, 0.75],
    "VA": [0.15, 0.235, 0.33, 0.425, 0.525, 0.62, 0.705],
    "MA": [0.22, 0.345, 0.46, 0.56, 0.655, 0.735],
    "LA": [0.17, 0.215, 0.265, 0.32, 0.375, 0.425, 0.48, 0.54],
}

# The four populations with located crossovers, rescored under the same rules.
EXISTING = {
    "compas_2016_race": "compas",
    "dutch_2001_sex": "dutch",
    "acs_income_sc_2018": "acs:SC",
    "acs_income_or_2018": "acs:OR",
}


def read_runs(name: str) -> pd.DataFrame | None:
    path = RESEARCH_RESULTS_DIR / name / "levelling_up_runs.csv"
    return pd.read_csv(path) if path.exists() else None


def sibling_n_test(stem: str) -> float | None:
    for directory in RESEARCH_RESULTS_DIR.glob(f"{stem}_levelling_up*"):
        runs = read_runs(directory.name)
        if runs is not None and "n_test" in runs.columns:
            return float(runs["n_test"].mean())
    return None


def natural_predictors(stem: str) -> tuple[float, float] | None:
    """(gap, n_test) at the natural operating point, from the plain arm."""
    runs = read_runs(f"{stem}_levelling_up")
    if runs is None:
        return None
    base = runs[runs["arm"] == "baseline"]
    if base.empty:
        return None
    n = (float(base["n_test"].mean()) if "n_test" in runs.columns
         else sibling_n_test(stem))
    if n is None:
        return None
    return float(base["dp_diff"].mean()), float(n)


def locate(stem: str, spec: str, points: list[float]) -> dict:
    """One population's crossover, through the exact pipeline documents 42/45 used:
    ``load_points_for`` reads only the named points, ``apply_rules`` applies both standing
    exclusions, ``crossover_bracket`` brackets the sign change."""
    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import crossover_bracket, load_points_for

    result: dict = {"population": stem}
    preds = natural_predictors(stem)
    if preds:
        result["gap"], result["n_test"] = preds
    ops = load_points_for(stem, points)
    if ops.empty:
        return result | {"status": "no arms", "arms_retained": 0}
    kept, counts = apply_rules(ops, majority_baseline(spec))
    result["arms_retained"] = counts["n_kept"]
    if kept.empty:
        return result | {"status": "all arms excluded"}
    if float(kept["pie"].max() - kept["pie"].min()) < SPREAD_GUARD:
        return result | {"status": "void (spread guard)"}
    bracket = crossover_bracket(kept)
    if bracket is None:
        return result | {"status": "unlocated"}
    return result | {"status": "located",
                     "crossover": float(np.mean(bracket)),
                     "bracket_lo": bracket[0], "bracket_hi": bracket[1]}


def loo_mae(x: np.ndarray, y: np.ndarray) -> float:
    """Leave-one-out MAE of the one-variable linear fit."""
    errors = []
    for i in range(len(y)):
        keep = np.arange(len(y)) != i
        slope, intercept = np.polyfit(x[keep], y[keep], 1)
        errors.append(abs(y[i] - (slope * x[i] + intercept)))
    return float(np.mean(errors))


def main() -> None:
    from scipy.stats import spearmanr

    from .viable_points import points_for

    # Existing populations are rescored on their own dense point sets — the same
    # deterministic seed-0 selection documents 42/45 scored; new states on the sealed
    # thresholds above.
    rows = [locate(stem, spec, points_for(spec)["points"])
            for stem, spec in EXISTING.items()]
    rows += [locate(f"acs_income_{s.lower()}_2018", f"acs:{s}", SWEEP[s]) for s in SWEEP]
    frame = pd.DataFrame(rows)
    print(frame.round(4).to_string(index=False))

    located = frame[frame.get("status") == "located"].dropna(subset=["gap", "n_test"])
    new = located[~located["population"].isin(EXISTING)]
    print(f"\nlocated: {len(located)} of {len(frame)} ({len(new)} new; "
          f"MIN_NEW = {MIN_NEW})")
    if len(new) < MIN_NEW:
        print("UNDERPOWERED — no verdict is claimed, as pre-registered")
    else:
        y = located["crossover"].to_numpy()
        constant_mae = float(np.mean(np.abs(y - CONSTANT_PRIOR)))
        print(f"\nconstant prior {CONSTANT_PRIOR}: MAE {constant_mae:.4f}")
        for name, column in (("R1 gap", "gap"), ("R2 size", "n_test")):
            x = located[column].to_numpy()
            rho = float(spearmanr(x, y).statistic)
            mae = loo_mae(x, y)
            holds = rho >= MIN_RHO and mae < constant_mae
            print(f"{name}: rho {rho:+.3f} (bar {MIN_RHO:+.2f})  LOO-MAE {mae:.4f} "
                  f"({'beats' if mae < constant_mae else 'LOSES to'} the constant)  "
                  f"{'HOLDS' if holds else 'FAILS'}")
        r = float(np.corrcoef(located["gap"], located["n_test"])[0, 1])
        print(f"R3 design check: |r(gap, size)| = {abs(r):.3f} "
              f"({'decorrelated' if abs(r) < 0.5 else 'STILL COLLINEAR — verdicts void'})")

    OUT = research_dir("residual")
    frame.round(6).to_csv(OUT / "residual.csv", index=False)
    print(f"\nwrote {OUT}/residual.csv")


if __name__ == "__main__":
    main()
