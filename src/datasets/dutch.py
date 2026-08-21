"""Dutch census 2001 occupational status — the first population outside the United States.

**Individual work, beyond the course submission.**

Four domains had been measured before this and all four are American: two US surveys, US
mortgage records, a Florida county's pretrial data, and US law schools. Three of the five are
also 2016–2018. So "this is a property of American administrative data in the late 2010s"
was an objection with no answer.

This is the Dutch national census of 2001: **60,420 people, a different country, a different
decade, and a different decision** — whether someone holds a high-status occupation.

Why it is worth having beyond the passport
------------------------------------------
* **It is large.** A 30% test split is over 18,000 people, seven times document 15's floor, so
  nothing here is limited by the arbitrariness that constrains COMPAS.
* **The disparity is enormous.** Men hold a high-status occupation at **0.626**, women at
  **0.327** — a base-rate gap of 0.30, roughly twice Adult's. If the direction of levelling
  down were driven by the size of the group gap rather than by the selection rate, this is
  where that should show.
* **It sits mid-range**, at a base rate of 0.476 — between the ACS income tasks and mortgage
  lending, in the region where crossovers have actually been observed.

Encoding decisions
------------------
The columns are census codes, not measurements, and treating a code as a number is the kind of
mistake that produces plausible wrong answers. ``household_position`` runs 1110–1220 and
``cur_eco_activity`` 111–141: those are nominal classifications whose numeric order means
nothing, so they are categorical.

Only ``age`` (twelve ordered bands) and ``edu_level`` (six ordered levels) are genuinely
ordinal and are kept numeric. ``household_size`` looks numeric and is not — its values are
111, 112, 113, 114, 125, 126, which are codes rather than counts — so it is categorical.

Source: the cleaned Dutch census distributed with github.com/tailequy/fairness_dataset,
derived from the 2001 IPUMS release.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "dutch"
CSV_URL = ("https://raw.githubusercontent.com/tailequy/fairness_dataset/"
           "main/experiments/data/dutch.csv")

SEX = "sex"

# Ordered bands, so their numeric order carries meaning.
NUMERIC = ["age", "edu_level"]

# Census classifications. Their codes are labels, not quantities -- household_size is 111,
# 112, 113, 114, 125, 126 rather than 1..6, which is why it is here and not above.
CATEGORICAL = ["household_position", "household_size", "prev_residence_place",
               "citizenship", "country_birth", "economic_status", "cur_eco_activity",
               "marital_status"]


class DutchLoader:
    """Dutch census 2001: does this person hold a high-status occupation?"""

    def __init__(self, *, protected: str = SEX) -> None:
        if protected != SEX:
            raise KeyError(f"cannot protect '{protected}'; this census carries only '{SEX}'")
        self.protected = protected

    @property
    def name(self) -> str:
        return "dutch_2001_sex"

    def _download(self) -> Path:
        path = DATA_DIR / "dutch.csv"
        if not path.exists():
            import urllib.request

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(CSV_URL, path)   # noqa: S310 - fixed GitHub host
        return path

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        frame = pd.read_csv(self._download()).reset_index(drop=True)

        # 1 is the favourable outcome, as everywhere in this project: a high-status
        # occupation. The source already encodes it that way, so no inversion is needed --
        # unlike COMPAS, where the recorded label is the outcome nobody wants.
        y = frame["occupation"].astype(int).rename("high_status_occupation")
        a = frame[SEX].astype(str)

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
            privileged_value="male",
            unprivileged_value="female",
            categorical_features=categorical,
            numeric_features=list(NUMERIC),
            secondary_attribute=None,
            # Household position encodes who is a spouse or head of household, which in a
            # 2001 census is close to a sex indicator; education and economic status follow.
            proxy_features=["household_position", "economic_status", "edu_level"],
            notes={
                "source": CSV_URL,
                "label": "occupation; 1 is a high-status occupation and is favourable",
                "why": "first non-US population, and the first outside 2016-2018",
                "gap": "male 0.626 against female 0.327 -- roughly twice Adult's base-rate "
                       "gap, which is where a group-gap explanation should show if it holds",
                "encoding": "household_position, household_size and cur_eco_activity are "
                            "census codes rather than quantities and are treated as "
                            "categorical; only age and edu_level are ordered",
            },
        )
