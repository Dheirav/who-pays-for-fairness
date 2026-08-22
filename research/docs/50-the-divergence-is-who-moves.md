# 50 — The route divergence is a divergence in *who moves*, and it is not a rate band

**Individual work, beyond the course submission. Post-hoc re-analysis of stored results** —
nothing here was predicted in advance. Recomputed by `src/experiments/analyse_routes.py`
from the stored arms; `research/results/routes/routes.csv` is the table every number below
comes from.

Documents 46/47 left this as a described fact with a conjecture attached: below a selection
rate of ~0.10, the operating-point route turns *up* while the income-cutoff route goes
*down*, and the accuracy rule does not catch the divergent arms. Four findings, one of which
corrects the fact's own boundary.

## F1 — The divergence is a divergence in who moves

At matched selection rates and matched baseline gaps, the two routes close the gap by
opposite mechanisms. Every turn-up arm closes it by **lifting** the unprivileged group —
`unpriv_gained / priv_lost` between **1.34 and 2.25** — while every down arm at comparable
rates closes it by **cutting** the privileged group, ratios **0.00 to 0.83**. The pool's
direction is the shadow of that ratio: nothing else about the arms separates them. Missouri's
cutoff arm and Alabama's op087 arm sit at the same rate (0.026 / 0.031) with the same gap
(0.024 / 0.033); one cuts 34 privileged approvals to add 3, the other adds 41 to cut 24.

## F2 — It is not a property of the rate band: "below 0.10" was an artifact of which arms existed

**Connecticut's op087 arm turns up at a selection rate of 0.142** — gained/lost 2.05,
+25.3% — far above the supposed boundary. The turn-up arms are exactly the **deepest one or
two thresholds of each ACS sweep** (0.81–0.87), and the rates they land at span 0.027 to
0.142 depending on how rich the state is. The boundary variable is position in the fitted
score distribution's tail, not the selection rate. Document 47's statement "they agree in
the middle and diverge at the bottom" survives; "the bottom" means the bottom of the
*sweep*, not below any fixed rate.

## F3 — Why the accuracy rule cannot catch it, measured

All 15 arms below a rate of 0.10 — turn-up and crash alike — **clear** the
trivial-predictor bar. The bar constrains global error; the artifact lives in the group
composition near the decision line, which global accuracy does not see. This is no longer a
conjecture about the rule's blind spot: it is a column in the table.

## F4 — Five candidate selectors, each killed by a measured counterexample

What decides whether a deep-tail arm lifts (ACS) or cuts (COMPAS, Dutch)? Every aggregate
computable from the stored arms fails:

| candidate | counterexample |
|---|---|
| selection rate below 0.10 | CT op087 turns up at 0.142 |
| gap relative to rate | MO cutoff (0.92) ≈ AL op087 (1.06), opposite directions |
| qualified reservoir* | Dutch op0965 has reservoir 0.295 and still cuts |
| accuracy clearance | all 15 low-rate arms clear; directions split 7 up, 8 down |
| threshold height | COMPAS cuts at 0.775; AL lifts at 0.815 |

*Reservoir: the unprivileged group's label base rate minus its selection rate at the
operating point — how many qualified people the threshold holds under water. It is
**necessary** for lifting (every turn-up arm has reservoir ≥ 0.18; every cutoff arm ≤ 0.05,
which is *why* the cutoff route can only cut) but not sufficient.

The crisp exhibit: **Oregon op087 and the Dutch census op0965 agree on every stored
quantity** — rate 0.052 vs 0.050, gap 0.034 vs 0.036, reservoir 0.262 vs 0.295, both clear
the bar — **and move in opposite directions** (+6.9% vs −27.8%). Whatever selects lift
versus cut is not in the aggregates; it lives in the score geometry near the threshold or in
the optimiser's feasible set, and settling it needs score-level measurement, not another
correlation.

## What this changes

* **The claim's scope statement sharpens.** "The two routes diverge below ~0.10" becomes:
  *the deepest-tail arms of an operating-point sweep are unreliable in direction, at
  whatever rate they land*; the label route and natural sub-populations carry the claim at
  low rates. The paper's limitation is updated accordingly.
* **Document 45's exclusion finding gets its mechanism.** The low-gap arms the 0.05
  exclusion drops are precisely the deep-tail arms, and what makes them untrustworthy is
  now measured: their direction comes from the lift-versus-cut choice, which nothing
  observable predicts.
* **The reservoir explains the cutoff route's consistency.** A model trained on a genuinely
  rare label leaves no qualified reservoir (≤ 0.05 everywhere here), so lifting is never
  cheap and the constraint can only cut — which is why the natural route obeys the monotone
  rule all the way down (document 49's Nebraska at 0.014, −6.35%).

## What stays open

The selector. The concrete next step, if it is worth an afternoon: for the matched pair
(Oregon op087, Dutch op0965), compute each group's score density in a window around the
threshold from the fitted baselines, and check whether the lift arm has unprivileged mass
piled just under the line where the cut arm does not. That is a mechanism probe, not a
correlation, and it would either name the selector or kill the geometry story too.

## Addendum, same day — the geometry story is killed too

The probe was run (`analyse_routes.py --probe-geometry`, results in
`routes_geometry_probe.csv`), over all nine deep-tail arms rather than just the matched
pair, and **both** simple geometry candidates fail:

* **Depth-to-equalise.** How far each group's threshold would have to move to close the gap
  by lifting versus by cutting. Cutting is cheaper *in score units* on **all nine arms**
  (depth ratios 1.32–6.11) — including the five that lifted. The ratio does not separate the
  directions either: COMPAS cuts at 1.38, inside the lift arms' 1.32–1.85 range.
* **Mass near the line.** Under a global group-correlated tilt, more unprivileged mass just
  below the threshold than privileged mass just above it would make lifting dominate. The
  privileged mass is larger on **all nine arms** (mass ratios 0.15–0.85), lift and cut
  alike, and the ranges overlap completely.

So the selector is not in the baseline score distribution's simple summaries at all — six
candidates are now dead (rate, gap-to-rate, reservoir, accuracy clearance, threshold height,
and both geometry forms). What remains is the optimiser itself: ExpGrad does not move
thresholds, it reweights and refits, and its chosen direction must come from the feasible
set of *linear* tilts — which features correlate with group, and where each group's mass
moves under the cheapest tilt. Probing that means diffing the mitigated models' per-person
scores against the baselines on one lift arm and one cut arm, not computing another summary
of the baseline. That is the next and probably last cheap step; past it, this is a theory
question rather than a measurement one.
