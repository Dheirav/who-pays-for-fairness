# 05 — Who pays for the fairness fix?

**Not in the initiation document.** This is the first analysis here that goes beyond the
specification. Beyond the specification is not the same as new: the decomposition it uses
was published by Ferry et al. (2023) — see below. What is original here is the measurement
on this data, not the instrument.

## The question the ablation table cannot answer

Document 04 reports that ExpGrad-DP took demographic parity difference from 0.186 to
0.018. That single number is compatible with two opposite stories:

* **Levelling up** — women's selection rate rose to meet men's. Nobody was made
  worse off.
* **Levelling down** — men's selection rate fell to meet women's. The gap closed by
  taking favourable outcomes away.

Same metric. Same table row. Opposite ethics. Mittelstadt, Wachter & Russell (2023),
*The Unfairness of Fair Machine Learning*, argue the second is the common case and
that gap-only reporting conceals it. So this document decomposes the gap instead of
just reporting it.

## The decomposition

**The instrument is not ours.** Ferry, Aivodji, Gambs, Huguet & Siala (2023), *When
Mitigating Bias is Unfair* (arXiv:2302.07185), audit fairness interventions along five
dimensions; the first three are impact size (how many people were affected), change
direction (who moved which way) and decision rates (what happened to the acceptance rate).
That is what Findings 1–3 below measure, published before this project began. It is used
here because it is the right instrument for the question, not because it is this project's.
What this document contributes is the measurement on Adult under six in-processing methods
— in particular the rate-versus-people contrast in Finding 2, which FRAME does not draw.

Exact, not a heuristic. Write the signed gap as `gap = r_priv − r_unpriv`. Then

```
closure = gap_before − gap_after
        = (r_priv_before − r_priv_after) + (r_unpriv_after − r_unpriv_before)
          \______ privileged loss ______/   \______ unprivileged gain _______/
```

The two terms sum to the closure **identically**, so their ratio is a well-defined
share: 1.0 is pure levelling down, 0.0 is pure levelling up. `tests/test_incidence.py`
verifies this identity over 200 random cases and pins the boundary behaviour (8/8
passing), including that a gap which *widened* returns NaN rather than a
plausible-looking number.

## Finding 1 — measured in rates, every method looks even-handed

| method | DP closure | share paid by privileged (rates) |
|---|---|---|
| expgrad_dp | 0.168 | 0.575 |
| gridsearch_dp | 0.182 | 0.575 |
| expgrad_eo | 0.079 | 0.531 |
| adversarial_debiasing | 0.166 | 0.508 |
| prejudice_remover | 0.122 | 0.498 |

All five land between 0.50 and 0.58 — "mixed", slightly weighted toward the
privileged group giving something up. On this evidence, the methods look reasonable
and roughly interchangeable.

## Finding 2 — measured in people, the same methods are lopsided

The rate decomposition is **population-size blind**. The privileged group has 9,158
test subjects; the unprivileged group has 4,409. An equal *rate* movement in both is a
2.1× unequal *headcount*.

| method | men who lost | women who gained | share paid by privileged (people) | lost per gained |
|---|---|---|---|---|
| expgrad_dp | 908.8 | 316.4 | **0.742** | 2.68 |
| gridsearch_dp | 984.0 | 342.4 | **0.743** | 2.69 |
| adversarial_debiasing | 841.4 | 360.4 | 0.700 | 1.96 |
| prejudice_remover | 557.2 | 270.6 | 0.673 | 2.04 |
| expgrad_eo | 412.8 | 211.6 | 0.660 | 1.92 |

The share moves from ~0.50–0.58 to **0.66–0.74**. Both numbers are correct; they
answer different questions. The rate answer is the one everybody reports, and it makes
the transfer look substantially more even-handed than it is to the people in it.

## Finding 3 — every method shrank the pie. None levelled up.

Demographic parity constrains the *ratio* of favourable outcomes, not the total. A
method can satisfy it perfectly while handing out fewer positive decisions overall —
and every method here did:

| method | change in total favourable decisions |
|---|---|
| gridsearch_dp | **−22.1%** |
| expgrad_dp | −20.5% |
| adversarial_debiasing | −14.8% |
| prejudice_remover | −10.2% |
| expgrad_eo | −7.9% |

**Not one of the five closed the gap primarily by extending favourable decisions to
the disadvantaged group.** This is the aggregate form of levelling down, and it is
invisible in every metric the ablation table reports — accuracy, DP, EO, and disparate
impact are all unchanged in appearance whether the pie grew or shrank.

The TPR decomposition tells the same story from another angle: for ExpGrad-DP, men's
true-positive rate fell from 0.617 to 0.450 while women's rose from 0.527 to 0.711.
Qualified men were newly rejected so that qualified women could be accepted.

## Finding 4 — most of one method's individual-level effect is a coin flip

`ExponentiatedGradient` returns a *distribution* over classifiers and samples one at
predict time. So some subjects get a different decision on every call, regardless of
any fairness constraint.

The **arbitrariness floor** measures this: draw twice from the *same fitted model* and
count disagreements. Anything at or below the floor is the method being
non-deterministic, not the constraint doing work.

| method | subjects whose decision changed | arbitrariness floor | share of the effect that is noise |
|---|---|---|---|
| **expgrad_eo** | 5.17% | **3.18%** | **62.4%** |
| expgrad_dp | 9.21% | 1.18% | 12.8% |
| gridsearch_dp | 9.97% | 0 | 0% |
| prejudice_remover | 6.13% | 0 | 0% |
| adversarial_debiasing | 9.37% | 0 | 0% |

**About 62% of the individual decisions ExpGrad-EO changes are re-sampling, not
fairness.** Reporting "this constraint changed 5.2% of people's outcomes" would be
wrong by a factor of two and a half. The same applicant applying twice can get
different answers, for no reason connected to fairness or to their application.

This is not a bug — the base paper is explicit that the output is randomized, and the
randomization is what makes the theory work. It is a cost the paper does not quantify,
and it lands on individuals rather than on the aggregate. It connects to the
predictive-multiplicity literature (Marx, Calmon & Ustun, ICML 2020; Cooper et al.,
AAAI 2024): when many models fit the data comparably well, which one you deploy is
arbitrary, and the arbitrariness is borne by the people the models disagree about.

## Relation to the base paper

Agarwal et al. (2018) is a paper about **feasibility and optimality**: given a
constraint, find the most accurate classifier satisfying it. Within that frame every
result here is a success — the constraints are satisfied, cheaply.

None of the findings above contradict the paper. All four are **outside its frame**:

| | The paper asks | This document asks |
|---|---|---|
| 1–2 | Is the constraint satisfied? | Who was moved to satisfy it? |
| 3 | What is the accuracy cost? | Did the total number of favourable decisions fall? |
| 4 | Does the randomized classifier converge? | What does randomization cost an individual? |

The constructive reading: the reduction is agnostic about *how* it satisfies a
constraint, because the constraint is all it is told. Demographic parity is a
statement about a ratio, and the cheapest way to fix a ratio is usually to reduce the
numerator. If you want the gap closed by levelling up, **that has to be part of the
objective** — it will not happen by accident, and the fairness metric will not tell you
whether it did.
