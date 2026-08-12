"""Plant a *pair* of redundant columns and watch attribution move between them.

**Written and committed before it was run.** Predictions and thresholds fixed below.

The third candidate
-------------------
Two explanations for document 06's attribution shift have been tested and refuted by
intervention. Document 16 killed "the constraint seeks reconstructions of the protected
attribute" -- a planted pure proxy is used *less* as it sharpens. Document 17 killed the
replacement, "the constraint seeks features with outcome signal" -- a planted outcome
predictor is not favoured either, and across six cells the constrained model tracked the
unconstrained one to within 0.03 attribution share while the share itself moved ninefold.

Document 17 recorded a third candidate with its premise measured and explicitly not
claimed: attribution moved between the **two most redundant features in Adult**.

| pair | Cramér's V |
|---|---|
| ``relationship`` <-> ``marital-status`` | **0.487** |
| next closest pair in Adult | 0.217 |
| the planted column and its strongest partner | 0.179 |

Shapley values divide credit between collinear features, and small weight changes can
reallocate that credit substantially without the model's behaviour changing at all. Both
planted columns so far had no redundant partner, which would explain why nothing moved in
either experiment. This tests it directly, at the same standard the two rejected
explanations were held to.

The Adult numbers to beat
-------------------------
Document 06 measured ``relationship`` 0.075 -> 0.189 (+0.114) and ``marital-status``
0.304 -> 0.235 (-0.069). The pair moves 0.183 in total magnitude while its *combined*
share moves only +0.045 -- a reallocation ratio of about 4. That is the signature this
experiment looks for: large movement between two features, small movement of their sum.

The manipulation
----------------
Two columns are planted, ``SYNTH_A`` and ``SYNTH_B``. Each independently indicates the
label with probability ``OUTCOME`` -- the setting document 17 found produces a 0.21
attribution share, so both are genuinely used. ``SYNTH_B`` then copies ``SYNTH_A`` with
probability ``redundancy`` and is otherwise drawn independently, so the two are equally
informative at every setting and differ only in how redundant they are with each other.

Stated in advance, so they can fail
-----------------------------------
**K0 -- manipulation check.** Cramér's V between the planted pair rises with
``redundancy``, while each column's own usefulness stays flat.

**K1 -- the test.** The swap magnitude ``|excess_A| + |excess_B|`` rises with redundancy
by more than ``MIN_SWAP``. This is reallocation between collinear features.

**K2 -- it is reallocation, not a net shift.** The pair's combined excess
``|excess_A + excess_B|`` stays below the swap magnitude at high redundancy. If the pair
gains attribution as a whole, something other than reallocation is happening.

**K3 -- behaviour does not change.** Accuracy and the achieved DP violation are flat
across redundancy levels. Reallocation that moved decisions would not be reallocation.

If K1 fails, the third explanation is refuted like the first two, and document 06's
attribution shift is unexplained with no remaining candidate this project can name. That
outcome is to be reported plainly rather than followed by a fourth guess.

Usage:
    python -m src.experiments.run_collinear --dataset acs:AL
"""

from __future__ import annotations

import argparse
from dataclasses import replace

import numpy as np
import pandas as pd

from ..datasets import build as build_dataset
from ..explain import aggregate_attributions, kernel_explainer_values, source_feature_map
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL
from .run_injection import DETERMINED_SHARE

A, B = "SYNTH_A", "SYNTH_B"
LEVEL_OTHER = "SYN-C"

# Document 17's top setting, where a planted column reaches a 0.21 attribution share.
# Both columns must actually be used or there is no credit to reallocate.
OUTCOME = 0.8

DEFAULT_REDUNDANCIES = [0.0, 0.5, 1.0]

# K1's bar, in attribution share. Adult's pair swaps 0.183; a ninth of that is a
# conservative floor, and matches MIN_RELOCATION used by the two earlier experiments.
MIN_SWAP = 0.02


def cramers_v(left: pd.Series, right: pd.Series) -> float:
    from scipy.stats import chi2_contingency

    table = pd.crosstab(left, right)
    if min(table.shape) < 2:
        return float("nan")
    chi2 = chi2_contingency(table)[0]
    n = table.to_numpy().sum()
    return float(np.sqrt(chi2 / (n * (min(table.shape) - 1))))


