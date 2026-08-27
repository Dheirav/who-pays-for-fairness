"""Experiment 7.1: a sealed direction test on real approvals the rule has never seen.

**Individual work, beyond the course submission. Sealed before any arm of this cohort ran.**

Three referees independently named a held-out real-allocation test as the one experiment
that would most improve this paper. Two earlier attempts on lending exist and neither
tested anything:

* the **six-market sweep seal** failed (2 of 6) because the sweep protocol is unreliable on
  mortgage data, and the paper says so;
* the **sealed lending cohort** failed for the opposite reason --- every scored arm went up,
  so a constant ``up`` scored 8 of 8 and tied the rule. The same defect runs through the
  fifty-market coverage: US mortgage approval sits at rates of 0.82 and above, the rule
  predicts extension everywhere, and nothing can discriminate.

**What makes this cohort different is the design, not the data.** Loan purpose moves the
approval rate a long way within one market: on 2018 the measured purpose arms span 0.555
(home improvement) to 0.901 (refinancing), straddling the located lending crossover. Pairing
a low-rate purpose with a high-rate purpose in each market therefore produces a cohort where
the rule predicts *different* directions for the two arms of the same market, and a constant
cannot tie it by construction. That is what the previous lending seal lacked.

The cohort
----------
HMDA **2021**, a reporting year this project has never touched, race arm, eight markets with
no purpose-level arm in the record, two purposes each: ``improvement`` and ``refinance``.
Sixteen arms, eight person-samples. Vermont is deliberately absent: it was used to profile
runtime before this protocol was written, so its arms are not held out.

The rule, and it is the published one
-------------------------------------
``down below the crossover, up at or above``, with the crossover fixed at ``CROSSOVER =
0.660`` --- the pooled lending value already published in this paper's crossover table. It is
not chosen for this cohort and not fitted to it.

What counts as success
----------------------
**S1.** The rule scores at least ``MIN_CORRECT`` of the scored arms **and** strictly beats
every null below. Beating the bar but not a null is a failure, and will be reported as one.

The nulls, all three committed here:

* ``constant`` --- always predict the majority outcome. This is what killed the last lending
  cohort and it is the one that matters.
* ``purpose`` --- improvement predicts down, refinance predicts up. Purpose correlates with
  rate, so this asks whether the *rate* carries the prediction or the loan product does.
* ``survey`` --- the 0.54 ACS prior instead of the lending one, asking whether the
  lending-specific value earns its place.

**S2, reported not predicted.** Scored a second time without the magnitude guard. Document 69
established that the guard deletes near-crossover arms and so removes exactly the discordance
a paired test needs; both scorings are recorded so that neither can be chosen afterwards.

Run:  python -m src.experiments.analyse_allocation_seal
      python -m src.experiments.analyse_allocation_seal --dataset hmda_az_2021
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

BASE, PLAIN = "baseline", "expgrad_dp"

# The published pooled lending crossover, not a value fitted to this cohort.
CROSSOVER = 0.660
# The ACS survey prior, as the third null.
SURVEY_PRIOR = 0.54
# The protocol's magnitude guard, unchanged.
MIN_MAGNITUDE = 1.0
# The audit's own gates.
NOISE_FLOOR, GAP_FLOOR = 2500, 0.05
# S1's bar: a clear majority of the scored arms, and every null beaten.
MIN_CORRECT_FRACTION = 0.75

MARKETS = ("AZ", "CO", "GA", "NC", "OH", "TN", "VA", "WA")
PURPOSES = ("improvement", "refinance")
YEAR = "2021"

SEALED = [(f"hmda:{m}:derived_race:{p}:{YEAR}",
           f"hmda_{m.lower()}_{YEAR}_race_{p}") for m in MARKETS for p in PURPOSES]


def _assert_names_match_the_loader() -> None:
    """The directory a spec produces must be the one this module reads.

    Five of twenty-four names were wrong in an earlier sealed cohort because a loader
    default was silently omitted from the stem. Resolving each spec here turns that class of
    error into an exception before any arm runs, rather than a silent miss afterwards.
    """
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
            "spec": spec, "population": stem,
            "market": stem.split("_")[1], "purpose": stem.split("_")[-1],
            "n_test": float(base.n_test.mean()),
            "gap": float(base.dp_diff.mean()),
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
    survey = np.where(kept.rate >= SURVEY_PRIOR, "up", "down")
    purpose = np.where(kept.purpose == "refinance", "up", "down")
    ups = int((actual == "up").sum())
    constant = max(ups, len(kept) - ups)
    return {
        "n": len(kept), "populations": int(kept.market.nunique()),
        "rule": int((rule == actual).sum()),
        "constant": constant,
        "purpose": int((purpose == actual).sum()),
        "survey": int((survey == actual).sum()),
        "floor": int(np.ceil(MIN_CORRECT_FRACTION * len(kept))),
        "rate_lo": float(kept.rate.min()), "rate_hi": float(kept.rate.max()),
        "down_calls": int((rule == "down").sum()),
    }


def report(s: dict, label: str) -> bool:
    if not s["n"]:
        print(f"\n{label}: no arm survives the gates --- VOID")
        return False
    beats = {k: s["rule"] > s[k] for k in ("constant", "purpose", "survey")}
    passes = s["rule"] >= s["floor"] and all(beats.values())
    print(f"\n{label}: {s['n']} arms over {s['populations']} markets, "
          f"rates {s['rate_lo']:.3f}--{s['rate_hi']:.3f}")
    print(f"  the rule predicts down on {s['down_calls']} of {s['n']} "
          f"--- a constant cannot tie unless that is 0 or {s['n']}")
    print(f"  rule {s['rule']}/{s['n']}   bar {s['floor']}")
    for k in ("constant", "purpose", "survey"):
        print(f"    vs {k:<9} {s[k]}/{s['n']}   {'beaten' if beats[k] else 'NOT beaten'}")
    print(f"  {'HOLDS' if passes else 'FAILS'}")
    return passes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", default=None, help="restrict to one stem, for inspection")
    args = ap.parse_args()
    _assert_names_match_the_loader()

    frame = load()
    if args.dataset:
        frame = frame[frame.population.str.startswith(args.dataset)]
    print(f"Sealed allocation cohort: {len(SEALED)} arms specified, {len(frame)} present")
    if frame.empty:
        raise SystemExit("no arms yet --- this module is committed before they run")
    print(frame[["population", "rate", "pie", "gap", "n_test"]]
          .round(4).to_string(index=False))

    primary = report(score(frame, guard=True), "S1 (magnitude guard applied, primary)")
    report(score(frame, guard=False), "S2 (no guard, reported not predicted)")

    out = research_dir("allocation_seal")
    frame.to_csv(out / "arms.csv", index=False)
    pd.DataFrame([score(frame, guard=True) | {"scoring": "guarded"},
                  score(frame, guard=False) | {"scoring": "unguarded"}]).to_csv(
        out / "scores.csv", index=False)
    print(f"\nwrote {out}/arms.csv and {out}/scores.csv")
    print(f"\nS1 verdict: {'HOLDS' if primary else 'FAILS'}")


if __name__ == "__main__":
    main()
