"""A sealed cross-task shape prediction: the family called from the base rate, on two new tasks.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists.** Six populations from two folktables
tasks this project has never run --- ACSEmployment and ACSPublicCoverage, race arms ---
every threshold below fixed from seed-0 baseline scores, every prediction from the
population's label base rate, both computable before any constraint is fitted.

What is being tested
--------------------
Documents 52--57 established the curve-family boundary only across states and vintages
of one task (income). Document 54 sealed it cross-year and it failed on nominal-label
grounds later resolved by document 57; document 55 showed the family is not
attribute-independent. This test changes the **question asked of the same instrument**:
employment status and public-coverage receipt, with the attribute held fixed (race,
White vs Non-White, the higher-rate side declared per task from measurement --- on
coverage it is Non-White, an inversion that defeats any rule secretly tracking "the
same group always loses").

The sex arms of coverage were screened out honestly first: all three fail the frozen
0.05 gap floor (gaps 0.028--0.047, measured 24 Aug), so by the frozen exclusions that
family is a refusal, recorded in NEXT.md's corrected screen note.

The populations, with the measured base rate and the sealed call
----------------------------------------------------------------
``p`` measured from the label before any sweep; prediction = LOW below 0.365, HIGH at
or above (the boundary sealed in ``analyse_shapes``). The design places calls on both
sides, so no constant can match a clean pass: the best constant (HIGH) scores 4 of 6.

============================  ======  ==========
population                    p       prediction
============================  ======  ==========
acs_employment_al_2018_rac1p  0.410   HIGH
acs_employment_oh_2018_rac1p  0.461   HIGH
acs_employment_pa_2018_rac1p  0.467   HIGH
acs_coverage_oh_2018_rac1p    0.333   LOW
acs_coverage_pa_2018_rac1p    0.306   LOW
acs_coverage_ny_2018_rac1p    0.401   HIGH
============================  ======  ==========

What counts as success
----------------------
Identical to document 54's rubric, unchanged: among scored (non-flat) sweeps, at least
``scored - 1`` correct **and** strictly more than the best constant on the same
sweeps; fewer than ``MIN_SCORED = 4`` scorable populations voids the test as
underpowered. Families are classified exactly as ``analyse_shapes.family`` over
retained arms (frozen exclusions; arms below rate 0.10 advisory --- none of the sealed
thresholds targets below 0.15), with the 2.0-point flat guard. The natural arms are run
and recorded but the family is read from the operating-point sweep, as in every prior
shape test.

Run:  python -m src.experiments.analyse_task_shapes
"""

from __future__ import annotations

import pandas as pd

from ..results_io import research_dir

SPREAD_GUARD = 2.0
MIN_SCORED = 4
BOUNDARY = 0.365

# name -> (spec, sealed thresholds from seed-0 scores, measured p, sealed call)
SEALED = {
    "acs_employment_al_2018_rac1p": ("acsemp:AL:RAC1P",
        [0.8041, 0.7226, 0.6267, 0.5163, 0.3897, 0.2627], 0.410, "HIGH"),
    "acs_employment_oh_2018_rac1p": ("acsemp:OH:RAC1P",
        [0.8594, 0.7923, 0.7157, 0.6159, 0.4941, 0.357], 0.461, "HIGH"),
    "acs_employment_pa_2018_rac1p": ("acsemp:PA:RAC1P",
        [0.8536, 0.7894, 0.7111, 0.6118, 0.4932, 0.3677], 0.467, "HIGH"),
    "acs_coverage_oh_2018_rac1p": ("acscov:OH:RAC1P",
        [0.6418, 0.4767, 0.3727, 0.304, 0.2489, 0.2053], 0.333, "LOW"),
    "acs_coverage_pa_2018_rac1p": ("acscov:PA:RAC1P",
        [0.6005, 0.4362, 0.3226, 0.2625, 0.2179, 0.1826], 0.306, "LOW"),
    "acs_coverage_ny_2018_rac1p": ("acscov:NY:RAC1P",
        [0.6565, 0.5205, 0.442, 0.3899, 0.3464, 0.305], 0.401, "HIGH"),
}


def main() -> None:
    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import load_points_for
    from .analyse_shapes import family

    rows = []
    for name, (spec, points, p, call) in SEALED.items():
        ops = load_points_for(name, points)
        if ops.empty:
            print(f"  {name}: no arms yet")
            continue
        kept, _ = apply_rules(ops, majority_baseline(spec))
        kept = kept[kept["selection_rate"] >= 0.10]
        pies = kept.sort_values("selection_rate")["pie"].tolist()
        spread = max(pies) - min(pies) if pies else 0.0
        observed = "flat" if spread < SPREAD_GUARD or len(pies) < 4 else family(pies)
        rows.append({"population": name, "p": p, "predicted": call,
                     "observed": observed, "spread": round(spread, 2),
                     "arms": len(pies),
                     "signs": "".join("+" if x > 0 else "-" for x in pies)})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    print(frame.to_string(index=False))
    scored = frame[frame["observed"] != "flat"]
    correct = int((scored["predicted"] == scored["observed"]).sum())
    constant = max(int((scored["observed"] == "LOW").sum()),
                   int((scored["observed"] == "HIGH").sum()))
    print(f"\nscored {len(scored)} of {len(frame)} (flat excluded; MIN_SCORED "
          f"{MIN_SCORED})")
    if len(scored) < MIN_SCORED:
        print("UNDERPOWERED — no verdict is claimed, as pre-registered")
    else:
        bar = len(scored) - 1
        holds = correct >= bar and correct > constant
        print(f"S1  {correct}/{len(scored)} correct (bar {bar}, and must beat the "
              f"constant)  {'HOLDS' if holds else 'FAILS'}")
        print(f"    best constant scores {constant}/{len(scored)}  "
              f"{'beaten' if correct > constant else 'NOT beaten'}")

    OUT = research_dir("task_shapes")
    frame.to_csv(OUT / "task_shapes.csv", index=False)
    print(f"\nwrote {OUT}/task_shapes.csv")


if __name__ == "__main__":
    main()
