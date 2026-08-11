"""Ablation: hold data, base classifier and metrics fixed; vary only the mitigation.

Produces the full results table from section 7 of the initiation document.

The six rows themselves live in :mod:`src.experiments.methods`, shared with the
who-pays analysis so the two experiments cannot drift into comparing differently
configured models. That module also documents why every row uses logistic regression.

All six methods are in-processing: none modifies, reweights-on-disk, resamples, or
relabels the training data. Only the objective handed to the learner changes.

Usage:
    python -m src.experiments.run_ablation
    python -m src.experiments.run_ablation --seeds 0 1 2 3 4 --eta 5.0
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..datasets.adult import AdultLoader
from ..metrics import evaluate, group_breakdown
from ..preprocessing import prepare
from .methods import BASE_MODEL, METHOD_ORDER, MethodParams, fit_all

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"
ROW_ORDER = METHOD_ORDER


def run_seed(dataset, seed: int, params: MethodParams):
    split = prepare(dataset, random_state=seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }

    predictors, seconds = fit_all(split, seed, params)

    rows, breakdowns = [], {}
    for label, predict in predictors.items():
        y_pred = predict(seed)
        row = evaluate(split.y_test, y_pred, split.a_test, label=label, **group_kw)
        row.update({"seed": seed, "fit_seconds": round(seconds[label], 1)})
        rows.append(row)
        breakdowns[label] = group_breakdown(split.y_test, y_pred, split.a_test, **group_kw)

    return rows, breakdowns


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--eps", type=float, default=0.01, help="ExpGrad fairness slack")
    parser.add_argument("--eta", type=float, default=5.0, help="Prejudice Remover penalty")
    parser.add_argument("--alpha", type=float, default=1.0, help="adversary weight")
    parser.add_argument("--epochs", type=int, default=30, help="adversarial training epochs")
    args = parser.parse_args()

    params = MethodParams(eps=args.eps, eta=args.eta, alpha=args.alpha, epochs=args.epochs)
    dataset = AdultLoader().load()
    print(f"=== ablation on {dataset.name}: base classifier = {BASE_MODEL} ===")
    print(dataset.base_rates().to_string(index=False))

    all_rows, first = [], {}
    for seed in args.seeds:
        print(f"\n--- seed {seed} ---", flush=True)
        rows, breakdowns = run_seed(dataset, seed, params)
        all_rows.extend(rows)
        if not first:
            first = breakdowns

    results = pd.DataFrame(all_rows)
    numeric = ["accuracy", "demographic_parity_diff", "equalized_odds_diff", "disparate_impact"]
    summary = (
        results.groupby("method")[numeric].agg(["mean", "std"]).round(4).reindex(ROW_ORDER)
    )

    print(f"\n=== per-group rates, seed {args.seeds[0]} ===")
    for label in ROW_ORDER:
        print(f"\n[{label}]")
        print(first[label].round(4).to_string())

    print(f"\n=== ablation results over {len(args.seeds)} seeds (mean / std) ===")
    print(summary.to_string())
    print("\nFair at 0: demographic_parity_diff, equalized_odds_diff.  Fair at 1: disparate_impact.")

    # Stability ranking -- ablation question 2. Reported from the metric each method
    # targets where it has one, so a method is judged on its own objective.
    stability = (
        results.groupby("method")[numeric].std().round(4).reindex(ROW_ORDER)
    )
    print("\n=== run-to-run std dev (lower = more stable) ===")
    print(stability.to_string())

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_DIR / "ablation_runs.csv", index=False)
    summary.to_csv(RESULTS_DIR / "ablation_summary.csv")
    print(f"\nwrote {RESULTS_DIR / 'ablation_runs.csv'} and ablation_summary.csv")


if __name__ == "__main__":
    main()
