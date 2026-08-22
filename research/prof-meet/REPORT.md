# The project, complete — 22 August 2026

This is the whole project in a few pages, written so it can be read instead of the paper.
The paper (10 pages, IEEE format) exists and is current; everything here points at a result
that is committed in the repository, and every number below is re-derived from stored
results by an automated check before it is allowed to appear in a document.

## The question, and why it matters

A fairness constraint asks a model to give two groups similar approval rates, but it does
not say how the gap should close. It can close because more people from the disadvantaged
group are approved, or because people from the advantaged group lose approvals they would
have had. Both count as success, and the fairness metric — the number a company would report
and a regulator would check — comes out the same in both cases. This means a team imposing a
constraint cannot tell, from its own dashboard, whether it is about to extend opportunities
or withdraw them.

The literature already knew the metric was silent about this. What it did not have is a way
to know **in advance** which of the two outcomes a given system will produce. That is what
this project measured, and the answer turns out to be readable from one number every
deployed system already has: the rate at which its current model says yes.

## The finding

Below a crossover in the baseline approval rate — empirically near 0.54 — an
attribute-blind parity constraint shrinks the total pool of favourable decisions, while
above it the same constraint grows the pool. On UCI Adult (rate 0.24), six different
mitigation methods all shrink the pool, by 7.9% to 22.1%. On mortgage approvals (rate
0.81), the identical constraint grows it by 4.3%. The parity metric reports success
identically in both cases, which is exactly the problem: the direction is invisible to the
certificate but predictable from the rate.

The claim is deliberately narrow, and each boundary is measured rather than assumed. It
holds within a population, in the attribute-blind in-processing regime, and it predicts the
direction only — magnitude is ordered within a population (Spearman rho up to +0.96) but
does not transfer across populations, where a pooled slope reaches only +0.487 against a
pre-registered bar of +0.70 and therefore fails.

## Why the evidence is stronger than a correlation

Every correlation in the project was computed after the arms were run, which is the weakest
support for a claim of the form "you can know in advance". So the rule was tested the only
way that format can be tested: **sealed predictions, committed to git before the data
existed.**

The first sealed test failed, and the failure was informative. A refinement added from four
in-sample populations two hours before the seal turned what would have been 7 of 8 into
**4 of 8**, no better than a constant. The refinement was withdrawn, and the simple rule —
down below 0.54, up at or above — was re-sealed against ten states the project had never
touched, with the bar (at least 9 of 10, and strictly beating the best constant) committed
before any run.

**It scored 9 of 10, against a best constant of 6.** The one miss is charged against the
rule under the criterion sealed with it, and it is an instructive miss: an arm whose true
effect is around −0.04% and flips sign between random seeds, which means there may have
been no direction there to predict.

The complete ledger of registered tests is below, and one thing matters for reading it:
these are not seven attempts at one claim, of which two succeeded. Each test targeted a
**different** claim, and each failure removed a claim *stronger* than the one that
survives — so the failures are boundary measurements, and the passes test the claim as
those boundaries define it. Averaging the rows into "2 out of 7" would be reading a map as
a scorecard.

| Test | Outcome | What it settled |
|---|---|---|
| HMDA held-out sweep | 2 of 4 — fail | our measuring procedure is unreliable on mortgage data, so no claim rests on it there |
| Equalized-odds transfer | +0.334 vs +0.70 — fail | the rule works for parity, which controls approval rates directly; it failed for equalized odds, which does not |
| Post-processing transfer | r = −0.024 — fail | the rule stops working the moment the model may read the protected attribute — and that turned out to be the boundary the theory predicts |
| Selection-rate derivation | beaten by a constant — fail | we cannot explain **why** the rule works; the paper claims only that it does |
| Sealed rule, refined | 4 of 8 — fail | the extra clause we had added from early data was wrong, and is withdrawn |
| Attribute-aware replication | 9 of 9 — **holds** | where the attribute is readable, the disadvantaged group always gains — as the theory says, predicted in advance |
| Re-seal, unrefined rule | 9 of 10, constant 6 — **holds** | the simple rule predicts populations it has never seen, from the approval rate alone |

