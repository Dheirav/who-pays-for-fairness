"""COMPAS recidivism screening, as a third instrument.

**Individual work, beyond the course submission.**

Every population measured before this is either the American Community Survey or HMDA
mortgage records: two instruments, one country, one year. The selection-rate rule is claimed
to be about *decision systems*, and that claim cannot be tested inside the two instruments it
was found in. This is the first of two datasets from unrelated domains.

Three decisions here would silently corrupt the result if made the other way, so each is
stated rather than buried.

**The label is inverted, on purpose.** This project's convention is that ``y == 1`` is the
*favourable* outcome and the selection rate is the fraction of people receiving it. The
recorded target, ``two_year_recid``, is the opposite: a 1 means the person reoffended, which
is the outcome that gets someone detained. So the target is ``1 - two_year_recid`` --
"predicted not to reoffend", which is the decision a defendant wants. Leaving the raw
polarity would invert every direction in this project's vocabulary and produce numbers that
look valid and mean the opposite.

**The COMPAS score is not a feature.** ``decile_score`` and ``score_text`` are the output of
the very kind of instrument being audited. Including them would make the task "reproduce
COMPAS from COMPAS", the model would be near-perfect for uninteresting reasons, and the
mitigation would be operating on a proxy for a proprietary score rather than on a risk
prediction. They are dropped, as is ``v_decile_score``.

**Race is restricted to two groups.** The interface takes one binary protected attribute, and
ProPublica's analysis -- the reason this dataset is a fairness benchmark at all -- compares
African-American against Caucasian defendants. Other groups are dropped rather than pooled
into a meaningless "other", and the row count that results is reported rather than hidden.

**This population is below document 15's floor, and that is expected.**
[Document 15](../../research/docs/15-arbitrariness-at-small-scale.md) found that under about
2,500 test subjects the reduction's own randomness exceeds the entire effect of the
constraint. After ProPublica's filter this dataset has 6,172 rows, so a 30% test split is
about 1,850 -- under the floor. Arms here are expected to be noisy, more seeds are used, and
a noisy result is a *confirmation* of document 15 on a new dataset rather than a failure of
the rule being tested.

Source: github.com/propublica/compas-analysis, the file behind "Machine Bias" (2016).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "compas"
CSV_URL = ("https://raw.githubusercontent.com/propublica/compas-analysis/"
           "master/compas-scores-two-years.csv")

RACE, SEX = "race", "sex"

# ProPublica compare these two groups; the interface takes one binary attribute.
RACE_GROUPS = ("Caucasian", "African-American")
SEX_GROUPS = ("Male", "Female")

PROTECTED_SCHEMES = {
    RACE: {"privileged": "Caucasian", "unprivileged": "African-American",
           "keep": RACE_GROUPS},
    # Female is the ADVANTAGED group on this outcome, which is the reverse of the usual
    # reading and is a fact about the data rather than a claim about society: women in this
    # cohort reoffend less (favourable rate 0.649 against 0.521), so they receive the
    # favourable prediction more often. `privileged` must follow the base rates or every
    # who-pays number comes out sign-inverted while still looking plausible -- exactly the
    # orientation slip `base.py` was written to prevent.
    SEX: {"privileged": "Female", "unprivileged": "Male", "keep": SEX_GROUPS},
}

CATEGORICAL = ["c_charge_degree", "age_cat"]
NUMERIC = ["age", "priors_count", "juv_fel_count", "juv_misd_count", "juv_other_count"]


class CompasLoader:
    """COMPAS two-year recidivism, with the favourable outcome as the target."""

    def __init__(self, *, protected: str = RACE) -> None:
        if protected not in PROTECTED_SCHEMES:
            raise KeyError(
                f"cannot protect '{protected}'; available: {sorted(PROTECTED_SCHEMES)}")
        self.protected = protected

    @property
    def name(self) -> str:
        return f"compas_2016_{self.protected}"

    def _download(self) -> Path:
        path = DATA_DIR / "compas-scores-two-years.csv"
        if not path.exists():
            import urllib.request

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(CSV_URL, path)   # noqa: S310 - fixed GitHub host
        return path

    @staticmethod
    def _propublica_filter(frame: pd.DataFrame) -> pd.DataFrame:
        """The filter ProPublica document in their own notebook, applied unchanged.

        Reproducing their row count is the only available check that this is the same
        population every other paper on this dataset is talking about. Inventing a cleaner
        filter would give a defensible dataset that is not comparable to anything.
        """
        return frame[
            (frame["days_b_screening_arrest"] <= 30)
            & (frame["days_b_screening_arrest"] >= -30)
            & (frame["is_recid"] != -1)
            & (frame["c_charge_degree"] != "O")
            & (frame["score_text"] != "N/A")
        ]

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        scheme = PROTECTED_SCHEMES[self.protected]
        frame = self._propublica_filter(pd.read_csv(self._download()))
        frame = frame[frame[self.protected].isin(scheme["keep"])].reset_index(drop=True)

        # 1 is favourable: predicted NOT to reoffend. See the module docstring.
        y = (1 - frame["two_year_recid"]).astype(int).rename("no_recidivism")
        a = frame[self.protected].astype(str)

        categorical = list(CATEGORICAL)
        numeric = list(NUMERIC)
        other = SEX if self.protected == RACE else RACE
        if other == SEX:
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
            # priors_count carries the most information about race here, and it is the
            # feature the fairness literature argues about most.
            proxy_features=["priors_count", "age_cat"],
            notes={
                "source": CSV_URL,
                "filter": "ProPublica's documented screening-date and charge-degree filter",
                "label": "1 - two_year_recid, so that 1 is the favourable outcome",
                "excluded": "decile_score, score_text, v_decile_score -- the instrument's "
                            "own output, which would make the task circular",
                "power": "test split is below document 15's 2,500-subject floor; arms here "
                         "are expected to be noisy and are run at more seeds",
            },
        )
