# 39 — Three more instruments: criminal justice, legal education, and a non-US census

**Individual work, beyond the course submission.** Predictions and thresholds were fixed in
`src/experiments/analyse_generalisation.py` and committed at `0ce4ced` and later for the
Dutch arm, before any of the arms scored here were run.

**Read [document 40](40-the-arms-that-were-worse-than-doing-nothing.md) alongside this.** It
imposes an exclusion rule that changes two of the verdicts below, and both scorings are given
here rather than only the surviving one.

## The weakness this closes

Every population measured before this was the American Community Survey or HMDA mortgage
records: two instruments, one country, one year. The claim is about **decision systems**, and
no number of additional ACS states can test that — they share an instrument, an encoding and
a label construction.

| instrument | domain | n | base rate | why it is here |
|---|---|---|---|---|
| **COMPAS** (2016) | criminal justice | 5,278 | 0.53 | the canonical fairness benchmark; its absence is itself a question |
| **LSAC** bar passage | legal education | 20,798 | **0.89** | naturally generous — populates the top of the range |
| **Dutch census** (2001) | occupational status | 60,420 | 0.48 | **non-US, non-2010s**, and a group gap twice Adult's |

The second and third were chosen for reasons beyond the domain. Almost every *natural*
population here sits at a **low** selection rate and only mortgage lending occupied the top,
so the half of the claim predicting levelling **up** was tested far less hard than the other.
And the oldest competing explanation — that the *gap between the groups* drives the direction
rather than the overall rate — had never been tested on a population with an extreme gap.

**None of the three has a label cutoff to move.** The only way to vary the selection rate is
the operating-point route, so this is simultaneously a test of the rule and of the procedure
[document 35](35-what-to-do-about-it.md) recommends.

## The result

| instrument | r (as run) | r (after doc 40's rule) | verdict |
|---|---|---|---|
| COMPAS | **+0.870** | **+0.870**, 0 arms dropped | **HOLDS** |
| Dutch | **+0.915** | **+0.915**, 0 arms dropped | **HOLDS** |
| LSAC | +0.968 | — 1 arm survives | **VOID** |

**The naive alternative is dead.** It was named in advance: *"the rule is a property of income
prediction and American mortgage lending; on criminal justice and legal education it predicts
nothing"*, needing |r| < 0.30. Two instruments clear +0.87 with every arm intact.

**LSAC's +0.968 is withdrawn**, not because the relationship failed but because five of its
six arms were models beaten by always predicting "passes" — see document 40. The number was
reported to the supervisor before that was noticed, and the correction is recorded rather
than quietly replaced.

## G7 — the group-gap alternative loses on the population built to test it

Dutch men hold a high-status occupation at **0.626** and women at **0.327**: a gap of
**0.298**, roughly twice Adult's. [Document 23](23-the-selection-rate-sets-the-direction.md)
partialled the group gap out and the relationship survived, but no population then measured
had a gap this large, so the test was weakest where it mattered.

**r = +0.915 across all six arms, none excluded by either rule.** Twice the gap changes
nothing. The competing explanation predicted a failed correlation or a crossover outside the
observed span, and got neither.

One honest qualification: the arms do **not** bracket a clean crossover. Ordered by descending
rate the pie changes run +12.38, +13.64, −4.34, **+0.29**, −27.04, −35.99 — one arm at a rate
of 0.390 sits out of order at +0.29%, a value indistinguishable from zero. The relationship is
strong; the transition point on this population cannot be located from six arms.

## G1 — the predicted sign, at the natural operating point

| instrument | natural rate | change in the pool |
|---|---|---|
| **LSAC** | 0.954 | **+3.81%** — predicted |
| Dutch | 0.437 | +0.88% |
| COMPAS (race) | 0.583 | +20.00% — *sign not predicted* |
| COMPAS (sex) | 0.628 | −5.12% — *sign not predicted* |

LSAC levelling up at 0.954 was written down in advance and is the first natural population at
the very top of the range. COMPAS's sign was explicitly **not** predicted, because 0.583 sits
inside the band where crossovers have been observed, and it is not claimed now.

## G6 — a prediction aimed at this project's own earlier work, and doc 15 won

[Document 15](15-arbitrariness-at-small-scale.md) put the floor for measurability at about
2,500 test subjects. COMPAS has **1,584**; LSAC has **6,240**.

| | arms whose sign flips between seeds | worst standard deviation |
|---|---|---|
| **COMPAS** (below the floor) | **2 of 4** | **28.30** |
| **LSAC** (above it) | **0 of 4** | 0.35 |

Document 15 made a correct out-of-sample prediction on a dataset it never saw, at twelve seeds
against five. That is worth more than any single correlation here: an earlier result in this
project has predictive power, which is the only real evidence that the rest of its numbers can
be trusted.

The consequence is that **COMPAS carries direction, never magnitude.**

## The remedy works on all three

The selection-rate floor — the project's one *useful* contribution — had never been run outside
ACS and HMDA. It runs by default in every arm here:

| instrument | plain | with the floor |
|---|---|---|
| COMPAS | +20.00%, exchange 0.47 | **+26.77%**, exchange 0.38 |
| Dutch | +0.88%, exchange 0.94 | **+1.13%**, exchange 0.93 |
| LSAC | +3.81%, exchange 0.03 | +3.80%, exchange 0.05 |

It helps where there is damage to undo and is close to free where there is not, which is what
[document 21](21-the-floor-replicates.md) found on survey data and what it should do.

## Two results that did not go the predicted way

**G5 failed on COMPAS.** [Document 33](33-the-rule-does-not-survive-equalized-odds.md) found
the pool moves roughly eight times *less* under equalized odds. On COMPAS it moves **more** —
+20.0% becomes +32.7% on the race arm, −5.1% becomes −10.6% on sex. On Dutch it also grows,
+0.88% to +4.07%. Document 33's magnitude claim is **ACS-specific and is now stated that way**.

**COMPAS's two attribute arms disagree at their natural operating points** — race grows the
pool 20.0%, sex shrinks it 5.1%, at similar selection rates. That looked like evidence the
crossover is attribute-specific. [Document 40](40-the-arms-that-were-worse-than-doing-nothing.md)
tested it directly on Oregon and found the opposite: sex gives 0.362–0.653 and race gives
0.358–0.652, nearly identical. The two facts are compatible — COMPAS's race and sex arms are
not the same population, because the race arm drops defendants outside the two groups
ProPublica compare — but the tension is recorded rather than resolved by assertion.

## What this buys, stated plainly

Five domains, four instruments, two countries, two decades. The relationship reproduces on
criminal justice and on a Dutch census, and on the latter with twice the group inequality.

What it does **not** buy: the crossover *location* still cannot be quoted as a constant, LSAC's
headline is withdrawn, and COMPAS is too small to carry a magnitude claim.
