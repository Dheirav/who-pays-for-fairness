"""The relaxed-zeta ordering, extended: every population, both sealed cohorts, a second probe.

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**

The councils' last unfinished analysis item, demanded twice over: the correspondence
between the theory's relaxed ordering and this project's selection rate rests on 26
arms from 15 populations, one probe, no interval. This closes it four ways:

* **Breadth**: the relaxed ordering (quantile-trimmed zeta extrema, the 5/95 form of
  ``analyse_zeta``) versus the rate rule versus the observed direction, on **every
  population with a stored natural arm** this module can map to a spec — three seeds
  each, seed-averaged like everything else here.
* **Head-to-head on the sealed cohorts**: the two direction cohorts' own arms, where
  the comparison actually matters for the paper's claims.
* **A second nu estimator**: a gradient-boosted probe beside the logistic one, on the
  original 26-arm set, so "certified on zero arms" and the +0.935 stop resting on one
  possibly-misspecified plug-in.
* **Trim sensitivity and an interval**: q in {0.025, 0.05, 0.10} on the original set,
  and a population-clustered bootstrap interval on r(rate, zeta separation).

Nothing here is sealed; it strengthens or weakens a post-hoc correspondence, stated
as such.

Run:  python -m src.experiments.analyse_zeta_extension
      python -m src.experiments.analyse_zeta_extension --dataset acs:OR
"""

from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

SEEDS = [0, 1, 2]
TRIMS = (0.025, 0.05, 0.10)


def spec_for_stem(stem: str) -> str | None:
    from .analyse_verdicts import spec_for

    got = spec_for(stem)
    if got is not None:
        return got
    ipums = re.match(r"^ipums_income_(?P<c>br|mx)_(?P<y>\d{4})"
                     r"(?P<race>_race)?_t(?P<t>\d+)_s\d+k$", stem)
    if ipums:
        attr = "RACE" if ipums.group("race") else "SEX"
        return (f"ipums:{ipums.group('c').upper()}:{ipums.group('y')}:{attr}:"
                f"{ipums.group('t')}")
    task = re.match(r"^acs_(employment|coverage)_(?P<st>[a-z]{2})_2018_rac1p$", stem)
    if task:
        key = "acsemp" if task.group(1) == "employment" else "acscov"
        return f"{key}:{task.group('st').upper()}:RAC1P"
    return None


def natural_stems() -> list[str]:
    stems = []
    for directory in sorted(RESEARCH_RESULTS_DIR.glob("*_levelling_up")):
        stem = directory.name[: -len("_levelling_up")]
        if re.search(r"_(op[\d]+|eo|hgb|eps\d+|post|aware)$", stem):
            continue
        if (directory / "levelling_up_runs.csv").exists():
            stems.append(stem)
    return stems


def measure(spec: str, stem: str, seed: int, probe_kind: str, q: float) -> dict | None:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression

    from ..datasets import build as build_dataset
    from ..models import build as build_model
    from ..preprocessing import prepare

    dataset = build_dataset(spec).load()
    split = prepare(dataset, random_state=seed)
    model = build_model("logistic_regression", random_state=seed)
    model.fit(split.X_train, split.y_train)
    eta = model.predict_proba(split.X_test)[:, 1]
    a_train = (np.asarray(split.a_train) == dataset.privileged_value).astype(int)
    if probe_kind == "hgb":
        probe = HistGradientBoostingClassifier(random_state=seed)
    else:
        probe = LogisticRegression(max_iter=2000)
    probe.fit(split.X_train, a_train)
    px = probe.predict_proba(split.X_test)[:, 1]
    p = a_train.mean()
    nu = px / p - (1 - px) / (1 - p)
    z = (eta - 0.5) / nu
    above, below = z[nu > 0], z[nu < 0]
    if len(above) < 50 or len(below) < 50:
        return None
    runs = pd.read_csv(RESEARCH_RESULTS_DIR / f"{stem}_levelling_up"
                       / "levelling_up_runs.csv")
    grouped = runs.groupby("arm").mean(numeric_only=True)
    if "expgrad_dp" not in grouped.index:
        return None
    pie = float(grouped.loc["expgrad_dp", "positives_pct_change"])
    rate = float(grouped.loc["baseline", "positives"]
                 / grouped.loc["baseline", "n_test"])
    return {"population": stem, "rate": rate, "pie": pie,
            "sep": float(np.quantile(above, 1 - q) - np.quantile(below, 1 - q))}


