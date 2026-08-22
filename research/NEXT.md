# What to do next, and what will bite you

Live handover. Read this first, then `research/README.md` for the document index. Documents
11–50 are the research record; the paper is `research/paper/ieee/paper.tex`. The checklist this
replaced, with the original reasoning behind each completed item, is in
[`NEXT-archive.md`](NEXT-archive.md), including the two items completed on 22 Aug (the
re-seal, and the route-divergence mechanism).

**Standing rule.** Anything whose outcome could go either way gets its predictions, its
numerical thresholds **and the naive baseline it must beat** committed to git *before* the run.
Re-analysis of existing results is labelled post-hoc. Both are fine; mislabelling is not. The
rule exists because a derivation of ours cleared every stated bar and was then beaten by a
constant (document 26). After document 49: a seal that predicts *signs* must also pre-state a
minimum-magnitude guard, because its one miss was an arm whose true effect is
indistinguishable from zero — a sign prediction has nothing to grip there, and discovering
that after the run cannot excuse the miss.

---

## Where the work stands

* **47 independent populations**, 6 domains, 7 data sources, 3 countries, 2 decades. ("5
  instruments" was stale once Taiwan and Adult were counted; the paper now says 7 sources.)
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
* **The paper** is 8 pages, IEEE format, builds from `research/paper/ieee/build.sh`.
  `research/paper/draft-v2.md` is **superseded** — do not edit it; the pack copies the typeset
  PDF.
* **55 automated checks** across five suites re-derive every load-bearing figure from stored
  results. Run all five before trusting anything:
  `for m in test_documented_claims test_output_isolation test_incidence test_acs_threshold test_new_instruments; do .venv/bin/python -m tests.$m; done`

### Five results to know before touching anything

1. **The first sealed prediction failed; the re-seal of the simpler rule holds** (documents
   47, 49). Doc 47: predictions committed first scored **4 of 8, not beating a constant**,
   because they carried a refinement added two hours earlier from four in-sample populations;
   document 46 is withdrawn in place because of it. Doc 49: the pre-refinement rule — *down
   below 0.54, up above* — re-sealed against ten never-measured states scored **9 of 10, bar
   9, constant 6**. The one miss (MN, 0.699) is flagged by the sealed criterion as against
   the rule, not a boundary call; its effect is seed-noise around zero, noted post-hoc.
2. **The rule is regime-bound** (documents 43, 47). Under post-processing it vanishes
   (r = −0.024 against +0.585). That is the theory's regime boundary rather than fragility, and
   the attribute-aware prediction holds **27 of 27**, nine pre-registered.
3. **The theory is silent, not refuted** (document 27). *Backfire*'s conditions are stated over
   extrema of a quantity that diverges on real data, and they are *sufficient, not necessary*.
   A relaxed form tracks the direction on 24 of 26. **Never write "0 of 26" as though datasets
   had been tested and failed.**
4. **The two routes agree in the middle and diverge at the bottom** (documents 32, 47). Below
   a selection rate of ~0.10 the operating-point route and the label route give opposite signs,
   and the accuracy rule does not separate them.

---

## Open, in the order I would do them

- [ ] **What separates the states that level up below 0.54?** New top question (document
      52). TX, FL, NJ, VA, MA level up at natural rates 0.29–0.52 where every earlier
      population levelled down; several show U-shaped sweeps with no crossover at all. The
      misses are internally consistent (FL turns up at 0.288 and its located crossover is
      0.284), so something population-level is real here.
      **A post-hoc shape screen (23 Aug, scratch `shapes.py`) found the candidate:** within
      ACS, base rate orders the shape class — p ≤ 0.36 gives monotone/all-negative (8/8),
      p 0.37–0.47 gives U-shapes, p ≥ 0.44 gives all-positive, with slight interleaving —
      and the sharper form is (natural rate − p), the reservoir headroom: monotone states
      run far below their base rate, U/all-positive states at or above it, which ties the
      shape to docs 50/51's lift mechanism. Cross-instrument it fails (COMPAS is monotone
      at p = 0.53), consistent with everything else here. **The sealable test is IPUMS:**
      Brazil/Mexico base rates are computable before any sweep, so commit shape
      predictions (thresholds fitted on ACS only) before the first non-Western arm runs.
      The 9 unused ACS states are below the noise floor and cannot serve.
- [ ] **The crossover residual — still open, and harder** (document 52). The sealed test
      returned UNDERPOWERED (3 new locations against a minimum of 6) because locating a
      crossover assumes a monotone landscape and a third of the large states do not have
      one. A future design must handle U-shapes and levels-up-everywhere before it can ask
      what predicts the location; located values now span 0.28–0.65.
- [ ] **A novelty audit for the lottery finding.** Document 30's sweep predates document
      51, so "the cut is a lottery" has never been checked against the literature the way
      the core claims were. Before the paper leans on it as a contribution: a targeted
      pass over randomized-fair-classifier and mixture-degeneracy vocabulary. An evening.
- [ ] **The lift-or-cut selector** (document 50's open remainder, now harder). Six candidates
      are dead: rate, gap-to-rate, reservoir, accuracy clearance, threshold height, and — per
      the same-day addendum — both simple geometry forms (depth-to-equalise and
      mass-near-the-line fail on all nine deep-tail arms; `--probe-geometry` recomputes
      them). The selector is not in the baseline score distribution's summaries. Last cheap
      step: refit ExpGrad on one lift arm (OR@0.87) and one cut arm (Dutch@0.965) and diff
      the mitigated models' per-person scores against baseline by group — look at what the
      optimiser's tilt actually did. Past that, it is a theory question.
- [ ] **A *sweepable* non-Western population.** Taiwan is non-Western but the viable-band test
      refused it, as it did LSAC. One that can be swept would be the first crossover located
      outside the West.
- [ ] **The crossover residual.** Two candidate predictors are collinear at +0.947 and neither
      survives four populations (document 44). Needs ~15 populations with located crossovers;
      there are 4.
- [ ] **Magnitude.** Ordered within a population (ρ up to +0.96), no pooled slope (+0.487,
      failed). A better model is possible; the current concession is honest without one.

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

- [ ] **Venue and page limit** — decides what survives from 37 documents. Paper is 8pp; FAccT
      or AIES would want ~10.
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
