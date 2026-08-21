"""Arms whose model is worse than doing nothing, and whether the switch point is attribute-specific.

**Individual work, beyond the course submission.**

**Written before any of the arms it scores were run**, and committed before them.

Two separate pre-registrations live here because they share the machinery and were decided
at the same moment; they are reported separately and neither is allowed to rescue the other.

---------------------------------------------------------------------------------------
A1 -- the operating-point sweep works by breaking the model, and that was never controlled
---------------------------------------------------------------------------------------
[Document 32](../../research/docs/32-the-rate-not-the-task.md) varies the selection rate by
moving the classifier's decision threshold. That holds the task exactly fixed, which was the
point -- but it also **degrades the classifier**, and nothing in the design bounded how far.

Counting arms whose baseline accuracy falls below its own **majority-class baseline** --
the accuracy of always predicting the more common label, which is what "doing nothing"
achieves:

| instrument | base rate | arms worse than doing nothing |
|---|---|---|
| COMPAS | 0.53 | 0 of 6 |
| ACS Alabama | 0.31 | **3 of 6** |
| HMDA pooled | 0.73 | **2 of 6** |
| LSAC | 0.89 | **5 of 6** |

This is structural rather than incidental. Pushing the selection rate *down* on a task where
most people already qualify requires a classifier that refuses qualified people, and past some
point that is worse than a constant. It is worst exactly where the base rate is highest --
which is why **LSAC is nearly all bad arms and why HMDA's sweep failed**: the same cause,
found twice without being recognised.

Document 23's exclusion rule does not catch it. That rule drops arms with little *parity gap*
to remove, and on high-base-rate data the parity gap stays large while the model falls apart.

**The rule, fixed here:** an arm is excluded if its baseline accuracy is below
``max(p, 1 - p)`` on its own test labels. No tuning constant; the comparison is to the
trivial predictor, which is the weakest defensible standard.

**A1a -- re-scoring what already exists. POST-HOC, and labelled so.** Every sweep already run
is re-scored under the rule. This cannot be a prediction: the data has been seen. It is
reported as a correction, whatever it does to the published correlations.

**A1b -- the pre-registered, out-of-sample half.** Four HMDA populations the operating-point
route has never touched -- Mississippi alone, Louisiana alone, and the pooled home-improvement
and refinance products -- are swept and scored under the rule *from the start*.

    **Prediction.** On each, after exclusion, the pie change rises with the selection rate at
    ``r >= MIN_R``, the spread clears document 37's guard, and a crossover can be bracketed.

    **The naive alternative it must beat:** "the exclusion does not help -- lending is simply
    a domain where this route does not work". That predicts continued non-monotonicity, or so
    few surviving arms that every population comes back VOID. It is a live possibility: the
    exclusion removes arms, and removing arms from a six-point sweep can leave nothing.

---------------------------------------------------------------------------------------
A2 -- is the switch point a property of the population, or of the protected attribute?
---------------------------------------------------------------------------------------
On COMPAS the two attribute arms disagree at their natural operating points: protecting race
grows the pool by 20.0%, protecting sex shrinks it by 5.1%, on the same people at similar
selection rates. Document 35 tells a practitioner to measure their own crossover; if the
answer depends on which attribute is protected, that instruction is incomplete.

The ACS states have both arms available but have only ever been swept on sex.

    **A2 prediction.** Sweeping Alabama and Oregon on **race**, the crossover bracket
    **overlaps** the one their sex sweep produced. The reasoning: the crossover was argued in
    document 32 to be a property of where the task sits on the selection-rate scale, and the
    scale is a property of the population, not of how it is partitioned.

    **This is a genuine coin-flip and COMPAS points the other way**, which is why it is
    written down. If the brackets are disjoint, the crossover is attribute-specific, document
    35's procedure has to be run per attribute, and document 32's "population-specific"
    becomes "population-and-attribute-specific".

Run:  python -m src.experiments.analyse_calibration --mode rescore
      python -m src.experiments.analyse_calibration --mode attribute --states AL OR
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from .analyse_operating_point import crossover_bracket, load_points_for, op_arm_name_for
from .analyse_threshold import MIN_BASELINE_GAP, MIN_R, MIN_SPAN_PIE

# A1's rule. No tuning constant: the comparison is to the trivial predictor.
def majority_baseline(dataset_spec: str) -> float:
    from ..datasets import build

    rate = float(build(dataset_spec).load().y.mean())
    return max(rate, 1.0 - rate)


def apply_rules(ops: pd.DataFrame, floor: float) -> tuple[pd.DataFrame, dict]:
    """Document 23's parity-gap rule, then A1's accuracy rule. Both reported."""
    ops = ops.copy()
    ops["selection_rate"] = ops["positives_base"] / ops["n_test"]
    parity_ok = ops["dp_base"] >= MIN_BASELINE_GAP
    accuracy_ok = ops["acc_base"] >= floor
    kept = ops[parity_ok & accuracy_ok]
    return kept, {
        "n_arms": len(ops),
        "dropped_parity": int((~parity_ok).sum()),
        "dropped_accuracy": int((parity_ok & ~accuracy_ok).sum()),
        "n_kept": len(kept),
    }


def score(label: str, ops: pd.DataFrame, floor: float) -> dict:
    kept, counts = apply_rules(ops, floor)
    print(f"\n--- {label} --- (majority-class baseline {floor:.3f})")
    print(f"    {counts['n_arms']} arms; {counts['dropped_parity']} dropped on parity gap, "
          f"{counts['dropped_accuracy']} dropped as worse than doing nothing; "
          f"{counts['n_kept']} retained")
    if len(kept) < 3:
        print("    VOID -- too few arms survive to say anything")
        return {"label": label, "void": True, **counts}

    r = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
    spread = float(kept["pie"].max() - kept["pie"].min())
    band = crossover_bracket(kept)
    informative = spread >= MIN_SPAN_PIE
    print(f"    r = {r:+.3f} (bar {MIN_R})  spread {spread:.2f} (bar {MIN_SPAN_PIE})  "
          f"crossover {band}")
    print(f"    -> {'HOLDS' if (r >= MIN_R and informative and band) else 'FAILS' if informative else 'VOID'}")
    return {"label": label, "void": not informative, "r": r, "spread": spread,
            "band_low": None if band is None else band[0],
            "band_high": None if band is None else band[1],
            "holds": bool(r >= MIN_R and informative and band is not None), **counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["rescore", "heldout", "attribute"],
                        default="rescore")
    parser.add_argument("--states", nargs="+", default=["AL", "OR"])
    args = parser.parse_args()

    from .analyse_generalisation import POINTS as GEN_POINTS
    from .analyse_operating_point import HMDA_POINTS, OPERATING_POINTS

    results = []

    if args.mode == "rescore":
        print("=== A1a: re-scoring every existing sweep. POST-HOC, not a prediction. ===")
        targets = [(f"acs:{s}", f"acs_income_{s.lower()}_2018", OPERATING_POINTS)
                   for s in ["AL", "OR", "CT", "KY", "SC"]]
        targets += [("hmda:MS,LA:derived_race", "hmda_ms_la_2018_race", HMDA_POINTS),
                    ("compas", "compas_2016_race", GEN_POINTS["compas"]),
                    ("lawschool", "lawschool_race", GEN_POINTS["lawschool"])]
        for spec, name, points in targets:
            ops = load_points_for(name, points)
            if ops.empty:
                continue
            results.append(score(name, ops, majority_baseline(spec)))

    elif args.mode == "heldout":
        print("=== A1b: the PRE-REGISTERED out-of-sample test, four fresh HMDA populations ===")
        for spec in ["hmda:MS:derived_race", "hmda:LA:derived_race",
                     "hmda:MS,LA:derived_race:improvement",
                     "hmda:MS,LA:derived_race:refinance"]:
            from ..datasets import build
            name = build(spec).name
            ops = load_points_for(name, HMDA_POINTS)
            if ops.empty:
                print(f"\n--- {name} --- no arms yet")
                continue
            results.append(score(name, ops, majority_baseline(spec)))

    else:
        print("=== A2: does the crossover move when the protected attribute changes? ===")
        for state in args.states:
            for attribute, suffix in [("SEX", ""), ("RAC1P", "_rac1p")]:
                spec = f"acs:{state}:{attribute}"
                name = f"acs_income_{state.lower()}_2018{suffix}"
                ops = load_points_for(name, OPERATING_POINTS)
                if ops.empty:
                    print(f"\n--- {name} --- no arms yet")
                    continue
                results.append(score(f"{state}/{attribute}", ops, majority_baseline(spec)))

        bands = {r["label"]: (r.get("band_low"), r.get("band_high"))
                 for r in results if r.get("band_low") is not None}
        print("\nA2 verdict")
        for state in args.states:
            sex, race = bands.get(f"{state}/SEX"), bands.get(f"{state}/RAC1P")
            if not sex or not race:
                print(f"  {state}: undecidable -- one arm set does not bracket a flip")
                continue
            overlap = sex[0] <= race[1] and race[0] <= sex[1]
            print(f"  {state}: sex {sex[0]:.3f}-{sex[1]:.3f} against race "
                  f"{race[0]:.3f}-{race[1]:.3f}  -> "
                  f"{'OVERLAP (as predicted)' if overlap else 'DISJOINT -- attribute-specific'}")

    if results:
        OUT = research_dir("calibration")
        pd.DataFrame(results).to_csv(OUT / f"{args.mode}.csv", index=False)
        print(f"\nwrote {OUT}/{args.mode}.csv")


if __name__ == "__main__":
    main()
