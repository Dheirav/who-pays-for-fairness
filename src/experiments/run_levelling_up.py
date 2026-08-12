"""Does making "don't shrink the pie" part of the objective actually work?

Document 05's third finding is that every mitigation in the ablation closed the
demographic-parity gap partly by *withdrawing* favourable decisions: the total number of
positive predictions fell by 7.9% to 22.1%, and not one method closed the gap primarily by
extending favourable decisions to the disadvantaged group. That document ends with a claim
it never tested:

    "If you want the gap closed by levelling up, **that has to be part of the objective**
    -- it will not happen by accident."

This tests it, by adding a floor on the overall selection rate alongside the parity
constraint (:mod:`src.levelling_up`). Three arms on identical splits:

1. **baseline** -- unconstrained.
2. **expgrad_dp** -- demographic parity alone, the ablation's winning row.
3. **expgrad_dp_floor** -- demographic parity *and* a floor at the baseline's own
   selection rate, enforced together in one game rather than patched afterwards.

The honest framing, repeated from :mod:`src.levelling_up`: this is **not a new method**.
Agarwal et al. define constraints as linear in the classifier's conditional moments and a
selection-rate floor is one of those, so it sits inside the base paper's framework. What
is new is the question.

What is measured is not only whether the pie survives but **who pays**, using the same
decomposition as :mod:`src.incidence`. A variant that preserved the total while still
taking from the same people would not be levelling up; it would be levelling down with
compensation elsewhere.

Usage:
    python -m src.experiments.run_levelling_up
    python -m src.experiments.run_levelling_up --dataset acs:AL --seeds 0 1 2
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from fairlearn.reductions import ExponentiatedGradient

from ..datasets import build as build_dataset
from ..incidence import decompose_gap, flip_counts, outcome_total, people_incidence
from ..levelling_up import demographic_parity_without_shrinking
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL

ARMS = ["baseline", "expgrad_dp", "expgrad_dp_floor"]


def fit_arms(split, seed: int, eps: float) -> dict[str, np.ndarray]:
    baseline = build_model(BASE_MODEL, random_state=seed)
    baseline.fit(split.X_train, split.y_train)

    plain = fit_exponentiated_gradient(
        build_model(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint="demographic_parity", eps=eps,
    )

    # The floor is the baseline's own selection rate on the training split -- "do not
    # hand out fewer favourable decisions than the unconstrained model would have". Any
    # fixed target would do; this one makes the comparison to the ablation direct.
    target = float(np.mean(baseline.predict(split.X_train)))
    floored = ExponentiatedGradient(
        build_model(BASE_MODEL, random_state=seed),
        constraints=demographic_parity_without_shrinking(target, eps=eps),
        eps=eps,
    )
    floored.fit(split.X_train, split.y_train, sensitive_features=split.a_train)

    return {
        "baseline": baseline.predict(split.X_test),
        "expgrad_dp": plain.predict(split.X_test, random_state=seed),
        "expgrad_dp_floor": floored.predict(split.X_test, random_state=seed),
    }, target


def run_seed(dataset, seed: int, eps: float) -> list[dict]:
    split = prepare(dataset, random_state=seed)
    group_kw = {"privileged": dataset.privileged_value,
                "unprivileged": dataset.unprivileged_value}
    predictions, target = fit_arms(split, seed, eps)
    y_base = predictions["baseline"]

    rows = []
    for arm in ARMS:
        y = predictions[arm]
        scores = evaluate(split.y_test, y, split.a_test, label=arm, **group_kw)
        row = {"seed": seed, "arm": arm, "floor_target": target,
               "accuracy": scores["accuracy"],
               "dp_diff": scores["demographic_parity_diff"],
               "eo_diff": scores["equalized_odds_diff"],
               "disparate_impact": scores["disparate_impact"],
               "positives": int(np.asarray(y).sum())}
        if arm != "baseline":
            selection = decompose_gap(split.y_test, split.a_test, y_base, y,
                                      **group_kw).loc["selection_rate"]
            flips = flip_counts(split.a_test, y_base, y, **group_kw)
            people = people_incidence(flips)
            totals = outcome_total(y_base, y)
            row |= {
                "dp_closure": selection["closure"],
                "share_levelling_down": selection["share_levelling_down"],
                "people_share_levelling_down": people["people_share_levelling_down"],
                "lost_per_gained": people["lost_per_gained"],
                "priv_lost": flips.loc["privileged", "lost"],
                "unpriv_gained": flips.loc["unprivileged", "gained"],
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
    print(f"=== levelling up: {dataset.name} ===\n")

    rows = []
    for seed in args.seeds:
        print(f"--- seed {seed} ---", flush=True)
        rows.extend(run_seed(dataset, seed, args.eps))

    runs = pd.DataFrame(rows)
    summary = runs.groupby("arm")[
        ["accuracy", "dp_diff", "eo_diff", "disparate_impact", "positives",
         "positives_pct_change", "share_levelling_down",
         "people_share_levelling_down", "lost_per_gained"]
    ].mean().round(4).reindex(ARMS)

    print("\n=== mean over seeds ===")
    print(summary.to_string())

    plain = summary.loc["expgrad_dp"]
    floored = summary.loc["expgrad_dp_floor"]
    base = summary.loc["baseline"]
    print("\n" + "=" * 74)
    print(f"  demographic parity   {base['dp_diff']:.4f} -> "
          f"{plain['dp_diff']:.4f} (plain) / {floored['dp_diff']:.4f} (with floor)")
    print(f"  favourable decisions {plain['positives_pct_change']:+.1f}% (plain) / "
          f"{floored['positives_pct_change']:+.1f}% (with floor)")
    print(f"  accuracy cost        {base['accuracy'] - plain['accuracy']:.4f} (plain) / "
          f"{base['accuracy'] - floored['accuracy']:.4f} (with floor)")
    print(f"  share paid by the privileged group, in people:")
    print(f"                       {plain['people_share_levelling_down']:.3f} (plain) / "
          f"{floored['people_share_levelling_down']:.3f} (with floor)")
    print(f"  favourable decisions destroyed per one created:")
    print(f"                       {plain['lost_per_gained']:.2f} (plain) / "
          f"{floored['lost_per_gained']:.2f} (with floor)")
    print("=" * 74)

    OUT = output_dir(dataset.name + "_levelling_up")
    for path in save(OUT, "levelling_up", {"runs": runs, "summary": summary},
                     params=dict(dataset=args.dataset, seeds=args.seeds, eps=args.eps),
                     force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
