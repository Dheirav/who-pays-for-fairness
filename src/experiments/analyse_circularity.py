"""What does the sweep buy that one fit does not? The circularity objection, measured.

**Individual work, beyond the course submission. Post-hoc accounting, labelled as such.**

The sharpest objection raised against this paper so far, and the one it had been
asserting an answer to rather than showing one:

    Locating a crossover requires sweeping the constraint across operating points. A
    team that can afford that sweep could instead fit the constrained model once, at
    the operating point it actually uses, and read the pool change directly. What has
    prediction bought over measurement?

The objection is correct that a single fit answers the question it asks. It is wrong
that the question a single fit answers is the one a deploying team has. A single fit
returns a *point*: what this constraint did, at this threshold, on this run. The sweep
returns a *neighbourhood*: whether that point is stable, whether it is near a sign
change, and whether the population admits a stable sign at all. Three measurements
separate them, and this module runs all three over every stored sweep.

* ``--locality``  How far does one fit's answer travel? For each adjacent pair of arms
  in a sweep, both above the paper's own 1.0-point magnitude floor, does the sign at
  one hold at the other? A single fit implicitly claims it does.
* ``--distance``  How close do populations sit to their own boundary? For every
  population with both a located crossover and a natural arm, the gap between the two.
  Where that gap is small, the difference between a constraint that withdraws and one
  that extends is a threshold move the team already controls --- and one fit reports
  the withdrawal without reporting the lever.
* ``--stability``  Where is a single fit's sign unreliable on its own terms? Seed
  agreement on the sign, binned by distance from the crossover. This is the weakest of
  the three and is reported as such: repeated fits at one operating point would also
  expose it, so it is not something only a sweep can see.

The honest summary the module prints: the sweep's value is *shape*, not precision.

Run:  python -m src.experiments.analyse_circularity
      python -m src.experiments.analyse_circularity --locality
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR

# The paper's own independence rule, so this module cannot quietly count an attribute
# arm as a second population while the rest of the paper counts it as one.
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from scripts.independence import population  # noqa: E402

BASE, PLAIN = "baseline", "expgrad_dp"

# Document 52's noise floor and the paper's own magnitude floor, both reused rather than
# re-chosen: a module written to answer an objection must not get to pick new guards.
NOISE_FLOOR = 2500
MIN_MAGNITUDE = 1.0
MIN_ARMS = 4
SEEDS = 5

_OP = re.compile(r"^(.*_levelling_up)_op([\d]+)$")


def _knob(raw: str) -> float:
    """``op0305`` is 0.305 and ``op03`` is 0.3; the leading zero is the decimal point."""
    return float("0." + raw[1:]) if raw.startswith("0") else float(raw)


def load_sweeps() -> dict[str, pd.DataFrame]:
    """Every stored operating-point family with enough arms and seeds to read a shape."""
    fam: dict[str, dict[float, pathlib.Path]] = collections.defaultdict(dict)
    for d in RESEARCH_RESULTS_DIR.iterdir():
        m = _OP.match(d.name)
        if m and (d / "levelling_up_runs.csv").exists():
            fam[m.group(1)][_knob(m.group(2))] = d

    sweeps = {}
    for pop, arms in fam.items():
        rows = []
        for _, d in sorted(arms.items()):
            df = pd.read_csv(d / "levelling_up_runs.csv")
            base, plain = df[df.arm == BASE], df[df.arm == PLAIN]
            if base.empty or plain.empty or "n_test" not in df.columns:
                continue
            per_seed = plain.set_index("seed")["positives_pct_change"].dropna()
            if len(per_seed) < SEEDS:
                continue
            # Take the first five wherever an arm was later deepened, so that every
            # population contributes the same seed budget to the agreement counts.
            per_seed = per_seed.loc[sorted(per_seed.index)[:SEEDS]]
            rows.append({
                "rate": float((base["positives"] / base["n_test"]).mean()),
                "n_test": float(base["n_test"].mean()),
                "pie": float(per_seed.mean()),
                "seeds": per_seed.to_numpy(),
            })
        if len(rows) >= MIN_ARMS:
            frame = pd.DataFrame(rows).sort_values("rate").reset_index(drop=True)
            if frame["n_test"].mean() >= NOISE_FLOOR:
                sweeps[pop] = frame
    return sweeps


def crossover(frame: pd.DataFrame) -> float:
    """Midpoint of the bracket, on the definition of ``analyse_operating_point``."""
    below, above = frame[frame.pie < 0]["rate"], frame[frame.pie > 0]["rate"]
    if below.empty or above.empty or below.max() >= above.min():
        return float("nan")
    return float((below.max() + above.min()) / 2)


def natural_rate(pop: str) -> float:
    path = RESEARCH_RESULTS_DIR / pop / "levelling_up_runs.csv"
    if not path.exists():
        return float("nan")
    df = pd.read_csv(path)
    base = df[df.arm == BASE]
    if base.empty or "n_test" not in df.columns:
        return float("nan")
    return float((base["positives"] / base["n_test"]).mean())


def locality(sweeps: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Adjacent-arm sign agreement: does one fit's answer hold one step away?"""
    rows = []
    for pop, f in sweeps.items():
        for i in range(len(f) - 1):
            a, b = f.iloc[i], f.iloc[i + 1]
            if min(abs(a.pie), abs(b.pie)) < MIN_MAGNITUDE:
                continue
            rows.append({"pop": pop, "moved": b.rate - a.rate,
                         "flipped": np.sign(a.pie) != np.sign(b.pie)})
    return pd.DataFrame(rows)