def collect(pairs, probe_kind: str, q: float) -> pd.DataFrame:
    rows = []
    for spec, stem in pairs:
        got = [r for s in SEEDS if (r := measure(spec, stem, s, probe_kind, q))]
        if not got:
            print("x", end="", flush=True)
            continue
        mean = {k: float(np.mean([g[k] for g in got]))
                for k in ("rate", "pie", "sep")}
        rows.append({"population": stem, **mean})
        print(".", end="", flush=True)
    print()
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["obs"] = np.where(frame["pie"] > 0, "up", "down")
    frame["zeta_call"] = np.where(frame["sep"] > 0, "up", "down")
    frame["rate_call"] = np.where(frame["rate"] > 0.5, "up", "down")
    return frame


def report(label: str, frame: pd.DataFrame) -> None:
    n = len(frame)
    if n == 0:
        print(f"{label}: nothing measurable")
        return
    z = int((frame["zeta_call"] == frame["obs"]).sum())
    r = int((frame["rate_call"] == frame["obs"]).sum())
    agree = int((frame["zeta_call"] == frame["rate_call"]).sum())
    corr = float(np.corrcoef(frame["rate"], frame["sep"])[0, 1])
    print(f"{label}: n={n}  zeta {z}/{n}  rate {r}/{n}  "
          f"zeta-rate agree {agree}/{n}  r(rate, sep)={corr:+.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one spec (default: everything mappable)")
    args = parser.parse_args()
    OUT = research_dir("zeta")

    pairs = [(spec, stem) for stem in natural_stems()
             if (spec := spec_for_stem(stem)) is not None
             and (not args.dataset or args.dataset == spec)]
    print(f"{len(pairs)} populations mappable; logistic probe, q=0.05, "
          f"seeds {SEEDS}")
    full = collect(pairs, "logistic", 0.05)
    report("ALL POPULATIONS", full)
    full.to_csv(OUT / "zeta_all_populations.csv", index=False)

    sealed_pairs = []
    for path in ("sealed/sealed.csv", "resealed/resealed.csv"):
        for _, row in pd.read_csv(RESEARCH_RESULTS_DIR / path).iterrows():
            sealed_pairs.append((row["spec"], row["population"]))
    sealed_frame = collect(sealed_pairs, "logistic", 0.05)
    report("SEALED COHORTS (head-to-head)", sealed_frame)
    sealed_frame.to_csv(OUT / "zeta_sealed_cohorts.csv", index=False)

    # Robustness axes on the original correspondence set.
    original = pd.read_csv(OUT / "zeta_correspondence.csv")
    original_pairs = [(spec, stem) for stem in original["pop"]
                      if (spec := spec_for_stem(stem)) is not None]
    for q in TRIMS:
        trimmed = collect(original_pairs, "logistic", q)
        report(f"ORIGINAL SET, logistic, trim {q}", trimmed)
    hgb = collect(original_pairs, "hgb", 0.05)
    report("ORIGINAL SET, gradient-boosted probe", hgb)
    hgb.to_csv(OUT / "zeta_hgb_probe.csv", index=False)

    if len(full) > 3:
        rng = np.random.default_rng(0)
        rs = []
        for _ in range(2000):
            idx = rng.integers(0, len(full), len(full))
            sample = full.iloc[idx]
            if sample["rate"].std() > 0 and sample["sep"].std() > 0:
                rs.append(float(np.corrcoef(sample["rate"], sample["sep"])[0, 1]))
        lo, hi = np.percentile(rs, [2.5, 97.5])
        print(f"\nbootstrap 95% interval on r(rate, sep), all populations: "
              f"[{lo:+.3f}, {hi:+.3f}]")
    print(f"\nwrote {OUT}/")


if __name__ == "__main__":
    main()
