"""Taiwan credit-card default, 2005 — the first population outside the West.

**Individual work, beyond the course submission.**

Five domains had been measured and every one is Western: two US surveys, US mortgage records,
a Florida county's pretrial data, US law schools, and the Dutch census. "This is a property of
Western administrative data" was an objection with no answer.

This is the UCI credit-card default study: **30,000 credit customers of a Taiwanese bank in
2005**, a different continent, a different legal system, and a lending decision that is not a
mortgage.

Three decisions worth stating, because two of them invert results silently if made the other
way.

**The label is inverted.** The recorded target is ``default payment``, where 1 means the
customer defaulted --- the outcome nobody wants. This project's convention is that ``y == 1``
is favourable, so the target is ``1 - default``: "predicted not to default", which is what a
customer wants and what gets them credit. Left as recorded, every direction this project
reports would come out backwards while still looking valid.

**Female is the advantaged group here**, at a favourable rate of 0.792 against 0.758 for men.
That is a fact about this cohort's repayment, not a claim about society, and it is the same
trap COMPAS set: declaring male privileged because intuition says so would sign-invert every
who-pays number. ``tests/test_new_instruments.py`` asserts the declared privileged group
actually has the higher favourable rate.

**The repayment-history columns are kept and they are strong.** ``PAY_0`` through ``PAY_6``
record how many months late each of the last six payments was, and they predict default far
better than anything else here. They are legitimate --- a lender genuinely has them at decision
time --- but they make the task easy, and an easy task compresses the score distribution, which
is exactly what determines whether an operating-point sweep is possible at all. The viable band
is therefore measured rather than assumed.

Source: Yeh & Lien (2009), UCI ``default of credit card clients``, via the cleaned copy in
github.com/tailequy/fairness_dataset.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "taiwan"
CSV_URL = ("https://raw.githubusercontent.com/tailequy/fairness_dataset/"
           "main/experiments/data/credit-card-clients.csv")

SEX = "SEX"
TARGET = "default payment"

# Codes, not quantities: 1 = graduate school, 2 = university, 3 = high school, and so on.
CATEGORICAL = ["EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]

NUMERIC = ["LIMIT_BAL", "AGE",
           "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
           "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]


class TaiwanCreditLoader:
    """Taiwan 2005 credit default, with the favourable outcome as the target."""

    def __init__(self, *, protected: str = SEX) -> None:
        if protected != SEX:
            raise KeyError(f"cannot protect '{protected}'; this dataset carries only '{SEX}'")
        self.protected = protected

    @property
    def name(self) -> str:
        return "taiwan_2005_sex"

    def _download(self) -> Path:
        path = DATA_DIR / "credit-card-clients.csv"
        if not path.exists():
            import urllib.request

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(CSV_URL, path)   # noqa: S310 - fixed GitHub host
        return path

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        frame = pd.read_csv(self._download()).reset_index(drop=True)

        # 1 is favourable: predicted NOT to default. See the module docstring.
        y = (1 - frame[TARGET]).astype(int).rename("no_default")
        # Named rather than left as 1/2, so the groups cannot be read backwards -- the
        # convention slip base.py exists to prevent.
        a = frame[SEX].map({1: "male", 2: "female"}).astype(str)

        categorical = list(CATEGORICAL)
        if include_protected_in_features:
            categorical.append(SEX)

        X = frame[[*categorical, *NUMERIC]].copy()
        for column in categorical:
            X[column] = X[column].astype(str)

        return FairnessDataset(
            name=self.name,
            X=X, y=y, a=a,
            protected_attribute=SEX,
            # Women in this cohort default less, so they receive the favourable prediction
            # more often. `privileged` follows the base rates, not the intuition.
            privileged_value="female",
            unprivileged_value="male",
            categorical_features=categorical,
            numeric_features=list(NUMERIC),
            secondary_attribute=None,
            proxy_features=["PAY_0", "LIMIT_BAL", "MARRIAGE"],
            notes={
                "source": CSV_URL,
                "label": "1 - default payment, so that 1 is the favourable outcome",
                "why": "first non-Western population, and a consumer-credit decision rather "
                       "than a mortgage",
                "orientation": "female is the advantaged group here (0.792 against 0.758)",
                "easy_task": "PAY_0..PAY_6 are repayment history and predict default "
                             "strongly; the viable band is measured, not assumed",
            },
        )
