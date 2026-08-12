"""Why does constraining demographic parity cost equalized odds *this much*?

**Written and committed before any of it was computed.** docs/13 records what happens
otherwise: a correlation chosen after seeing which correlations existed, stated
confidently, and wrong. The predictions below have their thresholds fixed here.

The open question
-----------------
The impossibility results (Kleinberg et al. 2016; Chouldechova 2017) say demographic
parity and equalized odds cannot both hold unless base rates are equal. That settles
*whether* the conflict exists. It says nothing about its size.

P2 in docs/11 proposed the obvious answer -- the cost tracks the base-rate gap -- and it
failed: r = +0.241 across ten populations, with Utah holding the largest gap in the study
while equalized odds *improved* there. Two further candidates were ruled out at the same
time: the amount of DP actually removed (r = +0.111) and the baseline DP gap (r = +0.044).

So the conflict is near-universal in direction (9 of 10 populations) and unpredicted in
magnitude. That is an honest loose end and this module is an attempt to close it.

The hypothesis
--------------
Base rates alone cannot be the answer, because they describe the *labels* and say nothing
about the classifier's ability to act on them. Under demographic parity both groups are
held to one selection rate ``s``. A group whose base rate is far from ``s`` must have
people moved across its decision boundary. How much that costs in TPR and FPR depends on
**how well the model separates positives from negatives inside that group**: where scores
are well separated, the selection rate can move a long way while touching mostly
borderline cases; where they are not, the same movement rips through the middle of the
distribution and error rates move sharply.

So the proposed quantity is base-rate pressure *divided by* within-group separability --
how far each group must be pushed, weighted by how much it hurts to push it.

Stated in advance, so they can fail
-----------------------------------
**C1 -- separability predicts the cost where the base-rate gap does not.** Across the
pooled populations, |r| between the EO cost and within-group separability exceeds 0.5,
against the base-rate gap's +0.241.

**C2 -- the combination beats either part alone.** ``base_rate_gap / mean_group_auc``
correlates with the cost more strongly than either the gap or separability separately. If
this fails but C1 holds, separability is the whole story and base rates are irrelevant,
which would be a stronger and stranger result.

**C3 -- it holds within each arm separately.** Not only pooled. Same reason as A3 in
:mod:`analyse_arms`: a relationship that appears only after pooling is a relationship
fitted to the pooled data.

If all three fail, the honest report is that the magnitude of the DP/EO conflict is not
predicted by any quantity this project has tested, and that stays written down rather
than being retried until something correlates.

The confirmation, added after C1-C3 failed
------------------------------------------
They did fail, and the explanation that emerged instead -- that post-constraint EO is
independent of pre-constraint EO, so the cost is dominated by the baseline -- was found by
looking at those failures rather than by testing a stated prediction. document 14 reports
it as exploratory and names the test that could refute it:

    if post-constraint EO is a property of the constrained *solution* rather than of the
    model it replaced, two different mitigations satisfying the same DP bound on the same
    population should land at similar EO.

``expgrad_dp`` and ``gridsearch_dp`` both target DP <= 0.01 and both already exist in
every run, so this costs no refits. The test was written into document 14 and committed
before being run, which is what separates it from fitting a test to a known answer.

**D0 -- precondition.** Both methods must actually satisfy comparable DP, or they are not
two solutions to the same problem and nothing below means anything. Mean |DP difference
between the methods| must be under 0.02.

**D1 -- the two methods agree across populations.** r(EO after expgrad, EO after
gridsearch) > 0.7.

**D2 -- they agree more than populations differ.** Mean |EO difference between methods|
is smaller than the standard deviation of EO across populations. If the choice of
mitigation matters as much as the choice of population, the endpoint is not a property of
the constraint and document 14's explanation is wrong.

Usage:
    python -m src.experiments.analyse_conflict
    python -m src.experiments.analyse_conflict --seeds 0 1 2
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from ..datasets import build as build_dataset
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import research_dir
from .analyse_sweep import DEFAULT_STATES, SEX_ARM, correlate, output_dir

RACE_ARM = "RAC1P"

# C1's bar. The base-rate gap manages +0.241; a replacement that cannot clear 0.5 is not
# an explanation, it is another weak correlation.
MIN_USEFUL_CORRELATION = 0.5

# Below this, no verdict is reported. analyse_arms shipped without this guard and
# promptly announced a result from two of nine populations; the first run of *this*
# module then printed "C3 FAILS" from three. A module that answers before the data can
# support an answer is worse than one that stays silent, because it looks like an answer.
MIN_POPULATIONS_PER_ARM = 8

# D0/D1/D2, fixed here before the confirmation was run. See the docstring.
MAX_DP_DISAGREEMENT = 0.02
MIN_METHOD_AGREEMENT = 0.7


def within_group_separability(dataset, seeds: list[int]) -> dict[str, float]:
    """Mean ROC AUC of the unconstrained model, computed inside each group.

    Pooled AUC will not do. A model can look highly discriminative overall purely because
    it separates the two protected groups from each other -- which is exactly the
    behaviour this project has spent documents establishing it does. Only within-group
    AUC measures the thing the hypothesis is about: given that you must move this group's
    selection rate, how expensive is the move?
    """
    scores = []
    for seed in seeds:
        split = prepare(dataset, random_state=seed)
        model = build_model("decision_tree", random_state=seed)
        model.fit(split.X_train, split.y_train)
        probability = model.predict_proba(split.X_test)[:, 1]

        for value in (dataset.privileged_value, dataset.unprivileged_value):
            mask = np.asarray(split.a_test) == value
            y, p = np.asarray(split.y_test)[mask], probability[mask]
            # A group with one label present has no ranking to score; skipping it is not
            # a judgement call, the quantity is undefined.
            if len(np.unique(y)) < 2:
                continue
            scores.append(roc_auc_score(y, p))

    return {"group_auc": float(np.mean(scores)) if scores else float("nan"),
            "group_auc_min": float(np.min(scores)) if scores else float("nan")}


def population_row(key: str, label: str, arm: str, seeds: list[int]) -> dict | None:
    """One population's EO cost alongside the quantities proposed to explain it."""
    dataset = build_dataset(key).load()
    path = output_dir(dataset.name) / "who_pays_runs.csv"
    if not path.exists():
        return None

    runs = pd.read_csv(path)
    dp = runs[runs["method"] == "expgrad_dp"]
    if dp.empty:
        return None
    grid = runs[runs["method"] == "gridsearch_dp"]

    rates = dataset.base_rates().set_index("group")
    gap = rates.loc["privileged", "P(y=1)"] - rates.loc["unprivileged", "P(y=1)"]
    separability = within_group_separability(dataset, seeds)

    return {
        "population": label,
        "arm": arm,
        "n": dataset.n_samples,
        "base_rate_gap": gap,
        "baseline_eo": float(dp["baseline_eo_diff"].mean()),
        "eo_expgrad": float(dp["eo_diff"].mean()),
        "dp_expgrad": float(dp["dp_diff"].mean()),
        "eo_gridsearch": float(grid["eo_diff"].mean()) if not grid.empty else np.nan,
        "dp_gridsearch": float(grid["dp_diff"].mean()) if not grid.empty else np.nan,
        "eo_cost": float((dp["eo_diff"] - dp["baseline_eo_diff"]).mean()),
        **separability,
        # The proposed composite: pressure to move, weighted by the cost of moving.
        "pressure_over_separability": gap / separability["group_auc"]
        if separability["group_auc"] else np.nan,
    }


