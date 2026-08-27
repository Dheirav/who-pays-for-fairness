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

---

## Panel review, round 3 — five blind referees plus one external

Five agents read the paper cold (statistician, fairness domain, practitioner, structural
editor, adversary) with no access to `PAPER-TODO.md`, `EVIDENCE-MAP.md` or the state note.
All five plus the external reviewer returned **major revision**; none returned reject.

**Question 0 converged.** All five wrote the same central claim unprompted, so §3 worked.
**All five also flagged the same overreach in it** — "property of the population rather than
the method" (contradicted by our own post-processing boundary) and "predict in advance" (the
deployable version needs the sweep). Six independent readers; that sentence goes.

### Fixed this pass

| | Defect | Fix |
|---|---|---|
| 1 | Four methods used and uncited — Zhang, Kamishima (2 of 5 in the ablation table), Feldman (a column in it), Hardt (the abstract's scope condition) | All cited, verified against Crossref/dblp/proceedings; method citations moved to the caption to avoid an overfull box |
| 2 | The ledger described four ways — 9 / "sixteen of which two" / "five failures" / **18 rows** | One canonical account derived from the table: 18 rows, 12 fail, 3 hold, 2 underpowered, 1 a reading. The 9-direction-test subset checks out and is now labelled as a subset |
| 3 | Table I and Table II disagreed on lending — 66 arms/50 markets vs 70/42 | Recomputed: **66 arms over 40 states**. The four extra are LA and MS, which predate the recorded denominator and so have no selection rate. New module `analyse_lending_coverage.py`; `independence.py` now requires a computable rate |
| 3b | **"All fifty markets" overstated by ten** — only 40 states carry a rate-bearing race arm | Corrected in four places, including the ledger |
| 7 | "Located crossovers span 0.28 to 0.65", repeated 8 times including the abstract | True span is **0.22 to 0.81**. Corrected everywhere. This cuts against us — a wider span makes the transported prior worse |
| 8 | Sequential correction applied at ×2 while our own abstract names a family of nine | Both readings now stated: ×2 gives 0.09, ×9 gives 0.41 |
| 9 | The people-share denominator misstated in the paper *and* in `incidence.py`'s docstring | Both corrected — see below |

**Guarded** by `test_paper_ledger_and_coverage_counts_are_derived_not_narrated`, which checks
the paper against *itself* rather than against data. Every prior guard verified a number
against the results; none checked whether the paper said the same thing twice. That gap
produced four of these seven. Negative-tested both ways.

### The finding that would have been fatal, and wasn't

The statistician's lead item was that Table IV's people-share column is arithmetically
impossible given its exchange rates: `share ≤ e/(1+e)`, and all five rows exceed it. The
argument is sound; the premise came from our prose. The real denominator is
`priv_lost + unpriv_gained`, a strict subset of "individuals whose decision changed", so the
ceiling does not bind. **The numbers were right and the description was not** — in the paper
and in the docstring, which also described `lost_per_gained` as a ratio it does not compute.
A careful referee read our definition correctly and derived an impossibility. That is worse
than a small numeric error, and it is fixed in both places.

### Parked, with a reason

**#4, post-processing counted as 17 populations and 18 of 18.** Both may be legitimate —
the correlation needs a selection rate and the group-direction check does not, exactly the
pattern that explains the lending discrepancy. But the post-processing cell has **no
committed module**, so neither number is reproducible and I will not patch numbers I cannot
derive. Same defect class as doc 72's fifty-market counts, which this pass did fix by
writing the module. This one needs the same treatment.

### Prior work — checked against the sources, not from memory

**No work requires a rescope.** The predictor is unclaimed in all four.

- **Hu & Chen (FAccT 2020)** is the real pre-emption, and it is on *our own dataset*: an
  in-processing parity-proxy constraint leaving both groups with fewer favourable
  classifications. Their existence claim is prior to ours; `docs/05-who-pays.md` must stop
  reading as unanticipated. Cited and distinguished.
- **Liu et al. (ICML 2018)** — the closest structural analogue, but a different quantity
  (one group's score change over time), a different axis (that group's own rate) and a
  different decision class (group-specific). Cited and distinguished in three respects.
  *The referee who called this our most damaging omission cited a non-existent author* —
  it is Rolf and Simchowitz, not "Ball".
- **Menon & Williamson (2018)** — a per-instance threshold correction, not the base-rate
  shift it was described as; it never evaluates the net. One sentence.
- **The infra-marginal line (Corbett-Davies 2017; Corbett-Davies, Gaebler, Nilforoshan,
  Shroff & Goel 2023 — five authors, not two)** does **not** supply our mechanism: their
  flip is one group's share of a *fixed budget*, and their explanatory variable is group
  prevalence, not the selection rate.

**But the mechanism concession was stronger than the evidence supports**, and this is the
substantive change. Zeng et al. give the parity-optimal thresholds in closed form for the
attribute-*aware* Bayes case; to first order the group sizes cancel and the pool's direction
is set by which group carries more score density at the margin. That is a candidate
mechanism three lines from a published theorem. "We cannot say why" is not defensible once a
referee finds it. The paper now says what is true: **we failed to extend a known marginal
argument to the blind randomized case**, which is a different and more honest claim.

### Block 1 — done

| | Was | Now |
|---|---|---|
| **Claim sentence** | "a property of the population rather than of the fairness method... from the rate at which its current model already says yes" | Scoped to in-processing, with the two load-bearing words named: the rate is free, **the crossover costs a sweep**. The dashboard-only version is the transported prior, and it is demoted in the same paragraph |
| **#5** | "each correlation stays between +0.80 and +0.92... the floor dependence does not reach the domain table" | True of the *natural-arm* column only. Table IX's 0.05 column **is** Table V's dense column, and South Carolina reads +0.905 at the committed floor against **+0.012** at 0.02. Conceded, with the earlier claim named as wrong |
| **#6** | "12 of 12... where the rule predicts extension" | Reports the constant: every arm sits at 0.82+, so the rule predicts up on all of them and **a constant scores 25 of 31 and 12 of 12 identically**. Consistency, not skill — and US mortgage supplies no market that straddles a crossover |
| **#10** | "+0.844 and +0.946 over twelve points each, both significant at p < 0.001" | Withdrawn. Twelve thresholds on one score vector are not twelve draws. The population-level statistic is given instead: four positive slopes of six, **sign test p = 0.34**, with the two negatives named as a stated exclusion rather than a rescue |

Guarded by `test_paper_block1_claims_stay_narrowed`, which pins the narrowing language rather
than a number — all four read perfectly well in their overclaimed form, which is why they
survived three audits. Negative-tested on all four; the first attempt at that negative test
silently failed because the phrases wrap across lines, which is the same trap that hid two of
these defects in the first place.

### Still open

- **The claim sentence** — six readers, same objection. Highest priority.
- **#5** §V-D's floor-robustness defence is false for South Carolina's dense sweep (+0.012 at
  floor 0.02), and Table IX's floor-0.05 column is byte-identical to Table V's dense sweeps.
