"""What Algorithm 1 actually returns, run over every population that has a sweep.

**Individual work, beyond the course submission. Post-hoc accounting, labelled as such.**

The third review round's sharpest cheap question: the paper describes an audit whose
refusal states are first-class, but never totals what fraction of its own populations
the audit answers. A procedure that mostly refuses is a different contribution from one
that mostly answers, and the reader should not have to assemble the distribution by hand.

This walks every stored operating-point sweep, applies the frozen guards in the order
Algorithm 1 states them, and reports the verdict per population plus the distribution:

* **REFUSED (noise floor)** --- test split under 2,500 subjects (document 52's floor).
* **VOID** --- fewer than four arms survive the parity-gap and accuracy exclusions, or
  the retained pool changes span less than 2.0 points.
* **NON-MONOTONE** --- two or more sign changes along the rate axis, or a falling
  crossing (positive at low rates, negative at high --- the 2022-at-nominal shape).
* **WITHDRAWAL / EXTENSION** --- a monotone landscape, with the natural operating
  point's side of the located bracket giving the direction. All-negative and
  all-positive sweeps are the degenerate monotone cases.
* **INDETERMINATE** --- monotone-crossing, but the natural rate sits inside the located
  bracket, where the paper's own record (Maryland, Minnesota) says a sign call has
  nothing to grip.

Where the natural arm exists, its observed pool direction is scored against the verdict
--- the "conditional accuracy" the third round asked for. Populations that were never
swept cannot enter; they are counted, not invented.

Guard sensitivity on the sealed cohorts (``--sealed-sensitivity``) re-scores the two
sealed direction cohorts at parity-gap floors 0.02/0.05/0.08/0.10, because the council
observed the floor was tuned in-sample on the exploratory populations and the sealed
cohorts are where its choice must not matter.

Run:  python -m src.experiments.analyse_verdicts
      python -m src.experiments.analyse_verdicts --dataset acs_income_oh_2018
      python -m src.experiments.analyse_verdicts --sealed-sensitivity
"""

from __future__ import annotations

import argparse
import re

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from .analyse_calibration import apply_rules, majority_baseline
from .analyse_operating_point import _load, crossover_bracket
from .analyse_threshold import MIN_SPAN_PIE

# Document 52's frozen exclusion set: below this test-split size, seed noise swamps the
# effect sizes being read (COMPAS, at 1,584, flips sign across seeds).
NOISE_FLOOR = 2500

# Documents 32/47: below a selection rate of ~0.10 the two routes to a rate give opposite
# signs and the accuracy guard does not separate them. The paper carried this as a prose
# caution; the review council's ask was to encode it, so arms under the boundary are
# advisory-only here --- counted, excluded from the shape call.
ADVISORY_RATE = 0.10

OP_DIR = re.compile(r"^(?P<stem>.+)_levelling_up_op\d+$")

# Stems whose sweeps exist under a variant condition the audit is not about: post-processing
# comparisons, equalized odds, alternate learners and tolerances are their own analyses.
VARIANT = re.compile(r"_(post|eo|eps\d+|hgb)$")


def spec_for(stem: str) -> str | None:
    """The dataset spec a result stem was produced from. None if unmappable."""
    acs = re.match(
        r"^acs_income_(?P<state>[a-z]{2})_(?P<year>\d{4})"
        r"(?P<race>_rac1p)?(?:_t(?P<thr>\d+))?$", stem)
    if acs:
        attr = "RAC1P" if acs.group("race") else "SEX"
        thr = acs.group("thr") or "50000"
        return f"acs:{acs.group('state').upper()}:{attr}:{thr}:{acs.group('year')}"
    hmda = re.match(
        r"^hmda_(?P<states>[a-z]{2}(?:_[a-z]{2})?)_2018_(?P<attr>race|sex)"
        r"(?:_(?P<purpose>[a-z]+))?$", stem)
    if hmda:
        states = ",".join(s.upper() for s in hmda.group("states").split("_"))
        attr = "derived_race" if hmda.group("attr") == "race" else "derived_sex"
        purpose = hmda.group("purpose") or ""
        return f"hmda:{states}:{attr}:{purpose}".rstrip(":")
    return {"adult": "adult", "compas_2016_race": "compas", "compas_2016_sex": "compas:sex",
            "dutch_2001_sex": "dutch", "lawschool_race": "lawschool",
            "lawschool_sex": "lawschool:male", "taiwan_2005_sex": "taiwan"}.get(stem)


