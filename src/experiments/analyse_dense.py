"""Denser sweeps, and a second optimiser tested a way that can work.

**Individual work, beyond the course submission.**

**Written before any of the arms it scores were run**, and committed before them. The only
things measured beforehand are each population's *viable band* -- a property of its scores and
labels, computed with no mitigated arm in existence -- and the points that follow from it.

Closing three items left open by [document 40](../../research/docs/40-the-arms-that-were-worse-than-doing-nothing.md)
and [document 41](../../research/docs/41-two-scope-tests-one-void-by-my-own-error.md).

---------------------------------------------------------------------------
D -- twelve points instead of six, chosen after the exclusion rules existed
---------------------------------------------------------------------------
Six operating points could not survive the parity-gap rule and the accuracy rule together:
Alabama, Kentucky and South Carolina were left with two arms each and went void, and Oregon
kept three. The relationship did not fail there; the design did, because the points were fixed
before either rule was written.

:mod:`src.experiments.viable_points` now picks them from the data: twelve thresholds spread
**evenly in selection rate** across the band where the classifier still beats the trivial
predictor and the rate sits inside [0.05, 0.95]. Evenly in rate rather than in threshold,
because the score distribution is dense in places and equal threshold steps give clustered
rates -- which is how five of LSAC's six arms landed in a region none of them could survive.

**D1 -- the design works.** Each sweepable population retains at least **six** arms after both
exclusion rules. This is the whole point of the redesign, and if it fails the operating-point
route needs abandoning rather than refining.

**D2 -- the relationship holds where it can now be measured.** On each, ``r >= MIN_R``, spread
clears document 37's guard, and a crossover is locatable. Alabama, Kentucky and South Carolina
have **no prior estimate** -- they were void -- so these are fresh measurements, not
re-confirmations.

**D3 -- the crossovers agree with what was already located.** Oregon previously gave
0.362-0.653 and COMPAS 0.485-0.689 under the six-point design. The denser sweeps should
**overlap** those. A disjoint result would mean the located crossover depends on which points
were chosen, which would undermine every crossover in the project.

**D4 -- LSAC is declared unsweepable in advance, and no arms are run there.** Its viable band
spans **0.056** of selection rate against the 0.40 this project requires. Every threshold that
reaches a low rate produces a classifier worse than approving everyone, because 89% of
candidates pass. This is a **prediction that no choice of points fixes it**, and it is the
sharpest available statement of when document 35's procedure cannot be used.

---------------------------------------------------------------------------
P -- the second optimiser, tested a way that is not broken by construction
---------------------------------------------------------------------------
Document 41's post-processing arm was void: ``ThresholdOptimizer`` re-derives its own
thresholds from the estimator's scores, so it never saw the decision rule the sweep was
manipulating and returned an identical model at all six operating points.

The fix is the design document 41 named: **vary the population, not the decision rule.** Run
post-processing at each population's own natural operating point across every population
available, and correlate the baseline selection rate against the change in the pool across
them -- the design of documents 22 and 31, which does not require the method to respect an
imposed threshold.

**P1 -- the prediction.** Across populations under post-processing, the change in the pool
rises with the baseline selection rate at ``r >= MIN_R``.

**The naive alternative, and it is live:** *"the direction is a property of Agarwal's
reduction. Under a structurally different optimiser there is no relationship."* It predicts
|r| < ``MIN_NAIVE_R``. Post-processing equalises group rates by moving thresholds rather than
by reweighting a training objective, and it reads the protected attribute at prediction time,
which puts it in the **attribute-aware** regime that *Backfire*'s theory treats separately from
everything else measured here. There is a real reason it might behave differently.

**P2 -- the comparison.** The same correlation is computed over the same populations under the
reduction, from results already on disk, so "weaker", "stronger" and "absent" can be told
apart rather than asserted.

Run:  python -m src.experiments.analyse_dense --mode dense
      python -m src.experiments.analyse_dense --mode optimiser
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from .analyse_calibration import apply_rules, majority_baseline
from .analyse_operating_point import MIN_NAIVE_R, crossover_bracket, load_points_for
from .analyse_threshold import MIN_R
from .viable_points import points_for

# Populations whose viable band clears MIN_VIABLE_SPAN. LSAC is absent by D4.
DENSE = ["acs:AL", "acs:KY", "acs:SC", "acs:OR", "dutch", "compas"]

# What the six-point design located, for D3.
PRIOR_BANDS = {
    "acs_income_or_2018": (0.362, 0.653),
    "compas_2016_race": (0.485, 0.689),
}

# P: every population with a post-processed arm at its natural operating point.
OPTIMISER_POPULATIONS = [
    "adult", "acs:AL", "acs:OR", "acs:UT", "acs:MS", "acs:WV", "acs:NM", "acs:ND",
    "acs:VT", "acs:WY", "acs:KY", "acs:SC", "acs:CT",
    "hmda:MS:derived_race", "hmda:LA:derived_race", "compas", "dutch", "lawschool",
]


def _arm(name: str, suffix: str = "") -> pd.DataFrame | None:
    # Adult's levelling-up arms live under research/results/adult_levelling_up, not in the
    # course results root: `output_dir` routes on the *stem*, and "adult_levelling_up" is not
    # the course dataset name. Special-casing it to RESULTS_DIR read the wrong file.
    path = RESEARCH_RESULTS_DIR / f"{name}_levelling_up{suffix}" / "levelling_up_runs.csv"
    if not path.exists():
        return None
    return pd.read_csv(path).groupby("arm").mean(numeric_only=True)


def dense_mode() -> list[dict]:
    results = []
    for spec in DENSE:
        info = points_for(spec)
        ops = load_points_for(info["dataset"], info["points"])
        if ops.empty:
            print(f"\n--- {info['dataset']} --- no arms yet")
            continue
        kept, counts = apply_rules(ops, majority_baseline(spec))
        print(f"\n--- {info['dataset']} --- viable band {info['low']:.3f}-{info['high']:.3f}")
        print(f"    {counts['n_arms']} arms; {counts['dropped_parity']} dropped on parity, "
              f"{counts['dropped_accuracy']} on accuracy; {counts['n_kept']} retained "
              f"(D1 needs >= 6)  {'HOLDS' if counts['n_kept'] >= 6 else 'FAILS'}")
        if len(kept) < 3:
            results.append({"dataset": info["dataset"], "void": True, **counts})
            continue
        r = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
        band = crossover_bracket(kept)
        spread = float(kept["pie"].max() - kept["pie"].min())
        print(f"    D2  r = {r:+.3f} (bar {MIN_R})  spread {spread:.2f}  crossover {band}")
        row = {"dataset": info["dataset"], "void": False, "r": r, "spread": spread,
               "n_kept": counts["n_kept"], "d1": counts["n_kept"] >= 6,
               "band_low": None if band is None else band[0],
               "band_high": None if band is None else band[1]}
        prior = PRIOR_BANDS.get(info["dataset"])
        if prior and band:
            agree = band[0] <= prior[1] and prior[0] <= band[1]
            print(f"    D3  against the six-point band {prior}: "
                  f"{'OVERLAP' if agree else 'DISJOINT -- the crossover depends on the points'}")
            row["d3"] = agree
        results.append(row)
    return results


def optimiser_mode() -> list[dict]:
    rows = []
    for spec in OPTIMISER_POPULATIONS:
        from ..datasets import build as build_dataset

        name = "adult" if spec == "adult" else build_dataset(spec).name
        post = _arm(name, "_post")
        base = _arm(name)
        if post is None or base is None:
            continue
        arm = next((a for a in post.index if a.startswith("postprocess")), None)
        if arm is None or "n_test" not in post.columns:
            continue
        rows.append({
            "population": name,
            "rate": float(post.loc["baseline", "positives"] / post.loc["baseline", "n_test"]),
            "pie_post": float(post.loc[arm, "positives_pct_change"]),
            "pie_reduction": float(base.loc["expgrad_dp", "positives_pct_change"])
            if "expgrad_dp" in base.index else np.nan,
            "dp_base": float(post.loc["baseline", "dp_diff"]),
        })

    frame = pd.DataFrame(rows)
    if len(frame) < 4:
        print(f"only {len(frame)} populations with post-processed arms; need more")
        return rows

    kept = frame[frame["dp_base"] >= 0.05]
    print(kept.round(4).to_string(index=False))
    r_post = float(np.corrcoef(kept["rate"], kept["pie_post"])[0, 1])
    paired = kept.dropna(subset=["pie_reduction"])
    r_red = float(np.corrcoef(paired["rate"], paired["pie_reduction"])[0, 1])
    print(f"\nP1  post-processing, across {len(kept)} populations:  r = {r_post:+.3f} "
          f"(bar {MIN_R}; naive alternative beaten at {MIN_NAIVE_R}: "
          f"{abs(r_post) >= MIN_NAIVE_R and r_post > 0})  "
          f"{'HOLDS' if r_post >= MIN_R else 'FAILS'}")
    print(f"P2  the reduction, over the same {len(paired)} populations: r = {r_red:+.3f}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["dense", "optimiser"], default="dense")
    args = parser.parse_args()

    results = dense_mode() if args.mode == "dense" else optimiser_mode()
    if results:
        OUT = research_dir("dense")
        pd.DataFrame(results).to_csv(OUT / f"{args.mode}.csv", index=False)
        print(f"\nwrote {OUT}/{args.mode}.csv")


if __name__ == "__main__":
    main()
