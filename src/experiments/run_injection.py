"""Plant a proxy and see whether the constraint moves onto it.

**Written and committed before it was run.** Predictions and thresholds are fixed below.

What this is for
----------------
Document 06 found that constraining demographic parity on Adult moves SHAP attribution
*off* ``marital-status`` and *onto* ``relationship``, whose Husband/Wife levels determine
sex outright for 46% of rows -- a 151% increase. The proposed mechanism was that the
constrained model searches for the best available reconstruction of the protected
attribute.

Document 11 tested that observationally and it held: ACS records husband/wife as a single
50.2%-male code, offers no comparable target, and leaks sex at 0.76-0.84 against Adult's
0.936, with no overlap across nine populations. That is nine independent confirmations of
a *correlation*: populations lacking a strong proxy leak less.

It is not an intervention. "Adult has a proxy and behaves this way" and "the proxy causes
the behaviour" are still distinguishable, and the way to distinguish them is to add a
proxy to a population that lacks one and see whether the behaviour follows.

The manipulation
----------------
A synthetic categorical ``SYNTH`` is added to an ACS state, built to mirror the structure
of Adult's ``relationship`` rather than an abstract "correlated feature":

* a fraction ``DETERMINED_SHARE`` of rows (0.46, Adult's Husband+Wife share) take one of
  two sex-indicating levels;
* the rest take a third, uninformative level -- Adult's Unmarried/Own-child/etc.;
* the indicating levels are correct with probability ``strength``, so P(Male | level A)
  is approximately ``strength``.

At ``strength = 0.5`` the levels carry no information about sex whatever, which is the
null: the column exists, has the same cardinality and the same marginal distribution, and
says nothing. Any effect seen there is an artifact of adding a column, not of adding a
proxy.

Stated in advance, so they can fail
-----------------------------------
**I0 -- manipulation check.** Sex leakage AUC rises monotonically with strength. If
planting the proxy does not make sex more recoverable, nothing below means anything and
the experiment is void rather than negative.

**I1 -- the baseline uses it.** Attribution on ``SYNTH`` in the unconstrained model rises
with strength. It must: the column is informative about income through its correlation
with sex. This is a sanity check, not a finding.

**I2 -- the constrained model uses it MORE.** The excess -- attribution under
``expgrad_dp`` minus attribution under the baseline -- exceeds ``MIN_RELOCATION`` at full
strength, and is larger at full strength than at the null. This is relocation, and it is
the actual test.

**I3 -- nothing happens at the null.** The excess at ``strength = 0.5`` is below
``MIN_RELOCATION``. If a meaningless column also attracts the constrained model, the
mechanism is not about proxies and I2 means nothing.

If I2 fails while I0 holds, document 06's mechanism is not causal: the constraint does not
seek out reconstructions of the protected attribute, and the Adult observation needs
another explanation.

Usage:
    python -m src.experiments.run_injection --dataset acs:AL
    python -m src.experiments.run_injection --dataset acs:AL --strengths 0.5 1.0 --seeds 0
"""

from __future__ import annotations

import argparse
from dataclasses import replace

import numpy as np
import pandas as pd

from ..datasets import build as build_dataset
from ..explain import (
    aggregate_attributions,
    kernel_explainer_values,
    linear_explainer_values,
    source_feature_map,
)
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient
from ..models import build as build_model
from ..preprocessing import prepare
from ..results_io import output_dir, save
from .methods import BASE_MODEL

SYNTH = "SYNTH"

# Adult's Husband + Wife share of all rows. The planted column mirrors that structure so
# the comparison is against the feature whose behaviour prompted the question, rather
# than against an arbitrary correlated column.
DETERMINED_SHARE = 0.46

LEVEL_MALE, LEVEL_FEMALE, LEVEL_OTHER = "SYN-A", "SYN-B", "SYN-C"

DEFAULT_STRENGTHS = [0.5, 0.7, 0.85, 1.0]

