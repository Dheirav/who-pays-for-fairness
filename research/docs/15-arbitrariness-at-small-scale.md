# 15 — When the coin flip is bigger than the constraint

**Individual work, beyond the course submission.** Extends Finding 4 of
[document 05](../../docs/05-who-pays.md) across 19 arms drawn from 10 populations.

## The finding this extends

`ExponentiatedGradient` returns a *distribution* over classifiers and samples one at
predict time, so some subjects get a different decision on every call regardless of any
fairness constraint. Document 05 measured this with an **arbitrariness floor** — draw
twice from the *same fitted model* and count disagreements — and found that on Adult,
**62% of the individual decisions ExpGrad-EO changes are re-sampling rather than
fairness**.

That was one population. The question here is whether the floor scales, and it does, in a
direction that matters.

## The result

Across 38 runs of the two randomized methods over 19 arms:

```
floor / churn > 1  in 5 of 38 runs
r(test-set size, floor / churn) = −0.360
```

A ratio above 1 means **the method's own randomness exceeds its entire measured effect** —
two draws from one fitted model disagree about more people than the fairness constraint
moved in the first place.

| population | method | test set | churn | floor | ratio |
|---|---|---|---|---|---|
| WY · sex | expgrad_eo | 920 | 0.0272 | 0.0460 | **1.57** |
| VT · race | expgrad_dp | 1,131 | 0.0460 | 0.0539 | **1.20** |
| VT · race | expgrad_eo | 1,131 | 0.0377 | 0.0445 | **1.17** |
| ND · sex | expgrad_eo | 1,337 | 0.0374 | 0.0516 | **1.37** |
| WV · race | expgrad_eo | 2,431 | 0.0132 | 0.0133 | **1.01** |

Every exceedance is in a small test set, and the gradient is monotone:

| test set | runs | mean floor/churn | exceedances |
|---|---|---|---|
| under 1,500 | 12 | **0.79** | 4 |
| 1,500–3,000 | 8 | 0.46 | 1 |
| over 3,000 | 18 | **0.35** | 0 |

On the largest populations roughly a third of the individual-level effect is noise. Below
1,500 test subjects it is four fifths, and in four runs it is all of it.

## Why this matters more than it first appears

The aggregate metrics do not move. A run where the floor exceeds the churn still reports a
respectable DP violation, a plausible accuracy, and a fairness improvement that looks
identical to one where the constraint did the work. Nothing in the ablation table
distinguishes them. The only way to see it is to draw twice from the same fitted model,
which no standard reporting pipeline does.

This is the same theme as documents 05 and 12 in a third setting: **the headline number
describes an outcome state and says nothing about the process that produced it.** Here the
process is partly a coin flip, and the metric is silent about that.

It also compounds the cross-flow result. [Document 11](11-replication-across-populations.md)
found the rate-to-people conversion degrading below roughly 10,000 rows because the
mitigation jitters and moves people in both directions at once. This is the same jitter
measured directly rather than inferred from its consequences — and it lands on the same
populations.

## The honest limits

* **Five exceedances out of 38** is a small count, and the correlation with size is
  −0.360, which is not strong. The size *ordering* in the banded table is cleaner than the
  correlation, and bands were chosen after seeing the data, so they illustrate rather than
  establish.
* **`churn_that_is_noise` clips at 1.0** (`src/incidence.py:186`). That is the right
  reporting choice — a method cannot be more than 100% noise — but it means the published
  column cannot show these cases at all. The unclipped ratio had to be recomputed from
  `arbitrariness_floor` and `total_churn` to find them, which is why this went unnoticed
  through documents 05 and 11.
* **Three seeds per ACS population** against five for Adult. Small test sets have noisy
  floors *and* noisy churn, and the ratio of two noisy quantities is noisier still. The
  effect is real in direction; its size should not be quoted precisely.
* **This says nothing about deterministic methods.** `gridsearch_dp`,
  `prejudice_remover` and `adversarial_debiasing` have a floor of zero by construction and
  are excluded.

## What it does not license

It does **not** show that these mitigations fail on small populations. The constraint is
still satisfied; DP still falls. What it shows is that *which individuals* pay for it is,
at small scale, substantially arbitrary — the same applicant can receive different
decisions from the same fitted model for reasons unconnected to fairness or to their
application. That is a cost borne by individuals and invisible in every aggregate the
method reports, which is precisely the predictive-multiplicity argument (Marx, Calmon &
Ustun, ICML 2020; Cooper et al., AAAI 2024) arriving in a fairness pipeline.
