# 35 — What to actually do about it

**Individual work, beyond the course submission.** **Derived, not measured.** No experiment
was run for this document and no prediction was registered. It assembles documents 19, 21,
23, 31, 32, 33 and 34 into a procedure someone could follow, and every number in it is
carried from those.

## Why this document exists

The project's finding is *check your selection rate*. On its own that changes no decision:
it tells a team what to look at and nothing about what to do with the answer. And until
document 32 the honest advice ended at "the crossover is population-specific, so measure it"
— which is not advice, because nothing said how.

## The procedure

### Step 0 — Does the rule apply to your constraint at all?

**Only if the criterion constrains selection rates.** Demographic parity and disparate impact
do. Equalized odds and equal opportunity do not: they equalise error rates within each
true-outcome stratum, and any movement in the pool is a side effect.

Under equalized odds the relationship is measurably weaker — r = +0.644 against parity's
+0.775 on identical arms — and the pool moves roughly **eight times less**
([document 33](33-the-rule-does-not-survive-equalized-odds.md)). If you are imposing an
error-rate criterion, expect little change in the number of favourable decisions, and do not
use the selection rate to predict its direction.

### Step 1 — What is your baseline selection rate?

The fraction of applicants your current, unconstrained model approves. Every deployed system
already knows this number; it costs nothing to look up.

### Step 2 — Where is *your* crossover?

**Do not use 0.25–0.60.** That is Alabama's. Oregon's is 0.35–0.65. Mortgage lending's is
0.64–0.77 ([document 31](31-the-crossover-on-natural-data.md)). The crossover is
population-specific, and quoting one population's as a constant is the mistake
[document 32](32-the-rate-not-the-task.md) rules out by evidence.

**Measure it on the model you already have:**

1. take your fitted model's scores on held-out data;
2. sweep its decision threshold to produce baselines at a range of selection rates spanning
   your operating point;
3. at each one, fit the constraint and record the change in the **total number of favourable
   decisions**, not the fairness metric;
4. the crossover is where that change turns from negative to positive.

**Check the spread before trusting the answer.** If the largest and smallest pie changes
differ by less than about two percentage points, you have not measured a crossover — you have
fitted a line to noise, which is precisely how Connecticut produces a confident-looking
r = −0.924 that means nothing. Document 33's E0 uses a 2.0-point bar for this and document
23's T1 should have.

This needs **no new data, no relabelling and no second population** — only *k* fits of a
constrained model on data you already hold.

**How far this is actually validated — read this before using it.** Document 32 tested this
route against the very different route of moving the label, on five ACS populations and on
mortgage data:

* the direction and the sign change reproduce in **four ACS populations of five**;
* the two routes agree on *where* the crossover sits in **three of five** (Alabama, Oregon,
  South Carolina). In **Kentucky they disagree** by one arm's width — 0.61–0.76 against
  0.26–0.61, with opposite signs on the arm at 0.61, both under 1%;
* in **Connecticut** there is nothing to find: every arm levels up and the spread is 0.34
  percentage points;
* on **pooled Mississippi and Louisiana lending data the route fails** — the relationship is
  not monotone (r = +0.633) and no single crossover can be bracketed.

**So this procedure is not validated on lending, which is the domain this project most wants
to speak to.** Use it on a rate-constraining criterion, expect it to work about four times in
five, and treat a result that shows no sign change as "your arms do not span the crossover"
rather than "there is no crossover".

### Step 3 — Act on where you sit

**Below your crossover** — expect the constraint to close the gap by **withdrawing**
favourable decisions. Add a floor on the overall selection rate alongside the parity
constraint. It is not a new method: a selection-rate floor is a linear moment constraint
inside Agarwal et al.'s own framework, and a variant of the minimum rate constraints
Mittelstadt, Wachter & Russell (2023) propose in their §6, which must be cited.

What it costs and returns ([documents 19](19-levelling-up-is-expressible.md) and
[21](21-the-floor-replicates.md)): about **0.12 accuracy points**; the exchange rate falls
from **1.47 to 0.88** favourable decisions destroyed per one created, across 19 populations
and both protected-attribute arms, landing below 1.0 in 16 of them. The benefit scales with
the damage at **r ≈ −0.99** — the worse the levelling down, the more the floor recovers — so
it is cheapest to skip exactly where it matters least.

**Above your crossover** — the constraint is likely to *extend* favourable decisions rather
than withdraw them, and the floor buys little. Measure anyway; do not assume.

### Step 4 — What this will not tell you

**The rate predicts which way, not how much.** Three independent manipulations each preserved
the direction and the crossover while changing the magnitude by three- to eight-fold:

| manipulation | direction | magnitude |
|---|---|---|
| route to the selection rate ([doc 32](32-the-rate-not-the-task.md)) | unchanged | 3× |
| constraint tolerance across 25× ([doc 34](34-the-crossover-survives-the-tolerance.md)) | unchanged | 4× |
| criterion, parity → equalized odds ([doc 33](33-the-rule-does-not-survive-equalized-odds.md)) | weaker | 8× |

So this procedure will tell you whether you are about to withdraw opportunities. It will not
tell you how many. Forecasting the size requires running your own constraint, which step 2
has you doing anyway.

## Two ways to get this wrong

**Trusting a threshold that wrecks the model.** The sweep in step 2 works by mis-calibrating
your classifier on purpose, and at the extremes that produces a model nobody would deploy —
on the lending data the arm at a selection rate of 0.350 came from a model approving 35% of
applicants where 72.5% are actually approved, at accuracy 0.594 against 0.838 at its best
threshold. That arm is what breaks monotonicity there. On ACS data such arms are filtered
automatically because their parity gap collapses; **on lending they are not**, because the
parity gap stays large. Discard any arm whose accuracy is far below your deployed model's,
and say how many you discarded.

**Trusting a small arm.** Below roughly 2,500 test subjects the method's own randomness
exceeds the entire effect of the constraint ([document 15](15-arbitrariness-at-small-scale.md)).
Test-set size is not sufficient on its own either: document 32's discarded arm had 6,681 test
subjects but only **206 baseline positives**, and its five seeds ran from +3.4% to +27.9%. If
the pool is small, the pie change is noise regardless of how large the sample is.

**Reading the fairness metric as an answer.** It reports the same success either way — that
is the frame this project inherited from Maheshwari et al. (2023) and Ferry et al. (2023),
not something it found. The whole procedure above exists because the certifying number does
not distinguish the two outcomes.

## The limits of the evidence behind this

Everything here rests on US data from 2018 across two instruments — the ACS and HMDA — one
label construction per instrument, and two protected attributes. The direction relationship
is replicated widely within that; the crossover *locations* are measured on four populations.
Nothing here has been tested outside the United States, outside 2018, or on a domain that is
neither income prediction nor mortgage lending.
