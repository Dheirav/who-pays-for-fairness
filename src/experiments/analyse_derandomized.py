"""Does the direction survive the derandomization a deployer would be forced to apply?

**Individual work, beyond the course submission. Post-hoc test, labelled as such.**

The third council's bank examiner made the sharpest deployment point: a US lender
operating under adverse-action-notice duties cannot deploy a randomized mixture, so the
model that actually ships is a *deterministic* extraction of it --- and every direction
result in this project is measured on the mixture. If the direction does not survive
extraction, the audit predicts a model nobody deploys.

Two standard extractions of the mixture's per-person probability $p_1(x)$, both measured
against the same baseline:

* **majority** --- predict favourable where $p_1(x) \\ge 0.5$; the naive reading of the
  mixture as a classifier.
* **rate-matched** --- threshold $p_1$ at the quantile that reproduces the mixture's own
  expected selection rate; the extraction a deployer who trusts the mitigation's operating
  point would choose. Its pool size copies the mixture's by construction, so the question
  it answers is whether the *parity gap* survives, while majority answers whether the
  *pool direction* does.

For each natural arm: baseline pool and gap, the mixture's expected pool change and gap,
and both extractions' pool changes and gaps, seed-averaged. The direction verdict is the
sign of the extraction's pool change against the mixture's.

Run:  python -m src.experiments.analyse_derandomized
      python -m src.experiments.analyse_derandomized --dataset acs:OR
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir

# The natural-arm cohort of the third council's probes, spanning both directions.
POPULATIONS = ["adult", "acs:AL", "acs:OR", "acs:KY", "acs:SC", "acs:CT",
               "acs:FL", "acs:VA", "acs:MA", "dutch"]


def rates(pred: np.ndarray, priv: np.ndarray) -> tuple[float, float]:
    return float(pred.mean()), abs(float(pred[priv].mean()) - float(pred[~priv].mean()))


def profile(spec: str, seeds: int = 5) -> dict:
    from ..datasets import build as build_dataset
    from ..mitigation import fit_exponentiated_gradient
    from ..models import build as build_model
    from ..preprocessing import prepare

    dataset = build_dataset(spec).load()
    rows = []
    for seed in range(seeds):
        split = prepare(dataset, random_state=seed)
        priv = np.asarray(split.a_test == dataset.privileged_value)
        base = build_model("logistic_regression", random_state=seed)
        base.fit(split.X_train, split.y_train)
        base_pred = np.asarray(base.predict(split.X_test)).astype(float)
        mitigated = fit_exponentiated_gradient(
            build_model("logistic_regression", random_state=seed),
            split.X_train, split.y_train, split.a_train,
            constraint="demographic_parity", eps=0.01)
        p1 = np.asarray(mitigated._pmf_predict(split.X_test))[:, 1]

        r_base, gap_base = rates(base_pred, priv)
        # The mixture's expectations, which every stored result in this project reports.
        r_mix = float(p1.mean())
        gap_mix = abs(float(p1[priv].mean()) - float(p1[~priv].mean()))
        majority = (p1 >= 0.5).astype(float)
        # Rate-matched: keep exactly the mixture's expected number of favourables,
        # taking the highest-probability people first.
        matched = (p1 >= np.quantile(p1, 1.0 - r_mix)).astype(float)
        r_maj, gap_maj = rates(majority, priv)
        r_mat, gap_mat = rates(matched, priv)
        rows.append({
            "r_base": r_base, "gap_base": gap_base,
            "d_mix": 100.0 * (r_mix - r_base) / r_base, "gap_mix": gap_mix,
            "d_majority": 100.0 * (r_maj - r_base) / r_base, "gap_majority": gap_maj,
            "d_matched": 100.0 * (r_mat - r_base) / r_base, "gap_matched": gap_mat,
        })
    mean = pd.DataFrame(rows).mean()
    sign = lambda x: "up" if x > 0 else "down"
    return {"population": spec, **{k: float(v) for k, v in mean.items()},
            "direction_mix": sign(mean["d_mix"]),
            "direction_majority": sign(mean["d_majority"]),
            "direction_matched": sign(mean["d_matched"]),
            "majority_agrees": sign(mean["d_majority"]) == sign(mean["d_mix"]),
            "seeds": len(rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one population spec (default: the cohort)")
    args = parser.parse_args()

    specs = [s for s in POPULATIONS if not args.dataset or s == args.dataset]
    rows = []
    for spec in specs:
        rows.append(profile(spec))
        print(pd.DataFrame(rows[-1:]).round(3).to_string(
            index=False, header=(len(rows) == 1)), flush=True)
    frame = pd.DataFrame(rows)

    agree = int(frame["majority_agrees"].sum())
    print(f"\nmajority extraction agrees with the mixture's direction on "
          f"{agree}/{len(frame)} populations")
    print("rate-matched extraction preserves the pool by construction; its question is "
          "the gap:")
    print(frame[["population", "gap_base", "gap_mix", "gap_majority", "gap_matched"]]
          .round(4).to_string(index=False))

    OUT = research_dir("derandomized")
    frame.round(6).to_csv(OUT / "derandomized.csv", index=False)
    print(f"\nwrote {OUT}/derandomized.csv")


if __name__ == "__main__":
    main()
