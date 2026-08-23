"""ACSEmployment and ACSPublicCoverage — the cross-task arms of the shape test.

**Individual work, beyond the course submission.**

Every income population, whatever its state or year, asks folktables' ACSIncome
question. Documents 54--57 left the curve-shape boundary tested only across states and
vintages of that one task; these two loaders change the *question* while holding the
survey instrument fixed, which is the cheapest independence rung below the IPUMS
cohort (different instrument entirely).

A lost scratch screen was recorded in NEXT.md as saying the sex arms pass; the
re-screen of 24 Aug measured otherwise and NEXT.md is corrected: **every
coverage-by-sex arm fails the 0.05 gap floor** (gaps 0.028--0.047), so by the frozen
exclusions that whole family is a refusal. The usable design is the **race** arms of
both tasks: employment AL/OH/PA (p 0.41--0.47, gaps 0.056--0.079) and coverage
OH/PA/NY (p 0.31--0.40, gaps 0.131--0.151) --- attribute held fixed, task varying,
base rates on **both** sides of the sealed 0.365 boundary, so a constant cannot match
the family calls.

Two deliberate conventions:

* **Tasks are folktables' own** (``ACSEmployment``, ``ACSPublicCoverage``): their
  feature lists, filters and targets, unmodified, so nothing about the label is this
  project's choice. There is no threshold knob; the tasks are natively binary.
* **The advantaged group is declared per task from measurement, because the signed
  parity-gap convention requires the privileged group to be the higher-rate one.**
  On employment that is Male (sex) and White (race). On coverage it *inverts*: Male
  on sex, and **Non-White on race** (0.46 vs 0.31 in OH) --- public coverage is
  means-tested, so the group disadvantaged on income is the higher-rate group here.
  That inversion is a feature of the design: a rule that secretly tracks "the same
  group always loses" rather than the selection rate fails on these arms.

``ST`` is dropped from Coverage's features because single-state loading makes it a
constant column.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .acs import DATA_DIR, SEX_LABELS
from .base import FairnessDataset

PROTECTED = "SEX"

TASKS = {
    "employment": {
        "target_name": "employed",
        "privileged": "Male",
        "unprivileged": "Female",
        "race_privileged": "White",
        "race_unprivileged": "Non-White",
        "numeric": ["AGEP", "SCHL"],
        "drop": [],
    },
    "coverage": {
        "target_name": "public_coverage",
        # Measured 24 Aug: men and Non-White respondents are the higher-rate groups,
        # so the advantaged declaration inverts relative to the income arms.
        "privileged": "Male",
        "unprivileged": "Female",
        "race_privileged": "Non-White",
        "race_unprivileged": "White",
        "numeric": ["AGEP", "SCHL", "PINCP"],
        "drop": ["ST"],
    },
}


class ACSTaskLoader:
    """One state of a folktables task that is not income.

    Args:
        task: ``"employment"`` or ``"coverage"``.
        state: two-letter state code.
        year: ACS survey year; the screen and seal use 2018.
    """

    def __init__(self, task: str, state: str, *, year: str = "2018",
                 protected: str = PROTECTED) -> None:
        if task not in TASKS:
            raise KeyError(f"unknown ACS task '{task}'; have {sorted(TASKS)}")
        if protected not in (PROTECTED, "RAC1P"):
            raise KeyError(f"cannot protect '{protected}' on an ACS task")
        self.task = task
        self.state = state.upper()
        self.year = str(year)
        self.protected = protected

    @property
    def name(self) -> str:
        stem = f"acs_{self.task}_{self.state.lower()}_{self.year}"
        return stem if self.protected == PROTECTED else f"{stem}_rac1p"

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        from folktables import ACSDataSource, ACSEmployment, ACSPublicCoverage

        problem = {"employment": ACSEmployment,
                   "coverage": ACSPublicCoverage}[self.task]
        spec = TASKS[self.task]

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        source = ACSDataSource(survey_year=self.year, horizon="1-Year",
                               survey="person", root_dir=str(DATA_DIR))
        frame = source.get_data(states=[self.state], download=True)
        if "RELP" not in frame.columns and "RELSHIPP" in frame.columns:
            # Same rename and caveat as the income loader: unordered levels either
            # way, not comparable across the 2018/2019 boundary.
            frame = frame.rename(columns={"RELSHIPP": "RELP"})

        X, y, _ = problem.df_to_pandas(frame)
        X = X.reset_index(drop=True)
        y = pd.Series(np.asarray(y).astype(int).ravel(),
                      name=spec["target_name"], index=X.index)

        sex = X[PROTECTED].map(SEX_LABELS).astype(object)
        if sex.isna().any():
            raise ValueError("unexpected SEX code outside {1, 2}")
        if self.protected == PROTECTED:
            a = sex.copy()
            privileged, unprivileged = spec["privileged"], spec["unprivileged"]
        else:
            # The income loader's coarse race split, with its caveats: White vs
            # everyone else. Which side is "privileged" is per-task (see TASKS).
            from .acs import RACE_LABELS, RACE_PRIVILEGED

            race = X["RAC1P"].map(RACE_LABELS).fillna("Unknown")
            a = race.where(race == RACE_PRIVILEGED,
                           other="Non-White").astype(object)
            privileged = spec["race_privileged"]
            unprivileged = spec["race_unprivileged"]
        a.name = self.protected

        features = X.drop(columns=[self.protected, *[c for c in spec["drop"]
                                                     if c in X.columns]])
        if self.protected != PROTECTED and PROTECTED in features.columns:
            features[PROTECTED] = sex
        numeric = [c for c in spec["numeric"] if c in features.columns]
        categorical = [c for c in features.columns if c not in numeric]
        for column in categorical:
            features[column] = features[column].astype(str)

        if include_protected_in_features:
            features[self.protected] = a.to_numpy()
            categorical = [*categorical, self.protected]

        return FairnessDataset(
            name=self.name,
            X=features[[*categorical, *numeric]],
            y=y,
            a=a,
            protected_attribute=self.protected,
            privileged_value=privileged,
            unprivileged_value=unprivileged,
            categorical_features=categorical,
            numeric_features=numeric,
            secondary_attribute=None,
            proxy_features=[],
            notes={
                "source": f"folktables ACS{self.task.capitalize()}",
                "reference": "Ding et al. (2021), Retiring Adult, NeurIPS",
                "state": self.state,
                "year": self.year,
                "advantaged_declaration": privileged,
            },
        )
