"""Third direction cohort: the unrefined rule re-sealed for statistical power.

**Individual work, beyond the course submission.**

**This file is committed, and externally timestamped, before any of the arms it scores
exist.** The rule, the populations, the cutoffs, the bar, the magnitude guard and the three
nulls to beat are all fixed here.

Why this test exists
--------------------
The re-seal (`analyse_resealed`) scored 9 of 10 against a best constant of 6 and passed its
bar. Its *paired* statistic is much weaker: rule and constant disagree on only the five arms
the rule called up, the rule wins four of those five, and the one-sided sign test gives
p ~ 0.19. With a sequential correction for this being the second attempt, the binomial tail
sits near 0.09. The paper says so, and calls the pass "suggestive, not significant".

That weakness is a design property, not a result. Ten arms of which only five are
discordant cannot produce a small paired p however well the rule performs. The fix is a
cohort built for discordance: outcomes spread evenly either side of the crossover so the
best constant is weak, and enough arms that the discordant subset can carry inference.

    discordant arms   rule wins   one-sided p
          5               5          0.031     <- the re-seal's ceiling, even at 5/5
         12              11          0.0032
         12              12          0.0002

Twenty-four populations, balanced, yield about twelve discordant arms. That is the target.

The rule, unchanged
-------------------
* measured baseline selection rate **below 0.54** -> predict **DOWN**
* **at or above 0.54** -> predict **UP**

Identical to the re-seal. No low-rate clause (document 46's refuted refinement), no
per-population characterisation, no sweep. The 0.54 prior predates every population here.

The populations, and why these
------------------------------
Twenty-four ACS state-years this project has never measured, swept, viability-checked or
downloaded: twelve at 2014 and twelve at 2019, all distinct states. Every state-year the
project has touched at those vintages (NV, NY, TX, VA at 2014; NV, OH at 2019) is excluded
by construction. One arm per population, so the arm count is the population count
(document 38's trap).

2022 is excluded deliberately: at nominal labels those vintages invert, and the paper's own
diagnosis is that a fixed dollar cutoff is a different task each year. Using it would test
the label, not the rule.

Cutoffs are assigned from the cutoff-to-rate mapping observed on the 2018 arms, chosen so
the *expected* rates spread evenly across both sides of 0.54 -- twelve up, twelve down --
rather than clustering where a constant could match the rule. The expectations are design
guesses. **The prediction for each arm is the rule applied to its measured baseline rate,
whatever that turns out to be.**

What counts as success
----------------------
**S1 -- the prediction.** All three must hold:

1. at least ``MIN_CORRECT`` of the scored arms correct;
2. strictly beating the best constant on the scored arms;
3. the paired one-sided sign test on the discordant arms giving ``p < 0.05``.

Condition 3 is the one the re-seal lacked and the reason this cohort exists. A pass on 1
and 2 with a paired p above 0.05 is **not** a pass, and will be reported as a failure of S1.

**S2 -- the named nulls.** Scored beside the rule, not as a bar: a cutoff-only reading
(predict from the income cutoff alone, ignoring the measured rate) and a 0.50-prior reading
(the rule with the crossover moved to 0.50). The race cohort found the 0.50 prior edging
0.54 in-band; if that repeats here it is reported, and the fixed value stays fallible.

**The magnitude guard, stated in advance.** Document 49's lesson: a seal predicting signs
must pre-state a minimum magnitude, because a near-zero arm has no sign to predict.
Minnesota was charged a miss for an effect of -0.04% that flips across seeds, while Iowa at
+0.04% scored correct -- two indistinguishable arms, counted opposite ways. Here, an arm
whose seed-mean |pool change| is below ``MIN_MAGNITUDE`` points is scored
\\textsc{indeterminate}: excluded from the numerator and the denominator alike, and
reported with its value. This can only shrink the cohort, never flatter it.

Run:  python -m src.experiments.analyse_third_direction
"""

from __future__ import annotations

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from ..skill import score, score_pair

# The crossover prior, unchanged from the re-seal and fitted to no population below.
CROSSOVER = 0.54

# The alternative prior the race cohort found competitive in-band. Scored, not predicted.
HALF_PRIOR = 0.50

# S1's bar. Twenty-four arms; the guard may reduce the scored set, and the bar is stated
# as a fraction of *scored* arms so that a shrunken cohort is not thereby made easier.
MIN_CORRECT_FRACTION = 0.833          # 20 of 24 if none is excluded
MAX_PAIRED_P = 0.05

# Below this, in percentage points of pool change, an arm has no sign to predict.
MIN_MAGNITUDE = 1.0

