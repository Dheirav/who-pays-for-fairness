# What to do next, and what will bite you

Live handover. Read this first, then `research/README.md` for the document index. Documents
11–68 are the research record; the paper is `research/paper/ieee/paper.tex`. The checklist this
replaced, with the original reasoning behind each completed item, is in
[`NEXT-archive.md`](NEXT-archive.md), including the two items completed on 22 Aug (the
re-seal, and the route-divergence mechanism).

**Standing rule.** Anything whose outcome could go either way gets its predictions, its
numerical thresholds **and the naive baseline it must beat** committed to git *before* the run.
After document 56, a corollary: **no hypothesis born from a campaign's data may be sealed
against arms measured the same day** — its test set must postdate it.
Re-analysis of existing results is labelled post-hoc. Both are fine; mislabelling is not. The
rule exists because a derivation of ours cleared every stated bar and was then beaten by a
constant (document 26). After document 49: a seal that predicts *signs* must also pre-state a
minimum-magnitude guard, because its one miss was an arm whose true effect is
indistinguishable from zero — a sign prediction has nothing to grip there, and discovering
that after the run cannot excuse the miss. After document 66: a two-stage seal carries a
**screen gate** between stage B and the runs — measure the baseline gaps, record which
populations the frozen exclusions refuse, and run only the survivors; a pre-data seal
cannot pre-screen, and Brazil's absent sex gap cost a day of compute that a seed-0
screen would have caught. After documents 69 and 70, two more, and they are the ones
most likely to be forgotten:

**State the expected yield and the minimum n before sealing, not after.** Four tests have
now returned UNDERPOWERED and a fifth failed on an unreachable bar — the third
direction cohort needed p < 0.05 on its discordant arms and its own magnitude guard left it
four, where four of four is already 0.0625. Every one of those was predictable from stored
results in five minutes. A seal that does not state how many scored arms it expects, and
what it will do if it gets fewer, is not finished.

**A magnitude guard and discordance are anti-correlated; a seal cannot maximise both.**
Effect size grows with distance from the crossover (r = +0.648), and the arms that
discriminate a rule from its null are the near-crossover ones. So the guard document 49
requires deletes exactly the evidence a paired test needs, and scaling the cohort scales
both sides. The way out is not a bigger cohort: it is to stop scoring signs. A seal that
commits a *probability* per arm and scores with `brier_skill()` (`src/skill.py`) weights
near-zero arms down instead of deleting them, and keeps their information. **No seal has
used it yet, and the next direction seal should.**

---

## Where the work stands

* **107 independent populations**, 6 domains, 8 data sources, 5 countries, 2 decades:
  the six-market lending seal added six HMDA states, the third cohort added Brazil
  2000/2010 and Mexico 2015/2020 (IPUMS, the 8th source), and 26 Aug added 24 fresh ACS
  state-years (16 at 2014, 14 at 2019) plus 16 HMDA markets — 8 sealed, 8 post-hoc.
  Cross-task and aware arms share persons with counted populations and are **not** new
  populations, and `hmda_ms_la` pools two markets already counted — the count guard
  enforces all three rules and is the authority on the number.
* **After document 52 the claim carries a sharper scope.** The sealed 9/10 stands, but the
  ten large states swept that night score the fixed 0.54 prior at 5/10 post-hoc, each miss
  consistent with its own state's sweep: the within-population relationship survives, the
  universal prior does not transfer everywhere, and located crossovers now span 0.28–0.65.
* **The claim, in full:** within a population, in the **attribute-blind in-processing** regime,
  the baseline selection rate against the ~0.54 prior predicts *which way* a parity constraint
  moves the pool of favourable decisions, and orders *how much* within the population. Neither
  the magnitude nor a pooled slope transfers between populations. The crossover is ~0.54 as a
  **prior for auditing, not a constant** — and the direction claim is now **sealed**: 9 of 10
  on never-measured states, bar 9, constant 6, committed first (document 49).
