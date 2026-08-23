# The project, complete — 25 August 2026

This is the whole project in a few pages, written so it can be read instead of the paper.
The paper (15 pages, IEEE format, before the planned compression pass that waits on your
page-limit answer) exists and is current; everything here points at a result that is
committed in the repository, and every number below is re-derived from stored results by
an automated check before it is allowed to appear in a document. Since the previous
version of this report: the paper has been through three adversarial review panels
(twenty-four independent reviews in total, no reject verdicts), every cheap fix they
converged on is applied, and an apparent 2022 anomaly has been traced to its mechanism
and resolved.

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
| Attribute-aware consistency | 9 of 9 — **holds** | where the attribute is readable, the disadvantaged group always gains; a consistency check with the theorem, which had already made this outcome near-certain — counted as confirmation, not as forecasting skill |
| Re-seal, unrefined rule | 9 of 10, constant 6 — **holds** | the simple rule predicts populations it has never seen, from the approval rate alone |
| Crossover-residual test | 3 located vs floor 6 — underpowered | what predicts the switch point's *location* stays unjudged; a third of large states have no switch point to locate |
| Sealed magnitude model | MAE 4.50 vs 0.77 — fail | the effect's *size* cannot be predicted from what we tried; the direction-only concession is earned |
| Sealed shape boundary | 4 of 6 — fail | the base-rate boundary called every 2014 shape and both predicted flips; the 2022 curves misbehaved for a reason found later (below) |
| Sealed attribute-independence | 2 of 6 — fail | a population's curve shape is not a property of its label alone; the race arms behave differently from the sex arms |

Eight of the eleven rows are failures or refusals, reported uncorrected, which removes
the usual way lucky results reach print: selective reporting. The passes carry their own
health warnings, stated in the paper where the claims are made. The one-in-twenty chance
figure for the 9 of 10 is against an independent guesser; the stricter paired comparison
— did the rule beat the best constant on the same ten arms — comes down to the five calls
they disagree on, of which the rule wins four, about one in five by chance. And the
sealed cohort has a design confound the paper states next to the score: every arm reaches
its approval rate through the income cutoff, so a rule reading only the cutoff would
score identically there. The experiment that separates them is designed, committed, and
waiting on data (the census extract below).

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

## A 2022 anomaly, diagnosed to its mechanism and resolved

Four 2022 state-years initially appeared to *invert* the relationship — the opposite
pattern to every earlier vintage — and for two days that stood as the project's most
worrying open item. Three candidate mechanisms were then run to ground. Pandemic-era
survey weighting: exculpated (applying the Census Bureau's person weights moves 2022's
rates and gaps no more than 2018's). A recoded survey column: acquitted (2019 files carry
the recode and behave classically). The third candidate is confirmed as the substantial
cause: the $50,000 income label, fixed in nominal terms, had slid down an
inflation-compressed earnings distribution — the task had changed under the label.
Re-measured at $60,000, the 2022 real-equivalent of 2018's $50,000, Ohio returns to a
clean crossing at its old location and the inverted patterns disappear. Measured at
constant real value there is no detected change in the phenomenon from 2014 through 2022.
The practical lesson made it into the paper's abstract: a fixed nominal outcome
definition is a different task each year, so labels should be anchored in real terms and
teams should audit their own current data.

## Three rounds of adversarial review, and what they changed

The paper was put through three review panels of independent reviewers with instructions
to be harsh: six, then eight, then ten reviewers, the last round spanning lenses from a
bank examiner and an EU regulator to a hostile senior skeptic told to argue the work is
trivial. Twenty-four reviews, no reject verdicts; the skeptic conceded the
trivial-arithmetic reading fails (an effect that vanishes under post-processing cannot be
rate arithmetic). Every converged fix is applied. The ones that produced new results:

* **The audit's own totals.** Run over all 45 swept population-label pairs, the
  procedure returns a usable direction on 27 (never contradicting what the constraint
  actually did), declares no-crossover on 6, and refuses on the rest — it answers six
  times in ten, with the refusals counted rather than hidden.
* **The "lottery" is bounded.** The earlier finding that a constraint can close the gap
  by discarding approvals at random, under an unchanged certificate, was probed at
  normal operating points as a control: it does not appear there in any of seven
  populations. It is a severe-operating-point phenomenon — a checkable red flag, not
  the ordinary cost of fairness.