# (dataset spec, directory name). One arm per state-year; expected rates spread 0.02-0.90,
# twelve either side of 0.54, assigned from the 2018 cutoff-to-rate mapping.
SEALED = [
    # --- 2014: expected below the crossover ---
    ("acs:AL:SEX:50000:2014", "acs_income_al_2014"),
    ("acs:AZ:SEX:70000:2014", "acs_income_az_2014_t70000"),
    ("acs:CO:SEX:100000:2014", "acs_income_co_2014_t100000"),
    ("acs:FL:SEX:50000:2014", "acs_income_fl_2014"),
    ("acs:GA:SEX:70000:2014", "acs_income_ga_2014_t70000"),
    ("acs:IL:SEX:100000:2014", "acs_income_il_2014_t100000"),
    # --- 2014: expected at or above the crossover ---
    ("acs:IN:SEX:30000:2014", "acs_income_in_2014_t30000"),
    ("acs:KY:SEX:20000:2014", "acs_income_ky_2014_t20000"),
    ("acs:MA:SEX:30000:2014", "acs_income_ma_2014_t30000"),
    ("acs:MI:SEX:20000:2014", "acs_income_mi_2014_t20000"),
    ("acs:MN:SEX:10000:2014", "acs_income_mn_2014_t10000"),
    ("acs:MO:SEX:30000:2014", "acs_income_mo_2014_t30000"),
    # --- 2019: expected below the crossover ---
    ("acs:NC:SEX:50000:2019", "acs_income_nc_2019"),
    ("acs:NJ:SEX:70000:2019", "acs_income_nj_2019_t70000"),
    ("acs:NM:SEX:50000:2019", "acs_income_nm_2019"),
    ("acs:OK:SEX:100000:2019", "acs_income_ok_2019_t100000"),
    ("acs:OR:SEX:70000:2019", "acs_income_or_2019_t70000"),
    ("acs:PA:SEX:50000:2019", "acs_income_pa_2019"),
    # --- 2019: expected at or above the crossover ---
    ("acs:SC:SEX:30000:2019", "acs_income_sc_2019_t30000"),
    ("acs:TN:SEX:20000:2019", "acs_income_tn_2019_t20000"),
    ("acs:UT:SEX:30000:2019", "acs_income_ut_2019_t30000"),
    ("acs:WA:SEX:10000:2019", "acs_income_wa_2019_t10000"),
    ("acs:WI:SEX:20000:2019", "acs_income_wi_2019_t20000"),
    ("acs:WV:SEX:30000:2019", "acs_income_wv_2019_t30000"),
]

# The cutoff each population is labelled at, for the cutoff-only null. Read off SEALED so
# the two can never drift apart.
CUTOFF = {name: int(spec.split(":")[3]) for spec, name in SEALED}

# The cutoff-only null: predict from the label alone, ignoring the measured rate. A cutoff
# at or above this threshold predicts DOWN. Fixed here, before any arm exists.
CUTOFF_SPLIT = 50000


def _assert_names_match_the_loader() -> None:
    """Every directory name here must be the one the loader will actually write to.

    Five of these names were wrong on first writing: a $50,000 cutoff is the loader's
    default and is omitted from the name, so ``acs:AL:SEX:50000:2014`` produces
    ``acs_income_al_2014`` and not ``..._t50000``. The seal would have reported those five
    arms as never run. A seal whose population list does not resolve is worse than no seal,
    so this is checked rather than trusted.
    """
    from ..datasets import build

    wrong = [(spec, name, build(spec).name) for spec, name in SEALED
             if build(spec).name != name]
    assert not wrong, "sealed names disagree with the loader: " + "; ".join(
        f"{spec} -> {real}, not {name}" for spec, name, real in wrong)


def predict(rate: float) -> str:
    """The rule. Two words long, sealed with no further clauses."""
    return "down" if rate < CROSSOVER else "up"


def predict_half(rate: float) -> str:
    return "down" if rate < HALF_PRIOR else "up"


def predict_cutoff(name: str) -> str:
    """The cutoff-only null: reads the label, never the model."""
    return "down" if CUTOFF[name] >= CUTOFF_SPLIT else "up"


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
                     "null_half": predict_half(rate),
                     "null_cutoff": predict_cutoff(name),
                     "actual": "up" if pie > 0 else "down",
                     "indeterminate": abs(pie) < MIN_MAGNITUDE})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    print(frame[["population", "rate", "pie", "predicted", "actual", "indeterminate"]]
          .round(4).to_string(index=False))

    guarded = frame[frame["indeterminate"]]
    scored = frame[~frame["indeterminate"]]
    if len(guarded):
        print(f"\nmagnitude guard excluded {len(guarded)} arm(s) under "
              f"{MIN_MAGNITUDE} points, as sealed:")
        for _, row in guarded.iterrows():
            print(f"    {row['population']}: {row['pie']:+.3f}%")
    if scored.empty:
        raise SystemExit("every arm fell under the magnitude guard")

    s = score(scored["predicted"].tolist(), scored["actual"].tolist())
    need = -(-int(MIN_CORRECT_FRACTION * len(scored)) // 1)
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
    for col, label in (("null_cutoff", "cutoff-only null"), ("null_half", "0.50-prior null")):
        pair = score_pair(scored["predicted"] == scored["actual"],
                          scored[col] == scored["actual"], label)
        print(f"      {pair.line()}")

    out = research_dir("third_direction")
    frame.round(6).to_csv(out / "third_direction.csv", index=False)
    print(f"\nwrote {out}/third_direction.csv")


if __name__ == "__main__":
    main()
