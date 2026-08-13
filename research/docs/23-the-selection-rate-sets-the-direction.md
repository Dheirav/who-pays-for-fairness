# 23 — What decides whether the constraint levels up or down

**Individual work, beyond the course submission.** Tests the conjecture
[document 22](22-levelling-down-is-not-universal.md) recorded and explicitly refused to
claim. Predictions and thresholds were fixed in `src/experiments/analyse_threshold.py`
before any arm was run.

## The question

Document 22 found the levelling-down direction reversing on HMDA mortgage data. The
obvious candidate was the **selection rate** — every survey population sits at 0.195–0.353
and HMDA's arms at 0.808 and 0.758 — but that comparison is worthless as evidence, because
the two datasets differ in domain, instrument, label semantics, feature set, group ratio,
proxy leakage and selection rate simultaneously.

## The design: move one number

ACS Income's label is "earns more than $50,000", a cutoff chosen by the benchmark. Moving
it on one fixed state varies the base rate while holding the population, the survey
instrument, the feature set, the group ratio and the proxy structure **exactly** fixed.

That the arms are otherwise identical is asserted rather than assumed:
`tests/test_acs_threshold.py` checks that the rows, the features, the protected groups and
the feature values are unchanged across cutoffs, and that the rebuilt problem reproduces
`ACSIncome` exactly at $50,000.

Alabama and Oregon, six cutoffs each, five seeds, ε = 0.01. Each state's $50,000 arm is
the one already committed for [document 21](21-the-floor-replicates.md), reused unchanged.

Oregon is the harder test of the two. At the default cutoff it has the **highest selection
rate of all nineteen survey populations** (0.354) and loses only 3.1% of its pie, so it
starts much nearer the crossover than Alabama does.

## The result — Alabama

| cutoff | selection rate | baseline DP | change in favourable decisions | destroyed per created |
|---|---|---|---|---|
| $100,000 | 0.030 | 0.033 | **−29.71%** | 22.03 |
| $70,000 | 0.099 | 0.091 | **−22.05%** | 2.18 |
| $50,000 | 0.252 | 0.129 | **−2.34%** | 1.14 |
| $30,000 | 0.598 | 0.111 | **+0.98%** | 0.83 |
| $20,000 | 0.760 | 0.074 | **+0.80%** | 0.75 |
| $10,000 | 0.890 | 0.039 | **+0.08%** | 0.89 |

Same people. Same features. Same groups. Only the finish line moved.

Reading Alabama first; Oregon follows below.

**T0 — the knob works.** HOLDS. Selection rate spans 0.029 to 0.890, monotone in the
cutoff.

**T1 — the direction tracks the selection rate.** HOLDS. r = **+0.801** across the four
non-degenerate arms, and the sign flips: −22.05% at rate 0.099 against +0.80% at 0.760.

**T2 — and it is not the base-rate gap in disguise.** HOLDS, and this is the one that
mattered. The gap is genuinely confounded with the rate here — r = −0.408 between them,
because the gap must vanish at both extremes — but partialling it out leaves
**r = +0.980**. Holding the gap fixed does not weaken the relationship; it sharpens it.

**T3 — the exchange rate agrees.** HOLDS. r = −0.874, from 2.18 favourable decisions
destroyed per one created at the lowest rate to 0.75 at the highest.

**The crossover sits between 0.25 and 0.60.** Below it the constraint takes decisions away;
above it, it hands them out.

## Oregon replicates it, more sharply

The same six cutoffs on Oregon, whose selection rate spans 0.043 to 0.908:

| | Alabama | **Oregon** | pooled, 8 arms |
|---|---|---|---|
| T1 r(selection rate, pie change) | +0.801 | **+0.964** | +0.775 |
| T2 partial r, base-rate gap held fixed | +0.980 | **+0.994** | +0.828 |
| T3 r(selection rate, exchange rate) | −0.874 | **−0.993** | −0.923 |
| last shrinking arm / first growing arm | 0.252 / 0.597 | **0.353 / 0.637** | — |

All four predictions hold in both states, and the crossover brackets agree: the last arm
that shrinks the pie sits at 0.25–0.35 and the first that grows it at 0.60–0.64 in both.
Oregon's own numbers are the stronger of the two despite starting nearer the crossover.