- **#6** The 12-of-12 lending count has no discriminating power — every arm sits above the
  crossover, so a constant "up" ties it. `analyse_lending_coverage.py` now prints this;
  the paper's ledger row says it; §VIII-A does not yet.
- **#10** Dense-sweep p < 0.001 is pseudoreplicated — 12 thresholds on one score vector.
- **The lottery: cut**, on the editor's argument, which is our own control experiment — the
  signature does not appear at any natural operating point, and the rest of the paper
  addresses teams at theirs. Four sentences plus Algorithm 1 line 19; publish separately.
- **§5 structure.** The editor's measured cut list reaches 10.3 pages and puts the audit
  third instead of on page 15.

**Cost of this pass:** 21 → 22 pages, 0 overfull, 81 pytest checks. Variants retuned to
7.65pt and 6.9pt, which is the last time that is honest — the type is now small enough that
§5's cuts are the only real fix.

---

## Block 2 — the restructure, in progress

`paper.tex` is untouched and stays the **complete record** — 22 pages, every result, every
failed seal. It is what the doc-guards check and where a number should be looked up.
`paper-submission.tex` is the cut. Content that leaves the cut has not been withdrawn.

**22 pages / 21,762 words → 15 pages / 14,363 words** so far. Target is ~10 pages (~9,700).

