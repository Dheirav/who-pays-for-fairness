"""Baseline: unmitigated ERM, the first row of the results table.

Trains the base classifiers with no fairness intervention and reports accuracy plus
the three fairness metrics. This is the reference every mitigation method is measured
against, and on its own it is the project's evidence that the bias exists at all.

Runs over multiple seeds by default. A single run cannot support any claim about
stability, and the ablation asks explicitly which methods are stable -- so variance
is collected from the baseline onward rather than retrofitted later.

Usage:
    python -m src.experiments.run_baseline
    python -m src.experiments.run_baseline --seeds 1 2 3 4 5 --include-protected
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ..datasets import build as build_dataset
from ..metrics import crosscheck_against_fairlearn, evaluate, group_breakdown
from ..models import MODELS, build
from ..preprocessing import prepare
from ..results_io import output_dir, save

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"



def run_once(dataset, model_name: str, seed: int) -> tuple[dict, pd.DataFrame]:
    split = prepare(dataset, random_state=seed)
    estimator = build(model_name, random_state=seed)
    estimator.fit(split.X_train, split.y_train)
    y_pred = estimator.predict(split.X_test)

    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }
    crosscheck_against_fairlearn(split.y_test, y_pred, split.a_test, **group_kw)

    row = evaluate(split.y_test, y_pred, split.a_test, label=model_name, **group_kw)
    row["seed"] = seed
    breakdown = group_breakdown(split.y_test, y_pred, split.a_test, **group_kw)
    return row, breakdown


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="replace canonical results produced by a different run")
    parser.add_argument("--dataset", default="adult",
                        help="adult | acs | acs:WY | acs:CA,TX")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--models", nargs="+", default=sorted(MODELS), choices=sorted(MODELS))
    parser.add_argument(
        "--include-protected",
        action="store_true",
        help="give the model the protected attribute as an input feature",
    )
    args = parser.parse_args()

    dataset = build_dataset(args.dataset).load(
        include_protected_in_features=args.include_protected)

    print(f"=== dataset: {dataset.name} ({dataset.n_samples:,} rows) ===")
    print(json.dumps(dataset.notes, indent=2, default=str))
    print("\n=== base rates (the disparity the model learns from) ===")
    print(dataset.base_rates().to_string(index=False))

    rows, breakdowns = [], {}
    for model_name in args.models:
        for seed in args.seeds:
            row, breakdown = run_once(dataset, model_name, seed)
            rows.append(row)
            breakdowns.setdefault(model_name, breakdown)  # first seed, illustrative

    results = pd.DataFrame(rows)
    numeric = ["accuracy", "demographic_parity_diff", "equalized_odds_diff", "disparate_impact"]
    summary = results.groupby("method")[numeric].agg(["mean", "std"]).round(4)

    for model_name, breakdown in breakdowns.items():
        print(f"\n=== per-group rates: {model_name} (seed {args.seeds[0]}) ===")
        print(breakdown.round(4).to_string())

    print(f"\n=== baseline results over {len(args.seeds)} seeds (mean / std) ===")
    print(summary.to_string())
    print("\nFair at 0: demographic_parity_diff, equalized_odds_diff.  Fair at 1: disparate_impact.")
    OUT = output_dir(dataset.name)
    for path in save(OUT, "baseline", {"runs": results, "summary": summary},
                     params=dict(seeds=args.seeds, models=args.models, protected=args.include_protected), force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
