"""Does the crossover appear across a NATURAL split, with no cutoff manipulation?

**Individual work, beyond the course submission.**

**Written and committed before any arm of this sweep was run.**

The weakness this exists to close
---------------------------------
Every natural population in this project sits at a selection rate of <= 0.353 or >= 0.758.
**Zero** sit in 0.36-0.74. Document 23's crossover -- the centre of the paper's claim -- has
therefore only ever been observed by *manufacturing* it, by moving an arbitrary income
cutoff. The obvious review comment is that the transition was engineered.

HMDA closes that. Lenders record *why* the loan was sought, and approval rates differ
sharply by purpose. Pooling Mississippi and Louisiana, race arm:

    improvement   0.516   n_test 2,943   parity gap 0.296
    other         0.564   n_test 4,198   parity gap 0.296
    cashout       0.637   n_test 7,022   parity gap 0.247
    purchase      0.767   n_test 28,841  parity gap 0.226
    refinance     0.784   n_test 9,103   parity gap 0.187

Real lending decisions, one instrument, two states, one year. Nothing is manipulated: the
selection rate varies because home-improvement lending and refinancing are different
businesses. Three arms land inside the band that previously had no natural population at
all, and every arm clears document 15's 2,500-subject floor.

Why the sign test is useless here, and what replaces it
------------------------------------------------------
All five arms sit at or above 0.516, so document 23's rule predicts levelling **up** for
every one of them, and a constant rule saying "all up" would very likely score 5/5. A sign
test would therefore pass without discriminating -- which is exactly the failure document 26
records, where a prediction cleared its bar and was beaten by a constant.

So the predictions below are about **ordering and magnitude**, where a constant rule has
nothing to say, and each names the naive alternative it must beat.

Stated in advance, so they can fail
-----------------------------------
**P0 -- manipulation check.** The five arms span at least ``MIN_RATE_SPAN`` in selection
rate, every arm clears ``MIN_TEST`` test subjects, and every arm has a baseline parity gap of
at least ``MIN_GAP``. If the purposes do not differ in selection rate, or an arm has nothing
to mitigate, nothing below identifies anything.

**P1 -- the relationship holds on natural data.** Pearson ``r(selection rate, pie change)``
across the five arms is at least ``MIN_R``.
*Naive alternative it must beat:* no relationship, |r| < 0.30. A constant-direction rule
cannot produce a correlation, so this is not a bar a constant can clear.

**P2 -- the ordering holds.** Spearman rank correlation between selection rate and pie change
is at least ``MIN_RHO``.
*Naive alternative:* random ordering, expected rho = 0.

**P3 -- the sharpest single comparison.** The lowest arm (improvement, 0.516) has a smaller
pie change than the highest (refinance, 0.784).
*Naive alternative:* a coin flip between the two.

**Not predicted.** The *sign* at improvement. At 0.516 it sits inside document 23's crossover
band of 0.25-0.60, where the rule explicitly does not determine direction. Claiming a sign
there would be claiming more than the rule supports, and if it comes out negative that is
consistent rather than contradictory -- it is what a crossover means.

If P1 and P2 fail, document 23's relationship does not appear on a natural split and holds
only where the selection rate was moved artificially. That would be a serious finding against
the paper and is to be reported as one.

Run:  python -m src.experiments.analyse_purpose
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

PURPOSES = ["improvement", "other", "cashout", "purchase", "refinance"]
STATES = "MS,LA"

MIN_RATE_SPAN = 0.20    # P0
MIN_TEST = 2500         # P0, document 15's floor
MIN_GAP = 0.05          # P0, document 12's degenerate-arm ground
MIN_R = 0.70            # P1
MIN_RHO = 0.80          # P2

PLAIN, BASE, FLOORED = "expgrad_dp", "baseline", "expgrad_dp_floor"


def arm_dir(purpose: str) -> str:
    return f"hmda_{STATES.lower().replace(',', '_')}_2018_race_{purpose}_levelling_up"


def load(purposes: list[str]) -> pd.DataFrame:
    rows = []
    for purpose in purposes:
        path = RESEARCH_RESULTS_DIR / arm_dir(purpose) / "levelling_up_runs.csv"
        if not path.exists():
            continue
        runs = pd.read_csv(path)
        mean = runs.groupby("arm").mean(numeric_only=True)
        if not {PLAIN, BASE}.issubset(mean.index):
            continue
        n_test = runs[runs.arm == BASE]["n_test"].mean() if "n_test" in runs.columns else np.nan
        rows.append({
            "purpose": purpose,
            "n_test": n_test,
            "positives_base": mean.loc[BASE, "positives"],
            "dp_base": mean.loc[BASE, "dp_diff"],
            "dp_plain": mean.loc[PLAIN, "dp_diff"],
            "pie_plain": mean.loc[PLAIN, "positives_pct_change"],
            "pie_floor": mean.loc[FLOORED, "positives_pct_change"]
            if FLOORED in mean.index else np.nan,
            "exchange_plain": mean.loc[PLAIN, "lost_per_gained"],
        })
    return pd.DataFrame(rows)


def verdict(frame: pd.DataFrame) -> None:
    print(frame.round(4).to_string(index=False))

    span = frame["rate"].max() - frame["rate"].min()
    p0 = (span >= MIN_RATE_SPAN and (frame["n_test"] >= MIN_TEST).all()
          and (frame["dp_base"] >= MIN_GAP).all())
    print(f"\nP0  the purposes differ, and each has something to fix -> "
          f"{'HOLDS' if p0 else 'FAILS'}")
    print(f"      selection rate {frame['rate'].min():.3f} to {frame['rate'].max():.3f} "
          f"(span {span:.3f}, bar {MIN_RATE_SPAN})")
    print(f"      smallest test set {frame['n_test'].min():.0f} (bar {MIN_TEST}); "
          f"smallest parity gap {frame['dp_base'].min():.4f} (bar {MIN_GAP})")

    if len(frame) < 4:
        print("\n  too few arms to correlate; stopping here")
        return

    r = float(np.corrcoef(frame["rate"], frame["pie_plain"])[0, 1])
    p1 = r >= MIN_R
    print(f"\nP1  it holds on a natural split                  -> {'HOLDS' if p1 else 'FAILS'}")
    print(f"      r = {r:+.3f}  (bar {MIN_R}; the naive 'no relationship' alternative is "
          f"|r| < 0.30)")

    rho = float(stats.spearmanr(frame["rate"], frame["pie_plain"]).statistic)
    p2 = rho >= MIN_RHO
    print(f"\nP2  the ordering holds                           -> {'HOLDS' if p2 else 'FAILS'}")
    print(f"      Spearman rho = {rho:+.3f}  (bar {MIN_RHO})")

    lo = frame.loc[frame["rate"].idxmin()]
    hi = frame.loc[frame["rate"].idxmax()]
    p3 = lo["pie_plain"] < hi["pie_plain"]
    print(f"\nP3  lowest arm below highest arm                 -> {'HOLDS' if p3 else 'FAILS'}")
    print(f"      {lo['purpose']} ({lo['rate']:.3f}): {lo['pie_plain']:+.2f}%   vs   "
          f"{hi['purpose']} ({hi['rate']:.3f}): {hi['pie_plain']:+.2f}%")

    print("\n" + "=" * 78)
    if p0 and p1 and p2:
        print("The crossover relationship appears on a natural split of real lending")
        print("decisions, with no cutoff manipulation. Document 23's central weakness -- that")
        print("the transition had only ever been manufactured -- is closed.")
    elif p0 and not (p1 or p2):
        print("The relationship does NOT appear on a natural split. Document 23's result may")
        print("hold only where the selection rate was moved artificially, which is a serious")
        print("finding against the paper and is to be reported as one.")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", nargs="+", default=PURPOSES,
                        help="loan purposes to analyse")
    args = parser.parse_args()

    frame = load(args.dataset)
    if frame.empty:
        print("no purpose arms found; run run_levelling_up with "
              f"--dataset hmda:{STATES}:derived_race:<purpose>")
        return
    frame["rate"] = frame["positives_base"] / frame["n_test"]
    verdict(frame)

    out = research_dir("purpose_sweep")
    frame.to_csv(out / "purpose_sweep.csv", index=False)
    print(f"\nwrote {out}/purpose_sweep.csv")


if __name__ == "__main__":
    main()
