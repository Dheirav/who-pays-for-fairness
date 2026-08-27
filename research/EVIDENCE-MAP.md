# Evidence map

Every result in the paper, sorted by the job it does. Written for item 3.2 of
`PAPER-TODO.md`, after two external reviews independently said the strongest result is
obscured by everything competing with it.

The sort is by **function**, not by quality. A result in *Boundary* is not a weaker result
than one in *Core*; it is answering a different question. A result in *History* is one the
paper still reports and still stands behind — it has simply stopped being load-bearing.

The rule for placement: **if this result were deleted, what breaks?**

- **Core** — the central claim itself dies.
- **Validation** — the claim survives but becomes assertion.
- **Boundary** — the claim survives and gets *wider* than it deserves. These exist to stop
  the claim being over-read, which is why removing them is the dangerous edit, not the safe one.
- **History** — nothing breaks. Kept because it is true, was sealed, and shows the shape of
  what was tried.

---

## The central claim

> Whether a parity constraint hands out more favourable decisions or takes them away is a
> property of the **population**, not of the fairness method — and a team can measure which
> one it is about to cause, before it causes it.

Everything below is either that claim, a defence of it, a fence around it, or a record of
what was tried on the way.

---

## Core — delete these and the claim dies

| Result | Figure | Where | Why it is core |
|---|---|---|---|
| **The direction is not fixed** | Adult: pool shrinks 7.9–22.1% across five methods. HMDA: identical constraint *grows* it 4.3% | §IV | Without a reversal there is no phenomenon, only levelling down |
| **The certifying metric cannot see it** | Parity difference 0.018 on the population that destroyed a fifth of its approvals; 0.010 on the one that created more than it destroyed | §IV | This is *why* anyone should care. The dashboard is not merely silent — it is comfortable |
| **The exchange rate** | 2.68 destroyed per 1 created (Adult); 0.50 (HMDA) | §IV | Turns "the direction differs" into a magnitude a team can act on |
| **The baseline selection rate predicts which** | Direction flips at a population-specific crossover; within-population monotone rise of Δpool with rate | §V | The predictor. Everything downstream is about how far this transports |
| **Measured at scale** | 161 disjoint population samples, six domains, eight sources, five countries | §III, §V | The reversal is not one dataset's quirk |
| **The audit locates a crossover on your own model** | Three overlapping estimates of the mortgage crossover agree | §V, §IX | Makes the finding a procedure rather than an observation |
| **The audit refuses when it cannot answer** | 22% of randomly drawn populations admit no directional rule; the procedure returns NON-MONOTONE, not a guess | §VIII | Refusal is what separates the procedure from the intuition. Without it the tool is a coin flip wearing a lab coat |

---

## Validation — delete these and the claim becomes assertion

| Result | Figure | Where |
|---|---|---|
| It is the **rate**, not label rarity | Screen-gated race cohort: cutoff-only null 5 of 10 against the rate rules' 8–9, sealed, ten arms from two person-samples | §VII |
| It is the rate, not the **loan product** | Sealed lending cohort: purpose-only null beaten 8 vs 5, on real approvals | §VII |
| It is the rate, not **task difficulty** | Fixed task, moved decision rule only, across the mid-range | §V |
| It is the rate, not the **group gap** | Five-domain comparison against the group-gap alternative | §V |
| Agrees with contemporaneous theory | Percentile-relaxed ordering agrees on 24 of 26 arms; r = +0.935; across 150 arms r = +0.850 (clustered 95% CI +0.813 to +0.892) | §I, §VIII |
| Survives a change of learner | Gradient-boosted probe r = +0.946 | §V |
| Survives route, tolerance, attribute | Twenty-five-fold tolerance range; sex → race | §V |
| The prediction transports at all | Sealed 9 of 10 on ten never-measured populations, best constant 6 | §VII |
| Within-population claim passes off-instrument | ρ ≥ 0.9 | §VII |

