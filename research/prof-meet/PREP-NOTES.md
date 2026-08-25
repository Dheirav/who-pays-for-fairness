# Prep notes for the meeting

Private notes, not part of what the professor sees. Each question comes with the
answer and the reason behind the answer, because the reason is what survives a
follow-up question.

## A. Datasets: what and why

**Walk me through your datasets.** Eight sources, 67 populations. UCI Adult (45k
rows, 1994 census, predict income over $50k) is the standard benchmark where the
coursework began. ACS Income is Adult's modern replacement, available per US state,
which is the whole trick: forty-plus states means many populations that differ in
exactly the quantities the finding depends on. HMDA is real mortgage decisions from
eight state markets, the only source where a real institution made a real allocation.
COMPAS is criminal-justice risk, with the target inverted so y=1 is always the
favourable outcome. LSAC is bar passage, chosen because it is extremely generous (89%
pass). The Dutch census was chosen because its group gap is twice Adult's, which makes
it the test of the "big gaps drive everything" alternative. Taiwan credit is the
non-Western control. IPUMS Brazil and Mexico are the off-instrument cohort, requested
specifically because every ACS state shares one survey instrument and a finding that
lives in one instrument is not a finding about fairness.

**Why so many datasets?** Because the claim is that the direction depends on the
population. One dataset cannot show a crossover between populations; you need
populations sitting on both sides of it.

**Population versus arm.** A population is a disjoint set of people. An arm is one
population under one configuration (a threshold, a label cutoff). I count
populations, never arms, because three times an arm count masqueraded as a population
count in my own history, and an automated guard now recomputes the number from disk.

## B. Methodology: what I actually ran

**The model.** L2-regularised logistic regression on one-hot categoricals plus
standardized numerics. A boosted-tree section shows the finding is not model-specific.
70/30 split stratified on group and label, re-drawn per seed, five seeds per arm.
Every quoted number is a seed mean, because on small data the method's own randomness
exceeds the constraint's whole effect.

**The mitigation.** Fairlearn's ExponentiatedGradient (the Agarwal 2018 reductions
approach) with a demographic-parity constraint at epsilon 0.01, the library default,
which bounds training-time violation. It returns a randomized mixture of classifiers,
which is what makes the lottery finding possible. Five other methods on Adult confirm
the pool-shrink is not one method's quirk.

**What a sweep is, and the two routes.** To test whether the approval rate drives the
direction you must vary the rate. The label route moves the income cutoff, which also
changes how rare the label is. The operating-point route keeps the label and moves the
model's decision threshold, which also degrades the classifier. The two confounds are
disjoint, so where both routes give the same answer, the shared variable (the rate) is
what is operative. They agree mid-range and diverge below rate 0.10, which is now an
advisory zone in the audit.

**The guards, and why those values.** An arm is dropped if the baseline group gap is
under 0.05 (nothing to mitigate), if accuracy is below max(p, 1-p) (worse than
predicting the majority; such arms once produced two headline results I had to
withdraw), if the test split is under 2,500 people (seed noise dominates), and effects
under 1.0 point are never sign-scored (an arm at -0.04% flips sign across seeds, which
cost the re-seal its one miss). Honest answer to "why 0.05": it was tuned during the
exploratory phase, which the paper discloses, but it has been frozen in every seal
since, and a sensitivity table shows where it matters and where it does not.

## C. The five quantities to be fluent in

Selection rate: fraction of the test split the model marks favourable. Pool change:
percent change in total favourable decisions after mitigation, the number the fairness
metric hides. Crossover: the rate where the pool change flips sign, reported as a
bracket. Exchange rate: approvals destroyed per approval created (2.68 on Adult; the
one-line floor drops it to 0.88). Who-pays split: by rates the burden looks even, by
people 66-74% of changed decisions are withdrawals, because the advantaged group is
bigger.

## D. The sealed methodology (my strongest card)

**What sealed means.** The rule, the population list, the pass mark, and the naive
baseline it must beat are committed to git before the data exists or the runs happen.
Post-hoc analysis is allowed but labeled. Sixteen such tests stand; ten failed or were
refused, all published. Recent seals are also timestamped into the Bitcoin blockchain,
so the ordering does not depend on trusting my clock.

