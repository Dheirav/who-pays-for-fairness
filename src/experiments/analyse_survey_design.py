"""Do the transported quantities survive the survey's own design? Weights, households, imputation.

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**

The fourth council's economist accepted the audit's unweighted convention for a
deployer's own pool but not for the transported quantities, and named three specific
threats this module measures:

* ``--weighted``: the located ACS crossovers and the two campaign outliers, re-read
  under PWGTP. Models are fitted unweighted (the declared convention --- the model a
  team deploys is fitted on its sample); the *evaluation* is run both ways, so each
  arm carries an unweighted and a design-weighted selection rate and pool change, and
  each state a bracket under each reading. The question: does any bracket move
  materially, and do Florida and Pennsylvania remain outliers when the sample is
  weighted back to the state?
* ``--clustered``: sex-arm uncertainty with households respected. ACS samples
  households, and household members share income processes, so resampling persons
  understates uncertainty on sex arms. The nested bootstrap of document 61 is repeated
  on the two located ACS states with the inner resample drawn over ``SERIALNO``
  clusters instead of rows.
* ``--allocation``: PUMS incomes are substantially hot-deck imputations (``FPINCP``),
  a share that rose in pandemic vintages --- an untested candidate in the 2022
  episode. Label base rates and sex gaps are recomputed excluding allocation-flagged
  rows for the four 2022 states (both labels) and one classic control, and the natural
  arms of the Ohio pair are refitted on the unallocated rows.

Auxiliary columns (weights, household serials, allocation flags) are aligned to the
model pipeline's rows by rebuilding folktables' own problem with the auxiliaries
appended to its feature list --- same filter, same order --- and the alignment is
asserted on a shared column rather than trusted.

Run:  python -m src.experiments.analyse_survey_design --allocation
      python -m src.experiments.analyse_survey_design --weighted --clustered
      python -m src.experiments.analyse_survey_design --weighted --dataset acs:OR
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir

# State -> target rates spanning its known bracket (document 61 / Table VII), with a
# margin either side so the bracket can move and still be seen moving.
WEIGHTED_STATES = {
    "acs:SC": [0.44, 0.49, 0.53, 0.57, 0.61],
    "acs:OR": [0.46, 0.51, 0.55, 0.59, 0.63],
    "acs:FL": [0.20, 0.24, 0.28, 0.32, 0.36],
    "acs:OH": [0.46, 0.51, 0.55, 0.59, 0.63],
    "acs:PA": [0.56, 0.60, 0.64, 0.68, 0.72],
}
CLUSTERED_STATES = ["acs:SC", "acs:OR"]
ALLOCATION_LABEL_SPECS = [
    "acs:AL:SEX:50000:2022", "acs:SC:SEX:50000:2022", "acs:OH:SEX:50000:2022",
    "acs:NV:SEX:50000:2022", "acs:AL:SEX:60000:2022", "acs:SC:SEX:60000:2022",
    "acs:OH:SEX:60000:2022", "acs:NV:SEX:60000:2022", "acs:OH:SEX:50000:2018",
]
ALLOCATION_MODEL_SPECS = ["acs:OH:SEX:50000:2018", "acs:OH:SEX:60000:2022"]
SEEDS = 5
B = 200


def auxiliaries(spec: str) -> pd.DataFrame:
    """PWGTP / SERIALNO / FPINCP aligned to the loader's row order, or die loudly."""
    from folktables import ACSDataSource, ACSIncome, BasicProblem

    from ..datasets import build as build_dataset

    loader = build_dataset(spec)
    dataset = loader.load()
    source = ACSDataSource(survey_year=loader.year, horizon="1-Year", survey="person",
                          root_dir="data/acs")
    frame = source.get_data(states=loader.states, download=True)
    if "RELP" not in frame.columns and "RELSHIPP" in frame.columns:
        frame = frame.rename(columns={"RELSHIPP": "RELP"})
    aux_columns = [c for c in ("PWGTP", "SERIALNO", "FPINCP") if c in frame.columns]
    problem = BasicProblem(
        features=[*ACSIncome.features, *aux_columns],
        target=ACSIncome.target,
        target_transform=lambda income: income > loader.threshold,
        group=ACSIncome.group,
        preprocess=ACSIncome._preprocess,
        postprocess=ACSIncome._postprocess,
    )
    X, _, _ = problem.df_to_pandas(frame)
    X = X.reset_index(drop=True)
    assert len(X) == dataset.n_samples, "auxiliary rebuild lost rows"
    assert (X["AGEP"].to_numpy() == dataset.X["AGEP"].to_numpy()).all(), (
        "auxiliary rows are not aligned with the loader's")
    return X[aux_columns], dataset