### Done

| | | |
|---|---|---|
| Deleted | Cross-task shape subsection (adjudicates a hypothesis the paper never advances), the intersectional section (self-disclaimed as replication), the denominator table (an accounting of the accounting) | −1,224 |
| Contributions | Six numbered items restating the abstract → six short paragraphs | 990 → 563 |
| Re-seal subsection | The longest block in the paper, one undivided run of ten topics → the table, the two statistics, the sequential correction, the design limit, the paired-test ceiling | 1,550 → 646 |
| Lottery | **Cut to four sentences** plus Algorithm 1's line 19, on its own control experiment: the signature does not appear at any natural operating point, which is where every reader of this paper sits. Publish separately | 829 → 168 |
| Crossover history | The chronology goes; what constrains the claim stays | 1,132 → 511 |
| Abstract | Its second half pre-empted reviewers before the reader knew what was being caveated | 486 → 319 |
| Intro opening | Restated the abstract clause for clause | 150 → 103 |
| Circularity answer | 470 words of rebuttal → the two facts and the concession | 482 → 333 |
| Regime boundary, Reproducibility, Limitations, Discussion, failures, related work | | −3,900 |

### Two near-misses worth recording

**The cutting tool deleted the bibliography.** A section with no following section fell back
to `\end{document}` as its boundary, which swallowed all 29 references — and the result
compiled to 17 clean pages with no error. Only a citation-undefined warning caught it. The
tool now ends a block at the next heading *or the bibliography*, never at `\end{document}`,
and says so in the docstring. This is the second time on this paper that a bounded-looking
cut has overreached and still compiled.

**Three dangling references** (`tab:denominators`, `sec:crosstask`, `sec:lottery`,
`sec:discussion`) were left by cuts and caught by the build rather than by reading.

### Second pass

**15 pages / 13,585 words**, down from 22 / 21,762.

| | | |
|---|---|---|
| Audit section | Guard provenance to two sentences, the magnitude-floor sweep to its conclusion, the floor-as-remedy block deleted (the Discussion states it better) | 2,774 → 2,498 |
| Setup | The data paragraph compressed, and **the predicted-labels scope limit moved here from Limitations** — it bounds everything that follows, so it belongs where the reader first meets the eight sources | 1,445 → 1,235 |
| **Reorder** | The audit now runs third: phenomenon → predictor → regime boundary → **audit** → boundaries. Previously it began around page 15, after seven pages of caveats | — |
| **Ledger split** | Eight claim-constraining rows in the body; the other ten in the complete record. The caption no longer says "Nothing is omitted", which was false the moment it was cut | 682 → 313 |
| Float placement | `[!t]` on all 13 floats plus raised float fractions. **The ledger and Algorithm 1 were rendering after the references** while the text walked through their line numbers; nothing lands after them now | — |

### Two more near-misses

**An earlier cut left half a sentence behind.** Deleting the floor-as-remedy block, my code
searched backwards for the enclosing `\textbf{` and landed *inside* it, leaving `The floor is`
orphaned. It only became visible when the section swap put `\section{Boundaries}` immediately
after it. Compiled clean until then.

**A duplicated `sec:boundaries` label** — one on the section, one on a subsection I had
rewritten earlier. LaTeX resolves silently to the last one, so every cross-reference would
have pointed at the wrong target. Found by enumerating labels, not by reading.

### Remaining

- **The Audit section, 2,774 words** — the largest block left, and the one the editor says
  should be *promoted* to third. It deserves a careful pass rather than a fast one.
- **Setup and Method, 1,445** — compress the survey-methodology block to two sentences.
- **The reorder**, which is the single change the editor rated highest: audit third, regime
  boundary after the predictor, Algorithm 1 and the ledger into the body from after the
  references, predicted-labels-not-allocations into Setup where the reader first meets the
  eight sources.
