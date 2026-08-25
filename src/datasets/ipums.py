"""IPUMS International income task — the off-instrument cohort.

**Individual work, beyond the course submission.**

Every ACS population shares one survey instrument, which is why the sealed 9-of-10
cannot separate "the selection rate predicts" from "the ACS income cutoff predicts"
(the confound the paper states beside the score). This loader carries the populations
that break the tie: Brazil (2000, 2010 censuses) and Mexico (2015 intercensal, 2020
census) from IPUMS International — different continent, different instruments,
different currencies, and label thresholds that will be set by *quantile* rather than
in nominal currency, which is document 57's real-anchoring lesson applied from the
start.

Written before the extract exists. The variable set below is IPUMS-I's harmonized
naming; whether the delivered extract actually carries each column is checked loudly at
load time, and ``python -m src.experiments.analyse_ipums_sealed --verify`` reports the
delivered schema before anything else is allowed to run.

Mapping to the ACS task, so the arms are comparable:

===========  ==================================  ============
IPUMS        meaning                             ACS analogue
===========  ==================================  ============
``AGE``      age                                 AGEP
``EDATTAIN`` educational attainment (harmonized) SCHL
``MARST``    marital status                      MAR
``OCCISCO``  occupation, ISCO major group        OCCP
``INDGEN``   industry, harmonized                --
``CLASSWK``  class of worker                     COW
``URBAN``    urban/rural                         --
``SEX``      **protected attribute**             SEX
``INCEARN``  earned income (label source)        PINCP
===========  ==================================  ============

The filter mirrors folktables' ``adult_filter`` in intent: age over 16, employed where
employment status exists, and a valid positive earned income. IPUMS sentinel codes
(9{,}999{,}998 unknown / 9{,}999{,}999 NIU and their shorter variants) are treated as
missing, never as income.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .base import FairnessDataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "ipums"

# ISO numeric codes, as IPUMS-I's COUNTRY variable records them.
COUNTRIES = {"BR": 76, "MX": 484}

PROTECTED = "SEX"
PRIVILEGED, UNPRIVILEGED = "Male", "Female"
SEX_LABELS = {1: "Male", 2: "Female"}

# Brazil's RACE variable (absent from the Mexican samples). The arm follows the
# standard IBGE contrast: branco against preto+pardo (White vs Black-or-Brown),
# restricting to those groups the way the HMDA arms restrict to two, because every
# metric in this project is defined over two groups. Indigenous, Asian, other and
# unknown rows leave the arm rather than being pooled into either side.
RACE_WHITE = {10}
RACE_BLACK_BROWN = {20, 21, 22, 23, 24, 51, 53}

# Harmonized names, split by how they enter the model. Only columns actually present in
# the delivered extract are used; the loader records which in ``notes`` and refuses to
# run if the required core is missing.
CATEGORICAL = ["MARST", "EDATTAIN", "OCCISCO", "INDGEN", "CLASSWK", "URBAN"]
# YRSCHOOL is absent from Brazil 2010 and its codes 90-99 are categories, not
# years; EDATTAIN carries education categorically, so age is the one numeric.
NUMERIC = ["AGE"]
REQUIRED = ["COUNTRY", "YEAR", "AGE", "SEX"]
INCOME_CANDIDATES = ["INCEARN", "INCTOT"]

# Everything at or above this is an IPUMS missing/NIU sentinel, whatever the column
# width: 9999998/9999999 and the 8-digit variants.
INCOME_SENTINEL = 9_999_998
CHUNK_ROWS = 500_000

# Stage B may fix a per-population subsample (rows drawn once, rng(0), after the
# filter): the filtered samples run 161k-415k, the record's own populations run
# 10k-130k, and the noise floor is 2,500 test rows -- scale buys runtime, not power.
# None means the full filtered sample; a value is part of the sealed stage-B commit
# and joins the dataset's name so full-size and subsampled runs can never collide.
SUBSAMPLE_ROWS: int | None = 60_000


def extract_files() -> list[Path]:
    return sorted([*DATA_DIR.glob("*.csv"), *DATA_DIR.glob("*.csv.gz")])


class IPUMSIncomeLoader:
    """One country-year of the IPUMS International extract, as an income task.

    Args:
        country: ``"BR"`` or ``"MX"``.
        year: census/survey year as a string, e.g. ``"2000"``.
        protected: only ``"SEX"`` is supported; present for interface symmetry.
        threshold: income cutoff in the sample's own currency units. Required ---
            there is deliberately no default, because document 57 showed a fixed
            nominal default is a silent task change; the sealed protocol sets these
            by quantile and commits the resulting values before any run.
    """

    def __init__(self, country: str, year: str, *,
                 protected: str = PROTECTED, threshold: int | None = None) -> None:
        if country.upper() not in COUNTRIES:
            raise KeyError(f"unknown IPUMS country '{country}'; have {sorted(COUNTRIES)}")
        if protected not in (PROTECTED, "RACE"):
            raise KeyError("only SEX and RACE are supported on the IPUMS cohort")
        if protected == "RACE" and country.upper() != "BR":
            raise KeyError("RACE is only carried by the Brazilian samples")
        if threshold is None:
            raise ValueError(
                "an IPUMS spec must carry an explicit income threshold "
                "(e.g. 'ipums:BR:2000:SEX:350'); the sealed protocol derives it "
                "by quantile and commits it before any run"
            )
        self.country = country.upper()
        self.year = str(year)
        self.protected = protected
        self.threshold = int(threshold)

    @property
    def name(self) -> str:
        stem = f"ipums_income_{self.country.lower()}_{self.year}"
        if self.protected != PROTECTED:
            stem = f"{stem}_race"
        stem = f"{stem}_t{self.threshold}"
        if SUBSAMPLE_ROWS is not None:
            stem = f"{stem}_s{SUBSAMPLE_ROWS // 1000}k"
        return stem

    def _read(self) -> pd.DataFrame:
        files = extract_files()
        if not files:
            raise FileNotFoundError(
                f"no IPUMS extract under {DATA_DIR}; place the delivered "
                ".csv or .csv.gz there"
            )
        code, year = COUNTRIES[self.country], int(self.year)
        wanted = [*REQUIRED, *INCOME_CANDIDATES, *CATEGORICAL, *NUMERIC, "EMPSTAT",
                  "PERWT", "RACE"]
        chunks = []
        for path in files:
            header = pd.read_csv(path, nrows=0)
            usecols = [c for c in wanted if c in header.columns]
            missing = [c for c in REQUIRED if c not in header.columns]
            if missing:
                raise KeyError(f"{path.name} lacks required columns {missing}; "
                               f"delivered: {sorted(header.columns)}")
            if not any(c in header.columns for c in INCOME_CANDIDATES):
                raise KeyError(f"{path.name} carries no income column "
                               f"({INCOME_CANDIDATES}); the task cannot be built")
            # Chunked so a multi-sample extract never has to fit in memory whole;
            # the 8 GB WSL ceiling is a measured constraint of this project's machine.
            for chunk in pd.read_csv(path, usecols=usecols, chunksize=CHUNK_ROWS):
                part = chunk[(chunk["COUNTRY"] == code) & (chunk["YEAR"] == year)]
                if len(part):
                    chunks.append(part)
        if not chunks:
            raise ValueError(f"extract holds no rows for {self.country} {self.year}")
        return pd.concat(chunks, ignore_index=True)

    def load(self, *, include_protected_in_features: bool = False) -> FairnessDataset:
        frame = self._read()

        income_column = next(c for c in INCOME_CANDIDATES if c in frame.columns)
        income = pd.to_numeric(frame[income_column], errors="coerce")
        income = income.where(income < INCOME_SENTINEL)

        keep = (frame["AGE"].between(17, 90)) & income.notna() & (income > 0)
        if "EMPSTAT" in frame.columns:
            keep &= frame["EMPSTAT"] == 1
        keep &= frame["SEX"].isin([1, 2])
        if self.protected == "RACE":
            keep &= frame["RACE"].isin(RACE_WHITE | RACE_BLACK_BROWN)
        frame, income = frame[keep].reset_index(drop=True), income[keep].reset_index(drop=True)
        if SUBSAMPLE_ROWS is not None and len(frame) > SUBSAMPLE_ROWS:
            chosen = np.random.default_rng(0).choice(len(frame), SUBSAMPLE_ROWS,
                                                     replace=False)
            chosen.sort()
            frame = frame.iloc[chosen].reset_index(drop=True)
            income = income.iloc[chosen].reset_index(drop=True)

        y = pd.Series((income > self.threshold).astype(int), name="income")
        if self.protected == "RACE":
            a = pd.Series(np.where(frame["RACE"].isin(RACE_WHITE),
                                   "White", "Black-or-Brown"), dtype=object)
            privileged, unprivileged = "White", "Black-or-Brown"
        else:
            a = frame["SEX"].map(SEX_LABELS).astype(object)
            privileged, unprivileged = PRIVILEGED, UNPRIVILEGED
        a.name = self.protected

        categorical = [c for c in CATEGORICAL
                       if c in frame.columns and frame[c].notna().any()]
        numeric = [c for c in NUMERIC
                   if c in frame.columns and frame[c].notna().any()]
        features = frame[[*categorical, *numeric]].copy()
        for column in categorical:
            features[column] = features[column].astype(str)

        if include_protected_in_features:
            features[PROTECTED] = a.to_numpy()
            categorical = [*categorical, PROTECTED]

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
                "source": "IPUMS International",
                "reference": "Minnesota Population Center, IPUMS-I",
                "country": self.country,
                "year": self.year,
                "income_column": income_column,
                "income_threshold": self.threshold,
                "filter": "age 17-90, employed where EMPSTAT present, "
                          "valid positive income",
                "weights": "PERWT carried in the extract but unused, matching the "
                           "ACS convention declared in the paper",
            },
        )
