"""Why the direction flips: a derivation, and a prediction it can fail.

**Individual work, beyond the course submission.**

**Written and committed before the populations it will be tested on exist.** The twelve
populations already measured motivated this derivation and cannot test it -- their outcomes
were seen first. The test set is the states and the second HMDA population run *after* this
file was committed. If the prediction fails there it is reported as a failed derivation, in
the manner of docs/21's L2 and docs/24's G2, and not retuned.

The identity, which needs no assumptions
----------------------------------------
Let the privileged group be share ``p`` of the population with unconstrained selection rate
``r_A``, and the unprivileged group ``1-p`` at ``r_B``, with ``r_A > r_B``. The
unconstrained total selection rate is the size-weighted average

    rbar = p*r_A + (1-p)*r_B

Demographic parity puts **both** groups on one common rate ``s``, so the constrained total
is ``s`` exactly. Therefore

    change in favourable decisions = s - rbar

Write ``lambda = (s - r_B) / (r_A - r_B)`` for where the common rate sits on the interval
between the two original rates: 0 means dragged down to the unprivileged rate, 1 means
lifted to the privileged one. Substituting ``rbar``:

    **the pie is preserved exactly when lambda == p**

Levelling down is ``lambda < p`` and nothing else. It is the optimiser choosing a
compromise *below* the size-weighted one. This much is arithmetic and is true of any
dataset, any classifier and any solver.

Where the optimiser puts the common rate
----------------------------------------
Assumptions, stated before the result rather than after:

* **A1 -- group-wise thresholding is optimal.** Verified against Corbett-Davies et al.
  (2017): "the optimal algorithms that result require detaining defendants above
  race-specific risk thresholds."
* **A2 -- calibration.** The score is the probability, ``eta_g(t) = t``.
* **A3 -- location shift.** The two groups' score distributions differ only by a shift
  ``delta``. This is strong and is the assumption most likely to be wrong.
* **A4 -- the score density is unimodal.**

Accepting one more person at group ``g``'s threshold changes total error by ``1 - 2*eta``:
a person with ``eta > 1/2`` is better accepted than rejected. Raising the common rate by
``ds`` flips ``n_g * ds`` people in each group, so

    d(error)/ds = sum_g n_g * (1 - 2*eta_g(t_g(s)))

Setting that to zero gives the first-order condition for the accuracy-optimal common rate:

    **p * eta_A + (1-p) * eta_B = 1/2**

The size-weighted average of the true positive probability at the two thresholds is one
half. Unconstrained, each group sits at ``eta_g = 1/2`` separately and the condition holds
trivially; the constraint forces them to share ``s`` while that weighted average is held.

Now let ``Q(s)`` be the score at the ``(1-s)`` quantile -- the threshold that selects the
top ``s`` of a group. Under A2 and A3 the condition becomes ``Q_B(s*) = 1/2 - p*delta``,
while ``Q_B(r_B) = 1/2`` and ``Q_B(r_A) = 1/2 - delta``.

**If ``Q_B`` were linear between ``r_B`` and ``r_A``, then ``s*`` would land exactly at the
size-weighted point and the pie would never move.** Levelling down is therefore entirely a
*curvature* effect, and its sign follows from the curvature of the quantile function:

    Q''(s) = -f'(Q(s)) / f(Q(s))**3

so ``Q`` is convex where the density is falling and concave where it is rising. A convex
``Q`` lies below its chord, which puts ``s*`` below the size-weighted point -- levelling
down. A concave ``Q`` puts it above -- levelling up.

The density falls above the mode and rises below it. So:

    **operating above the mode of the score distribution -> levelling down**
    **operating below it -> levelling up**
    **the crossover is at the mode**

Operationally, let ``m`` be the selection rate at the mode: the fraction of the population
scoring above the densest point of the score distribution. Then the prediction is

    **sign(lambda - p) = sign(rbar - m)**

and this is a per-population number, not a universal constant. For a symmetric score
distribution the mode is the median and ``m = 0.5``, which is why the crossover observed in
document 23 sits between 0.25 and 0.60 rather than anywhere else -- but nothing here
requires symmetry, and the test below uses each population's own measured ``m``.

Stated in advance, so they can fail
-----------------------------------
**M0 -- the identity holds.** ``(s - rbar)/rbar`` reproduces the recorded percentage change
in favourable decisions to within ``IDENTITY_TOL``. This is arithmetic; if it fails, the
measurement pipeline is wrong, not the theory.

**M1 -- the sign prediction.** ``sign(lambda - p) == sign(rbar - m)`` in at least
``MIN_SIGN_ACCURACY`` of held-out populations. **This is the derivation's actual claim.**

**M2 -- the crossover locates.** Across held-out populations the measured ``rbar`` at which
``lambda - p`` changes sign lies within ``CROSSOVER_TOL`` of the measured ``m``.

**M3 -- linearity is the null.** ``|lambda - p|`` correlates with the measured curvature of
the quantile function at the operating point. If the pie moves just as much where ``Q`` is
straight as where it bends, the curvature account is wrong even if M1 passes by luck.

If M1 fails, the derivation is wrong and the paper reports the flip as an empirical
regularity without a mechanism, which is where document 23 already stands.

Run:  python -m src.experiments.analyse_mechanism --dataset adult acs:AL
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..datasets import build as build_dataset
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import research_dir
from .methods import BASE_MODEL

IDENTITY_TOL = 0.5          # percentage points
MIN_SIGN_ACCURACY = 0.75    # M1
CROSSOVER_TOL = 0.15        # M2, in selection-rate units

# Kernel bandwidth for locating the mode of the score distribution, as a fraction of the
# score range. Fixed here rather than tuned, because tuning it after seeing which value
# reproduces the observed crossover is exactly the move this module exists to avoid.
BANDWIDTH = 0.05


def mode_selection_rate(scores: np.ndarray, bandwidth: float = BANDWIDTH) -> float:
    """Fraction of the population scoring above the densest point of the score density.

    The mode is where the quantile function's curvature changes sign, so this is the
    selection rate the derivation predicts as the crossover.
    """
    grid = np.linspace(scores.min(), scores.max(), 512)
    # Simple fixed-bandwidth Gaussian KDE, written out rather than tuned by a library
    # default that could vary between versions.
    h = bandwidth * (scores.max() - scores.min())
    density = np.exp(-0.5 * ((grid[:, None] - scores[None, :]) / h) ** 2).sum(axis=1)
    mode_score = float(grid[int(np.argmax(density))])
    return float(np.mean(scores > mode_score))


def quantile_curvature(scores: np.ndarray, rate: float) -> float:
    """Sign and rough size of Q''(s) at the operating rate, from the density slope.

    ``Q'' = -f'(Q)/f(Q)^3``, so the sign is the negative of the density's slope at the
    threshold. Returned normalised by the density so the number is comparable across
    populations with different score scales.
    """
    threshold = float(np.quantile(scores, 1.0 - rate))
    h = BANDWIDTH * (scores.max() - scores.min())
    window = np.abs(scores - threshold) < h
    if window.sum() < 20:
        return float("nan")
    below = float(np.mean((scores > threshold - h) & (scores <= threshold)))
    above = float(np.mean((scores > threshold) & (scores < threshold + h)))
    density = (below + above) / 2
    return float((below - above) / density) if density > 0 else float("nan")


def measure(dataset_spec: str, seeds: list[int]) -> dict:
    """Per-population quantities the derivation needs, measured from the baseline model."""
    dataset = build_dataset(dataset_spec).load()
    rates, modes, curvatures = [], [], []
    for seed in seeds:
        split = prepare(dataset, random_state=seed)
        model = build_model(BASE_MODEL, random_state=seed)
        model.fit(split.X_train, split.y_train)
        scores = model.predict_proba(split.X_test)[:, 1]
        predictions = model.predict(split.X_test)
        rates.append(float(np.mean(predictions)))
        modes.append(mode_selection_rate(scores))
        curvatures.append(quantile_curvature(scores, float(np.mean(predictions))))
    return {
        "dataset": dataset_spec,
        "name": dataset.name,
        "rbar_model": float(np.mean(rates)),
        "mode_rate": float(np.mean(modes)),
        "curvature": float(np.nanmean(curvatures)),
        "predicted_direction": "up" if np.mean(rates) > np.mean(modes) else "down",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", nargs="+", required=True, dest="datasets",
                        help="dataset specs to measure, e.g. adult acs:AL hmda:MS:derived_race")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    args = parser.parse_args()

    rows = [measure(spec, args.seeds) for spec in args.datasets]
    frame = pd.DataFrame(rows)
    print(frame.round(4).to_string(index=False))
    print("\n  rbar_model  = the unconstrained model's overall selection rate")
    print("  mode_rate   = fraction scoring above the densest point of the score density")
    print("  prediction  = levelling UP where rbar > mode_rate, DOWN where rbar < mode_rate")
    print("\n  Pair these with lambda - p from the levelling-up runs to evaluate M1.")

    out = research_dir("mechanism")
    frame.to_csv(out / "mechanism_measurements.csv", index=False)
    print(f"\nwrote {out}/mechanism_measurements.csv")


if __name__ == "__main__":
    main()