# I2/I3's bar, in units of attribution share. Document 06 saw `relationship` go from
# 0.075 to 0.189 on Adult, an excess of 0.114; a tenth of that is a conservative floor
# for calling relocation real.
MIN_RELOCATION = 0.02


def inject(dataset, strength: float, random_state: int, outcome: float = 0.5):
    """Return a copy of `dataset` carrying a planted column with two tunable properties.

    ``strength`` controls how well the column determines the protected attribute;
    ``outcome`` controls how well it predicts the label *independently* of that. They are
    separate bits of the same level label, so a level is one of four combinations, and
    the two properties can be varied one at a time.

    At ``outcome = 0.5`` the label bit is noise and the column is a pure protected-
    attribute proxy -- the configuration document 16 used. At ``strength = 0.5`` the sex
    bit is noise and the column is a pure outcome predictor. Adult's ``relationship`` sits
    at neither extreme: it determines sex for 46% of rows *and* spans 0.44-0.47 in P(y=1)
    within a single sex, which is what motivated separating the two.

    Building a feature from ``y`` is label leakage by construction. That is deliberate --
    the point is a feature that genuinely predicts the outcome, which is what
    ``relationship`` is -- and it is why ``outcome`` is held well below 1.
    """
    rng = np.random.default_rng(random_state)
    n = len(dataset.X)
    is_privileged = (dataset.a.to_numpy() == dataset.privileged_value)
    is_positive = (dataset.y.to_numpy() == 1)

    determined = rng.random(n) < DETERMINED_SHARE
    sex_bit = np.where(rng.random(n) < strength, is_privileged, ~is_privileged)
    outcome_bit = np.where(rng.random(n) < outcome, is_positive, ~is_positive)

    column = np.full(n, LEVEL_OTHER, dtype=object)
    for sex_value in (True, False):
        for outcome_value in (True, False):
            mask = determined & (sex_bit == sex_value) & (outcome_bit == outcome_value)
            column[mask] = f"SYN-{'P' if sex_value else 'U'}{'H' if outcome_value else 'L'}"

    X = dataset.X.copy()
    X[SYNTH] = pd.Series(column, index=X.index).astype(str)

    return replace(
        dataset,
        name=f"{dataset.name}_synth{strength:g}_out{outcome:g}",
        X=X,
        categorical_features=[*dataset.categorical_features, SYNTH],
        # The planted column is the only proxy of interest; the real ones are measured
        # separately by run_shap and are not what this experiment is about.
        proxy_features=[SYNTH],
        notes={**dataset.notes, "injected_proxy": {"strength": strength,
                                                   "outcome": outcome,
                                                   "determined_share": DETERMINED_SHARE}},
    )


def within_group_outcome_spread(planted) -> float:
    """Range of P(y=1) across the planted levels, inside one protected group.

    The manipulation check for the outcome dimension, and the same quantity measured on
    Adult's ``relationship`` in document 16 (0.438 within males, 0.473 within females). A
    column that encoded only the protected attribute would score near zero here.
    """
    column = planted.X[SYNTH].to_numpy()
    y = planted.y.to_numpy()
    spreads = []
    for group in (planted.privileged_value, planted.unprivileged_value):
        mask = planted.a.to_numpy() == group
        frame = pd.DataFrame({"level": column[mask], "y": y[mask]})
        rates = frame.groupby("level")["y"].agg(["mean", "size"])
        rates = rates[rates["size"] >= 100]
        if len(rates) > 1:
            spreads.append(rates["mean"].max() - rates["mean"].min())
    return float(np.mean(spreads)) if spreads else float("nan")


