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

# ``RAC1P`` is selectable as the protected attribute for one narrow purpose: the group
# ratio N_priv/N_unpriv on sex is confined to 1.02-1.24 across every ACS state, while
# Adult sits alone at 2.08 and therefore carries the entire high-ratio end of P1 (see
# docs/11, "Limits of the replication itself"). Splitting on race instead spans roughly
# 1.5 to 15 *at large sample sizes*, which is the region the design is missing.
#
# The split is White vs everyone else. That aggregate is not defensible as a claim
# about racial fairness and is not used as one: this arm exists to vary two numbers --
# the group ratio and the sample size -- in a formula whose inputs are only ever counts.
# Binarising as White vs Black instead would defeat the purpose, because the states with
# a large Black population are precisely the ones nearest 1:1 (MS ~1.5) while the states
# with a high ratio would have an unprivileged group of a few dozen people.
RACE_PRIVILEGED, RACE_UNPRIVILEGED = "White", "Non-White"

# Which attributes may be protected, and what each implies for the rest of the dataset.
# Keyed by column; the values that are not the protected one stay in the features.
PROTECTED_SCHEMES = {
    "SEX": {
        "privileged": PRIVILEGED,
        "unprivileged": UNPRIVILEGED,
        "secondary": "RAC1P",
        # Same semantic ordering as Adult, but note RELP is NOT sex-determining here --
        # husband/wife is one code. That contrast is the point of the dataset.
        "proxies": ["RELP", "MAR", "OCCP", "WKHP"],
    },
    "RAC1P": {
        "privileged": RACE_PRIVILEGED,
        "unprivileged": RACE_UNPRIVILEGED,
        "secondary": "SEX",
        # Place of birth is to race what `relationship` is to sex on Adult: the
        # single most direct reconstruction available in the feature set.
        "proxies": ["POBP", "OCCP", "COW", "SCHL"],
    },
}

# Levels below this share of the data are pooled into "Other". Without it, OCCP and
# POBP contribute several hundred one-hot columns, most of them near-empty, which
# inflates the feature count far past Adult's 85 and makes the two datasets'
# attribution shares incomparable. The threshold is reported in `notes`.
RARE_LEVEL_THRESHOLD = 0.005
POOLED_LABEL = "OTHER-RARE"


class ACSIncomeLoader:
    """Loader for the folktables ACSIncome task, one or more states.

    Args:
        states: Two-letter state codes. A single state keeps runtime near Adult's;
            several states pooled gives a larger and more heterogeneous population.
        protected: Which column to constrain on -- see :data:`PROTECTED_SCHEMES`.
        year: ACS survey year.
        horizon: ``"1-Year"`` or ``"5-Year"``.
    """

    def __init__(
        self,
        states: list[str] | None = None,
        *,
        protected: str = PROTECTED,
        year: str = "2018",
        horizon: str = "1-Year",
    ) -> None:
        if protected not in PROTECTED_SCHEMES:
            raise KeyError(
                f"cannot protect '{protected}'; available: {sorted(PROTECTED_SCHEMES)}"
            )
        self.states = states or ["CA"]
        self.protected = protected
        self.year = year
        self.horizon = horizon

    @property
    def name(self) -> str:
        """Identity of the population *as configured*, not just as sampled.

        The protected attribute belongs in the name because it changes the features,
        the groups and every metric downstream -- two runs differing only in it are
        different datasets. Omitting it would give a race-protected Mississippi run the
        same output directory as the sex-protected one already committed there, which
        is exactly the silent-overwrite failure ``results_io`` and
        ``tests/test_output_isolation.py`` exist to prevent. The default is left
        unsuffixed so the committed sex results keep their paths.
        """
        stem = f"acs_income_{'_'.join(self.states).lower()}_{self.year}"
        return stem if self.protected == PROTECTED else f"{stem}_{self.protected.lower()}"

    def _pool_rare_levels(self, column: pd.Series) -> pd.Series:
        """Collapse levels rarer than the threshold into a single readable bucket.

        Named rather than a numeric sentinel: these labels become one-hot column names
        and then SHAP feature names, and ``OCCP_-1.0`` in an attribution table is
        indistinguishable from a real occupation code to anyone reading it.
        """
        frequencies = column.value_counts(normalize=True)
        keep = set(frequencies[frequencies >= RARE_LEVEL_THRESHOLD].index)
        pooled = column.astype(str).where(column.isin(keep), other=POOLED_LABEL)
        return pooled

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

        scheme = PROTECTED_SCHEMES[self.protected]

        sex = X[PROTECTED].map(SEX_LABELS).astype(object)
        if sex.isna().any():
            raise ValueError("unexpected SEX code outside {1, 2}")
        race = X["RAC1P"].map(RACE_LABELS).fillna("Unknown")

        if self.protected == PROTECTED:
            a = sex
        else:
            # Everything that is not White, including "Unknown", falls in the
            # unprivileged group; see the note on RACE_PRIVILEGED for why the split is
            # this coarse and what it is and is not evidence of.
            a = race.where(race == RACE_PRIVILEGED, other=RACE_UNPRIVILEGED).astype(object)
        a.name = self.protected

        # Only the protected column leaves the feature set. The other one stays, which
        # is what makes it available as `secondary_attribute` for the intersectional
        # analysis -- and, for the race arm, keeps sex present as a candidate proxy.
        features = X.drop(columns=[self.protected])
        if "RAC1P" in features.columns:
            features["RAC1P"] = race
        if PROTECTED in features.columns:
            features[PROTECTED] = sex

        pooled = {}
        for column in ("OCCP", "POBP"):
            before = features[column].nunique()
            features[column] = self._pool_rare_levels(features[column])
            pooled[column] = {"levels_before": int(before),
                              "levels_after": int(features[column].nunique())}

        # SEX joins the candidates because it is a genuine feature whenever it is not
        # the protected attribute; the presence filter then drops whichever one is.
        categorical = [c for c in [*CATEGORICAL, PROTECTED] if c in features.columns]
        numeric = [c for c in NUMERIC if c in features.columns]

        if include_protected_in_features:
            features[self.protected] = a.to_numpy()
            categorical = [*categorical, self.protected]

        # Categoricals must be strings for the one-hot encoder to treat ACS integer
        # codes as unordered labels rather than as magnitudes.
        for column in categorical:
            features[column] = features[column].astype(str)

        return FairnessDataset(
            name=self.name,
            X=features[[*categorical, *numeric]],
            y=y,
            a=a,
            protected_attribute=self.protected,
            privileged_value=scheme["privileged"],
            unprivileged_value=scheme["unprivileged"],
            categorical_features=categorical,
            numeric_features=numeric,
            secondary_attribute=scheme["secondary"],
            proxy_features=scheme["proxies"],
            notes={
                "source": "folktables ACSIncome",
                "reference": "Ding et al. (2021), Retiring Adult, NeurIPS",
                "states": self.states,
                "protected_attribute": self.protected,
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