- **Split the ledger three ways** — 8 claim-constraining rows in the body, the rest to the
  supplement.
- **Figure 1: eight panels → four**, and trim two long table captions.
- The submission version has **no guards of its own yet**. The record's 82 checks still pass;
  the cut needs its own once the content settles.


---

## The figures showed 5% of the record

Raised while cutting: the images are stale, and they represent a very small chunk of the data.
Both true, and the second is the serious one.

| | |
|---|---|
| What the figures drew | 8 populations, 72 arms — and one figure drew a single state |
| What the paper claims | 161 populations, 8 sources, 6 domains, 5 countries |
| **Coverage** | **5%** |

Worse, they were generated on 22 Aug and the generator still hardcoded `CROSSOVER =
(0.511, 0.576)` — the four-population cluster the paper has since **withdrawn**. The figure
was drawing, as a highlighted band, a claim the text retracts nine pages later.

And my plan for them was to cut the small multiples from eight panels to four, which would
have taken coverage from 5% to 2.5%. That was the wrong instinct and the interruption caught
it.

### Three figures that draw the record, `src/experiments/make_coverage_figures.py`

- **`fig-survey`** — all fifty populations of the landscape survey, at their operating rate,
  coloured by verdict. The paper's only randomly sampled evidence and its scope claim, drawn
  for the first time. It also shows what the sample does *not* contain: nothing above 0.55,
  and 25 of 47 inside the band where the rate alone cannot be read.
- **`fig-crossovers`** — all 22 located crossovers against the withdrawn cluster band, which
  makes the retraction visible instead of textual: the span is 0.22–0.81 and the cluster was
  an artefact of which populations had been swept. Florida appears twice, at 0.284 by sex and
  0.439 by race.
- **`fig-calibration`** — all forty sealed arms by effect size, showing almost every miss to
  the left of the one-point guard. The 95%-against-61% split had been prose only.

Coverage goes from 5% to the survey's 50, all 22 located crossovers, and all 40 sealed arms.
Added to **both** papers — the record makes the same claim about scale and had the same
problem. The small-multiples figure stays in both, with a caption now saying it is drawn for
shape and not for scale.

**The density variants are now superseded and left over limit.** They existed to compress the
complete record to a page count; at 7.65pt and 6.9pt there is no honest density left, and
shrinking further to absorb three figures would make an unreadable document to hit a number.
`paper-submission.tex` is a genuine cut and is what a page limit should be met with. The
reason is recorded in `make_variants.py` rather than left as a silent failure.


### Encoding, after a second look at the survey figure

Colour alone was carrying four verdict classes, two of which were adjacent oranges. Now:

| verdict | marker | fill | reading |
|---|---|---|---|
| classic (30) | circle | filled | a directional rule applies |
| monotone (7) | square | filled | a directional rule applies |
| inverted (2) | triangle | open | it does not |
| non-monotone (8) | cross | open | it does not |

**Filled against open carries the 78/22 split**, so the figure's whole point is legible
before the legend is read and survives being printed in greyscale. Palette moved to
Okabe-Ito across all three figures — the previous one paired a red and a green, which is the
common confusion, and had inverted and non-monotone as two shades of the same orange.

Two things the redraw exposed. The legend was sitting on top of the rising data and is now
in the empty right half. And **three of the fifty draws have no computable operating rate**,
so they cannot be placed on a rate axis at all: the figure was quietly showing 47 while its
title spoke of fifty. It now says so on the figure rather than leaving the arithmetic to
fail for a reader who counts the markers.


### Captions and the audit/boundaries overlap

**The long captions were a placement problem, not a page saving.** Both carried real
arguments, so they were moved into the body rather than cut:

- `tab:crossover` (176 → 55 words): the reason for separating whether a crossing exists from
  where it sits — the Dutch census reads 0.576 with a 95% interval of 0.572–0.580 under seeds
  alone, and *no* nested resample brackets a crossing at all. Plus the caution that the rates
  in that table are not one economic object.
- `tab:domains` (118 → 45): which half of the table carries weight, and why no *p*-value is
  quoted on the dense sweeps.