def fitted_arms(spec: str, targets: list[float]):
    """Per seed: baseline scores, per-arm mitigated probabilities, aligned auxiliaries."""
    from ..mitigation import fit_exponentiated_gradient
    from ..models import build as build_model
    from ..preprocessing import prepare

    aux, dataset = auxiliaries(spec)
    for seed in range(SEEDS):
        split = prepare(dataset, random_state=seed)
        test_aux = aux.iloc[split.idx_test].reset_index(drop=True)
        base = build_model("logistic_regression", random_state=seed)
        base.fit(split.X_train, split.y_train)
        scores = base.predict_proba(split.X_test)[:, 1]
        arms = []
        for rate in targets:
            tau = float(np.quantile(scores, 1 - rate))
            mitigated = fit_exponentiated_gradient(
                build_model(f"logistic_regression@{tau}", random_state=seed),
                split.X_train, split.y_train, split.a_train,
                constraint="demographic_parity", eps=0.01)
            arms.append({
                "target": rate,
                "base_pred": (scores > tau).astype(float),
                "mit_p1": np.asarray(mitigated._pmf_predict(split.X_test))[:, 1],
            })
        yield seed, test_aux, arms


def bracket_of(rates: list[float], pies: list[float]) -> tuple[float, float] | None:
    below = [r for r, d in zip(rates, pies) if d < 0]
    above = [r for r, d in zip(rates, pies) if d > 0]
    if not below or not above or max(below) >= min(above):
        return None
    return max(below), min(above)


def weighted_and_clustered(spec: str, targets: list[float], clustered: bool,
                           rng: np.random.Generator) -> dict:
    per_arm: dict = {}
    midpoints, failures = [], 0
    for seed, aux, arms in fitted_arms(spec, targets):
        weights = aux["PWGTP"].to_numpy(dtype=float)
        serial = aux["SERIALNO"].to_numpy()
        for arm in arms:
            base, p1 = arm["base_pred"], arm["mit_p1"]
            r_u = float(base.mean())
            r_w = float(np.average(base, weights=weights))
            pie_u = 100.0 * (float(p1.mean()) - r_u) / r_u
            pie_w = 100.0 * (float(np.average(p1, weights=weights)) - r_w) / r_w
            cell = per_arm.setdefault(arm["target"], {"r_u": [], "r_w": [],
                                                      "pie_u": [], "pie_w": []})
            cell["r_u"].append(r_u); cell["r_w"].append(r_w)
            cell["pie_u"].append(pie_u); cell["pie_w"].append(pie_w)
        if clustered:
            households = pd.Series(range(len(serial))).groupby(serial).groups
            keys = list(households)
            for _ in range(B):
                chosen = rng.integers(0, len(keys), len(keys))
                idx = np.concatenate([households[keys[k]].to_numpy()
                                      for k in chosen])
                rates, pies = [], []
                for arm in arms:
                    b = arm["base_pred"][idx]
                    if b.sum() == 0:
                        continue
                    r = float(b.mean())
                    rates.append(r)
                    pies.append(100.0 * (float(arm["mit_p1"][idx].mean()) - r) / r)
                bracket = bracket_of(rates, pies)
                if bracket is None:
                    failures += 1
                else:
                    midpoints.append((bracket[0] + bracket[1]) / 2)
    summary = {"population": spec}
    means = {k: {q: float(np.mean(v[q])) for q in v} for k, v in per_arm.items()}
    order = sorted(means)
    for tag in ("u", "w"):
        bracket = bracket_of([means[k][f"r_{tag}"] for k in order],
                             [means[k][f"pie_{tag}"] for k in order])
        summary[f"bracket_{tag}"] = (f"{bracket[0]:.3f}-{bracket[1]:.3f}"
                                     if bracket else "none")
    if clustered and midpoints:
        lo, hi = np.percentile(midpoints, [2.5, 97.5])
        summary["cluster_ci"] = f"{lo:.3f}-{hi:.3f}"
        summary["cluster_no_crossing"] = round(failures / (SEEDS * B), 3)
    return summary


