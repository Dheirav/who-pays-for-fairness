"""Does the 2026 theory's condition predict the direction we measured?

**Individual work, beyond the course submission.**

**POST-HOC.** The directions were already known when this was written, so this is a
correspondence check between a published theory and existing measurements -- not a test
that could have surprised us. Labelled as such in document 27.

arXiv:2603.06901 Theorem 3, for the attribute-blind regime, defines

    zeta(x) = (eta(x) - c) / nu_DM(x)

with ``eta`` the score, ``c`` the unconstrained threshold, and ``nu_DM`` the constraint
gradient: positive on the *advantaged-like* region A, negative on the *disadvantaged-like*
region B. Over the extrema of each region,

    A_max <= B_min  =>  every group's rate weakly FALLS  (levelling down)
    B_max <  A_min  =>  every group's rate weakly RISES  (levelling up)

For demographic parity the gradient is the group density ratio, so ``nu`` is estimable from
a probe predicting the protected attribute from the features -- the same probe
``FairnessDataset.attribute_leakage`` already uses.

What this finds, written up in document 27:

1. **Neither strict condition holds on any population.** ``zeta`` diverges as ``nu -> 0``,
   so the empirical extrema of the two regions always overlap. The conditions are
   sufficient, not necessary, and are never met on real data.
2. **A relaxed ordering version does predict the direction**, and the overall selection rate
   proxies it at r = +0.935 -- which is what connects the theory to a quantity a
   practitioner can compute before building anything.

Run:  python -m src.experiments.analyse_zeta
"""
import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/home/dheirav/Code/Res_Ai")
from pathlib import Path
from src.datasets import build
from src.preprocessing import prepare
from src.models import build as build_model
from src.experiments.methods import BASE_MODEL
from sklearn.linear_model import LogisticRegression
R = Path("/home/dheirav/Code/Res_Ai/research/results")

def measure_seeds(spec, seeds, c=0.5, q=0.05):
    """Average the zeta extrema over seeds, as everything else in this project does.

    The first version of this ran a single seed while every other analysis here uses five,
    which made it the least robust number in the project and the one carrying the most
    weight.
    """
    got = [r for s in seeds if (r := measure(spec, seed=s, c=c, q=q))]
    if not got:
        return None
    out = {"pop": got[0]["pop"]}
    for k in got[0]:
        if k != "pop":
            out[k] = float(np.mean([g[k] for g in got]))
    out["n_seeds"] = len(got)
    return out


def measure(spec, seed=0, c=0.5, q=0.05):
    d = build(spec).load(); s = prepare(d, random_state=seed)
    m = build_model(BASE_MODEL, random_state=seed); m.fit(s.X_train, s.y_train)
    eta = m.predict_proba(s.X_test)[:, 1]
    a_tr = (np.asarray(s.a_train) == d.privileged_value).astype(int)
    probe = LogisticRegression(max_iter=2000).fit(s.X_train, a_tr)
    px = probe.predict_proba(s.X_test)[:, 1]; p = a_tr.mean()
    nu = px/p - (1-px)/(1-p)
    z = (eta - c)/nu; A, B = z[nu > 0], z[nu < 0]
    if len(A) < 50 or len(B) < 50: return None
    # observed outcome
    lu = R/f"{d.name}_levelling_up"/"levelling_up_runs.csv"
    if not lu.exists(): return None
    runs = pd.read_csv(lu); mm = runs.groupby("arm").mean(numeric_only=True)
    pie = mm.loc["expgrad_dp","positives_pct_change"]
    rate = mm.loc["baseline","positives"]/len(s.y_test)
    return {"pop": d.name, "rate": rate, "pie": pie,
            "A_max_q": np.quantile(A,1-q), "B_max_q": np.quantile(B,1-q),
            "A_min_q": np.quantile(A,q),   "B_min_q": np.quantile(B,q),
            "A_med": np.median(A), "B_med": np.median(B)}

SPECS = ["adult"] + \
    [f"acs:{st}" for st in ["AL","OR","UT","MS","WV","NM","ND","VT","WY","KY","SC","CT"]] + \
    [f"acs:AL:SEX:{t}" for t in (20000,30000,70000,100000)] + \
    [f"acs:OR:SEX:{t}" for t in (20000,30000,70000)] + \
    [f"acs:KY:SEX:{t}" for t in (20000,70000)] + \
    ["hmda:MS:derived_race","hmda:MS:derived_sex","hmda:LA:derived_race","hmda:LA:derived_sex"]
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--dataset", nargs="+", default=None)
_ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
_args = _ap.parse_args()
if _args.dataset: SPECS = _args.dataset
rows=[]
for sp in SPECS:
    try:
        r = measure_seeds(sp, _args.seeds)
        if r: rows.append(r); print(".", end="", flush=True)
    except Exception: print("x", end="", flush=True)
print()
f = pd.DataFrame(rows)
f["obs"] = np.where(f.pie > 0, "up", "down")
f["zeta_rule"] = np.where(f.A_max_q > f.B_max_q, "up", "down")
f["med_rule"]  = np.where(f.A_med  > f.B_med,  "up", "down")
f["rate_rule"] = np.where(f.rate > 0.5, "up", "down")
print(f[["pop","rate","pie","obs","zeta_rule","med_rule","rate_rule"]].round(3).to_string(index=False))
n=len(f)
print(f"\n  n = {n}")
for rule in ["zeta_rule","med_rule","rate_rule"]:
    print(f"    {rule:<11} agrees with observed: {(f[rule]==f.obs).sum()}/{n}")
print(f"\n    zeta_rule agrees with rate_rule: {(f.zeta_rule==f.rate_rule).sum()}/{n}")
sep = f.A_max_q - f.B_max_q
print(f"    r(selection rate, A_max_q - B_max_q) = {np.corrcoef(f.rate, sep)[0,1]:+.3f}")
print(f"    r(pie change,     A_max_q - B_max_q) = {np.corrcoef(f.pie,  sep)[0,1]:+.3f}")
from src.results_io import research_dir
out = research_dir("zeta")
f.to_csv(out / "zeta_correspondence.csv", index=False)
print(f"\nwrote {out}/zeta_correspondence.csv")
