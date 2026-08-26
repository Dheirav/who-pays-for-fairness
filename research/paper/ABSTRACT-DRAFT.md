# Proposed abstract — draft, not applied

Current abstract: **596 words**. Draft below: **338 words**.

`COMPRESSION-PLAN.md` lists the abstract as venue-pending and never-cut, so this is a
proposal, not an edit. It resolves the tension in the review: two boundaries are *added*
(magnitude non-transfer, predicted-labels-vs-allocations) while the paragraph gets shorter,
by moving secondary research history into the body where it already lives.

## What is dropped, and where it survives

| dropped from abstract | its home |
|---|---|
| the 2022 vintage / CPI / quantile lesson | Limitations (primary home, stated in full) |
| the ζ correspondence and 150 arms | Contributions + §Regime |
| the theory's 27/27 group-level result | §Regime |
| the Brazil/Mexico underpowered components | §resealed |
| detail of the race cohort's null scores | §resealed (one clause retained below) |

## What is added

- **magnitude does not transfer**, and a sealed model of it lost to predicting zero
- **five of eight sources are predicted labels, not allocations** — the reviewer's point 17,
  and the caveat a lending or public-sector reader will look for first

## Draft

> A group-fairness constraint requires two groups' selection rates to be close, but does not
> say how the gap should close: the disadvantaged group can be lifted, or the advantaged group
> pulled down. Both satisfy the constraint, and the metric that certifies it reports the same
> number in each case, so a deployment team cannot tell from its own dashboard which of the two
> it is about to cause. We show the direction is predictable in advance from a quantity every
> deploying organisation already has: the rate at which its current model says yes, read against
> that population's crossover. Across 67 disjoint population samples covering six decision
> domains and eight data sources on five countries, an in-processing parity constraint withdraws
> favourable decisions when the baseline selection rate sits below a crossover and extends them
> when it sits above; on UCI Adult five in-processing methods each shrink the pool by 7.9–22.1%,
> while on mortgage lending the identical constraint grows it.
>
> The claim is deliberately narrow, and sealed tests made it so. Direction is predictable within
> a population; magnitude is not, and a sealed model of it lost to predicting zero. Crossovers
> are population-specific — located values span 0.28 to 0.65 — so the fixed 0.54 prior is a
> fallible substitute for measuring one's own: sealed at 9 of 10 on never-measured populations
> (best constant 6; binomial tail 0.046, but only p ≈ 0.19 paired against that constant), and 5
> of 10 post-hoc on a second cohort. An earlier sealed attempt carrying an in-sample refinement
> failed at four of eight, and we report both outcomes because the difference between them is
> what a sealed test exists to expose. A screen-gated Brazilian race cohort separates the
> selection rate from label rarity in the rate's favour. The relationship survives a change of
> route, a twenty-five-fold tolerance range, a boosted-tree learner and a protected attribute
> swapped from sex to race, but disappears under post-processing — and a sealed deconfounding
> test locates that boundary at the optimizer family, not attribute access. One scope limit
> belongs here: in five of the eight sources the favourable decisions are predicted labels
> rather than allocations, and HMDA, the one source recording real approvals, is where our
> sweep protocol failed its held-out test. The practical outcome is a procedure that locates a
> team's own crossover from its deployed model, and refuses when it cannot.

## Two wording changes carried in

- "67 independent populations" → "**67 disjoint population samples**". *Independent* has a
  statistical reading that invites questions about independence assumptions the paper is not
  making; *disjoint person samples* is what the Setup section actually defines.
- "attribute-blind in-processing" → "**in-processing**" in the headline sentence, because the
  sealed deconfounding test found blindness is not load-bearing. See the title question below.
