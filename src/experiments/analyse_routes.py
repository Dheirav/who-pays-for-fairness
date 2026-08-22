"""Why the two routes to a low selection rate disagree: who moves, not how many.

**Individual work, beyond the course submission. Post-hoc re-analysis of stored results —
nothing here was predicted in advance, and document 50 labels every claim accordingly.**

Documents 46/47 left a described fact with a conjecture attached: below a selection rate of
~0.10 the operating-point route turns *up* while the income-cutoff route goes *down*, and the
accuracy rule does not catch the divergent arms. This recomputes the divergence from the
stored arms at three depths:

1. **Who moves.** For every arm in and around the divergence region, the gap closure is
   decomposed into lifted unprivileged vs cut privileged (``unpriv_gained / priv_lost``).
   The pool's direction is the shadow of that ratio.
2. **The qualified reservoir.** The unprivileged group's *label* base rate minus its
   selection rate at the operating point — how many qualified people the threshold is
   holding under water. Derived per arm from the stored rate and gap plus the dataset's
   group shares: ``r_u = r - w_p * gap``.
3. **The accuracy bar.** Each arm's baseline accuracy against ``max(p, 1-p)`` from the
   dataset's own label, so "the rule does not catch it" is a measured row, not a memory.

Arms that predate the ``n_test`` column get their denominator from a sibling arm of the same
population — the split size is a property of the population, not the arm — rather than
producing the NaN-verdict failure this repository has already shipped once.

Run:  python -m src.experiments.analyse_routes
      python -m src.experiments.analyse_routes --dataset acs_income_al_2018   # one population
"""

from __future__ import annotations

import argparse
import re

import pandas as pd

from ..datasets import build
from ..results_io import RESEARCH_RESULTS_DIR, research_dir

# Population stem -> the dataset spec that carries its label and group structure. The
# operating-point route never changes the label, so one spec serves every op arm of a
# population; each cutoff arm is its own label and appears with its own spec below.
OP_POPULATIONS = {
    "acs_income_al_2018": "acs:AL",
    "acs_income_ct_2018": "acs:CT",
    "acs_income_ky_2018": "acs:KY",
    "acs_income_or_2018": "acs:OR",
    "acs_income_sc_2018": "acs:SC",
    "compas_2016_race": "compas",
    "dutch_2001_sex": "dutch",
    "lawschool_race": "lawschool",
}

# The cutoff-route arms at comparable rates: the sealed arms of documents 47 and 49 that sit
# below ~0.25, each a genuinely rarer label.
CUTOFF_ARMS = {
    "acs_income_mo_2018_t100000": "acs:MO:SEX:100000",
    "acs_income_az_2018_t100000": "acs:AZ:SEX:100000",
    "acs_income_in_2018_t70000": "acs:IN:SEX:70000",
    "acs_income_ne_2018_t100000": "acs:NE:SEX:100000",
    "acs_income_wa_2018_t70000": "acs:WA:SEX:70000",
}

OP_SUFFIX = re.compile(r"_levelling_up_(op[\d]+)$")


def read_runs(name: str) -> pd.DataFrame | None:
    path = RESEARCH_RESULTS_DIR / name / "levelling_up_runs.csv"
    return pd.read_csv(path) if path.exists() else None


def sibling_n_test(stem: str) -> float | None:
    """A denominator for pre-``n_test`` arms, from any arm of the same population."""
    for directory in RESEARCH_RESULTS_DIR.glob(f"{stem}_levelling_up*"):
        runs = read_runs(directory.name)
        if runs is not None and "n_test" in runs.columns:
            return float(runs["n_test"].mean())
    return None


def arm_facts(name: str, n_fallback: float | None) -> dict | None:
    runs = read_runs(name)
    if runs is None:
        return None
    base = runs[runs["arm"] == "baseline"]
    mit = runs[runs["arm"] == "expgrad_dp"]
    if base.empty or mit.empty:
        return None
    n = float(base["n_test"].mean()) if "n_test" in runs.columns else n_fallback
    if n is None or pd.isna(n):
        return None
    lost = float(mit["priv_lost"].mean())
    return {
        "rate": float(base["positives"].mean()) / n,
        "gap": float(base["dp_diff"].mean()),
        "accuracy": float(base["accuracy"].mean()),
        "gained_per_lost": float(mit["unpriv_gained"].mean()) / lost if lost else float("inf"),
        "dpool": float(mit["positives_pct_change"].mean()),
        "seeds": int(len(base)),
    }


def population_facts(spec: str) -> dict:
    dataset = build(spec).load()
    privileged = dataset.a == dataset.privileged_value
    p = float(dataset.y.mean())
    return {
        "w_p": float(privileged.mean()),
        "base_u": float(dataset.y[~privileged].mean()),
        "trivial": max(p, 1.0 - p),
    }


# The deep-tail arms the geometry probes run over: (spec, threshold, observed direction).
# Fixed here because they are the arms document 50 is about, not a tunable default.
PROBE_ARMS = [
    ("acs:OR", 0.87, "up"), ("acs:AL", 0.87, "up"), ("acs:KY", 0.87, "up"),
    ("acs:SC", 0.87, "up"), ("acs:CT", 0.87, "up"),
    ("dutch", 0.965, "down"), ("dutch", 0.93, "down"),
    ("compas", 0.775, "down"), ("lawschool", 0.995, "down (void)"),
]


