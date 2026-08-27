"""What the selection-rate floor buys, on the branch the audit sends it to.

**Individual work, beyond the course submission. Post-hoc accounting, labelled as such.**

The floor is the paper's practical recommendation and, until now, its least-evidenced claim:
a single sentence in the Discussion asserting "about 0.12 accuracy points" and an exchange
rate moving "from 1.47 to 0.88", with no table, no method and no denominator a reader could
check. Two referees said so independently. This module supplies the measurement.

Two decisions about what to measure, both of which change the answer:

* **Natural arms only.** Every stored population carries a floor variant --- 1,400 arms ---
  but most are operating-point sweeps at rates no deployer occupies. A team applies the floor
  at its own operating point, so that is where the cost should be read.
* **Only where the constraint withdraws.** Algorithm 1 sends the floor to the
  \\textsc{withdrawal} branch. Averaging over arms it extends flatters the remedy by mixing
  in cases it was never prescribed for.

Applying the audit's own noise and parity gates then leaves 86 arms over 70 populations.

One quantity is deliberately *not* reported. Earlier versions related the floor's benefit to
the damage it repairs at ``r = -0.99``. The benefit is the damage minus what remains, so the
two share a term and the correlation is arithmetic. It is withdrawn rather than restated.

Run:  python -m src.experiments.analyse_floor
      python -m src.experiments.analyse_floor --dataset acs_income_sc_2018
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

BASE, PLAIN, FLOOR = "baseline", "expgrad_dp", "expgrad_dp_floor"

# The audit's own gates, in value, so the floor is measured on arms the audit would accept.
NOISE_FLOOR = 2500
GAP_FLOOR = 0.05


def load(prefix: str | None = None) -> pd.DataFrame:
    sys.path.insert(0, str(RESEARCH_RESULTS_DIR.parents[1]))
    from scripts.independence import population

    rows = []
    for directory in sorted(RESEARCH_RESULTS_DIR.glob("*_levelling_up")):
        if prefix and not directory.name.startswith(prefix):
            continue
        path = directory / "levelling_up_runs.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if not {BASE, PLAIN, FLOOR}.issubset(set(frame.arm.unique())):
            continue
        if "n_test" not in frame.columns:
            continue
        base = frame[frame.arm == BASE]
        if float(base.n_test.mean()) < NOISE_FLOOR:
            continue
        if abs(float(base.dp_diff.mean())) < GAP_FLOOR:
            continue
        plain, floored = frame[frame.arm == PLAIN], frame[frame.arm == FLOOR]
        rows.append({
            "population": population(directory.name),
            "acc_plain": float(plain.accuracy.mean()),
            "acc_floor": float(floored.accuracy.mean()),
            "exchange_plain": float(plain.lost_per_gained.mean()),
            "exchange_floor": float(floored.lost_per_gained.mean()),
            "pool_plain": float(plain.positives_pct_change.mean()),
            "pool_floor": float(floored.positives_pct_change.mean()),
        })
    return pd.DataFrame(rows).dropna()


def withdrawing(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[frame.pool_plain < 0]


def summarise(frame: pd.DataFrame) -> dict:
    return {
        "arms": len(frame),
        "populations": int(frame.population.nunique()),
        "exchange_plain": float(frame.exchange_plain.median()),
        "exchange_floor": float(frame.exchange_floor.median()),
        "below_one_floor": int((frame.exchange_floor < 1.0).sum()),
        "below_one_plain": int((frame.exchange_plain < 1.0).sum()),
        "pool_plain": float(frame.pool_plain.median()),
        "pool_floor": float(frame.pool_floor.median()),
        "accuracy_cost": float((frame.acc_plain - frame.acc_floor).mean() * 100),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", default=None, help="restrict to one population stem")
    args = ap.parse_args()

    arms = load(args.dataset)
    w = withdrawing(arms)
    print(f"Natural arms clearing both audit gates: {len(arms)} over "
          f"{arms.population.nunique()} populations")
    print(f"Of those, the plain constraint withdraws on {len(w)} over "
          f"{w.population.nunique()} populations --- the branch the floor is prescribed for\n")
    s = summarise(w)
    print(f"  exchange rate      {s['exchange_plain']:.2f} -> {s['exchange_floor']:.2f}  (median)")
    print(f"  at or below 1.0    {s['below_one_plain']} of {s['arms']} -> "
          f"{s['below_one_floor']} of {s['arms']}")
    print(f"  change in the pool {s['pool_plain']:+.2f}% -> {s['pool_floor']:+.2f}%  (median)")
    print(f"  accuracy cost      {s['accuracy_cost']:.2f} points (mean)")
    print("\n  Not reported, deliberately: the benefit-against-damage correlation. The benefit")
    print("  is the damage minus the remainder, so the two share a term and any correlation")
    print("  between them is arithmetic rather than a finding.")

    out = research_dir("floor")
    arms.to_csv(out / "arms.csv", index=False)
    pd.DataFrame([s]).to_csv(out / "summary.csv", index=False)
    print(f"\nwrote {out}/arms.csv and {out}/summary.csv")


if __name__ == "__main__":
    main()
