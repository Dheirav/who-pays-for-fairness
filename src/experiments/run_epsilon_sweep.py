"""Does levelling down depend on how tight the constraint is?

Document 05 found that every mitigation closed the fairness gap mostly by withdrawing
favourable decisions from the advantaged group, and that all five shrank the total
number of approvals. Every one of those runs used a single constraint slack,
ε = 0.01 -- almost no slack at all.

That leaves an obvious objection, and it is a good one: **at ε = 0.01 the model may
have no room to do anything else.** If levelling down is an artifact of an unusually
tight constraint, the honest recommendation is "loosen it", and the finding is much
narrower than document 05 implies. If it persists across the whole range, the finding
is a property of optimising a ratio, and loosening the constraint only buys a smaller
version of the same behaviour.

This sweeps ε and re-runs the incidence decomposition at each value. The measurement
is the same one in :mod:`src.incidence`; only the constraint strength changes.

Usage:
    python -m src.experiments.run_epsilon_sweep
    python -m src.experiments.run_epsilon_sweep --seeds 0 1 2 --eps 0.005 0.05 0.2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..datasets import build as build_dataset
from ..incidence import decompose_gap, flip_counts, outcome_total, people_incidence
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


# From "almost no slack" to "looser than the unmitigated gap", so the sweep spans the
# whole meaningful range: the baseline violation is ~0.186, so ε = 0.20 imposes no
# real constraint and should reproduce the baseline.
EPSILONS = [0.005, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20]


def run(dataset, seed: int, eps: float) -> dict:
    split = prepare(dataset, random_state=seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }

    baseline = build(BASE_MODEL, random_state=seed).fit(split.X_train, split.y_train)
    y_base = baseline.predict(split.X_test)

    model = fit_exponentiated_gradient(
        build(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint="demographic_parity", eps=eps,
    )
    y_mit = model.predict(split.X_test, random_state=seed)

    scores = evaluate(split.y_test, y_mit, split.a_test, label="expgrad_dp", **group_kw)
    selection = decompose_gap(
        split.y_test, split.a_test, y_base, y_mit, **group_kw
    ).loc["selection_rate"]
    flips = flip_counts(split.a_test, y_base, y_mit, **group_kw)
    people = people_incidence(flips)
    pie = outcome_total(y_base, y_mit)

    return {
        "seed": seed,
        "eps": eps,
        "accuracy": scores["accuracy"],
        "dp_diff": scores["demographic_parity_diff"],
        "eo_diff": scores["equalized_odds_diff"],
        "closure": selection["closure"],
        "rate_share_levelling_down": selection["share_levelling_down"],
        "people_share_levelling_down": people["people_share_levelling_down"],
        "lost_per_gained": people["lost_per_gained"],
        "priv_lost": flips.loc["privileged", "lost"],
        "unpriv_gained": flips.loc["unprivileged", "gained"],
        "pie_change_pct": pie["pct_change"],
        "verdict": selection["verdict"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="replace canonical results produced by a different run")
    parser.add_argument("--dataset", default="adult",
                        help="adult | acs | acs:WY | acs:CA,TX")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--eps", type=float, nargs="+", default=EPSILONS)
    args = parser.parse_args()

    dataset = build_dataset(args.dataset).load()
    print("=== does levelling down survive a looser constraint? ===")
    print(f"base classifier: {BASE_MODEL}; unmitigated DP gap is ~0.186, so the largest")
    print("epsilon here imposes no real constraint and should reproduce the baseline.\n")

    rows = []
    for eps in args.eps:
        print(f"--- eps = {eps} ---", flush=True)
        for seed in args.seeds:
            rows.append(run(dataset, seed, eps))

    results = pd.DataFrame(rows)
    summary = results.groupby("eps")[[
        "accuracy", "dp_diff", "eo_diff", "closure", "rate_share_levelling_down",
        "people_share_levelling_down", "lost_per_gained", "priv_lost",
        "unpriv_gained", "pie_change_pct",
    ]].mean().round(4)

    print(f"\n=== over {len(args.seeds)} seeds ===")
    print(summary.to_string())
    print("\nIf levelling down were an artifact of a tight constraint, the shares would")
    print("fall and pie_change_pct would approach zero as eps grows. Read those two")
    print("columns together: a shrinking pie with a stable share means the behaviour is")
    print("the same at every strength, just smaller.")
    OUT = output_dir(dataset.name)
    for path in save(OUT, "epsilon_sweep", {"runs": results, "summary": summary},
                     params=dict(seeds=args.seeds, eps=args.eps), force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
