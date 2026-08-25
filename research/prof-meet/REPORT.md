# The project, complete - 25 August 2026

This is the whole project in a few pages, written so it can be read instead of the
paper. The paper (17 pages, IEEE format, with a written compression plan to about 10
pages that waits on your venue answer) exists and is current. Everything here points at
a result committed in the repository, and every number below is re-derived from stored
results by an automated check before it is allowed to appear in a document.

Since the previous version of this report: the paper absorbed two further review
rounds (five rounds and 37 independent reviews in total, no reject verdicts), a sealed
test overturned our own explanation of where the finding's boundary lies, two more
sealed campaigns ran to verdicts that went against us and were recorded uncorrected,
and the record grew to 67 populations across 8 data sources and 5 countries.

## The question, and why it matters

A fairness constraint asks a model to give two groups similar approval rates, but it
does not say how the gap should close. It can close because more people from the
disadvantaged group are approved, or because people from the advantaged group lose
approvals they would have had. Both count as success, and the fairness metric, the
number a company would report and a regulator would check, comes out the same in both
cases. A team imposing a constraint cannot tell, from its own dashboard, whether it is
about to extend opportunities or withdraw them.

The literature knew the metric was silent about this. What it did not have is a way to
know in advance which of the two outcomes a given system will produce. That is what
this project measured. The answer is readable from one number every deployed system
already has: the rate at which its current model says yes.

## The finding, stated at the strength the evidence supports

Within a population, under in-processing mitigation, the baseline approval rate read
against that population's own crossover predicts whether the constraint will grow or
shrink the pool of favourable decisions. Measured on your own data through the audit
procedure, this holds everywhere the audit returns an answer (27 of 27 consistency
checks). As a transported shortcut, "below about 0.54 the fix takes, above it gives"
works often but not always: sealed at 9 of 10 on never-measured states, 5 of 10
post-hoc on larger states, and the strongest sealed evidence cannot yet separate the
approval rate from the income cutoff that produced it. The experiment designed to
separate them is running as this report is written (see the final section). The claim
covers direction only. Size does not transfer, and a sealed model of size lost to
predicting zero.

## Who pays, which the metric also hides

Measured in rates, the burden of a fairness fix looks nearly even. Measured in people
it is not: on Adult, between 66% and 74% of the individuals whose decision changed were
advantaged-group members losing an approval, at 2.68 approvals destroyed per one
created. A one-line floor in the training objective drops that exchange rate to 0.88
across nineteen arms for about 0.12 accuracy points. The harm is optional once you know
to ask; knowing when to ask is what the crossover rule is for.

## The complete ledger of registered tests

Every prediction was registered with its thresholds and the naive alternative it had to
beat, before the data existed. Sixteen registered tests now stand; ten failed or were
refused, and every failure is reported uncorrected. Read each row by what it settled,
not as attempts at one claim.

| Test | Outcome | What it settled |
|---|---|---|
| HMDA held-out sweep | 2 of 4, fail | the sweep procedure is unreliable on mortgage data |
| Equalized-odds transfer | +0.334 vs +0.70, fail | the rule is about criteria that control approval rates |
| Post-processing transfer | r = -0.024, fail | the rule vanishes under post-processing |
| Selection-rate derivation | beaten by a constant, fail | we cannot explain why the rule works, only that it does |
| Sealed rule, refined | 4 of 8, fail | the clause added from early data was wrong, and is withdrawn |
| Attribute-aware consistency | 9 of 9, holds | a consistency check with the theorem, whose prior was near one; not forecasting skill |
| Re-seal, unrefined rule | 9 of 10, constant 6, holds | the simple rule predicts unseen states from the rate alone, with the confound below |
| Crossover-residual test | 3 located vs floor 6, underpowered | what predicts the switch point's location stays unjudged |
| Sealed magnitude model | MAE 4.50 vs 0.77, fail | size cannot be predicted from what we tried |
| Sealed shape boundary | 4 of 6, fail | the 2022 curves inverted; later traced to the label's sliding quantile |
| Sealed attribute-independence | 2 of 6, fail | curve shape is not a property of the label alone |
| Sealed cross-task shape | 0 of 4, fail | the shape boundary belongs to the income question; every call inverted, unexplained |
| Regime deconfounding | two sealed readings; r = +0.672, method reading | the boundary is the optimizer family, not attribute access; see below |
| Six-market lending seal | M2 2 of 6 fail; M1 underpowered | the sweep stays unreliable on mortgages across six independent markets; the direction held on 7 of 8 |
| Third cohort (Brazil, Mexico) | underpowered on all components | Brazil's sex gaps sit below the audit's own floor and the gates refused them; the confound stands open |
| Race-arm cohort (screen-gated) | S1 fails by one arm; S2 holds | the cutoff-only reading is beaten 8-9 vs 5: it is the rate, not label rarity; the 0.54 value holds no in-band privilege; the within-population claim passes off-instrument at rho 0.9-1.0 |

