"""Can we predict how much, and is 0.55 a defensible prior for where?

**Individual work, beyond the course submission.**

**Written before either analysis was run**, and committed before them. Both use arms already
on disk — no new compute — which makes the pre-registration *more* important rather than less:
the data exists, so nothing but a committed prediction stops the model being fitted to it.

---------------------------------------------------------------------------
M -- magnitude, which the paper concedes without ever having tried
---------------------------------------------------------------------------
The paper says the selection rate predicts **which way** a constraint moves the pool and not
**how much**. That is true of everything measured: four manipulations preserve direction while
changing size three- to eight-fold.

But it was never *attempted*. "We tried to predict the magnitude and could not" is a far
stronger concession than "we did not try", and a referee is entitled to ask why not.

The obvious model, and the one a practitioner would guess: **the further a task sits from its
own crossover, the larger the effect.** An arm just below the crossover should barely move the
pool; an arm far below it should shed decisions heavily.

**M1 -- within populations.** In each population with a located crossover, the *signed*
distance from the crossover predicts the pie change: Spearman rho >= ``MIN_RHO``. Scored as
the fraction of populations in which it holds; it must hold in **more than half** to count.

**M2 -- across populations, the harder half.** Pooling every retained arm from every
population, the pie change is predicted by the signed distance from that population's own
crossover at ``r >= MIN_R``. This asks whether **one slope** fits every domain, which is what
"predicting the magnitude" would actually require.

**M3 -- does the group gap add anything?** The baseline parity gap is the other quantity a
practitioner has. Adding it to M2's predictor should raise the correlation by at least
``MIN_GAIN`` to be worth reporting; otherwise it is noise and is dropped.

**The naive alternative, named in advance:** *"magnitude is not predictable from anything we
have"* -- |r| < ``MIN_NAIVE`` in M2. **This is the outcome the paper currently assumes**, and
it is entirely possible: the magnitude varies three- to eight-fold under manipulations that
leave the distance from the crossover untouched, which is direct evidence against M2 before it
is run. If the naive alternative wins, the concession stands and is *earned*.

---------------------------------------------------------------------------
C -- is "expect about 0.55" a defensible prior, or a coincidence of four points?
---------------------------------------------------------------------------
[Document 42](../../research/docs/42-denser-sweeps-and-where-the-crossover-sits.md) found four
populations across three domains and two countries agreeing on the crossover to within 0.08.
Document 32 had called the crossover "population-specific". Both cannot be right.

**C1 -- do they cluster?** The standard deviation of non-lending crossover mid-points is below
``MAX_SD``. If it is, "expect roughly 0.55 and check" is a defensible instruction; if not,
document 32's original wording was right and document 42 over-read four points.

**C2 -- is the residual explained by anything?** Across populations, the crossover mid-point
is correlated against base rate, between-group gap and test-set size. **No prediction is made
about the direction of any of these**; the question is whether any |r| exceeds ``MIN_R``, which
would turn the prior into a formula. With so few populations this is a screen, not a model, and
it is reported as one.

**C3 -- does lending separate?** The lending mid-points sit above every non-lending one. That
observation comes from a single mortgage market measured three overlapping ways, so C3 asks
only whether the separation is clean, and the answer cannot establish that *lending* is
different -- only that this market is.

Run:  python -m src.experiments.analyse_magnitude --mode magnitude
      python -m src.experiments.analyse_magnitude --mode crossover
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

from ..results_io import research_dir
from .analyse_calibration import apply_rules, majority_baseline
from .analyse_operating_point import crossover_bracket, load_points_for
from .analyse_threshold import MIN_R
from .viable_points import points_for

# M1: rank correlation within a population.
MIN_RHO = 0.70

# M3: the parity gap must buy at least this much to be worth carrying.
MIN_GAIN = 0.10

# The bar the naive "magnitude is unpredictable" alternative has to clear to lose.
MIN_NAIVE = 0.30

# C1: below this spread, "expect about 0.55" is a defensible instruction.
MAX_SD = 0.05

SWEPT = ["acs:AL", "acs:KY", "acs:SC", "acs:OR", "dutch", "compas"]


def collect() -> pd.DataFrame:
    """Every retained arm from every densely swept population, with its own crossover."""
    frames = []
    for spec in SWEPT:
        info = points_for(spec)
        kept, _ = apply_rules(load_points_for(info["dataset"], info["points"]),
                              majority_baseline(spec))
        if len(kept) < 3:
            continue
        band = crossover_bracket(kept)
        kept = kept.copy()
        kept["population"] = info["dataset"]
        kept["crossover"] = np.nan if band is None else (band[0] + band[1]) / 2
        frames.append(kept)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def magnitude_mode() -> dict:
    arms = collect()
    located = arms.dropna(subset=["crossover"]).copy()
    located["distance"] = located["selection_rate"] - located["crossover"]

    print(f"{len(arms)} retained arms; {len(located)} in populations with a located crossover "
          f"({located['population'].nunique()} populations)")

    held = {}
    for name, rows in located.groupby("population"):
        if len(rows) < 4:
            continue
        rho = float(stats.spearmanr(rows["distance"], rows["pie"]).statistic)
        held[str(name)] = rho
        print(f"    {name:22} rho = {rho:+.3f}  ({len(rows)} arms)")
    passing = sum(1 for r in held.values() if r >= MIN_RHO)
    m1 = passing > len(held) / 2
    print(f"\nM1  signed distance orders the pie change within a population: "
          f"{passing}/{len(held)}  {'HOLDS' if m1 else 'FAILS'}")

    r2 = float(np.corrcoef(located["distance"], located["pie"])[0, 1])
    m2 = r2 >= MIN_R
    print(f"M2  one slope across every population: r = {r2:+.3f} (bar {MIN_R})  "
          f"{'HOLDS' if m2 else 'FAILS'}")
    print(f"    naive 'magnitude is unpredictable' alternative "
          f"{'BEATEN' if r2 >= MIN_NAIVE else 'WINS'} at {MIN_NAIVE}")

    # M3: does the parity gap add anything to the signed distance?
    both = np.column_stack([located["distance"], located["dp_base"]])
    coefficients, *_ = np.linalg.lstsq(
        np.column_stack([both, np.ones(len(both))]), located["pie"], rcond=None)
    fitted = np.column_stack([both, np.ones(len(both))]) @ coefficients
    r3 = float(np.corrcoef(fitted, located["pie"])[0, 1])
    gain = r3 - abs(r2)
    print(f"M3  adding the baseline parity gap: r = {r3:+.3f}, gain {gain:+.3f} "
          f"(bar {MIN_GAIN})  {'WORTH CARRYING' if gain >= MIN_GAIN else 'dropped as noise'}")

    return {"m1": m1, "m1_passing": passing, "m1_total": len(held), "r_distance": r2,
            "m2": m2, "r_with_gap": r3, "gain": gain,
            "naive_beaten": bool(r2 >= MIN_NAIVE), "n_arms": len(located)}


def crossover_mode() -> dict:
    from ..datasets import build as build_dataset

    rows = []
    for spec in SWEPT:
        info = points_for(spec)
        kept, _ = apply_rules(load_points_for(info["dataset"], info["points"]),
                              majority_baseline(spec))
        band = crossover_bracket(kept) if len(kept) >= 3 else None
        if band is None:
            continue
        dataset = build_dataset(spec).load()
        base_rates = dataset.base_rates().set_index("group")["P(y=1)"]
        rows.append({
            "population": info["dataset"],
            "crossover": (band[0] + band[1]) / 2,
            "base_rate": float(dataset.y.mean()),
            "group_gap": float(base_rates["privileged"] - base_rates["unprivileged"]),
            "n": int(dataset.n_samples),
            "lending": info["dataset"].startswith("hmda"),
        })
    frame = pd.DataFrame(rows)
    print(frame.round(4).to_string(index=False))

    non_lending = frame[~frame["lending"]]
    sd = float(non_lending["crossover"].std())
    c1 = sd < MAX_SD
    print(f"\nC1  spread of non-lending crossovers: sd = {sd:.4f} (bar {MAX_SD})  "
          f"{'CLUSTERS' if c1 else 'DOES NOT CLUSTER'}")
    print(f"    range {non_lending['crossover'].min():.3f}-"
          f"{non_lending['crossover'].max():.3f}, mean {non_lending['crossover'].mean():.3f}")

    result = {"c1": c1, "sd": sd, "mean": float(non_lending["crossover"].mean()),
              "n_populations": len(non_lending)}
    print("\nC2  is the residual explained by anything? (screen, not a model)")
    for column in ["base_rate", "group_gap", "n"]:
        if len(non_lending) < 4:
            continue
        r = float(np.corrcoef(non_lending[column], non_lending["crossover"])[0, 1])
        print(f"    crossover vs {column:12} r = {r:+.3f}  "
              f"{'-> worth modelling' if abs(r) >= MIN_R else ''}")
        result[f"r_{column}"] = r
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["magnitude", "crossover"], default="magnitude")
    args = parser.parse_args()

    result = magnitude_mode() if args.mode == "magnitude" else crossover_mode()
    OUT = research_dir("magnitude")
    pd.Series(result).to_csv(OUT / f"{args.mode}.csv", header=False)
    print(f"\nwrote {OUT}/{args.mode}.csv")


if __name__ == "__main__":
    main()