def allocation() -> None:
    from folktables import ACSDataSource, adult_filter

    from ..datasets import build as build_dataset

    label_rows = []
    for spec in ALLOCATION_LABEL_SPECS:
        loader = build_dataset(spec)
        source = ACSDataSource(survey_year=loader.year, horizon="1-Year",
                              survey="person", root_dir="data/acs")
        frame = adult_filter(source.get_data(states=loader.states, download=True))
        y = frame["PINCP"] > loader.threshold
        sex = frame["SEX"]
        flagged = (frame["FPINCP"] == 1) if "FPINCP" in frame.columns else None
        def stats(mask):
            yy, ss = y[mask], sex[mask]
            return (float(yy.mean()),
                    float(yy[ss == 1].mean() - yy[ss == 2].mean()), int(mask.sum()))
        p_all, gap_all, n_all = stats(np.ones(len(y), dtype=bool))
        if flagged is None:
            label_rows.append({"spec": spec, "n": n_all, "p": round(p_all, 3),
                               "gap": round(gap_all, 3), "note": "no FPINCP column"})
            continue
        p_cl, gap_cl, n_cl = stats(~flagged.to_numpy())
        label_rows.append({
            "spec": spec, "n": n_all, "allocated_share": round(float(flagged.mean()), 3),
            "p": round(p_all, 3), "p_unallocated": round(p_cl, 3),
            "gap": round(gap_all, 3), "gap_unallocated": round(gap_cl, 3),
        })
    frame = pd.DataFrame(label_rows)
    print(frame.to_string(index=False))
    OUT = research_dir("allocation")
    frame.to_csv(OUT / "allocation_labels.csv", index=False)

    from ..mitigation import fit_exponentiated_gradient
    from ..models import build as build_model
    from ..preprocessing import prepare

    model_rows = []
    for spec in ALLOCATION_MODEL_SPECS:
        aux, dataset = auxiliaries(spec)
        keep = aux["FPINCP"].to_numpy() != 1
        clean = dataset.__class__(
            name=f"{dataset.name}_unallocated", X=dataset.X[keep].reset_index(drop=True),
            y=dataset.y[keep].reset_index(drop=True),
            a=dataset.a[keep].reset_index(drop=True),
            protected_attribute=dataset.protected_attribute,
            privileged_value=dataset.privileged_value,
            unprivileged_value=dataset.unprivileged_value,
            categorical_features=dataset.categorical_features,
            numeric_features=dataset.numeric_features,
            secondary_attribute=None, proxy_features=[],
            notes={**dataset.notes, "filter": "allocation-flagged incomes excluded"})
        pies = []
        for seed in range(SEEDS):
            split = prepare(clean, random_state=seed)
            base = build_model("logistic_regression", random_state=seed)
            base.fit(split.X_train, split.y_train)
            rate = float(np.asarray(base.predict(split.X_test)).mean())
            mitigated = fit_exponentiated_gradient(
                build_model("logistic_regression", random_state=seed),
                split.X_train, split.y_train, split.a_train,
                constraint="demographic_parity", eps=0.01)
            p1 = np.asarray(mitigated._pmf_predict(split.X_test))[:, 1]
            pies.append(100.0 * (float(p1.mean()) - rate) / rate)
        model_rows.append({"spec": spec, "kept_share": round(float(keep.mean()), 3),
                           "pie_unallocated": round(float(np.mean(pies)), 2)})
    frame = pd.DataFrame(model_rows)
    print(frame.to_string(index=False))
    frame.to_csv(OUT / "allocation_arms.csv", index=False)
    print(f"wrote {OUT}/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict the weighted/clustered pass to one state spec")
    parser.add_argument("--weighted", action="store_true")
    parser.add_argument("--clustered", action="store_true")
    parser.add_argument("--allocation", action="store_true")
    args = parser.parse_args()

    if args.allocation:
        allocation()
        return
    rng = np.random.default_rng(0)
    rows = []
    for spec, targets in WEIGHTED_STATES.items():
        if args.dataset and args.dataset != spec:
            continue
        clustered = args.clustered and spec in CLUSTERED_STATES
        rows.append(weighted_and_clustered(spec, targets, clustered, rng))
        print(pd.DataFrame(rows[-1:]).to_string(index=False), flush=True)
    frame = pd.DataFrame(rows)
    OUT = research_dir("uncertainty")
    frame.to_csv(OUT / "weighted_crossovers.csv", index=False)
    print(f"\nwrote {OUT}/weighted_crossovers.csv")


if __name__ == "__main__":
    main()
