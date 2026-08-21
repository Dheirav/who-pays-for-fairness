"""Who pays for the fairness fix? -- incidence analysis of every mitigation.

This experiment is **not** in the initiation document. It exists because the ablation
table there answers "did the gap close?" and cannot answer "how?", and the second
question is the one that decides whether a mitigation is defensible. See
:mod:`src.incidence` for the decomposition, the Mittelstadt et al. (2023) argument
behind it, and Ferry et al. (2023, arXiv:2302.07185), who published the same audit
axes first. What is new here is which populations the instrument is pointed at, not
the instrument.

Three things are measured for each method, all against the *same* baseline on the
*same* split, so nothing is confounded by resampling:

1. **Gap decomposition** -- what share of each closed gap came from the privileged
   group losing ground rather than the unprivileged group gaining it.
2. **Individual churn** -- how many test subjects had their decision reversed, per
   group and per direction. A group's rate can be unchanged while its members trade
   places, and only this catches that.
3. **Arbitrariness floor** -- for the randomized reductions classifiers, how much two
   draws from the *same* fitted model disagree with each other. Churn below this floor
   is not caused by the fairness constraint at all; it is the method being
   non-deterministic. Reporting churn without it overstates what the constraint did.

Usage:
    python -m src.experiments.run_who_pays
    python -m src.experiments.run_who_pays --seeds 0 1 2 3 4
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..datasets import build as build_dataset
from ..incidence import (
    churn_attribution,
    decompose_gap,
    disagreement,
    flip_counts,
    outcome_total,
    people_incidence,
)
from ..metrics import evaluate
from ..results_io import output_dir, save
from .methods import METHOD_ORDER, STOCHASTIC_AT_PREDICT, MethodParams, fit_all

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"

MITIGATIONS = [m for m in METHOD_ORDER if m != "baseline"]

# Second draw from a randomized classifier, for the arbitrariness floor. Any value
# differing from the fit seed works; it is fixed so the number is reproducible.
ALT_PREDICT_SEED = 9_999


def run_seed(dataset, seed: int, params: MethodParams, *, detail: bool = False) -> list[dict]:
    from ..preprocessing import prepare

    split = prepare(dataset, random_state=seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }

    predictors, _ = fit_all(split, seed, params)
    predictions = {name: fn(seed) for name, fn in predictors.items()}
    y_base = predictions["baseline"]
    # Carried on every row so one run answers both "who paid" and "what did
    # constraining one metric cost the other" -- the latter needs the unmitigated
    # reference beside each mitigated result, and refitting to get it would double
    # the cost of a multi-population sweep.
    base_scores = evaluate(split.y_test, y_base, split.a_test, label="baseline", **group_kw)

    rows = []
    for name in MITIGATIONS:
        y_mit = predictions[name]
        decomposition = decompose_gap(
            split.y_test, split.a_test, y_base, y_mit, **group_kw
        )
        flips = flip_counts(split.a_test, y_base, y_mit, **group_kw)
        totals = outcome_total(y_base, y_mit)
        scores = evaluate(split.y_test, y_mit, split.a_test, label=name, **group_kw)

        # Arbitrariness floor: two draws from one fit. Zero for deterministic methods.
        floor = (
            disagreement(y_mit, predictors[name](ALT_PREDICT_SEED))
            if name in STOCHASTIC_AT_PREDICT
            else 0.0
        )

        selection = decomposition.loc["selection_rate"]
        tpr = decomposition.loc["tpr"]
        people = people_incidence(flips)
        total_churn = disagreement(y_base, y_mit)
        rows.append({
            "seed": seed,
            "method": name,
            "accuracy": scores["accuracy"],
            "dp_diff": scores["demographic_parity_diff"],
            "eo_diff": scores["equalized_odds_diff"],
            "baseline_accuracy": base_scores["accuracy"],
            "baseline_dp_diff": base_scores["demographic_parity_diff"],
            "baseline_eo_diff": base_scores["equalized_odds_diff"],
            "n_priv": int((split.a_test == dataset.privileged_value).sum()),
            "n_unpriv": int((split.a_test == dataset.unprivileged_value).sum()),
            # -- selection-rate gap (the demographic parity story) --
            "dp_closure": selection["closure"],
            "dp_from_priv_loss": selection["from_privileged_loss"],
            "dp_from_unpriv_gain": selection["from_unprivileged_gain"],
            "dp_share_levelling_down": selection["share_levelling_down"],
            "dp_verdict": selection["verdict"],
            # -- TPR gap (who gets the outcome they qualified for) --
            "tpr_closure": tpr["closure"],
            "tpr_share_levelling_down": tpr["share_levelling_down"],
            "tpr_verdict": tpr["verdict"],
            # -- individual incidence --
            "priv_lost": flips.loc["privileged", "lost"],
            "priv_gained": flips.loc["privileged", "gained"],
            "unpriv_lost": flips.loc["unprivileged", "lost"],
            "unpriv_gained": flips.loc["unprivileged", "gained"],
            "pct_churn_priv": flips.loc["privileged", "pct_churn"],
            "pct_churn_unpriv": flips.loc["unprivileged", "pct_churn"],
            # Same question as dp_share_levelling_down, but counted in people rather
            # than rates -- the two disagree because the groups differ in size.
            "people_share_levelling_down": people["people_share_levelling_down"],
            "lost_per_gained": people["lost_per_gained"],
            "net_favourable_change": people["net_favourable_change"],
            "total_churn": total_churn,
            "arbitrariness_floor": floor,
            "churn_that_is_noise": churn_attribution(total_churn, floor),
            # -- aggregate welfare --
            "positives_delta": totals["delta"],
            "positives_pct_change": totals["pct_change"],
        })

        if detail:
            print(f"\n[{name}]")
            print(decomposition[[
                "priv_before", "priv_after", "unpriv_before", "unpriv_after",
                "gap_before", "gap_after", "closure",
                "from_privileged_loss", "from_unprivileged_gain",
                "share_levelling_down", "verdict",
            ]].round(4).to_string())
            print(flips[["n", "gained", "lost", "net", "pct_churn"]].round(2).to_string())
            print(f"  rate-level share paid by privileged : "
                  f"{selection['share_levelling_down']:.3f}")
            print(f"  people-level share paid by privileged: "
                  f"{people['people_share_levelling_down']:.3f}  "
                  f"({people['lost_per_gained']:.2f} lost per 1 gained)")
            print(f"  total favourable outcomes: {totals['positives_before']} -> "
                  f"{totals['positives_after']} ({totals['pct_change']:+.1f}%)")
            if floor:
                print(f"  arbitrariness floor: {floor:.4f} of subjects flip between two "
                      f"draws of the same fitted model -- "
                      f"{100 * churn_attribution(total_churn, floor):.0f}% of this "
                      f"method's churn is its own randomness, not the constraint")

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="replace canonical results produced by a different run")
    parser.add_argument("--dataset", default="adult",
                        help="adult | acs | acs:WY | acs:CA,TX")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--eps", type=float, default=0.01)
    parser.add_argument("--eta", type=float, default=5.0)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    params = MethodParams(eps=args.eps, eta=args.eta, alpha=args.alpha, epochs=args.epochs)

    dataset = build_dataset(args.dataset).load()
    print("=== who pays for the fairness fix? ===")
    print(dataset.base_rates().to_string(index=False))

    all_rows = []
    for seed in args.seeds:
        print(f"\n--- seed {seed} ---", flush=True)
        # Full per-method tables for the first seed only; the rest feed the averages.
        all_rows.extend(run_seed(dataset, seed, params, detail=seed == args.seeds[0]))

    results = pd.DataFrame(all_rows)

    headline = (
        results.groupby("method")[[
            "dp_closure", "dp_from_priv_loss", "dp_from_unpriv_gain",
            "dp_share_levelling_down", "people_share_levelling_down",
            "lost_per_gained", "positives_pct_change",
        ]].mean().round(4).reindex(MITIGATIONS)
    )
    print("\n=== demographic-parity gap: where the closure came from (mean over seeds) ===")
    print(headline.to_string())
    print("\ndp_share_levelling_down     = share of the closed gap paid for by the")
    print("                              privileged group losing selection *rate*.")
    print("people_share_levelling_down = the same question counted in *people*. It is")
    print("                              higher because the privileged group is larger,")
    print("                              so equal rate movement is unequal headcount.")
    print("lost_per_gained             = favourable decisions destroyed per one created.")

    churn = (
        results.groupby("method")[[
            "priv_lost", "priv_gained", "unpriv_lost", "unpriv_gained",
            "net_favourable_change", "total_churn", "arbitrariness_floor",
            "churn_that_is_noise",
        ]].mean().round(4).reindex(MITIGATIONS)
    )
    print("\n=== individual decisions reversed (mean counts per test set) ===")
    print(churn.to_string())
    print("\ntotal_churn and arbitrariness_floor are fractions of the test set.")
    print("churn_that_is_noise = floor / total_churn: the share of a method's")
    print("individual-level effect that is re-sampling, not the fairness constraint.")
    OUT = output_dir(dataset.name)
    for path in save(OUT, "who_pays", {"runs": results, "summary": headline},
                     params=dict(seeds=args.seeds, eps=args.eps, eta=args.eta, alpha=args.alpha, epochs=args.epochs), force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
