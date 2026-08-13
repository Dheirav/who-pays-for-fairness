"""Does the group ratio explain the magnitude that the selection rate does not?

**Individual work, beyond the course submission.**

**Written and committed before any arm of this sweep was run.**

Where this comes from
---------------------
[Document 23](../../research/docs/23-the-selection-rate-sets-the-direction.md) established
that the selection rate sets the **direction** of levelling down, on two states, surviving
the base-rate-gap confound. It also recorded, plainly, that it does not set the magnitude:

    Alabama at 0.252 loses 2.34% where Adult at 0.205 loses 20.5% -- an order of magnitude
    apart at a comparable rate. The selection rate is *a* moderator, not *the* determinant.

The obvious suspect is the **group ratio**. Adult's is 2.08 privileged per unprivileged;
Alabama's sex arm is 1.09. Documents 11 and 13 already found group ratio to be a genuine
cause of the rate-versus-people divergence, acting through cross-flow, so it is not a
free-floating guess.

The design: two factors, crossed
--------------------------------
The sex arm cannot test this -- every ACS state sits between 1.02 and 1.24, and Adult alone
carries the high end, which is exactly the gap document 11 complained about. The **race
arm** spans 1.94 to 25.3.

So: four states chosen for spread in group ratio, crossed with the income cutoffs of
document 23. Group ratio varies *between* states; selection rate varies *within* each.

| state | group ratio | test subjects |
|---|---|---|
| MS | 1.94 | 3,957 |
| AL | 3.20 | 6,681 |
| OR | 6.36 | 6,576 |
| UT | 8.52 | 4,902 |

The states are chosen so that **size is not monotone in ratio** (3,957 / 6,681 / 6,576 /
4,902 against a rising ratio). Documents 11 and 13 record that group ratio and sample size
are entangled across ACS populations, and that mistaking one for the other cost this
project a retraction. This choice weakens that entanglement by construction, and G3
controls for what remains.

All four have more than 2,500 test subjects, document 15's floor for the constraint's
effect to exceed the method's own randomness.

Stated in advance, so they can fail
-----------------------------------
**G0 -- manipulation check.** Group ratio spans at least ``MIN_RATIO_SPAN`` across states
and the selection rate spans at least ``MIN_RATE_SPAN`` within every state. Both factors
must move or nothing below is identified.

**G1 -- document 23 replicates in the race arm.** The selection-rate effect holds within
each state at ``r >= MIN_R``. Document 23 is two states of *one* protected attribute; if
the direction result does not survive changing the attribute, its reach is narrower than
that document claims and this must be reported before anything about ratio is read.

**G2 -- the prediction.** Holding the selection rate fixed, a larger group ratio means
*more* levelling down. Partial ``r(log ratio, pie change | selection rate) <=
-MIN_PARTIAL_R``. Negative because more levelling down is a more negative pie change.

**G3 -- and it is not sample size in disguise.** G2 survives controlling for test-set size
as well: partial ``r(log ratio, pie change | selection rate, n) <= -MIN_PARTIAL_R_2``. This
is the prediction most likely to fail. Document 13 retracted document 11's confident
correction on exactly this confound, and the retraction is the reason this control is fixed
here rather than added later.

**G4 -- the floor still rescues.** ``r(pie change, amount rescued) <= -0.9`` across all
cells, as in document 23. If the floor stops tracking the damage once the group ratio moves,
document 23's strongest practical claim is narrower than stated.

If G2 fails, group ratio does not explain the residual and document 23's "something else"
remains unidentified. If G2 holds and G3 fails, the residual is sample size rather than
ratio, and this project has walked into document 11's error a second time -- which is worth
knowing and would be reported as such.

Run:  python -m src.experiments.analyse_ratio
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..datasets.acs import DEFAULT_THRESHOLD
from ..results_io import RESEARCH_RESULTS_DIR, output_dir, research_dir
from .analyse_levelling_up import test_size
from .analyse_threshold import PLAIN, BASE, FLOORED, partial_corr

# Chosen for spread in group ratio at adequate sample size, with size deliberately not
# monotone in ratio. See the module docstring.
DEFAULT_STATES = ["MS", "AL", "OR", "UT"]

# $10,000 is dropped from document 23's set: it was degenerate in both states there
# (baseline parity gap under 0.05) and would only add cells the exclusion rule discards.
THRESHOLDS = [20_000, 30_000, DEFAULT_THRESHOLD, 70_000, 100_000]

MIN_RATIO_SPAN = 3.0        # G0: max/min group ratio across states
MIN_RATE_SPAN = 0.40        # G0: selection-rate span within a state
MIN_R = 0.50                # G1: within-state selection-rate correlation
MIN_PARTIAL_R = 0.40        # G2
MIN_PARTIAL_R_2 = 0.30      # G3, looser because it partials out two variables at once
MIN_BASELINE_GAP = 0.05     # document 12's degenerate-arm ground, as in document 23


def population(state: str) -> str:
    return f"acs_income_{state.lower()}_2018_rac1p"


def arm_dir(state: str, threshold: int) -> str:
    stem = population(state)
    if threshold != DEFAULT_THRESHOLD:
        stem = f"{stem}_t{threshold}"
    return f"{stem}_levelling_up"


def load(states: list[str], thresholds: list[int]) -> pd.DataFrame:
    rows = []
    for state in states:
        n_test = test_size(arm_dir(state, DEFAULT_THRESHOLD))
        # Routed through `output_dir` rather than named off a results root, for the same
        # reason as `analyse_levelling_up.test_size`: the guard in test_output_isolation
        # cannot tell a read from a write and correctly flags the literal.
        who = pd.read_csv(output_dir(population(state)) / "who_pays_runs.csv")
        ratio = float((who["n_priv"] / who["n_unpriv"]).mean())
        for threshold in thresholds:
            path = RESEARCH_RESULTS_DIR / arm_dir(state, threshold) / "levelling_up_runs.csv"
            if not path.exists():
                continue
            runs = pd.read_csv(path)
            mean = runs.groupby("arm").mean(numeric_only=True)
            if not {PLAIN, BASE}.issubset(mean.index):
                continue
            rows.append({
                "state": state, "threshold": threshold,
                "group_ratio": ratio, "n_test": n_test,
                "selection_rate": mean.loc[BASE, "positives"] / n_test,
                "dp_base": mean.loc[BASE, "dp_diff"],
                "pie_plain": mean.loc[PLAIN, "positives_pct_change"],
                "pie_floor": mean.loc[FLOORED, "positives_pct_change"]
                if FLOORED in mean.index else np.nan,
                "exchange_plain": mean.loc[PLAIN, "lost_per_gained"],
            })
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["log_ratio"] = np.log(frame["group_ratio"])
    return frame


def verdict(frame: pd.DataFrame) -> None:
    print(frame.round(4).to_string(index=False))
    kept = frame[frame["dp_base"] >= MIN_BASELINE_GAP]
    dropped = frame[frame["dp_base"] < MIN_BASELINE_GAP]
    print(f"\n  degenerate arms excluded (baseline gap < {MIN_BASELINE_GAP}): {len(dropped)}")
    for _, row in dropped.iterrows():
        print(f"      {row['state']} ${row['threshold']:,}: dp_base {row['dp_base']:.4f}")

    ratios = frame.groupby("state")["group_ratio"].first()
    ratio_span = ratios.max() / ratios.min()
    rate_spans = frame.groupby("state")["selection_rate"].agg(lambda s: s.max() - s.min())
    g0 = ratio_span >= MIN_RATIO_SPAN and (rate_spans >= MIN_RATE_SPAN).all()
    print(f"\nG0  both factors move                     -> {'HOLDS' if g0 else 'FAILS'}")
    print(f"      group ratio {ratios.min():.2f} to {ratios.max():.2f} "
          f"({ratio_span:.1f}x, bar {MIN_RATIO_SPAN}x)")
    print(f"      selection-rate span per state: "
          f"{', '.join(f'{s}={v:.2f}' for s, v in rate_spans.items())}  (bar {MIN_RATE_SPAN})")

    within = {}
    for state, rows in kept.groupby("state"):
        if len(rows) >= 3:
            within[state] = float(np.corrcoef(rows["selection_rate"], rows["pie_plain"])[0, 1])
    g1 = bool(within) and all(r >= MIN_R for r in within.values())
    print(f"\nG1  docs/23 replicates in the race arm    -> {'HOLDS' if g1 else 'FAILS'}")
    print(f"      within-state r: {', '.join(f'{s}={r:+.3f}' for s, r in within.items())}"
          f"  (bar {MIN_R})")

    if len(kept) < 6:
        print("\n  too few cells for the partial correlations; stopping here")
        return

    r2 = partial_corr(kept["log_ratio"], kept["pie_plain"], kept["selection_rate"])
    g2 = r2 <= -MIN_PARTIAL_R
    print(f"\nG2  a larger group ratio means more harm -> {'HOLDS' if g2 else 'FAILS'}")
    print(f"      partial r = {r2:+.3f} holding the selection rate fixed  "
          f"(bar {-MIN_PARTIAL_R})")
    print(f"      raw r(log ratio, pie) = "
          f"{float(np.corrcoef(kept['log_ratio'], kept['pie_plain'])[0, 1]):+.3f}")

    # Two controls at once: residualise both variables on selection rate and size, then
    # correlate what is left. Equivalent to a second-order partial correlation.
    def residual(target: str, controls: list[str]) -> np.ndarray:
        design = np.column_stack([np.ones(len(kept))] + [kept[c].to_numpy() for c in controls])
        beta, *_ = np.linalg.lstsq(design, kept[target].to_numpy(), rcond=None)
        return kept[target].to_numpy() - design @ beta

    controls = ["selection_rate", "n_test"]
    r3 = float(np.corrcoef(residual("log_ratio", controls), residual("pie_plain", controls))[0, 1])
    g3 = r3 <= -MIN_PARTIAL_R_2
    print(f"\nG3  and it is not sample size in disguise -> {'HOLDS' if g3 else 'FAILS'}")
    print(f"      partial r = {r3:+.3f} holding rate AND size fixed  (bar {-MIN_PARTIAL_R_2})")
    print(f"      r(log ratio, n_test) = "
          f"{float(np.corrcoef(kept['log_ratio'], kept['n_test'])[0, 1]):+.3f}  "
          "-- how entangled the two are in this design")

    rescued = frame["pie_floor"] - frame["pie_plain"]
    r4 = float(np.corrcoef(frame["pie_plain"], rescued)[0, 1])
    g4 = r4 <= -0.9
    print(f"\nG4  the floor still tracks the damage    -> {'HOLDS' if g4 else 'FAILS'}")
    print(f"      r = {r4:+.3f}  (bar -0.9)")

    print("\n" + "=" * 78)
    if g0 and g2 and g3:
        print("Group ratio explains magnitude where the selection rate explains direction,")
        print("and it is not sample size. Document 23's residual has an identified cause.")
    elif g0 and g2 and not g3:
        print("Group ratio predicts magnitude until sample size is held fixed, at which")
        print("point it does not. That is document 11's error repeated, and the honest")
        print("reading is that size rather than ratio carries the residual.")
    elif g0 and not g2:
        print("Group ratio does NOT explain the residual. Document 23's 'something else'")
        print("stays unidentified, and this candidate is refuted on its own chosen test.")
    else:
        print("G0 failed; the design did not vary what it needed to. Nothing above holds.")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=DEFAULT_STATES)
    parser.add_argument("--thresholds", type=int, nargs="+", default=THRESHOLDS)
    args = parser.parse_args()

    frame = load(args.states, args.thresholds)
    if frame.empty:
        print("no arms found; run run_levelling_up with --dataset acs:<ST>:RAC1P:<cutoff>")
        return
    verdict(frame)

    out = research_dir("ratio_sweep")
    frame.to_csv(out / "ratio_sweep.csv", index=False)
    print(f"\nwrote {out}/ratio_sweep.csv")


if __name__ == "__main__":
    main()
