"""Separate group ratio from population size, by pooling two protected attributes.

**Written and committed before the race-arm results existed.** The point of this module
is to fix the analysis while the answer is still unknown, because the analysis it
replaces already produced one confident and wrong reading of the same data (docs/11,
"A correction worth recording"), and the failure mode there was choosing what to
correlate after seeing what correlated.

The problem it addresses
------------------------
P1 claims the rate-to-people conversion is population arithmetic. On the sex arm it
fails in a pattern that admits two readings which that arm cannot tell apart:

* the formula degrades as the two groups become more **unequal in size**; or
* the formula degrades as the population gets **smaller**, because small samples make
  the mitigation jitter and produce cross-flows the formula has no term for.

Across the ten sex-arm populations these two quantities correlate at **r = +0.794**
(Adult is both the largest and the most lopsided), so neither correlation with the error
is interpretable on its own. This is not a subtle statistical point -- reading the nine
states without Adult reversed the sign of the ratio correlation, from +0.366 to -0.587.

The design
----------
Protecting ``RAC1P`` on the same nine states spans a group ratio of 1.94 to 24.98 with
the confound **inverted**: r(ratio, n) = -0.567 there, because the racially homogeneous
states are also the small ones. Pooling the arms should therefore drive the confound
toward zero and leave nineteen populations in which ratio and size vary independently.

Stated in advance, so they can fail
-----------------------------------
**A1 -- the confound breaks under pooling.** |r(ratio, n)| < 0.3 over the pooled
populations. If this fails, nothing else here is interpretable either and the module
should say so rather than proceed.

**A2 -- size survives, ratio does not.** Controlling for size, the partial correlation
between group ratio and the formula's error is near zero; controlling for ratio, the
partial correlation with size stays clearly negative. This is the prediction that
follows from docs/11's restatement, in which cross-flow is the mechanism and ratio is a
passenger.

**A3 -- cross-flow remains the strongest single predictor** in both arms separately, not
only pooled. A mechanism that only appears after pooling is a mechanism fitted to the
pooled data.

If A2 fails and ratio survives instead, docs/11's restatement of P1 is wrong and the
original group-size reading was right after all. That outcome is why this is worth
running.

Usage:
    python -m src.experiments.analyse_arms
    python -m src.experiments.analyse_arms --states VT NM MS WV WY ND UT AL OR
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESULTS_DIR
from .analyse_sweep import DEFAULT_STATES, SEX_ARM, correlate, load_population, test_p1

RACE_ARM = "RAC1P"

# A1's threshold, and the "near zero" of A2. Chosen because at |r| = 0.3 the shared
# variance is under 10%, which is the point at which the two quantities can be read as
# varying independently enough for a partial correlation to mean something. Fixed here
# rather than after seeing the data.
CONFOUND_CEILING = 0.3

# An arm reporting fewer populations than this is a sweep still running, not a result.
# Without this the module happily produced a verdict from two of nine race populations,
# which is the exact failure it was written to prevent: an analysis that answers before
# the data supports an answer is worse than no analysis, because it looks like one.
MIN_POPULATIONS_PER_ARM = 8


def partial_correlation(frame: pd.DataFrame, x: str, y: str, control: str) -> float:
    """Correlation between x and y with the linear effect of `control` removed.

    This is the whole point of building a second arm: with ratio and size decorrelated,
    the partial correlations answer "does ratio predict the error *among populations of
    similar size*", which is the question the sex arm could not pose.
    """
    columns = [x, y, control]
    data = frame[columns].astype(float).dropna()
    if len(data) < 4:
        return float("nan")
    r_xy = np.corrcoef(data[x], data[y])[0, 1]
    r_xc = np.corrcoef(data[x], data[control])[0, 1]
    r_yc = np.corrcoef(data[y], data[control])[0, 1]
    denominator = np.sqrt((1 - r_xc**2) * (1 - r_yc**2))
    return float((r_xy - r_xc * r_yc) / denominator) if denominator else float("nan")


def arm_table(states: list[str], arm: str) -> pd.DataFrame | None:
    """Per-population P1 fit for one protected attribute."""
    suffix = "" if arm == SEX_ARM else f":{arm}"
    populations = [("adult", "Adult")] if arm == SEX_ARM else []
    populations += [(f"acs:{s}{suffix}", s) for s in states]

    frames = []
    for key, label in populations:
        frame = load_population(key, label)
        if frame is None:
            print(f"  skipped {label} [{arm}]: no who-pays results")
            continue
        frames.append(frame)
    if not frames:
        return None

    table = test_p1(pd.concat(frames, ignore_index=True)).reset_index()
    table["arm"] = arm
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=DEFAULT_STATES)
    args = parser.parse_args()

    tables = [t for t in (arm_table(args.states, arm)
                          for arm in (SEX_ARM, RACE_ARM)) if t is not None]
    if len(tables) < 2:
        raise SystemExit("both arms are needed; run run_who_pays on the missing one")

    short = [(t["arm"].iat[0], len(t)) for t in tables if len(t) < MIN_POPULATIONS_PER_ARM]
    if short:
        raise SystemExit(
            "refusing to report: "
            + "; ".join(f"{arm} arm has {n} populations, needs "
                        f"{MIN_POPULATIONS_PER_ARM}" for arm, n in short)
            + "\nthe sweep is incomplete -- a verdict from a partial arm is not a verdict"
        )

    pooled = pd.concat(tables, ignore_index=True)
    pooled["log_ratio"] = np.log(pooled["group_ratio"])

    print("=" * 78)
    print("Per-arm P1 fit")
    print("=" * 78)
    for arm, group in pooled.groupby("arm", sort=False):
        print(f"\n[{arm}]  {len(group)} populations")
        print(group.set_index("population")[
            ["n", "group_ratio", "cross_flow", "mean_abs_error"]
        ].round(4).to_string())
        r_conf, _ = correlate(group, "group_ratio", "n")
        r_flow, _ = correlate(group, "cross_flow", "mean_abs_error")
        print(f"  r(ratio, n) within arm        = {r_conf:+.3f}")
        print(f"  r(cross-flow, error) within arm = {r_flow:+.3f}   [A3]")

    print()
    print("=" * 78)
    print(f"A1  pooling breaks the confound   (target |r| < {CONFOUND_CEILING})")
    print("=" * 78)
    # Ratio is compared on a log scale as well: it spans 1.02 to 24.98, so a Pearson
    # correlation on the raw value is dominated by the two most lopsided populations.
    r_conf, _ = correlate(pooled, "group_ratio", "n")
    r_conf_log, _ = correlate(pooled, "log_ratio", "n")
    print(f"  pooled r(group_ratio, n)     = {r_conf:+.3f}")
    print(f"  pooled r(log group_ratio, n) = {r_conf_log:+.3f}")
    broken = abs(r_conf_log) < CONFOUND_CEILING
    print(f"  -> A1 {'HOLDS' if broken else 'FAILS'}: ratio and size "
          f"{'vary independently enough to be separated' if broken else 'remain confounded'}")
    if not broken:
        print("     The partial correlations below are NOT interpretable. Reported for")
        print("     completeness only; do not draw a mechanism from them.")

    print()
    print("=" * 78)
    print("A2  size survives, ratio does not")
    print("=" * 78)
    r_ratio, _ = correlate(pooled, "log_ratio", "mean_abs_error")
    r_size, _ = correlate(pooled, "n", "mean_abs_error")
    r_flow, _ = correlate(pooled, "cross_flow", "mean_abs_error")
    p_ratio = partial_correlation(pooled, "log_ratio", "mean_abs_error", "n")
    p_size = partial_correlation(pooled, "n", "mean_abs_error", "log_ratio")
    print(f"  {'':28}{'raw':>8}{'partial':>10}")
    print(f"  {'log group ratio vs error':28}{r_ratio:>+8.3f}{p_ratio:>+10.3f}"
          f"   (controlling for size)")
    print(f"  {'population size vs error':28}{r_size:>+8.3f}{p_size:>+10.3f}"
          f"   (controlling for ratio)")
    print(f"  {'cross-flow vs error':28}{r_flow:>+8.3f}{'--':>10}")
    # A2 as stated requires two things: ratio's partial near zero AND size's clearly
    # negative. "size beats ratio" is a weaker claim and would have been scored as a
    # pass with ratio sitting at +0.47, so it is not the test.
    ratio_dies = abs(p_ratio) < CONFOUND_CEILING
    size_lives = p_size < -CONFOUND_CEILING
    if ratio_dies and size_lives:
        verdict = ("A2 HOLDS: size predicts the error; ratio does not, once size is "
                   "held fixed")
    elif size_lives:
        verdict = (f"A2 PARTIAL: size survives (partial {p_size:+.3f}) but ratio does "
                   f"not vanish (partial {p_ratio:+.3f}, needed |r| < "
                   f"{CONFOUND_CEILING}). Both quantities carry signal; docs/11's "
                   f"restatement is incomplete rather than wrong")
    elif ratio_dies:
        verdict = (f"A2 FAILS: ratio vanishes but size does not survive either "
                   f"(partial {p_size:+.3f}). Neither is the driver; look to cross-flow "
                   f"directly")
    else:
        verdict = (f"A2 FAILS: ratio predicts the error independently of size "
                   f"(partial {p_ratio:+.3f}) -- docs/11's restatement of P1 is wrong "
                   f"and the group-size reading was right")
    print(f"  -> {verdict}")

    out = RESULTS_DIR / "sweep"
    out.mkdir(parents=True, exist_ok=True)
    pooled.to_csv(out / "arms_p1_pooled.csv", index=False)
    print(f"\nwrote {out}/arms_p1_pooled.csv")


if __name__ == "__main__":
    main()
