"""A sealed shape prediction: the response curve's family, called from the base rate alone.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists.** Eight state-year populations, none ever
swept; every threshold below was fixed from seed-0 baseline scores, and every prediction
from the population's label base rate --- both computable before any constraint is fitted.

What is being tested
--------------------
[Document 52](../../research/docs/52-the-campaign-answers-a-different-question.md) found the
within-population response curve comes in families: the original populations are monotone
(down, cross, up) or all-negative, while the large rich states are U-shaped or positive
throughout. A post-hoc screen over the 14 swept populations found one boundary separates
the families cleanly in-sample, 14 of 14: the label base rate ``p`` at **0.365**. The
mechanism reading, via documents 50/51: low ``p`` leaves a qualified reservoir only at high
rates, so lifting wins only there (monotone); as ``p`` approaches one half the reservoir
logic wins across the window and the down-region shrinks away.

Found by a screen, that is document 26's setup, so it earns nothing until sealed. The
cross-year design also separates the boundary from its confounds: the same state appears on
both sides of it eight years apart (Nevada), and 2014 arms appear on both sides of the
prediction (TX/NY predicted LOW-family, VA predicted HIGH-family), so neither "state" nor
"survey year" alone can produce a pass.

The families, fixed here
------------------------
Classified from the retained arms' pool changes, sorted by selection rate:

* **LOW-family** --- all-negative, or exactly one sign change (the classic monotone
  crossing).
* **HIGH-family** --- all-positive, or two or more sign changes (the U and its relatives).

An arm set whose retained pool changes span less than ``SPREAD_GUARD = 2.0`` points is
**flat**: recorded, excluded from the score, and counted toward the underpowered floor.

The populations, with the measured base rate and the sealed call
----------------------------------------------------------------
``p`` measured from the label before any sweep; prediction = LOW below 0.365, HIGH at or
above. The 2018 shapes these imply flips against are in document 52.

====================  ======  ==========
population            p       prediction
====================  ======  ==========
acs_income_tx_2014    0.316   LOW   (2018 was HIGH --- a predicted flip)
acs_income_ny_2014    0.359   LOW   (2018 was HIGH --- a predicted flip)
acs_income_nv_2014    0.286   LOW   (never measured in any year before this week)
acs_income_va_2014    0.388   HIGH  (rich in 2014 too; breaks the year confound)
acs_income_nv_2022    0.413   HIGH  (same state as NV-2014, opposite call)
acs_income_sc_2022    0.376   HIGH  (2018 was LOW --- a predicted flip)
acs_income_al_2022    0.379   HIGH  (2018 was LOW --- a predicted flip)
acs_income_oh_2022    0.416   HIGH  (2018 was LOW --- a predicted flip)
====================  ======  ==========

What counts as success
----------------------
**S1.** Among scored (non-flat) arms, at least ``scored - 1`` predictions correct, **and**
strictly more than the best constant (always-LOW or always-HIGH) scores on the same arms.
Fewer than ``MIN_SCORED = 6`` scorable populations voids the test as underpowered.

**S2, reported not gating:** the within-state flips. TX, NY, SC, AL, OH and the NV pair
each carry a cross-year comparison; how many flipped as called is the result a constant
cannot even express.

Run:  python -m src.experiments.analyse_shapes
"""

from __future__ import annotations

import pandas as pd

from ..results_io import research_dir

SPREAD_GUARD = 2.0
MIN_SCORED = 6
BOUNDARY = 0.365

# name -> (spec, sealed thresholds from seed-0 scores, measured p, sealed call)
SEALED = {
    "acs_income_tx_2014": ("acs:TX:SEX:50000:2014",
        [0.155, 0.2, 0.25, 0.3, 0.355, 0.415, 0.475, 0.54], 0.316, "LOW"),
    "acs_income_ny_2014": ("acs:NY:SEX:50000:2014",
        [0.125, 0.18, 0.235, 0.3, 0.365, 0.43, 0.5, 0.57, 0.64], 0.359, "LOW"),
    "acs_income_nv_2014": ("acs:NV:SEX:50000:2014",
        [0.2, 0.24, 0.275, 0.315, 0.36, 0.41, 0.465], 0.286, "LOW"),
    "acs_income_va_2014": ("acs:VA:SEX:50000:2014",
        [0.12, 0.185, 0.26, 0.335, 0.415, 0.5, 0.59, 0.68], 0.388, "HIGH"),
    "acs_income_nv_2022": ("acs:NV:SEX:50000:2022",
        [0.23, 0.305, 0.38, 0.46, 0.53, 0.595, 0.66], 0.413, "HIGH"),
    "acs_income_sc_2022": ("acs:SC:SEX:50000:2022",
        [0.175, 0.24, 0.305, 0.37, 0.435, 0.495, 0.56, 0.625], 0.376, "HIGH"),
    "acs_income_al_2022": ("acs:AL:SEX:50000:2022",
        [0.17, 0.235, 0.305, 0.375, 0.445, 0.51, 0.575, 0.64], 0.379, "HIGH"),
    "acs_income_oh_2022": ("acs:OH:SEX:50000:2022",
        [0.2, 0.28, 0.365, 0.45, 0.525, 0.6, 0.665], 0.416, "HIGH"),
}

# The 2018 family of the same state, from document 52, for the S2 flip report.
FAMILY_2018 = {"tx": "HIGH", "ny": "HIGH", "va": "HIGH", "sc": "LOW", "al": "LOW",
               "oh": "LOW"}


def family(pies: list[float]) -> str:
    signs = [pie > 0 for pie in pies]
    flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    if all(signs):
        return "HIGH"          # all-positive
    if flips >= 2:
        return "HIGH"          # U and relatives
    return "LOW"               # all-negative, or one clean crossing


def main() -> None:
    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import load_points_for

    rows = []
    for name, (spec, points, p, call) in SEALED.items():
        ops = load_points_for(name, points)
        if ops.empty:
            print(f"  {name}: no arms yet")
            continue
        kept, _ = apply_rules(ops, majority_baseline(spec))
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

    flips = []
    for _, row in frame.iterrows():
        state = row["population"].split("_")[2]
        if state in FAMILY_2018 and row["observed"] != "flat":
            flipped = row["observed"] != FAMILY_2018[state]
            called = row["predicted"] != FAMILY_2018[state]
            flips.append((row["population"], FAMILY_2018[state], row["observed"],
                          "flip" if flipped else "same",
                          "as called" if flipped == called else "AGAINST the call"))
    if flips:
        print("\nS2  cross-year comparisons against the 2018 family:")
        for name, was, now, kind, verdict in flips:
            print(f"    {name}: 2018 {was} -> {now}  ({kind}, {verdict})")

    OUT = research_dir("shapes")
    frame.to_csv(OUT / "shapes.csv", index=False)
    print(f"\nwrote {OUT}/shapes.csv")


if __name__ == "__main__":
    main()
