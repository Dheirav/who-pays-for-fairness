"""A confirmatory test of the attribute-aware regime, on populations never post-processed.

**Individual work, beyond the course submission.**

**Committed before any of the arms it scores exist.**

Why this is worth running at all
--------------------------------
[Document 43](../../research/docs/43-the-rule-is-about-one-regime-and-the-theory-says-which.md)
reports that in the attribute-aware regime the advantaged group loses and the disadvantaged
gains in 18 of 18 populations. That check was **decided after** the pre-registered test around
it had failed, so it is post-hoc, and the paper labels it so.

Post-hoc is not worthless, but it is the weakest form of the strongest claim in that document.
This converts it, on populations that have never been post-processed: the nine added since --
Taiwan 2005 and the eight ACS states used for the sealed prediction.

What is actually being tested
-----------------------------
*Fairness May Backfire* proves that where the protected attribute is available at decision
time, fairness "necessarily (weakly) improves outcomes for the disadvantaged group and (weakly)
worsens outcomes for the advantaged group". That is a **theorem**, not a conjecture, so a
confirmation is not a discovery. What an empirical test can establish is whether its assumptions
bind on real data -- a theorem about a population-level Bayes optimum need not describe what a
particular post-processing implementation does to a particular finite sample.

**T1 -- the prediction.** On every population, under post-processing, the advantaged group
loses favourable decisions and the disadvantaged group gains them. The bar is **all of them**,
because the theorem says "necessarily": a single clean exception is informative and a
majority is not the claim.

**What failure would mean**, and it is not "the theorem is wrong". Most likely it would mean the
implementation is not achieving the optimum the theorem is stated over, or that a finite sample
with a small group can move against it. Either is worth knowing before the paper leans on
document 43's count, which is why the outcome is reported whichever way it falls rather than
folded into the existing 18.

**T2 -- reported, not predicted.** The change in the *total* pool under post-processing is
recorded for each population, but no prediction is attached: the theorem constrains the two
groups' directions, not their sum, and document 43 already found the selection rate predicts
nothing here (r = -0.024).

Run:  python -m src.experiments.analyse_attribute_aware
"""

from __future__ import annotations

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# Populations with no post-processed arm before this test.
FRESH = [
    ("taiwan", "taiwan_2005_sex"),
    ("acs:GA:SEX:10000", "acs_income_ga_2018_t10000"),
    ("acs:NC:SEX:20000", "acs_income_nc_2018_t20000"),
    ("acs:MI:SEX:30000", "acs_income_mi_2018_t30000"),
    ("acs:TN", "acs_income_tn_2018"),
    ("acs:IN:SEX:70000", "acs_income_in_2018_t70000"),
    ("acs:AZ:SEX:100000", "acs_income_az_2018_t100000"),
    ("acs:MO:SEX:100000", "acs_income_mo_2018_t100000"),
    ("acs:MD:SEX:50000", "acs_income_md_2018"),
]


def main() -> None:
    rows = []
    for _spec, name in FRESH:
        path = RESEARCH_RESULTS_DIR / f"{name}_levelling_up_post" / "levelling_up_runs.csv"
        if not path.exists():
            print(f"  {name}: no post-processed arm yet")
            continue
        frame = pd.read_csv(path).groupby("arm").mean(numeric_only=True)
        arm = next((a for a in frame.index if a.startswith("postprocess")), None)
        if arm is None or "priv_lost" not in frame.columns:
            continue
        rows.append({
            "population": name,
            "priv_lost": float(frame.loc[arm, "priv_lost"]),
            "unpriv_gained": float(frame.loc[arm, "unpriv_gained"]),
            "pie": float(frame.loc[arm, "positives_pct_change"]),
        })

    out = pd.DataFrame(rows)
    if out.empty:
        raise SystemExit("no post-processed arms on the fresh populations yet")

    out["as_theory_predicts"] = (out["priv_lost"] > 0) & (out["unpriv_gained"] > 0)
    print(out.round(2).to_string(index=False))

    correct, total = int(out["as_theory_predicts"].sum()), len(out)
    print(f"\nT1  advantaged loses AND disadvantaged gains: {correct}/{total}  "
          f"{'HOLDS' if correct == total else 'FAILS'}  (bar: all of them)")
    if correct != total:
        for _, row in out[~out["as_theory_predicts"]].iterrows():
            print(f"    exception: {row['population']} "
                  f"(priv_lost {row['priv_lost']:.0f}, unpriv_gained {row['unpriv_gained']:.0f})")

    print(f"\nT2  change in the total pool, reported not predicted: "
          f"{out['pie'].min():+.2f}% to {out['pie'].max():+.2f}%")

    path = research_dir("attribute_aware") / "confirmatory.csv"
    out.to_csv(path, index=False)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
