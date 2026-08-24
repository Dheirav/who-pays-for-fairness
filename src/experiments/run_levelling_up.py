"""Does making "don't shrink the pie" part of the objective actually work?

Document 05's third finding is that every mitigation in the ablation closed the
demographic-parity gap partly by *withdrawing* favourable decisions: the total number of
positive predictions fell by 7.9% to 22.1%, and not one method closed the gap primarily by
extending favourable decisions to the disadvantaged group. That document ends with a claim
it never tested:

    "If you want the gap closed by levelling up, **that has to be part of the objective**
    -- it will not happen by accident."

This tests it, by adding a floor on the overall selection rate alongside the parity
constraint (:mod:`src.levelling_up`). Three arms on identical splits:

1. **baseline** -- unconstrained.
2. **expgrad_dp** -- demographic parity alone, the ablation's winning row.
3. **expgrad_dp_floor** -- demographic parity *and* a floor at the baseline's own
   selection rate, enforced together in one game rather than patched afterwards.

The honest framing, repeated from :mod:`src.levelling_up`: this is **not a new method**.
Agarwal et al. define constraints as linear in the classifier's conditional moments and a
selection-rate floor is one of those, so it sits inside the base paper's framework. What
is new is the question.

What is measured is not only whether the pie survives but **who pays**, using the same
decomposition as :mod:`src.incidence`. A variant that preserved the total while still
taking from the same people would not be levelling up; it would be levelling down with
compensation elsewhere.

Two knobs exist for the research track and change the arms that are run:

``--constraint equalized_odds`` asks the same question of a criterion that does **not**
mention selection rates. Demographic parity moves the pool of favourable decisions by
construction, so levelling down under it is arguably mechanical; under equalized odds any
movement is a side effect. The floored arm is dropped there rather than faked --
:func:`demographic_parity_without_shrinking` composes a floor with *parity*, and there is
no honest way to read it as an equalized-odds object.

``--model`` swaps the base learner, so that "levelling down is a property of linear
models" can be answered instead of conceded.

Both reach the **output directory name**, not merely the parameter signature. A signature
separates the archived copy but two runs would still race for the canonical one, and this
project has shipped four silent overwrite bugs already. Defaults produce the original
path unchanged, so every existing arm on disk and every reference to it stays valid.

Usage:
    python -m src.experiments.run_levelling_up
    python -m src.experiments.run_levelling_up --dataset acs:AL --seeds 0 1 2
    python -m src.experiments.run_levelling_up --dataset acs:AL --constraint equalized_odds
    python -m src.experiments.run_levelling_up --dataset acs:AL --model hist_gradient_boosting
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from fairlearn.reductions import ExponentiatedGradient

from ..datasets import build as build_dataset
from ..incidence import decompose_gap, flip_counts, outcome_total, people_incidence
from ..levelling_up import demographic_parity_without_shrinking
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL

CONSTRAINT_CODE = {"demographic_parity": "dp", "equalized_odds": "eo"}

# Only non-default learners appear in a path, so the default arms keep the names the
# existing results, documents and analysers already use.
MODEL_CODE = {"hist_gradient_boosting": "hgb", "decision_tree": "tree"}


def model_code(model: str) -> str:
    """Short, readable, collision-free path fragment for a non-default learner.

    ``logistic_regression@0.30`` is the same learner read at a different decision
    threshold, and two operating points are two different results, so the threshold has to
    survive into the directory name like every other knob here.
    """
    base, _, threshold = model.partition("@")
    if threshold:
        # Normalised through float, so that "0.30" typed on a command line and the float
        # 0.3 held in an analyser's constant list produce the SAME directory. Formatting
        # the raw string gave op030 and op03, and the arms then simply vanished from the
        # analysis -- no error, just two fewer rows and a verdict computed over the rest.
        return f"op{float(threshold):g}".replace(".", "")
    return MODEL_CODE[base]

DEFAULT_CONSTRAINT = "demographic_parity"


def arms_for(constraint: str, method: str = "reduction") -> list[str]:
    """Which arms this constraint supports.

    The floor is a demographic-parity object. Under equalized odds the run is baseline
    against the plain constraint, which is all the direction question needs.
    """
    if method == "postprocess":
        # The floor is a reduction object and there is no post-processing analogue, so the
        # run is baseline against the constraint, which is all the direction question needs.
        return ["baseline", f"postprocess_{CONSTRAINT_CODE[constraint]}"]
    plain = f"expgrad_{CONSTRAINT_CODE[constraint]}"
    return ["baseline", plain] + (
        ["expgrad_dp_floor"] if constraint == DEFAULT_CONSTRAINT else []
    )


DEFAULT_EPS = 0.01

# Every crossover result in this project comes from one optimiser: Agarwal et al.'s
# reduction. "This is a property of that algorithm" has had no answer. Post-processing is
# the structurally different alternative -- it leaves the trained model alone and moves
# per-group thresholds afterwards -- and it necessarily reads the protected attribute at
# prediction time, which puts it in the *attribute-aware* regime that Backfire's theory
# treats separately from everything else measured here. That is a scope change, not a
# detail, and it is why the arm is named for the method rather than hidden as a variant.
METHOD_CODE = {"reduction": "", "postprocess": "_post"}


def output_stem(dataset_name: str, constraint: str, model: str,
                eps: float = DEFAULT_EPS, method: str = "reduction") -> str:
    """Where this configuration's results live, isolated from every other one.

    ``eps`` joins the path because loosening the constraint is a different experiment, not
    a re-run of the same one -- and without it the two would race for the canonical copy
    while `check_overwrite` merely refused the second, turning a naming bug into a failed
    run rather than a wrong number.
    """
    stem = f"{dataset_name}_levelling_up"
    if constraint != DEFAULT_CONSTRAINT:
        stem = f"{stem}_{CONSTRAINT_CODE[constraint]}"
    if model != BASE_MODEL:
        stem = f"{stem}_{model_code(model)}"
    if eps != DEFAULT_EPS:
        stem = f"{stem}_eps{eps:g}".replace(".", "")
    return stem + METHOD_CODE[method]


def fit_arms(split, seed: int, eps: float, constraint: str, model: str,
             method: str = "reduction"):
    baseline = build_model(model, random_state=seed)
    baseline.fit(split.X_train, split.y_train)

    if method == "postprocess":
        from fairlearn.postprocessing import ThresholdOptimizer

        post = ThresholdOptimizer(
            estimator=build_model(model, random_state=seed),
            constraints=("demographic_parity" if constraint == DEFAULT_CONSTRAINT
                         else "equalized_odds"),
            predict_method="predict_proba", prefit=False,
        )
        post.fit(split.X_train, split.y_train, sensitive_features=split.a_train)
        return {
            "baseline": baseline.predict(split.X_test),
            f"postprocess_{CONSTRAINT_CODE[constraint]}": post.predict(
                split.X_test, sensitive_features=split.a_test, random_state=seed),
        }, float("nan")

    plain = fit_exponentiated_gradient(
        build_model(model, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint=constraint, eps=eps,
    )

    predictions = {
        "baseline": baseline.predict(split.X_test),
        f"expgrad_{CONSTRAINT_CODE[constraint]}": plain.predict(
            split.X_test, random_state=seed),
    }

    if constraint != DEFAULT_CONSTRAINT:
        return predictions, float("nan")

    # The floor is the baseline's own selection rate on the training split -- "do not
    # hand out fewer favourable decisions than the unconstrained model would have". Any
    # fixed target would do; this one makes the comparison to the ablation direct.
    target = float(np.mean(baseline.predict(split.X_train)))
    floored = ExponentiatedGradient(
        build_model(model, random_state=seed),
        constraints=demographic_parity_without_shrinking(target, eps=eps),
        eps=eps,
    )
    floored.fit(split.X_train, split.y_train, sensitive_features=split.a_train)
    predictions["expgrad_dp_floor"] = floored.predict(split.X_test, random_state=seed)

    return predictions, target


def run_seed(dataset, seed: int, eps: float, constraint: str, model: str,
             method: str = "reduction") -> list[dict]:
    split = prepare(dataset, random_state=seed)
    group_kw = {"privileged": dataset.privileged_value,
                "unprivileged": dataset.unprivileged_value}
    predictions, target = fit_arms(split, seed, eps, constraint, model, method)
    y_base = predictions["baseline"]

    rows = []
    for arm in arms_for(constraint, method):
        y = predictions[arm]
        scores = evaluate(split.y_test, y, split.a_test, label=arm, **group_kw)
        row = {"seed": seed, "arm": arm, "floor_target": target,
               # Recorded because analyses downstream need a denominator for the selection
               # rate, and previously had to borrow one from the who-pays run.
               "n_test": len(split.y_test),
               "accuracy": scores["accuracy"],
               "dp_diff": scores["demographic_parity_diff"],
               "eo_diff": scores["equalized_odds_diff"],
               "disparate_impact": scores["disparate_impact"],
               "positives": int(np.asarray(y).sum())}
        if arm != "baseline":
            selection = decompose_gap(split.y_test, split.a_test, y_base, y,
                                      **group_kw).loc["selection_rate"]
            flips = flip_counts(split.a_test, y_base, y, **group_kw)
            people = people_incidence(flips)
            totals = outcome_total(y_base, y)
            row |= {
                "dp_closure": selection["closure"],
                "share_levelling_down": selection["share_levelling_down"],
                "people_share_levelling_down": people["people_share_levelling_down"],
                "lost_per_gained": people["lost_per_gained"],
                "priv_lost": flips.loc["privileged", "lost"],
                "unpriv_gained": flips.loc["unprivileged", "gained"],
                "positives_pct_change": totals["pct_change"],
            }
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="adult")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--eps", type=float, default=DEFAULT_EPS)
    parser.add_argument("--constraint", default=DEFAULT_CONSTRAINT,
                        choices=sorted(CONSTRAINT_CODE))
    parser.add_argument("--model", default=BASE_MODEL,
                        help="base learner; non-default values are isolated on disk")
    parser.add_argument("--method", default="reduction", choices=sorted(METHOD_CODE),
                        help="postprocess moves per-group thresholds after training and "
                             "reads the protected attribute at prediction time")
    parser.add_argument("--include-protected", action="store_true",
                        help="give the model the protected attribute as a feature: the "
                             "attribute-aware in-processing cell of the regime contrast. "
                             "Isolated on disk with an _aware suffix.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    arms = arms_for(args.constraint, args.method)
    plain_arm = arms[1]

    dataset = build_dataset(args.dataset).load(
        include_protected_in_features=args.include_protected)
    print(f"=== levelling up: {dataset.name} "
          f"[{args.constraint}, {args.model}] ===\n")

    rows = []
    for seed in args.seeds:
        print(f"--- seed {seed} ---", flush=True)
        rows.extend(run_seed(dataset, seed, args.eps, args.constraint, args.model,
                             args.method))

    runs = pd.DataFrame(rows)
    summary = runs.groupby("arm")[
        ["accuracy", "dp_diff", "eo_diff", "disparate_impact", "positives",
         "positives_pct_change", "share_levelling_down",
         "people_share_levelling_down", "lost_per_gained"]
    ].mean().round(4).reindex(arms)

    print("\n=== mean over seeds ===")
    print(summary.to_string())

    plain = summary.loc[plain_arm]
    base = summary.loc["baseline"]
    # The violation the constraint was actually asked to close, which is not the same
    # column under equalized odds -- reporting dp_diff there would score the run against
    # a criterion it never optimised.
    key = "dp_diff" if args.constraint == DEFAULT_CONSTRAINT else "eo_diff"
    print("\n" + "=" * 74)
    if "expgrad_dp_floor" in summary.index:
        floored = summary.loc["expgrad_dp_floor"]
        print(f"  demographic parity   {base[key]:.4f} -> "
              f"{plain[key]:.4f} (plain) / {floored[key]:.4f} (with floor)")
        print(f"  favourable decisions {plain['positives_pct_change']:+.1f}% (plain) / "
              f"{floored['positives_pct_change']:+.1f}% (with floor)")
        print(f"  accuracy cost        {base['accuracy'] - plain['accuracy']:.4f} (plain) / "
              f"{base['accuracy'] - floored['accuracy']:.4f} (with floor)")
        print(f"  share paid by the privileged group, in people:")
        print(f"                       {plain['people_share_levelling_down']:.3f} (plain) / "
              f"{floored['people_share_levelling_down']:.3f} (with floor)")
        print(f"  favourable decisions destroyed per one created:")
        print(f"                       {plain['lost_per_gained']:.2f} (plain) / "
              f"{floored['lost_per_gained']:.2f} (with floor)")
    else:
        print(f"  {args.constraint:<20} {base[key]:.4f} -> {plain[key]:.4f}")
        print(f"  favourable decisions {plain['positives_pct_change']:+.1f}%")
        print(f"  accuracy cost        {base['accuracy'] - plain['accuracy']:.4f}")
        print(f"  share paid by the privileged group, in people:  "
              f"{plain['people_share_levelling_down']:.3f}")
        print(f"  favourable decisions destroyed per one created: "
              f"{plain['lost_per_gained']:.2f}")
    print("=" * 74)

    stem = output_stem(dataset.name, args.constraint, args.model, args.eps, args.method)
    if args.include_protected:
        # A model that reads the attribute is a different regime, never a re-run.
        stem = f"{stem}_aware"
    OUT = output_dir(stem)
    for path in save(OUT, "levelling_up", {"runs": runs, "summary": summary},
                     params=dict(dataset=args.dataset, seeds=args.seeds, eps=args.eps,
                                 constraint=args.constraint, model=args.model),
                     force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