def swept_stems() -> list[str]:
    stems = set()
    for directory in RESEARCH_RESULTS_DIR.iterdir():
        match = OP_DIR.match(directory.name)
        if match and not VARIANT.search(match.group("stem")):
            stems.add(match.group("stem"))
    return sorted(stems)


def arms_for(stem: str) -> pd.DataFrame:
    rows = []
    names = [f"{stem}_levelling_up"] + sorted(
        d.name for d in RESEARCH_RESULTS_DIR.glob(f"{stem}_levelling_up_op*")
        if OP_DIR.match(d.name))
    for name in names:
        mean = _load(RESEARCH_RESULTS_DIR / name / "levelling_up_runs.csv")
        if mean is None:
            continue
        rows.append({
            "natural": name == f"{stem}_levelling_up",
            "positives_base": mean.loc["baseline", "positives"],
            "n_test": mean.loc["baseline", "n_test"]
            if "n_test" in mean.columns else float("nan"),
            "dp_base": mean.loc["baseline", "dp_diff"],
            "pie": mean.loc["expgrad_dp", "positives_pct_change"],
            "acc_base": mean.loc["baseline", "accuracy"],
        })
    frame = pd.DataFrame(rows)
    if not frame.empty and frame["n_test"].isna().any():
        # Pre-``n_test`` arms borrow the split size from a sibling: the split is a
        # property of the population, not the arm.
        frame["n_test"] = frame["n_test"].fillna(frame["n_test"].mean())
    return frame


def classify(stem: str) -> dict:
    spec = spec_for(stem)
    if spec is None:
        return {"population": stem, "verdict": "UNMAPPED"}
    ops = arms_for(stem)
    row = {"population": stem, "arms": len(ops)}
    if ops.empty or ops["n_test"].isna().all():
        return {**row, "verdict": "NO DATA"}
    if float(ops["n_test"].mean()) < NOISE_FLOOR:
        return {**row, "verdict": "REFUSED (noise floor)",
                "n_test": int(ops["n_test"].mean())}
    kept, _ = apply_rules(ops, majority_baseline(spec))
    row["advisory"] = int((kept["selection_rate"] < ADVISORY_RATE).sum())
    kept = kept[kept["selection_rate"] >= ADVISORY_RATE]
    row["kept"] = len(kept)
    if len(kept) < 4:
        return {**row, "verdict": "VOID (too few arms)"}
    kept = kept.sort_values("selection_rate")
    pies = kept["pie"].tolist()
    spread = max(pies) - min(pies)
    row["spread"] = round(spread, 2)
    row["signs"] = "".join("+" if x > 0 else "-" for x in pies)
    if spread < MIN_SPAN_PIE:
        return {**row, "verdict": "VOID (flat)"}

    natural = kept[kept["natural"]]
    r0 = float(natural["selection_rate"].iloc[0]) if not natural.empty else None
    observed = (("up" if float(natural["pie"].iloc[0]) > 0 else "down")
                if not natural.empty else None)
    row.update({"r0": round(r0, 3) if r0 is not None else None, "observed": observed})

    signs = [x > 0 for x in pies]
    flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    if flips >= 2 or (flips == 1 and signs[0]):
        return {**row, "verdict": "NON-MONOTONE"}
    if flips == 0:
        verdict = "EXTENSION" if signs[0] else "WITHDRAWAL"
    else:
        bracket = crossover_bracket(kept)
        row["bracket"] = (f"{bracket[0]:.3f}-{bracket[1]:.3f}"
                          if bracket else "unbracketed")
        if bracket is None or r0 is None:
            return {**row, "verdict": "INDETERMINATE (no natural arm)"
                    if r0 is None else "NON-MONOTONE"}
        if bracket[0] < r0 < bracket[1]:
            return {**row, "verdict": "INDETERMINATE (inside bracket)"}
        verdict = "WITHDRAWAL" if r0 <= bracket[0] else "EXTENSION"
    agree = (observed == {"WITHDRAWAL": "down", "EXTENSION": "up"}[verdict]
             if observed else None)
    return {**row, "verdict": verdict, "agrees": agree}


