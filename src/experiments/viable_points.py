"""Choosing operating points that can actually carry a verdict.

**Individual work, beyond the course submission.**

[Document 40](../../research/docs/40-the-arms-that-were-worse-than-doing-nothing.md) left the
operating-point sweeps in a bad state: six points, two exclusion rules, and five of eight
populations reduced to two to four arms with three of them void. The relationship was not what
failed there. The **design** was, and it failed because the points were chosen before either
exclusion rule existed.

This picks them afterwards instead, from a property of the data measured before any mitigated
arm is run.

**Viable band.** A threshold is viable when the resulting classifier

* beats the trivial predictor -- accuracy at least ``max(p, 1 - p)`` on the test labels, which
  is document 40's rule; and
* leaves a selection rate inside ``[RATE_FLOOR, RATE_CEILING]``, because an arm predicting
  almost nobody or almost everybody positive has too few flips to measure and lands in
  [document 15](../../research/docs/15-arbitrariness-at-small-scale.md)'s regime regardless of
  how large the sample is.

**Points are then spread evenly in selection rate across that band**, not evenly in threshold.
Thresholds are compressed wherever the score distribution is dense, so equal steps in
threshold give clustered rates -- which is how the LSAC sweep ended up with five arms in a
region that could never survive.

**Some populations have no viable band, and that is a finding rather than an obstacle.** On a
task where 89% of people already qualify, every threshold that reaches a low selection rate
produces a classifier worse than approving everyone. The measured viable span on LSAC is
**0.107**, against the 0.40 this project requires of a sweep, so the operating-point route is
**unusable there** and no number of extra points changes it. ``viable_band`` reports the span
so a caller can refuse rather than produce arms that will be excluded later.
"""

from __future__ import annotations

import numpy as np

# An arm outside these rates has too few flips to measure whatever the sample size.
RATE_FLOOR, RATE_CEILING = 0.05, 0.95

# Below this span of achievable selection rate, a sweep cannot identify a crossover.
MIN_VIABLE_SPAN = 0.40


def viable_band(scores, y_true, *, step: float = 0.005) -> tuple[float, float, float]:
    """The lowest and highest selection rate reachable by a classifier worth deploying.

    Returns ``(lowest_rate, highest_rate, span)``. A span below :data:`MIN_VIABLE_SPAN`
    means the population cannot support an operating-point sweep at all.
    """
    scores = np.asarray(scores, dtype=float)
    y_true = np.asarray(y_true, dtype=int)
    floor = max(float(y_true.mean()), 1.0 - float(y_true.mean()))

    rates = []
    for threshold in np.arange(step, 1.0, step):
        predicted = (scores > threshold).astype(int)
        rate = float(predicted.mean())
        if not (RATE_FLOOR <= rate <= RATE_CEILING):
            continue
        if float((predicted == y_true).mean()) >= floor:
            rates.append(rate)

    if not rates:
        return (float("nan"), float("nan"), 0.0)
    return (min(rates), max(rates), max(rates) - min(rates))


def choose_points(scores, y_true, *, count: int = 12,
                  step: float = 0.005) -> list[float]:
    """``count`` thresholds whose selection rates are spread evenly across the viable band.

    Even in *rate*, not in threshold: where the score distribution is dense, equal steps in
    threshold give clustered rates, and clustered rates are why a six-point sweep could lose
    five arms to one exclusion rule.
    """
    scores = np.asarray(scores, dtype=float)
    y_true = np.asarray(y_true, dtype=int)
    floor = max(float(y_true.mean()), 1.0 - float(y_true.mean()))

    usable = []
    for threshold in np.arange(step, 1.0, step):
        predicted = (scores > threshold).astype(int)
        rate = float(predicted.mean())
        if not (RATE_FLOOR <= rate <= RATE_CEILING):
            continue
        if float((predicted == y_true).mean()) >= floor:
            usable.append((rate, float(threshold)))

    if len(usable) < count:
        return [t for _, t in sorted(usable)]

    lowest, highest = min(r for r, _ in usable), max(r for r, _ in usable)
    targets = np.linspace(lowest, highest, count)
    chosen: list[float] = []
    for target in targets:
        rate, threshold = min(usable, key=lambda pair: abs(pair[0] - target))
        if threshold not in chosen:
            chosen.append(threshold)
    return sorted(chosen)


def points_for(dataset_spec: str, *, count: int = 12, seed: int = 0):
    """Viable band and chosen points for a dataset, from its own scores.

    Measured on the seed-0 split with the default learner, before any mitigated arm exists,
    so choosing the points cannot depend on any outcome being scored later.
    """
    from ..datasets import build as build_dataset
    from ..models import build as build_model
    from ..preprocessing import prepare

    dataset = build_dataset(dataset_spec).load()
    split = prepare(dataset, random_state=seed)
    model = build_model("logistic_regression", random_state=seed)
    model.fit(split.X_train, split.y_train)
    scores = model.predict_proba(split.X_test)[:, 1]

    band = viable_band(scores, split.y_test)
    points = choose_points(scores, split.y_test, count=count)
    return {"dataset": dataset.name, "low": band[0], "high": band[1], "span": band[2],
            "sweepable": band[2] >= MIN_VIABLE_SPAN, "points": points}


if __name__ == "__main__":
    import sys

    for spec in sys.argv[1:] or ["acs:AL", "acs:KY", "acs:SC", "acs:OR",
                                 "dutch", "compas", "lawschool"]:
        info = points_for(spec)
        verdict = "sweepable" if info["sweepable"] else "NOT SWEEPABLE"
        print(f"{info['dataset']:22} rates {info['low']:.3f}-{info['high']:.3f} "
              f"span {info['span']:.3f}  {verdict}")
        print(f"    {len(info['points'])} points: "
              f"{', '.join(f'{t:.3f}' for t in info['points'])}")
