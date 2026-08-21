"""Is it the selection rate, or is it how hard the task is?

**Individual work, beyond the course submission.**

**Written before any operating-point arm was run**, and committed before them. Only the
manipulation check below had been measured when this file was written: the achievable
selection-rate range, which decided the six thresholds. No mitigated arm existed.

The crack this closes
---------------------
[Document 23](../../research/docs/23-the-selection-rate-sets-the-direction.md) reaches a
selection rate by **moving the income cutoff**. That is a single-factor design in the sense
that rows, features and groups are provably identical across arms -- and
``tests/test_acs_threshold.py`` asserts it -- but the factor it moves is the **label**. A
different cutoff is a different prediction problem: "earns over $100,000" is not merely a
rarer version of "earns over $20,000", it is a harder one, with a different Bayes error and
a different score distribution.

So document 23 cannot distinguish two explanations:

1. the **selection rate** sets the direction of levelling down, or
2. the **difficulty of the task** sets it, and the selection rate merely moves with it.

Both predict everything document 23 observed. And the second would explain the discrepancy
that [document 31](../../research/docs/31-the-crossover-on-natural-data.md) reports and does
not resolve: a natural crossover at 0.64-0.77 where the cutoff sweep put it at 0.25-0.60. If
the crossover is a property of the *route* to a selection rate rather than of the rate
itself, two routes should land in two places -- which is exactly what was seen.

The design
----------
Hold the label fixed and move **where the fitted model draws its line**
(:class:`src.models.ThresholdedClassifier`). One state, one cutoff, one feature set, one
label, one population. The learning problem is *identical* across arms -- the same fitted
scores, in fact -- and only the operating point changes.

This is a strictly stronger single-factor manipulation than document 23's, because document
23 changes the label and this changes nothing at all except the decision rule.

The six thresholds were chosen to reproduce document 23's Alabama selection rates as closely
as the score distribution allows, measured before any arm was run:

    threshold   0.02   0.06   0.16   0.49   0.72   0.87
    doc 23      0.890  0.760  0.598  0.252  0.099  0.029   (by income cutoff)

so the two axes are compared over the same range rather than over convenient ones.

What could make this uninformative, stated up front
---------------------------------------------------
At extreme thresholds the classifier approaches a constant and has little group disparity
left to remove, so those arms may be excluded by the same rule document 23 used. That is
expected and is not a result. If it removes so many arms that fewer than four remain, the
sweep is **void** rather than negative.

The naive alternative, named in advance
---------------------------------------
    **"The direction is set by how hard the task is. Move only the decision rule and
    nothing happens: no relationship, or no sign change."**

That is the live hypothesis this exists to test, not a straw man -- it is exactly what
document 31's non-overlapping crossover hints at. If it wins, document 23's headline needs
restating as a claim about label difficulty, and that is the finding.

Stated in advance, so they can fail
-----------------------------------
**O0 -- manipulation check.** The baseline selection rate falls monotonically as the
threshold rises and spans at least ``MIN_SPAN``. Measured already at 0.017-0.832, so this is
a guard against a pipeline error rather than a real risk.

**O1 -- the prediction.** Across retained arms the change in favourable decisions rises with
the baseline selection rate at ``r >= MIN_R``. Beats the naive alternative only if
``|r| >= 0.30`` in the predicted direction.

**O2 -- the sign flips.** The lowest-rate retained arm shrinks the pool and the highest grows
it. Without this the effect merely weakens, which is much weaker than document 23 claims.

**O3 -- the decisive one: do the two axes agree on *where*?** The crossover bracket along the
operating-point axis -- the interval between the highest-rate arm that still shrinks the pool
and the lowest-rate arm that grows it -- **overlaps** document 23's bracket computed the same
way from the income-cutoff arms of the same state.

*If O1 and O2 hold and O3 holds*, the selection rate is the operative variable, the two
routes are interchangeable, and document 31's discrepancy is a domain difference rather than
an artifact of the manipulation.

*If O1 and O2 hold but O3 fails*, the rate predicts the **direction** but not **where the
transition sits**, the route matters, and document 23's "crossover between 0.25 and 0.60"
must be withdrawn as a number while its relationship survives. That is a real cost and it is
to be reported as one.

*If O1 fails*, difficulty rather than rate is doing the work in document 23, and the
project's headline needs rewriting. This is the outcome that would hurt most, which is why
it is written down here first.

Validating the procedure on the domain it is aimed at
-----------------------------------------------------
**Written before any HMDA operating-point arm was run.** Document 35 tells a practitioner to
locate their own crossover by sweeping their deployed model's decision threshold. That advice
is only worth giving if the route finds the crossover a *different* method already located in
the same domain.

[Document 31](../../research/docs/31-the-crossover-on-natural-data.md) put the mortgage
crossover between **0.643 and 0.773**, by comparing five real loan purposes rather than by
manipulating anything. Pooling Mississippi and Louisiana on the race arm gives a score
distribution spanning selection rates 0.348 to 0.947, measured before any arm was run, which
brackets that band comfortably.

**H1 -- the prediction.** The operating-point crossover on pooled HMDA lending **overlaps
document 31's 0.643-0.773 band**.

**The naive alternative it must beat:** "the operating-point route finds whatever crossover
the ACS data had (0.25-0.60), because the route rather than the domain sets it." That is the
live alternative -- it is what O3 rules out *within* a population but not *across* domains --
and it predicts a bracket sitting well below 0.643.

*If H1 holds*, two unrelated methods agree on the lending domain's crossover, and document
35's procedure is validated where it matters.

*If H1 fails*, the procedure locates something other than the crossover the natural split
found, and document 35's central recommendation must be withdrawn or heavily qualified. That
is the more costly outcome and it is written here first.

Run:  python -m src.experiments.analyse_operating_point --states AL OR
      python -m src.experiments.analyse_operating_point --dataset hmda:MS,LA:derived_race
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from .analyse_threshold import (
    MIN_BASELINE_GAP,
    MIN_R,
    MIN_SPAN,
    THRESHOLDS,
    arm_name,
    partial_corr,
)
from .run_levelling_up import model_code

BASE, PLAIN = "baseline", "expgrad_dp"

# Chosen to mirror document 23's Alabama selection rates, from the score distribution
# measured before any arm was run. See the module docstring.
OPERATING_POINTS = [0.02, 0.06, 0.16, 0.49, 0.72, 0.87]

# Chosen the same way for the lending data, whose scores sit far higher: these span
# selection rates 0.348 to 0.826 and bracket document 31's natural band of 0.643-0.773.
HMDA_POINTS = [0.92, 0.85, 0.75, 0.65, 0.55, 0.45]

# The band document 31 located by comparing real loan purposes, which H1 must overlap.
NATURAL_HMDA_BAND = (0.643, 0.773)

# O1: the naive alternative wins unless the correlation clears this in the right direction.
MIN_NAIVE_R = 0.30


def op_arm_name(state: str, threshold: float) -> str:
    """Where ``run_levelling_up --model logistic_regression@<t>`` writes, per its own rule."""
    return f"{arm_name(state, 50_000)}_{model_code(f'logistic_regression@{threshold}')}"


def op_arm_name_for(dataset_name: str, threshold: float) -> str:
    """The same rule for any dataset, addressed by its loader's own name."""
    return (f"{dataset_name}_levelling_up"
            f"_{model_code(f'logistic_regression@{threshold}')}")


