# 29 — Where deployed decision systems actually sit, and why the punchline was wrong

**Individual work, beyond the course submission.** The closing argument of every document in
this project asserted that lending, hiring and admissions are low-selection-rate settings,
so the regime where fairness constraints withdraw favourable decisions is the regime they
are deployed in. **That assertion was never measured, and it is wrong.**

## What the published figures say

| domain | source | selection rate | regime by [document 23](23-the-selection-rate-sets-the-direction.md) |
|---|---|---|---|
| **Résumé screening** | applicant-to-interview ratio, 2024 recruiting analytics | **0.02 – 0.03** | levelling **down**, extreme |
| Elite university admission | most-selective institutions | ~0.04 – 0.10 | levelling **down** |
| University admission, all four-year US institutions | NCES / IPEDS | **0.66 – 0.73** | levelling **up** |
| — public institutions | | ~0.78 | levelling **up** |
| **US mortgage lending** | HMDA 2023, aggregate denial rate 15.7% | **~0.84** | levelling **up** |

The applicant-to-interview ratio has itself been falling fast — around 0.15 in 2016, 0.084
in 2023, 0.02–0.03 in 2024 — so hiring has been moving *deeper* into the levelling-down
regime over the last decade.

## The claim that was wrong

"These domains are nearly all stingy, therefore the default is the harmful one."

They are not nearly all stingy. **They span the entire range and sit on opposite sides of
the crossover.** Résumé screening is at 0.02. Mortgage lending is at 0.84. Those are as far
apart as the scale allows, and both are flagship applications of algorithmic fairness.

## The corrected claim, which is stronger

> Two organisations can deploy the **identical** fairness constraint, in good faith, and get
> **opposite** effects on the total number of opportunities granted — and nothing in the
> fairness report tells either of them which happened.

A bank applying demographic parity to mortgage decisions is operating at ~0.84 and will
extend credit to more people. A firm applying the same constraint to résumé screening is
operating at ~0.02 and will interview fewer people overall. Same tool, same metric, same
reported success, opposite consequences.

That is a better argument than the original for three reasons:

1. **It does not depend on a claim about which regime is typical.** Both regimes are real
   and both are common.
2. **It makes the practical rule necessary rather than merely interesting.** If everything
   were low-rate, a practitioner could assume the worst and be right. Because the domains
   straddle the crossover, assuming is unsafe in both directions, and checking is the only
   option.
3. **It is checkable before any model exists**, from a historical approval rate — the one
   quantity every organisation in the table already has.

## An unplanned validation

The HMDA populations used here sit at selection rates of **0.758 and 0.808**. The published
national aggregate for US mortgage lending in 2023 is **~0.84**.

The lending data in this project is therefore representative of the domain rather than an
unusually permissive slice of it, which is what a reader might otherwise suspect of a single
state in a single year.

## Why this was not caught earlier

It was asserted in the first draft and repeated through eight documents without ever being
checked, because it sounded obviously true. The check took one afternoon of looking up
published statistics and required no computation at all.

That is the same failure mode as the two prior-art collisions: a claim that felt safe enough
not to verify. Three for three.

## Limits

* **Published aggregates, not measured on the data used here.** These are national figures
  from secondary sources, appropriate for a motivating argument and not for a result.
* **"Selection rate" is not defined identically across these sources.** Mortgage denial
  rates condition on completed applications; callback ratios condition on submitted
  applications; admission rates condition on applicants. The comparison is indicative of
  magnitude, not exact.
* **US only**, and mostly recent years.
* **Within-domain variation is large** and partly swamps the between-domain differences:
  elite and open-admission universities sit at opposite ends of the same table row. That
  strengthens the corrected claim rather than weakening it — even inside one domain, the
  direction is not safe to assume.