The pooled correlations are *weaker* than either state alone (+0.775 against +0.801 and
+0.964), which is what pooling two populations with different residual levels should do
and is reported rather than hidden. The per-state results are the evidence; the pooled
figure is a summary.

The manipulation check is evaluated per state rather than pooled, because monotonicity is
a within-population property — interleaving two states' selection rates would report a
failure that is an artifact of ordering. It holds in both.

## It places both datasets it was not fitted to

Adult sits at a selection rate of **0.205** and shrinks the pie by 20.5%. HMDA's race arm
sits at **0.808** and grows it by 4.3%. Both fall on the correct side of the crossover, and
neither is in the sweep.

**That is not a tight fit, and it should not be reported as one.** Alabama at 0.252 loses
2.34% where Adult at 0.205 loses 20.5% — an order of magnitude apart at a similar selection
rate. The selection rate is *a* moderator, not *the* determinant, and something else
(Adult's group ratio is 2.08 against Alabama's ~1.2) accounts for a great deal of the
residual. Document 21 already found Adult to be the extreme case in the study.

## The floor scales with the disease

Not predicted, and the most useful thing here. The selection-rate floor of
[document 19](19-levelling-up-is-expressible.md) rescues almost exactly as much as the
plain constraint destroys, across the entire range:

| selection rate | plain | with floor | rescued |
|---|---|---|---|
| 0.030 | −29.71% | **+1.22%** | +30.93 pts |
| 0.099 | −22.05% | **+2.06%** | +24.10 pts |
| 0.252 | −2.34% | **+4.26%** | +6.60 pts |
| 0.598 | +0.98% | +0.87% | −0.11 pts |
| 0.760 | +0.80% | +0.80% | −0.00 pts |
| 0.890 | +0.08% | +0.14% | +0.07 pts |

**r = −0.994** between how much the plain constraint destroys and how much the floor
recovers, and **−0.995 on Oregon**, and −0.992 pooled. Where there is nothing to fix it does
nothing, to within a tenth of a percentage point; where the plain constraint destroys 30% of
all favourable decisions it turns that into a small gain.

A remedy that scales with the severity of the problem and is inert where the problem is
absent is a much stronger recommendation than document 19's single-population result, and
it is the first evidence that the floor is worth applying by default rather than after
diagnosing a problem.

## What survives, and what does not

| claim | status |
|---|---|
| Document 22's conjecture | **Supported** on its own pre-registered single-factor test, including the confound check it was most likely to fail |
| "Levelling down is what parity constraints do" | **Wrong as stated.** It is what they do below a selection rate of roughly 0.3 |
| Selection rate as the *whole* explanation | **Not supported.** Adult and Alabama differ tenfold at a similar rate |
| Replication in a second population | **Holds.** Oregon reproduces all four predictions, more sharply than Alabama |
| The selection-rate floor | **Strengthened.** Its benefit tracks the damage at r = −0.994 across a 30-point range |

## Limits

* **Two states**, Alabama and Oregon, both ACS and both sex-arm. The crossover is quoted
  as a range because the two states bracket it differently (0.25–0.60 and 0.35–0.64), and
  a number would need more populations than this.
* **Four arms carry each state's correlation.** Two per state were excluded by the pre-registered T4 rule for
  having almost no baseline gap to close. The exclusions do not drive the result — across
  all six arms r = +0.838 for the pie and −0.596 for the exchange rate — but a correlation
  over four points is weak evidence on its own, and the monotone pattern across all six is
  the stronger claim. The pie change is *not* strictly monotone across all six: the top arm
  (+0.08% at rate 0.890) sits below the two beneath it, which is what a near-zero baseline
  gap should produce.
* **The exchange-rate correlation is outlier-sensitive.** The $100,000 arm's 22.03 is far
  outside the others, and dropping it moves r from −0.874 to −0.596.
* **One protected attribute, one base learner, one ε.** Sex, logistic regression, 0.01.
* **The mechanism is still a description, not an explanation.** "It is cheaper to lift the
  disadvantaged group when most people already qualify" is a plausible story consistent
  with the numbers. It has not been tested, and this project's record with plausible
  mechanistic stories is three proposed and three refuted (documents 16, 17, 20).