def load_points_for(dataset_name: str, points: list[float]) -> pd.DataFrame:
    """Operating-point arms for a dataset that is not an ACS state."""
    rows = []
    for t in points:
        mean = _load(RESEARCH_RESULTS_DIR / op_arm_name_for(dataset_name, t)
                     / "levelling_up_runs.csv")
        if mean is None:
            continue
        rows.append({
            "axis": "operating_point", "knob": t,
            "positives_base": mean.loc[BASE, "positives"],
            "n_test": mean.loc[BASE, "n_test"] if "n_test" in mean.columns else np.nan,
            "dp_base": mean.loc[BASE, "dp_diff"],
            "pie": mean.loc[PLAIN, "positives_pct_change"],
            "exchange": mean.loc[PLAIN, "lost_per_gained"],
            "acc_base": mean.loc[BASE, "accuracy"],
        })
    return pd.DataFrame(rows)


def _load(path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    mean = pd.read_csv(path).groupby("arm").mean(numeric_only=True)
    return mean if {PLAIN, BASE}.issubset(mean.index) else None


def load_operating_points(state: str, points: list[float]) -> pd.DataFrame:
    rows = []
    for t in points:
        mean = _load(RESEARCH_RESULTS_DIR / op_arm_name(state, t) / "levelling_up_runs.csv")
        if mean is None:
            continue
        rows.append({
            "axis": "operating_point", "knob": t,
            "positives_base": mean.loc[BASE, "positives"],
            "n_test": mean.loc[BASE, "n_test"] if "n_test" in mean.columns else np.nan,
            "dp_base": mean.loc[BASE, "dp_diff"],
            "pie": mean.loc[PLAIN, "positives_pct_change"],
            "exchange": mean.loc[PLAIN, "lost_per_gained"],
            "acc_base": mean.loc[BASE, "accuracy"],
        })
    return pd.DataFrame(rows)


def load_cutoffs(state: str) -> pd.DataFrame:
    """Document 23's arms for the same state, so the two axes are compared like for like."""
    rows = []
    for cutoff in THRESHOLDS:
        mean = _load(RESEARCH_RESULTS_DIR / arm_name(state, cutoff) / "levelling_up_runs.csv")
        if mean is None:
            continue
        rows.append({
            "axis": "income_cutoff", "knob": cutoff,
            "positives_base": mean.loc[BASE, "positives"],
            "n_test": mean.loc[BASE, "n_test"] if "n_test" in mean.columns else np.nan,
            "dp_base": mean.loc[BASE, "dp_diff"],
            "pie": mean.loc[PLAIN, "positives_pct_change"],
            "exchange": mean.loc[PLAIN, "lost_per_gained"],
            "acc_base": mean.loc[BASE, "accuracy"],
        })
    frame = pd.DataFrame(rows)
    if not frame.empty and frame["n_test"].isna().any():
        # Every cutoff arm predates the recorded denominator, so there is no sibling to
        # borrow from and the size has to come from the experiment that does record it --
        # the same route `analyse_threshold.attach_selection_rate` takes. Getting this
        # wrong is silent: the rates come out NaN and the crossover comparison reports
        # "disjoint" for two brackets it never actually computed.
        from .analyse_levelling_up import test_size
        size = test_size(arm_name(state, 50_000))
        frame["n_test"] = frame["n_test"].fillna(size)
    return frame


def crossover_bracket(frame: pd.DataFrame) -> tuple[float, float] | None:
    """The interval the sign change is known to sit inside.

    The highest selection rate that still shrinks the pool, and the lowest that grows it.
    Returns ``None`` when the arms do not bracket a sign change at all.
    """
    frame = frame.dropna(subset=["selection_rate", "pie"])
    below = frame[frame["pie"] < 0]["selection_rate"]
    above = frame[frame["pie"] > 0]["selection_rate"]
    if below.empty or above.empty or below.max() >= above.min():
        return None
    return float(below.max()), float(above.min())


def verdict(ops: pd.DataFrame, cuts: pd.DataFrame) -> dict:
    print(ops.round(4).to_string(index=False))

    span = ops["selection_rate"].max() - ops["selection_rate"].min()
    monotone = (ops.sort_values("knob")["selection_rate"].is_monotonic_decreasing)
    o0 = monotone and span >= MIN_SPAN
    print(f"\nO0  the operating point moves the selection rate  -> {'HOLDS' if o0 else 'FAILS'}")
    print(f"      {ops['selection_rate'].min():.3f} to {ops['selection_rate'].max():.3f} "
          f"(span {span:.3f}, bar {MIN_SPAN}); monotone in the threshold: {monotone}")
    if not o0:
        print("      the design does not vary what the conjecture is about; stopping")
        return {"void": True}

    kept = ops[ops["dp_base"] >= MIN_BASELINE_GAP]
    dropped = ops[ops["dp_base"] < MIN_BASELINE_GAP]
    print(f"\n    arms below a baseline parity gap of {MIN_BASELINE_GAP}: {len(dropped)} "
          f"excluded, by document 23's rule")
    for _, row in dropped.iterrows():
        print(f"      threshold {row['knob']}: dp_base {row['dp_base']:.4f}, "
              f"selection rate {row['selection_rate']:.3f}")
    if len(kept) < 4:
        print(f"\nVOID  only {len(kept)} arms retained; the sweep cannot answer the question")
        return {"void": True}

    r1 = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
    o1 = r1 >= MIN_R
    beats_naive = r1 >= MIN_NAIVE_R
    print(f"\nO1  pie change rises with the selection rate      -> {'HOLDS' if o1 else 'FAILS'}")
    print(f"      r = {r1:+.3f} over {len(kept)} arms  (bar {MIN_R}; naive alternative "
          f"beaten at {MIN_NAIVE_R}: {beats_naive})")
    print(f"      partial r holding the baseline parity gap fixed = "
          f"{partial_corr(kept['selection_rate'], kept['pie'], kept['dp_base']):+.3f}")

    lowest = kept.loc[kept["selection_rate"].idxmin()]
    highest = kept.loc[kept["selection_rate"].idxmax()]
    o2 = lowest["pie"] < 0 < highest["pie"]
    print(f"\nO2  the sign flips across the range               -> {'HOLDS' if o2 else 'FAILS'}")
    print(f"      lowest  rate {lowest['selection_rate']:.3f}: pie {lowest['pie']:+.2f}%")
    print(f"      highest rate {highest['selection_rate']:.3f}: pie {highest['pie']:+.2f}%")

    r3 = float(np.corrcoef(kept["selection_rate"], kept["exchange"])[0, 1])
    print(f"      exchange rate agrees: r = {r3:+.3f}")

    kept_cuts = cuts[cuts["dp_base"] >= MIN_BASELINE_GAP] if not cuts.empty else cuts
    op_band = crossover_bracket(kept)
    cut_band = crossover_bracket(kept_cuts) if not kept_cuts.empty else None

    print(f"\nO3  do the two routes agree on *where* it crosses?")
    print(f"      operating point : {op_band}")
    print(f"      income cutoff   : {cut_band}   (document 23's route, same state)")
    if op_band is None or cut_band is None:
        o3 = None
        print("      one route does not bracket a sign change; O3 is undecidable, not failed")
    else:
        o3 = op_band[0] <= cut_band[1] and cut_band[0] <= op_band[1]
        print(f"      -> {'OVERLAP: the routes agree' if o3 else 'DISJOINT: the routes disagree'}")

    print("\n" + "=" * 78)
    if o1 and o2 and o3:
        print("The selection rate is the operative variable, not the difficulty of the task.")
        print("Moving only the decision rule reproduces both the direction and the location,")
        print("so document 23's two candidate explanations separate in its favour, and")
        print("document 31's discrepancy is a difference between domains rather than an")
        print("artifact of how the rate was manufactured.")
    elif o1 and o2 and o3 is False:
        print("The rate predicts the DIRECTION along both routes but the two disagree on")
        print("WHERE the transition sits. The crossover is therefore a property of the route")
        print("as well as of the rate, 'between 0.25 and 0.60' must be withdrawn as a")
        print("number, and document 31's non-overlapping band is explained rather than")
        print("merely disclosed. The relationship survives; the constant does not.")
    elif not o1:
        print("Moving only the decision rule does NOT reproduce the relationship. Document")
        print("23's effect travels with the label's difficulty rather than with the")
        print("selection rate, and the project's headline must be restated. This is the")
        print("outcome the pre-registration named as most costly, and it is reported as it")
        print("stands.")
    else:
        print("Mixed: read O1-O3 individually rather than as a verdict.")
    print("=" * 78)

    return {"void": False, "r_pie": r1, "o0": o0, "o1": o1, "o2": o2, "o3": o3,
            "beats_naive": beats_naive, "n_kept": len(kept),
            "op_band": op_band, "cut_band": cut_band}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=["AL"])
    parser.add_argument("--points", type=float, nargs="+", default=OPERATING_POINTS)
    args = parser.parse_args()

    # Per state, never pooled. O3 asks where the crossover sits, and that is a property of
    # a population -- Alabama's and Oregon's differ. Pooling would interleave two brackets
    # into one meaningless interval and hide the very difference the comparison is for.
    written, results = [], {}
    for state in args.states:
        ops = load_operating_points(state, args.points)
        if ops.empty:
            print(f"no operating-point arms for {state}; run\n"
                  f"  python -m src.experiments.run_levelling_up --dataset acs:{state} "
                  f"--model logistic_regression@0.49")
            continue
        cuts = load_cutoffs(state)
        for frame in (ops, cuts):
            if not frame.empty:
                frame["selection_rate"] = frame["positives_base"] / frame["n_test"]
        print(f"=== operating point against income cutoff on {state} ===\n")
        results[state] = verdict(ops, cuts)
        ops["state"] = cuts["state"] = state
        written.append(pd.concat([ops, cuts]))
        print()

    if not written:
        raise SystemExit("no operating-point arms found for any requested state")

    OUT = research_dir("operating_point")
    pd.concat(written).round(6).to_csv(OUT / "operating_point_arms.csv", index=False)
    pd.DataFrame(results).to_csv(OUT / "operating_point_verdict.csv")
    print(f"wrote {OUT}/operating_point_arms.csv")


if __name__ == "__main__":
    main()
