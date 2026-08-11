"""Proxy removal: does deleting a leaky feature remove the leak, or move it?

Document 06 found that the demographic-parity constraint makes the model rely *more*
on ``relationship`` -- the feature whose Husband/Wife levels determine sex outright.
The obvious response is to delete it. This experiment tests whether that works.

It is the causal follow-up to an observational finding. Document 06 could only say
"attribution moved onto the best proxy"; removing the proxy and re-measuring says
whether the model can be prevented from reconstructing sex at all, or whether it
simply reaches for the next-best feature.

Each round removes one more feature and re-measures three things:

1. **Leakage** -- how well a probe can recover ``sex`` from the *remaining* features.
   This is the direct measurement. If AUC stays high after removing a proxy, the
   information was never in that column alone.
2. **Cost** -- what the removal does to accuracy and to the unmitigated fairness gap.
   Deleting predictive features is not free, and the price has to be on the table.
3. **Relocation** -- which feature the attribution moves to, from exact linear SHAP.

Rounds remove features in the order document 06 ranked them, most sex-determining
first, so each round is the strongest available "just delete the proxy" response to
the previous one.

Usage:
    python -m src.experiments.run_proxy_removal
    python -m src.experiments.run_proxy_removal --seeds 0 1 2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..datasets.adult import AdultLoader
from ..explain import aggregate_attributions, linear_explainer_values, proxy_share, source_feature_map
from ..incidence import outcome_total
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build
from ..preprocessing import prepare
from .methods import BASE_MODEL

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"

# Cumulative removal rounds, ordered by how much sex each feature determines.
ROUNDS = [
    [],
    ["relationship"],
    ["relationship", "marital-status"],
    ["relationship", "marital-status", "occupation"],
    ["relationship", "marital-status", "occupation", "hours-per-week"],
]


def round_label(removed: list[str]) -> str:
    return "none removed" if not removed else f"−{', '.join(removed)}"


def run_round(dataset, removed: list[str], seed: int, eps: float) -> dict:
    view = dataset.without_features(removed) if removed else dataset
    split = prepare(view, random_state=seed)
    group_kw = {
        "privileged": view.privileged_value,
        "unprivileged": view.unprivileged_value,
    }

    leakage = view.attribute_leakage(random_state=seed)

    baseline = build(BASE_MODEL, random_state=seed).fit(split.X_train, split.y_train)
    y_base = baseline.predict(split.X_test)
    base_scores = evaluate(split.y_test, y_base, split.a_test, label="baseline", **group_kw)

    mitigated = fit_exponentiated_gradient(
        build(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint="demographic_parity", eps=eps,
    )
    y_mit = mitigated.predict(split.X_test, random_state=seed)
    mit_scores = evaluate(split.y_test, y_mit, split.a_test, label="expgrad_dp", **group_kw)
    pie = outcome_total(y_base, y_mit)

    # Exact linear SHAP on the baseline: where does the attribution sit once the
    # previous round's top proxy is gone?
    mapping = source_feature_map(
        split.feature_names, view.categorical_features, view.numeric_features
    )
    values = linear_explainer_values(
        baseline.coef_[0], float(baseline.intercept_[0]), split.X_train, split.X_test
    )
    shares = aggregate_attributions(values, mapping)

    return {
        "seed": seed,
        "n_removed": len(removed),
        "removed": round_label(removed),
        "n_features": len(view.X.columns),
        "leakage_auc": leakage["leakage_auc"],
        "baseline_accuracy": base_scores["accuracy"],
        "baseline_dp": base_scores["demographic_parity_diff"],
        "expgrad_accuracy": mit_scores["accuracy"],
        "expgrad_dp": mit_scores["demographic_parity_diff"],
        "expgrad_pie_change": pie["pct_change"],
        "top_feature": str(shares.index[0]),
        "top_feature_share": float(shares.iloc[0]),
        "proxy_share": proxy_share(shares),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--eps", type=float, default=0.01)
    args = parser.parse_args()

    dataset = AdultLoader().load()
    print("=== proxy removal: does deleting the leak remove the information? ===")
    print(f"protected attribute: {dataset.protected_attribute}  "
          f"(absent from features throughout)\n")

    rows = []
    for removed in ROUNDS:
        print(f"--- {round_label(removed)} ---", flush=True)
        for seed in args.seeds:
            rows.append(run_round(dataset, removed, seed, args.eps))

    results = pd.DataFrame(rows)
    summary = (
        results.groupby(["n_removed", "removed"], sort=True)[[
            "n_features", "leakage_auc", "baseline_accuracy", "baseline_dp",
            "expgrad_accuracy", "expgrad_dp", "expgrad_pie_change", "proxy_share",
        ]].mean().round(4)
    )
    summary["top_feature"] = (
        results.groupby(["n_removed", "removed"])["top_feature"]
        .agg(lambda s: s.mode().iat[0])
    )

    print(f"\n=== over {len(args.seeds)} seeds ===")
    print(summary.to_string())

    base_auc = summary["leakage_auc"].iloc[0]
    print(f"\nleakage_auc        : how well a probe recovers sex from the remaining")
    print(f"                     features. Starts at {base_auc:.3f}; chance is 0.500.")
    print("expgrad_pie_change : change in the total number of favourable decisions.")
    print("top_feature        : the feature carrying the most attribution that round.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_DIR / "proxy_removal_runs.csv", index=False)
    summary.to_csv(RESULTS_DIR / "proxy_removal_summary.csv")
    print(f"\nwrote {RESULTS_DIR / 'proxy_removal_runs.csv'} and proxy_removal_summary.csv")


if __name__ == "__main__":
    main()
