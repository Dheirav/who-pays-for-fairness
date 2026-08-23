"""Is the lottery suboptimal inside its own class? The two-threshold comparison.

**Individual work, beyond the course submission. Post-hoc computation, labelled as
such.**

The paper's lottery section deliberately stops at "whether it is suboptimal *within*
the blind constrained class is an open computation, not a claim we make". This is that
computation. The lottery ExpGrad returns on deep cut arms is itself a blind mixture ---
keep everyone above one threshold with probability $w$, grant nothing below. The
smallest richer class is the **two-threshold blind mixture**:

    h(x) = w * 1[s(x) > t1] + (1 - w) * 1[s(x) > t2],   t1 < t2

which grants three probability levels (0, 1-w... w+1-w) rising with the score --- the
minimal score-informed structure a blind deployer could use. For each lottery arm and
seed, the search asks: does a $(t_1, t_2, w)$ exist with **the same demographic-parity
gap or better and the same expected pool size**, at **equal or higher expected
accuracy**? $w$ has a closed form per $(t_1, t_2)$ from the parity equation, so the
search is an exact grid over score quantiles, not an optimisation that can fail
silently.

Reading the outcome: if an equal-parity, equal-pool, score-informed blind mixture
matches or beats the lottery's accuracy, the flat lottery is an *optimiser artifact* a
vendor could be expected to avoid, and the paper's charge sharpens. If nothing in the
class does, the lottery is what the constraint demands at that operating point, and
the charge softens to exactly that.

Arms: the two flat-lottery signature arms (Dutch at 0.965, COMPAS at 0.775; COMPAS
sits below the noise floor and carries direction only, noted in the output).

Run:  python -m src.experiments.analyse_mixture_optimality
      python -m src.experiments.analyse_mixture_optimality --dataset dutch
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir

ARMS = [("dutch", 0.965), ("compas", 0.775)]
# The lottery arms operate near the score distribution's tail, so the threshold grid
# must reach into it: an emptiness verdict from a grid that stops at the 0.98 quantile
# would be an artifact of the grid, not of the class.
QUANTILES = np.unique(np.concatenate([
    np.linspace(0.02, 0.98, 49), [0.985, 0.99, 0.9925, 0.995, 0.9975]]))
RATE_TOLERANCE = 0.005
SEEDS = 5


def expected_accuracy(p1: np.ndarray, y: np.ndarray) -> float:
    return float((p1 * y + (1.0 - p1) * (1.0 - y)).mean())


def search(scores: np.ndarray, y: np.ndarray, priv: np.ndarray,
           target_rate: float, gap_ceiling: float) -> dict | None:
    taus = np.unique(np.quantile(scores, QUANTILES))
    above = scores[None, :] > taus[:, None]              # taus x persons
    rate_priv = above[:, priv].mean(axis=1)
    rate_unpriv = above[:, ~priv].mean(axis=1)
    best = None
    for i in range(len(taus)):
        for j in range(i + 1, len(taus)):
            # h = w*1[s>t1] + (1-w)*1[s>t2] with t1 < t2: parity requires
            # w*(a1 - a2) + a2 == w*(b1 - b2) + b2 for the two groups' rates.
            a1, a2 = rate_priv[i], rate_priv[j]
            b1, b2 = rate_unpriv[i], rate_unpriv[j]
            denominator = (a1 - a2) - (b1 - b2)
            if abs(denominator) < 1e-12:
                continue
            w = (b2 - a2) / denominator
            if not 0.0 <= w <= 1.0:
                continue
            p1 = w * above[i] + (1.0 - w) * above[j]
            rate = float(p1.mean())
            if abs(rate - target_rate) > RATE_TOLERANCE:
                continue
            gap = abs(float(p1[priv].mean()) - float(p1[~priv].mean()))
            if gap > gap_ceiling:
                continue
            accuracy = expected_accuracy(p1, y)
            if best is None or accuracy > best["accuracy"]:
                keep = scores > taus[j]
                corr = (float(np.corrcoef(p1[keep], scores[keep])[0, 1])
                        if keep.sum() > 2 and p1[keep].std() > 0 else 0.0)
                best = {"t1": float(taus[i]), "t2": float(taus[j]), "w": float(w),
                        "rate": rate, "gap": gap, "accuracy": accuracy,
                        "corr_above_t2": corr}
    return best


def profile(spec: str, tau: float) -> dict:
    from ..datasets import build as build_dataset
    from ..mitigation import fit_exponentiated_gradient
    from ..models import build as build_model
    from ..preprocessing import prepare

    dataset = build_dataset(spec).load()
    rows = []
    for seed in range(SEEDS):
        split = prepare(dataset, random_state=seed)
        priv = np.asarray(split.a_test == dataset.privileged_value)
        y = np.asarray(split.y_test).astype(float)
        base = build_model("logistic_regression", random_state=seed)
        base.fit(split.X_train, split.y_train)
        scores = base.predict_proba(split.X_test)[:, 1]
        mitigated = fit_exponentiated_gradient(
            build_model(f"logistic_regression@{tau}", random_state=seed),
            split.X_train, split.y_train, split.a_train,
            constraint="demographic_parity", eps=0.01)
        p1 = np.asarray(mitigated._pmf_predict(split.X_test))[:, 1]
        lottery = {
            "rate": float(p1.mean()),
            "gap": abs(float(p1[priv].mean()) - float(p1[~priv].mean())),
            "accuracy": expected_accuracy(p1, y),
        }
        alternative = search(scores, y, priv, lottery["rate"],
                             max(lottery["gap"], 0.01))
        rows.append({
            "seed": seed, **{f"lottery_{k}": v for k, v in lottery.items()},
            "found": alternative is not None,
            **({f"alt_{k}": v for k, v in alternative.items()} if alternative else {}),
        })
    frame = pd.DataFrame(rows)
    found = frame[frame["found"]]
    return {
        "arm": f"{spec}@{tau:g}",
        "seeds_with_alternative": int(frame["found"].sum()),
        "lottery_accuracy": round(float(frame["lottery_accuracy"].mean()), 4),
        "alt_accuracy": (round(float(found["alt_accuracy"].mean()), 4)
                         if len(found) else None),
        "alt_beats_or_ties": (int((found["alt_accuracy"]
                                   >= found["lottery_accuracy"] - 1e-6).sum())
                              if len(found) else 0),
        "alt_corr_above": (round(float(found["alt_corr_above_t2"].mean()), 3)
                           if len(found) else None),
        "detail": frame,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one arm's population (default: both)")
    args = parser.parse_args()

    OUT = research_dir("routes")
    summaries = []
    for spec, tau in ARMS:
        if args.dataset and args.dataset != spec:
            continue
        result = profile(spec, tau)
        detail = result.pop("detail")
        detail.round(6).to_csv(
            OUT / f"mixture_optimality_{spec.replace(':', '_')}.csv", index=False)
        summaries.append(result)
        print(pd.DataFrame(summaries[-1:]).to_string(index=False), flush=True)

    frame = pd.DataFrame(summaries)
    frame.to_csv(OUT / "mixture_optimality.csv", index=False)
    print("\nCOMPAS is below the noise floor and carries direction only, "
          "as everywhere in this project.")
    print(f"wrote {OUT}/mixture_optimality.csv")


if __name__ == "__main__":
    main()