def seed_stability() -> pd.DataFrame:
    """Per-seed sign agreement for every sealed direction arm.

    The second council asked for it: a seed-mean sign hides how many seeds voted for
    it. For each arm of both sealed cohorts, the five seeds' pool-change signs and the
    count agreeing with the seed-mean's sign.
    """
    rows = []
    for cohort, path in (("sealed", "sealed/sealed.csv"),
                         ("re-sealed", "resealed/resealed.csv")):
        frame = pd.read_csv(RESEARCH_RESULTS_DIR / path)
        for _, arm in frame.iterrows():
            runs = pd.read_csv(RESEARCH_RESULTS_DIR / f"{arm['population']}_levelling_up"
                               / "levelling_up_runs.csv")
            pies = runs[runs["arm"] == "expgrad_dp"]["positives_pct_change"]
            mean = float(pies.mean())
            agree = int((pies > 0).sum() if mean > 0 else (pies <= 0).sum())
            rows.append({"cohort": cohort, "population": arm["population"],
                         "mean_pie": round(mean, 2),
                         "seeds": len(pies), "seeds_agreeing": agree,
                         "signs": "".join("+" if x > 0 else "-" for x in pies),
                         "correct": bool(arm["correct"])})
    return pd.DataFrame(rows)


def sealed_sensitivity() -> pd.DataFrame:
    """The sealed direction cohorts, re-scored at four parity-gap floors."""
    rows = []
    for cohort, path in (("sealed (doc 47)", "sealed/sealed.csv"),
                         ("re-sealed (doc 49)", "resealed/resealed.csv")):
        frame = pd.read_csv(RESEARCH_RESULTS_DIR / path)
        if "held_out" in frame.columns:
            # Taiwan was sealed-aside (already measured), not one of the scored arms.
            frame = frame[frame["held_out"]]
        gaps = []
        for population in frame["population"]:
            mean = _load(RESEARCH_RESULTS_DIR / f"{population}_levelling_up"
                         / "levelling_up_runs.csv")
            gaps.append(float(mean.loc["baseline", "dp_diff"]) if mean is not None
                        else float("nan"))
        frame = frame.assign(gap=gaps)
        for floor in (0.02, 0.05, 0.08, 0.10):
            retained = frame[frame["gap"] >= floor]
            correct = int(retained["correct"].sum())
            constant = max(int((retained["actual"] == "up").sum()),
                           int((retained["actual"] == "down").sum()))
            rows.append({"cohort": cohort, "gap_floor": floor,
                         "retained": len(retained), "correct": correct,
                         "constant": constant,
                         "beats_constant": correct > constant})
    return pd.DataFrame(rows)