**The overlap, and one duplicate that was mine.** The Audit section had *two* cost paragraphs
— I wrote the second while repairing an orphaned sentence and never checked the section
already had one. Removed, with the single fact it added (the base-learner multiplier on a
production model) grafted onto the survivor.

Two real overlaps resolved:

- **UNSWEEPABLE was described twice** — as a verdict in the Audit and again as its own
  boundary subsection. Merged into the verdict, where the procedure is.
- **Boundaries was half sealed-test chronology**, which is what made it overlap the Audit's
  scope material. The failed first seal is compressed from 545 to 310 words: the lesson (a
  refinement drawn from in-sample data lost to the rule it replaced, and was route-specific)
  survives, and the ledger row carries the score.

### Where this leaves it

**15 pages, 13,564 words, zero overfull.** Down from 22 and 21,762.

The remaining gap to 10 is now mostly **the three new figures**, which occupy roughly 2.5
pages of area for 491 words of caption. That is a deliberate trade and it should be made
explicitly rather than by drift: the figures took evidence coverage from 5% of the record to
the survey's fifty, all 22 located crossovers and all 40 sealed arms. Reaching 10 pages from
here means choosing between them and roughly 2,500 further words of text — the Audit at 2,572
is still the largest block, and Setup at 1,235 has a survey-methodology passage that could go
to two sentences.


---

## Round 4 review: the cutting broke things, and the audit found them

Three referees on the cut, plus an external one. The framing news is good — the external
reviewer's one-sentence test came back as the intended claim, and both blind readers'
did too, so §3 and Block 1 landed. But **the cut-versus-record audit found ~30 defects and
most of them are mine.**

### Flat errors, fixed

| | What was wrong | Fixed |
|---|---|---|
| **Route-specificity stated backwards** | I wrote that the withdrawn clause "held where a rate is reached by moving the label and failed where it is reached by moving the decision threshold". The record says the opposite, and the cut's **own Table VIII** lists the failing arms as income cutoffs — label-route arms — so the sentence contradicted a table on the same page | yes |
| **Two withdrawals welded into one** | I merged the +0.979/+0.968 withdrawal (caused by the trivial-predictor exclusion on Alabama and LSAC) with the post-processing arithmetic artifact, asserting a cause the record contradicts. It also broke Setup's forward reference and lost "the same exclusion *rescued* mortgage lending" — a rule that moved two results in opposite directions | yes |
| **"Four populations of one instrument"** | Three instruments, three domains, two countries — contradicted by Table VI on the same page | yes |
| **"Four descriptions of the same table"** | Three. I conflated it with the separate "four counts were arm counts" | yes |
| **LSAC supplying the headline span** | I "corrected" the crossover span to 0.22–0.81 using a set that includes **the population the audit refuses as its showcase refusal**. Citing its crossover cites a rate no deployer can reach. The span over populations the audit accepts is **0.22–0.80**; `analyse_circularity` now flags refused populations | yes |

### Duplications I created, removed

- A **whole paragraph** duplicated between the Introduction and the Discussion, once with "25 of the 47" and once with "half".
- The predicted-labels limitation stated **twice** — the copy I moved to Setup says "this belongs here rather than in Limitations", and I left it in Limitations too. Self-refuting on the page.
- The LSAC refusal in two consecutive sentences; the arm-counts anecdote twice in Setup; "a constant divided by a shrinking baseline" twice.

### Five references went dead, and the fix restored a hedge

Cutting the lottery to four sentences orphaned Grgić-Hlača, Agarwal & Deshpande, Cotter and
Stone — and with them **the hedge that the charge is not "a lottery occurred" but that it
occurred unannounced**. Without it the paper was more accusatory than its evidence warrants.
Restored rather than deleted. Diana et al. lost the "we benchmark against minimax group
fairness" claim; restored too.

### Still outstanding from this round

- **The selection-rate floor is the least-evidenced claim in the paper** and it is the
  practical recommendation. "1.47 → 0.88" has no antecedent in the cut, no table, no method.
  Either present it or remove the remedy.
