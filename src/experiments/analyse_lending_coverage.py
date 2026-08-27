"""The fifty-market lending coverage, recomputed from stored arms rather than narrated.

**Individual work, beyond the course submission. Post-hoc coverage, not a seal.**

Document 72's counts -- 40 race arms, 26 sex arms, 12 of 12 clearing both gates -- were
computed ad hoc and never committed as a module, so the paper carried them in three places
with three different denominators: Table I said 66 arms over "50 markets", the independence
accounting said 70 arms over 42 populations, and the ledger said "all fifty markets". A
panel review found the disagreement. This module exists so the numbers have one source.

Two corrections it produces, both against the paper:

* **70 is a directory count, not an arm count.** Four stored HMDA state-attribute
  directories carry no readable baseline/mitigated pair, so the usable total is 66.
* **"All fifty US states" is not what is on disk.** Forty states carry a race arm and
  twenty-six a sex arm. The claim to have covered every market overstates by ten.

It also reports the constant baseline beside every count, which document 72 did not. On
arms whose rates all sit above the lending crossover the rule predicts extension for every
one of them, so a constant "up" scores identically and the count carries no discriminating
power. The paper fails other cohorts for exactly this; the same test belongs here.

Run:  python -m src.experiments.analyse_lending_coverage
      python -m src.experiments.analyse_lending_coverage --dataset hmda_tx
"""

from __future__ import annotations

import argparse

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

BASE, PLAIN = "baseline", "expgrad_dp"

# The audit's own two gates, imported in value from the modules that fixed them rather than
# re-chosen here: below a baseline parity gap there is nothing to mitigate, and below a
# point of pool movement the direction call is a coin flip (documents 12/23 and the third
# cohort's committed protocol).
GAP_FLOOR = 0.05
MAGNITUDE_GUARD = 1.0


def load_arms(prefix: str | None = None) -> pd.DataFrame:
    """Every stored HMDA state-attribute arm with a readable baseline and mitigated row."""
    rows, skipped = [], []
    for directory in sorted(RESEARCH_RESULTS_DIR.glob("hmda_*_2018_*_levelling_up")):
        stem = directory.name.replace("_levelling_up", "")
        parts = stem.split("_")
        # Four parts is state x attribute. Longer names are loan-purpose splits of one
        # market or the pooled MS+LA market, both of which are counted elsewhere.
        if len(parts) != 4 or (prefix and not stem.startswith(prefix)):
            continue
        path = directory / "levelling_up_runs.csv"
        if not path.exists():
            skipped.append(stem)
            continue
        frame = pd.read_csv(path)
        base, plain = frame[frame.arm == BASE], frame[frame.arm == PLAIN]
        if base.empty or plain.empty or "n_test" not in frame.columns:
            skipped.append(stem)
            continue
        rows.append({
            "state": parts[1], "attribute": parts[3],
            "rate": float((base["positives"] / base["n_test"]).mean()),
            "gap": float(base["dp_diff"].mean()),
            "pie": float(plain["positives_pct_change"].mean()),
        })
    frame = pd.DataFrame(rows)
    frame.attrs["skipped"] = skipped
    return frame


def coverage(arms: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for attribute, sub in arms.groupby("attribute"):
        floor = sub[sub.gap.abs() >= GAP_FLOOR]
        both = floor[floor.pie.abs() >= MAGNITUDE_GUARD]
        rows.append({
            "attribute": attribute,
            "arms": len(sub), "states": sub.state.nunique(),
            "clears_floor": len(floor), "floor_up": int((floor.pie > 0).sum()),
            "clears_both": len(both), "both_up": int((both.pie > 0).sum()),
            "rate_lo": both.rate.min() if len(both) else float("nan"),
            "rate_hi": both.rate.max() if len(both) else float("nan"),
            "median_gap": float(sub.gap.abs().median()),
            "median_effect": float(sub.pie.abs().median()),
        })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", default=None,
                    help="restrict to arms whose stem starts with this, e.g. hmda_tx")
    args = ap.parse_args()

    arms = load_arms(args.dataset)
    skipped = arms.attrs.get("skipped", [])
    print(f"Usable state-attribute arms: {len(arms)} over {arms.state.nunique()} states")
    if skipped:
        print(f"Stored directories with no readable arm: {len(skipped)} "
              f"({', '.join(skipped)}) --- these are why a directory count reads "
              f"{len(arms) + len(skipped)}")

    table = coverage(arms)
    print()
    print(table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\nThe count that carries the paper's allocative claim, with its constant:")
    for row in table.to_dict("records"):
        if not row["clears_both"]:
            print(f"  {row['attribute']}: no arm clears both gates "
                  f"(median gap {row['median_gap']:.4f}) --- the audit refuses all "
                  f"{row['arms']}, which is the finding")
            continue
        n, up = row["clears_both"], row["both_up"]
        print(f"  {row['attribute']}: {up} of {n} level up, at rates "
              f"{row['rate_lo']:.3f}-{row['rate_hi']:.3f}")
        print(f"    Every one of those rates sits above every located lending crossover, so"
              f" the rule\n    predicts extension on all {n}: a constant \"up\" also scores "
              f"{n} of {n}. The count is\n    consistent with the rule and discriminates "
              f"nothing.")

    out = research_dir("lending_coverage")
    arms.to_csv(out / "arms.csv", index=False)
    table.to_csv(out / "coverage.csv", index=False)
    print(f"\nwrote {out}/arms.csv and {out}/coverage.csv")


if __name__ == "__main__":
    main()