* **The deployable form preserves the verdict.** A regulated lender cannot deploy a
  randomized model, so the deterministic extraction was tested directly: it agrees with
  the randomized version's direction on 10 of 10 populations, with the fairness repair
  intact. The examiner's objection is answered with data.
* **The seeds tell the miss's story.** 16 of the 19 sealed arms are unanimous across
  random seeds; the three that split are exactly the near-zero effects — and the one
  sealed miss (Minnesota, −0.04%) splits 3-of-5 *identically* to an arm that scored
  correct (+0.04%). The audit now refuses such arms as indeterminate instead of scoring
  them.
* **Verifiability.** All eleven registered tests now have their registration and scoring
  commits pinned in the paper (each ordering re-verified), a checksum manifest pins the
  exact input files, and the paper states plainly that the chronology currently rests on
  our own clock — the next sealed test will be anchored with an external timestamp.

## Scale, and the discipline behind the numbers

The record holds **57 independent populations** across seven data sources (UCI Adult, ACS
states, HMDA mortgages, COMPAS, LSAC, the Dutch census, Taiwanese credit-card default),
six decision domains, three countries and two decades. The later campaigns mostly went
against us, in instructive ways: the test of what predicts the crossover's location
returned **underpowered** (three located against a floor of six), a sealed model of the
effect's *size* lost outright to predicting zero, and the three crossovers that did locate
**broke the cluster** — Florida at 0.284 and Pennsylvania at 0.652, far outside the
0.43–0.58 band, on the same instrument that built it. Several of the largest states turn
out to have no crossover at all, and the fixed 0.54 prior scores 5 of 10 on their natural
arms, each miss agreeing with that state's own measured crossover. So the
within-population claim survived the campaign's hardest tests, while the transferable
prior narrowed to "usually, not always" — and every one of those sentences comes from a
prediction committed before the data existed.

Three pieces of discipline are worth naming because they caught real errors:

* **55 automated checks** re-derive every documented figure from stored results; one of
  them caught the paper's population count going stale within minutes of new results
  landing, more than once.
* **Population counts are recomputed, never quoted** — three counts in the project's own
  history turned out to be arm counts masquerading as population counts, and the paper now
  carries a table saying exactly which populations enter which analysis.
* **Anything that could go either way is sealed first.** The standing rule commits
  predictions, thresholds and the naive baseline to beat before the run; re-analysis of
  existing results is labelled post-hoc every time it appears.

## What is open, honestly

* **Why the crossover sits where it sits.** Located values now span 0.28–0.65 and nothing
  predicts the location; the sealed test built to answer this returned underpowered, partly
  because a third of the large states have no crossover to locate — their response to the
  constraint is U-shaped or positive throughout, which is itself the newest open question.
* **Breadth.** The sealed 9-of-10 is ten US census populations — depth, not breadth. A
  non-Western census extract (Brazil 2000/2010, Mexico 2015/2020) is requested and pending
  approval, which would allow the first crossover located outside the West -- and it
  carries the one experiment the reviews agree matters most: the sealed cohort that
  separates the approval rate from the income cutoff, its design already committed.
* **Mechanism.** At extreme operating points the constraint closes the gap by two
  qualitatively different solutions — lifting the disadvantaged versus discarding
  approvals — and what selects between them is measured to be none of six candidate
  quantities. The paper states this as an open boundary rather than papering over it.

## What I am asking

1. **Venue and page limit.** The paper is 15 pages in IEEE conference format after the
   review rounds' additions; a compression pass with its cut list already written brings
   it to roughly 9-10 without losing any number, and your venue answer (FAccT/AIES ~10,
   IEEE conferences ~8) decides how deep it goes.
2. **Does the empirical half stand as a paper, given the theory paper exists?** My
   position: their theorem is uncomputable on data and this project supplies the
   measurement, the boundary verification and a sealed predictive rule — but this is the
   call I need from you.
3. **AI disclosure.** How the department wants assistance disclosed, including whether
   commits should carry a trailer; none currently do.
4. **Whether the course submission window is still open** for the rebuilt report and deck.
5. **Contacting the theory paper's authors.** Our results confirm their regime prediction
   (27 of 27, nine pre-registered), extend their framework with a computable proxy for its
   central quantity, and show its stated conditions cannot be evaluated on real data — the
   last of which rests on an estimator choice they would be the best people to challenge
   before a reviewer does. Standard practice would be a short collegial email, ideally
   after a preprint exists; I would like your read on whether and when, and whether you
   want to be on it.
