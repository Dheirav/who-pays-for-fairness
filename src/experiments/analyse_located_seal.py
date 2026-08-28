r"""Experiment 7.2: measured crossover against transported crossover, predicted forward.

**Individual work, beyond the course submission. Sealed before any of its six arms ran.**

This paper draws a distinction it has never tested prospectively. The **sweep-conditional**
claim says: measure your own population's crossover, then the selection rate predicts
direction against *that*. The weaker **transported-prior** claim says: use a crossover located
somewhere else. Every sealed test so far has tested the second one, and its record is three
cohorts and one pass.

Experiment 7.1b supplied the missing ingredient. On ten manufactured-housing arms the pool
change was monotone in the rate with a single sign change, bracketing a crossover at
**0.390--0.420**. The paper's published lending crossover, located on site-built purchase and
refinance lending, is **0.660**. Those two numbers disagree about every market whose rate
lands between them, which is roughly half of the manufactured arms measured so far.

So this cohort predicts six never-measured markets under both rules at once:

* ``LOCATED = 0.405`` --- the midpoint of the bracket located in 7.1b, fixed before these arms
  existed and reported in document 77;
* ``TRANSPORTED = 0.660`` --- the paper's own published lending value.

**S1.** The located rule scores at least ``MIN_CORRECT_FRACTION`` of the retained arms, beats
the best constant, **and beats the transported rule**. Beating the bar without beating the
transported rule is a failure and will be reported as one: the whole point is the comparison.

**The void condition, committed here rather than found afterwards.** The two rules differ only
on arms whose rate falls in [0.405, 0.660). **If no retained arm lands in that window the two
rules are identical on this cohort and the verdict is VOID, not a pass.** Experiment 7.1 was
undone by exactly this and did not say so in advance; 7.1b said so and survived it.

**S2, reported not predicted.** Scored again without the magnitude guard.

Neither rule is fitted to these six markets. The located value comes from ten other
populations; the transported value comes from a different product entirely.

Run:  python -m src.experiments.analyse_located_seal
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

BASE, PLAIN = "baseline", "expgrad_dp"

LOCATED = 0.405        # midpoint of 7.1b's bracket, from ten other populations
TRANSPORTED = 0.660    # the paper's published lending crossover
SURVEY_PRIOR = 0.54
MIN_MAGNITUDE = 1.0
NOISE_FLOOR, GAP_FLOOR = 2500, 0.05
MIN_CORRECT_FRACTION = 0.75

# Six markets clearing 2,500 manufactured test rows and never measured on this slice.
MARKETS = ("AR", "FL", "IN", "LA", "MS", "TX")
YEAR = "2021"

SEALED = [(f"hmda:{m}:derived_race::{YEAR}:manufactured",
           f"hmda_{m.lower()}_{YEAR}_race_manufactured") for m in MARKETS]


def _assert_names_match_the_loader() -> None:
    from ..datasets import build

    for spec, expected in SEALED:
        actual = build(spec).name
        if actual != expected:
            raise SystemExit(f"seal names {expected!r}; loader produces {actual!r}")


def load() -> pd.DataFrame:
    rows = []
    for _, stem in SEALED:
        path = RESEARCH_RESULTS_DIR / f"{stem}_levelling_up" / "levelling_up_runs.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        base, plain = frame[frame.arm == BASE], frame[frame.arm == PLAIN]
        if base.empty or plain.empty or "n_test" not in frame.columns:
            continue
        rows.append({
            "population": stem, "market": stem.split("_")[1],
            "n_test": float(base.n_test.mean()), "gap": float(base.dp_diff.mean()),
            "rate": float((base.positives / base.n_test).mean()),
            "pie": float(plain.positives_pct_change.mean()),
        })
    return pd.DataFrame(rows)


def score(frame: pd.DataFrame, *, guard: bool) -> dict:
    kept = frame[(frame.n_test >= NOISE_FLOOR) & (frame.gap.abs() >= GAP_FLOOR)]
    if guard:
        kept = kept[kept.pie.abs() >= MIN_MAGNITUDE]
    if kept.empty:
        return {"n": 0}
    actual = np.where(kept.pie > 0, "up", "down")
    located = np.where(kept.rate >= LOCATED, "up", "down")
    transported = np.where(kept.rate >= TRANSPORTED, "up", "down")
    survey = np.where(kept.rate >= SURVEY_PRIOR, "up", "down")
    ups = int((actual == "up").sum())
    return {
        "n": len(kept), "markets": int(kept.market.nunique()),
        "located": int((located == actual).sum()),
        "transported": int((transported == actual).sum()),
        "constant": max(ups, len(kept) - ups),
        "survey": int((survey == actual).sum()),
        # the arms on which the two crossovers disagree: the entire test
        "separating": int(((kept.rate >= LOCATED) & (kept.rate < TRANSPORTED)).sum()),
        "floor": int(np.ceil(MIN_CORRECT_FRACTION * len(kept))),
        "rate_lo": float(kept.rate.min()), "rate_hi": float(kept.rate.max()),
    }


def report(s: dict, label: str) -> str:
    if not s["n"]:
        print(f"\n{label}: no arm survives the gates --- VOID")
        return "VOID"
    print(f"\n{label}: {s['n']} arms over {s['markets']} markets, "
          f"rates {s['rate_lo']:.3f}--{s['rate_hi']:.3f}")
    print(f"  arms in [{LOCATED}, {TRANSPORTED}) where the two crossovers disagree: "
          f"{s['separating']}")
    if s["separating"] == 0:
        print("  VOID --- the located and transported rules are identical on this cohort,\n"
              "  which was pre-registered as a void outcome rather than a pass")
        return "VOID"
    beats = {k: s["located"] > s[k] for k in ("transported", "constant", "survey")}
    passes = s["located"] >= s["floor"] and all(beats.values())
    print(f"  located ({LOCATED}) {s['located']}/{s['n']}   bar {s['floor']}")
    for k in ("transported", "constant", "survey"):
        print(f"    vs {k:<12} {s[k]}/{s['n']}   {'beaten' if beats[k] else 'NOT beaten'}")
    verdict = "HOLDS" if passes else "FAILS"
    print(f"  {verdict}")
    return verdict


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", default=None)
    args = ap.parse_args()
    _assert_names_match_the_loader()

    frame = load()
    if args.dataset:
        frame = frame[frame.population.str.startswith(args.dataset)]
    print(f"Sealed located-crossover cohort: {len(SEALED)} arms specified, {len(frame)} present")
    if frame.empty:
        raise SystemExit("no arms yet --- this module is committed before they run")
    print(frame[["population", "rate", "pie", "gap", "n_test"]]
          .round(4).to_string(index=False))

    primary = report(score(frame, guard=True), "S1 (magnitude guard applied, primary)")
    report(score(frame, guard=False), "S2 (no guard, reported not predicted)")

    out = research_dir("located_seal")
    frame.to_csv(out / "arms.csv", index=False)
    pd.DataFrame([score(frame, guard=True) | {"scoring": "guarded"},
                  score(frame, guard=False) | {"scoring": "unguarded"}]).to_csv(
        out / "scores.csv", index=False)
    print(f"\nwrote {out}/arms.csv and {out}/scores.csv")
    print(f"\nS1 verdict: {primary}")


if __name__ == "__main__":
    main()
