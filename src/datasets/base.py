"""Dataset-agnostic interface for fairness experiments.

Every experiment in this project consumes a :class:`FairnessDataset` and never
refers to a dataset-specific column name. Adding a new dataset means writing one
loader that returns this structure; no experiment code changes.

Only Adult is implemented (see :mod:`src.datasets.adult`). The abstraction exists
because the planned follow-up work re-runs the identical experiment across many
distributions (ACS/folktables state slices), where hardcoded Adult column names
would require rewriting every script.

Conventions enforced here, because fairness metrics are sign-sensitive and silent
convention mismatches are the most common source of wrong numbers in this area:

* ``y == 1`` is always the *favorable* outcome (income > 50K).
* ``a`` holds the protected attribute and is kept **out** of ``X`` by default;
  whether the model may see it is an experimental condition, not a data property.
* ``privileged_value`` / ``unprivileged_value`` name the two groups explicitly
  rather than relying on a 0/1 encoding convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import pandas as pd


@dataclass(frozen=True)
class FairnessDataset:
    """A binary classification task with one binary protected attribute.

    Attributes:
        name: Short identifier used in result tables and filenames.
        X: Feature matrix. Excludes the protected attribute unless the loader was
            asked to include it.
        y: Binary target, where 1 is the favorable outcome.
        a: Protected attribute, aligned with ``X`` and ``y``.
        protected_attribute: Column name of the protected attribute.
        privileged_value: Value of ``a`` for the historically advantaged group.
        unprivileged_value: Value of ``a`` for the historically disadvantaged group.
        categorical_features: Columns of ``X`` needing categorical encoding.
        numeric_features: Columns of ``X`` to be treated as continuous.
        notes: Free-form provenance/preprocessing notes, surfaced in reports.
    """

    name: str
    X: pd.DataFrame
    y: pd.Series
    a: pd.Series
    protected_attribute: str
    privileged_value: Any
    unprivileged_value: Any
    categorical_features: list[str]
    numeric_features: list[str]
    notes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        n = len(self.X)
        if not (len(self.y) == len(self.a) == n):
            raise ValueError(
                f"X, y and a must align: got {n}, {len(self.y)}, {len(self.a)}"
            )
        if not (self.X.index.equals(self.y.index) and self.X.index.equals(self.a.index)):
            raise ValueError("X, y and a must share an identical index")

        y_values = set(pd.unique(self.y.dropna()))
        if not y_values <= {0, 1}:
            raise ValueError(f"y must be binary 0/1 (1 = favorable); found {y_values}")

        a_values = set(pd.unique(self.a.dropna()))
        expected = {self.privileged_value, self.unprivileged_value}
        if a_values != expected:
            raise ValueError(f"a must take values {expected}; found {a_values}")

        declared = set(self.categorical_features) | set(self.numeric_features)
        actual = set(self.X.columns)
        if declared != actual:
            raise ValueError(
                "categorical + numeric features must exactly cover X.columns; "
                f"missing={actual - declared}, unexpected={declared - actual}"
            )

    @property
    def n_samples(self) -> int:
        return len(self.X)

    def base_rates(self) -> pd.DataFrame:
        """Per-group size and P(y=1), the disparity that motivates the project.

        The gap between these two base rates is the source of the bias: ERM has no
        reference to ``a``, but reproduces this gap through correlated features.
        Worth reporting in the writeup before any mitigation numbers.
        """
        rows = []
        for label, value in (
            ("privileged", self.privileged_value),
            ("unprivileged", self.unprivileged_value),
        ):
            mask = self.a == value
            rows.append(
                {
                    "group": label,
                    "value": value,
                    "n": int(mask.sum()),
                    "share": float(mask.mean()),
                    "P(y=1)": float(self.y[mask].mean()),
                }
            )
        return pd.DataFrame(rows)


@runtime_checkable
class DatasetLoader(Protocol):
    """What a dataset must provide to be usable by any experiment here.

    Implementations own their download, cleaning and encoding decisions, and record
    them in ``FairnessDataset.notes`` so the writeup can cite them.
    """

    name: str

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        """Return the prepared dataset.

        Args:
            include_protected_in_features: If True, the protected attribute is also
                a model input. Kept as a parameter rather than a fixed choice because
                "fairness through unawareness" (dropping ``a``) is a condition worth
                measuring, not an assumption -- the Adult proxies (relationship,
                marital-status) mean dropping ``a`` reduces the disparity far less
                than intuition suggests.
        """
        ...