---

## Boundary — delete these and the claim overreaches

These are the load-bearing negatives. Each one was bought with a failed test.

| Boundary | What it rules out | Figure |
|---|---|---|
| **Magnitude is not predictable** | Any claim beyond direction | Sealed magnitude model lost to predicting zero: MAE 4.50 vs 0.77 |
| **Small effects have no reliable sign** | Any claim on sub-point effects | 95% correct above 1.0 point; **61% below it** — a coin flip |
| **Post-processing kills the relationship** | Any claim about fairness methods in general | r = −0.024. Sealed deconfounding locates the boundary at the **optimizer family**, not attribute access |
| **Equalized odds does not carry it** | Any claim about group-fairness constraints in general | r = +0.334 against a +0.70 bar |
| **22% of populations admit no rule** | Any claim of universality | Fifty populations, frame and seed fixed before any arm ran: 78% admit a rule, 64% classic |
| **The shape boundary does not transfer across tasks** | Any cross-task shape prediction | 0 of 4; every scored call inverted — transferred structure with a flipped sign, unexplained |
| **Very generous tasks are unsweepable** | Applicability at the top of the range | Computable test, stated |
| **Five of eight sources are predicted labels** | The allocation reading | Only HMDA records real approvals — and it is where the sweep protocol failed its held-out test (2 of 4) |
| **We cannot say why** | Any mechanistic claim | Derivation seal: beaten by a constant. We claim *predicts*, never *causes*; no pooled slope transfers |

---

## History — sealed, reported, no longer load-bearing

Kept in the paper because they were committed in advance and because the failures each
removed a stronger claim than the one that survives. **Demoted** as of this pass: none of
these should appear in the abstract's headline sentence or lead a contribution.

| Result | Status |
|---|---|
| **The fixed 0.54 prior** | A transported prior with a *measured failure rate*, not a constant of nature. 9 of 10 sealed, then 5 of 10 post-hoc — every miss agreeing with that population's own sweep. Located crossovers span **0.28 to 0.65**; the value 0.54 holds no in-band privilege (a 0.50 prior edged it by one arm) |
| Crossover clustering | Held until more states were measured; the cluster widened. Reported as first published, with its later history |
| Sealed rule, refined | 4 of 8. The extra clause added from early data was wrong and is withdrawn |
| Third direction cohort | 13 of 14, constant 9, paired p = 0.062. **Self-defeating by construction**: the magnitude guard deletes the near-crossover arms the paired test needs (r = +0.648 between distance from crossover and effect size), so four discordant arms is already p = 0.0625 |
| Crossover residual | Underpowered — 3 located against a floor of 6 |
| Six-market lending seal | Failed and underpowered; the natural-arm direction nonetheless holds 12 of 12 on all fifty markets |
| Third cohort (Brazil sex arms) | Refused by the audit's own disparity floor before scoring |
| Attribute-aware consistency | 9 of 9, but the theorem made the prior ≈ 1 — a consistency check, not forecasting skill |

**Of nine sealed or registered direction tests, one passed.** That number belongs in the
paper and stays there; it is the honest denominator for the sealed apparatus.

---

## What the map changes

1. **0.54 stops being a headline.** It is a transported prior in the History bucket with a
   measured failure rate. The Core claim is the *phenomenon* plus the *audit*, neither of
   which needs a fixed number.
2. **The certificate inversion leads.** 0.018 vs 0.010 is the single most compact statement
   of why the paper exists, and it currently sits mid-§IV.
3. **Refusal is a Core row, not a §IX implementation detail.** It is the only thing that
   distinguishes the procedure from the folk intuition "we say yes rarely, so fairness will
   take away". Located crossovers span 0.28–0.65; on fifty randomly drawn populations
   **53% sit inside that band** where the intuition has no answer, none sit clearly above
   it, and a further 22% follow no rule at all.
4. **The allocation claim narrows** rather than being defended. See 3.6.
