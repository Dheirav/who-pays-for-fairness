"""Does the selection-rate floor survive populations it was not derived from?

**Individual work, beyond the course submission.**

**Written before the sweep it analyses had finished**, and committed after it in the same
session, in authorship order rather than in wall-clock order. The claim being made is
about when the predictions were fixed, not about commit timestamps. Document 19 tested a
selection-rate floor on Adult alone and closed by saying so: *"It is one dataset. The three
population-level documents in this folder exist because single-dataset findings are exactly
what should not be trusted, and this one has not been through that."* This puts it through
that. The predictions and their thresholds are fixed below, before the numbers exist.

**One disclosure.** Wyoming was run first as a timing probe and its result was seen before
this module was written: parity held (0.0481 plain against 0.0527 floored), the pie loss
went from −10.1% to −1.2%, and the exchange rate from 2.06 to 1.10. One of the eighteen
cells was therefore not blind. It is left in the analysis and named here rather than
quietly dropped, because dropping a population after seeing it is the larger sin.

What is being tested
--------------------
Document 19's construction adds ``P(h(x) = 1) >= target`` alongside ``DemographicParity``,
with the target set to the unconstrained model's own selection rate. On Adult, five seeds:
parity was satisfied to the same tolerance (0.0179 against 0.0178) while the loss of
favourable decisions fell from **−20.5% to −0.6%** and the exchange rate from **2.68
destroyed per one created to 1.03**, for **0.37 accuracy points**.

The question is whether that is a fact about the objective or a fact about Adult.

Stated in advance, so they can fail
-----------------------------------
Across the nine ACS populations in each protected-attribute arm, plus Adult:

**L1 -- the floor does not cost parity.** Mean ``|dp_floor - dp_plain|`` at or under
``PARITY_TOLERANCE`` across populations, and ``dp_floor`` no worse than twice ``dp_plain``
in every population. If adding the floor breaks parity, the construction is a trade, not a
free lunch, and document 19's headline does not generalise.

**L2 -- the pie survives.** The floored arm's loss of favourable decisions is smaller in
absolute value than the plain arm's in **every** population, and the mean floored loss is
under ``MAX_FLOORED_LOSS``. This is the finding. If it fails anywhere, document 19 is
Adult-specific.

**L3 -- who pays changes, not just how many.** The exchange rate falls in every population,
and the mean floored exchange rate is under ``MAX_EXCHANGE``. A variant that held the total
while taking from the same people would pass L2 and fail this, and would be levelling down
with compensation rather than levelling up.

**L4 -- it stays cheap.** The floor's *extra* accuracy cost over the plain constraint
averages under ``MAX_EXTRA_COST``. Note this can come out negative: on the Wyoming probe
the floored arm was more accurate than the plain one, which is possible because a floor
that stops the optimiser withdrawing decisions can keep it nearer the unconstrained model.

**L5 -- the small-population caveat, predicted rather than discovered.** Document 15 found
that below roughly 2,500 test subjects the method's own randomness exceeds the entire
effect of the constraint. So the L2 effect should be *noisier* on small populations: the
across-seed spread of the floored arm's pie change should correlate negatively with test-set
size. If instead the effect is uniform across sizes, document 15's caution does not reach
this construction and that is worth knowing.

**Not predicted, and reported either way:** whether the race arm behaves like the sex arm.
Document 14 found the DP/EO conflict *reverses* across protected attributes, so there is a
live possibility of an arm difference here. No direction is claimed, because none is
derivable, and stating one after the fact is what document 13 records going wrong.

Run:  python -m src.experiments.analyse_levelling_up
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, output_dir, research_dir

DEFAULT_STATES = ["AL", "OR", "UT", "MS", "WV", "NM", "ND", "VT", "WY"]

SEX_ARM, RACE_ARM = "sex", "rac1p"

PLAIN, FLOORED, BASE = "expgrad_dp", "expgrad_dp_floor", "baseline"

# L1: how far the floored arm's parity may sit from the plain arm's, in DP difference.
# Document 19's Adult gap is 0.0001; the probe's is 0.0046. A tenth of a typical baseline
# violation (~0.19) is a generous bar that still fails a construction that trades parity
# away to protect the pie.
PARITY_TOLERANCE = 0.02

# L2: the floored arm's mean loss of favourable decisions. Adult's is -0.6%; the plain
# arm's range across the ablation is -7.9% to -22.1%. 5% sits well clear of both.
MAX_FLOORED_LOSS = 5.0

# L3: favourable decisions destroyed per one created. 1.0 is a clean one-for-one transfer;
# Adult's floored arm reaches 1.03 against 2.68 plain.
MAX_EXCHANGE = 1.5

# L4: extra accuracy cost of the floor over the plain constraint, in percentage points.
MAX_EXTRA_COST = 1.0

# L5: document 15's threshold, in test subjects.
SMALL_POPULATION = 2500


def population_dirs(states: list[str], arm: str) -> dict[str, str]:
    """Map a population label to its levelling-up results directory name."""
    suffix = "" if arm == SEX_ARM else f"_{RACE_ARM}"
    found = {}
    for state in states:
        name = f"acs_income_{state.lower()}_2018{suffix}_levelling_up"
        if (RESEARCH_RESULTS_DIR / name / "levelling_up_runs.csv").exists():
            found[state] = name
    if arm == SEX_ARM and (RESEARCH_RESULTS_DIR / "adult_levelling_up"
                           / "levelling_up_runs.csv").exists():
        found["Adult"] = "adult_levelling_up"
    return found


def test_size(name: str) -> float:
    """Test-set size for a population, taken from its who-pays run.

    ``run_levelling_up`` does not record it, and L5 is a claim about population size, so
    it is read from the experiment that does: ``who_pays_runs.csv`` carries ``n_priv`` and
    ``n_unpriv`` for the same split protocol and the same seeds.

    The directory comes from ``output_dir`` rather than from either results root by name,
    which is how :mod:`analyse_sweep` reaches the same file. Naming a root here would put
    the course-side path in this module and would trip -- correctly -- the guard in
    ``tests/test_output_isolation.py``, which cannot tell a read from a write.
    """
    dataset_name = "adult" if name == "adult_levelling_up" else name.removesuffix("_levelling_up")
    path = output_dir(dataset_name) / "who_pays_runs.csv"
    if not path.exists():
        return float("nan")
    runs = pd.read_csv(path)
    return float((runs["n_priv"] + runs["n_unpriv"]).mean())


def load_arm(states: list[str], arm: str) -> pd.DataFrame:
    """One row per population: the plain and floored arms side by side."""
    rows = []
    for label, name in population_dirs(states, arm).items():
        runs = pd.read_csv(RESEARCH_RESULTS_DIR / name / "levelling_up_runs.csv")
        mean = runs.groupby("arm").mean(numeric_only=True)
        spread = runs.groupby("arm").std(numeric_only=True)
        if not {PLAIN, FLOORED, BASE}.issubset(mean.index):
            continue
        rows.append({
            "population": label,
            "arm": arm,
            "n_test": test_size(name),
            "dp_base": mean.loc[BASE, "dp_diff"],
            "dp_plain": mean.loc[PLAIN, "dp_diff"],
            "dp_floor": mean.loc[FLOORED, "dp_diff"],
            "pie_plain": mean.loc[PLAIN, "positives_pct_change"],
            "pie_floor": mean.loc[FLOORED, "positives_pct_change"],
            "pie_floor_sd": spread.loc[FLOORED, "positives_pct_change"],
            "exchange_plain": mean.loc[PLAIN, "lost_per_gained"],
            "exchange_floor": mean.loc[FLOORED, "lost_per_gained"],
            "acc_base": mean.loc[BASE, "accuracy"],
            "acc_plain": mean.loc[PLAIN, "accuracy"],
            "acc_floor": mean.loc[FLOORED, "accuracy"],
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["extra_cost_pts"] = 100 * (frame["acc_plain"] - frame["acc_floor"])
    return frame.set_index("population")


def verdict(frame: pd.DataFrame, arm: str) -> dict[str, bool]:
    """Evaluate L1-L5 against the thresholds fixed in this module's docstring."""
    print(f"\n{'=' * 78}\n=== {arm} arm: {len(frame)} populations ===\n{'=' * 78}")
    print(frame.round(4).to_string())

    results = {}

    parity_gap = (frame["dp_floor"] - frame["dp_plain"]).abs()
    worst = frame["dp_floor"] > 2 * frame["dp_plain"]
    results["L1"] = parity_gap.mean() <= PARITY_TOLERANCE and not worst.any()
    print(f"\nL1  the floor does not cost parity            -> "
          f"{'HOLDS' if results['L1'] else 'FAILS'}")
    print(f"      mean |dp_floor - dp_plain| = {parity_gap.mean():.4f}  "
          f"(bar {PARITY_TOLERANCE})")
    if worst.any():
        print(f"      more than doubled in: {', '.join(frame.index[worst])}")

    improved = frame["pie_floor"].abs() < frame["pie_plain"].abs()
    results["L2"] = bool(improved.all()) and abs(frame["pie_floor"].mean()) < MAX_FLOORED_LOSS
    print(f"\nL2  the pie survives                          -> "
          f"{'HOLDS' if results['L2'] else 'FAILS'}")
    print(f"      mean pie change {frame['pie_plain'].mean():+.1f}% plain -> "
          f"{frame['pie_floor'].mean():+.1f}% floored  (bar {MAX_FLOORED_LOSS}%)")
    print(f"      smaller loss in {int(improved.sum())}/{len(frame)} populations")
    if not improved.all():
        print(f"      not improved in: {', '.join(frame.index[~improved])}")

    fell = frame["exchange_floor"] < frame["exchange_plain"]
    results["L3"] = bool(fell.all()) and frame["exchange_floor"].mean() < MAX_EXCHANGE
    print(f"\nL3  who pays changes                          -> "
          f"{'HOLDS' if results['L3'] else 'FAILS'}")
    print(f"      mean exchange {frame['exchange_plain'].mean():.2f} -> "
          f"{frame['exchange_floor'].mean():.2f} destroyed per created  (bar {MAX_EXCHANGE})")
    print(f"      fell in {int(fell.sum())}/{len(frame)} populations")

    results["L4"] = frame["extra_cost_pts"].mean() < MAX_EXTRA_COST
    print(f"\nL4  it stays cheap                            -> "
          f"{'HOLDS' if results['L4'] else 'FAILS'}")
    print(f"      extra accuracy cost of the floor = "
          f"{frame['extra_cost_pts'].mean():+.2f} pts  (bar {MAX_EXTRA_COST})")

    if frame["n_test"].notna().sum() >= 4 and frame["pie_floor_sd"].notna().sum() >= 4:
        mask = frame["n_test"].notna() & frame["pie_floor_sd"].notna()
        r = float(np.corrcoef(frame.loc[mask, "n_test"], frame.loc[mask, "pie_floor_sd"])[0, 1])
        results["L5"] = r < 0
        small = frame[frame["n_test"] < SMALL_POPULATION]
        print(f"\nL5  the effect is noisier when small          -> "
              f"{'HOLDS' if results['L5'] else 'FAILS'}")
        print(f"      r(test size, across-seed spread of the floored pie change) = {r:+.3f}")
        if len(small):
            print(f"      under {SMALL_POPULATION} test subjects: "
                  f"{', '.join(small.index)} (spread "
                  f"{small['pie_floor_sd'].mean():.2f} against "
                  f"{frame[frame['n_test'] >= SMALL_POPULATION]['pie_floor_sd'].mean():.2f})")
    else:
        print("\nL5  not evaluable -- test sizes or per-seed spreads unavailable")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=DEFAULT_STATES)
    args = parser.parse_args()

    frames, verdicts = {}, {}
    for arm in (SEX_ARM, RACE_ARM):
        frame = load_arm(args.states, arm)
        if frame.empty:
            print(f"\n=== {arm} arm: no results found; run run_levelling_up first ===")
            continue
        frames[arm] = frame
        verdicts[arm] = verdict(frame, arm)

    if len(frames) == 2:
        print(f"\n{'=' * 78}\n=== the two arms ===\n{'=' * 78}")
        for key in ("pie_plain", "pie_floor", "exchange_plain", "exchange_floor"):
            print(f"  {key:16s} sex {frames[SEX_ARM][key].mean():+8.2f}   "
                  f"race {frames[RACE_ARM][key].mean():+8.2f}")
        agree = {k: verdicts[SEX_ARM].get(k) == verdicts[RACE_ARM].get(k) for k in verdicts[SEX_ARM]}
        print(f"\n  predictions agreeing across arms: "
              f"{sum(agree.values())}/{len(agree)}"
              + ("" if all(agree.values())
                 else f" -- differ on {[k for k, v in agree.items() if not v]}"))

    if frames:
        out = research_dir("levelling_up_sweep")
        pd.concat(frames.values()).to_csv(out / "levelling_up_sweep.csv")
        print(f"\nwrote {out}/levelling_up_sweep.csv")


if __name__ == "__main__":
    main()