* **The paper** is 15 pages, IEEE format (compression Pass 3 pending the venue answer,
  cut list written in `paper/COMPRESSION-PLAN.md`), builds from `research/paper/ieee/build.sh`.
  `research/paper/draft-v2.md` is **superseded** — do not edit it; the pack copies the typeset
  PDF.
* **63 automated checks** across six suites re-derive every load-bearing figure from stored
  results. `test_skill` (26 Aug) pins the skill-margin arithmetic and re-derives the re-seal's
  reported statistics; `test_documented_claims` gained a guard on the paper's verdict
  distribution, which had already drifted once. Run all six before trusting anything:
  `for m in test_documented_claims test_output_isolation test_incidence test_acs_threshold test_new_instruments test_skill; do .venv/bin/python -m tests.$m; done`

  **Only 3 of the paper's 268 decimal figures are guarded.** The verdict totals were stale
  (27/45 in the text against 29/52 in the data) and nothing caught it. Guarding the ~15
  load-bearing figures is the outstanding hygiene job.

### Five results to know before touching anything

1. **The first sealed prediction failed; the re-seal of the simpler rule holds** (documents
   47, 49). Doc 47: predictions committed first scored **4 of 8, not beating a constant**,
   because they carried a refinement added two hours earlier from four in-sample populations;
   document 46 is withdrawn in place because of it. Doc 49: the pre-refinement rule — *down
   below 0.54, up above* — re-sealed against ten never-measured states scored **9 of 10, bar
   9, constant 6**. The one miss (MN, 0.699) is flagged by the sealed criterion as against
   the rule, not a boundary call; its effect is seed-noise around zero, noted post-hoc.
2. **The rule is method-bound, not blindness-bound** (documents 43, 47, **63**). Under
   post-processing it vanishes (r = −0.024 against +0.585) — but the sealed deconfounding
   cell shows the same reduction with the attribute readable keeps it (r = +0.672), so
   the boundary is the optimizer family and blindness is not load-bearing. The theorem's
   group-level prediction holds in every aware cell: 27/27 post-processing (nine
   pre-registered) plus 18/18 aware in-processing.
3. **The theory is silent, not refuted** (document 27). *Backfire*'s conditions are stated over
   extrema of a quantity that diverges on real data, and they are *sufficient, not necessary*.
   A relaxed form tracks the direction on 24 of 26. **Never write "0 of 26" as though datasets
   had been tested and failed.**
4. **The two routes agree in the middle and diverge at the bottom** (documents 32, 47). Below
   a selection rate of ~0.10 the operating-point route and the label route give opposite signs,
   and the accuracy rule does not separate them. Algorithm 1 now encodes this as the
   advisory rule, and the decile diff (doc 61) shows the mechanism: lift grades mass into
   the unprivileged mid-deciles, cut grants nothing below the top decile.
5. **Curve shape belongs to the question, not the base rate** (documents 54, 55, 60).
   Three shape seals failed three different ways — cross-year (a label artifact, resolved
   in 57), cross-attribute, and cross-task (0/4, every call inverted) — so the 0.365
   boundary is a property of the ACS income task only. Meanwhile the *direction* rule's
   expectation held at all six task arms' natural points, and Dutch's published crossover
   was downgraded by the nested bootstrap (doc 61): the solidly located non-lending
   crossovers are now three, not four.

---

## Open, in the order I would do them

