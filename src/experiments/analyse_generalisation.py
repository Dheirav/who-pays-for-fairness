"""Does any of this survive leaving the two instruments it was found in?

**Individual work, beyond the course submission.**

**Written before any COMPAS or LSAC arm was run**, and committed before them. Only the two
manipulation checks below had been measured — the achievable selection-rate range on each
dataset, which decided the operating points. No mitigated arm existed.

The weakness this closes
------------------------
Every population in this project is the American Community Survey or HMDA mortgage records:
two instruments, one country, one year. The claim is about **decision systems**, and no amount
of extra ACS states can test that — they share an instrument, an encoding and a label
construction. A reviewer gets to say the whole thing is a property of income prediction and
American mortgage lending.

Two datasets from unrelated domains, chosen for different reasons:

* **COMPAS** (criminal justice, 2016) — the canonical fairness benchmark. Its absence from a
  fairness paper is itself a question. Base rate 0.53.
* **LSAC bar passage** (legal education) — chosen because it is **naturally generous**, base
  rate 0.89. Almost every natural population measured so far sits at a *low* selection rate,
  and only mortgage lending occupies the top of the range. Since the rule predicts opposite
  directions at the two ends, the sample of tasks has been testing one half far harder than
  the other.

Neither has an income cutoff to move. **So the only way to vary the selection rate here is the
operating-point route** — which makes this simultaneously a test of the rule and a test of the
procedure [document 35](../../research/docs/35-what-to-do-about-it.md) actually recommends.

The naive alternative, named in advance
---------------------------------------
    **"The rule is a property of income prediction and American mortgage lending. On criminal
    justice and legal education it predicts nothing."**

This is the live hypothesis. It predicts |r| < ``MIN_NAIVE_R`` on both new instruments, and it
is the outcome that would most damage the paper, so it is written down first.

Stated in advance, so they can fail
-----------------------------------
**G0 — manipulation check.** On each instrument the operating-point sweep spans at least
``MIN_SPAN`` of selection rate, and at least four arms survive document 23's parity-gap
exclusion. Measured already at 0.08–0.95 (COMPAS) and 0.13–0.92 (LSAC), so this guards a
pipeline error rather than a real risk.

**G1 — the direction at the natural operating point.** Each dataset's *unmodified* model sits
somewhere on the rate scale, and the rule predicts a sign there.

* **LSAC at 0.89** is above every crossover measured anywhere in this project, so the
  constraint should **grow** the pool. Predicted.
* **COMPAS at 0.53** sits inside the band where crossovers have been observed (0.25–0.77
  across populations). **The sign is explicitly NOT predicted**, for the same reason
  [document 31](../../research/docs/31-the-crossover-on-natural-data.md) refused to predict
  its lowest arm. Claiming it afterwards either way would be unfalsifiable.

**G2 — the sweep reproduces the relationship.** On each instrument, across retained arms, the
pie change rises with the baseline selection rate at ``r >= MIN_R``, **and** the spread clears
document 37's ``MIN_SPAN_PIE`` guard so the correlation is not fitted to noise. Beating the
naive alternative requires ``r >= MIN_NAIVE_R``; passing requires ``MIN_R``.

**G3 — the crossovers differ between the two new domains.** Document 32 found the crossover is
population-specific, so two unrelated domains should not share one. **No prediction is made
about where either sits** — only that they are not the same, and that quoting any single band
as universal stays wrong.

**G4 — the robustness carries over.** On LSAC, the boosted learner and a five-fold looser
tolerance leave the crossover bracket where the linear model at the default tolerance put it,
as they do on four ACS populations of five.

**G5 — equalized odds stays weak.** On both instruments the pool moves less under equalized
odds than under demographic parity, consistent with
[document 33](../../research/docs/33-the-rule-does-not-survive-equalized-odds.md). Reported as
a magnitude comparison; no correlation bar attaches, because four arms cannot support one.

**G7 — the group-gap alternative, on the population where it should show.**
The oldest competing explanation is that the direction is set by the **gap between the two
groups** rather than by the overall selection rate. Document 23 partialled that gap out and
the relationship survived, but no population measured had an extreme gap, so the test was
weak where it mattered.

The Dutch census 2001 has one: men hold a high-status occupation at 0.626 and women at 0.327,
a gap of **0.298 — roughly twice Adult's**. It is also non-US and non-2010s, which no other
population here is.

    **Prediction.** The sweep behaves like every other mid-base-rate population: ``r >= MIN_R``
    with a sign flip, and the crossover lands inside the 0.25–0.77 span where every crossover
    so far has fallen. **A gap twice as large does not change the rule.**

    **The alternative it must beat:** "the group gap is doing the work, so a population with
    twice the gap behaves differently." That predicts either a failed correlation or a
    crossover outside the observed span.

**G6 — a prediction about this project's own earlier finding.**
[Document 15](../../research/docs/15-arbitrariness-at-small-scale.md) put the floor for
measurability at about 2,500 test subjects. COMPAS has **1,584**; LSAC has **6,240**. So
COMPAS arms should show **sign instability across seeds** and LSAC arms should not. If COMPAS
comes out noisy, that is document 15 confirmed on a dataset it never saw — not a failure of
the rule. If COMPAS comes out clean, document 15's floor is too conservative and should say so.

Run:  python -m src.experiments.analyse_generalisation --dataset compas
      python -m src.experiments.analyse_generalisation --dataset lawschool
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir
from .analyse_operating_point import (
    MIN_NAIVE_R,
    crossover_bracket,
    load_points_for,
)
from .analyse_threshold import MIN_BASELINE_GAP, MIN_R, MIN_SPAN, MIN_SPAN_PIE

# Chosen from each dataset's own score distribution, measured before any arm was run, to
# span the same selection-rate range the ACS sweeps cover. LSAC's scores are compressed
# against 1.0 because most candidates pass, so its thresholds sit far higher.
POINTS = {
    "compas": [0.15, 0.30, 0.45, 0.55, 0.65, 0.75],
    "lawschool": [0.60, 0.90, 0.95, 0.975, 0.99, 0.995],
    "dutch": [0.10, 0.25, 0.40, 0.62, 0.80, 0.93],
}

# G6: document 15's floor. COMPAS sits below it and LSAC above.
POWER_FLOOR = 2500


def verdict(name: str, ops: pd.DataFrame) -> dict:
    print(ops.round(4).to_string(index=False))

    span = float(ops["selection_rate"].max() - ops["selection_rate"].min())
    g0_span = span >= MIN_SPAN
    kept = ops[ops["dp_base"] >= MIN_BASELINE_GAP]
    dropped = len(ops) - len(kept)
    print(f"\nG0  selection-rate span {span:.3f} (bar {MIN_SPAN})  "
          f"{'HOLDS' if g0_span else 'FAILS'}")
    print(f"    {dropped} arms excluded by document 23's parity-gap rule; "
          f"{len(kept)} retained")
    if not g0_span or len(kept) < 4:
        print("\nVOID  the design does not identify anything on this dataset")
        return {"dataset": name, "void": True}

    spread = float(kept["pie"].max() - kept["pie"].min())
    informative = spread >= MIN_SPAN_PIE
    print(f"\nG2a the constraint moved the pool  spread {spread:.2f} points "
          f"(bar {MIN_SPAN_PIE})  {'HOLDS' if informative else 'VOID'}")
    if not informative:
        print("    below document 37's guard: any correlation here is fitted to noise, and")
        print("    this dataset is VOID rather than a refutation.")

    r = float(np.corrcoef(kept["selection_rate"], kept["pie"])[0, 1])
    band = crossover_bracket(kept)
    print(f"\nG2b rate vs pie change   r = {r:+.3f}  (bar {MIN_R}; naive alternative "
          f"beaten at {MIN_NAIVE_R}: {r >= MIN_NAIVE_R})  "
          f"{'HOLDS' if (r >= MIN_R and informative) else 'FAILS' if informative else 'VOID'}")
    print(f"    crossover bracket: {band}")

    lowest = kept.loc[kept["selection_rate"].idxmin()]
    highest = kept.loc[kept["selection_rate"].idxmax()]
    print(f"    lowest  rate {lowest['selection_rate']:.3f}: pie {lowest['pie']:+.2f}%")
    print(f"    highest rate {highest['selection_rate']:.3f}: pie {highest['pie']:+.2f}%")

    return {"dataset": name, "void": False, "span": span, "spread": spread,
            "informative": informative, "r": r, "n_kept": len(kept),
            "band_low": None if band is None else band[0],
            "band_high": None if band is None else band[1],
            "beats_naive": r >= MIN_NAIVE_R, "holds": bool(r >= MIN_R and informative)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="compas", choices=sorted(POINTS))
    parser.add_argument("--suffix", default="",
                        help='variant to read, e.g. "_hgb" or "_eps005"')
    args = parser.parse_args()

    from ..datasets import build as build_dataset

    name = build_dataset(args.dataset).name
    ops = load_points_for(name, POINTS[args.dataset], suffix=args.suffix)

    if ops.empty:
        raise SystemExit(
            f"no operating-point arms for {name}; run\n"
            f"  python -m src.experiments.run_levelling_up --dataset {args.dataset} "
            f"--model logistic_regression@{POINTS[args.dataset][2]}")

    ops["selection_rate"] = ops["positives_base"] / ops["n_test"]
    print(f"=== generalisation: {name} "
          f"({'below' if ops['n_test'].iloc[0] < POWER_FLOOR else 'above'} document 15's "
          f"{POWER_FLOOR}-subject floor) ===\n")
    result = verdict(name, ops)

    OUT = research_dir("generalisation")
    ops.round(6).to_csv(OUT / f"{name}_arms.csv", index=False)
    pd.Series(result).to_csv(OUT / f"{name}_verdict.csv", header=False)
    print(f"\nwrote {OUT}/{name}_arms.csv")


if __name__ == "__main__":
    main()