def report_two_factor(summary: pd.DataFrame, args) -> None:
    """Verdict for the 2-factor design. Thresholds are MIN_RELOCATION, fixed above.

    Document 16 refuted the claim that the constraint seeks reconstructions of the
    protected attribute: a planted *pure* proxy was used less as it sharpened. The
    replacement offered there was that Adult's ``relationship`` attracts the constrained
    model because it predicts the outcome well within each group, and its sex-determining
    character is incidental. That was consistent with the evidence and untested, because
    document 16 varied only one of the two properties.

    Varying both separates them:

    **R0 -- manipulation check.** Leakage must rise with the sex bit and the within-group
    outcome spread must rise with the outcome bit, each roughly independently of the
    other. If the two knobs are not separable, nothing below identifies anything.

    **R1 -- the replacement explanation.** Excess attribution under the constraint rises
    with the *outcome* dimension by more than MIN_RELOCATION, at both extremes of the sex
    dimension. This is the prediction document 16 could not test.

    **R2 -- document 16 replicates.** At fixed outcome strength, excess does not rise with
    the sex dimension.

    If R1 fails, the replacement explanation is wrong too, and the honest position is that
    the Adult attribution shift has no mechanism this project can identify.
    """
    print("\n=== mean over seeds: rows are (outcome strength, sex strength) ===")
    print(summary.to_string())

    outcomes = sorted(args.outcomes)
    strengths = sorted(args.strengths)
    lo_o, hi_o = outcomes[0], outcomes[-1]
    lo_s, hi_s = strengths[0], strengths[-1]

    print("\n" + "=" * 74)
    leak_rise = (summary.xs(hi_s, level="strength")["leakage_auc"].mean()
                 - summary.xs(lo_s, level="strength")["leakage_auc"].mean())
    spread_rise = (summary.xs(hi_o, level="outcome")["outcome_spread"].mean()
                   - summary.xs(lo_o, level="outcome")["outcome_spread"].mean())
    r0 = leak_rise > 0.02 and spread_rise > 0.05
    print(f"R0  the two knobs move different things       -> {'HOLDS' if r0 else 'FAILS'}")
    print(f"      sex knob raises leakage by      {leak_rise:+.4f}")
    print(f"      outcome knob raises spread by   {spread_rise:+.4f}")
    if not r0:
        print("      the design does not separate the properties; nothing below identifies")

    print()
    gains = {s: summary.loc[(hi_o, s), "excess"] - summary.loc[(lo_o, s), "excess"]
             for s in strengths}
    r1 = all(g > MIN_RELOCATION for g in gains.values())
    print(f"R1  outcome signal attracts the constraint    -> {'HOLDS' if r1 else 'FAILS'}")
    for s, gain in gains.items():
        print(f"      at sex strength {s:<5}: excess rises {gain:+.4f} "
              f"({summary.loc[(lo_o, s), 'excess']:+.4f} -> "
              f"{summary.loc[(hi_o, s), 'excess']:+.4f})   bar {MIN_RELOCATION}")

    print()
    sex_gains = {o: summary.loc[(o, hi_s), "excess"] - summary.loc[(o, lo_s), "excess"]
                 for o in outcomes}
    r2 = all(g <= MIN_RELOCATION for g in sex_gains.values())
    print(f"R2  sex signal does not                       -> {'HOLDS' if r2 else 'FAILS'}")
    for o, gain in sex_gains.items():
        print(f"      at outcome strength {o:<5}: excess moves {gain:+.4f}")

    print("=" * 74)
    if r0 and r1 and r2:
        print("The replacement explanation holds: the constrained model relocates onto a")
        print("feature for its OUTCOME signal, not for its ability to reconstruct sex.")
        print("Document 06's attribution shift is a cost-sensitive reweighting finding")
        print("a good within-group predictor, and the proxy character is incidental.")
    elif r0 and not r1:
        print("The replacement explanation FAILS too. Outcome signal does not attract the")
        print("constraint either, and the Adult attribution shift has no mechanism this")
        print("project has been able to identify. That is to be reported as it stands.")


def feature_mapping(split, dataset) -> dict[str, list[int]]:
    return source_feature_map(
        split.feature_names, dataset.categorical_features, dataset.numeric_features
    )


