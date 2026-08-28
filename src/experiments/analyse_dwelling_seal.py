r"""Experiment 7.1b: the first cohort of real approvals that can actually test the rule.

**Individual work, beyond the course submission. Sealed before any of its fourteen arms ran.**

Experiment 7.1 failed for a reason that had nothing to do with the rule: every arm of US
mortgage approval sits above the crossover, so the rule predicted extension everywhere, and a
rule that only ever says one thing cannot be distinguished from a constant that says the same
thing. Three attempts on lending had failed that way --- state level, fifty-market coverage,
and 7.1's purpose split, which was built to reach lower and returned 0 of 8 below the line.

A search of the register for any slice that reaches below 0.660 found one, and it is not a
loan purpose: **manufactured housing**. Pooled over four 2021 states the race arm approves it
at 0.505 against 0.850 for site-built.

**What this cohort does differently.** Each market contributes \emph{both} slices, so the rule
predicts \textsc{down} on the manufactured arm and \textsc{up} on the site-built arm of the
same market. No constant can match opposite predictions inside one market. That is the
property 7.1 was designed to have and did not.

**Why it might still be void, pre-registered here rather than discovered afterwards.** The
sharp null is ``dwelling-only'' --- manufactured predicts down, site-built up --- because
dwelling is what moves the rate. On most arms the rate rule and that null will agree by
construction. The test turns entirely on arms where they *disagree*: a manufactured arm whose
modelled rate lands above 0.660, or a site-built arm below it. **If no retained arm separates
them, this cohort discriminates nothing and the verdict is VOID, not a pass.** Recording that
in advance is the whole lesson of 7.1.

**What is already known, and it points against the rule.** Three exploratory manufactured
arms were run before this protocol to check the slice reaches: Georgia 0.390, Tennessee 0.527,
Ohio 0.628, of which the rule called one correctly. Those three markets are excluded here, and
their result is the reason this seal is worth making --- a pass against that prior would be
strong evidence, and a failure is what the prior already expects.

Run:  python -m src.experiments.analyse_dwelling_seal
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

BASE, PLAIN = "baseline", "expgrad_dp"

CROSSOVER = 0.660          # the published pooled lending value, not fitted here
SURVEY_PRIOR = 0.54
MIN_MAGNITUDE = 1.0
NOISE_FLOOR, GAP_FLOOR = 2500, 0.05
MIN_CORRECT_FRACTION = 0.75

# Seven markets clearing 2,500 test rows on BOTH slices. Georgia, Ohio, Tennessee and Vermont
# are excluded: arms of them have already been seen.
MARKETS = ("AL", "AZ", "KY", "MI", "NC", "SC", "WA")
DWELLINGS = ("manufactured", "sitebuilt")
YEAR = "2021"

SEALED = [(f"hmda:{m}:derived_race::{YEAR}:{d}",
           f"hmda_{m.lower()}_{YEAR}_race_{d}") for m in MARKETS for d in DWELLINGS]


def _assert_names_match_the_loader() -> None:
    from ..datasets import build

    for spec, expected in SEALED:
        actual = build(spec).name
        if actual != expected:
            raise SystemExit(f"seal names {expected!r}; loader produces {actual!r}")


def load() -> pd.DataFrame:
    rows = []
    for spec, stem in SEALED:
        path = RESEARCH_RESULTS_DIR / f"{stem}_levelling_up" / "levelling_up_runs.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        base, plain = frame[frame.arm == BASE], frame[frame.arm == PLAIN]
        if base.empty or plain.empty or "n_test" not in frame.columns:
            continue
        rows.append({
            "population": stem, "market": stem.split("_")[1],
            "dwelling": stem.split("_")[-1],
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
    rule = np.where(kept.rate >= CROSSOVER, "up", "down")
    dwelling = np.where(kept.dwelling == "sitebuilt", "up", "down")
    survey = np.where(kept.rate >= SURVEY_PRIOR, "up", "down")
    ups = int((actual == "up").sum())
    return {
        "n": len(kept), "markets": int(kept.market.nunique()),
        "rule": int((rule == actual).sum()),
        "constant": max(ups, len(kept) - ups),
        "dwelling": int((dwelling == actual).sum()),
        "survey": int((survey == actual).sum()),
        # the arms on which the rate rule and the dwelling null disagree: the whole test
        "separating": int((rule != dwelling).sum()),
        "rule_down": int((rule == "down").sum()),
        "floor": int(np.ceil(MIN_CORRECT_FRACTION * len(kept))),
        "rate_lo": float(kept.rate.min()), "rate_hi": float(kept.rate.max()),
    }


def report(s: dict, label: str) -> str:
    if not s["n"]:
        print(f"\n{label}: no arm survives the gates --- VOID")
        return "VOID"
    print(f"\n{label}: {s['n']} arms over {s['markets']} markets, "
          f"rates {s['rate_lo']:.3f}--{s['rate_hi']:.3f}")
    print(f"  the rule predicts down on {s['rule_down']} of {s['n']}")
    print(f"  arms separating the rule from the dwelling null: {s['separating']}")
    if s["separating"] == 0:
        print("  VOID --- the rate rule and the dwelling null are the same rule on this "
              "cohort,\n  which was pre-registered as a void outcome rather than a pass")
        return "VOID"
    beats = {k: s["rule"] > s[k] for k in ("constant", "dwelling", "survey")}
    passes = s["rule"] >= s["floor"] and all(beats.values())
    print(f"  rule {s['rule']}/{s['n']}   bar {s['floor']}")
    for k in ("constant", "dwelling", "survey"):
        print(f"    vs {k:<10} {s[k]}/{s['n']}   {'beaten' if beats[k] else 'NOT beaten'}")
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
    print(f"Sealed dwelling cohort: {len(SEALED)} arms specified, {len(frame)} present")
    if frame.empty:
        raise SystemExit("no arms yet --- this module is committed before they run")
    print(frame[["population", "rate", "pie", "gap", "n_test"]]
          .round(4).to_string(index=False))

    primary = report(score(frame, guard=True), "S1 (magnitude guard applied, primary)")
    report(score(frame, guard=False), "S2 (no guard, reported not predicted)")

    out = research_dir("dwelling_seal")
    frame.to_csv(out / "arms.csv", index=False)
    pd.DataFrame([score(frame, guard=True) | {"scoring": "guarded"},
                  score(frame, guard=False) | {"scoring": "unguarded"}]).to_csv(
        out / "scores.csv", index=False)
    print(f"\nwrote {out}/arms.csv and {out}/scores.csv")
    print(f"\nS1 verdict: {primary}")


if __name__ == "__main__":
    main()
