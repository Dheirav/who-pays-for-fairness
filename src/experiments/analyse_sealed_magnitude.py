"""A sealed magnitude prediction: how big, not just which way, frozen before the arms exist.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists.** New York's and Texas's sweep arms are queued
behind Florida's tonight and none has been written; Ohio began at 15:54 UTC, minutes before
this commit, and is therefore excluded along with every state whose arms are already on
disk.

Provenance, disclosed in full
-----------------------------
The paper concedes that magnitude does not transfer between populations (document 44's M2:
pooled r = +0.487 against a 0.70 bar). This afternoon nine candidate forms were searched,
post-hoc, over the 42 retained arms of the four populations with located crossovers. Six
lost to predicting zero. Three multiplicative forms beat it, and the best,

    log|pie| = 0.2438 * log|rate - 0.54| + 2.9181 * log(span) + 3.2380,

scored leave-one-population-out MAE 10.59 against 13.91 for predicting zero. **Found by
search on four populations, that is document 26's setup exactly**, and it earns nothing
until it predicts arms it has never seen. This file freezes the coefficients above --
fitted once, on all 42 old arms -- and the test below.

What is fixed here
------------------
* The model, verbatim, with its three coefficients frozen to the digits above. ``dist`` is
  the arm's baseline selection rate minus the fixed 0.54 prior -- the same prior the sealed
  direction rule used, and a quantity measurable before any constraint is fitted. ``span``
  is the population's seed-0 viable-band span, measured in the prescreen before any arm
  ran: **NY 0.7618, TX 0.6509**.
* The arms: every sealed sweep threshold of New York and Texas
  (``analyse_residual.SWEEP``), retained under the same exclusion rules as everything else.
* **S1, the bar:** the frozen model's mean absolute error on |pie| across the retained
  NY + TX arms is smaller than the error of predicting zero -- which is the incumbent,
  because "magnitude is not claimable" is operationally the zero prediction. Not smaller
  means the concession stands and this model joins the ledger as a failure.
* **S2, reported not gating:** Spearman rank correlation between predicted and observed
  |pie| -- does the model at least order the sizes?

Run:  python -m src.experiments.analyse_sealed_magnitude
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..results_io import research_dir

B_DIST = 0.2438
B_SPAN = 2.9181
INTERCEPT = 3.2380
CROSSOVER = 0.54

# Seed-0 viable-band spans, measured in the prescreen before any arm existed.
SEALED = {"NY": 0.7618, "TX": 0.6509}


def predicted_magnitude(rate: float, span: float) -> float:
    distance = abs(rate - CROSSOVER)
    if distance <= 0:
        return 0.0
    return float(np.exp(INTERCEPT + B_DIST * np.log(distance) + B_SPAN * np.log(span)))


def main() -> None:
    from scipy.stats import spearmanr

    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import load_points_for
    from .analyse_residual import SWEEP

    rows = []
    for state, span in SEALED.items():
        stem = f"acs_income_{state.lower()}_2018"
        ops = load_points_for(stem, SWEEP[state])
        if ops.empty:
            print(f"  {stem}: no arms yet")
            continue
        kept, _ = apply_rules(ops, majority_baseline(f"acs:{state}"))
        for _, arm in kept.iterrows():
            rows.append({
                "state": state, "rate": float(arm["selection_rate"]),
                "observed": abs(float(arm["pie"])),
                "predicted": predicted_magnitude(float(arm["selection_rate"]), span),
            })
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no sealed arms have been run yet")

    print(frame.round(3).to_string(index=False))
    model_mae = float((frame["predicted"] - frame["observed"]).abs().mean())
    zero_mae = float(frame["observed"].mean())
    print(f"\nS1  model MAE {model_mae:.3f} vs predict-zero {zero_mae:.3f}  "
          f"{'HOLDS' if model_mae < zero_mae else 'FAILS'}  (n={len(frame)})")
    rho = spearmanr(frame["predicted"], frame["observed"]).statistic
    print(f"S2  Spearman(|predicted|, |observed|) = {rho:+.3f}")

    OUT = research_dir("sealed_magnitude")
    frame.round(6).to_csv(OUT / "sealed_magnitude.csv", index=False)
    print(f"\nwrote {OUT}/sealed_magnitude.csv")


if __name__ == "__main__":
    main()