def _outcome_column(is_positive, determined, rng) -> np.ndarray:
    bit = np.where(rng.random(len(is_positive)) < OUTCOME, is_positive, ~is_positive)
    column = np.full(len(is_positive), LEVEL_OTHER, dtype=object)
    column[determined & bit] = "SYN-H"
    column[determined & ~bit] = "SYN-L"
    return column


def inject_pair(dataset, redundancy: float, random_state: int):
    """Two equally-informative planted columns whose mutual redundancy is `redundancy`."""
    rng = np.random.default_rng(random_state)
    n = len(dataset.X)
    is_positive = (dataset.y.to_numpy() == 1)

    # Separate `determined` masks. Sharing one made both columns take their
    # uninformative level on exactly the same rows, which coupled them at V = 0.74 even
    # with redundancy set to zero -- above Adult's 0.487, so the design had no
    # low-redundancy arm at all. Caught by measuring the manipulation before spending
    # compute on it.
    determined_a = rng.random(n) < DETERMINED_SHARE
    determined_b = rng.random(n) < DETERMINED_SHARE

    column_a = _outcome_column(is_positive, determined_a, rng)
    independent_b = _outcome_column(is_positive, determined_b, rng)
    # B copies A with probability `redundancy`, else stands on its own draw. Both are
    # built the same way, so they are equally useful at every setting and differ only in
    # how much they duplicate each other.
    copies = rng.random(n) < redundancy
    column_b = np.where(copies, column_a, independent_b)

    X = dataset.X.copy()
    X[A] = pd.Series(column_a, index=X.index).astype(str)
    X[B] = pd.Series(column_b, index=X.index).astype(str)

    return replace(
        dataset,
        name=f"{dataset.name}_pair{redundancy:g}",
        X=X,
        categorical_features=[*dataset.categorical_features, A, B],
        proxy_features=[A, B],
        notes={**dataset.notes, "injected_pair": {"redundancy": redundancy,
                                                  "outcome": OUTCOME}},
    )


