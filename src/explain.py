"""SHAP attribution: what does each model actually lean on, before and after mitigation?

The protected attribute is dropped from the feature matrix, so no model can use ``sex``
directly. That is fairness through unawareness, and it does not work -- the models
recover the same information from proxies (``relationship`` encodes Husband/Wife,
``marital-status`` encodes the same fact again, ``hours-per-week`` and ``occupation``
correlate with it). The interesting question the ablation table cannot answer is
whether a mitigation actually *stops leaning on the proxies*, or whether it keeps the
same reliance and merely corrects the output afterwards.

Two design decisions worth defending in the writeup:

**Attributions are aggregated back to source features.** One-hot encoding turns
``occupation`` into fourteen columns; reporting those separately makes a feature look
unimportant by spreading its mass thinly. Shapley values are additive, so summing the
columns of one source feature is exact, not an approximation.

**Attributions are reported as a share of the model's total attribution mass**, not in
raw units. The six methods emit scores on different scales -- a logit from a linear
model, a mixture probability from a randomized ensemble -- and raw mean-|SHAP| is not
comparable across them. The share answers the question that matters here: *of
everything this model bases decisions on, how much rides on the proxies?*

Exact linear SHAP is used wherever the model is linear (five of the seven explainers,
including one per protected group for Prejudice Remover). The two ExponentiatedGradient
rows are randomized ensembles of thresholded classifiers -- not linear in any
parameterisation -- so they are explained with ``KernelExplainer``, which samples. That
approximation is flagged in the output rather than hidden.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Features that carry information about sex without being sex. `relationship` is the
# blatant one on Adult -- its levels are literally Husband and Wife -- but the others
# are correlated enough to serve the same purpose for a model that wants it.
SEX_PROXIES = ["relationship", "marital-status", "hours-per-week", "occupation"]

# KernelExplainer cost is (n_background x nsamples) model evaluations per explained
# row. These are set so the two ensemble rows finish in minutes rather than hours; the
# resulting attributions are estimates with sampling error, unlike the linear rows.
KERNEL_BACKGROUND = 25
KERNEL_INSTANCES = 150
KERNEL_NSAMPLES = 400


def source_feature_map(
    feature_names: list[str], categorical: list[str], numeric: list[str]
) -> dict[str, list[int]]:
    """Map each original column to the encoded column indices it produced.

    Built from the dataset's own declared feature lists rather than by string-splitting
    the encoder's output, so a category value containing an underscore cannot silently
    land under the wrong source feature.
    """
    mapping: dict[str, list[int]] = {name: [] for name in [*categorical, *numeric]}
    for index, encoded in enumerate(feature_names):
        if encoded in mapping:                       # numeric passes through unchanged
            mapping[encoded].append(index)
            continue
        owners = [c for c in categorical if encoded.startswith(f"{c}_")]
        if not owners:
            raise KeyError(f"encoded column '{encoded}' matches no source feature")
        mapping[max(owners, key=len)].append(index)  # longest prefix wins
    return mapping


def aggregate_attributions(
    shap_values: np.ndarray, mapping: dict[str, list[int]]
) -> pd.Series:
    """Mean |SHAP| per source feature, normalised to shares summing to 1.

    Summing over an encoded feature's columns is valid because Shapley values are
    additive; the absolute value is taken *after* summing so that a feature whose
    levels push in opposite directions is credited for the influence it exerts, not
    netted out to zero.
    """
    totals = {
        feature: float(np.mean(np.abs(shap_values[:, columns].sum(axis=1))))
        for feature, columns in mapping.items()
        if columns
    }
    series = pd.Series(totals).sort_values(ascending=False)
    return series / series.sum()


def linear_explainer_values(
    coef: np.ndarray, intercept: float, background: np.ndarray, X: np.ndarray
) -> np.ndarray:
    """Exact SHAP values for a linear score. No sampling, no approximation.

    For a linear score the Shapley value is ``w_i * (x_i - E[x_i])``, so the background
    enters only through ``E[x]``. shap's default masker silently subsamples the
    background to 100 rows, which makes that expectation noisy and the word "exact"
    untrue; the masker is therefore constructed explicitly over the full training set.
    """
    import shap

    masker = shap.maskers.Independent(background, max_samples=len(background))
    explainer = shap.LinearExplainer((np.asarray(coef, dtype=float), float(intercept)), masker)
    return np.asarray(explainer.shap_values(X))


def kernel_explainer_values(
    score_fn, background: np.ndarray, X: np.ndarray, *, nsamples: int = KERNEL_NSAMPLES
) -> np.ndarray:
    """Sampled SHAP values for a model with no linear parameterisation."""
    import shap

    explainer = shap.KernelExplainer(score_fn, background)
    return np.asarray(explainer.shap_values(X, nsamples=nsamples, silent=True))


def proxy_share(shares: pd.Series, proxies: list[str] = SEX_PROXIES) -> float:
    """Combined attribution share of the sex proxies -- the headline number."""
    return float(shares.reindex(proxies).fillna(0.0).sum())
