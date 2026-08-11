"""Ablation: hold data, base classifier and metrics fixed; vary only the mitigation.

Produces the full results table from section 7 of the initiation document.

Every row uses **logistic regression** as the base classifier, including the
reductions rows -- which is why this experiment exists separately from
``run_mitigation`` (that one uses the decision tree the document specifies for the
base-paper track). Prejudice Remover and Adversarial Debiasing cannot wrap a decision
tree: one adds a term to a likelihood, the other needs gradients to flow from an
adversary into the predictor. Reporting a tree for some rows and a linear model for
others would vary the hypothesis class *and* the mitigation at once, so the table
would not isolate what it claims to.

All six methods are in-processing: none modifies, reweights-on-disk, resamples, or
relabels the training data. Only the objective handed to the learner changes.

Usage:
    python -m src.experiments.run_ablation
    python -m src.experiments.run_ablation --seeds 0 1 2 3 4 --eta 5.0
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from ..datasets.adult import AdultLoader
from ..inprocessing import AdversarialDebiasing, PrejudiceRemover
from ..metrics import evaluate, group_breakdown
from ..mitigation import fit_exponentiated_gradient, fit_grid_search
from ..models import build
from ..preprocessing import prepare

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"
BASE_MODEL = "logistic_regression"

ROW_ORDER = [
    "baseline",
    "expgrad_dp",
    "expgrad_eo",
    "gridsearch_dp",
    "prejudice_remover",
    "adversarial_debiasing",
]


def run_seed(dataset, seed: int, *, eps: float, eta: float, alpha: float, epochs: int):
    split = prepare(dataset, random_state=seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }
    rows, breakdowns = [], {}

    def record(label: str, y_pred, elapsed: float) -> None:
        row = evaluate(split.y_test, y_pred, split.a_test, label=label, **group_kw)
        row.update({"seed": seed, "fit_seconds": round(elapsed, 1)})
        rows.append(row)
        breakdowns[label] = group_breakdown(split.y_test, y_pred, split.a_test, **group_kw)

    def timed(label: str, fn) -> None:
        t0 = time.perf_counter()
        y_pred = fn()
        record(label, y_pred, time.perf_counter() - t0)
        print(f"    {label:<24} {time.perf_counter() - t0:6.1f}s", flush=True)

    def baseline():
        model = build(BASE_MODEL, random_state=seed)
        model.fit(split.X_train, split.y_train)
        return model.predict(split.X_test)

    def expgrad(constraint):
        def run():
            model = fit_exponentiated_gradient(
                build(BASE_MODEL, random_state=seed),
                split.X_train, split.y_train, split.a_train,
                constraint=constraint, eps=eps,
            )
            return model.predict(split.X_test, random_state=seed)
        return run

    def gridsearch():
        model = fit_grid_search(
            build(BASE_MODEL, random_state=seed),
            split.X_train, split.y_train, split.a_train,
            constraint="demographic_parity",
        )
        return model.predict(split.X_test)

    def prejudice_remover():
        model = PrejudiceRemover(eta=eta, random_state=seed).fit(
            split.X_train, split.y_train, split.a_train
        )
        # Requires the protected attribute at inference -- see the module docstring.
        return model.predict(split.X_test, split.a_test)

    def adversarial():
        model = AdversarialDebiasing(
            adversary_weight=alpha, epochs=epochs, random_state=seed
        ).fit(split.X_train, split.y_train, split.a_train)
        return model.predict(split.X_test)

    timed("baseline", baseline)
    timed("expgrad_dp", expgrad("demographic_parity"))
    timed("expgrad_eo", expgrad("equalized_odds"))
    timed("gridsearch_dp", gridsearch)
    timed("prejudice_remover", prejudice_remover)
    timed("adversarial_debiasing", adversarial)

    return rows, breakdowns


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--eps", type=float, default=0.01, help="ExpGrad fairness slack")
    parser.add_argument("--eta", type=float, default=5.0, help="Prejudice Remover penalty")
    parser.add_argument("--alpha", type=float, default=1.0, help="adversary weight")
    parser.add_argument("--epochs", type=int, default=30, help="adversarial training epochs")
    args = parser.parse_args()

    dataset = AdultLoader().load()
    print(f"=== ablation on {dataset.name}: base classifier = {BASE_MODEL} ===")
    print(dataset.base_rates().to_string(index=False))

    all_rows, first = [], {}
    for seed in args.seeds:
        print(f"\n--- seed {seed} ---", flush=True)
        rows, breakdowns = run_seed(
            dataset, seed, eps=args.eps, eta=args.eta, alpha=args.alpha, epochs=args.epochs
        )
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
