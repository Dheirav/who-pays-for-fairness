"""HMDA — mortgage approve/deny, the second *domain* rather than a second population.

**Individual work, beyond the course submission.**

Every population in this project so far is a household survey: Adult is a 1994 Census
extract and ACS Income is the modern reconstruction of it (Ding et al., 2021). Nineteen
populations across two protected attributes sounds like broad external validity, and it is
not: eighteen of them are US state slices of **one survey instrument**, sharing an
encoding, a sampling design and a synthetic income threshold. "Replicates across
populations" and "replicates across domains" are different claims and only the first has
been earned.

The Home Mortgage Disclosure Act data is a different kind of object. It is not a survey of
people, it is an administrative record of **real lending decisions**, mandated by statute
and reported by the lender. The label is not a threshold someone chose — it is whether an
institution approved a mortgage application. That makes levelling down concrete in a way
income prediction cannot: a favourable decision withdrawn is a mortgage not issued.

Why Mississippi
---------------
It is the state where [document 12](../../research/docs/12-intersectional-across-populations.md)
found the strongest intersectional result on ACS. Running HMDA there compares the *same
geography* across two unrelated instruments, which separates "a property of the survey"
from "a property of the population" — the one confound nineteen ACS states cannot break.

It also has the disparity. On 2018 applications, White applicants are approved at 0.772
against 0.521 for Black applicants: a **25-point gap, larger than Adult's sex gap**, which
is the disparity this project's entire argument is built on.

Two arms, mirroring the ACS design: ``derived_sex`` (Male vs Female) and ``derived_race``
(White vs Black or African American).

Leakage, and why the feature set is a whitelist
-----------------------------------------------
HMDA records the loan as well as the application, so a large share of its 99 columns exist
only *because* the decision went a particular way. Two kinds, and the second is the reason
this module cannot use a blacklist:

**Continuous fields recorded only for originated loans.** These announce themselves —
``interest_rate`` is missing for 96.8% of denials against 1.7% of approvals. A missingness
comparison across the outcome finds all of them (``rate_spread``, ``total_loan_costs``,
``origination_charges``, ``discount_points``, ``lender_credits``).

**Coded fields with a "not applicable" level, which that comparison cannot see.**
``denial_reason-1`` is *always populated*, so its missingness gap is 0.000 — and it alone
separates the outcome at **99.2% purity against a 72% base rate**, because every approved
application is coded "not applicable" and every denial carries a reason. ``purchaser_type``
is the same shape: value 0 covers 100% of denials and 52% of approvals, so any non-zero
value implies approval with certainty.

A blacklist built from the missingness diagnostic would have dropped the first group,
kept ``denial_reason-1``, and produced a model with near-perfect accuracy that had learned
nothing. Hence :data:`CATEGORICAL` and :data:`NUMERIC` below are an explicit allow-list of
fields available *at the moment of application*, and everything else is dropped by default.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "hmda"

# CFPB's public data browser. One state-year of approve/deny decisions.
CSV_URL = (
    "https://ffiec.cfpb.gov/v2/data-browser-api/view/csv"
    "?years={year}&states={state}&actions_taken=1,2,3"
)

# action_taken: 1 originated, 2 approved but not accepted, 3 denied. 1 and 2 are both
# *the lender approving*; the difference between them is the applicant's subsequent
# choice, which is not the decision under study. Codes 4 (withdrawn), 5 (closed for
# incompleteness), 6 (purchased loan) and 7/8 (preapproval requests) are excluded at
# download: none of them is a completed approve-or-deny by the lender.
APPROVED_CODES = (1, 2)
DENIED_CODE = 3

# Available when the application is filed. Anything not named here is dropped -- see the
# module docstring for why this is an allow-list rather than an exclusion list.
CATEGORICAL = [
    "conforming_loan_limit", "derived_loan_product_type", "derived_dwelling_category",
    "loan_type", "loan_purpose", "lien_status", "reverse_mortgage",
    "open-end_line_of_credit", "business_or_commercial_purpose", "occupancy_type",
    "construction_method", "total_units", "debt_to_income_ratio", "applicant_age",
    "co-applicant_age", "applicant_credit_score_type", "co-applicant_credit_score_type",
    "submission_of_application", "initially_payable_to_institution", "preapproval",
    "derived_msa-md",
]
NUMERIC = [
    "loan_amount", "income", "property_value", "tract_population",
    "tract_minority_population_percent", "tract_to_msa_income_percentage",
    "tract_owner_occupied_units", "tract_one_to_four_family_homes",
    "tract_median_age_of_housing_units", "ffiec_msa_md_median_family_income",
]

# Recorded, and deliberately unused. Kept as data rather than as prose so the writeup can
# cite the reason per field and a reader can check the classification.
EXCLUDED: dict[str, str] = {
    "interest_rate": "post-decision: 96.8% missing for denials",
    "rate_spread": "post-decision: 96.8% missing for denials",
    "total_loan_costs": "post-decision: recorded for originated loans",
    "origination_charges": "post-decision: recorded for originated loans",
    "total_points_and_fees": "post-decision: recorded for originated loans",
    "discount_points": "post-decision: recorded for originated loans",
    "lender_credits": "post-decision: recorded for originated loans",
    "loan_to_value_ratio": "post-decision: 29.5% missing for denials against 7.4%",
    "loan_term": "post-decision: missingness differs by outcome",
    "intro_rate_period": "post-decision: a term of the originated loan",
    "prepayment_penalty_term": "post-decision: a term of the originated loan",
    "negative_amortization": "post-decision: a term of the originated loan",
    "interest_only_payment": "post-decision: a term of the originated loan",
    "balloon_payment": "post-decision: a term of the originated loan",
    "other_nonamortizing_features": "post-decision: a term of the originated loan",
    "hoepa_status": "post-decision: a status of the originated loan",
    "multifamily_affordable_units": "post-decision: recorded for originated loans",
    "denial_reason-1": "IS the label: 99.2% purity alone, with no missingness gap",
    "denial_reason-2": "IS the label",
    "denial_reason-3": "IS the label",
    "denial_reason-4": "IS the label",
    "purchaser_type": "post-decision: any non-zero value implies approval with certainty",
    "aus-1": "the automated underwriting result; too close to the decision itself",
    "aus-2": "as aus-1", "aus-3": "as aus-1", "aus-4": "as aus-1", "aus-5": "as aus-1",
    "applicant_sex": "a protected attribute", "co-applicant_sex": "a protected attribute",
    "derived_ethnicity": "a protected attribute (ECOA), not used as a feature",
    "applicant_age_above_62": "duplicates applicant_age, as Adult's `education` duplicated "
                              "`education-num`; keeping both double-counts it in attribution",
    "co-applicant_age_above_62": "duplicates co-applicant_age",
    "lei": "lender identifier: ~600 levels, and an institution fixed effect rather than a "
           "property of the applicant",
    "census_tract": "identifier: thousands of levels",
    "county_code": "identifier: high cardinality, and tract-level covariates carry the "
                   "geography already",
    "activity_year": "constant within a download",
    "state_code": "constant within a download",
}

SEX, RACE = "derived_sex", "derived_race"

PROTECTED_SCHEMES = {
    SEX: {
        "privileged": "Male",
        "unprivileged": "Female",
        "secondary": RACE,
        # Ordered most-determining-first, from `attribute_leakage` on this dataset rather
        # than from intuition. Sex is weakly encoded here compared with Adult, where
        # `relationship` fixes it outright for 46% of rows.
        "proxies": ["income", "loan_amount", "co-applicant_age", "applicant_age"],
    },
    RACE: {
        "privileged": "White",
        "unprivileged": "Black or African American",
        "secondary": SEX,
        # `tract_minority_population_percent` is what Adult's `relationship` was for sex
        # and what ACS conspicuously lacked: a strong, *natural* proxy, already in the
        # data. Document 16 had to plant one synthetically because ACS offered none.
        "proxies": ["tract_minority_population_percent", "tract_to_msa_income_percentage",
                    "income", "derived_msa-md"],
    },
}

# `derived_sex` is 34% "Joint" and `derived_race` has nine levels. Both arms restrict to
# two groups, which is what every metric in this project is defined over.
ARM_GROUPS = {
    SEX: ["Male", "Female"],
    RACE: ["White", "Black or African American"],
}

RARE_LEVEL_THRESHOLD = 0.005
POOLED_LABEL = "OTHER-RARE"


class HMDALoader:
    """Loader for one state-year of HMDA approve/deny decisions.

    Args:
        state: Two-letter state code.
        protected: ``derived_sex`` or ``derived_race``.
        year: HMDA reporting year.
    """

    def __init__(self, state: str = "MS", *, protected: str = RACE,
                 year: str = "2018") -> None:
        if protected not in PROTECTED_SCHEMES:
            raise KeyError(
                f"cannot protect '{protected}'; available: {sorted(PROTECTED_SCHEMES)}"
            )
        self.state = state.upper()
        self.protected = protected
        self.year = year

    @property
    def name(self) -> str:
        """Population identity including the arm, for the same reason ACS does it.

        Two arms over one state-year are different datasets -- different groups, different
        features, different metrics -- and sharing an output directory between them is the
        silent-overwrite failure ``results_io`` exists to prevent.
        """
        return f"hmda_{self.state.lower()}_{self.year}_{self.protected.replace('derived_', '')}"

    def _download(self) -> Path:
        path = DATA_DIR / f"hmda_{self.year}_{self.state}.csv"
        if not path.exists():
            import urllib.request

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            url = CSV_URL.format(year=self.year, state=self.state)
            urllib.request.urlretrieve(url, path)     # noqa: S310 - fixed CFPB host
        return path

    def _pool_rare_levels(self, column: pd.Series) -> pd.Series:
        frequencies = column.value_counts(normalize=True)
        keep = set(frequencies[frequencies >= RARE_LEVEL_THRESHOLD].index)
        return column.astype(str).where(column.isin(keep), other=POOLED_LABEL)

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        scheme = PROTECTED_SCHEMES[self.protected]
        wanted = [*CATEGORICAL, *NUMERIC, SEX, RACE, "action_taken"]
        frame = pd.read_csv(self._download(), low_memory=False, usecols=wanted)

        n_downloaded = len(frame)
        frame = frame[frame["action_taken"].isin([*APPROVED_CODES, DENIED_CODE])]
        # 1 is the favourable outcome throughout this project: here, the lender approved.
        y = frame["action_taken"].isin(APPROVED_CODES).astype(int)

        # Restrict to the two groups the arm compares. This is a real reduction and is
        # reported: on Mississippi 2018 the sex arm keeps ~56% of applications, because
        # "Joint" is the single largest category and is not a person's sex.
        in_arm = frame[self.protected].isin(ARM_GROUPS[self.protected])
        frame, y = frame[in_arm], y[in_arm]
        n_in_arm = len(frame)

        features = frame[[*CATEGORICAL, *NUMERIC]].copy()

        # HMDA lets institutions below a reporting threshold file the literal string
        # "Exempt" in otherwise numeric fields, so `property_value` and `income` arrive as
        # object columns. Coercing here turns the sentinel into NaN *before* the
        # completeness mask, which routes those rows through the same listwise deletion as
        # any other missing value rather than crashing the encoder further downstream.
        n_exempt = 0
        for column in NUMERIC:
            coerced = pd.to_numeric(features[column], errors="coerce")
            n_exempt += int((coerced.isna() & features[column].notna()).sum())
            features[column] = coerced

        # Listwise deletion, as everywhere else in this project (see docs/01).
        complete = features.notna().all(axis=1)
        frame, y, features = frame[complete], y[complete], features[complete]

        frame = frame.reset_index(drop=True)
        features = features.reset_index(drop=True)
        y = pd.Series(y.to_numpy(), index=features.index, name="approved")

        a = frame[self.protected].astype(object)
        a.index, a.name = features.index, self.protected

        # The arm's *other* attribute stays in the features, which is what makes it
        # available as `secondary_attribute` for the intersectional analysis -- the same
        # arrangement as ACS.
        other = SEX if self.protected == RACE else RACE
        features = features.copy()
        features[other] = frame[other].astype(str).to_numpy()

        categorical = [*CATEGORICAL, other]
        numeric = list(NUMERIC)

        if include_protected_in_features:
            features[self.protected] = a.to_numpy()
            categorical = [*categorical, self.protected]

        pooled = {}
        for column in categorical:
            before = features[column].nunique()
            features[column] = self._pool_rare_levels(features[column])
            after = features[column].nunique()
            if after != before:
                pooled[column] = {"levels_before": int(before), "levels_after": int(after)}

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
                "source": "CFPB HMDA Data Browser",
                "reference": "Home Mortgage Disclosure Act, 2018 reporting year",
                "state": self.state,
                "year": self.year,
                "protected_attribute": self.protected,
                "task": "did the lender approve the mortgage application",
                "favourable_outcome": "action_taken in {1 originated, 2 approved not accepted}",
                "n_downloaded": int(n_downloaded),
                "n_in_arm": int(n_in_arm),
                "n_complete_cases": int(len(features)),
                "n_non_numeric_sentinels_coerced": int(n_exempt),
                "rare_level_threshold": RARE_LEVEL_THRESHOLD,
                "pooled_levels": pooled,
                "excluded_columns": EXCLUDED,
                "difference_from_the_survey_datasets":
                    "an administrative record of real lending decisions rather than a "
                    "household survey; the label is an institution's decision, not a "
                    "threshold applied to reported income",
            },
        )
