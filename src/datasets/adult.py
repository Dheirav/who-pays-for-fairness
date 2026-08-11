"""UCI Adult Census Income loader.

Source: https://archive.ics.uci.edu/dataset/2/adult
Fetched via OpenML (dataset "adult", version 2), then cached locally so runs are
reproducible and offline-repeatable.

Task: predict whether income exceeds $50K/yr. Protected attribute: ``sex``.

Caveat worth stating in the writeup: Adult is 1994 US census data with an
inflation-unadjusted $50K threshold, and Ding et al. (2021, "Retiring Adult")
argue it is a weak fairness benchmark for exactly that reason. It is used here
because it is the benchmark the base paper and the surrounding literature use,
which is what makes the results comparable.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import FairnessDataset

CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "adult.csv"

TARGET = "class"
PROTECTED = "sex"
PRIVILEGED = "Male"
UNPRIVILEGED = "Female"

# Dropped columns, with the reason each is dropped -- these are judgment calls a
# reader may reasonably question, so they are recorded rather than buried.
DROP_COLUMNS = {
    "fnlwgt": "census sampling weight, describes the survey design not the person",
    "education": "redundant with education-num, its own ordinal encoding",
}


class AdultLoader:
    """Loads and cleans Adult into the project's dataset interface."""

    name = "adult"

    def __init__(self, cache_path: Path | None = None) -> None:
        self.cache_path = Path(cache_path) if cache_path else CACHE_PATH

    def _fetch_raw(self) -> pd.DataFrame:
        if self.cache_path.exists():
            return pd.read_csv(self.cache_path)

        from sklearn.datasets import fetch_openml

        bunch = fetch_openml(name="adult", version=2, as_frame=True)
        raw = bunch.frame
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        raw.to_csv(self.cache_path, index=False)
        return raw

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        raw = self._fetch_raw()
        n_raw = len(raw)

        # OpenML encodes missing values as NaN; the raw UCI files use "?".
        df = raw.replace("?", pd.NA)

        # Listwise deletion. Missingness is concentrated in workclass / occupation /
        # native-country and is not obviously random, so this is itself a modelling
        # choice; it matches the standard Adult pipeline and keeps comparability with
        # published numbers.
        df = df.dropna().reset_index(drop=True)
        n_dropped = n_raw - len(df)

        y = (df[TARGET].astype(str).str.strip().str.rstrip(".") == ">50K").astype(int)
        y.name = "income_gt_50k"

        a = df[PROTECTED].astype(str).str.strip()
        a.name = PROTECTED
        unexpected = set(a.unique()) - {PRIVILEGED, UNPRIVILEGED}
        if unexpected:
            raise ValueError(f"unexpected values in '{PROTECTED}': {unexpected}")

        X = df.drop(columns=[TARGET, *DROP_COLUMNS])
        if not include_protected_in_features:
            X = X.drop(columns=[PROTECTED])

        for col in X.select_dtypes(include=["object", "category"]).columns:
            X[col] = X[col].astype(str).str.strip()

        categorical = sorted(X.select_dtypes(include=["object", "category"]).columns)
        numeric = sorted(c for c in X.columns if c not in categorical)

        return FairnessDataset(
            name=self.name,
            X=X,
            y=y,
            a=a,
            protected_attribute=PROTECTED,
            privileged_value=PRIVILEGED,
            unprivileged_value=UNPRIVILEGED,
            categorical_features=categorical,
            numeric_features=numeric,
            notes={
                "source": "OpenML adult v2 (UCI Adult Census Income)",
                "rows_raw": n_raw,
                "rows_after_dropna": len(df),
                "rows_dropped_missing": n_dropped,
                "dropped_columns": DROP_COLUMNS,
                "protected_in_features": include_protected_in_features,
                "favorable_outcome": "income > 50K (y=1)",
            },
        )
