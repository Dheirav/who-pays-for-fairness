# What the paper needs, everything, in order

Assembled 27 Aug from two external reviews, our own vulnerability audit, and what the last
week's experiments turned up. **M** = mechanical, has a right answer. **J** = judgement,
only you can settle it.

The ordering is deliberate: the mechanical work first, because it is cheap and because two
of the three errors found so far were things a check would have caught; then the judgement
that everything else waits on; then structure; then optional experiments.

---

## 1. Verifiable errors — do first, cheapest, highest embarrassment-per-hour

| | | |
|---|---|---|
| 1.1 | **Verify all 20 citations** against arXiv / Crossref / DOI records | M |
| 1.2 | **Check claim–evidence alignment**: does each cited work actually say what we say it says? | M |
| 1.3 | **Sweep for remaining count inconsistencies** across abstract, contributions, Setup, accounting table, ledger | M |

`ferry2023` was wrong in both authors *and* subtitle, and was found by an outside reader
rather than by us. Nineteen are unchecked. 1.2 matters because the same error attributed a
decomposition the paper leans on throughout to the wrong group — a wrong *characterisation*
of a correctly-cited work would be equally damaging and is not caught by 1.1.

---

## 2. Statistical presentation — no new data, real reanalysis

| | | |
|---|---|---|
| 2.1 | **Independent-unit accounting for every headline figure**: arms / populations / sources, computed not recalled | M |
| 2.2 | **Clustered inference** replacing naive binomial readings of 21/22, 24/26, 25/26, 18/19, 13/14 | M |
| 2.3 | **Leave-one-population-out** for the key success rates | M |
| 2.4 | **Restructure the crossover table**: separate P(a crossing exists) from the crossover estimate *conditional on* one existing | M |
| 2.5 | **State the survey sampling frame in the paper** — it lives in `survey-frame.json` and the paper never describes it | M |
| 2.6 | **A denominator box early in the paper**, showing how 161 / 52 / 50 / 150 / 19 relate | M |

2.2 is the reviewer's sharpest statistical point. Arms from one population are not
independent trials, and several headline ratios read as replication when they are not.
2.5 is the difference between "78% of randomly drawn populations" being checkable or not.

---

## 3. The claim hierarchy — the thing everything waits on

| | | |
|---|---|---|
| 3.1 | **Write the single central claim**, short enough to say aloud, with scope conditions listed *beneath* it rather than inside it | J |
| 3.2 | **Bucket every result**: core / validation / boundary / exploratory history | J |
| 3.3 | **Demote 0.54** from headline to a transported prior with a measured failure rate | J |
| 3.4 | **Lead with the certificate inverting** — 0.018 on the population that destroyed a fifth of its approvals, 0.010 on the one that created more than it destroyed | J |
| 3.5 | **Put the refusal procedure at the centre**, not in §IX | J |
| 3.6 | **Decide the allocation claim**: narrow it to predicted labels with preliminary lending evidence, *or* run 7.1 | J |

Nothing downstream can be settled before 3.1. Both reviews independently said the paper's
strongest result is obscured by everything competing with it, and that is a decision about
what the paper is, not a writing problem.

---

## 4. Answer the objections that currently have no answer

| | | |
|---|---|---|
| 4.1 | **The circularity objection.** If locating the crossover requires sweeping the constraint, what has prediction bought over simply fitting once and measuring? | J |
| 4.2 | **Guard provenance.** Distinguish exploratory design, confirmatory validation, and retrospective integration of the audit's thresholds | J |
| 4.3 | **The 1.0-point guard is operational, not natural** — say so rather than letting it read as a discovered constant | M |

4.1 is the strongest objection raised so far and the paper does not address it directly.
The honest answer is that the sweep buys the *shape* — whether you are near a boundary,
whether the direction is stable, whether a floor helps, whether the rule applies at all —
but the paper asserts this rather than showing it.

---

## 5. Structure

| | | |
|---|---|---|
| 5.1 | **Set a page target.** Governs everything below; without it, restructuring rearranges rather than compresses | J |
| 5.2 | **Reorder** against the evidence map | J |
| 5.3 | **Compress exploratory history**: failed derivation, refined rule, magnitude model, three shape boundaries | J |
| 5.4 | **Split the ledger into three categories** — exploratory / confirmatory / boundary — but **keep it in the main text** | J |
| 5.5 | **Fold docs 71–73's arguments** where only their numbers currently sit | M |

On 5.4 I disagree with the external recommendation to move the ledger to an appendix. Both
reviewers independently called it the most unusual thing about the paper. In the main text
sixteen mostly-failed registered tests read as rigour; in an appendix they read as hidden.

---

## 6. Trims

| | | |
|---|---|---|
| 6.1 | **Legal material** — trim the Discussion's implications, keep Scope's framing | J |
| 6.2 | **Abstract** — 427 words, still roughly double a normal one | J |
| 6.3 | **Failed-derivation provenance** — the outcome matters, the full history does not | J |

---

## 7. Optional experiments — only after 3.1 is settled

| | | |
|---|---|---|
| 7.1 | **A pre-registered real-allocation validation in a new domain** — employment screening, insurance underwriting, benefits eligibility, or a non-US lending register | J |
| 7.2 | **A second landscape survey at quantile-anchored labels**, to separate "this population is non-monotone" from "non-monotone *at this cutoff*" | J |
| 7.3 | **A fourth direction seal scored with `brier_skill`** rather than signs — the only route left to the paired p ≈ 0.19 | J |

Both external reviews independently named 7.1 as the single experiment that would most
improve the paper. It is also the only item here that cannot be resolved by narrowing a
claim instead — but narrowing is a legitimate alternative, and cheaper.

---

## The honest summary

Items 1 and 2 are perhaps a day, need no new compute, and fix things that are currently
wrong or unverifiable. Item 3 is a few hours of thinking and blocks everything after it.
Items 4 to 6 are the restructure proper. Item 7 is optional and should not start until 3.6
is decided, because narrowing the claim may make 7.1 unnecessary.

**The research is stronger than the paper.** Nothing on this list requires new data to make
the paper substantially better; only 7.1 would make the *result* stronger, and only if 3.6
goes that way.
