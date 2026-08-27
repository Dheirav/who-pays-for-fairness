#!/usr/bin/env python3
"""Independent-unit accounting: arms, populations and sources behind every headline figure.

**Individual work, beyond the course submission.**

Both external reviews raised the same objection, in the same words: a ratio like 25/26 or
21/22 reads as replication, but many of those arms come from the same population, and a
naive binomial reading of them overstates the evidence. The paper already applies this
discipline in places -- the zeta correspondence carries a population-clustered interval --
and states the rule in its accounting table. It does not apply it everywhere.

This computes the three denominators for each headline figure so none of them has to be
recalled:

* **arms** -- experimental configurations, the raw row count;
* **populations** -- disjoint person samples, the strongest replication unit. Arms of one
  population share people however many configurations they contribute;
* **sources** -- independent instruments, the external-generalisation unit.

The population rule is the one `tests/test_documented_claims.py` enforces, imported in
spirit rather than copied: strip the method, tolerance, cutoff and loan-purpose suffixes;
fold the cross-task ACS arms onto their income counterpart, since an employment row set
contains the income row set's workers; drop the protected-attribute suffix, since two
attribute arms of one state are one sample of people read two ways; and exclude the pooled
`hmda_ms_la` market, which is two markets already counted.

Run:  python scripts/independence.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "research" / "results"

_METHOD = re.compile(r"_(eo|hgb|eps\d+|op[\d]+|post|aware|s60k)$")
_PURPOSE = re.compile(r"_(purchase|refinance|cashout|improvement|other)$")


def population(name: str) -> str:
    """The paper's own definition, applied to a results directory stem."""
    stem = name.replace("_levelling_up", "")
    while _METHOD.search(stem):
        stem = _METHOD.sub("", stem)
    stem = _PURPOSE.sub("", re.sub(r"_t\d+", "", stem))
    stem = re.sub(r"^acs_(employment|coverage)_", "acs_income_", stem)
    return re.sub(r"_(rac1p|race|sex)$", "", stem)


def source(pop: str) -> str:
    for prefix, label in (("acs_income", "ACS"), ("hmda", "HMDA"), ("ipums", "IPUMS")):
        if pop.startswith(prefix):
            return label
    return {"adult": "Adult", "compas_2016": "COMPAS", "dutch_2001": "Dutch",
            "lawschool": "LSAC", "taiwan_2005": "Taiwan"}.get(pop, pop)


def account(label: str, names: list[str], figure: str) -> dict:
    pops = {population(n) for n in names} - {"hmda_ms_la_2018"}
    return {"figure": figure, "what": label, "arms": len(names),
            "populations": len(pops), "sources": len({source(p) for p in pops})}


def _read(rel: str) -> pd.DataFrame | None:
    p = R / rel
    return pd.read_csv(p) if p.exists() else None


def main() -> None:
    rows = []

    def add(label, figure, frame, col="population", keep=None):
        if frame is None:
            rows.append({"figure": figure, "what": label, "arms": "-",
                         "populations": "-", "sources": "-"}); return
        f = keep(frame) if keep else frame
        rows.append(account(label, f[col].astype(str).tolist(), figure))

    add("re-seal, unrefined rule", "9 of 10", _read("resealed/resealed.csv"))
    add("seal 1, refined rule", "4 of 8", _read("sealed/sealed.csv"),
        keep=lambda d: d[d["held_out"]])
    add("third direction cohort", "13 of 14", _read("third_direction/third_direction.csv"),
        keep=lambda d: d[~d["indeterminate"]])
    add("sealed lending cohort", "8 of 8", _read("lending_direction/lending_direction.csv"),
        keep=lambda d: d[~d["indeterminate"]])
    add("race cohort S1", "8 of 10", _read("ipums_sealed/race_s1.csv"))

    a, b = (_read("third_direction/third_direction.csv"),
            _read("lending_direction/lending_direction.csv"))
    if a is not None and b is not None:
        both = pd.concat([a, b])
        add("effect-size split, above 1 pt", "21 of 22", both[~both["indeterminate"]])
        add("effect-size split, below 1 pt", "11 of 18", both[both["indeterminate"]])

    v = _read("verdicts/verdicts.csv")
    add("audit verdict distribution", "29 of 52", v,
        keep=lambda d: d[d["verdict"] != "UNMAPPED"])

    z = _read("zeta/zeta_all_populations.csv")
    add("relaxed-zeta correspondence", "150 arms", z)
    add("zeta head-to-head, sealed", "18 of 19", _read("zeta/zeta_sealed_cohorts.csv"))

    add("landscape survey", "78% of 50", _read("survey/survey_verdicts.csv"))

    # Lending coverage: read the natural arms straight off the directories.
    # Arms with a computable selection rate, not directories -- and the difference is not
    # cosmetic. Four stored HMDA arms (LA and MS, both attributes) predate the recorded
    # test-set denominator, so they carry a measured pool change but no rate. Every lending
    # claim in the paper is read against a rate, so those four cannot enter the ratio they
    # would otherwise inflate. Counting directories reported 70 arms over 42 populations
    # here while Table I and document 72 said 66 over 40; a panel review found the two
    # tables disagreeing, and the rate-bearing set is the one the claims are about.
    lend = [d.name for d in R.glob("hmda_*_2018_*_levelling_up")
            if len(d.name.replace("_levelling_up", "").split("_")) == 4
            and "n_test" in pd.read_csv(d / "levelling_up_runs.csv", nrows=0).columns]
    if lend:
        rows.append(account("lending coverage, all markets", lend, "40 race + 26 sex"))

    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    dest = R / "independence"
    dest.mkdir(parents=True, exist_ok=True)
    out.to_csv(dest / "independence.csv", index=False)
    print(f"\nwrote {dest}/independence.csv")


if __name__ == "__main__":
    main()
