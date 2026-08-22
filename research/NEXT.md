# What to do next, and what will bite you

Live handover. Read this first, then `research/README.md` for the document index. Documents
11–47 are the research record; the paper is `research/paper/ieee/paper.tex`. The checklist this
replaced, with the original reasoning behind each completed item, is in
[`NEXT-archive.md`](NEXT-archive.md).

**Standing rule.** Anything whose outcome could go either way gets its predictions, its
numerical thresholds **and the naive baseline it must beat** committed to git *before* the run.
Re-analysis of existing results is labelled post-hoc. Both are fine; mislabelling is not. The
rule exists because a derivation of ours cleared every stated bar and was then beaten by a
constant (document 26).

---

## Where the work stands

* **27 independent populations**, 6 domains, 5 instruments, 3 countries, 2 decades.
* **The claim, in full:** within a population, in the **attribute-blind in-processing** regime,
  between roughly 0.10 and the crossover, the baseline selection rate predicts *which way* a
  parity constraint moves the pool of favourable decisions, and orders *how much*. Neither
  transfers between populations. The crossover is ~0.54 as a **prior for auditing, not a
  constant**.
* **The paper** is 8 pages, IEEE format, builds from `research/paper/ieee/build.sh`.
  `research/paper/draft-v2.md` is **superseded** — do not edit it; the pack copies the typeset
  PDF.
* **55 automated checks** across five suites re-derive every load-bearing figure from stored
  results. Run all five before trusting anything:
  `for m in test_documented_claims test_output_isolation test_incidence test_acs_threshold test_new_instruments; do .venv/bin/python -m tests.$m; done`

### Four results to know before touching anything

1. **The sealed prediction failed** (document 47). Nine populations, predictions committed
   first: **4 of 8, not beating a constant**. What broke it was a refinement added two hours
   earlier from four in-sample populations — carrying it turned a 7-of-8 prediction into
   4-of-8. Document 46 is withdrawn in place because of it.
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

- [ ] **Re-seal the simpler rule.** The 7-of-8 in document 47 is post-hoc. Sealing *down below
      0.54, up above* on fresh populations would convert this project's weakest evidence into
      its strongest. **Highest value on the list.** ~2 hours. Populations must never have been
      measured; 38 unused ACS states and several HMDA arms are available.
- [ ] **Explain the route divergence below 0.10.** Currently a described fact with a conjecture
      attached. Whatever explains it probably also explains why the accuracy rule fails to
      catch it — a real gap in the procedure document 35 recommends.
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
- [ ] **Is the course submission still open?** The report, deck and bundle were rebuilt because
      `docs/05` claimed originality for a decomposition Ferry et al. published first.