def distances(sweeps: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for pop, f in sweeps.items():
        c, nat = crossover(f), natural_rate(pop)
        if c == c and nat == nat:
            rows.append({"pop": pop, "natural": nat, "crossover": c, "gap": nat - c})
    frame = pd.DataFrame(rows)
    frame["sample"] = frame["pop"].map(population)
    return frame.sort_values("gap", key=abs).reset_index(drop=True)


def stability(sweeps: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for pop, f in sweeps.items():
        c = crossover(f)
        if c != c:
            continue
        for r in f.to_dict("records"):
            s = r["seeds"]
            rows.append({"pop": pop, "rate": r["rate"], "pie": r["pie"],
                         "dist": abs(r["rate"] - c),
                         "unanimous": bool(max((s > 0).sum(), (s < 0).sum()) == SEEDS)})
    return pd.DataFrame(rows)


def _bands(frame: pd.DataFrame, col: str) -> pd.Series:
    return pd.cut(frame[col], [0, 0.05, 0.10, 0.20, 1.0],
                  labels=["<0.05", "0.05-0.10", "0.10-0.20", ">0.20"])


def report_locality(sweeps) -> None:
    g = locality(sweeps)
    print("\nHOW FAR ONE FIT'S ANSWER TRAVELS")
    print("Adjacent arms of a sweep, both above the 1.0-point floor: does the sign hold?")
    print(f"\n  {'rate moved by':<16}{'pairs':>7}{'sign flipped':>15}")
    g = g.assign(band=_bands(g, "moved"))
    for b, s in g.groupby("band", observed=True):
        print(f"  {str(b):<16}{len(s):>7}{s.flipped.mean():>14.0%}")
    print(f"  {'-'*36}")
    print(f"  {'any move':<16}{len(g):>7}{g.flipped.mean():>14.0%}")
    print(f"\n  {g.flipped.sum()} of {len(g)} adjacent pairs disagree on the sign. A single")
    print("  fit asserts its answer holds at the operating point next door; here it")
    print(f"  fails to {g.flipped.mean():.0%} of the time, on effects large enough to read.")
    print("\n  Caveat, and it cuts against the headline: these sweeps were densified")
    print("  around located crossovers, so the narrow-gap bins oversample the boundary")
    print("  and the per-band rates are not a random sample of threshold moves.")


def report_distance(sweeps) -> None:
    d = distances(sweeps)
    # One row per disjoint person sample: where a state contributes a sex arm and a race
    # arm, the two are one population read two ways, and the nearer gap is the one that
    # matters to the claim being made -- so taking the minimum is the generous reading and
    # is labelled as such rather than presented as neutral.
    per_sample = d.loc[d.gap.abs().groupby(d["sample"]).idxmin()]
    print("\n\nHOW CLOSE POPULATIONS SIT TO THEIR OWN BOUNDARY")
    print(f"Arms with both a located crossover and a natural arm: {len(d)}, "
          f"from {d['sample'].nunique()} disjoint person samples")
    print()
    for lim in (0.05, 0.10, 0.15, 0.20):
        n = int((per_sample.gap.abs() <= lim).sum())
        m = int((d.gap.abs() <= lim).sum())
        print(f"  within {lim:.2f} of its own crossover: "
              f"{n:>2} of {len(per_sample)} samples ({n/len(per_sample):.0%})"
              f"   [{m} of {len(d)} arms]")
    print("\n  Where that gap is small the constraint's direction is not a fact about")
    print("  the population alone but about the threshold the team chose, and the team")
    print("  can move it. One fit reports the withdrawal and stops; the sweep reports")
    print("  the withdrawal and the distance to the sign change.\n")
    show = d.assign(pop=d["pop"].str.replace("_levelling_up", "", regex=False).str[:38])
    print(show[["pop", "natural", "crossover", "gap"]]
          .to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
    dup = d[d.duplicated("sample", keep=False)].sort_values("sample")
    if not dup.empty:
        print("\n  Same person sample, two protected attributes, two crossovers --- the")
        print("  boundary is a property of a (population, attribute) pair, not a state:")
        for s, sub in dup.groupby("sample"):
            xs = ", ".join(f"{v:+.3f}" for v in sub.crossover)
            print(f"    {s:<34} {xs}")


def report_stability(sweeps) -> None:
    s = stability(sweeps)
    s = s[s.dist.notna()].assign(band=_bands(s[s.dist.notna()], "dist"))
    print("\n\nWHERE ONE FIT'S SIGN IS UNRELIABLE ON ITS OWN TERMS")
    print("Seed agreement, by distance from the population's crossover.")
    print(f"\n  {'distance':<12}{'arms':>6}{'all 5 agree':>14}{'mean |pool %|':>15}")
    for b, sub in s.groupby("band", observed=True):
        print(f"  {str(b):<12}{len(sub):>6}{sub.unanimous.mean():>13.0%}"
              f"{sub.pie.abs().mean():>15.2f}")
    small = s[s.pie.abs() < MIN_MAGNITUDE]
    print(f"\n  Sub-{MIN_MAGNITUDE}-point arms: {len(small)}, unanimous on the sign "
          f"{small.unanimous.mean():.0%} of the time.")
    print("\n  Stated as the weakest of the three: repeated fits at one operating point")
    print("  would expose this too, and the magnitude floor predicts it about as well as")
    print("  the distance does. It is a reason to distrust one fit, not a thing only a")
    print("  sweep can see. The first two measurements are the answer to the objection.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--locality", action="store_true")
    ap.add_argument("--distance", action="store_true")
    ap.add_argument("--stability", action="store_true")
    ap.add_argument("--dataset", default=None,
                    help="restrict to populations whose results stem contains this, e.g. "
                         "acs_income_fl_2018. The headline figures are the unrestricted "
                         "run; a filtered one is for inspecting a single population.")
    args = ap.parse_args()
    every = not (args.locality or args.distance or args.stability)

    sweeps = load_sweeps()
    if args.dataset:
        sweeps = {k: v for k, v in sweeps.items() if args.dataset in k}
        if not sweeps:
            raise SystemExit(f"no stored sweep matches {args.dataset!r}")
        print(f"Restricted to {args.dataset!r}: {len(sweeps)} population(s). The figures "
              f"below are NOT the paper's, which quote the unrestricted run.")
    print(f"Populations with a usable sweep: {len(sweeps)} "
          f"(>= {MIN_ARMS} arms, {SEEDS} seeds, test split >= {NOISE_FLOOR})")

    if every or args.locality:
        report_locality(sweeps)
    if every or args.distance:
        report_distance(sweeps)
    if every or args.stability:
        report_stability(sweeps)


if __name__ == "__main__":
    main()
