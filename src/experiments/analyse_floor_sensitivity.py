"""The domain-table correlations at every parity-gap floor, not just the published one.

**Individual work, beyond the course submission. Post-hoc re-scoring of stored arms.**

The third council (and the second's statistician) made the same point about Table
tab:domains that the sensitivity table already concedes for the exploratory states: the
0.05 gap floor was tuned in-sample, so a correlation reported only at 0.05 is
conditioned on a chosen filter. This re-scores each domain-table population's own arm
set --- the identical arms, loaded the way their original analyses loaded them --- at
floors 0.02 / 0.05 / 0.08 / 0.10, with the accuracy rule (which has no tuning constant)
applied throughout. What must hold for the table to be trustworthy: the sign and rough
size of r should not be a property of the floor.

Run:  python -m src.experiments.analyse_floor_sensitivity
      python -m src.experiments.analyse_floor_sensitivity --dataset dutch
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir
from .analyse_calibration import majority_baseline
from .analyse_generalisation import POINTS as GEN_POINTS
from .analyse_operating_point import HMDA_POINTS, load_cutoffs, load_points_for

FLOORS = (0.02, 0.05, 0.08, 0.10)


def alabama_arms() -> pd.DataFrame:
    """Document 23's six income-cutoff arms, each its own label and therefore its own
    trivial-predictor floor."""
    ops = load_cutoffs("AL")
    ops["floor"] = [majority_baseline(f"acs:AL:SEX:{int(knob)}")
                    for knob in ops["knob"]]
    return ops


def op_arms(spec: str, stem: str, points: list[float]) -> pd.DataFrame:
    ops = load_points_for(stem, points)
    ops["floor"] = majority_baseline(spec)
    return ops


def score(label: str, ops: pd.DataFrame) -> list[dict]:
    ops = ops.copy()
    ops["selection_rate"] = ops["positives_base"] / ops["n_test"]
    ops = ops[ops["acc_base"] >= ops["floor"]]
    rows = []
    for floor in FLOORS:
        kept = ops[ops["dp_base"] >= floor]
        r = (float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
             if len(kept) >= 3 else float("nan"))
        rows.append({"population": label, "gap_floor": floor,
                     "retained": len(kept), "r": r})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one domain-table row (default: all)")
    args = parser.parse_args()

    populations = {
        "ACS Alabama (label route)": alabama_arms,
        "HMDA MS+LA pooled": lambda: op_arms(
            "hmda:MS,LA:derived_race", "hmda_ms_la_2018_race", HMDA_POINTS),
        "COMPAS race": lambda: op_arms(
            "compas", "compas_2016_race", GEN_POINTS["compas"]),
        "Dutch sex": lambda: op_arms(
            "dutch", "dutch_2001_sex", GEN_POINTS["dutch"]),
    }
    rows = []
    for label, loader in populations.items():
        if args.dataset and args.dataset.lower() not in label.lower():
            continue
        rows.extend(score(label, loader()))
    frame = pd.DataFrame(rows)
    print(frame.round(3).to_string(index=False))

    OUT = research_dir("verdicts")
    frame.round(6).to_csv(OUT / "domains_floor_sensitivity.csv", index=False)
    print(f"\nwrote {OUT}/domains_floor_sensitivity.csv")


if __name__ == "__main__":
    main()