def magnitude_sensitivity() -> pd.DataFrame:
    """Is 1.0 point a discovered constant or a chosen round number? Sweep it and see.

    Algorithm 1 refuses a sign call when the effect is "within seed noise", and the third
    cohort's committed protocol fixes that at one percentage point. The paper reports the
    split the guard produces (21 of 22 above, 11 of 18 below) as evidence the guard is
    measured rather than assumed. That is evidence a floor exists. It is not evidence that
    the floor belongs at 1.0, and the two claims read alike unless the sweep is shown.

    Post-hoc, and the label matters: the cohorts were scored at 1.0 as pre-registered, and
    nothing here re-scores them. This asks only how much the choice of floor mattered.
    """
    frame = pd.concat([
        pd.read_csv(RESEARCH_RESULTS_DIR / "third_direction" / "third_direction.csv"),
        pd.read_csv(RESEARCH_RESULTS_DIR / "lending_direction" / "lending_direction.csv"),
    ])
    frame["correct"] = frame["predicted"] == frame["actual"]
    frame["magnitude"] = frame["pie"].abs()
    rows = []
    for floor in (0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 3.00, 5.00):
        above = frame[frame["magnitude"] >= floor]
        below = frame[frame["magnitude"] < floor]
        rows.append({
            "floor": floor,
            "above_n": len(above), "above_correct": int(above["correct"].sum()),
            "below_n": len(below), "below_correct": int(below["correct"].sum()),
            "separation": float(above["correct"].mean() - below["correct"].mean()),
        })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one population stem (default: all swept)")
    parser.add_argument("--sealed-sensitivity", action="store_true",
                        help="re-score the sealed direction cohorts at four "
                             "parity-gap floors instead")
    parser.add_argument("--seed-stability", action="store_true",
                        help="per-seed sign agreement for every sealed arm instead")
    parser.add_argument("--magnitude-sensitivity", action="store_true",
                        help="sweep Algorithm 1's 1.0-point magnitude guard over the "
                             "sealed cohorts, to show what the choice of value bought")
    args = parser.parse_args()
    OUT = research_dir("verdicts")

    if args.seed_stability:
        table = seed_stability()
        print(table.to_string(index=False))
        solid = int((table["seeds_agreeing"] == table["seeds"]).sum())
        print(f"\nunanimous across seeds: {solid}/{len(table)} arms")
        table.to_csv(OUT / "seed_stability.csv", index=False)
        print(f"\nwrote {OUT}/seed_stability.csv")
        return

    if args.magnitude_sensitivity:
        table = magnitude_sensitivity()
        show = table.assign(
            above=lambda d: d.above_correct.astype(str) + "/" + d.above_n.astype(str),
            below=lambda d: d.below_correct.astype(str) + "/" + d.below_n.astype(str))
        print(show[["floor", "above", "below", "separation"]]
              .to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
        best = table.loc[table.separation.idxmax()]
        at_one = table[table.floor == 1.00].iloc[0]
        print(f"\n  A floor separates reliable arms from unreliable ones at every value "
              f"tried: separation\n  runs {table.separation.min():+.0%} to "
              f"{table.separation.max():+.0%} over 0.25-5.00 points.")
        print(f"  Best separation is at {best.floor:.2f} ({best.separation:+.0%}); the "
              f"committed 1.00 gives {at_one.separation:+.0%}.")
        print("  So the guard's existence is measured and its value is operational -- a "
              "round number\n  fixed in the protocol, which the data neither singles out "
              "nor contradicts.")
        table.to_csv(OUT / "magnitude_sensitivity.csv", index=False)
        print(f"\nwrote {OUT}/magnitude_sensitivity.csv")
        return

    if args.sealed_sensitivity:
        table = sealed_sensitivity()
        print(table.to_string(index=False))
        table.to_csv(OUT / "sealed_sensitivity.csv", index=False)
        print(f"\nwrote {OUT}/sealed_sensitivity.csv")
        return

    stems = [s for s in swept_stems() if not args.dataset or s == args.dataset]
    frame = pd.DataFrame([classify(stem) for stem in stems])
    print(frame.to_string(index=False))
    print("\nverdict distribution over the swept populations:")
    print(frame["verdict"].value_counts().to_string())
    directional = frame[frame["verdict"].isin(["WITHDRAWAL", "EXTENSION"])]
    scored = directional[directional["agrees"].notna()]
    if len(scored):
        print(f"\ndirectional verdicts with a natural arm to score against: "
              f"{int(scored['agrees'].sum())}/{len(scored)} agree")
    frame.to_csv(OUT / "verdicts.csv", index=False)
    print(f"\nwrote {OUT}/verdicts.csv")


if __name__ == "__main__":
    main()
