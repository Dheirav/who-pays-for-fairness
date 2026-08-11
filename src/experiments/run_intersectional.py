"""Intersectional fairness: does fixing sex leave a Sex x Race subgroup behind?

Not in the initiation document. Every method in the ablation table is constrained on
``sex`` alone, which is the field's default and has a known failure mode: constraints
on marginals can be satisfied while the cells *inside* those marginals stay unfair
(Kearns et al., 2018). This experiment tests that directly by comparing three arms on
the same splits:

1. **baseline**            -- no constraint at all.
2. **expgrad_dp (sex)**    -- the standard setup, and the winning row of the ablation.
3. **expgrad_dp (sex x race)** -- the same algorithm, constrained on the intersection.

Fairlearn's reductions accept a multi-valued sensitive feature directly, so arm 3 is
not a new algorithm; the contribution is the measurement, not the method.

**The result to read first is the reliability report, not the gap.** Sex x Race splits
Adult's test set into ten subgroups, five of which are too small to support a rate
estimate and one of which has *no positive labels at all*, making its true-positive
rate undefined by division rather than by convention. An intersectional analysis that
prints a ten-cell heatmap without saying so is reporting sampling noise as a finding.
The gaps here are therefore quoted twice: over all subgroups, and over only those large
enough to mean something. The distance between those two numbers is the point.

Usage:
    python -m src.experiments.run_intersectional
    python -m src.experiments.run_intersectional --seeds 0 1 2 --eps 0.01
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..datasets import build as build_dataset
from ..intersectional import (
    MIN_RELIABLE_DENOMINATOR,
    combine,
    gaps_overlap,
    max_gap,
    reliability_report,
    subgroup_table,
    worst_off,
)
from ..metrics import demographic_parity_difference
from ..mitigation import fit_exponentiated_gradient
from ..models import build
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


ARMS = ["baseline", "expgrad_dp_sex", "expgrad_dp_intersectional"]


def fit_arm(arm: str, split, seed: int, sensitive_intersectional: np.ndarray, eps: float):
    """Fit one arm and return its test-set predictions."""
    estimator = build(BASE_MODEL, random_state=seed)

    if arm == "baseline":
        return estimator.fit(split.X_train, split.y_train).predict(split.X_test)

    sensitive = split.a_train if arm == "expgrad_dp_sex" else sensitive_intersectional
    model = fit_exponentiated_gradient(
        estimator, split.X_train, split.y_train, sensitive,
        constraint="demographic_parity", eps=eps,
    )
    return model.predict(split.X_test, random_state=seed)


def run_seed(dataset, seed: int, eps: float, *, detail: bool) -> list[dict]:
    split = prepare(dataset, random_state=seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }

    subgroups_train = combine(split.a_train, split.column(dataset, dataset.secondary_attribute, train=True))
    subgroups_test = combine(split.a_test, split.column(dataset, dataset.secondary_attribute))

    rows = []
    for arm in ARMS:
        y_pred = fit_arm(arm, split, seed, subgroups_train, eps)
        table = subgroup_table(split.y_test, y_pred, subgroups_test)

        all_groups = max_gap(table, "selection_rate")
        reliable = max_gap(table, "selection_rate", reliable_only=True)
        bottom, bottom_rate = worst_off(table, "selection_rate")

        # The gerrymandering test: does the sex marginal look fair while the cells
        # inside it do not?
        sex_gap = demographic_parity_difference(y_pred, split.a_test, **group_kw)

        rows.append({
            "seed": seed,
            "arm": arm,
            "accuracy": float(np.mean(y_pred == split.y_test)),
            "sex_dp_gap": sex_gap,
            "intersectional_gap_all": all_groups["gap"],
            "intersectional_gap_reliable": reliable["gap"],
            "gap_inflation": all_groups["gap"] - reliable["gap"],
            "worst_subgroup": bottom,
            "worst_subgroup_rate": bottom_rate,
            "n_unreliable_subgroups": int((~table["reliable"]).sum()),
        })

        if detail:
            print(f"\n[{arm}]")
            print(table[[
                "n", "n_positive_label", "selection_rate", "sr_ci_low", "sr_ci_high",
                "tpr", "reliable",
            ]].round(4).to_string())
            print(f"  sex-only DP gap            : {sex_gap:.4f}")
            print(f"  Sex x Race gap, all 10     : {all_groups['gap']:.4f}  "
                  f"({all_groups['worst']} .. {all_groups['best']})")
            print(f"  Sex x Race gap, reliable {reliable['n_subgroups']} : "
                  f"{reliable['gap']:.4f}  ({reliable['worst']} .. {reliable['best']})")
            if reliable["worst"] and reliable["best"]:
                overlap = gaps_overlap(
                    table, "sr_ci_low", "sr_ci_high", reliable["worst"], reliable["best"]
                )
                print(f"  widest reliable gap is {'NOT ' if not overlap else ''}"
                      f"inside overlapping 95% CIs -> "
                      f"{'not evidence of a real difference' if overlap else 'a real difference'}")

    if detail:
        print(f"\n=== subgroups too small to quote (threshold n >= "
              f"{MIN_RELIABLE_DENOMINATOR} overall and positive-label) ===")
        print(reliability_report(table).round(4).to_string())

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="replace canonical results produced by a different run")
    parser.add_argument("--dataset", default="adult",
                        help="adult | acs | acs:WY | acs:CA,TX")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--eps", type=float, default=0.01)
    args = parser.parse_args()

    dataset = build_dataset(args.dataset).load()
    if dataset.secondary_attribute is None:
        raise SystemExit(f"{dataset.name} declares no secondary attribute to cross with")
    print("=== intersectional fairness: sex x race ===")
    print(f"protected attribute constrained by the ablation: {dataset.protected_attribute}")
    print(f"second attribute examined here: {dataset.secondary_attribute}\n")

    all_rows = []
    for seed in args.seeds:
        print(f"--- seed {seed} ---", flush=True)
        all_rows.extend(run_seed(dataset, seed, args.eps, detail=seed == args.seeds[0]))

    results = pd.DataFrame(all_rows)
    summary = (
        results.groupby("arm")[[
            "accuracy", "sex_dp_gap", "intersectional_gap_all",
            "intersectional_gap_reliable", "gap_inflation", "worst_subgroup_rate",
        ]].mean().round(4).reindex(ARMS)
    )
    summary["worst_subgroup_mode"] = (
        results.groupby("arm")["worst_subgroup"].agg(lambda s: s.mode().iat[0]).reindex(ARMS)
    )

    print(f"\n=== summary over {len(args.seeds)} seeds ===")
    print(summary.to_string())
    print("\nsex_dp_gap                  : the number the ablation table reports.")
    print("intersectional_gap_all      : max-min selection rate over all 10 subgroups.")
    print("intersectional_gap_reliable : the same, over subgroups large enough to")
    print("                              support the estimate. Quote this one.")
    print("gap_inflation               : how much of the headline intersectional gap")
    print("                              is contributed by unmeasurable subgroups.")
    OUT = output_dir(dataset.name)
    for path in save(OUT, "intersectional", {"runs": results, "summary": summary},
                     params=dict(seeds=args.seeds, eps=args.eps), force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
