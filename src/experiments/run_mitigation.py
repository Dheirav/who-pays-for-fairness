"""Base-paper track: baseline vs Exponentiated Gradient under DP and EO constraints.

Produces the main results table (deliverables 1-3 of the initiation document).

Within a seed, every method is fitted on the *same* train/test split, so differences
between rows come from the mitigation and not from resampling. Across seeds the split
changes, which is what the reported standard deviations measure.

Usage:
    python -m src.experiments.run_mitigation
    python -m src.experiments.run_mitigation --seeds 0 1 2 --models decision_tree
    python -m src.experiments.run_mitigation --eps 0.05
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from ..datasets.adult import AdultLoader
from ..metrics import evaluate, group_breakdown
from ..mitigation import fit_exponentiated_gradient
from ..models import MODELS, build
from ..preprocessing import prepare

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def run_seed(dataset, model_name: str, seed: int, eps: float, max_iter: int):
    """Fit baseline and both constrained models on one split."""
    split = prepare(dataset, random_state=seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }

    rows, breakdowns = [], {}

    def record(label: str, y_pred, elapsed: float) -> None:
        row = evaluate(split.y_test, y_pred, split.a_test, label=label, **group_kw)
        row.update({"model": model_name, "seed": seed, "fit_seconds": round(elapsed, 1)})
        rows.append(row)
        breakdowns[label] = group_breakdown(split.y_test, y_pred, split.a_test, **group_kw)

    t0 = time.perf_counter()
    baseline = build(model_name, random_state=seed)
    baseline.fit(split.X_train, split.y_train)
    record("baseline", baseline.predict(split.X_test), time.perf_counter() - t0)

    for constraint, label in (
        ("demographic_parity", "expgrad_dp"),
        ("equalized_odds", "expgrad_eo"),
    ):
        t0 = time.perf_counter()
        mitigated = fit_exponentiated_gradient(
            build(model_name, random_state=seed),
            split.X_train,
            split.y_train,
            split.a_train,
            constraint=constraint,
            eps=eps,
            max_iter=max_iter,
        )
        # random_state fixed for reproducibility -- predict() samples from the learned
        # distribution over classifiers, so it is stochastic by construction.
        y_pred = mitigated.predict(split.X_test, random_state=seed)
        record(label, y_pred, time.perf_counter() - t0)

    return rows, breakdowns


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--models", nargs="+", default=["decision_tree"], choices=sorted(MODELS))
    parser.add_argument("--eps", type=float, default=0.01, help="fairness slack epsilon")
    parser.add_argument("--max-iter", type=int, default=50)
    args = parser.parse_args()

    dataset = AdultLoader().load()
    print(f"=== {dataset.name}: {dataset.n_samples:,} rows, eps={args.eps} ===")
    print(dataset.base_rates().to_string(index=False))

    all_rows, first_breakdowns = [], {}
    for model_name in args.models:
        for seed in args.seeds:
            print(f"\nfitting {model_name}, seed {seed} ...", flush=True)
            rows, breakdowns = run_seed(dataset, model_name, seed, args.eps, args.max_iter)
            all_rows.extend(rows)
            first_breakdowns.setdefault(model_name, breakdowns)

    results = pd.DataFrame(all_rows)
    numeric = ["accuracy", "demographic_parity_diff", "equalized_odds_diff", "disparate_impact"]
    order = ["baseline", "expgrad_dp", "expgrad_eo"]

    summary = (
        results.groupby(["model", "method"])[numeric]
        .agg(["mean", "std"])
        .round(4)
        .reindex(order, level="method")
    )

    for model_name, breakdowns in first_breakdowns.items():
        print(f"\n=== per-group rates: {model_name}, seed {args.seeds[0]} ===")
        for label in order:
            print(f"\n[{label}]")
            print(breakdowns[label].round(4).to_string())

    print(f"\n=== results over {len(args.seeds)} seeds (mean / std) ===")
    print(summary.to_string())
    print("\nFair at 0: demographic_parity_diff, equalized_odds_diff.  Fair at 1: disparate_impact.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_DIR / "mitigation_runs.csv", index=False)
    summary.to_csv(RESULTS_DIR / "mitigation_summary.csv")
    print(f"\nwrote {RESULTS_DIR / 'mitigation_runs.csv'} and mitigation_summary.csv")


if __name__ == "__main__":
    main()
