# What I did, what I found, and what I need from you

## Where this started

This began as the course project for Responsible AI: measure and mitigate bias in an
income classifier on the standard UCI Adult benchmark. That part is complete and
submitted. While doing it I noticed something the assignment did not ask about, and I
kept pulling on it after the deliverable was done. Everything in this document is
individual work beyond the course submission, and all of it is committed in a public
repository where every number below is re-derived from stored results by automated
checks.

## The observation that started it

A fairness constraint asks a model to approve two groups at similar rates, but it does
not say how the gap should close. The model can approve more people from the group
that was behind, or approve fewer from the group that was ahead. Both count as
success, and the fairness metric that certifies the fix comes out identical in both
cases. So a team imposing a constraint cannot tell, from its own reporting, whether it
is about to extend opportunities or withdraw them.

On Adult, every mitigation method I tested closed the gap the second way. The total
pool of approvals shrank by 8 to 22 percent depending on the method, and when I
counted people instead of rates, 66 to 74 percent of everyone whose decision changed
was a person losing an approval. The metric reported success identically throughout,
which meant the interesting question was not whether this happens but when.

## The finding

I measured what decides the direction, across what grew to 67 populations from 8 data
sources in 5 countries: US census data across forty states and multiple years, real
mortgage decisions from eight state markets, criminal justice, education, the Dutch
census, Taiwanese credit, and census extracts from Brazil and Mexico.

Within a population, the baseline approval rate read against that population's own
switch point predicts whether the constraint will grow or shrink the pool. Stingy
systems lose approvals when you impose parity, while generous systems gain them, and
the switch between the two sits at a measurable crossover. On mortgage data, where
approval rates run above 0.8, the same constraint that shrinks Adult's pool by a fifth
grows the pool instead, in 7 of the 8 markets tested. The claim covers direction only:
the size of the effect is ordered within a population but does not transfer between
populations, and a model of size that I registered in advance lost to predicting zero,
so the paper does not claim it.

There is a transported shortcut, "below roughly 0.54 the fix takes, above it gives",
and it works often but not always. It called 9 of 10 never-measured states correctly
in a prediction committed to the repository before the data existed, but it managed
only 5 of 10 on a later set of larger states, and located crossovers now span 0.28 to
0.85. So the honest form of the finding is: measure your own crossover with the audit
procedure I built, and treat 0.54 as a starting guess rather than a law.

## How I made sure this is real

Correlations found after the fact are weak evidence for a claim of the form "you can
know in advance", so the project runs on pre-registered predictions. A prediction, its
pass mark, and the naive alternative it must beat are committed to the repository
before the data exists, and the recent commitments are also timestamped into the
Bitcoin blockchain so the ordering does not depend on trusting my clock.

Sixteen such tests now stand. Ten failed or were refused, and every failure is
published uncorrected, because each one removed a claim stronger than the one that
survives. The ones that matter most:

| Test | Outcome | What it settled |
|---|---|---|
| Sealed direction rule, refined | 4 of 8, fail | a clause I added from early data was wrong, and is withdrawn |
| Re-seal of the simple rule | 9 of 10, holds | the rule predicts unseen states from the rate alone |
| Sealed magnitude model | fail | effect size cannot be predicted; direction only |
| Post-processing transfer | fail | the rule vanishes when the fix is applied after training |
| Regime deconfounding | method reading | see the correction below |
| Six-market lending seal | protocol fail, direction holds | my sweep procedure is unreliable on mortgages, while the direction held on 7 of 8 markets |
| Brazil and Mexico, sex arms | refused | Brazil has almost no conditional sex gap, so my own gates declined to answer |
| Brazil race arms, screen-gated | rate wins | see below: the biggest open question, answered |

Two results from the final campaigns deserve their own lines. First, the one standing
worry about the 9-of-10 was that those arms reached their rates through an income
cutoff, so a rule reading only the cutoff would have scored identically, which meant
the evidence could not separate "the approval rate predicts" from "the label's rarity
predicts". A powered test on Brazil's racial gap separated them: the cutoff-only
reading scored 5 of 10 while the rate scored 8, so it is the rate. Second, the
0.54 value itself earned no special status in that test, which is consistent with
everything above: the portable thing is the procedure, not the number.

## What I got wrong, and what correcting it taught

Two of the project's biggest findings came from being wrong in public.

For two review cycles I claimed the rule works only when the model cannot see the
protected attribute, and I read that as matching the boundary a related theory paper
draws. A reviewer pointed out my evidence changed two things at once, so I sealed the
missing experiment with both possible readings' pass marks committed in advance. The
result went against my own interpretation: the same method with the attribute visible
keeps the relationship fully intact, so the boundary is the kind of method, not
blindness, and the rule applies more widely than I had claimed.

Separately, four 2022 states appeared to invert the whole relationship. The cause
turned out to be that the "earns over $50,000" label had slid down the income
distribution, and a strict inflation correction was not enough because real incomes
grew past it. What restores normal behaviour is matching the label's position in the
distribution, which is a general lesson: outcome definitions anchored to fixed
dollar amounts are a different task every year without anyone noticing.

One more finding worth naming because it is fully mine: at severe operating points the
constraint achieves equality by discarding approvals at random, so a person's own
score stops mattering, under a certificate that looks like an informed adjustment. I
verified this inside the fitted models, showed it does not happen at any normal
operating point tested, and showed no alternative of the same kind exists where it
does happen. A citation-graph audit found this observation nowhere in the literature.

## How this relates to the existing theory

A March 2026 theory paper proved that in this setting the direction can go either way
depending on the data. That paper contains no experiments, never mentions an approval
rate, and states its conditions over quantities that could not be evaluated on any of
26 real datasets under either of two estimators I tried. My contribution relative to
it: the computable predictor it lacks, the validation record, the boundary map, and
one correction to where its regime line bites in practice, while its own group-level
prediction held in every one of the 45 attribute-aware populations I measured. The
approval rate tracks their theoretical quantity at a correlation of 0.85 across 150
populations, so the number I use appears to be the practical stand-in for the quantity
their theorem is written over.

## Where it stands

The paper is 18 pages in IEEE format with a written plan to compress to about 10 once
a venue is chosen. The record behind it: 68 numbered research documents, 55 automated
checks that fail if any documented number disagrees with stored results, and every
pre-registration verifiable from the public repository.

## The decisions I need from you

1. **Venue and page limit.** The work is shaped like FAccT or AIES. Your answer
   decides the compression depth, and the plan is already written.

2. **Does the empirical half stand as a paper, given the theory paper exists?** My
   position: their theorem is not computable on data and mine is the instrument that
   reads it, which is a recognized kind of contribution. This is the call I most need
   from you.

3. **The title.** The current title claims a scope my own sealed test dismantled. Two
   bounded replacements are drafted, and I would like your pick.

4. **Contacting the theory paper's authors.** My results confirm their group-level
   prediction everywhere, correct their regime boundary, and hand them an open theory
   problem. Standard practice is a short collegial email once a preprint exists. I
   want your read on whether and when, and whether you want to be on it.