The passes carry their own health warnings, stated where the claims are made. The
9-of-10's one-in-twenty binomial tail is against an independent guesser; paired against
the best constant on the same ten arms it is about one in five, and a sequential
correction puts the corrected tail near 0.09. And the sealed cohort has a design
confound stated next to the score: every arm reaches its approval rate through the
income cutoff, so a rule reading only the cutoff scores identically there.

## The week's biggest self-correction: the boundary is the method, not blindness

For two review rounds we said the rule works when the model cannot see the protected
attribute and stops when it can, and we read that as the theory's regime boundary. A
reviewer pointed out our test for this changed two things at once, so it could not
locate the boundary at either. We sealed the missing experiment with both readings'
pass bars committed in advance and ran it: the same optimizer, given the attribute, on
the same eighteen populations. The relationship survived (r = +0.672, stronger than the
blind cell's +0.585). So the boundary is the kind of method, not blindness; the rule's
reach widens; and the theory paper's own group-level claim came out stronger than we
had said, holding in every attribute-aware cell measured, 27 of 27 plus 18 of 18. The
paper's framing is corrected in place and reported as what it is: a reviewer finding a
real hole, and the sealed test siding against our own two-round-old interpretation.

## The lottery, fully characterized

At severe operating points the constraint achieves equality by discarding approvals at
random: your own score stops mattering. We opened the fitted models and saw the
structure directly (members carrying 0.87 of the weight while granting almost
nothing). Three bounds make this precise rather than alarming. It does not appear at
any of nine natural operating points probed, lending included. Where it does appear, no
alternative of the same kind exists at all, so it is what the constraint demands there,
not a vendor's mistake. And the deterministic model a regulated lender would actually
deploy preserves the predicted direction in 10 of 10 populations. The honest charge is
that the lottery happens unannounced, under a certificate that looks like an informed
adjustment.

## The label lesson: anchor to the distribution, not to dollars

Four 2022 states appeared to invert the relationship. The cause was ordinary: the
"earns over $50,000" label had slid down the income distribution. Re-anchored to match
2018's base rates the states behave normally again, and a strict inflation adjustment
is not enough, because real incomes grew past it. Weights, household structure, and
imputed incomes were each tested and each bends the numbers without breaking the
shape. The design lesson is now in the paper's abstract: anchor outcome definitions to
the distribution they cut, a quantile, and audit your own current data.

## The final two campaigns, both scored against us and banked

The six-market lending seal: the sweep protocol failed off its home market (2 of 6),
so lending crossover locations stay unclaimed; the natural-arm direction held on 7 of
8 markets, so the headline contrast survives at exactly the strength the abstract
already gives it.

The third cohort (Brazil 2000/2010, Mexico 2015/2020): underpowered on every
component, because Brazil's income models carry almost no sex gap (0.005-0.039,
below the audit's own 0.05 floor) and the gates refused to manufacture an answer on
another continent. Two things were banked from the refusal: Mexico 2015 brackets the
first crossover ever located outside the United States (0.423-0.483, below the US
cluster), and the standing rule gained a screen gate so no future seal burns compute
on populations its own exclusions would refuse. The race-arm cohort now running is
that gate's first use: Brazil's White versus Black-or-Brown gaps measure three to five
times the floor, so the deconfounding question finally had a powered test - and it answered: it is
the rate (see the ledger's final row).

## The discipline behind the numbers

Sixteen registered tests with committed pass marks; every seal-to-score commit pair
pinned in the paper; the six most recent seals anchored into the Bitcoin blockchain at
sealing time, so the chronology no longer rests on our own clock; 55 automated checks
that re-derive every documented figure from stored results (the population count is
recomputed, never quoted, and the guard has corrected the paper twice); five
adversarial review rounds absorbed, with the two largest corrections in the project
coming from reviewers we took seriously enough to run their experiments.

## What is open, honestly

~~Whether the approval rate or the label's rarity carries the sealed 9-of-10.~~
Answered while this report was being written: the race cohort broke the confound in
the rate's favour (the cutoff-only reading scored 5 of 10 against the rate rules'
8-9). The transported 0.54 value itself showed no in-band privilege over 0.50, so the
"measure your own crossover" form of the claim is the one the evidence crowns. What governs a population's curve
shape (three sealed tests say what it is not). Why the crossover sits where it sits
(locations span 0.28-0.85 including lending, and the located non-lending set is three
after an honest downgrade). Healthcare, where the one public dataset screened was
refused by our own gates and credentialed clinical data is the natural next domain,
with fixed-capacity allocation explicitly out of scope.

## What I am asking

1. Venue and page limit. The reviews' consensus is FAccT-shaped; the compression plan
   to about 10 pages is written and waits on your answer.
2. The title. The current one claims a scope our own sealed test dismantled; two
   bounded candidates are drafted, and the choice is best made once the race cohort
   scores.
3. Does the empirical half stand as a paper, given the theory paper exists? The
   reviews' answer, including a stand-in for the theory authors ("I do not feel
   scooped, I feel operationalized"), was yes; I want yours.
4. AI disclosure. Assistance was substantial (code, analyses, drafting, simulated
   review); how does the department want it disclosed?
5. Contacting the theory paper's authors, after a preprint exists; your call on
   whether and when.