- [ ] **What separates the states that level up below 0.54?** New top question (document
      52). TX, FL, NJ, VA, MA level up at natural rates 0.29–0.52 where every earlier
      population levelled down; several show U-shaped sweeps with no crossover at all. The
      misses are internally consistent (FL turns up at 0.288 and its located crossover is
      0.284), so something population-level is real here.
      **The base-rate boundary was sealed and scored** (document 54): FAILS at 4/6 against
      bar 5, constant not beaten — asymmetrically. The 2014 side went 4/4 *including both
      sealed within-state flips* (TX and NY, U-shaped in 2018, classic in 2014 exactly as
      the boundary called); the 2022 side failed because **all four 2022 populations
      invert** — positive at low rates, negative at high — a shape never seen in any
      earlier vintage and the relationship's first sign-flip. The inversion half of
      this item is **resolved by document 57**: the 2022 sign-flip was substantially the
      nominal label sliding (real-threshold reruns restore 2018-like behaviour; weighting
      and the recode acquitted). What remains open here is the pre-resolution half — why
      TX/FL/NJ/VA/MA level up at their natural rates and what governs curve shape — with
      the post-hoc note that real-anchoring rehabilitates the base-rate boundary as an
      IPUMS hypothesis. **The cross-task seal then failed harder (document 60): 0/4 with
      every call inverted on employment/coverage**, so the boundary is income-task-local
      and whatever governs shape involves the task's structure. IPUMS (Brazil 2000/2010,
      Mexico 2015/2020) remains the cross-country test, in the one domain the boundary
      has ever worked.
- [ ] **The crossover residual — still open, and harder** (document 52). The sealed test
      returned UNDERPOWERED (3 new locations against a minimum of 6) because locating a
      crossover assumes a monotone landscape and a third of the large states do not have
      one. A future design must handle U-shapes and levels-up-everywhere before it can ask
      what predicts the location; located values now span 0.28–0.65.
- [x] **A novelty audit for the lottery finding. DONE, citation-graph level** (document 53
      + addendum): 89 citing papers of four anchors screened, ten varied-vocabulary arXiv
      queries; the observation, the signature and the direction connection found nowhere.
      Four fences for the write-up: Long et al. 2023 (across-model multiplicity — now
      cited in the paper), Agarwal & Deshpande 2022 (theory's optimum randomizes at the
      boundary, not globally), Cotter et al. 2019 (derandomization), Grgić-Hlača et al.
      2017 (randomness *advocated* as a fairness device — the mirror image; the
      indictment is uninformative randomness, not randomness). The lottery is clear to
      promote into the paper.
