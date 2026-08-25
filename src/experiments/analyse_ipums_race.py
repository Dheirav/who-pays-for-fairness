"""The fourth deconfounding attempt: Brazil's race arms, screened first, then sealed.

**Individual work, beyond the course submission.**

**Committed before any arm it scores exists, and the first seal run under document 66's
screen gate.** The third cohort was refused by Brazil's absent conditional sex gap; the
same extract carries RACE, and the IBGE contrast (White vs Black-or-Brown) is where
Brazilian income disparity actually lives. The gate ran before this seal, and its
measurements are recorded here as part of the commitment:

==========================  =====  =====  =====  =====  ====
population / label          p      rate   gap    acc    gate
==========================  =====  =====  =====  =====  ====
BR-2000 race, t280 (q0.45)  0.538  0.559  0.169  0.727  PASS
BR-2000 race, t380 (q0.60)  0.393  0.319  0.160  0.754  PASS
BR-2010 race, t600 (q0.45)  0.528  0.539  0.133  0.708  PASS
BR-2010 race, t800 (q0.60)  0.380  0.301  0.142  0.750  PASS
==========================  =====  =====  =====  =====  ====

Gaps three to five times the 0.05 floor; every label passes accuracy. The question is
the same as stage A's S1: with rates concentrated in-band and both routes mixed, does
the baseline selection rate against the 0.54 prior beat the 0.5-prior null and the
cutoff-only null — off-instrument, off-continent, on an attribute the instrument can
finally power?

Design, fixed here
------------------
Arms per population: the primary label's natural arm; four op arms on the primary label
at target rates (0.42, 0.48, 0.54, 0.60), thresholds from seed-0 baseline scores,
committed below; the secondary label's natural arm. Twelve arms, five seeds, the 60k
sealed subsamples of stage B.

**S1.** Scorable = in-band [0.40, 0.65] retained arms with seed-mean
|pool change| >= 1.0 point, under the frozen exclusions. Rule: down below 0.54, up at
or above. **Bar: correct on at least ceil(0.6 * scorable) and strictly more correct
than each null** (0.5-prior; cutoff-only from the label base rate). **Floor: at least
8 scorable arms**, else UNDERPOWERED.

**S2.** Spearman rate-vs-pool-change over each population's retained primary arms where
the landscape is monotone; bar rho >= +0.70 on every scorable population, floor 2.

Op thresholds, from seed-0 scores (committed):
BR-2000 t280: 0.42->0.6115, 0.48->0.5655, 0.54->0.5166, 0.60->0.4637.
BR-2010 t600: 0.42->0.5916, 0.48->0.5465, 0.54->0.4998, 0.60->0.4513.

Run:  python -m src.experiments.analyse_ipums_race     # score stored arms
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir

COHORT = {
    ("BR", "2000"): {"primary": 280, "secondary": 380,
                     "op_points": {0.42: 0.6115, 0.48: 0.5655,
                                   0.54: 0.5166, 0.60: 0.4637}},
    ("BR", "2010"): {"primary": 600, "secondary": 800,
                     "op_points": {0.42: 0.5916, 0.48: 0.5465,
                                   0.54: 0.4998, 0.60: 0.4513}},
}
PRIOR, NULL_A = 0.54, 0.50
MAGNITUDE_GUARD = 1.0
S1_SHARE, S1_FLOOR = 0.6, 8
S2_RHO, S2_FLOOR = 0.70, 2
GAP_FLOOR, NOISE_FLOOR = 0.05, 2500


def _arm(stem: str) -> dict | None:
    path = RESEARCH_RESULTS_DIR / stem / "levelling_up_runs.csv"
    if not path.exists():
        return None
    runs = pd.read_csv(path)
    base = runs[runs["arm"] == "baseline"]
    mit = runs[runs["arm"] == "expgrad_dp"]
    return {
        "rate": float(base["positives"].mean()) / float(base["n_test"].mean()),
        "gap": float(base["dp_diff"].mean()),
        "acc": float(base["accuracy"].mean()),
        "n_test": float(base["n_test"].mean()),
        "pie": float(mit["positives_pct_change"].mean()),
    }


def main() -> None:
    from ..datasets import build as build_dataset
    from ..datasets.ipums import SUBSAMPLE_ROWS

    suffix = f"_s{SUBSAMPLE_ROWS // 1000}k" if SUBSAMPLE_ROWS else ""
    call = lambda x, prior: "up" if x >= prior else "down"
    s1_rows, s2_rows = [], []
    for (country, year), entry in COHORT.items():
        arms = []
        for kind in ("primary", "secondary"):
            threshold = entry[kind]
            stem = f"ipums_income_{country.lower()}_{year}_race_t{threshold}{suffix}"
            spec = f"ipums:{country}:{year}:RACE:{threshold}"
            got = _arm(f"{stem}_levelling_up")
            if got:
                p = float(build_dataset(spec).load().y.mean())
                arms.append({"kind": kind, "route": "label", "p": p, **got})
        primary_stem = (f"ipums_income_{country.lower()}_{year}_race_"
                        f"t{entry['primary']}{suffix}")
        p_primary = next((a["p"] for a in arms if a["kind"] == "primary"), None)
        for rate, tau in entry["op_points"].items():
            code = str(tau).replace(".", "")
            got = _arm(f"{primary_stem}_levelling_up_op{code}")
            if got and p_primary is not None:
                arms.append({"kind": "primary-op", "route": "op",
                             "p": p_primary, **got})
        frame = pd.DataFrame(arms)
        if frame.empty:
            print(f"{country} {year}: no arms yet")
            continue
        trivial = frame["p"].apply(lambda p: max(p, 1 - p))
        kept = frame[(frame["gap"] >= GAP_FLOOR) & (frame["n_test"] >= NOISE_FLOOR)
                     & (frame["acc"] >= trivial)]
        in_band = kept[(kept["rate"] >= 0.40) & (kept["rate"] <= 0.65)
                       & (kept["pie"].abs() >= MAGNITUDE_GUARD)]
        for _, row in in_band.iterrows():
            actual = "up" if row["pie"] > 0 else "down"
            s1_rows.append({
                "population": f"{country}{year}-race", "route": row["route"],
                "rate": round(row["rate"], 3), "pie": round(row["pie"], 2),
                "actual": actual,
                "rule": call(row["rate"], PRIOR) == actual,
                "null_half": call(row["rate"], NULL_A) == actual,
                "null_cutoff": call(row["p"], PRIOR) == actual,
            })
        primary = kept[kept["kind"].isin(["primary", "primary-op"])]
        primary = primary.sort_values("rate")
        if len(primary) >= 4:
            pies = primary["pie"].tolist()
            signs = [x > 0 for x in pies]
            flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
            monotone = flips == 0 or (flips == 1 and not signs[0])
            rho = float(primary["rate"].corr(primary["pie"], method="spearman"))
            s2_rows.append({"population": f"{country}{year}-race",
                            "monotone": monotone,
                            "rho": round(rho, 3) if monotone else None,
                            "signs": "".join("+" if x > 0 else "-" for x in pies)})

    s1 = pd.DataFrame(s1_rows)
    print("--- S1: the prior against both nulls, race arms, in-band ---")
    print(s1.to_string(index=False) if not s1.empty else "no scorable arms")
    if len(s1) < S1_FLOOR:
        print(f"UNDERPOWERED: {len(s1)} scorable against a floor of {S1_FLOOR}")
    else:
        bar = int(np.ceil(S1_SHARE * len(s1)))
        correct = int(s1["rule"].sum())
        beats = (correct > int(s1["null_half"].sum())
                 and correct > int(s1["null_cutoff"].sum()))
        holds = correct >= bar and beats
        print(f"S1  {correct}/{len(s1)} (bar {bar}); null-0.5 "
              f"{int(s1['null_half'].sum())}, null-cutoff "
              f"{int(s1['null_cutoff'].sum())}; both beaten: {beats}  "
              f"{'HOLDS' if holds else 'FAILS'}")
    s2 = pd.DataFrame(s2_rows)
    print("\n--- S2: within-population ordering ---")
    print(s2.to_string(index=False) if not s2.empty else "no populations")
    scorable = s2[s2["monotone"]] if not s2.empty else s2
    if len(scorable) < S2_FLOOR:
        print(f"UNDERPOWERED: {len(scorable)} monotone against a floor of {S2_FLOOR}")
    else:
        holds = bool((scorable["rho"] >= S2_RHO).all())
        print(f"S2 every monotone population at rho >= {S2_RHO}: "
              f"{'HOLDS' if holds else 'FAILS'}")
    OUT = research_dir("ipums_sealed")
    for name, table in (("race_s1", s1), ("race_s2", s2)):
        if not table.empty:
            table.to_csv(OUT / f"{name}.csv", index=False)
    print(f"\nwrote {OUT}/")


if __name__ == "__main__":
    main()
