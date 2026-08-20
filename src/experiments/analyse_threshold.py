"""Is the levelling-down direction set by how many people the task says yes to?

**Individual work, beyond the course submission.**

**Written before the sweep was run**, and committed after it in the same session, in
authorship order rather than in wall-clock order -- the claim is about when the predictions
were fixed, not about commit timestamps. No threshold arm had been executed when this file
was written. The predictions and their thresholds are fixed below.

Where this comes from
---------------------
[Document 22](../../research/docs/22-levelling-down-is-not-universal.md) found the
levelling-down direction **reversing** on HMDA mortgage data: the demographic parity
constraint grew the pool of favourable decisions by 4.3% instead of shrinking it, at an
exchange rate of 0.50. Every survey population in documents 11-13 and 21 went the other
way, 18 of 19 shrinking the pie.

The obvious candidate is where the task sits on the selection-rate scale. The survey
populations all land between **0.195 and 0.353**; HMDA's arms sit at **0.808 and 0.758**.
When most applicants are approved already, closing a gap by lifting the disadvantaged
group is cheap, because they are near the boundary anyway.

That conjecture cannot be tested by comparing the two datasets, and document 22 says so:
they differ in domain, instrument, label semantics, feature set, group ratio, proxy
leakage **and** selection rate at once. Attributing the reversal to the last of those is
the inference this project has already retracted twice.

The design
----------
ACS Income's label is "earns more than $50,000" -- a cutoff chosen by the benchmark, not a
fact about the world. Moving it on **one fixed state** varies the base rate while holding
the population, the survey instrument, the feature set, the group ratio and the proxy
structure exactly fixed. One factor moves. ``tests/test_acs_threshold.py`` asserts that the
rows, features and groups are identical across arms and that only the label changes.

The known confound, and how it is handled
-----------------------------------------
The threshold does not move the selection rate alone. It also moves the **base-rate gap
between the groups**, which is bounded by zero at both extremes -- when almost everyone or
almost nobody is labelled positive, no group difference can exist -- so the gap rises and
then falls while the selection rate climbs monotonically. Document 11's P2 already
suspected the base-rate gap of driving conflict magnitude.

So the gap is measured in every arm and partialled out in **T2**. If the relationship does
not survive that, the sweep has found a base-rate-gap effect wearing a selection-rate
costume, and the conjecture is not supported.

Stated in advance, so they can fail
-----------------------------------
**T0 -- manipulation check.** The baseline selection rate rises monotonically with a
falling cutoff and spans at least ``MIN_SPAN``. If the knob does not move the quantity the
conjecture is about, nothing below identifies anything and the sweep is void.

**T1 -- the prediction.** The change in favourable decisions under the plain constraint
rises with the baseline selection rate, at ``r >= MIN_R``, **and** the sign flips: the
lowest-selection-rate arm shrinks the pie and the highest grows it. A correlation without a
sign change would mean the effect merely weakens, which is a much weaker claim than
document 22 needs.

**T2 -- the confound.** T1's correlation survives partialling out the baseline demographic
parity gap, at ``r >= MIN_PARTIAL_R``. This is the prediction most likely to fail and it is
the one that matters.

**T3 -- the exchange rate agrees.** Favourable decisions destroyed per one created falls as
the selection rate rises, at ``r <= -MIN_R``. T1 and T3 measure the same phenomenon through
different arithmetic, so they should agree; if they disagree, something is wrong with one
of the measures rather than with the conjecture.

**T4 -- degenerate arms are excluded, by a rule fixed here.** An arm whose baseline parity
gap is under ``MIN_BASELINE_GAP`` has essentially no unfairness to remove, and its
"mitigation" is noise. Document 12 excluded Vermont on exactly this ground at 0.0124.
Excluded arms are printed, not hidden, and the correlations are reported both ways.

If T1 fails, the selection-rate conjecture is dead and document 22's reversal belongs to
something else about HMDA. If T1 holds and T2 fails, the moderator is the base-rate gap
rather than the selection rate. Both outcomes are informative and both are to be reported.

Run:  python -m src.experiments.analyse_threshold --states AL
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..datasets.acs import DEFAULT_THRESHOLD
from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# Chosen to span the base-rate range, from a cutoff most people clear to one almost nobody
# does. On Wyoming these give roughly 0.72, 0.36 and 0.08; the exact rates are a property
# of each state and are measured rather than assumed.
THRESHOLDS = [10_000, 20_000, 30_000, DEFAULT_THRESHOLD, 70_000, 100_000]

PLAIN, FLOORED, BASE = "expgrad_dp", "expgrad_dp_floor", "baseline"

# T0: the selection rate must span at least this much, or the knob does not work.
MIN_SPAN = 0.40

# T1/T3: correlation bars. Six arms is few, so these are deliberately demanding.
MIN_R = 0.70

# T2: what must survive partialling out the baseline parity gap.
MIN_PARTIAL_R = 0.40

# T4: below this baseline parity gap there is nothing to mitigate. Document 12's ground.
MIN_BASELINE_GAP = 0.05


def arm_name(state: str, threshold: int, suffix: str = "") -> str:
    """Directory for one arm.

    ``suffix`` selects a variant of the same sweep -- ``"_hgb"`` for the boosted-tree
    learner -- and must match what ``run_levelling_up.output_stem`` produced. The default
    is empty, so every existing arm and every document quoting one keeps its path.
    """
    stem = f"acs_income_{state.lower()}_2018"
    if threshold != DEFAULT_THRESHOLD:
        stem = f"{stem}_t{threshold}"
    return f"{stem}_levelling_up{suffix}"


def partial_corr(x, y, control) -> float:
    """Correlation of x and y with `control` held fixed."""
    x, y, control = np.asarray(x, float), np.asarray(y, float), np.asarray(control, float)

    def r(a, b):
        return float(np.corrcoef(a, b)[0, 1])

    r_xy, r_xc, r_yc = r(x, y), r(x, control), r(y, control)
    return (r_xy - r_xc * r_yc) / np.sqrt((1 - r_xc**2) * (1 - r_yc**2))


def load(states: list[str], thresholds: list[int], suffix: str = "") -> pd.DataFrame:
    rows = []
    for state in states:
        for threshold in thresholds:
            path = (RESEARCH_RESULTS_DIR / arm_name(state, threshold, suffix)
                    / "levelling_up_runs.csv")
            if not path.exists():
                continue
            runs = pd.read_csv(path)
            mean = runs.groupby("arm").mean(numeric_only=True)
            if not {PLAIN, BASE}.issubset(mean.index):
                continue
            rows.append({
                "state": state,
                "threshold": threshold,
                "positives_base": mean.loc[BASE, "positives"],
                "dp_base": mean.loc[BASE, "dp_diff"],
                "dp_plain": mean.loc[PLAIN, "dp_diff"],
                "pie_plain": mean.loc[PLAIN, "positives_pct_change"],
                "pie_floor": mean.loc[FLOORED, "positives_pct_change"]
                if FLOORED in mean.index else np.nan,
                "exchange_plain": mean.loc[PLAIN, "lost_per_gained"],
                "acc_base": mean.loc[BASE, "accuracy"],
                "acc_plain": mean.loc[PLAIN, "accuracy"],
                # Recorded by later runs; absent from the arms that predate the column, which
                # is why `attach_selection_rate` still has a fallback.
                "n_test": mean.loc[BASE, "n_test"] if "n_test" in mean.columns else np.nan,
            })
    return pd.DataFrame(rows)


def attach_selection_rate(frame: pd.DataFrame, states: list[str]) -> pd.DataFrame:
    """Baseline selection rate per arm, from the who-pays run of the same population.

    ``run_levelling_up`` records the positive *count* but not the denominator, so the
    test-set size comes from the experiment that does record it -- exactly as in
    :mod:`analyse_levelling_up`.

    One size serves every arm of a state, and that is exact rather than approximate: the
    threshold changes only the label, so the row count and the 30% test split are
    identical across arms. ``tests/test_acs_threshold.py`` asserts that invariant.
    """
    from .analyse_levelling_up import test_size

    # The default arm's directory is this state's population, so its who-pays run is the
    # right denominator for every arm. Reusing `test_size` rather than repeating the
    # lookup also keeps the course-side results root out of this module, which the guard
    # in tests/test_output_isolation.py checks for and cannot distinguish from a write.
    sizes = {state: test_size(arm_name(state, DEFAULT_THRESHOLD)) for state in states}
    frame = frame.copy()
    # Prefer the size the run recorded for itself. The lookup below reaches the *default*
    # learner's who-pays run, which is the right denominator only because the split
    # protocol is identical across learners -- true, but worth not relying on when the
    # number is available directly.
    looked_up = frame["state"].map(sizes)
    frame["n_test"] = frame["n_test"].fillna(looked_up) if "n_test" in frame else looked_up
    frame["selection_rate"] = frame["positives_base"] / frame["n_test"]
    return frame


def verdict(frame: pd.DataFrame) -> None:
    print(frame.round(4).to_string(index=False))

    kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
    dropped = frame[frame["dp_base"] < MIN_BASELINE_GAP]
    print(f"\nT4  arms with a baseline parity gap under {MIN_BASELINE_GAP}: "
          f"{len(dropped)} excluded")
    for _, row in dropped.iterrows():
        print(f"      ${row['threshold']:,} on {row['state']}: dp_base {row['dp_base']:.4f}, "
              f"selection rate {row['selection_rate']:.3f}")

    # Monotonicity is a within-population property: pooling two states interleaves their
    # selection rates, so a pooled check reports a failure that is an artifact of the
    # ordering rather than of the knob. T0 is therefore required *in every state*.
    span = frame["selection_rate"].max() - frame["selection_rate"].min()
    per_state = {
        state: rows.sort_values("threshold", ascending=False)["selection_rate"]
                   .is_monotonic_increasing
        for state, rows in frame.groupby("state")
    }
    monotone = all(per_state.values())
    t0 = monotone and span >= MIN_SPAN
    print(f"\nT0  the knob moves the selection rate      -> {'HOLDS' if t0 else 'FAILS'}")
    print(f"      {frame['selection_rate'].min():.3f} to {frame['selection_rate'].max():.3f} "
          f"(span {span:.3f}, bar {MIN_SPAN})")
    print(f"      monotone in the cutoff within every state: {monotone} "
          f"({', '.join(f'{s}={v}' for s, v in per_state.items())})")
    if not t0:
        print("      the design does not vary what the conjecture is about; nothing below holds")

    if len(kept) < 3:
        print("\n  too few non-degenerate arms to correlate; stopping here")
        return

    r1 = float(np.corrcoef(kept["selection_rate"], kept["pie_plain"])[0, 1])
    lowest = kept.loc[kept["selection_rate"].idxmin()]
    highest = kept.loc[kept["selection_rate"].idxmax()]
    flipped = lowest["pie_plain"] < 0 < highest["pie_plain"]
    t1 = r1 >= MIN_R and flipped
    print(f"\nT1  the pie change rises with it           -> {'HOLDS' if t1 else 'FAILS'}")
    print(f"      r = {r1:+.3f} over {len(kept)} arms  (bar {MIN_R})")
    print(f"      lowest  rate {lowest['selection_rate']:.3f}: pie {lowest['pie_plain']:+.2f}%")
    print(f"      highest rate {highest['selection_rate']:.3f}: pie {highest['pie_plain']:+.2f}%")
    print(f"      sign flips across the range: {flipped}")

    r2 = partial_corr(kept["selection_rate"], kept["pie_plain"], kept["dp_base"])
    t2 = r2 >= MIN_PARTIAL_R
    print(f"\nT2  and survives the base-rate gap         -> {'HOLDS' if t2 else 'FAILS'}")
    print(f"      partial r = {r2:+.3f} holding dp_base fixed  (bar {MIN_PARTIAL_R})")
    print(f"      r(selection rate, dp_base) = "
          f"{float(np.corrcoef(kept['selection_rate'], kept['dp_base'])[0, 1]):+.3f}")

    r3 = float(np.corrcoef(kept["selection_rate"], kept["exchange_plain"])[0, 1])
    t3 = r3 <= -MIN_R
    print(f"\nT3  the exchange rate agrees               -> {'HOLDS' if t3 else 'FAILS'}")
    print(f"      r = {r3:+.3f}  (bar {-MIN_R})")
    print(f"      {lowest['exchange_plain']:.2f} destroyed per created at the lowest rate, "
          f"{highest['exchange_plain']:.2f} at the highest")

    print("\n" + "=" * 78)
    if t0 and t1 and t2:
        print("The selection rate is a moderator of the levelling-down direction, and the")
        print("relationship is not the base-rate gap in disguise. Document 22's reversal has")
        print("a candidate mechanism that survived a single-factor test.")
    elif t0 and t1 and not t2:
        print("The direction tracks the selection rate, but not once the base-rate gap is")
        print("held fixed. The moderator is more likely the gap than the rate, and the")
        print("conjecture as stated in document 22 is NOT supported.")
    elif t0 and not t1:
        print("The selection rate does NOT set the direction. Document 22's reversal belongs")
        print("to something else about HMDA, and the conjecture is refuted on its own")
        print("chosen test. That is to be reported as it stands.")
    else:
        print("T0 failed, so nothing above identifies anything. Fix the manipulation before")
        print("reading any of the correlations.")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=["AL"])
    parser.add_argument("--thresholds", type=int, nargs="+", default=THRESHOLDS)
    parser.add_argument("--suffix", default="",
                        help='variant of the sweep to read, e.g. "_hgb" for the boosted '
                             "trees; the output file carries it too, so variants cannot "
                             "overwrite each other")
    args = parser.parse_args()

    frame = load(args.states, args.thresholds, args.suffix)
    if frame.empty:
        print("no threshold arms found; run run_levelling_up with --dataset acs:<ST>:SEX:<cutoff>")
        return
    frame = attach_selection_rate(frame, args.states)
    verdict(frame)

    out = research_dir("threshold_sweep")
    path = out / f"threshold_sweep{args.suffix}.csv"
    frame.to_csv(path, index=False)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
