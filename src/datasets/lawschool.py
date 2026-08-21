"""LSAC law school bar passage, as a fourth instrument and a high-selection-rate task.

**Individual work, beyond the course submission.**

This dataset is here for a reason beyond adding a domain. Almost every population measured in
this project sits at a low selection rate: the ACS income arms run from 0.03 to 0.89 but the
*natural* ones cluster under 0.36, and only mortgage lending occupies the top of the range.
That matters because the selection-rate rule predicts **opposite directions** at the two ends,
so an unbalanced sample of tasks tests one half of the claim far harder than the other.

Bar passage is naturally generous: about **89%** of candidates pass. It therefore lands where
the rule predicts levelling *up*, in a domain unrelated to lending, and gives the top of the
range a second instrument.

Two decisions worth stating.

**What the decision is.** The favourable outcome is ``pass_bar``. The task is read as
predicting who will pass -- the kind of prediction used for admissions and for allocating
academic support -- and not as the admission decision itself. That framing matters for the
next point.

**``zfygpa`` and ``zgpa`` are kept, and they are post-admission.** They are first-year and
cumulative law-school grades, so they exist only *after* someone is admitted. Under the
reading above they are legitimate predictors of bar passage. They would be leakage under an
admissions reading, which is why the reading is stated rather than assumed. This is the same
hazard as HMDA's ``denial_reason``, handled the same way: name the feature, name the reading
that makes it valid, and let a reader disagree with the reading rather than discover the
feature.

Source: the cleaned LSAC National Longitudinal Bar Passage Study distributed with
github.com/tailequy/fairness_dataset.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "lawschool"
CSV_URL = ("https://raw.githubusercontent.com/tailequy/fairness_dataset/"
           "main/experiments/data/law_school_clean.csv")

RACE, SEX = "race", "male"

PROTECTED_SCHEMES = {
    RACE: {"privileged": "White", "unprivileged": "Non-White"},
    SEX: {"privileged": "male", "unprivileged": "female"},
}

CATEGORICAL = ["fulltime", "tier"]
NUMERIC = ["decile1b", "decile3", "lsat", "ugpa", "zfygpa", "zgpa", "fam_inc"]


class LawSchoolLoader:
    """LSAC bar passage, a naturally high-selection-rate decision task."""

    def __init__(self, *, protected: str = RACE) -> None:
        if protected not in PROTECTED_SCHEMES:
            raise KeyError(
                f"cannot protect '{protected}'; available: {sorted(PROTECTED_SCHEMES)}")
        self.protected = protected

    @property
    def name(self) -> str:
        return f"lawschool_{'race' if self.protected == RACE else 'sex'}"

    def _download(self) -> Path:
        path = DATA_DIR / "law_school_clean.csv"
        if not path.exists():
            import urllib.request

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(CSV_URL, path)   # noqa: S310 - fixed GitHub host
        return path

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        scheme = PROTECTED_SCHEMES[self.protected]
        frame = pd.read_csv(self._download()).reset_index(drop=True)

        y = frame["pass_bar"].astype(int).rename("pass_bar")
        if self.protected == RACE:
            a = frame[RACE].astype(str)
        else:
            # Recorded as a 0/1 column; named explicitly so the groups cannot be read
            # backwards, which is the convention slip base.py exists to prevent.
            a = frame[SEX].map({1.0: "male", 0.0: "female"}).astype(str)

        categorical = list(CATEGORICAL)
        numeric = list(NUMERIC)
        if self.protected == RACE:
            categorical.append(SEX)          # sex is a usable feature when race is protected
        if include_protected_in_features:
            categorical.append(self.protected)

        X = frame[[*categorical, *numeric]].copy()
        for column in categorical:
            X[column] = X[column].astype(str)

        return FairnessDataset(
            name=self.name,
            X=X, y=y, a=a,
            protected_attribute=self.protected,
            privileged_value=scheme["privileged"],
            unprivileged_value=scheme["unprivileged"],
            categorical_features=categorical,
            numeric_features=numeric,
            secondary_attribute=SEX if self.protected == RACE else None,
            # Admissions-test and grade measures carry most of the group signal here.
            proxy_features=["lsat", "ugpa", "zfygpa"],
            notes={
                "source": CSV_URL,
                "label": "pass_bar; 1 is favourable",
                "reading": "predicting who passes the bar, not the admission decision -- "
                           "which is what makes the post-admission grade features valid",
                "post_admission_features": "zfygpa, zgpa",
                "why": "a naturally high selection rate (~0.89), where the rule predicts "
                       "levelling UP, in a domain unrelated to lending",
            },
        )