def report(frame: pd.DataFrame, title: str) -> dict[str, float]:
    print(f"\n{title}  ({len(frame)} populations)")
    correlations = {}
    for column in ("base_rate_gap", "group_auc", "group_auc_min",
                   "pressure_over_separability"):
        r, _ = correlate(frame, column, "eo_cost")
        correlations[column] = r
        print(f"  r(eo_cost, {column:26}) = {r:+.3f}")
    return correlations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="+", default=DEFAULT_STATES)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    args = parser.parse_args()

    populations = [("adult", "Adult", SEX_ARM)]
    populations += [(f"acs:{s}", s, SEX_ARM) for s in args.states]
    populations += [(f"acs:{s}:{RACE_ARM}", s, RACE_ARM) for s in args.states]

    rows = []
    for key, label, arm in populations:
        row = population_row(key, label, arm, args.seeds)
        if row is None:
            print(f"  skipped {label} [{arm}]: no who-pays results")
            continue
        rows.append(row)
        print(f"  {label:6} [{arm:5}]  eo_cost {row['eo_cost']:+.4f}  "
              f"group_auc {row['group_auc']:.4f}", flush=True)

    frame = pd.DataFrame(rows)

    short = [(arm, len(group)) for arm, group in frame.groupby("arm")
             if len(group) < MIN_POPULATIONS_PER_ARM]
    if short:
        out = research_dir("conflict")
        frame.to_csv(out / "conflict_predictors_partial.csv", index=False)
        raise SystemExit(
            "refusing to report: "
            + "; ".join(f"{arm} arm has {n} populations, needs "
                        f"{MIN_POPULATIONS_PER_ARM}" for arm, n in short)
            + f"\nthe measurements are written to {out}/conflict_predictors_partial.csv"
            + "\nbut no verdict follows from them"
        )

    print("\n" + "=" * 78)
    print("C1  separability predicts the cost where the base-rate gap does not")
    print("=" * 78)
    pooled = report(frame, "pooled")
    best_separability = max(abs(pooled["group_auc"]), abs(pooled["group_auc_min"]))
    c1 = best_separability > MIN_USEFUL_CORRELATION
    print(f"\n  -> C1 {'HOLDS' if c1 else 'FAILS'}: separability reaches "
          f"|r| = {best_separability:.3f} against the base-rate gap's "
          f"{abs(pooled['base_rate_gap']):.3f} (bar: {MIN_USEFUL_CORRELATION})")

    print("\n" + "=" * 78)
    print("C2  the combination beats either part alone")
    print("=" * 78)
    combined = abs(pooled["pressure_over_separability"])
    parts = max(abs(pooled["base_rate_gap"]), best_separability)
    c2 = combined > parts
    print(f"  combined |r| = {combined:.3f}   best single part |r| = {parts:.3f}")
    print(f"  -> C2 {'HOLDS' if c2 else 'FAILS'}")

    print("\n" + "=" * 78)
    print("C3  it holds within each arm separately")
    print("=" * 78)
    per_arm = {arm: report(group, f"[{arm}]")
               for arm, group in frame.groupby("arm", sort=False)}
    c3 = all(
        max(abs(values["group_auc"]), abs(values["pressure_over_separability"]))
        > MIN_USEFUL_CORRELATION
        for values in per_arm.values()
    )
    print(f"\n  -> C3 {'HOLDS' if c3 else 'FAILS'}: the relationship "
          f"{'survives' if c3 else 'does not survive'} inside each arm")

    if not (c1 or c2):
        print("\n  NOTE: neither C1 nor C2 held. The honest conclusion is that the")
        print("  magnitude of the DP/EO conflict is not predicted by any quantity this")
        print("  project has tested. That is a result and is to be reported as one.")

    print("\n" + "=" * 78)
    print("D   does the endpoint belong to the constrained solution?")
    print("=" * 78)
    both = frame.dropna(subset=["eo_gridsearch"])
    dp_disagreement = (both["dp_expgrad"] - both["dp_gridsearch"]).abs().mean()
    eo_disagreement = (both["eo_expgrad"] - both["eo_gridsearch"]).abs().mean()
    spread = both["eo_expgrad"].std()
    r_methods, _ = correlate(both, "eo_expgrad", "eo_gridsearch")
    r_base, _ = correlate(both, "baseline_eo", "eo_expgrad")

    print(both[["population", "arm", "baseline_eo", "eo_expgrad", "eo_gridsearch"]]
          .round(4).to_string(index=False))
    print(f"\n  mean |DP difference between methods| = {dp_disagreement:.4f} "
          f"(D0 bar: < {MAX_DP_DISAGREEMENT})")
    d0 = dp_disagreement < MAX_DP_DISAGREEMENT
    print(f"  -> D0 {'HOLDS' if d0 else 'FAILS'}"
          f"{'' if d0 else ': the two are not solving the same problem, so D1/D2 are void'}")

    print(f"\n  r(EO expgrad, EO gridsearch)         = {r_methods:+.3f} "
          f"(D1 bar: > {MIN_METHOD_AGREEMENT})")
    d1 = r_methods > MIN_METHOD_AGREEMENT
    print(f"  -> D1 {'HOLDS' if d1 else 'FAILS'}")

    print(f"\n  mean |EO difference between methods| = {eo_disagreement:.4f}")
    print(f"  sd of EO across populations          = {spread:.4f}")
    d2 = eo_disagreement < spread
    print(f"  -> D2 {'HOLDS' if d2 else 'FAILS'}: the choice of mitigation matters "
          f"{'less' if d2 else 'as much as or more'} than the choice of population")

    print(f"\n  for reference, r(baseline EO, EO after) = {r_base:+.3f} -- the exploratory")
    print( "  finding this section exists to confirm or refute")
    if d0 and d1 and d2:
        print("\n  -> document 14's explanation survives a test it could have failed.")
    else:
        print("\n  -> document 14's explanation does NOT survive. It is exploratory and")
        print("     must be reported as refuted, not quietly rewritten.")

    out = research_dir("conflict")
    frame.to_csv(out / "conflict_predictors.csv", index=False)
    print(f"\nwrote {out}/conflict_predictors.csv")


if __name__ == "__main__":
    main()
