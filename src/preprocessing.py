"""Splitting and feature encoding.

Design decision -- the encoder is fitted separately and applied to produce dense
arrays, rather than being bundled into an ``sklearn.Pipeline`` with the estimator.
The reason is the mitigation stage: ``fairlearn.reductions.ExponentiatedGradient``
refits its base estimator with ``sample_weight``, and a ``Pipeline`` does not route
that keyword to the final step without extra plumbing. Handing the reduction a bare
estimator over pre-encoded arrays keeps the base paper's reweight-and-retrain loop
working unmodified.

The encoder is fitted on the training split only, so no test information reaches it.

Note that encoding is *not* a bias intervention. Nothing here alters rows, labels or
class balance -- it is the representation change any tabular model requires, and the
project's "the data is never modified" claim is about the mitigation stage.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .datasets.base import FairnessDataset


@dataclass(frozen=True)
class SplitData:
    """A fitted train/test split with encoded features and aligned attributes."""

    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    a_train: np.ndarray
    a_test: np.ndarray
    feature_names: list[str]
    encoder: ColumnTransformer

    @property
    def n_features(self) -> int:
        return self.X_train.shape[1]


def build_encoder(dataset: FairnessDataset) -> ColumnTransformer:
    """One-hot for categoricals, standardised numerics.

    Scaling is unnecessary for trees but required for the regularised linear models
    used later in the ablation; applying it uniformly keeps a single representation
    across every method, so differences in results come from the mitigation and not
    from the features.
    """
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False, drop=None),
                dataset.categorical_features,
            ),
            ("numeric", StandardScaler(), dataset.numeric_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def prepare(
    dataset: FairnessDataset,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
    stratify_on_group_and_label: bool = True,
) -> SplitData:
    """Split, then fit the encoder on train and apply it to both halves.

    Args:
        stratify_on_group_and_label: Stratify on the ``(a, y)`` interaction rather
            than on ``y`` alone. Without this, the four cells that fairness metrics
            are computed from -- especially (unprivileged, y=1), the smallest -- vary
            in size across seeds, which shows up as fairness-metric noise that looks
            like model instability but is really sampling noise.
    """
    strata = (
        dataset.a.astype(str) + "|" + dataset.y.astype(str)
        if stratify_on_group_and_label
        else dataset.y
    )

    idx_train, idx_test = train_test_split(
        dataset.X.index,
        test_size=test_size,
        random_state=random_state,
        stratify=strata,
    )

    encoder = build_encoder(dataset)
    X_train = encoder.fit_transform(dataset.X.loc[idx_train])
    X_test = encoder.transform(dataset.X.loc[idx_test])

    return SplitData(
        X_train=np.asarray(X_train, dtype=float),
        X_test=np.asarray(X_test, dtype=float),
        y_train=dataset.y.loc[idx_train].to_numpy(dtype=int),
        y_test=dataset.y.loc[idx_test].to_numpy(dtype=int),
        a_train=dataset.a.loc[idx_train].to_numpy(),
        a_test=dataset.a.loc[idx_test].to_numpy(),
        feature_names=list(encoder.get_feature_names_out()),
        encoder=encoder,
    )