- **The survey-methodology convention block** (unweighted, nominal, no household clustering;
  crossovers shift 0.03–0.08 under weighting) was dropped entirely, and it qualifies every
  crossover number in the paper — including the 0.54-vs-0.50 argument, which is the same
  order of magnitude as the shift.
- **Dropped concessions** that should come back: "that seven is post-hoc and we do not claim
  it"; Iowa, the arm that split 3-of-5 across seeds identically to the Minnesota miss and
  scored *correct*; the race cohort's leave-one-out drop from 8/10 to 60%; the dead-band
  calibration (1 of 6 within 0.05 of the crossover).
- **Table I rows** pointing at analyses the cut no longer contains, and the intersectional
  section deleted whole when two sentences would have carried it.
- **Anonymisation** — the submission carries a name and email on the title page.

### The page decision, answered

The area chair's verdict: **cut the text, not the figures**, and the gap is 5 pages rather
than 2.5 — neither option alone reaches ten. Its reasoning is measurable: "0.22 to 0.81"
appears 7 times, "78%" 7 times, "9 of 10" 7 times, and the paper carries four separate
summary layers over a 10,500-word body. It would cut Figure 4 on merit (forty points
conveying two fractions the text states three times), shrink Figures 2 and 3 to single
column, and keep Figures 1 and 5. And it warns that §VII and §III need redrafting from
blank rather than trimming clause by clause, "or they will come back at 1,800 words each".


## Restorations, and the floor presented properly

**Five concessions restored** to both papers, all from the record:

- *"That seven is post-hoc and we do not claim it; what was sealed scored four."*
- **Iowa** — splits 3-of-5 across seeds *identically* to the Minnesota miss and scored
  **correct**. One of the headline nine was luck, and the paper says so again.
- The race cohort's **leave-one-out drop from 8 of 10 to 60%**, in the body at length and in
  the contributions in short form — a contributions list that hides it is the flattering
  summary the audit objected to.
- The **dead-band calibration**: 19 of 19 beyond 0.30 from the crossover, 23 of 27, 5 of 6,
  and **1 of 6 within 0.05**. This is the quantitative motivation for `INDETERMINATE` and it
  had been cut down to its conclusion.
- The **three survey conventions** — unweighted, nominal, no household clustering — with the
  measured consequence that **every located crossover shifts 0.03–0.08 under weighting**,
  which is the same order as the 0.54-against-0.50 argument. Stated as a reason to read the
  value as convention-relative and the *ordering* as the finding.

### The floor, measured instead of asserted — `analyse_floor.py`

It was the paper's practical recommendation and its least-evidenced claim: one sentence,
"about 0.12 accuracy points", "1.47 to 0.88", no denominator a reader could check. Two
referees said so independently.

Measured on the branch Algorithm 1 actually sends it to — natural arms only, both audit gates
applied, and only where the plain constraint withdraws: **86 arms over 70 populations.**

| | plain | with floor |
|---|---|---|
| Exchange rate | 1.33 | **0.94** |
| At or below one-for-one | 0 of 86 | **70 of 86** |
| Change in the pool | −2.94% | **+0.98%** |
| Accuracy cost | — | 0.05 pts |

**The numbers are better than the ones that were asserted** — the floor is four times cheaper
than claimed, and on the median withdrawing arm it does not soften the withdrawal but
*reverses* it. Two decisions changed the answer and both are stated in the module: natural
arms only (1,400 arms carry a floor variant, but most are at rates no deployer occupies), and
only the withdrawal branch (averaging over arms it extends flatters a remedy prescribed for
the other case).

**One quantity is deliberately not reported.** The benefit-scaling-with-damage correlation of
*r ≈ −0.99* is withdrawn: benefit is damage minus remainder, so the two share a term and the
correlation is arithmetic. A referee flagged it; it would have been a headline number that
means nothing.

Guarded by `test_paper_floor_table_matches_results`, which also asserts the old unsourced
figures have not returned.

**Cost:** record 24 pages, cut 16, both zero overfull, 84 checks. The cut grew because
restoring honesty costs words — the redrafts of §VII and §III are where the pages come back.
