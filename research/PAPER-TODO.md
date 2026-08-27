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

## 3. The claim hierarchy — DONE

Framing chosen: **phenomenon first, audit second, prediction third.** The full bucketing
lives in `research/EVIDENCE-MAP.md`, which is the artefact this section produced.

| | | |
|---|---|---|
| 3.1 | Central claim written, scope conditions beneath it — Introduction | done |
| 3.2 | Every result bucketed core / validation / boundary / history — `EVIDENCE-MAP.md`; Contributions reordered to match | done |
| 3.3 | 0.54 demoted — out of the abstract's headline and out of Contribution 1; 16 → 15 mentions, all now technical or explicitly framed as a fallible prior | done |
| 3.4 | Certificate inversion now opens the abstract and appears in the Introduction's third paragraph | done |
| 3.5 | Refusal promoted: named in the abstract, in the claim block as one of three outcomes, and made Contribution 2; §IX retitled *The Audit: Give, Take, or Refuse* | done |
| 3.6 | Allocation claim **narrowed**, not re-run | done |

**The central claim, as it now stands:**

> Whether a parity constraint hands out more favourable decisions or takes them away is a
> property of the population being decided about rather than of the fairness method — and a
> team can measure which one it is about to cause, before it causes it, from the rate at
> which its current model already says yes.

Four scope conditions sit beneath it, each bought with a failed test: direction only and
only above one percentage point; about four populations in five; in-processing not
post-processing; mostly predicted labels rather than allocations.

**3.6, decided.** Narrow rather than run experiment 7.1. The claim is stated as being about
predicted labels in five of eight sources, with the real-allocation evidence named as what
it is: HMDA's natural arms plus one sealed lending cohort that beat a loan-purpose null
8 vs 5 — preliminary, and sitting next to the held-out sweep failure on the same source.
7.1 remains available and would upgrade this; it is not needed for the claim to be honest.

**Also answered here** (the "someone could do this without the tool" objection): the rule is
simple, but the boundary is not knowable without measuring. Located crossovers span
0.28–0.65; in the one setting where populations were drawn at random rather than chosen —
US state-level income, fifty draws — no operating rate reached 0.55 and 25 of the 47 with a
computable rate sat inside that span, where an unaided reading of "often" against "rarely"
has nothing to say. A further fifth admit no rule at all, where the intuition answers
confidently and the audit declines. In the Introduction.

**Cost:** paper 19 → 20 pages, abstract 431 → 475 words, 0 overfull boxes. The 8- and
10-page variants were retuned (7.9pt/0.32in and 7.0pt/0.25in) and are back in limit with
content parity asserted.

---

## 4. Answer the objections that currently have no answer

| | | |
|---|---|---|
| 4.1 | **The circularity objection** — answered with measurement, `docs/74` | done |
| 4.2 | **Guard provenance** — audited from git, `docs/75` | done |
| 4.3 | **The 1.0-point guard is operational, not natural** — swept and stated | done |

**4.1, done.** The objection — *if locating the crossover requires sweeping the constraint,
what has prediction bought over fitting once and measuring?* — now has a demonstrated answer
in the audit section, backed by `src/experiments/analyse_circularity.py` and `docs/74`.

The answer is **narrower than the assertion it replaces**, which is the point. The sweep does
not buy a better estimate of what the constraint does at today's threshold; repeated fits at
one operating point buy that. It buys *shape*:

- **One fit's answer does not travel.** 69 of 639 adjacent arm pairs (11%) disagree on the
  sign, with both effects above the 1.0-point guard. The direction a single fit reports is
  not reliably a property of the population rather than of the threshold it used.
- **Populations sit close to their own boundary.** Of 21 disjoint person samples with both a
  located crossover and a natural arm, 11 are within 0.10 and 6 within 0.05; Florida 2018 is
  0.004 away. For those teams the direction is a threshold they control, and one fit reports
  the withdrawal without reporting the lever.
- **There is no constant to look up.** Florida 2018 crosses at 0.284 read by sex and 0.439
  read by race — the same people, two boundaries.

**Conceded in the same paragraph**, because it is true: 5 of 21 samples sit beyond 0.20 and
would have reached the same decision from one fit. That 24% over-states the waste, since
every sample in the set already passed the monotonicity screen and the 22% of populations
admitting no rule never enter it. The third leg (seed stability near the crossover;
sub-1.0-point arms unanimous only 55% of the time) is reported and **explicitly discounted**
— repeated fits at one point would expose it too, so it is not something only a sweep sees.

Guarded by `test_paper_circularity_answer_matches_the_sweeps`, negative-tested both ways.

---

**4.2, done — and it found two false statements in the paper.**

A guard's provenance is a property of the **(guard, result) pair**, not of the guard. The
paper had claimed all remaining guards "come from the exploratory phase" and that "every
sealed test from the re-seal onward carried both rules frozen". Neither was true.

- The **2-point void guard is retrospective**: written for the equalized-odds
  pre-registration, imported *backwards* into the threshold sweep. It moved three
  Connecticut arm sets from refutation to VOID — a change in the conjecture's favour. Doc 37
  had checked the other direction and found zero confirmations manufactured; the paper now
  says both halves.
- The **0.10 advisory boundary descends from a refuted clause** — sealed as a prediction,
  scored 4 of 8, withdrawn. It survives only as an exclusion, where it can refuse an arm but
  cannot manufacture a correct call. Disclosed rather than left to be found.
- **Three of four sealed analysers apply neither exclusion rule.** The re-seal scores all ten
  populations raw. Only the race cohort carries both. This cuts *for* the paper — the sealed
  record is less filtered than it had claimed — which is why nobody would have caught it.

**A correction to my own audit, recorded in `docs/75`.** The first draft dated the noise
floor and advisory boundary from the commits introducing the constants `NOISE_FLOOR` and
`ADVISORY_RATE` (08-23) and called both retrospective. Both datings were wrong — they caught
a *re-encoding*, not an introduction. The 2,500 floor is doc 15's, from 08-12. Searching a
constant's name rather than its value is the exact error the document exists to catch.

**4.3, done.** "Measured, not assumed" was doing two jobs. Sweeping the guard over the same
forty sealed arms: **every floor from 0.25 to 5.00 separates**, by +13% to +35%; the best is
0.25 (+35%) and the committed 1.0 gives +34%. The dip to +13% at 0.75 shows the estimate is
noisy at forty arms, so no value can be argued to be *the* right one. The floor's
**existence is measured; its value is operational.** New flag:
`analyse_verdicts --magnitude-sensitivity`.

Guarded by `test_paper_guard_provenance_matches_the_code`, which re-derives which analysers
apply which rules rather than trusting the prose. Its first version passed for the wrong
reason — a bare `"operational" in text` also matches `operationalizes` elsewhere — and is now
site-anchored and negative-tested.

**Cost:** paper stays 21 pages, 0 overfull, 80 pytest checks. The 10-page variant was retuned
to 7.8pt/0.30in.

**Cost:** paper 20 → 21 pages, 0 overfull, 79 pytest checks / 35 documented-claims checks.

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