def probe_geometry(seeds: int = 5) -> pd.DataFrame:
    """The two geometry candidates for the lift-or-cut selector, both of which fail.

    *Depth*: how far each group's threshold would have to move to equalise rates by
    lifting (unpriv down to priv's rate) or by cutting (priv up to unpriv's rate).
    *Mass*: how many of each group sit within a window of the threshold. Either would be a
    usable pre-fit guard if it separated the observed directions; document 50's addendum
    records that neither does.
    """
    import numpy as np

    from ..datasets import build as build_dataset
    from ..models import build as build_model
    from ..preprocessing import prepare

    rows = []
    for spec, tau, direction in PROBE_ARMS:
        dataset = build_dataset(spec).load()
        d_lift, d_cut, below_u, above_p = [], [], [], []
        for seed in range(seeds):
            split = prepare(dataset, random_state=seed)
            model = build_model("logistic_regression", random_state=seed)
            model.fit(split.X_train, split.y_train)
            s = model.predict_proba(split.X_test)[:, 1]
            priv = np.asarray(split.a_test == dataset.privileged_value)
            r_p, r_u = float((s[priv] > tau).mean()), float((s[~priv] > tau).mean())
            if r_p <= r_u:
                continue
            d_lift.append(tau - float(np.quantile(s[~priv], 1 - r_p)))
            d_cut.append(float(np.quantile(s[priv], 1 - r_u)) - tau)
            window = 0.02
            below_u.append(int(((s >= tau - window) & (s < tau) & ~priv).sum()))
            above_p.append(int(((s >= tau) & (s < tau + window) & priv).sum()))
        if not d_lift:
            continue
        rows.append({"arm": f"{spec}@{tau:g}", "observed": direction,
                     "d_lift": float(np.mean(d_lift)), "d_cut": float(np.mean(d_cut)),
                     "depth_ratio": float(np.mean(d_lift)) / float(np.mean(d_cut)),
                     "unpriv_near_below": float(np.mean(below_u)),
                     "priv_near_above": float(np.mean(above_p)),
                     "mass_ratio": float(np.mean(below_u)) / float(np.mean(above_p))})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=None,
                        help="restrict to one population stem (default: all)")
    parser.add_argument("--rate-ceiling", type=float, default=0.30,
                        help="survey arms whose baseline rate is below this")
    parser.add_argument("--probe-geometry", action="store_true",
                        help="refit the deep-tail baselines and score the two geometry "
                             "candidates for the lift-or-cut selector")
    args = parser.parse_args()

    if args.probe_geometry:
        probe = probe_geometry()
        print(probe.round(4).to_string(index=False))
        OUT = research_dir("routes")
        probe.round(6).to_csv(OUT / "routes_geometry_probe.csv", index=False)
        print(f"\nwrote {OUT}/routes_geometry_probe.csv")
        return

    rows = []
    for stem, spec in OP_POPULATIONS.items():
        if args.dataset and args.dataset != stem:
            continue
        pop = population_facts(spec)
        n_fb = sibling_n_test(stem)
        for directory in sorted(RESEARCH_RESULTS_DIR.glob(f"{stem}_levelling_up_op*")):
            match = OP_SUFFIX.search(directory.name)
            if not match:
                continue
            facts = arm_facts(directory.name, n_fb)
            if facts is None or facts["rate"] >= args.rate_ceiling:
                continue
            rows.append({"population": stem, "arm": match.group(1), "route": "op",
                         **facts, **pop})
    for stem, spec in CUTOFF_ARMS.items():
        if args.dataset and args.dataset != stem:
            continue
        # Cutoff arms all postdate the n_test column, so no sibling fallback is needed.
        facts = arm_facts(f"{stem}_levelling_up", None)
        if facts is None or facts["rate"] >= args.rate_ceiling:
            continue
        rows.append({"population": stem, "arm": "cutoff", "route": "cutoff",
                     **facts, **population_facts(spec)})

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("no arms matched")

    # Derived quantities: the unprivileged selection rate, the qualified reservoir, and
    # whether the arm clears the trivial-predictor bar.
    frame["r_unpriv"] = frame["rate"] - frame["w_p"] * frame["gap"]
    frame["reservoir"] = frame["base_u"] - frame["r_unpriv"]
    frame["clears_bar"] = frame["accuracy"] >= frame["trivial"]
    frame["direction"] = frame["dpool"].map(lambda v: "up" if v > 0 else "down")

    show = frame.sort_values(["route", "population", "rate"])
    print(show[["population", "arm", "route", "rate", "gap", "clears_bar",
                "reservoir", "gained_per_lost", "dpool", "direction", "seeds"]]
          .round(3).to_string(index=False))

    low = frame[frame["rate"] < 0.10]
    up = low[low["direction"] == "up"]
    down = low[low["direction"] == "down"]
    print(f"\nbelow 0.10: {len(low)} arms, {len(up)} up, {len(down)} down")
    if len(up) and len(down):
        print(f"  up arms:   gained/lost {up['gained_per_lost'].min():.2f}-"
              f"{up['gained_per_lost'].max():.2f}, all op route: "
              f"{sorted(set(up['route'])) == ['op']}")
        print(f"  down arms: gained/lost {down['gained_per_lost'].min():.2f}-"
              f"{down['gained_per_lost'].max():.2f}")
        print(f"  accuracy bar cleared by {int(low['clears_bar'].sum())}/{len(low)} — "
              f"the rule does not separate the directions")

    OUT = research_dir("routes")
    frame.round(6).to_csv(OUT / "routes.csv", index=False)
    print(f"\nwrote {OUT}/routes.csv")


if __name__ == "__main__":
    main()
