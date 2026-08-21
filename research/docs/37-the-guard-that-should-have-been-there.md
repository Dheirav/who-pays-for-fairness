# 37 — The guard that should have been in T1, applied retrospectively

**Individual work, beyond the course submission.** **A correction to this project's own
method**, not a new result. No experiment was run; every arm set already scored under
document 23's T1 is re-scored against a guard T1 never had, and the outcome of each is
reported whether or not it changes.

## The defect

[Document 23](23-the-selection-rate-sets-the-direction.md)'s **T1** requires a correlation
of at least +0.70 between the baseline selection rate and the change in the pool of
favourable decisions. It sets **no minimum on how much the pool has to move**.

That is a real hole. A correlation is scale-free: four arms that shift the pool by 0.05%,
0.10%, 0.13% and 0.14% can produce an r of any magnitude at all, because r measures ordering
rather than size. Connecticut does exactly this — **r = −0.924 on a spread of 0.10 percentage
points** — and T1 scores it as a refutation of the conjecture.

**The project already knew this.** [Document 33](33-the-rule-does-not-survive-equalized-odds.md)'s
**E0**, written months later, requires a **2.0-point spread** before any correlation is
allowed to count, and says why in as many words: *"any correlation is fitted to noise, and
reporting a large r would be the same mistake document 26 caught."* The later
pre-registration is better designed than the one carrying the headline, and nobody noticed
until Connecticut turned up.

## The audit

Every arm set ever scored under T1 — five populations across three constraint tolerances and
one alternative learner — re-scored with E0's guard applied.

| arm set | arms | r | spread | verdict |
|---|---|---|---|---|
| AL ε = 0.01 | 4 | +0.801 | 23.02 | informative |
| OR ε = 0.01 | 4 | +0.964 | 8.48 | informative |
| **CT ε = 0.01** | 4 | **−0.130** | **0.34** | **VOID** |
| KY ε = 0.01 | 4 | +0.802 | 16.43 | informative |
| SC ε = 0.01 | 4 | +0.880 | 14.53 | informative |
| AL ε = 0.05 | 4 | +0.944 | 5.21 | informative |
| OR ε = 0.05 | 4 | +0.851 | **2.03** | informative, barely |
| **CT ε = 0.05** | 4 | **−0.924** | **0.10** | **VOID** |
| KY ε = 0.05 | 4 | +0.817 | 7.09 | informative |
| SC ε = 0.05 | 4 | +0.898 | 2.29 | informative |
| AL ε = 0.002 | 4 | +0.784 | 23.18 | informative |
| OR ε = 0.002 | 4 | +0.963 | 9.11 | informative |
| **CT ε = 0.002** | 4 | **−0.332** | **0.60** | **VOID** |
| KY ε = 0.002 | 4 | +0.799 | 16.42 | informative |
| SC ε = 0.002 | 4 | +0.873 | 15.29 | informative |
| AL boosted trees | 4 | +0.902 | 22.86 | informative |
| OR boosted trees | 4 | +0.989 | 12.17 | informative |
| CT boosted trees | 4 | +0.923 | 3.40 | informative |
| KY boosted trees | 4 | +0.935 | 13.01 | informative |
| SC boosted trees | 4 | +0.986 | 12.59 | informative |

**Twenty arm sets. Three fall below the guard. All three are Connecticut under logistic
regression.**

## What the audit found, and what it did not

**No result is overturned. Zero arm sets passed T1 on noise.** The guard's only effect is to
turn three *failures* into three *voids*. Every conclusion this project has drawn from T1 was
drawn from an arm set that clears the bar, most of them by an order of magnitude.

That is the direction a missing guard is least damaging in — the hole could have manufactured
a false positive and did not — but the asymmetry is luck rather than design, and it does not
excuse the omission.

**What does change:** Connecticut can no longer be reported as a population where the
selection-rate rule fails. It is a population where the constraint barely moves the pool, so
the question does not arise there. [Document 34](34-the-crossover-survives-the-tolerance.md)
said "Connecticut fails at all three tolerances"; the correct statement is that Connecticut is
void at all three. Its *signs* are consistent with the rule at every tolerance — all four arms
sit above the crossover and all four level up — which is a weaker observation than a passed
correlation and a stronger one than a failure.

**One arm set is marginal.** Oregon at ε = 0.05 clears the guard with a spread of 2.03 points
against a bar of 2.0. It passes, and it is flagged here rather than left for someone else to
notice.

## Why Connecticut, and why only under a linear model

Connecticut's four arms span selection rates 0.306–0.821, and its lowest is already above
where the crossover sits in every other population measured. There is no arm below the
crossover, so there is nothing to move down and the pool changes by fractions of a percent.

Under boosted trees the same state has a spread of 3.40 points, clears the guard, and passes
T1 at +0.923 with a sign flip ([document 36](36-not-a-property-of-linear-models.md)). The
stronger learner produces a larger baseline parity gap and therefore has enough to remove for
the effect to appear. **Connecticut is not a counterexample; it is a population where the
linear model has almost nothing to take away.**

## The lesson, which is about method rather than about fairness

A pre-registration can be rigorous about the wrong thing. T1 fixes a threshold, names what
would refute it, and is entirely explicit — and it still cannot distinguish "the effect is
absent" from "nothing happened at all", because it never asks whether the manipulation
produced any effect to correlate with. E0 asks, because by then this project had already been
caught by [document 26](26-the-derivation-does-not-earn-its-keep.md), where a derivation
cleared every stated bar and was beaten by a constant.

The guard is now in `analyse_threshold.MIN_SPAN_PIE` and prints as **T1b**, before T1, so a
void arm set cannot be read as a verdict. `tests/test_documented_claims.py` asserts that the
retrospective audit still finds no arm set passing T1 on a sub-threshold spread — if one ever
appears, a documented conclusion is resting on noise and the test says so.
