"""Re-sealing the simple monotone rule: down below 0.54, up above, on ten fresh states.

**Individual work, beyond the course submission.**

**This file is committed before any of the arms it scores exist.** The rule, the populations,
the bar and the constant to beat are all fixed here.

Why this test exists
--------------------
[Document 47](../../research/docs/47-the-sealed-prediction-failed-and-took-document-46-with-it.md)
sealed a *refined* rule and it failed at 4 of 8, no better than a constant. Scoring the same
eight arms under the rule this project held **before** the refinement — *down below the
crossover, up above it* — gave 7 of 8. That 7/8 is post-hoc: the rule was chosen after the
outcomes were known, from a menu of two. It is currently the weakest evidence format attached
to the project's central claim.

This test converts it. The monotone rule is sealed **as is** — no low-rate clause, no
refinement of any kind, which is document 46's lesson applied: every clause a rule carries
must have been sealed *before* the data that tests it. Below a selection rate of 0.10 this
rule says **down**, exactly where document 46's clause said up and lost by three arms.

The rule, in full
-----------------
* selection rate **below 0.54** — predict **DOWN**;
* **at or above 0.54** — predict **UP**.

The crossover is the same prior as the last seal: 0.54, the mid-point of the non-lending
cluster in [document 44](../../research/docs/44-how-much-and-where-two-concessions-tested.md),
used as document 35 instructs a practitioner to use it. No population below is used to fit it.

The populations, and why these
------------------------------
Ten arms from **ten distinct ACS states**, none of which has ever been measured, swept,
viability-checked or downloaded by this project — so the arm count *is* the population count,
by construction (document 38's trap). One arm per state.

Income cutoffs are assigned from the cutoff-to-rate mapping observed on document 47's arms,
chosen so the *expected* rates spread across both sides of 0.54 — five up, five down — rather
than clustering where a constant could match the rule. The expectations are design guesses,
not predictions: the prediction for each arm is the rule applied to the **measured** baseline
selection rate, whatever it turns out to be.

All ten states clear document 15's noise floor: the smallest (NE, ~10.8k rows) leaves ~3.2k
test subjects against the 2,500 minimum.

What counts as success, and the constant to beat
------------------------------------------------
**S1 — the prediction.** At least ``MIN_CORRECT = 9`` of the 10 signs are correct, **and**
the count strictly beats the best constant. By design a constant scores ~5 of 10 if the rule
is right; the constant actually scored is computed from the outcomes, whatever they are.
Document 47's post-hoc showing was 7 of 8; sealing a bar of 9 of 10 claims that rate was not
luck. 8 of 10 is a *failure* even if it beats the constant, and will be reported as one.

**S2 — where the misses fall.** Reported, not predicted: a rule with a threshold should be
wrong only at the threshold. Every miss is reported with its distance from 0.54; a miss
further than 0.05 from the crossover is evidence against the rule itself rather than against
the placement of its boundary.

Run:  python -m src.experiments.analyse_resealed
"""

from __future__ import annotations

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# The crossover prior, unchanged from the last seal. Not fitted to anything below.
CROSSOVER = 0.54

# S1's bar, and it is strict: 8 of 10 fails even though it beats a constant.
MIN_CORRECT = 9

# A miss further than this from the crossover indicts the rule, not the boundary. S2 only.
BOUNDARY = 0.05

# (dataset spec, directory name). One arm per state; expected rates spread 0.03-0.90.
SEALED = [
    ("acs:IA:SEX:10000", "acs_income_ia_2018_t10000"),
    ("acs:WI:SEX:20000", "acs_income_wi_2018_t20000"),
    ("acs:KS:SEX:20000", "acs_income_ks_2018_t20000"),
    ("acs:CO:SEX:30000", "acs_income_co_2018_t30000"),
    ("acs:MN:SEX:30000", "acs_income_mn_2018_t30000"),
    ("acs:NV", "acs_income_nv_2018"),
    ("acs:OK", "acs_income_ok_2018"),
    ("acs:AR", "acs_income_ar_2018"),
    ("acs:WA:SEX:70000", "acs_income_wa_2018_t70000"),
    ("acs:NE:SEX:100000", "acs_income_ne_2018_t100000"),
]


def predict(rate: float) -> str:
    """The rule. Monotone, two words long, and sealed with no further clauses."""
    return "down" if rate < CROSSOVER else "up"


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
    for spec, name in SEALED:
        got = observed(name)
        if got is None:
            print(f"  {name}: no arm yet")
            continue
        rate, pie = got
        rows.append({"spec": spec, "population": name, "rate": rate, "pie": pie,
                     "predicted": predict(rate),
                     "actual": "up" if pie > 0 else "down"})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    frame["correct"] = frame["predicted"] == frame["actual"]
    print(frame[["population", "rate", "pie", "predicted", "actual", "correct"]]
          .round(4).to_string(index=False))

    correct = int(frame["correct"].sum())
    constant = max(int((frame["actual"] == "up").sum()),
                   int((frame["actual"] == "down").sum()))
    bar = correct >= MIN_CORRECT and correct > constant
    print(f"\nS1  {correct}/{len(frame)} correct (bar {MIN_CORRECT}, and must beat the "
          f"constant)  {'HOLDS' if bar else 'FAILS'}")
    print(f"    best constant scores {constant}/{len(frame)}  "
          f"{'beaten' if correct > constant else 'NOT beaten'}")

    misses = frame[~frame["correct"]]
    if len(misses):
        print(f"\nS2  misses, by distance from the crossover (boundary calls are within "
              f"{BOUNDARY}):")
        for _, row in misses.iterrows():
            distance = abs(row["rate"] - CROSSOVER)
            kind = "boundary call" if distance <= BOUNDARY else "AGAINST THE RULE"
            print(f"    {row['population']}: rate {row['rate']:.3f}, "
                  f"|rate - {CROSSOVER}| = {distance:.3f}  ({kind})")
    else:
        print("\nS2  no misses")

    OUT = research_dir("resealed")
    frame.round(6).to_csv(OUT / "resealed.csv", index=False)
    print(f"\nwrote {OUT}/resealed.csv")


if __name__ == "__main__":
    main()
