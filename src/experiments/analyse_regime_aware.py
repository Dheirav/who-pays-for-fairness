"""The deconfounding cell: attribute-aware in-processing, sealed before any of its arms exist.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists.** The fourth council's causal methodologist
identified the confound this test removes: the paper's regime contrast changes two
things at once --- both attribute-aware cells are post-processing, both blind cells are
the reduction --- so "the boundary is attribute access" and "the boundary is the
optimizer family" are observationally equivalent in the record so far. This runs the
missing cell: the \\emph{same} reduction (ExponentiatedGradient, demographic parity,
$\\varepsilon = 0.01$), on the \\emph{same} populations as document 43's contrast, with
one change --- the model reads the protected attribute
(``include_protected_in_features``), so the constraint operates where the theory says
the direction is determined.

The populations
---------------
Document 43's regime cohort, fixed here: Adult, the twelve ACS states post-processed
there, both HMDA markets' race arms, COMPAS, the Dutch census, and LSAC --- eighteen
populations, natural arms, five seeds. The frozen exclusions apply to the correlation
(parity gap $\\ge 0.05$, accuracy $\\ge \\max(p, 1-p)$, test split $\\ge 2{,}500$);
direction rows are reported for every population with exceptions named.

The two readings, and what each predicts --- committed now
----------------------------------------------------------
**Theory reading (attribute access is the boundary):**
  * **R1**: the advantaged group loses and the disadvantaged gains (seed-mean weak
    inequalities, as the theorem states them) in **all** scorable populations --- the
    bar is all of them because the theorem says "necessarily"; a single clean exception
    is reported as such.
  * **R2**: the baseline selection rate predicts nothing: $|r| < 0.30$ across the
    retained natural arms --- the same bar document 43's naive alternative carried.

**Optimizer-family reading (the reduction is the boundary):** the relationship
persists when the same optimizer merely gains the attribute: $r \\ge +0.40$.

**The dead zone is declared in advance:** $0.30 \\le r < 0.40$, or R1 failing while R2
holds, settles neither reading; the outcome is recorded as UNDECIDED and no verdict is
claimed. Nothing about one sub-test may rescue the other.

Run:  python -m src.experiments.analyse_regime_aware          # score stored _aware arms
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# Document 43's regime cohort: (spec, result stem). The _aware suffix is the runner's.
POPULATIONS = [
    ("adult", "adult"),
    ("acs:AL", "acs_income_al_2018"),
    ("acs:CT", "acs_income_ct_2018"),
    ("acs:KY", "acs_income_ky_2018"),
    ("acs:MS", "acs_income_ms_2018"),
    ("acs:ND", "acs_income_nd_2018"),
    ("acs:NM", "acs_income_nm_2018"),
    ("acs:OR", "acs_income_or_2018"),
    ("acs:SC", "acs_income_sc_2018"),
    ("acs:UT", "acs_income_ut_2018"),
    ("acs:VT", "acs_income_vt_2018"),
    ("acs:WV", "acs_income_wv_2018"),
    ("acs:WY", "acs_income_wy_2018"),
    ("hmda:MS:derived_race", "hmda_ms_2018_race"),
    ("hmda:LA:derived_race", "hmda_la_2018_race"),
    ("compas", "compas_2016_race"),
    ("dutch", "dutch_2001_sex"),
    ("lawschool", "lawschool_race"),
]

R2_THEORY_BAR = 0.30       # |r| below this: the rate predicts nothing, as theory reads
R2_FAMILY_BAR = 0.40       # r at or above this: the relationship survived the attribute
NOISE_FLOOR = 2500
GAP_FLOOR = 0.05


def main() -> None:
    from .analyse_calibration import majority_baseline

    rows = []
    for spec, stem in POPULATIONS:
        path = (RESEARCH_RESULTS_DIR / f"{stem}_levelling_up_aware"
                / "levelling_up_runs.csv")
        if not path.exists():
            print(f"  {stem}: no aware arm yet")
            continue
        runs = pd.read_csv(path)
        base = runs[runs["arm"] == "baseline"]
        mit = runs[runs["arm"] == "expgrad_dp"]
        rows.append({
            "population": stem,
            "rate": float(base["positives"].mean()) / float(base["n_test"].mean()),
            "gap": float(base["dp_diff"].mean()),
            "acc": float(base["accuracy"].mean()),
            "n_test": float(base["n_test"].mean()),
            "trivial": majority_baseline(spec),
            "pie": float(mit["positives_pct_change"].mean()),
            "priv_lost": float(mit["priv_lost"].mean()),
            "unpriv_gained": float(mit["unpriv_gained"].mean()),
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no aware arms have been run yet")

    frame["as_theory_predicts"] = ((frame["priv_lost"] >= 0)
                                   & (frame["unpriv_gained"] >= 0))
    print(frame.round(3).to_string(index=False))

    correct, total = int(frame["as_theory_predicts"].sum()), len(frame)
    r1 = correct == total
    print(f"\nR1  advantaged loses AND disadvantaged gains: {correct}/{total}  "
          f"{'HOLDS' if r1 else 'FAILS'}  (bar: all of them)")
    for _, row in frame[~frame["as_theory_predicts"]].iterrows():
        print(f"    exception: {row['population']} (priv_lost {row['priv_lost']:.0f}, "
              f"unpriv_gained {row['unpriv_gained']:.0f})")

    kept = frame[(frame["gap"] >= GAP_FLOOR) & (frame["n_test"] >= NOISE_FLOOR)
                 & (frame["acc"] >= frame["trivial"])]
    r = float(np.corrcoef(kept["rate"], kept["pie"])[0, 1])
    print(f"\nR2  rate vs pool change across {len(kept)} retained natural arms: "
          f"r = {r:+.3f}")
    print(f"    theory reading needs |r| < {R2_THEORY_BAR}; "
          f"optimizer-family reading needs r >= {R2_FAMILY_BAR}")

    if r1 and abs(r) < R2_THEORY_BAR:
        verdict = ("THEORY READING HOLDS: the boundary is attribute access --- the same "
                   "optimizer, given the attribute, behaves as the theorem determines")
    elif r >= R2_FAMILY_BAR:
        verdict = ("OPTIMIZER-FAMILY READING: the relationship survives attribute "
                   "access under the same optimizer --- the regime story weakens")
    else:
        verdict = "UNDECIDED, as pre-registered: neither reading's bar is met"
    print(f"\n{verdict}")

    OUT = research_dir("attribute_aware")
    frame.round(6).to_csv(OUT / "regime_aware.csv", index=False)
    print(f"\nwrote {OUT}/regime_aware.csv")


if __name__ == "__main__":
    main()
