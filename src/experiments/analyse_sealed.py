"""A sealed prediction: which way, on populations never measured, decided before running.

**Individual work, beyond the course submission.**

**This file is committed before any of the arms it scores exist.** Everything it needs is
fixed here: which populations, what the rule predicts for each, what would count as a failure,
and the constant it has to beat.

Why this test and not another
-----------------------------
Every result in this project so far is a correlation computed after the arms were run. That is
the weakest evidence format for a claim of the form *"you can know in advance"*, and it is the
one thing external review identified as missing --- correctly, because the project's own
held-out test (four HMDA populations, document 40) was scored a failure at two of four.

This is the format that answers it. **Take populations whose direction has never been
measured, predict the sign from the selection rate alone, commit the predictions, then run.**

The rule being tested, in full
------------------------------
As of [document 46](../../research/docs/46-the-relationship-turns-back-up-at-the-bottom.md)
the relationship is bounded on both sides, which makes the prediction **non-monotone** and
therefore not reproducible by any constant:

* selection rate **below 0.10** -- the constraint has little to withdraw because the
  disadvantaged group's rate is already near zero, so predict **UP**;
* between **0.10 and the crossover** -- predict **DOWN**;
* **above the crossover** -- predict **UP**.

The crossover is taken as **0.54**, the mid-point of the non-lending cluster in
[document 44](../../research/docs/44-how-much-and-where-two-concessions-tested.md), used here
as a prior exactly as document 35 instructs a practitioner to use it. No population below is
used to fit it.

The populations, and why these
------------------------------
Eight arms, none of which has ever had its direction measured. Six are ACS states this project
has never touched, at income cutoffs chosen to spread the selection rate across the whole
range rather than to sit conveniently. The seventh and eighth are Taiwan credit-card default
2005 --- the first non-Western population here --- and one further ACS arm at the bottom of the
range.

Taiwan cannot be swept: its viable band spans 0.194 against the 0.40 required, so no crossover
can be located on it. Its *natural* operating point can still be predicted, which is what a
practitioner would have to do there anyway.

What counts as success, and the constant to beat
------------------------------------------------
**S1 -- the prediction.** At least ``MIN_CORRECT`` of the 8 signs are correct.

**The naive alternative, and it is strong.** Because more arms fall on the *up* side than the
*down* side, a constant answering "up" every time scores **5 of 8** without knowing anything.
The rule must beat that, so ``MIN_CORRECT`` is set at **7**, and 6 of 8 is a *failure* despite
being better than chance. This is document 26's lesson applied: a threshold without a baseline
can be cleared by a derivation a constant outperforms.

**S2 -- the non-monotone half.** The two arms predicted UP because they sit *below* 0.10 are
the ones no constant and no monotone rule can get right while also getting the middle band
right. If S1 passes but both of these are wrong, the rule is working only as "high rate means
up" and that is what will be reported.

**S3 -- Taiwan.** Reported separately, because it is the only non-Western population and one
arm cannot carry a claim. Its outcome does not enter S1's count.

Run:  python -m src.experiments.analyse_sealed
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# The crossover prior, from the non-lending cluster. Not fitted to anything below.
CROSSOVER = 0.54

# Below this the constraint has little to withdraw; document 46.
LOW_REGIME = 0.10

# S1's bar. A constant answering "up" scores 5 of 8, so 6 is not enough.
MIN_CORRECT = 7

# (dataset spec, directory name). Chosen to spread the selection rate, not to be convenient.
SEALED = [
    ("acs:GA:SEX:10000", "acs_income_ga_2018_t10000"),
    ("acs:NC:SEX:20000", "acs_income_nc_2018_t20000"),
    ("acs:MI:SEX:30000", "acs_income_mi_2018_t30000"),
    ("acs:TN", "acs_income_tn_2018"),
    ("acs:IN:SEX:70000", "acs_income_in_2018_t70000"),
    ("acs:AZ:SEX:100000", "acs_income_az_2018_t100000"),
    ("acs:MO:SEX:100000", "acs_income_mo_2018_t100000"),
    ("acs:MD:SEX:50000", "acs_income_md_2018"),
]

TAIWAN = ("taiwan", "taiwan_2005_sex")


def predict(rate: float) -> str:
    """The rule, applied to a selection rate. Non-monotone by design."""
    if rate < LOW_REGIME:
        return "up"
    if rate < CROSSOVER:
        return "down"
    return "up"


def observed(name: str) -> tuple[float, float] | None:
    path = RESEARCH_RESULTS_DIR / f"{name}_levelling_up" / "levelling_up_runs.csv"
    if not path.exists():
        return None
    runs = pd.read_csv(path)
    base = runs[runs["arm"] == "baseline"]
    plain = runs[runs["arm"] == "expgrad_dp"]
    if base.empty or plain.empty:
        return None
    return (float(base["positives"].mean() / base["n_test"].mean()),
            float(plain["positives_pct_change"].mean()))


def main() -> None:
    rows = []
    for spec, name in SEALED + [TAIWAN]:
        got = observed(name)
        if got is None:
            print(f"  {name}: no arm yet")
            continue
        rate, pie = got
        rows.append({"spec": spec, "population": name, "rate": rate, "pie": pie,
                     "predicted": predict(rate),
                     "actual": "up" if pie > 0 else "down",
                     "held_out": name != TAIWAN[1]})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    frame["correct"] = frame["predicted"] == frame["actual"]
    print(frame[["population", "rate", "pie", "predicted", "actual", "correct"]]
          .round(4).to_string(index=False))

    scored = frame[frame["held_out"]]
    correct = int(scored["correct"].sum())
    constant = max(int((scored["actual"] == "up").sum()),
                   int((scored["actual"] == "down").sum()))
    print(f"\nS1  {correct}/{len(scored)} correct (bar {MIN_CORRECT})  "
          f"{'HOLDS' if correct >= MIN_CORRECT else 'FAILS'}")
    print(f"    best constant scores {constant}/{len(scored)}  "
          f"{'beaten' if correct > constant else 'NOT beaten'}")

    low = scored[scored["rate"] < LOW_REGIME]
    if len(low):
        print(f"\nS2  arms below {LOW_REGIME}, which no monotone rule can also get right: "
              f"{int(low['correct'].sum())}/{len(low)} correct")

    taiwan = frame[~frame["held_out"]]
    if len(taiwan):
        row = taiwan.iloc[0]
        print(f"\nS3  Taiwan (non-Western, reported separately): rate {row['rate']:.3f}, "
              f"predicted {row['predicted']}, observed {row['actual']} "
              f"({row['pie']:+.2f}%)")

    OUT = research_dir("sealed")
    frame.round(6).to_csv(OUT / "sealed.csv", index=False)
    print(f"\nwrote {OUT}/sealed.csv")


if __name__ == "__main__":
    main()
