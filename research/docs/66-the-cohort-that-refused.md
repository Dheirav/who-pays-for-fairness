# 66 — The cohort that refused

**Individual work, beyond the course submission. Sealed test, scored as committed.**
The third cohort (seals `50d467f` stage A, `a624cf5` stage B, both externally
anchored); Brazil 2000/2010, Mexico 2015/2020; 42 arms × 5 seeds on sealed 60k
subsamples.

## The verdict: UNDERPOWERED on all three components, as pre-registered

S1: 7 scorable in-band arms against the floor of 12. S2: one monotone population
against the floor of 2 (MX-2015, ρ = 0.70, exactly at the bar). S3: zero scorable
shape sweeps. No verdict is claimed on any component.

## Why: Brazil has almost no conditional sex gap for the gates to act on

Baseline parity gaps at the sealed labels: BR-2000 0.031/0.007/0.005, BR-2010
0.039/0.008 — nearly every Brazilian arm sits below the 0.05 floor, and the audit's
own first gate refused them, exactly as it refused UCI diabetes. Mexico is marginal
(0.03–0.08). This is the fourth refusal species in action, off-instrument and
off-continent: the machinery declined to manufacture an answer. It is also a
substantive cross-country fact: under this feature set, employed Brazilians' sex income
disparity at mid-band labels is small enough that a parity constraint has little to act
on.

## Recorded without a verdict

On the seven surviving arms the rule scores 5/7, the 0.5-prior null 5/7, the
cutoff-only null 6/7 — **the label-rarity confound on the 9-of-10 remains open**, and
the paper's abstract clause stands unchanged. And one unqualified positive: MX-2015
brackets a crossover at **0.423–0.483** — the first located outside the United States —
*below* the US survey cluster, further stretching the located span (now 0.28–0.85
counting the two lending locations of doc 65).

## The design lesson, added to the standing rule

A seal committed before the data exists cannot pre-screen the gaps its own exclusions
require. Future two-stage seals carry a **screen gate** between stage B and the runs:
measure the baseline gaps, record which populations the frozen gates refuse, and only
then run the survivors — refusals cost a day of compute this time and should cost a
seed-0 screen instead.

## The salvage that respects the seal

The extract carries RACE for Brazil, and Brazilian racial income gaps are large where
the sex gaps are not. A race-arm supplement — screened first, then sealed, per the new
gate — is the natural fourth cohort and costs about two hours. The sex-arm verdict
above stands as scored and is not reopened.
