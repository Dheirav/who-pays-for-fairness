"""A sealed attribute-independence test: the race arm's curve family, called from the sex arm's.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists.** Six race-protected populations, none ever
swept; thresholds fixed from seed-0 scores of the race-arm feature sets.

What is being tested
--------------------
Documents 50/51 read the response curve's shape as a property of the *label side* --- the
base rate and the reservoir of qualified-but-unselected people --- not of which attribute
the constraint protects. If that mechanism story is right, protecting race instead of sex
on the same state must produce the **same curve family**, because the label, the people and
the base rate are identical; only the groups change. If shapes flip with the attribute, the
label-side story is wrong, and that is worth exactly as much.

The predictions are the states' observed 2018 sex-arm families (document 52), fixed here:

==============================  =====  ==========
population                      p      prediction
==============================  =====  ==========
acs_income_tx_2018_rac1p        0.365  HIGH  (sex arm: U-shaped)
acs_income_va_2018_rac1p        0.437  HIGH  (sex arm: all-positive)
acs_income_oh_2018_rac1p        0.340  LOW   (sex arm: classic crossing)
acs_income_fl_2018_rac1p        0.331  LOW   (sex arm: classic crossing)
acs_income_nj_2018_rac1p        0.490  HIGH  (sex arm: all-positive)
acs_income_il_2018_rac1p        0.394  HIGH  (sex arm: U-shaped)
==============================  =====  ==========

The base rates equal the sex arms' by construction (same label), which is the point.

What counts as success
----------------------
Same rubric as the cross-year seal, and the same family classifier, imported from it:
among scored (non-flat) arms, at least ``scored - 1`` correct **and** strictly beating the
best constant; fewer than ``MIN_SCORED = 4`` scorable arms voids the test as underpowered.
The race gap differs from the sex gap, so per-arm exclusions may bite differently --- that
is the standing rule doing its job, not a design flaw.

Run:  python -m src.experiments.analyse_race_shapes
"""

from __future__ import annotations

import pandas as pd

from ..results_io import research_dir

SPREAD_GUARD = 2.0
MIN_SCORED = 4

SEALED = {
    "acs_income_tx_2018_rac1p": ("acs:TX:RAC1P",
        [0.11, 0.16, 0.225, 0.29, 0.36, 0.43, 0.5, 0.57, 0.645], "HIGH"),
    "acs_income_va_2018_rac1p": ("acs:VA:RAC1P",
        [0.145, 0.23, 0.335, 0.43, 0.53, 0.63, 0.72], "HIGH"),
    "acs_income_oh_2018_rac1p": ("acs:OH:RAC1P",
        [0.135, 0.18, 0.235, 0.29, 0.355, 0.415, 0.485, 0.55], "LOW"),
    "acs_income_fl_2018_rac1p": ("acs:FL:RAC1P",
        [0.165, 0.21, 0.255, 0.305, 0.355, 0.41, 0.47, 0.535], "LOW"),
    "acs_income_nj_2018_rac1p": ("acs:NJ:RAC1P",
        [0.225, 0.345, 0.465, 0.57, 0.67, 0.755], "HIGH"),
    "acs_income_il_2018_rac1p": ("acs:IL:RAC1P",
        [0.135, 0.205, 0.275, 0.35, 0.425, 0.505, 0.58, 0.655], "HIGH"),
}


def main() -> None:
    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import load_points_for
    from .analyse_shapes import family

    rows = []
    for name, (spec, points, call) in SEALED.items():
        ops = load_points_for(name, points)
        if ops.empty:
            print(f"  {name}: no arms yet")
            continue
        kept, _ = apply_rules(ops, majority_baseline(spec))
        pies = kept.sort_values("selection_rate")["pie"].tolist()
        spread = max(pies) - min(pies) if pies else 0.0
        observed = "flat" if spread < SPREAD_GUARD or len(pies) < 4 else family(pies)
        rows.append({"population": name, "predicted": call, "observed": observed,
                     "spread": round(spread, 2), "arms": len(pies),
                     "signs": "".join("+" if x > 0 else "-" for x in pies)})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    print(frame.to_string(index=False))
    scored = frame[frame["observed"] != "flat"]
    correct = int((scored["predicted"] == scored["observed"]).sum())
    constant = max(int((scored["observed"] == "LOW").sum()),
                   int((scored["observed"] == "HIGH").sum()))
    print(f"\nscored {len(scored)} of {len(frame)} (MIN_SCORED {MIN_SCORED})")
    if len(scored) < MIN_SCORED:
        print("UNDERPOWERED — no verdict is claimed, as pre-registered")
    else:
        bar = len(scored) - 1
        holds = correct >= bar and correct > constant
        print(f"S1  {correct}/{len(scored)} correct (bar {bar}, and must beat the "
              f"constant)  {'HOLDS' if holds else 'FAILS'}")
        print(f"    best constant scores {constant}/{len(scored)}  "
              f"{'beaten' if correct > constant else 'NOT beaten'}")

    OUT = research_dir("race_shapes")
    frame.to_csv(OUT / "race_shapes.csv", index=False)
    print(f"\nwrote {OUT}/race_shapes.csv")


if __name__ == "__main__":
    main()