def run_one(dataset, redundancy: float, seed: int) -> dict:
    planted = inject_pair(dataset, redundancy, random_state=seed)
    split = prepare(planted, random_state=seed)
    mapping = source_feature_map(split.feature_names, planted.categorical_features,
                                 planted.numeric_features)
    X_train = np.asarray(split.X_train, dtype=float)
    X_test = np.asarray(split.X_test, dtype=float)

    baseline = build_model(BASE_MODEL, random_state=seed)
    baseline.fit(split.X_train, split.y_train)
    expgrad = fit_exponentiated_gradient(
        build_model(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint="demographic_parity", eps=0.01,
    )

    # Matched explainers, for the reason document 16 records: the estimand is a
    # difference between two models, so an exact/sampled pair would bias it directly.
    rng = np.random.default_rng(seed)
    background = X_train[rng.choice(len(X_train), 25, replace=False)]
    instances = X_test[rng.choice(len(X_test), 150, replace=False)]

    base = aggregate_attributions(
        kernel_explainer_values(lambda d: baseline.predict_proba(d)[:, 1],
                                background, instances), mapping)
    mit = aggregate_attributions(
        kernel_explainer_values(lambda d: np.asarray(expgrad._pmf_predict(d))[:, 1],
                                background, instances), mapping)

    excess_a = float(mit.get(A, 0.0) - base.get(A, 0.0))
    excess_b = float(mit.get(B, 0.0) - base.get(B, 0.0))

    group_kw = {"privileged": planted.privileged_value,
                "unprivileged": planted.unprivileged_value}
    y_base = baseline.predict(split.X_test)
    y_mit = expgrad.predict(split.X_test, random_state=seed)
    base_scores = evaluate(split.y_test, y_base, split.a_test, **group_kw)
    mit_scores = evaluate(split.y_test, y_mit, split.a_test, **group_kw)

    return {
        "redundancy": redundancy,
        "seed": seed,
        "cramers_v": cramers_v(planted.X[A], planted.X[B]),
        "base_a": float(base.get(A, 0.0)), "base_b": float(base.get(B, 0.0)),
        "mit_a": float(mit.get(A, 0.0)), "mit_b": float(mit.get(B, 0.0)),
        "excess_a": excess_a, "excess_b": excess_b,
        "swap": abs(excess_a) + abs(excess_b),
        "net": abs(excess_a + excess_b),
        "baseline_accuracy": base_scores["accuracy"],
        "mitigated_accuracy": mit_scores["accuracy"],
        "mitigated_dp": mit_scores["demographic_parity_diff"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="acs:AL")
    parser.add_argument("--redundancies", type=float, nargs="+",
                        default=DEFAULT_REDUNDANCIES)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    dataset = build_dataset(args.dataset).load()
    print(f"=== planting a redundant pair in {dataset.name} ===")
    print("Adult's anchor: relationship +0.114, marital-status -0.069, "
          "swap 0.183, net 0.045\n")

    rows = []
    for redundancy in args.redundancies:
        for seed in args.seeds:
            row = run_one(dataset, redundancy, seed)
            rows.append(row)
            print(f"  redundancy {redundancy:<5} seed {seed}  V {row['cramers_v']:.3f}  "
                  f"excess_a {row['excess_a']:+.4f}  excess_b {row['excess_b']:+.4f}  "
                  f"swap {row['swap']:.4f}  net {row['net']:.4f}", flush=True)

    runs = pd.DataFrame(rows)
    summary = runs.groupby("redundancy")[
        ["cramers_v", "base_a", "base_b", "mit_a", "mit_b",
         "excess_a", "excess_b", "swap", "net",
         "baseline_accuracy", "mitigated_accuracy", "mitigated_dp"]
    ].mean().round(4)
    print("\n=== mean over seeds ===")
    print(summary.to_string())

    low, high = min(args.redundancies), max(args.redundancies)
    print("\n" + "=" * 74)
    v_rise = summary.loc[high, "cramers_v"] - summary.loc[low, "cramers_v"]
    usefulness = (summary["base_a"] + summary["base_b"]).std()
    k0 = v_rise > 0.2 and usefulness < 0.05
    print(f"K0  redundancy rises, usefulness flat   -> {'HOLDS' if k0 else 'FAILS'}  "
          f"(V {summary.loc[low, 'cramers_v']:.3f} -> {summary.loc[high, 'cramers_v']:.3f}, "
          f"pair-share sd {usefulness:.4f})")

    swap_rise = summary.loc[high, "swap"] - summary.loc[low, "swap"]
    k1 = swap_rise > MIN_SWAP
    print(f"K1  attribution swaps more when redundant -> {'HOLDS' if k1 else 'FAILS'}  "
          f"(swap {summary.loc[low, 'swap']:.4f} -> {summary.loc[high, 'swap']:.4f}, "
          f"rise {swap_rise:+.4f}, bar {MIN_SWAP})")

    k2 = summary.loc[high, "net"] < summary.loc[high, "swap"]
    print(f"K2  it is a swap, not a net gain          -> {'HOLDS' if k2 else 'FAILS'}  "
          f"(at redundancy {high}: swap {summary.loc[high, 'swap']:.4f} vs "
          f"net {summary.loc[high, 'net']:.4f})")

    acc_spread = summary["mitigated_accuracy"].std()
    dp_spread = summary["mitigated_dp"].std()
    k3 = acc_spread < 0.01 and dp_spread < 0.01
    print(f"K3  behaviour unchanged across settings   -> {'HOLDS' if k3 else 'FAILS'}  "
          f"(accuracy sd {acc_spread:.4f}, DP sd {dp_spread:.4f})")
    print("=" * 74)
    if k0 and k1 and k2:
        print("Collinearity explains it: the constraint reallocates SHAP credit between")
        print("redundant features without changing what the model does. Adult's shift is")
        print("an attribution artifact of two near-duplicate columns, not a change in")
        print("what the model relies on.")
    elif k0 and not k1:
        print("The third explanation FAILS as well. Document 06's attribution shift is")
        print("unexplained, and this project has no remaining candidate to offer. That is")
        print("the result; a fourth guess would be cheaper than the three that were tested.")

    OUT = output_dir(dataset.name + "_collinear")
    for path in save(OUT, "collinear", {"runs": runs, "summary": summary},
                     params=dict(dataset=args.dataset, redundancies=args.redundancies,
                                 seeds=args.seeds), force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
