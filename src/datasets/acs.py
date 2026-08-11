"""ACS Income (folktables) — the modern replacement for Adult.

Ding, Hardt, Miller & Schmidt (2021), *Retiring Adult: New Datasets for Fair Machine
Learning*, NeurIPS. Adult is a 1994 extract with a fixed $50K threshold and known
idiosyncrasies; ACSIncome reconstructs the same prediction task from current American
Community Survey microdata, and — the reason it matters here — it is available **per
state**, so the same experiment can be run across populations that differ in exactly
the quantities this project's findings are hypothesised to depend on.

That is the point of adding it. Not "a second dataset for robustness", but a set of
populations with measurably different group-size ratios and base-rate gaps, which turns
three observations from Adult into predictions that can fail:

* the people-vs-rates divergence in :mod:`src.incidence` should follow group sizes, so
  a state near 1:1 should show the two shares converge (Adult's ratio is 2.08:1);
* the demographic-parity/equalized-odds conflict should scale with the base-rate gap;
* proxy relocation should weaken where no sex-determining proxy exists.

**The third is a natural control this dataset supplies for free.** Adult's
``relationship`` column has Husband and Wife as separate levels, so it determines sex
outright for 46% of rows. ACS records the same relation as a single ``RELP`` code 1
("husband/wife"), which is 50.2% male — no level of ``RELP`` exceeds 0.64. If the
constraint's documented shift onto ``relationship`` is really a search for the best
reconstruction of sex, it should have much less to work with here.

Feature mapping to Adult, so results are comparable:

===========  ==================================  ============
ACS          meaning                             Adult analogue
===========  ==================================  ============
``AGEP``     age                                 age
``SCHL``     educational attainment (ordinal)    education-num
``WKHP``     usual hours worked per week         hours-per-week
``COW``      class of worker                     workclass
``MAR``      marital status                      marital-status
``OCCP``     occupation code                     occupation
``POBP``     place of birth                      native-country
``RELP``     relationship to reference person    relationship
``RAC1P``    race                                race
``SEX``      **protected attribute**             sex
===========  ==================================  ============

Adult has no capital-gain/capital-loss analogue in ACSIncome; that is a real
difference between the tasks and is noted rather than papered over.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "acs"

# ACS codes are integers with no inherent order, so they are one-hot encoded like any
# other categorical. Two of them are far wider than anything in Adult -- OCCP carries
# ~370 distinct codes against Adult's widest at 41 -- so rare levels are pooled; see
# RARE_LEVEL_THRESHOLD.
CATEGORICAL = ["COW", "MAR", "OCCP", "POBP", "RELP", "RAC1P"]
NUMERIC = ["AGEP", "SCHL", "WKHP"]

PROTECTED = "SEX"
PRIVILEGED, UNPRIVILEGED = "Male", "Female"
SEX_LABELS = {1: "Male", 2: "Female"}

# ACS race codes, spelled out so intersectional subgroup tables are readable rather
# than being labelled "RAC1P=3".
RACE_LABELS = {
    1: "White", 2: "Black", 3: "Amer-Indian", 4: "Alaska-Native",
    5: "Amer-Indian-or-Alaska-Native", 6: "Asian", 7: "Pacific-Islander",
    8: "Other", 9: "Two-or-more",
}

# Levels below this share of the data are pooled into "Other". Without it, OCCP and
# POBP contribute several hundred one-hot columns, most of them near-empty, which
# inflates the feature count far past Adult's 85 and makes the two datasets'
# attribution shares incomparable. The threshold is reported in `notes`.
RARE_LEVEL_THRESHOLD = 0.005


class ACSIncomeLoader:
    """Loader for the folktables ACSIncome task, one or more states.

    Args:
        states: Two-letter state codes. A single state keeps runtime near Adult's;
            several states pooled gives a larger and more heterogeneous population.
        year: ACS survey year.
        horizon: ``"1-Year"`` or ``"5-Year"``.
    """

    def __init__(
        self,
        states: list[str] | None = None,
        *,
        year: str = "2018",
        horizon: str = "1-Year",
    ) -> None:
        self.states = states or ["CA"]
        self.year = year
        self.horizon = horizon

    @property
    def name(self) -> str:
        return f"acs_income_{'_'.join(self.states).lower()}_{self.year}"

    def _pool_rare_levels(self, column: pd.Series) -> pd.Series:
        """Collapse levels rarer than the threshold into a single 'Other'."""
        frequencies = column.value_counts(normalize=True)
        keep = set(frequencies[frequencies >= RARE_LEVEL_THRESHOLD].index)
        return column.where(column.isin(keep), other=-1)

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        from folktables import ACSDataSource, ACSIncome

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        source = ACSDataSource(
            survey_year=self.year, horizon=self.horizon, survey="person",
            root_dir=str(DATA_DIR),
        )
        frame = source.get_data(states=self.states, download=True)
        X, y, _ = ACSIncome.df_to_pandas(frame)

        X = X.reset_index(drop=True)
        y = pd.Series(np.asarray(y).astype(int).ravel(), name="income", index=X.index)

        a = X[PROTECTED].map(SEX_LABELS).astype(object)
        a.name = PROTECTED
        if a.isna().any():
            raise ValueError("unexpected SEX code outside {1, 2}")

        features = X.drop(columns=[PROTECTED])
        features["RAC1P"] = features["RAC1P"].map(RACE_LABELS).fillna("Unknown")

        pooled = {}
        for column in ("OCCP", "POBP"):
            before = features[column].nunique()
            features[column] = self._pool_rare_levels(features[column])
            pooled[column] = {"levels_before": int(before),
                              "levels_after": int(features[column].nunique())}

        categorical = [c for c in CATEGORICAL if c in features.columns]
        numeric = [c for c in NUMERIC if c in features.columns]

        if include_protected_in_features:
            features[PROTECTED] = a.to_numpy()
            categorical = [*categorical, PROTECTED]

        # Categoricals must be strings for the one-hot encoder to treat ACS integer
        # codes as unordered labels rather than as magnitudes.
        for column in categorical:
            features[column] = features[column].astype(str)

        return FairnessDataset(
            name=self.name,
            X=features[[*categorical, *numeric]],
            y=y,
            a=a,
            protected_attribute=PROTECTED,
            privileged_value=PRIVILEGED,
            unprivileged_value=UNPRIVILEGED,
            categorical_features=categorical,
            numeric_features=numeric,
            secondary_attribute="RAC1P",
            # Same semantic ordering as Adult, but note RELP is NOT sex-determining
            # here -- husband/wife is one code. That contrast is the point of the
            # dataset for this project.
            proxy_features=["RELP", "MAR", "OCCP", "WKHP"],
            notes={
                "source": "folktables ACSIncome",
                "reference": "Ding et al. (2021), Retiring Adult, NeurIPS",
                "states": self.states,
                "year": self.year,
                "horizon": self.horizon,
                "rare_level_threshold": RARE_LEVEL_THRESHOLD,
                "pooled_levels": pooled,
                "difference_from_adult":
                    "no capital-gain / capital-loss analogue; RELP records husband/wife "
                    "as a single code, so unlike Adult's `relationship` no level of it "
                    "determines sex",
            },
        )
