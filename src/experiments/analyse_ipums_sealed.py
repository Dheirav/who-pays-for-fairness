"""The third sealed cohort: off-instrument, in-band, mixed-route. Committed before the data exists.

**Individual work, beyond the course submission.**

**This file is stage A of a two-stage seal, committed while the IPUMS extract is still
pending human review.** Stage A fixes everything that can be fixed without the data:
the populations, the label and arm construction *procedures*, the rule, both nulls,
the exclusions, the magnitude guard, the bars, and the power floors. Stage B runs
``--measure`` on the day the extract arrives, which turns the procedures into concrete
currency thresholds and operating points from the data's own quantiles and seed-0
baseline scores --- and that output is committed (and externally timestamped) **before
any constraint is fitted**. Document 56's corollary is satisfied by construction: no
arm this file scores will exist until after both commits.

Why this cohort exists
----------------------
The sealed 9-of-10 (document 49) cannot separate the selection rate from label rarity:
every arm reached its rate through the ACS income cutoff, and the achieved rates left
[0.30, 0.70] unsampled. The paper states this confound beside the score and names this
design as the resolution. Three properties do the work:

* **Off-instrument.** Brazil 2000/2010 and Mexico 2015/2020 (IPUMS International):
  different continent, instruments, languages, currencies. A pass cannot be an ACS
  artifact.
* **In-band.** Arms are constructed to land selection rates inside [0.40, 0.65] ---
  the region the first two cohorts never sampled and the hardest band for the prior.
* **Mixed routes.** Label-route arms (two label quantiles per population) and
  operating-point arms (label fixed, decision threshold moved) appear in the same
  score. On op arms the label's rarity is constant while the rate varies, which is
  exactly where a cutoff-only rule and the selection-rate rule must diverge.

The design, fixed here
----------------------
**Populations:** the four country-years in ``POPULATIONS``, protected attribute SEX,
loaded by ``src/datasets/ipums.py`` (filter: age 17--90, employed where recorded,
valid positive earned income).

**Labels by quantile, never nominal currency** (document 57's lesson): the primary
label is income above its population's ``PRIMARY_Q`` = 0.45 quantile (base rate
$p \\approx 0.55$); the secondary label uses ``SECONDARY_Q`` = 0.60 ($p \\approx
0.40$). The two ``SHAPE_POPULATIONS`` add a third label at ``SHAPE_Q`` = 0.75
($p \\approx 0.25$), placing calls on both sides of the 0.365 boundary.

**Arms per population:** the primary label's natural arm; op arms on the primary
label at target rates ``TARGET_RATES`` = (0.42, 0.48, 0.54, 0.60), thresholds read
from seed-0 baseline scores at stage B; the secondary label's natural arm. The shape
populations extend the primary sweep to rates near 0.20 and 0.75 and sweep the
``SHAPE_Q`` label at six points --- those wide arms serve S2/S3 only, never S1.
Five seeds per arm; every scored quantity is the seed mean.

**Frozen exclusions** (identical to the paper's): baseline parity gap $\\ge 0.05$;
baseline accuracy $\\ge \\max(p, 1-p)$; test split $\\ge 2{,}500$; arms below rate
0.10 advisory. **Magnitude guard, stated in advance this time:** an arm whose
seed-mean $|\\Delta\\mathrm{pool}| < 1.0$ point is recorded and excluded from S1 ---
document 49's miss and the seed-stability table (16/19 unanimous, every split a
near-zero arm) are the evidence that a sign is not defined there.

What is scored, and against what
--------------------------------
**S1 --- the transported prior, deconfounded.** Rule: down below 0.54, up at or
above, applied to each scorable in-band arm's measured baseline rate. Scored
head-to-head on the same arms against **null A** (the same rule at 0.50) and
**null B** (cutoff-only: the call from the arm's *label base rate* against 0.54,
constant across a label's op arms). **Bar: correct on at least
$\\lceil 0.6 \\cdot \\mathrm{scorable} \\rceil$ arms and strictly more correct than
each null.** Floor: at least 12 scorable arms, else UNDERPOWERED and no verdict.

**S2 --- the within-population claim.** Per population, Spearman rate-vs-pool-change
over the retained primary-label arms, for populations whose landscape is monotone
(one rising sign change or one-signed; non-monotone populations are recorded as
Algorithm 1 verdicts, not scored). **Bar: $\\rho \\ge +0.70$ in every scorable
population.** Floor: at least 2 scorable populations.

**S3 --- the base-rate shape boundary, real-anchored** (document 57's post-hoc note,
now sealed): each shape sweep's family called LOW below $p = 0.365$, HIGH at or
above, classified exactly as ``analyse_shapes.family`` with the 2.0-point flat guard
and the 0.10 advisory rule. **Bar: at least scored$-$1 correct and strictly beating
the best constant.** Floor: at least 3 non-flat sweeps.

S1, S2 and S3 are separate claims; no outcome of one rescues another.

Run:  python -m src.experiments.analyse_ipums_sealed             # print this protocol
      python -m src.experiments.analyse_ipums_sealed --verify    # extract-arrival check
      python -m src.experiments.analyse_ipums_sealed --measure   # stage B numbers
      python -m src.experiments.analyse_ipums_sealed --score     # after the runs
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# The cohort. Fixed at stage A; the isolation guard reads this file as pre-registered.
POPULATIONS = [("BR", "2000"), ("BR", "2010"), ("MX", "2015"), ("MX", "2020")]
SHAPE_POPULATIONS = [("BR", "2000"), ("MX", "2020")]

PRIMARY_Q, SECONDARY_Q, SHAPE_Q = 0.45, 0.60, 0.75
TARGET_RATES = (0.42, 0.48, 0.54, 0.60)
SHAPE_EXTRA_RATES = (0.20, 0.75)

PRIOR, NULL_A = 0.54, 0.50
MAGNITUDE_GUARD = 1.0          # |seed-mean pool change|, percentage points
S1_SHARE, S1_FLOOR = 0.6, 12
S2_RHO, S2_FLOOR = 0.70, 2
S3_FLOOR = 3
BOUNDARY = 0.365               # analyse_shapes' sealed boundary, real-anchored here

# Stage B fills this dict, in its own commit, before any constraint run:
# (country, year) -> {"primary": threshold, "secondary": threshold,
#                     "shape": threshold or None, "op_points": {rate: tau}}
THRESHOLDS_STAGE_B: dict = {}


def verify() -> None:
    from ..datasets.ipums import COUNTRIES, INCOME_CANDIDATES, extract_files

    files = extract_files()
    if not files:
        print("no extract delivered yet: data/ipums/ is empty")
        return
    for path in files:
        header = pd.read_csv(path, nrows=0)
        print(f"{path.name}: {len(header.columns)} columns")
        print(f"  income column(s) present: "
              f"{[c for c in INCOME_CANDIDATES if c in header.columns]}")
        counts = {}
        for chunk in pd.read_csv(path, usecols=["COUNTRY", "YEAR"],
                                 chunksize=500_000):
            for (country, year), n in chunk.value_counts().items():
                counts[(country, year)] = counts.get((country, year), 0) + int(n)
        for (country, year), n in sorted(counts.items()):
            code = {v: k for k, v in COUNTRIES.items()}.get(country, country)
            print(f"  {code} {year}: {n:,} rows")


def measure() -> None:
    """Stage B: the quantile thresholds and op points, printed for their own commit."""
    from ..datasets import build as build_dataset
    from ..models import build as build_model
    from ..preprocessing import prepare

    for country, year in POPULATIONS:
        # The quantiles come from the loader's own read path, so they are taken over
        # exactly the rows the label will see.
        from ..datasets.ipums import IPUMSIncomeLoader

        loader = IPUMSIncomeLoader(country, year, threshold=1)
        raw = loader._read()
        income = pd.to_numeric(raw[[c for c in ("INCEARN", "INCTOT")
                                    if c in raw.columns][0]], errors="coerce")
        income = income.where(income < 9_999_998).dropna()
        income = income[income > 0]
        quantiles = {"primary": PRIMARY_Q, "secondary": SECONDARY_Q}
        if (country, year) in SHAPE_POPULATIONS:
            quantiles["shape"] = SHAPE_Q
        thresholds = {k: int(np.quantile(income, q)) for k, q in quantiles.items()}
        print(f"{country} {year}: n_filtered≈{len(income):,}  thresholds {thresholds}")

        spec = f"ipums:{country}:{year}:SEX:{thresholds['primary']}"
        dataset = build_dataset(spec).load()
        split = prepare(dataset, random_state=0)
        model = build_model("logistic_regression", random_state=0)
        model.fit(split.X_train, split.y_train)
        scores = model.predict_proba(split.X_test)[:, 1]
        rates = TARGET_RATES + (SHAPE_EXTRA_RATES
                                if (country, year) in SHAPE_POPULATIONS else ())
        ops = {rate: round(float(np.quantile(scores, 1 - rate)), 4) for rate in rates}
        print(f"  p={dataset.y.mean():.3f}  natural-arm spec: {spec}")
        print(f"  op thresholds from seed-0 scores: {ops}")
    print("\nPaste the printed values into THRESHOLDS_STAGE_B, commit, timestamp the "
          "commit, and only then run the arms.")


def _arm(stem: str) -> dict | None:
    path = RESEARCH_RESULTS_DIR / stem / "levelling_up_runs.csv"
    if not path.exists():
        return None
    runs = pd.read_csv(path)
    base = runs[runs["arm"] == "baseline"]
    mit = runs[runs["arm"] == "expgrad_dp"]
    if base.empty or mit.empty:
        return None
    pies = mit["positives_pct_change"]
    return {
        "rate": float(base["positives"].mean()) / float(base["n_test"].mean()),
        "gap": float(base["dp_diff"].mean()),
        "acc": float(base["accuracy"].mean()),
        "n_test": float(base["n_test"].mean()),
        "pie": float(pies.mean()),
        "unanimous": bool((pies > 0).all() or (pies <= 0).all()),
    }


def score() -> None:
    if not THRESHOLDS_STAGE_B:
        raise SystemExit("stage B has not been committed; nothing may be scored")
    from ..datasets import build as build_dataset
    from .analyse_shapes import SPREAD_GUARD, family

    call = lambda x, prior: "up" if x >= prior else "down"
    s1_rows, s2_rows, s3_rows = [], [], []
    for country, year in POPULATIONS:
        entry = THRESHOLDS_STAGE_B[(country, year)]
        stems = {}
        for kind in ("primary", "secondary", "shape"):
            threshold = entry.get(kind)
            if threshold is None:
                continue
            stem = f"ipums_income_{country.lower()}_{year}_t{threshold}"
            stems[kind] = stem
        p_by_kind = {
            kind: float(build_dataset(
                f"ipums:{country}:{year}:SEX:{entry[kind]}").load().y.mean())
            for kind in stems
        }
        # Natural label arms (both routes' label half) and the primary op arms.
        arms = []
        for kind, stem in stems.items():
            natural = _arm(f"{stem}_levelling_up")
            if natural:
                arms.append({"population": f"{country}{year}", "kind": kind,
                             "route": "label", "p": p_by_kind[kind], **natural})
        for rate, tau in entry.get("op_points", {}).items():
            # "0.49" -> "049", matching run_levelling_up's op-arm directory naming.
            code = str(tau).replace(".", "")
            op = _arm(f"{stems['primary']}_levelling_up_op{code}")
            if op:
                arms.append({"population": f"{country}{year}", "kind": "primary-op",
                             "route": "op", "p": p_by_kind["primary"], **op})
        frame = pd.DataFrame(arms)
        if frame.empty:
            print(f"{country} {year}: no arms yet")
            continue

        kept = frame[(frame["gap"] >= 0.05) & (frame["n_test"] >= 2500)]
        kept = kept[kept["acc"] >= kept["p"].apply(lambda p: max(p, 1 - p))]
        in_band = kept[(kept["rate"] >= 0.40) & (kept["rate"] <= 0.65)
                       & (kept["pie"].abs() >= MAGNITUDE_GUARD)]
        for _, row in in_band.iterrows():
            actual = "up" if row["pie"] > 0 else "down"
            s1_rows.append({
                "population": row["population"], "route": row["route"],
                "rate": round(row["rate"], 3), "pie": round(row["pie"], 2),
                "unanimous": row["unanimous"], "actual": actual,
                "rule": call(row["rate"], PRIOR) == actual,
                "null_half": call(row["rate"], NULL_A) == actual,
                "null_cutoff": call(row["p"], PRIOR) == actual,
            })
        primary = kept[kept["kind"].isin(["primary", "primary-op"])]
        primary = primary[primary["rate"] >= 0.10].sort_values("rate")
        if len(primary) >= 4:
            pies = primary["pie"].tolist()
            signs = [x > 0 for x in pies]
            flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
            monotone = flips == 0 or (flips == 1 and not signs[0])
            rho = float(primary["rate"].corr(primary["pie"], method="spearman"))
            s2_rows.append({"population": f"{country}{year}", "monotone": monotone,
                            "rho": round(rho, 3) if monotone else None,
                            "arms": len(primary)})
        for kind in ("primary", "shape"):
            if (country, year) not in SHAPE_POPULATIONS or kind not in stems:
                continue
            sweep = kept[kept["kind"].isin([kind, f"{kind}-op"])]
            sweep = sweep[sweep["rate"] >= 0.10].sort_values("rate")
            if len(sweep) < 4:
                continue
            pies = sweep["pie"].tolist()
            spread = max(pies) - min(pies)
            observed = ("flat" if spread < SPREAD_GUARD else family(pies))
            predicted = "LOW" if p_by_kind[kind] < BOUNDARY else "HIGH"
            s3_rows.append({"population": f"{country}{year}", "label": kind,
                            "p": round(p_by_kind[kind], 3), "predicted": predicted,
                            "observed": observed})

    OUT = research_dir("ipums_sealed")
    s1 = pd.DataFrame(s1_rows)
    print("\n--- S1: transported prior, in-band, mixed routes ---")
    print(s1.to_string(index=False) if not s1.empty else "no scorable arms")
    if len(s1) < S1_FLOOR:
        print(f"UNDERPOWERED: {len(s1)} scorable against a floor of {S1_FLOOR} "
              f"-- no S1 verdict is claimed, as pre-registered")
    else:
        bar = int(np.ceil(S1_SHARE * len(s1)))
        correct = int(s1["rule"].sum())
        beats = (correct > int(s1["null_half"].sum())
                 and correct > int(s1["null_cutoff"].sum()))
        holds = correct >= bar and beats
        print(f"S1 {correct}/{len(s1)} (bar {bar}); null-0.5 "
              f"{int(s1['null_half'].sum())}, null-cutoff "
              f"{int(s1['null_cutoff'].sum())}; both beaten: {beats}  "
              f"{'HOLDS' if holds else 'FAILS'}")
    s2 = pd.DataFrame(s2_rows)
    print("\n--- S2: within-population ordering ---")
    print(s2.to_string(index=False) if not s2.empty else "no populations")
    scorable = s2[s2["monotone"]] if not s2.empty else s2
    if len(scorable) < S2_FLOOR:
        print(f"UNDERPOWERED: {len(scorable)} monotone populations against a floor "
              f"of {S2_FLOOR}")
    else:
        holds = bool((scorable["rho"] >= S2_RHO).all())
        print(f"S2 every monotone population at rho >= {S2_RHO}: "
              f"{'HOLDS' if holds else 'FAILS'}")
    s3 = pd.DataFrame(s3_rows)
    print("\n--- S3: real-anchored shape boundary ---")
    print(s3.to_string(index=False) if not s3.empty else "no sweeps")
    scored = s3[s3["observed"] != "flat"] if not s3.empty else s3
    if len(scored) < S3_FLOOR:
        print(f"UNDERPOWERED: {len(scored)} non-flat sweeps against a floor of "
              f"{S3_FLOOR}")
    else:
        correct = int((scored["predicted"] == scored["observed"]).sum())
        constant = max(int((scored["observed"] == "LOW").sum()),
                       int((scored["observed"] == "HIGH").sum()))
        holds = correct >= len(scored) - 1 and correct > constant
        print(f"S3 {correct}/{len(scored)} (bar {len(scored) - 1}, constant "
              f"{constant})  {'HOLDS' if holds else 'FAILS'}")
    for name, table in (("s1", s1), ("s2", s2), ("s3", s3)):
        if not table.empty:
            table.to_csv(OUT / f"{name}.csv", index=False)
    print(f"\nwrote {OUT}/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true",
                        help="report the delivered extract's schema and row counts")
    parser.add_argument("--measure", action="store_true",
                        help="stage B: print the quantile thresholds and op points "
                             "for their own pre-run commit")
    parser.add_argument("--score", action="store_true",
                        help="score the stored arms under the sealed protocol")
    args = parser.parse_args()
    if args.verify:
        verify()
    elif args.measure:
        measure()
    elif args.score:
        score()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
