"""Sealed lending cohort: does a crossover located in one market transfer to others?

**Individual work, beyond the course submission.**

**This file is committed, and externally timestamped, before any of its markets are
downloaded.** The rule, the prior, the markets, the purposes, the bar, the magnitude guard
and the nulls are fixed here.

Why this test exists
--------------------
The paper's weakest scope limit is that five of eight data sources are predicted labels
rather than allocations: in most of the record nobody receives anything. HMDA is the one
source recording a real approve-or-deny by a lender, and it is also where the *sweep*
protocol failed twice -- 2 of 4, then 2 of 6 across six markets. What survived those
failures is the **natural-arm** reading, which held 7 of 8.

So the allocation evidence rests on a route that has never been sealed. This seals it.

The design problem, and the purposes that solve it
--------------------------------------------------
State-level lending rates cluster high -- Louisiana 0.794, South Carolina 0.841, Georgia
0.835, North Carolina 0.873 -- all above any located lending crossover, so a cohort of whole
markets would predict UP everywhere and a constant would match it. That is the re-seal's
five-discordant-arm problem in a worse form.

Loan purposes give the spread the states do not: on the pooled Mississippi--Louisiana
market, home improvement sits at 0.555 and levels down while refinancing sits at 0.871 and
levels up. Sealing (market x purpose) pairs therefore puts arms either side of the crossover
by construction, from natural sub-populations, with no sweep and no threshold moved.

The rule
--------
* measured baseline approval rate **below 0.660** -> predict **DOWN**
* **at or above 0.660** -> predict **UP**

0.660 is the pooled Mississippi--Louisiana crossover already located in the paper's crossover
table. It is a *transported* prior, exactly like 0.54 on the survey side, and this cohort is
its first sealed test. None of the markets below contributed to locating it.

Note what this does and does not test. It tests whether a crossover located in one lending
market transfers to others. It does not test the sweep procedure, which the six-market seal
already found unreliable here, and it does not re-test the within-population claim.

The markets, and why these
--------------------------
Eight states this project has never downloaded, let alone measured, crossed with the two
purposes that straddle the crossover. Sixteen arms from eight markets; the arm count is
deliberately twice the market count and is reported as such, since purposes within a state
are sub-populations of one market and not independent populations.

What counts as success
----------------------
**S1.** All three must hold: at least ``MIN_CORRECT`` of the scored arms correct; strictly
beating the best constant; and the paired one-sided sign test giving ``p < 0.05``. A pass on
the count with a weak paired statistic is a failure, and will be reported as one.

**S2.** Two named nulls, reported not predicted: a purpose-only reading (predict DOWN for
improvement and UP for refinance, ignoring the measured rate) and the survey prior 0.54
applied to lending. The purpose-only null is the sharp one -- if it scores as well as the
rule, then the purposes are carrying the prediction and the rate is not, which is the
lending analogue of the label-rarity confound the race cohort broke.

**Magnitude guard**, pre-stated per document 49: an arm whose seed-mean |pool change| is
under ``MIN_MAGNITUDE`` points is \\textsc{indeterminate} and leaves both the numerator and
the denominator.

Run:  python -m src.experiments.analyse_lending_direction
"""

from __future__ import annotations

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from ..skill import score, score_pair

# The pooled Mississippi--Louisiana crossover, located before any market below was touched.
CROSSOVER = 0.660

# The survey-side prior, scored here only to see whether it transports across domains.
SURVEY_PRIOR = 0.54

MIN_CORRECT_FRACTION = 0.8125        # 13 of 16 if no arm is excluded
MAX_PAIRED_P = 0.05
MIN_MAGNITUDE = 1.0

# Eight markets never downloaded here, each at the two purposes that straddle the crossover.
MARKETS = ["NY", "IL", "MA", "MD", "MN", "WI", "IN", "KY"]
PURPOSES = ["improvement", "refinance"]

SEALED = [(f"hmda:{state}:derived_race:{purpose}",
           f"hmda_{state.lower()}_2018_race_{purpose}")
          for state in MARKETS for purpose in PURPOSES]

PURPOSE_OF = {name: name.rsplit("_", 1)[1] for _, name in SEALED}


def predict(rate: float) -> str:
    return "down" if rate < CROSSOVER else "up"


def predict_survey_prior(rate: float) -> str:
    return "down" if rate < SURVEY_PRIOR else "up"


def predict_purpose(name: str) -> str:
    """The purpose-only null: reads the loan product, never the model's rate."""
    return "down" if PURPOSE_OF[name] == "improvement" else "up"


def _assert_names_match_the_loader() -> None:
    from ..datasets import build

    wrong = [(spec, name, build(spec).name) for spec, name in SEALED
             if build(spec).name != name]
    assert not wrong, "sealed names disagree with the loader: " + "; ".join(
        f"{spec} -> {real}, not {name}" for spec, name, real in wrong)


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
    _assert_names_match_the_loader()
    rows = []
    for spec, name in SEALED:
        got = observed(name)
        if got is None:
            print(f"  {name}: no arm yet")
            continue
        rate, pie = got
        rows.append({"spec": spec, "population": name, "rate": rate, "pie": pie,
                     "predicted": predict(rate),
                     "null_purpose": predict_purpose(name),
                     "null_survey": predict_survey_prior(rate),
                     "actual": "up" if pie > 0 else "down",
                     "indeterminate": abs(pie) < MIN_MAGNITUDE})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    print(frame[["population", "rate", "pie", "predicted", "actual", "indeterminate"]]
          .round(4).to_string(index=False))

    guarded, scored = frame[frame["indeterminate"]], frame[~frame["indeterminate"]]
    if len(guarded):
        print(f"\nmagnitude guard excluded {len(guarded)} arm(s) under {MIN_MAGNITUDE} points:")
        for _, row in guarded.iterrows():
            print(f"    {row['population']}: {row['pie']:+.3f}%")
    if scored.empty:
        raise SystemExit("every arm fell under the magnitude guard")

    s = score(scored["predicted"].tolist(), scored["actual"].tolist())
    need = int(MIN_CORRECT_FRACTION * len(scored))
    conditions = {
        f"at least {need} of {len(scored)} correct": s.correct >= need,
        f"beats the best constant ({s.constant_correct})": s.correct > s.constant_correct,
        f"paired sign test p < {MAX_PAIRED_P}": s.sign_p < MAX_PAIRED_P,
    }
    print(f"\nS1  {s.line()}")
    for label, ok in conditions.items():
        print(f"      {'PASS' if ok else 'FAIL'}  {label}")
    print(f"    S1 {'HOLDS' if all(conditions.values()) else 'FAILS'}")

    print("\nS2  named nulls, reported not predicted:")
    for col, label in (("null_purpose", "purpose-only null"), ("null_survey", "0.54 survey prior")):
        pair = score_pair(scored["predicted"] == scored["actual"],
                          scored[col] == scored["actual"], label)
        print(f"      {pair.line()}")

    out = research_dir("lending_direction")
    frame.round(6).to_csv(out / "lending_direction.csv", index=False)
    print(f"\nwrote {out}/lending_direction.csv")


if __name__ == "__main__":
    main()
