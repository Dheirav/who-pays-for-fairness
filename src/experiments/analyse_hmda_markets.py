"""Six independent mortgage markets, sealed before any of their arms exist.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists.** The examiner's standing objection across
two review rounds: every lending claim rests on one two-state market (MS+LA) measured
three overlapping ways, whose sweep protocol failed its only held-out test (2 of 4,
rescued post-hoc by the accuracy rule). Six further 2018 markets were downloaded and
screened --- AL, SC, TN, GA, NC, OH race arms, every gap 0.148--0.231, every test split
over 34,000 --- and this file seals the two predictions the lending story needs, with
their bars, before a single sweep runs.

**M1 --- "lending is different", quantified.** Every located non-lending crossover sits
at 0.511--0.558 (unweighted convention); the one lending market's three overlapping
estimates sit at 0.66--0.76. Prediction: each new market's located crossover bracket
has its midpoint **at or above 0.60**. Bar: at least ``scored - 1`` of the markets that
locate a crossover, **and** strictly more markets at-or-above 0.60 than inside the
non-lending span [0.43, 0.58] --- the naive alternative ("MS+LA was market selection;
lending crossovers land where the survey ones do") predicts the reverse. Floor: at
least ``M1_FLOOR = 4`` markets locate a crossover at all, else UNDERPOWERED.

**M2 --- the protocol's held-out redemption.** With the frozen exclusions (baseline
parity gap >= 0.05, accuracy >= max(p, 1-p), the 0.10 advisory rule), each market's
retained arms give r >= +0.70 between selection rate and pool change **and** bracket a
crossing. Bar: at least ``scored - 1`` of 6. This is the A1b prediction run on markets
that share no lender pool with MS+LA: the protocol either works off its home market or
the paper keeps saying it is unreliable on mortgage data.

Recorded, not scored: each natural arm's direction against the 0.54 prior. Every
screened approval rate is 0.745--0.792, so the prior calls "up" everywhere and a
constant matches it; the record is kept because a single natural "down" at those rates
would be a violation worth more than the score.

Arms: the established lending grid ``HMDA_POINTS`` (0.45--0.92) plus the natural arm,
five seeds. Sweeps may not begin until this commit is pushed and its hash stamped.

Run:  python -m src.experiments.analyse_hmda_markets      # score stored arms
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

MARKETS = [
    ("hmda:AL:derived_race", "hmda_al_2018_race"),
    ("hmda:SC:derived_race", "hmda_sc_2018_race"),
    ("hmda:TN:derived_race", "hmda_tn_2018_race"),
    ("hmda:GA:derived_race", "hmda_ga_2018_race"),
    ("hmda:NC:derived_race", "hmda_nc_2018_race"),
    ("hmda:OH:derived_race", "hmda_oh_2018_race"),
]
POINTS = [0.92, 0.85, 0.75, 0.65, 0.55, 0.45]
M1_BOUNDARY = 0.60
NON_LENDING_SPAN = (0.43, 0.58)
M1_FLOOR = 4
M2_R_BAR = 0.70
GAP_FLOOR, ADVISORY_RATE = 0.05, 0.10


def main() -> None:
    from .analyse_calibration import majority_baseline
    from .analyse_operating_point import crossover_bracket, load_points_for

    m1_rows, m2_rows, natural_rows = [], [], []
    for spec, stem in MARKETS:
        ops = load_points_for(stem, POINTS)
        natural_path = RESEARCH_RESULTS_DIR / f"{stem}_levelling_up" / "levelling_up_runs.csv"
        if ops.empty and not natural_path.exists():
            print(f"  {stem}: no arms yet")
            continue
        floor = majority_baseline(spec)
        if natural_path.exists():
            runs = pd.read_csv(natural_path)
            base = runs[runs["arm"] == "baseline"]
            mit = runs[runs["arm"] == "expgrad_dp"]
            rate = float(base["positives"].mean()) / float(base["n_test"].mean())
            pie = float(mit["positives_pct_change"].mean())
            natural_rows.append({"market": stem, "rate": round(rate, 3),
                                 "pie": round(pie, 2),
                                 "prior_call_up_correct": pie > 0})
        if ops.empty:
            continue
        ops = ops.copy()
        ops["selection_rate"] = ops["positives_base"] / ops["n_test"]
        kept = ops[(ops["dp_base"] >= GAP_FLOOR) & (ops["acc_base"] >= floor)
                   & (ops["selection_rate"] >= ADVISORY_RATE)]
        kept = kept.sort_values("selection_rate")
        if len(kept) < 3:
            m2_rows.append({"market": stem, "kept": len(kept), "r": None,
                            "bracket": None, "m2": False})
            continue
        r = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
        bracket = crossover_bracket(kept)
        m2_rows.append({"market": stem, "kept": len(kept), "r": round(r, 3),
                        "bracket": (f"{bracket[0]:.3f}-{bracket[1]:.3f}"
                                    if bracket else None),
                        "m2": r >= M2_R_BAR and bracket is not None})
        if bracket is not None:
            mid = (bracket[0] + bracket[1]) / 2
            m1_rows.append({"market": stem, "midpoint": round(mid, 3),
                            "at_or_above_060": mid >= M1_BOUNDARY,
                            "inside_survey_span": NON_LENDING_SPAN[0]
                            <= mid <= NON_LENDING_SPAN[1]})

    print("--- natural arms (recorded; the constant matches the prior here) ---")
    print(pd.DataFrame(natural_rows).to_string(index=False)
          if natural_rows else "none yet")
    print("\n--- M2: protocol off its home market ---")
    m2 = pd.DataFrame(m2_rows)
    print(m2.to_string(index=False) if not m2.empty else "none yet")
    if not m2.empty:
        passed = int(m2["m2"].sum())
        bar = len(m2) - 1
        print(f"M2  {passed}/{len(m2)} markets at r >= {M2_R_BAR} with a bracket "
              f"(bar {bar})  {'HOLDS' if passed >= bar else 'FAILS'}")

    print("\n--- M1: lending is different, quantified ---")
    m1 = pd.DataFrame(m1_rows)
    print(m1.to_string(index=False) if not m1.empty else "none yet")
    if len(m1) < M1_FLOOR:
        print(f"UNDERPOWERED: {len(m1)} located against a floor of {M1_FLOOR} "
              f"-- no M1 verdict is claimed, as pre-registered")
    else:
        above = int(m1["at_or_above_060"].sum())
        inside = int(m1["inside_survey_span"].sum())
        bar = len(m1) - 1
        holds = above >= bar and above > inside
        print(f"M1  {above}/{len(m1)} midpoints >= {M1_BOUNDARY} (bar {bar}); "
              f"{inside} inside the survey span; naive alternative "
              f"{'beaten' if above > inside else 'NOT beaten'}  "
              f"{'HOLDS' if holds else 'FAILS'}")

    OUT = research_dir("hmda_markets")
    for name, frame in (("natural", pd.DataFrame(natural_rows)), ("m2", m2),
                        ("m1", m1)):
        if not frame.empty:
            frame.to_csv(OUT / f"{name}.csv", index=False)
    print(f"\nwrote {OUT}/")


if __name__ == "__main__":
    main()
