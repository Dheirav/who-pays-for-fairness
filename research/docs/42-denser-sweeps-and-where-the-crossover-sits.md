# 42 — Twelve points instead of six: two populations reverse, and the crossover clusters

**Individual work, beyond the course submission.** The design, the point-selection rule and the
predictions were fixed in `src/experiments/viable_points.py` and
`src/experiments/analyse_dense.py` and committed before any arm was run.

## Why the sweeps were redesigned

[Document 40](40-the-arms-that-were-worse-than-doing-nothing.md) left the operating-point
sweeps unusable: six points, two exclusion rules, and Alabama, Kentucky and South Carolina
reduced to two arms each and declared void. The points had been chosen before either exclusion
rule existed.

They are now chosen from the data — twelve thresholds spread **evenly in selection rate**
across the band where the classifier still beats the trivial predictor, computed before any
mitigated arm exists.

## D1 — the redesign works

| population | arms retained of 12 |
|---|---|
| COMPAS | 12 |
| Alabama | 11 |
| South Carolina | 11 |
| Oregon | 10 |
| Kentucky | 10 |
| Dutch | 9 |

**Nine to twelve arms everywhere**, against two to four under the six-point design. D1 required
at least six and holds on all of them. Whatever else follows is now measured on arm sets large
enough to carry a verdict.

## D2 — and three of six fail, two of them by reversing

| population | r | spread | crossover | |
|---|---|---|---|---|
| Dutch | **+0.946** | 59.86 | 0.534–0.618 | HOLDS |
| South Carolina | **+0.905** | 6.12 | 0.505–0.554 | HOLDS |
| COMPAS | **+0.844** | 107.12 | 0.474–0.549 | HOLDS |
| Oregon | +0.664 | 5.91 | 0.528–0.589 | **FAILS** — just under the 0.70 bar |
| Alabama | **−0.368** | 21.02 | none | **FAILS** |
| Kentucky | **−0.654** | 2.63 | none | **FAILS** |

Alabama and Kentucky do not merely fail. They come back **negative**, on eleven and ten arms
with spreads well clear of document 37's guard. These are not underpowered arm sets and the
result cannot be dismissed as noise.

### Why, and it is a property of the design rather than of those states

The viable band — the range of selection rates reachable by a classifier worth deploying —
tops out at **0.566 on Alabama and 0.561 on Kentucky**. Every crossover located anywhere in
this project sits at or above roughly 0.47. So those two sweeps lie almost entirely **on one
side of the crossover**, and both are measuring the relationship *within* the low-rate region
rather than *across* the transition.

The six-point sweeps reached rates of 0.87 because they included arms whose classifier was
worse than a constant — the arms document 40 removed. Removing them was correct and it cost
those populations the only arms that crossed the transition.

**So the honest statement is narrower than before: the relationship is monotone across the
crossover, and is not monotone within the low-rate region on its own.** Oregon, whose viable
band reaches 0.702 and which therefore does span the transition, gives +0.664 — positive, and
just short of the bar. Dutch, COMPAS and South Carolina, whose bands reach 0.95, 0.95 and 0.56,
give +0.946, +0.844 and +0.905.

This is a real qualification and it was not visible under the six-point design, which mixed
sub-crossover arms with arms that should never have been included.

## D3 — the located crossover does not depend on the points

Where both designs produced a bracket, they agree:

| population | six-point | twelve-point | |
|---|---|---|---|
| Oregon | 0.362–0.653 | 0.528–0.589 | **overlap** |
| COMPAS | 0.485–0.689 | 0.474–0.549 | **overlap** |

The denser brackets are much narrower, as more points should make them, and sit inside the
coarser ones. The crossover is a property of the population and not of the sampling.

## The crossover clusters far more tightly than document 32 claimed

Collecting every located crossover in the project, by mid-point:

| population | domain | mid-point |
|---|---|---|
| Oregon (six-point) | income | 0.507 |
| COMPAS (twelve-point) | criminal justice | 0.511 |
| South Carolina | income | 0.530 |
| Oregon (twelve-point) | income | 0.558 |
| Dutch | occupational status | 0.576 |
| COMPAS (six-point) | criminal justice | 0.587 |
| **HMDA Louisiana** | **lending** | **0.659** |
| **HMDA pooled** | **lending** | **0.660** |
| **HMDA refinance** | **lending** | **0.758** |

**Four distinct non-lending populations — across three domains, two countries and four
instruments — cluster between 0.507 and 0.587.** Every lending estimate sits above 0.659.

[Document 32](32-the-rate-not-the-task.md) concluded the crossover is "population-specific",
on the strength of Alabama at 0.25–0.60 against Oregon at 0.35–0.65 — two coarse brackets whose
apparent difference is largely the imprecision of six points. With twelve, ACS income, criminal
justice and a Dutch census agree to within 0.08.

**What this does not license.** The lending cluster comes from **one mortgage market**
(Mississippi and Louisiana, 2018) measured three ways — the pooled arm contains Louisiana, and
refinance is a subset of both. So it is one population's worth of independent evidence, not
three, and "lending is different" is a hypothesis rather than a finding. What can be said is
that the non-lending estimates agree far better than expected, and that the single lending
market measured here does not join them.

## What changes

* Document 32's "population-specific" should become **"stable across three domains at roughly
  0.51–0.59, with one lending market sitting higher"**, which is both more useful and more
  falsifiable.
* [Document 35](35-what-to-do-about-it.md)'s instruction to measure your own crossover stands,
  but gains a prior: expect roughly 0.55 unless you are lending, and treat a wildly different
  answer as a reason to check your sweep rather than a discovery.
* The claim that the relationship holds **within** one side of the crossover is withdrawn. It
  holds across the transition; Alabama and Kentucky show it does not hold below it.
