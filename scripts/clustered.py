#!/usr/bin/env python3
"""Every headline ratio, read with the population as the unit rather than the arm.

**Individual work, beyond the course submission.**

`scripts/independence.py` establishes how many disjoint person-samples sit behind each
figure. This does the inference that follows from it: an arm-level accuracy, the same
accuracy with a population counted once, a bootstrap that resamples *populations* so
correlated arms travel together, and a leave-one-population-out worst fold.

Where a figure spans fewer than five person-samples the bootstrap is suppressed rather than
printed: with two clusters there are three distinct resamples, and the interval comes out
narrow because of that, not because the estimate is precise.

Run:  python scripts/clustered.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.skill import cluster_stats                                  # noqa: E402
from scripts.independence import population                          # noqa: E402

R = ROOT / "research" / "results"


def _read(rel: str) -> pd.DataFrame | None:
    p = R / rel
    return pd.read_csv(p) if p.exists() else None


def main() -> None:
    rows = []

    def add(label, frame, correct, pop="population", keep=None):
        if frame is None:
            return
        f = keep(frame) if keep else frame
        if f.empty:
            return
        # Cluster on the PERSON-SAMPLE, not the arm name. Without this, the lending
        # cohort's eight market-by-purpose arms read as eight clusters when they are five
        # markets, and the survey's fifty draws read as fifty when two state-years were
        # drawn under both attributes.
        s = cluster_stats(correct(f), f[pop].astype(str).map(population))
        rows.append({
            "figure": label, "arms": f"{s.arms_correct}/{s.arms}",
            "arm_acc": s.arms_correct / s.arms,
            "pops": f"{s.populations_correct}/{s.populations}",
            "cluster_lo": s.lo if s.interval_is_interpretable else None,
            "cluster_hi": s.hi if s.interval_is_interpretable else None,
            "lopo_worst": s.lopo_min,
        })
        print(f"  {label:<34} {s.line()}")

    print("headline ratios, population-clustered:\n")
    add("re-seal, unrefined rule", _read("resealed/resealed.csv"),
        lambda d: d["predicted"] == d["actual"])
    add("seal 1, refined rule", _read("sealed/sealed.csv"),
        lambda d: d["predicted"] == d["actual"], keep=lambda d: d[d["held_out"]])
    add("third direction cohort", _read("third_direction/third_direction.csv"),
        lambda d: d["predicted"] == d["actual"], keep=lambda d: d[~d["indeterminate"]])
    add("sealed lending cohort", _read("lending_direction/lending_direction.csv"),
        lambda d: d["predicted"] == d["actual"], keep=lambda d: d[~d["indeterminate"]])
    add("race cohort S1, rate rule", _read("ipums_sealed/race_s1.csv"),
        lambda d: d["rule"].astype(bool))
    add("race cohort S1, cutoff null", _read("ipums_sealed/race_s1.csv"),
        lambda d: d["null_cutoff"].astype(bool))

    a, b = (_read("third_direction/third_direction.csv"),
            _read("lending_direction/lending_direction.csv"))
    if a is not None and b is not None:
        both = pd.concat([a, b])
        add("effect-size, above 1 pt", both[~both["indeterminate"]],
            lambda d: d["predicted"] == d["actual"])
        add("effect-size, below 1 pt", both[both["indeterminate"]],
            lambda d: d["predicted"] == d["actual"])

    s = _read("survey/survey_verdicts.csv")
    add("landscape survey, directional", s,
        lambda d: d["verdict"].str.startswith(("CLASSIC", "MONOTONE")))

    out = R / "independence"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).round(4).to_csv(out / "clustered.csv", index=False)
    print(f"\nwrote {out}/clustered.csv")
    print("\nCI suppressed where a figure spans fewer than five person-samples: a bootstrap")
    print("over two clusters has three distinct resamples and its narrowness is an artefact.")


if __name__ == "__main__":
    main()