**Why 9-of-10 is not luck, honestly ordered.** Against an independent guesser at the
best constant's skill, about 1 in 20. Paired against the constant on the same ten
arms, it reduces to five disagreements of which the rule won four, about 1 in 5, and
the paper prints "suggestive, not significant". The real convincer is different: the
refined rule looked equally convincing in-sample, got the same sealed test, and failed
4 of 8. Sealing distinguishes what post-hoc analysis cannot.

**The rate-versus-cutoff worry, resolved.** The 9-of-10 arms all reached their rates
through income cutoffs, so a cutoff-reading rule would have scored identically, which
the abstract admits. This week's screen-gated test on Brazil's race arms held cutoff
rarity constant on the operating-point arms: the cutoff reading scored 5 of 10, the
rate scored 8. It is the rate. The 0.54 value itself earned no special status, which
matches the standing advice: measure your own crossover.

## E. The findings, one breath each

1. Direction is predictable, size is not: a sealed size model lost to predicting
   zero, so the paper claims direction only.
2. The boundary is the method family, not blindness: my own earlier claim, overturned
   by my own sealed test after a reviewer caught that my evidence changed two things
   at once. Aware in-processing keeps the relationship (r = +0.672); only
   post-processing kills it.
3. The lottery: at severe operating points the mixture keeps everyone above the line
   with one flat probability, so a person's own score stops mattering. Verified inside
   the fitted models, absent at all nine natural points probed, no same-kind
   alternative exists where it appears, and the deterministic version a bank would
   deploy preserves the direction 10 of 10. The charge is that it is unannounced.
4. Quantile anchoring: the 2022 inversion was the $50k label sliding down the income
   distribution, inflation-fixing is not enough because real incomes grew past it,
   so anchor outcome definitions to a quantile.
5. The theory relationship: their conditions unevaluable under two estimators, my
   rate tracks their quantity at 0.85 across 150 populations, their group-level
   theorem confirmed in all 45 aware populations, and their regime boundary
   corrected by my sealed test.

## F. Gotcha questions, with the honest answers

**Why unweighted survey data?** Inherited from the folktables benchmark, declared in
the setup, and stress-tested: design weights shift crossover locations by 0.03-0.08
but the ordering and the outliers hold, and the audit itself needs no weights because
a deployer's own applicant pool is the population of interest.

**Some correlations sit on 4-5 arms.** Labeled descriptive where they do. The
load-bearing evidence is sign patterns and sealed calls, not those r values, and the
domain table was shown to be invariant to the exclusion floor.

**Why logistic regression and not deep models?** The claim is about the constraint's
behaviour, not the learner's. A boosted tree reproduces it, and simple learners make
the internal probes (mixture members, the theory quantity) possible.

**What would falsify this?** A powered sealed cohort where in-band directions do not
follow rates. That is exactly the test I keep running; one sub-claim (the shape
boundary) was falsified this way, 0 for 4, and it is published as such.

**Where does it not apply?** Post-processing, equalized-odds constraints,
fixed-capacity allocation (a set number of seats or beds, where the pool cannot
change), gaps under 0.05, non-monotone landscapes (a third of the biggest states),
and healthcare, which was never measured; the one public clinical dataset screened
was refused by my own gates.

**Is this not just the Backfire paper?** The table on the ask page. Out loud: they
proved the answer exists, I built the instrument that reads it, and my sealed test
corrected where their boundary sits. Their own group-level prediction held everywhere
I looked, so the work strengthens them while standing on its own.

**What did you get wrong?** Lead with it. Two withdrawn headline correlations (arms
worse than doing nothing), a failed refinement (4 of 8), a failed derivation (beaten
by a constant), a failed size model, the regime misreading a reviewer caught, and a
21-to-1 exchange figure I once quoted outside its population before my own
no-transfer rule stopped me. Each has a numbered document.

**Why subsample Brazil to 60k rows?** The noise floor is 2,500 test rows and the
record's own populations run 10k-130k, so scale bought runtime, not power. The rule
was fixed and committed before any outcome existed, and the label quantiles still
come from the full samples.

## G. The three sentences to have ready

If asked for the finding: "Within a population, the baseline approval rate against
that population's own crossover predicts whether a parity constraint gives or takes,
and the fairness metric cannot tell the difference on its own."

If asked about the theory: "They proved the answer exists; I built the instrument
that reads it, and along the way corrected where their boundary sits."

If asked why to trust it: "Sixteen predictions were registered before the data
existed, ten failed, and every failure is published; the method that kept producing
results I did not want is the reason to believe the ones that survived."