Five failures are reported uncorrected, which removes the usual way lucky results reach
print: selective reporting. And the passes are unlikely to be luck on their own terms — 9
of 10 against a guesser as good as the best constant happens about one time in twenty by
chance, the arms were deliberately spread so no constant strategy could score well, and
the refined rule, which looked equally convincing in-sample, was given the same sealed
test and failed it.

## The relationship to the 2026 theory paper

*Fairness May Backfire* (arXiv:2603.06901) proves that in the attribute-blind regime the
direction is distribution-dependent, so the conditionality itself is theirs and the paper
says so. What they do not have is any way to compute the direction: their conditions are
stated over a quantity that diverges on real data, and on 26 real arms from 15 populations
they can be evaluated on none. Their paper contains no experiments and no occurrence of
"selection rate" or "base rate", which was checked against the full text.

The project's position relative to them is two-sided, and both sides are measured. Their
regime distinction is right: under attribute-aware post-processing the selection-rate
relationship vanishes entirely (r = −0.024 against +0.585 on the same populations), and
their prediction for that regime — the disadvantaged group always gains — holds on **27 of
27 populations, nine of them pre-registered**. And their structural quantity is tracked by
the plain selection rate at r = +0.935, which means the number this project uses is a
computable proxy for the quantity their theorem is stated over. They proved the question
has an answer; this project built the instrument that reads it.

## Who actually pays, which the metric also hides

Measured in rates, the burden of a fairness fix looks nearly even. Measured in people it is
not: on Adult, between 66% and 74% of the individuals whose decision changed were
advantaged-group members losing an approval, at 2.68 approvals destroyed per one created.
Adding a one-line floor to the objective — "do not shrink the pool" — drops that exchange
rate to 0.88 across nineteen arms at a cost of about 0.12 accuracy points, so the harm is
optional once you know to ask for it. Knowing when to ask is what the crossover rule is for.

## Scale, and the discipline behind the numbers

As of this afternoon the record holds **39 independent populations** across seven data
sources (UCI Adult, ACS states, HMDA mortgages, COMPAS, LSAC, the Dutch census, Taiwanese
credit-card default), six decision domains, three countries and two decades. A
pre-registered sweep of ten further states is running tonight, which takes it to 47 and
tests — with predictions committed this afternoon, before any of those arms existed —
whether anything measurable predicts where a population's crossover sits.

Three pieces of discipline are worth naming because they caught real errors:

* **55 automated checks** re-derive every documented figure from stored results; one of
  them caught the paper's population count going stale within minutes of new results
  landing today.
* **Population counts are recomputed, never quoted** — three counts in the project's own
  history turned out to be arm counts masquerading as population counts, and the paper now
  carries a table saying exactly which populations enter which analysis.
* **Anything that could go either way is sealed first.** The standing rule commits
  predictions, thresholds and the naive baseline to beat before the run; re-analysis of
  existing results is labelled post-hoc every time it appears.

## What is open, honestly

* **Why 0.54.** The crossover clusters (0.43–0.58 carrying bootstrap intervals) but nothing
  explains its location; the one derivation attempt cleared its pre-registered bars and was
  then beaten by a constant, and that failure is reported. Tonight's sealed sweep is the
  first adequately powered test of the two candidate predictors.
* **Breadth.** The sealed 9-of-10 is ten US census populations — depth, not breadth. A
  non-Western census extract (Brazil 2000/2010, Mexico 2015/2020) is requested and pending
  approval, which would allow the first crossover located outside the West.
* **Mechanism.** At extreme operating points the constraint closes the gap by two
  qualitatively different solutions — lifting the disadvantaged versus discarding
  approvals — and what selects between them is measured to be none of six candidate
  quantities. The paper states this as an open boundary rather than papering over it.

## What I am asking

1. **Venue and page limit.** The paper is 10 pages in IEEE conference format; FAccT or
   AIES would want roughly 10, IEEE conferences 8. This decides what gets cut.
2. **Does the empirical half stand as a paper, given the theory paper exists?** My
   position: their theorem is uncomputable on data and this project supplies the
   measurement, the boundary verification and a sealed predictive rule — but this is the
   call I need from you.
3. **AI disclosure.** How the department wants assistance disclosed, including whether
   commits should carry a trailer; none currently do.
4. **Whether the course submission window is still open** for the rebuilt report and deck.