def run_one(dataset, strength: float, seed: int, outcome: float = 0.5) -> dict:
    planted = inject(dataset, strength, random_state=seed, outcome=outcome)
    split = prepare(planted, random_state=seed)
    mapping = feature_mapping(split, planted)
    X_train = np.asarray(split.X_train, dtype=float)
    X_test = np.asarray(split.X_test, dtype=float)

    baseline = build_model(BASE_MODEL, random_state=seed)
    baseline.fit(split.X_train, split.y_train)

    expgrad = fit_exponentiated_gradient(
        build_model(BASE_MODEL, random_state=seed),
        split.X_train, split.y_train, split.a_train,
        constraint="demographic_parity", eps=0.01,
    )

    # The estimand here is a *difference between two models*, so both must be measured
    # the same way. run_shap explains the linear baseline exactly and the randomized
    # ensemble by sampling, and flags the mismatch; that is defensible when reporting
    # each model's own reliance, and not defensible when the difference is the result.
    # An exact and a sampled estimator can differ systematically, and that difference
    # would land directly on `excess`. So the verdict uses KernelExplainer for both,
    # with identical background and instances. The exact baseline is computed anyway,
    # as a check on how much the explainer choice moves the number.
    rng = np.random.default_rng(seed)
    background = X_train[rng.choice(len(X_train), 25, replace=False)]
    instances = X_test[rng.choice(len(X_test), 150, replace=False)]

    base_shares = aggregate_attributions(
        kernel_explainer_values(
            lambda data: baseline.predict_proba(data)[:, 1], background, instances,
        ),
        mapping,
    )
    base_shares_exact = aggregate_attributions(
        linear_explainer_values(baseline.coef_[0], float(baseline.intercept_[0]),
                                X_train, X_test),
        mapping,
    )
    # `_pmf_predict` is the deterministic function underneath the randomized predict;
    # explaining a sampled draw would attribute the coin flip rather than the model.
    mitigated_shares = aggregate_attributions(
        kernel_explainer_values(
            lambda data: np.asarray(expgrad._pmf_predict(data))[:, 1],
            background, instances,
        ),
        mapping,
    )

    y_base = baseline.predict(split.X_test)
    y_mit = expgrad.predict(split.X_test, random_state=seed)
    group_kw = {"privileged": planted.privileged_value,
                "unprivileged": planted.unprivileged_value}

    return {
        "strength": strength,
        "outcome": outcome,
        "seed": seed,
        "outcome_spread": within_group_outcome_spread(planted),
        "leakage_auc": planted.attribute_leakage(random_state=seed)["leakage_auc"],
        "synth_baseline": float(base_shares.get(SYNTH, 0.0)),
        "synth_baseline_exact": float(base_shares_exact.get(SYNTH, 0.0)),
        "synth_mitigated": float(mitigated_shares.get(SYNTH, 0.0)),
        "excess": float(mitigated_shares.get(SYNTH, 0.0) - base_shares.get(SYNTH, 0.0)),
        "excess_mismatched": float(mitigated_shares.get(SYNTH, 0.0)
                                   - base_shares_exact.get(SYNTH, 0.0)),
        "baseline_accuracy": evaluate(split.y_test, y_base, split.a_test, **group_kw)["accuracy"],
        "mitigated_accuracy": evaluate(split.y_test, y_mit, split.a_test, **group_kw)["accuracy"],
        "mitigated_dp": evaluate(split.y_test, y_mit, split.a_test,
                                 **group_kw)["demographic_parity_diff"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="acs:AL")
    parser.add_argument("--strengths", type=float, nargs="+", default=DEFAULT_STRENGTHS)
    parser.add_argument("--outcomes", type=float, nargs="+", default=[0.5],
                        help="how well the planted column predicts y, independently of sex")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    dataset = build_dataset(args.dataset).load()
    print(f"=== planting a proxy in {dataset.name} ===")
    print(f"native sex leakage (no planted column): "
          f"{dataset.attribute_leakage()['leakage_auc']:.4f}\n")

    rows = []
    for outcome in args.outcomes:
        for strength in args.strengths:
            for seed in args.seeds:
                row = run_one(dataset, strength, seed, outcome=outcome)
                rows.append(row)
                print(f"  sex {strength:<5} outcome {outcome:<5} seed {seed}  "
                      f"leakage {row['leakage_auc']:.4f}  spread {row['outcome_spread']:.3f}  "
                      f"base {row['synth_baseline']:.4f}  mit {row['synth_mitigated']:.4f}"
                      f"  excess {row['excess']:+.4f}", flush=True)

    runs = pd.DataFrame(rows)
    two_factor = len(args.outcomes) > 1
    summary = runs.groupby(["outcome", "strength"] if two_factor else "strength")[
        ["leakage_auc", "outcome_spread", "synth_baseline", "synth_baseline_exact",
         "synth_mitigated", "excess", "excess_mismatched",
         "baseline_accuracy", "mitigated_accuracy", "mitigated_dp"]
    ].mean().round(4)

    print("\n=== mean over seeds ===")
    print(summary.to_string())

    if two_factor:
        report_two_factor(summary, args)
        OUT = output_dir(dataset.name + "_injection2")
        for path in save(OUT, "injection2", {"runs": runs, "summary": summary},
                         params=dict(dataset=args.dataset, strengths=args.strengths,
                                     outcomes=args.outcomes, seeds=args.seeds),
                         force=args.force):
            print(f"wrote {path}")
        return

    low, high = min(args.strengths), max(args.strengths)
    print("\n" + "=" * 74)
    i0 = summary["leakage_auc"].is_monotonic_increasing
    print(f"I0  leakage rises with strength                    -> "
          f"{'HOLDS' if i0 else 'FAILS'}  "
          f"({summary['leakage_auc'].iloc[0]:.4f} -> {summary['leakage_auc'].iloc[-1]:.4f})")
    if not i0:
        print("    the manipulation did not work; nothing below is interpretable")

    i1 = summary.loc[high, "synth_baseline"] > summary.loc[low, "synth_baseline"]
    print(f"I1  the baseline leans on it more as it sharpens   -> "
          f"{'HOLDS' if i1 else 'FAILS'}  "
          f"({summary.loc[low, 'synth_baseline']:.4f} -> "
          f"{summary.loc[high, 'synth_baseline']:.4f})")

    excess_high, excess_low = summary.loc[high, "excess"], summary.loc[low, "excess"]
    i2 = excess_high > MIN_RELOCATION and excess_high > excess_low
    print(f"I2  the CONSTRAINED model leans on it even more    -> "
          f"{'HOLDS' if i2 else 'FAILS'}  "
          f"(excess {excess_high:+.4f} at strength {high}, bar {MIN_RELOCATION})")

    i3 = abs(excess_low) < MIN_RELOCATION
    print(f"I3  nothing happens when the column is meaningless -> "
          f"{'HOLDS' if i3 else 'FAILS'}  "
          f"(excess {excess_low:+.4f} at strength {low})")
    drift = (summary["excess_mismatched"] - summary["excess"]).abs().mean()
    print(f"    explainer check: using the exact baseline instead of the matched one")
    print(f"    moves the excess by {drift:.4f} on average -- reported because the")
    print(f"    estimand is a difference, so a mismatched pair would bias it directly")
    print("=" * 74)
    if i0 and i2 and i3:
        print("document 06's mechanism is causal on this evidence: planting a proxy")
        print("makes the constrained model relocate onto it, and a meaningless column")
        print("of the same shape does not.")
    elif i0 and not i2:
        print("document 06's mechanism is NOT causal: the proxy was planted, sex became")
        print("more recoverable, and the constraint did not move onto it. The Adult")
        print("observation needs another explanation, and this is to be reported.")

    OUT = output_dir(dataset.name + "_injection")
    for path in save(OUT, "injection", {"runs": runs, "summary": summary},
                     params=dict(dataset=args.dataset, strengths=args.strengths,
                                 seeds=args.seeds), force=args.force):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
