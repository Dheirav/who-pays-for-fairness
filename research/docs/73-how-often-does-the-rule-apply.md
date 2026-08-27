# 73 — How often does the rule apply at all?

**Individual work, beyond the course submission. Descriptive survey, not a seal.**
Fifty randomly drawn ACS populations, 660 arms, 27 Aug.
Frame and draw committed before any arm ran: [`../survey-frame.json`](../survey-frame.json).

## The gap this fills

Every statement this project makes about how often the audit answers has rested on a
denominator nobody chose. The verdict distribution of Section IX walks the sweeps this
project happened to accumulate over months, selected by whatever question was being asked at
the time. [Document 71](71-the-prior-cannot-see-the-landscape.md) is worse in this respect
and says so: its six populations were picked *because* they sat near a boundary, so its
finding that five of six are non-monotone supports no rate at all.

The question underneath is one nobody appears to have measured: **how often does a
population's response to a parity constraint admit a directional rule in the first place?**

## Design

Frame: 50 states x {2014, 2018, 2019} x {SEX, RAC1P}, income cutoff held at $50,000 — 300
populations. Fifty drawn uniformly at random, RNG seed 20260827, written to
`research/survey-frame.json` before any arm ran. Twelve operating points each, five seeds,
plus the natural arm. The draw came out balanced without being forced: 25 SEX / 25 RAC1P,
and 14 / 14 / 22 across the three vintages.

2022 is excluded. Its inversion is a diagnosed nominal-label artifact, and including it
would have conflated a label problem with a landscape property.

Each population is classified by Algorithm 1's own rules, after its parity floor: the
median population contributed 12 swept arms of which 10 survived.

## The result

| landscape | n | share |
|---|---|---|
| **classic** (− to +, one rising crossing) | 32 | **64%** |
| monotone, one sign throughout | 7 | 14% |
| non-monotone, 2 sign changes | 7 | 14% |
| non-monotone, 3 sign changes | 2 | 4% |
| **inverted** (+ to −) | 2 | 4% |

Grouped by whether a directional rule applies at all:

| | n | share |
|---|---|---|
| **the rule applies** | 39 | **78%** |
| **no rule applies** | 11 | **22%** (Wilson 95% CI 13–35%) |

**A parity constraint's response admits a directional rule in roughly four populations in
five, and does not in the fifth.**

## What it corrects

**The convenience sample was mildly optimistic.** The audit's own stored-sweep tally gave 8
non-monotone of 52, about 15%. The unbiased draw says 22%, with the interval running to 35%.
Not a large discrepancy, and reassuring about the historical sweeps — but in the direction
this kind of error usually runs, and the honest figure is the larger one.

**Inversion is not only a 2022 label artifact.** Two populations invert here, at a fixed
$50,000 cutoff in 2018 and 2019 — `acs:IA:SEX:50000:2019` and `acs:WI:SEX:50000:2018`. With
Missouri 2014 from document 71 that is three independent sightings outside 2022. The paper's
account should become: the 2022 inversions were substantially label-driven, *and* inversion
occurs otherwise at a low rate, around 4%.

**Sex arms are the harder ones.** Directional in 68% of sex arms against 88% of race arms,
and both inverted populations are sex arms. On 25 each that difference is not significant,
but it points the same way as the lending result of
[document 72](72-every-market-in-the-country.md), where every one of 26 sex arms fell below
the audit's disparity floor. Sex gaps are smaller, and smaller gaps make for noisier
landscapes.

## What it does not settle

**ACS only.** Lending is excluded deliberately: its sweeps are unreliable and document 71
gives the mechanism, so including it would have measured the sweep's failure rather than the
landscape's shape. Nothing here is a statement about mortgage markets.

**One cutoff.** Holding the label at $50,000 isolates the population as the varying factor,
but it cannot separate "this population is non-monotone" from "this population is
non-monotone *at this cutoff*". Given the vintage finding, that distinction is not obviously
minor, and a quantile-anchored second pass would settle it.

**Fifty is enough for a headline and not for a breakdown.** The 78% carries an interval of
13 to 35 points on its complement; the by-attribute and by-year splits above are reported
because they are suggestive, and should not be quoted as findings.

## Why the number matters

It bounds the claim rather than supporting it. The paper's central result is a rule about
direction; this says the rule is in scope for about two populations in three by the strict
reading (classic only) or four in five by the generous one (any directional verdict). Both
are majorities, and neither is "generally".

The audit already refuses the other fifth without being told to. That is the part worth
keeping: **the procedure's refusals are not a shortfall, they are the measured 22%.**