- [ ] **The lift-or-cut selector** (document 50's open remainder). Six summary candidates
      are dead (rate, gap-to-rate, reservoir, accuracy clearance, threshold height, both
      geometry forms — `--probe-geometry`). The last cheap step ran 24 Aug
      (`--probe-diff`, doc 61): the decile table shows lift = graded mass into
      unprivileged deciles 3–8, cut = nothing below decile 9 — and the mixture-optimality
      result bounds the question: where the cut happens, **no** two-threshold blind
      alternative is feasible, so the selector is about when the constraint admits an
      informed solution at all. Past the decile table, it is a theory question.
- [ ] **A *sweepable* non-Western population.** Taiwan is non-Western but the viable-band test
      refused it, as it did LSAC. The IPUMS cohort is the answer, fully prepared and
      waiting on the extract; it would give the first crossovers located outside the West.
      (The count of solidly located crossovers fell to three when Dutch was downgraded —
      doc 61 — so the residual question of document 44 is even further from powered.)
- [ ] **Magnitude.** Ordered within a population (ρ up to +0.96), no pooled slope (+0.487,
      failed). A better model is possible; the current concession is honest without one.

## The fourth council (eight panelists, 25 Aug) — verification round

Four returning lenses (forecasting, examiner, skeptic, replication) all opened
"prior demands fully/largely implemented" and downgraded major→minor; the replication
director independently verified all 23 hashes and the Bitcoin receipts end-to-end.
Four fresh lenses: consistency auditor (8 mechanical bugs, all fixed), toolkit
maintainer (minor; caught one outright false sentence about two-member mixtures, fixed),
causal methodologist (**major**: the regime contrast confounds attribute access with
optimizer family — fix is attribute-aware *in-processing* on the 17 populations, loaders
already support `include_protected_in_features`), economist (**major**: the $60k
re-anchoring conflates CPI with base-rate matching and is partly circular; weighted
crossover replication owed; PUMS income allocation untested). **Text batch landed at
`0303c01`** (34 edits: Dutch propagated to table/figure/prior-provenance with the
no-call-changes check verified, cross-task seal restated neutrally in its own subsection
`sec:crosstask`, lottery claims family-scoped, corrected sequential tail ≈0.09 printed,
Reg B §1002.15 conditions, anchoring paragraph in present tense, guards provenance,
five-not-six methods). **Cheap-compute batch DONE (document 62)**: the two anchorings disagree — Ohio stays
inverted at strict-CPI $58,275 while classic at base-rate-matched $60k, so **the
quantile is the anchor** and doc 57 is refined in place; the lottery's degenerate
support observed member-by-member; no lottery on either HMDA natural arm (9/9);
the prior recomputed without Dutch changes no call. **The causal major's experiment is DONE (document 63)**: the sealed deconfounding
cell returned the method reading — blindness is not load-bearing, the regime framing is
corrected in place. **The economist's items are DONE (document 64)**: weights shift every
crossover down 0.03–0.08 but the ordering and outliers hold (the 0.54 prior belongs to
the unweighted convention, now said in the paper); household-clustered intervals widen
modestly; allocation is a uniform level effect, acquitted as a 2022 mechanism. Round
four is fully discharged except what waits on IPUMS.

## The third council (ten panelists, 25 Aug) — done, fixes applied (document 58)

Ten fresh lenses (HCI, examiner, EU law, sociology, ML systems, Goodhart, pedagogy,
replication lab, forecasting, hostile skeptic): 6 minor / 4 major, no rejects. All
text-only fixes and the cheap-compute batch are in the paper (14 pp, builds clean, 55
checks green + pytest now runnable, 65 pass). Three new committed analyses:
`analyse_verdicts.py` (verdict distribution 27/6/10/1/1 over 45 swept pairs, 27/27
consistent; `--sealed-sensitivity`: re-seal keeps 7 of 8 vs constant 5 at the frozen
floor), `--probe-natural` in `analyse_routes.py` (**no lottery at any of 7 natural
arms** — severe-operating-point phenomenon; per-fit timing became the cost paragraph).
Algorithm 1 gained INDETERMINATE, the 0.10 advisory rule and the lottery probe; the
paired sign test (p ≈ 0.19) stands beside the binomial; all eleven seal→score hash pairs
are pinned in the paper, orderings re-verified. **The follow-up batch landed as document
59** (25 Aug): derandomization 10/10 (`analyse_derandomized.py`), domain table
floor-invariant (`analyse_floor_sensitivity.py`), seed stability 16/19 unanimous with
the splits exactly the near-zero arms (`--seed-stability`), and two worked traces in the
paper's appendix. Still owed from this round: multi-market HMDA sweeps — **the downloads are done**
(24 Aug: AL, SC, TN, GA, NC, OH joined MS, LA; 663 MB, checksummed in the manifest), so
what remains is screen → seal → sweep, roughly a day's chain. External timestamping is
now practice: both live seals (IPUMS stage A `50d467f`, cross-task `d8bfae8`) carry
receipts in `research/seals/`, and the cross-task pair is scored (doc 60).

## The second council (eight panelists, 24 Aug) — synthesis and state

Verdicts: major ×5, minor ×2, **accept-with-conditions** (meta-reviewer: "top decile on
rigor and honesty"). Textual batch landed at `55dd84e`; history pushed, seal hashes now in
the paper. The load-bearing outcomes:

* **The red team broke the 9/10's strong reading**: all label-route arms, mid-band
  unsampled, so the pass cannot discriminate rate from label rarity nor 0.54 from any
  mid-band prior — admitted in the paper where the claim is made. **Third-cohort spec
  (binding, for IPUMS):** off-instrument, rates concentrated in [0.40, 0.65], both routes
  mixed, scored head-to-head against the cutoff-only and 0.5-prior nulls, with the
  minimum-magnitude guard and exclusions frozen in the seal.
* **The inversion is RESOLVED (document 57)**: (1) weighting exculpated at label level;
  (2) **real-threshold drift confirmed as the substantial cause** — at $60k Ohio is
  cleanly classic at its old crossover, AL/SC lose their inverted limbs, NV stays
  below-guard noise; (3) composition reweighting recorded unnecessary. No detected
  time-dependence 2014–2022 at constant real value; doc 54 superseded; the paper's
  vintage caveat replaced by the real-anchor-your-labels lesson. Open lead kept: 2022
  *models* under-express a sex gap the labels still carry (`analyse_weights.py` side-fact).
  Post-hoc, for IPUMS only: the base-rate boundary would have called the real-anchored
  2022 shapes correctly.
* **Repro packaging**: pushed; lockfile added; checksums done 25 Aug
  (`research/data-manifest.csv`, 59 files); retrieval-recipe URLs still owed.
* **Philosopher/economist items**: normative baseline, Broome/Stone, welfare-vocabulary,
  survey conventions — all in the paper as of `55dd84e`. HMDA applicant-selection
  paragraph still owed if the lending contrast is ever asserted harder.

## The review council's remaining items (textual batch landed at `2e5432d`)

Six-panel review, 24 Aug; verdict major-revision 4–2; all converged textual fixes applied.
Still open, by kind:

* **Structural** — the compression Pass 3 (already planned) now also carries the council's
  merge: sealed narrative unified with the ledger, surviving claim promoted to a titled
  destination, intersectional relocated. Venue answer decides the depth of the cut.
* **Analyses** — DONE except one: seed stability and the four-floor correlations landed
  as document 59; the blind-mixture comparison (feasible set empty — the lottery is
  in-class necessary) and the nested bootstrap (Dutch downgraded, three rows confirmed)
  landed as document 61. The relaxed-ζ head-to-head is now DONE too
  (document 68: rate 18/19 vs ζ 17/19 on the sealed cohorts; the proxy holds on 150
  populations with an interval and a second probe). **No analysis or compute item
  remains open anywhere in the project**; everything left is human-gated.
* **The third sealed cohort** the statistician demands is IPUMS — **stage A of its
  two-stage seal is committed** (25 Aug): `src/datasets/ipums.py` (chunked loader,
  quantile-only thresholds, sentinel handling, verified end-to-end on a synthetic
  extract) and `src/experiments/analyse_ipums_sealed.py` (the full protocol: 4
  populations, labels at income quantiles 0.45/0.60/0.75, op arms at target rates
  0.42–0.60, S1 prior-vs-both-nulls with the ≥1.0-point magnitude guard and floor 12,
  S2 within-population ρ ≥ 0.70, S3 real-anchored shape boundary, all bars fixed).
  **Arrival-day ceremony, in order:** place the extract in `data/ipums/` → `--verify`
  (schema + row counts) → `--measure` (quantile thresholds + seed-0 op points) → paste
  into `THRESHOLDS_STAGE_B`, commit → `ots stamp` that commit's hash and commit the
  receipt to `research/seals/` → only then run the arms (~40 arms × 5 seeds,
  sequentially — the 8 GB VM) → `--score`. OpenTimestamps client is in the venv and
  requirements; the dry-run stamped against four public calendars.
* **Supervisor-level** — title revision to the bounded claim (area chair's #1), and
  whether the lottery is promoted to a headline contribution.

## Sealed, swept, and scored

* **ACSEmployment and ACSPublicCoverage — sealed and scored 24 Aug** (`analyse_task_shapes.py`).
  The 23 Aug scratch screen's sex-arm claims did **not** survive re-measurement: every
  coverage-by-sex arm fails the 0.05 gap floor (0.028–0.047) and men, not women, are the
  higher-rate group — that note was wrong and is corrected here. The committed design is
  the **race arms of both tasks**: employment AL/OH/PA (p 0.410/0.461/0.467, gaps
  0.056–0.079, all HIGH calls) and coverage OH/PA/NY (p 0.333/0.306/0.401, gaps
  0.131–0.151, LOW/LOW/HIGH — and Non-White is the higher-rate group on coverage, the
  designed inversion). Six sweeps at seed-0-fixed thresholds, doc-54 rubric (scored−1 +
  beat constant 4/6, MIN_SCORED 4), the cross-task test of the shape boundary one rung
  below cross-instrument.

## Screened and refused, so nobody screens them twice

* **UCI diabetes readmission (130 hospitals, 102k rows), 23 Aug.** Band is excellent
  (0.135–0.948, span 0.813) but no attribute carries a workable gap: gender +0.018, race
  −0.034 (inverted), both under the 0.05 floor. A parity constraint has nothing to act on
  there. Third refusal species alongside band-too-narrow (LSAC, Taiwan) and
  below-noise-floor (the small states).

## Explicitly not doing

**Another derivation.** *Backfire*'s Theorem 3 is the mechanism and we cite it; document 26
tried the selection-rate version and lost to a constant. Three paragraphs say this well; a
fourth attempt duplicates published work.

**More ACS states for breadth.** They share one instrument, so they buy precision on a claim
whose weakness is not precision. They remain the right source for *held-out* populations.

---

## Traps in this repository, all of which have fired

Every one produced a plausible wrong answer without raising an error. They will recur.

* **Counts that are arm counts.** "19 populations" was 19 arms from 10; "26" was 26 from 15;
  "fourteen" was 14 from 4. Recompute from the results file; never quote a count from prose.
* **Replacements that silently no-op.** Assert `count(old) == 1` before every `.replace()`. A
  missing assert left a function defined and never called while the build reported success.
* **Missing denominators.** Arms predating the `n_test` column give NaN selection rates, and a
  NaN comparison reads as a verdict — once printing "DISJOINT: the routes disagree" when the
  truth was the opposite.
* **Path formatting.** `0.30` on a command line and the float `0.3` in an analyser gave `op030`
  and `op03`; three arms vanished from a verdict with no error.
* **`pgrep` by job name.** A `pdflatex` blocked on stdin ran for ten hours because every check
  searched for names of jobs I remembered starting. Search by *behaviour*: `sleep`, `until`,
  anything under the job directory.
* **Exclusion rules doing invisible work.** The parity bar at 0.05 concealed an entire regime;
  the accuracy bar withdrew two headline results. Sweep every threshold before trusting a
  correlation.
* **Refinements from in-sample data.** Document 46 was internally consistent, backed by a
  twenty-seed replication, and made out-of-sample prediction worse. Only a sealed test caught
  it.

---

## Blocked on the supervisor

- [ ] **Venue and page limit** — decides what survives from 51 documents. Paper is 15pp
      before the planned compression to ~9–10; FAccT or AIES would want ~10, IEEE ~8.
- [ ] **Is the empirical half a paper**, given *Backfire* exists? See `prof-meet/03-the-ask.pdf`.
      The position is strong: their conditions are unusable on data, their regime distinction
      holds 27/27, and the selection rate proxies their quantity at r = +0.935.
- [ ] **AI disclosure**, including whether commits should carry a trailer. None do.
- [ ] **Contacting the *Backfire* authors** — our results confirm their regime prediction,
      extend their framework, and bound its applicability; the uncomputability finding
      rests on an estimator choice they are best placed to challenge. Standard move is a
      collegial email after a preprint exists; supervisor first, their call on timing.
- [ ] **Is the course submission still open?** The report, deck and bundle were rebuilt because
      `docs/05` claimed originality for a decomposition Ferry et al. published first.
