"""Compare the selection-rate floor against remedies that already exist.

**Individual work, beyond the course submission.**

Documents 19, 21 and 23 all measure the floor against plain ``ExponentiatedGradient``.
That shows the floor does what it was designed to do; it does not show the floor is worth
having, because the field already has answers to levelling down. This runs five arms on
identical splits with identical metrics:

1. ``baseline`` -- unconstrained.
2. ``expgrad_dp`` -- demographic parity alone.
3. ``expgrad_dp_floor`` -- parity plus the selection-rate floor (document 19).
4. ``group_thresholds`` -- per-group thresholds on the unconstrained score. The
   theoretically optimal DP classifier (Corbett-Davies et al. 2017; Menon & Williamson
   2018), and therefore a **bound** rather than a rival: it says how much the reduction's
   search costs relative to solving the constrained problem directly.
5. ``minimax`` -- minimise the worst group's error (Martinez et al. 2020; Diana et al.
   2021). The established way to avoid levelling down *without* imposing parity.

Two asymmetries that must be read with the table rather than discovered afterwards:

* **``group_thresholds`` uses the protected attribute at prediction time.** Nothing else
  here does -- the whole project drops it from the feature matrix. That is a legal and
  practical difference, not a modelling detail, and it is why this arm is a bound rather
  than a recommendation.
* **``minimax`` does not target demographic parity and will not satisfy it.** Its parity
  numbers are reported because hiding them would be worse, not because it is failing at
  something it was trying to do.

Usage:
    python -m src.experiments.run_baselines --dataset adult --seeds 0 1 2 3 4
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from fairlearn.reductions import ExponentiatedGradient

from ..baselines import fit_group_thresholds, fit_minimax
from ..datasets import build as build_dataset
from ..incidence import decompose_gap, flip_counts, outcome_total, people_incidence
from ..levelling_up import demographic_parity_without_shrinking
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL

ARMS = ["baseline", "expgrad_dp", "expgrad_dp_floor", "group_thresholds", "minimax"]

# Arms that see the protected attribute when predicting. Recorded in the output so a
# reader of the CSV alone cannot mistake the comparison for a like-for-like one.
USES_ATTRIBUTE_AT_PREDICT = {"group_thresholds"}

# Arms that are not trying to satisfy demographic parity.
NOT_TARGETING_PARITY = {"baseline", "minimax"}


def fit_arms(split, seed: int, eps: float) -> tuple[dict, dict]:
    baseline = build_model(BASE_MODEL, random_state=seed)
    baseline.fit(split.X_train, split.y_train)

    plain = fit_exponentiated_gradient(
        build_model(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint="demographic_parity", eps=eps,
    )

    target = float(np.mean(baseline.predict(split.X_train)))
    floored = ExponentiatedGradient(
        build_model(BASE_MODEL, random_state=seed),
        constraints=demographic_parity_without_shrinking(target, eps=eps),
        eps=eps,
    )
    floored.fit(split.X_train, split.y_train, sensitive_features=split.a_train)

    thresholded = fit_group_thresholds(
        build_model(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
    )
    minimax, minimax_info = fit_minimax(
        lambda: build_model(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
    )

    predictions = {
        "baseline": baseline.predict(split.X_test),
        "expgrad_dp": plain.predict(split.X_test, random_state=seed),
        "expgrad_dp_floor": floored.predict(split.X_test, random_state=seed),
        "group_thresholds": thresholded.predict(split.X_test, split.a_test),
        "minimax": minimax.predict(split.X_test),
    }
    info = {"floor_target": target,
            "threshold_rate": thresholded.rate,
            "minimax_worst_error": minimax_info["worst_group_error"]}
    return predictions, info


def run_seed(dataset, seed: int, eps: float) -> list[dict]:
    split = prepare(dataset, random_state=seed)
    group_kw = {"privileged": dataset.privileged_value,
                "unprivileged": dataset.unprivileged_value}
    predictions, info = fit_arms(split, seed, eps)
    y_base = predictions["baseline"]

    rows = []
    for arm in ARMS:
        y = predictions[arm]
        scores = evaluate(split.y_test, y, split.a_test, label=arm, **group_kw)
        row = {
            "seed": seed, "arm": arm,
            "uses_attribute_at_predict": arm in USES_ATTRIBUTE_AT_PREDICT,
            "targets_parity": arm not in NOT_TARGETING_PARITY,
            "accuracy": scores["accuracy"],
            "dp_diff": scores["demographic_parity_diff"],
            "eo_diff": scores["equalized_odds_diff"],
            "disparate_impact": scores["disparate_impact"],
            "positives": int(np.asarray(y).sum()),
            **info,
        }
        if arm != "baseline":
            selection = decompose_gap(split.y_test, split.a_test, y_base, y,
                                      **group_kw).loc["selection_rate"]
            flips = flip_counts(split.a_test, y_base, y, **group_kw)
            people = people_incidence(flips)
            totals = outcome_total(y_base, y)
            row |= {
                "dp_closure": selection["closure"],
                "people_share_levelling_down": people["people_share_levelling_down"],
                "lost_per_gained": people["lost_per_gained"],
                "positives_pct_change": totals["pct_change"],
            }
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="adult")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--eps", type=float, default=0.01)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    dataset = build_dataset(args.dataset).load()
    print(f"=== baselines: {dataset.name} ===\n")

    rows = []
    for seed in args.seeds:
        print(f"--- seed {seed} ---", flush=True)
        rows.extend(run_seed(dataset, seed, args.eps))

    runs = pd.DataFrame(rows)
    summary = runs.groupby("arm")[
        ["accuracy", "dp_diff", "eo_diff", "disparate_impact", "positives",
         "positives_pct_change", "people_share_levelling_down", "lost_per_gained"]
    ].mean().round(4).reindex(ARMS)

    print("\n=== mean over seeds ===")
    print(summary.to_string())
    print("\n  group_thresholds sees the protected attribute when predicting; no other arm")
    print("  does. minimax does not target parity, so its dp_diff is not a failure.")

    OUT = output_dir(dataset.name + "_baselines")
    for path in save(OUT, "baselines", {"runs": runs, "summary": summary},
                     params=dict(dataset=args.dataset, seeds=args.seeds, eps=args.eps),
                     force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
