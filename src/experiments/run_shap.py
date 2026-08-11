"""SHAP before/after: does mitigation stop the model leaning on sex proxies?

Section 6 of the initiation document lists SHAP as a stretch goal. It earns its place
because it answers something none of the fairness metrics can: *why* the mitigated
model behaves differently. There are two possibilities and they are not equivalent.

* The mitigation **reduced reliance on the proxies** -- the model stopped reading
  ``relationship`` and ``marital-status`` as stand-ins for sex, and now decides on
  features that plausibly bear on income.
* The mitigation **kept the same reliance and corrected the output afterwards** -- it
  still reasons the same way, and the constraint just shifts a threshold. The metric
  improves; the mechanism is untouched. A model like this would break the moment it
  met a population with different proxy correlations.

``sex`` is not in the feature matrix, so every model here is "unaware". Whatever
reliance shows up is proxy reliance by construction.

See :mod:`src.explain` for how attributions are aggregated and normalised, and why
five of the six methods get exact linear SHAP while the two randomized ensembles are
sampled.

Usage:
    python -m src.experiments.run_shap
    python -m src.experiments.run_shap --seed 0 --instances 300
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..datasets.adult import AdultLoader
from ..explain import (
    KERNEL_BACKGROUND,
    KERNEL_INSTANCES,
    SEX_PROXIES,
    aggregate_attributions,
    kernel_explainer_values,
    linear_explainer_values,
    proxy_share,
    source_feature_map,
)
from ..preprocessing import prepare
from .methods import METHOD_ORDER, MethodParams, fit_all

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"

# Rows explained with exact linear SHAP, and how to pull the linear score out of each.
# Everything else falls back to sampling.
LINEAR_METHODS = {"baseline", "gridsearch_dp", "prejudice_remover", "adversarial_debiasing"}


def linear_parts(name: str, model, split) -> list[tuple[str, np.ndarray, float, np.ndarray]]:
    """Return ``(label, coef, intercept, rows_it_applies_to)`` for a linear method.

    Prejudice Remover returns *two* entries. Its parameterisation is one weight vector
    per protected group, so there is no single linear model to explain -- and the fact
    that the two differ is itself the finding, since it means the method reasons
    differently about applicants depending on their sex.
    """
    X = split.X_test

    if name == "baseline":
        return [(name, model.coef_[0], float(model.intercept_[0]), X)]

    if name == "gridsearch_dp":
        chosen = model.predictors_[model.best_idx_]
        return [(name, chosen.coef_[0], float(chosen.intercept_[0]), X)]

    if name == "adversarial_debiasing":
        weight = model.predictor_.weight.detach().numpy()[0]
        bias = float(model.predictor_.bias.detach().numpy()[0])
        return [(name, weight, bias, X)]

    if name == "prejudice_remover":
        entries = []
        for index, group in enumerate(model.groups_):
            mask = split.a_test == group
            entries.append(
                (f"{name} [{group}]", model.W_[index], float(model.b_[index]), X[mask])
            )
        return entries

    raise KeyError(name)


def score_fn_for(name: str, model):
    """A deterministic real-valued score for a method with no linear form.

    ``ExponentiatedGradient`` returns a distribution over classifiers; ``_pmf_predict``
    gives the probability it assigns to the positive class, which is the deterministic
    function underlying its stochastic ``predict``. Explaining that is the honest
    target -- explaining a single sampled draw would attribute the coin flip.
    """
    if name in ("expgrad_dp", "expgrad_eo"):
        return lambda X: np.asarray(model._pmf_predict(X))[:, 1]
    raise KeyError(name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--instances", type=int, default=KERNEL_INSTANCES,
                        help="test rows explained by the sampled explainer")
    parser.add_argument("--eps", type=float, default=0.01)
    parser.add_argument("--eta", type=float, default=5.0)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    import shap

    params = MethodParams(eps=args.eps, eta=args.eta, alpha=args.alpha, epochs=args.epochs)
    dataset = AdultLoader().load()
    split = prepare(dataset, random_state=args.seed)

    mapping = source_feature_map(
        split.feature_names, dataset.categorical_features, dataset.numeric_features
    )
    print(f"=== SHAP attribution, seed {args.seed} ===")
    print(f"{len(split.feature_names)} encoded columns -> {len(mapping)} source features")
    print(f"sex is {'IN' if dataset.protected_attribute in mapping else 'NOT in'} "
          f"the feature matrix; proxies examined: {', '.join(SEX_PROXIES)}\n")

    _, _, models = fit_all(split, args.seed, params, return_models=True)

    shares: dict[str, pd.Series] = {}
    exactness: dict[str, str] = {}

    for name in METHOD_ORDER:
        model = models[name]
        if name in LINEAR_METHODS:
            for label, coef, intercept, rows in linear_parts(name, model, split):
                values = linear_explainer_values(coef, intercept, split.X_train, rows)
                shares[label] = aggregate_attributions(values, mapping)
                exactness[label] = "exact"
                print(f"  {label:<32} exact linear SHAP on {len(rows)} rows")
        else:
            background = shap.kmeans(split.X_train, KERNEL_BACKGROUND)
            rows = split.X_test[: args.instances]
            values = kernel_explainer_values(score_fn_for(name, model), background, rows)
            shares[name] = aggregate_attributions(values, mapping)
            exactness[name] = "sampled"
            print(f"  {name:<32} sampled SHAP on {len(rows)} rows "
                  f"({KERNEL_BACKGROUND} background)")

    table = pd.DataFrame(shares).fillna(0.0)
    table = table.loc[table.mean(axis=1).sort_values(ascending=False).index]

    print("\n=== attribution share per source feature (columns sum to 1) ===")
    print(table.round(4).to_string())

    proxies = pd.DataFrame({
        "proxy_share": {label: proxy_share(series) for label, series in shares.items()},
        "shap_quality": exactness,
    })
    baseline_share = proxies.loc["baseline", "proxy_share"]
    proxies["change_vs_baseline"] = proxies["proxy_share"] - baseline_share
    proxies["pct_change"] = 100.0 * proxies["change_vs_baseline"] / baseline_share

    print(f"\n=== combined share of attribution on sex proxies ({', '.join(SEX_PROXIES)}) ===")
    print(proxies.round(4).to_string())
    print("\nA method that genuinely stopped using proxies would show a large negative")
    print("change. A method near zero change corrected its output without changing how")
    print("it reasons -- the metric moved, the mechanism did not.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(RESULTS_DIR / "shap_feature_shares.csv")
    proxies.to_csv(RESULTS_DIR / "shap_proxy_reliance.csv")
    print(f"\nwrote {RESULTS_DIR / 'shap_feature_shares.csv'} and shap_proxy_reliance.csv")


if __name__ == "__main__":
    main()
