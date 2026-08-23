"""Nested rows-by-seeds bootstrap for the located crossovers.

**Individual work, beyond the course submission. Post-hoc uncertainty analysis,
labelled as such --- it locates nothing new, it puts honest intervals on locations
already published.**

The paper's crossover brackets (Table IV) carry seed-resampled intervals the Setup
section itself calls anti-conservative: rows are resampled by the train/test split
only, so sampling variability in *who is in the test set* never reaches the interval.
The second council's statistician asked for the nested version. This is it:

* **Seeds** (outer): for each seed, the baseline and the mitigation are refitted from
  scratch --- five genuinely different models per population.
* **Rows** (inner): for each seed, the test split's rows are bootstrap-resampled
  ``B`` times; each resample re-computes every arm's selection rate and pool change
  from that seed's stored per-person predictions, so no refit is needed inside the
  loop.
* Each (seed, resample) pair yields a full arm curve and therefore one crossover
  bracket; the interval reported is the percentile range of the bracket midpoints
  over all pairs, with the fraction of pairs that failed to bracket a crossing
  reported beside it rather than hidden.

Arms are built at fixed target selection rates from each seed's own score quantiles
(rate space, not threshold space), spanning the region the published brackets sit in.
Populations: the four located non-lending crossovers of Table IV.

Run:  python -m src.experiments.analyse_nested_bootstrap
      python -m src.experiments.analyse_nested_bootstrap --dataset dutch
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir

# The four populations whose located crossovers Table IV reports (lending's three
# estimates share one market and are excluded; their uncertainty is a different
# problem). Published midpoints, for the comparison column only.
POPULATIONS = {
    "compas": 0.511,
    "acs:SC": 0.530,
    "acs:OR": 0.558,
    "dutch": 0.576,
}
TARGET_RATES = [0.35, 0.42, 0.49, 0.56, 0.63, 0.70]
B = 200
SEEDS = 5


def population_curves(spec: str, seeds: int = SEEDS) -> list[dict]:
    """Per-seed fitted quantities, computed once; the row bootstrap reuses them."""
    from ..datasets import build as build_dataset
    from ..mitigation import fit_exponentiated_gradient
    from ..models import build as build_model
    from ..preprocessing import prepare

    dataset = build_dataset(spec).load()
    fitted = []
    for seed in range(seeds):
        split = prepare(dataset, random_state=seed)
        base = build_model("logistic_regression", random_state=seed)
        base.fit(split.X_train, split.y_train)
        scores = base.predict_proba(split.X_test)[:, 1]
        arms = []
        for rate in TARGET_RATES:
            tau = float(np.quantile(scores, 1 - rate))
            mitigated = fit_exponentiated_gradient(
                build_model(f"logistic_regression@{tau}", random_state=seed),
                split.X_train, split.y_train, split.a_train,
                constraint="demographic_parity", eps=0.01)
            arms.append({
                "target": rate,
                "base_pred": (scores > tau).astype(np.int8),
                "mit_p1": np.asarray(mitigated._pmf_predict(split.X_test))[:, 1],
            })
        fitted.append({"n": len(scores), "arms": arms})
    return fitted


def bracket_of(rates: np.ndarray, pies: np.ndarray) -> float | None:
    below = rates[pies < 0]
    above = rates[pies > 0]
    if below.size == 0 or above.size == 0 or below.max() >= above.min():
        return None
    return float((below.max() + above.min()) / 2)


def nested(fitted: list[dict], rng: np.random.Generator) -> tuple[list[float], int]:
    midpoints, failures = [], 0
    for per_seed in fitted:
        n = per_seed["n"]
        for _ in range(B):
            idx = rng.integers(0, n, n)
            rates, pies = [], []
            for arm in per_seed["arms"]:
                base = arm["base_pred"][idx]
                mit = arm["mit_p1"][idx]
                r = float(base.mean())
                if base.sum() == 0:
                    continue
                rates.append(r)
                pies.append(100.0 * (float(mit.mean()) - r) / r)
            mid = bracket_of(np.array(rates), np.array(pies))
            if mid is None:
                failures += 1
            else:
                midpoints.append(mid)
    return midpoints, failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one population spec (default: all four)")
    args = parser.parse_args()

    rng = np.random.default_rng(0)
    rows = []
    for spec, published in POPULATIONS.items():
        if args.dataset and args.dataset != spec:
            continue
        fitted = population_curves(spec)
        midpoints, failures = nested(fitted, rng)
        total = SEEDS * B
        if midpoints:
            lo, hi = np.percentile(midpoints, [2.5, 97.5])
            rows.append({"population": spec, "published_mid": published,
                         "boot_median": round(float(np.median(midpoints)), 3),
                         "ci_lo": round(float(lo), 3), "ci_hi": round(float(hi), 3),
                         "no_crossing_share": round(failures / total, 3),
                         "pairs": total})
        else:
            rows.append({"population": spec, "published_mid": published,
                         "no_crossing_share": 1.0, "pairs": total})
        print(pd.DataFrame(rows[-1:]).to_string(index=False,
                                                header=(len(rows) == 1)), flush=True)

    frame = pd.DataFrame(rows)
    OUT = research_dir("uncertainty")
    frame.to_csv(OUT / "nested_bootstrap.csv", index=False)
    print(f"\nwrote {OUT}/nested_bootstrap.csv")


if __name__ == "__main__":
    main()
