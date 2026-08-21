"""Does the selection rate predict the direction under a criterion that never mentions it?

**Individual work, beyond the course submission.**

**Written before any Alabama or Oregon equalized-odds arm was run**, and committed before
them. Only the Wyoming smoke test existed when this file was written, and what it showed is
reported below rather than hidden, because it is the reason for E0.

The weakness this closes
------------------------
Every result in documents 05, 11-13 and 21-23 is demographic parity. As it stands the
project's claim is about **one constraint**, not about fairness constraints, and a reviewer
gets to say that the whole phenomenon is an artifact of the one criterion that is defined in
terms of selection rates. Under demographic parity, equalising the rates *is* the objective,
so moving the pool of favourable decisions is arguably mechanical.

Equalized odds does not mention selection rates. It equalises true- and false-positive rates
*within* each true-outcome stratum, and any change to the total number of favourable
decisions is a side effect. That makes this a **harder** test than the demographic-parity
sweep, not an easier one, and either outcome is worth reporting:

* if the rate still predicts the direction, the finding is about fairness constraints rather
  than about one of them;
* if it does not, document 23 acquires a scope condition -- it is a statement about
  rate-matching criteria -- and that is a sharper claim than the one it replaces.

The design
----------
The demographic-parity arms already on disk for Alabama and Oregon are re-run under
``--constraint equalized_odds`` at the same six income cutoffs and the same five seeds. The
baseline arm is the same unconstrained model in both, so the baseline selection rate is
identical across the two analyses by construction and the comparison is like-for-like.

The floored arm does not exist here. :func:`src.levelling_up.demographic_parity_without_
shrinking` composes a floor with *parity*; there is no honest way to read it as an
equalized-odds object, so it is dropped rather than faked. The direction question does not
need it.

**Arms are excluded by document 23's rule and not a new one** -- baseline demographic-parity
gap below ``MIN_BASELINE_GAP``. Using the equalized-odds gap instead would have been
defensible, but it would exclude a different set of arms and the two sweeps would then no
longer cover the same populations, which is the whole point of running this on the arms
already on disk.

The naive alternative, named in advance
---------------------------------------
Document 26's lesson was that a pre-registration which fixes a threshold but not **a
baseline to beat** can be passed by a derivation that a constant outperforms. The constant
to beat here is:

    **"Equalized odds does not move the pool of favourable decisions, so there is no
    direction to predict."**

This is a serious possibility rather than a straw man. The Wyoming smoke test moved the pie
by **+0.4%** where the demographic-parity arms move it by tens of percent. If every arm
clusters near zero, then a rule that says "no change" is nearly exact everywhere, any
correlation is fitted to noise, and reporting a large ``r`` would be the same mistake
document 26 caught. **E0 exists to let that constant win**, and if it wins it is reported as
the result rather than worked around.

Stated in advance, so they can fail
-----------------------------------
**E0 -- the constraint must bind, and must move something.** Two parts, both required:
the median relative reduction in the equalized-odds gap across retained arms is at least
``MIN_BINDING``; **and** the spread of the pie change across retained arms -- largest minus
smallest -- is at least ``MIN_SPAN_PIE`` percentage points. If the first fails, the
constraint is not doing anything and nothing below identifies anything. If the second fails,
**the constant wins**: equalized odds leaves the pool essentially untouched everywhere, the
direction question does not arise, and that is the finding.

**E1 -- the prediction.** Across retained arms, the change in favourable decisions rises
with the baseline selection rate at ``r >= MIN_R``. This is the primary test.

**E2 -- the exchange rate agrees.** Favourable decisions destroyed per one created falls as
the selection rate rises, at ``r <= -MIN_R``. E1 and E2 measure the same phenomenon through
different arithmetic; disagreement means one of the measures is wrong rather than that the
conjecture is.

**E3 -- the sign flips.** The lowest-rate retained arm shrinks the pool and the highest grows
it. **Secondary, and explicitly allowed to fail while E1 holds.** That combination would mean
the effect is real but weaker under equalized odds -- the rate still orders the arms, but the
constraint never has enough leverage to push a shrinking task into a growing one. That is a
scope condition, and it is reported as one rather than as a success.

**E4 -- the comparison.** The equalized-odds correlation is reported beside the
demographic-parity correlation **on exactly the same arms**, so that "weaker but present" and
"absent" can be told apart. No threshold attaches to this one; it is context for E1, and
fixing a bar for it after seeing E1 would be the error this file exists to avoid.

Run:  python -m src.experiments.analyse_eo --states AL OR
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..datasets.acs import DEFAULT_THRESHOLD
from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from .analyse_threshold import (
    MIN_BASELINE_GAP,
    MIN_R,
    THRESHOLDS,
    arm_name,
    partial_corr,
)

BASE = "baseline"
PLAIN_DP, PLAIN_EO = "expgrad_dp", "expgrad_eo"

# E0, first part: the median arm must lose at least this fraction of its equalized-odds
# gap, or the constraint is not binding and the run says nothing.
MIN_BINDING = 0.20

# E0, second part: the pie change must vary by at least this many percentage points across
# arms. Below it, "equalized odds does not move the pool" is the better description and the
# constant beats any correlation fitted to the residue.
MIN_SPAN_PIE = 2.0


def eo_arm_name(state: str, threshold: int) -> str:
    """Where ``run_levelling_up --constraint equalized_odds`` writes, per its own rule."""
    return f"{arm_name(state, threshold)}_eo"


# The signature of the runs this document's verdict was computed from. `results_io` keeps
# one archived copy per parameter set, so naming it here pins the pre-registered result to
# the data it was decided on -- a later re-run at a different seed count replaces the
# canonical copy but cannot silently restate the verdict.
PREREGISTERED = "constraintequalized_odds_eps0.01_modellogistic_regression_seeds0-4"


def _runs_file(signature: str | None) -> str:
    return "levelling_up_runs.csv" if signature is None \
        else f"levelling_up_runs__{signature}.csv"


def _mean_by_arm(path):
    if not path.exists():
        return None
    return pd.read_csv(path).groupby("arm").mean(numeric_only=True)


def load(states: list[str], thresholds: list[int],
         signature: str | None = PREREGISTERED) -> pd.DataFrame:
    """One row per arm, carrying both constraints' outcomes on the same population.

    ``signature`` selects which archived run to read; ``None`` reads whatever is canonical.
    It defaults to the pre-registered five-seed set so the verdict does not move under a
    later re-run.
    """
    rows = []
    for state in states:
        for threshold in thresholds:
            eo = _mean_by_arm(
                RESEARCH_RESULTS_DIR / eo_arm_name(state, threshold) / _runs_file(signature))
            if eo is None or not {PLAIN_EO, BASE}.issubset(eo.index):
                continue

            row = {
                "state": state,
                "threshold": threshold,
                "positives_base": eo.loc[BASE, "positives"],
                "n_test": eo.loc[BASE, "n_test"],
                "dp_base": eo.loc[BASE, "dp_diff"],
                "eo_base": eo.loc[BASE, "eo_diff"],
                "eo_after": eo.loc[PLAIN_EO, "eo_diff"],
                "pie_eo": eo.loc[PLAIN_EO, "positives_pct_change"],
                "exchange_eo": eo.loc[PLAIN_EO, "lost_per_gained"],
                "acc_base": eo.loc[BASE, "accuracy"],
                "acc_eo": eo.loc[PLAIN_EO, "accuracy"],
            }

            # The parity arm of the same population, for E4. Absent is not an error: the
            # comparison is reported on whatever overlaps.
            dp = _mean_by_arm(
                RESEARCH_RESULTS_DIR / arm_name(state, threshold) / "levelling_up_runs.csv")
            row["pie_dp"] = (dp.loc[PLAIN_DP, "positives_pct_change"]
                             if dp is not None and PLAIN_DP in dp.index else np.nan)
            row["exchange_dp"] = (dp.loc[PLAIN_DP, "lost_per_gained"]
                                  if dp is not None and PLAIN_DP in dp.index else np.nan)
            rows.append(row)

    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["selection_rate"] = frame["positives_base"] / frame["n_test"]
        frame["eo_reduction"] = 1 - frame["eo_after"] / frame["eo_base"]
    return frame


def verdict(frame: pd.DataFrame) -> dict:
    print(frame.round(4).to_string(index=False))

    kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
    dropped = frame[frame["dp_base"] < MIN_BASELINE_GAP]
    print(f"\nE4-exclusion  arms below a baseline parity gap of {MIN_BASELINE_GAP}: "
          f"{len(dropped)} excluded, by document 23's rule")
    for _, row in dropped.iterrows():
        print(f"      ${row['threshold']:,} on {row['state']}: dp_base "
              f"{row['dp_base']:.4f}, selection rate {row['selection_rate']:.3f}")

    if len(kept) < 4:
        print(f"\nVOID  only {len(kept)} arms retained; no correlation is meaningful")
        return {"void": True}

    binding = float(kept["eo_reduction"].median())
    span = float(kept["pie_eo"].max() - kept["pie_eo"].min())
    e0_binds, e0_moves = binding >= MIN_BINDING, span >= MIN_SPAN_PIE

    def r(a, b):
        return float(np.corrcoef(kept[a], kept[b])[0, 1])

    r_pie = r("selection_rate", "pie_eo")
    r_exchange = r("selection_rate", "exchange_eo")
    e1, e2 = r_pie >= MIN_R, r_exchange <= -MIN_R

    ordered = kept.sort_values("selection_rate")
    lowest, highest = ordered.iloc[0], ordered.iloc[-1]
    e3 = lowest["pie_eo"] < 0 < highest["pie_eo"]

    print(f"\nE0  equalized-odds gap reduction, median over arms: {binding:+.3f} "
          f"(needs >= {MIN_BINDING})  {'HOLDS' if e0_binds else 'FAILS'}")
    print(f"    pie change spread across arms: {span:.2f} points "
          f"(needs >= {MIN_SPAN_PIE})  {'HOLDS' if e0_moves else 'FAILS'}")
    if not e0_moves:
        print("    -> the constant wins: equalized odds does not move the pool enough for")
        print("       a direction to exist. E1-E3 are reported but carry no weight.")

    print(f"\nE1  selection rate vs pie change under EO:      r = {r_pie:+.3f} "
          f"(needs >= {MIN_R})  {'HOLDS' if e1 else 'FAILS'}")
    print(f"E2  selection rate vs exchange rate under EO:   r = {r_exchange:+.3f} "
          f"(needs <= {-MIN_R})  {'HOLDS' if e2 else 'FAILS'}")
    print(f"E3  sign flip: lowest arm (rate {lowest['selection_rate']:.3f}) "
          f"{lowest['pie_eo']:+.2f}%, highest (rate {highest['selection_rate']:.3f}) "
          f"{highest['pie_eo']:+.2f}%  {'HOLDS' if e3 else 'FAILS'}")
    if e1 and not e3:
        print("    -> ordering without reversal: the rate predicts the direction under EO")
        print("       but the constraint lacks the leverage to cross over. Scope condition.")

    paired = kept.dropna(subset=["pie_dp"])
    out = {"void": False, "binding": binding, "span": span, "e0": e0_binds and e0_moves,
           "r_pie_eo": r_pie, "r_exchange_eo": r_exchange, "e1": e1, "e2": e2, "e3": e3,
           "n_kept": len(kept)}

    if len(paired) >= 4:
        r_dp = float(np.corrcoef(paired["selection_rate"], paired["pie_dp"])[0, 1])
        r_eo_paired = float(np.corrcoef(paired["selection_rate"], paired["pie_eo"])[0, 1])
        print(f"\nE4  on the same {len(paired)} arms:")
        print(f"      demographic parity  r = {r_dp:+.3f}, "
              f"pie change spans {paired['pie_dp'].min():+.1f}% to {paired['pie_dp'].max():+.1f}%")
        print(f"      equalized odds      r = {r_eo_paired:+.3f}, "
              f"pie change spans {paired['pie_eo'].min():+.1f}% to {paired['pie_eo'].max():+.1f}%")
        # Reported because a correlation surviving the confound is the claim document 23
        # had to defend, and the same confound is present here.
        print(f"      EO correlation partialling out the baseline parity gap: "
              f"{partial_corr(paired['selection_rate'], paired['pie_eo'], paired['dp_base']):+.3f}")
        out |= {"r_pie_dp_paired": r_dp, "r_pie_eo_paired": r_eo_paired, "n_paired": len(paired)}

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=["AL", "OR"])
    parser.add_argument("--thresholds", type=int, nargs="+", default=THRESHOLDS)
    parser.add_argument("--signature", default=PREREGISTERED,
                        help="archived run to read; 'canonical' reads the latest instead")
    args = parser.parse_args()

    signature = None if args.signature == "canonical" else args.signature
    frame = load(args.states, args.thresholds, signature)
    if frame.empty:
        raise SystemExit(
            "no equalized-odds arms found; run\n"
            "  python -m src.experiments.run_levelling_up --dataset acs:AL::<threshold> "
            "--constraint equalized_odds")

    print(f"=== equalized odds across {len(frame)} arms "
          f"({', '.join(args.states)}), default cutoff ${DEFAULT_THRESHOLD:,} ===\n")
    result = verdict(frame)

    OUT = research_dir("eo")
    frame.round(6).to_csv(OUT / "eo_arms.csv", index=False)
    pd.Series(result).to_csv(OUT / "eo_verdict.csv", header=False)
    print(f"\nwrote {OUT}/eo_arms.csv")


if __name__ == "__main__":
    main()
