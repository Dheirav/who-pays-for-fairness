# 47 — The sealed prediction failed, and the refinement added two hours earlier is why

**Individual work, beyond the course submission.** Predictions, populations, the rule and the
bar were fixed in `src/experiments/analyse_sealed.py` and committed at `f64d9a7`, **before any
of the nine arms existed**.

## The result

**4 of 8. The bar was 7. It fails, and it does not beat a constant.**

| population | rate | change in pool | predicted | actual | |
|---|---|---|---|---|---|
| MO, $100k | 0.026 | **−16.48%** | up | down | ✗ |
| AZ, $100k | 0.037 | **−23.34%** | up | down | ✗ |
| IN, $70k | 0.081 | **−23.32%** | up | down | ✗ |
| TN, $50k | 0.255 | −1.68% | down | down | ✓ |
| MD, $50k | 0.508 | +0.78% | down | up | ✗ |
| MI, $30k | 0.612 | +0.85% | up | up | ✓ |
| NC, $20k | 0.789 | +0.16% | up | up | ✓ |
| GA, $10k | 0.905 | +0.30% | up | up | ✓ |

Best constant: **4 of 8.** The sealed rule did not beat guessing.

## What broke it

The rule that was sealed carried
[document 46](46-the-relationship-turns-back-up-at-the-bottom.md)'s refinement: *up* below a
selection rate of 0.10, *down* to the crossover, *up* above it. **S2 asked specifically whether
the low-rate arms would come out positive. All three came out strongly negative** — −16%, −23%,
−23%. Not marginally, not noisily.

Scoring the same eight arms under the rule this project held **before** document 46:

| rule | score |
|---|---|
| sealed rule, with document 46's low-rate refinement | **4/8** |
| simple monotone: down below 0.54, up above | **7/8** |
| constant "always up" | 4/8 |
| constant "always down" | 4/8 |

**The refinement turned a 7-of-8 prediction into a 4-of-8 one.** Document 46 was written two
hours before this test, from four populations, and it made out-of-sample performance
substantially worse.

**The 7/8 is post-hoc and is not claimed as the sealed result.** What was sealed scored 4/8 and
that is the result. But the comparison is the finding, and it could not have been obtained any
other way.

## Why document 46 was wrong, and it is not simply noise

Document 46's low-rate arms came from the **operating-point route** — thresholding one fixed
score vector at an extreme. The sealed arms come from the **income-cutoff route** — a genuinely
different label with a genuinely low base rate. Both reach a selection rate near 0.05.

They disagree completely at that rate: **+8.73, +6.85, +9.09 by the operating-point route
against −16.48, −23.34, −23.32 by the cutoff route.**

So the turn-up is **a property of the route, not of the selection rate**. Thresholding a fitted
model at an extreme produces a classifier that is nothing like a model trained on a rare label,
and near a rate of 0.05 that difference dominates.

This qualifies [document 32](32-the-rate-not-the-task.md) precisely. That document showed the
two routes agree — on direction, on the location of the crossover, on two populations. **They
agree in the middle of the range and diverge at the bottom of it.** The accuracy rule does not
catch the divergent arms: they clear the trivial-predictor bar and are still route artifacts.

## What now stands

* **The simple monotone rule survives the sealed test** at 7 of 8, and its single miss is
  Maryland at 0.508 — within 0.03 of the crossover, on an effect of +0.78%. That is a boundary
  call on a near-zero quantity, which is what a rule with a threshold should get wrong.
* **Document 46 is withdrawn as a claim about selection rate.** What it measured is real and
  reproducible: the operating-point route turns up at the bottom. What it concluded — that the
  relationship turns up below 0.10 — does not hold on the natural route and should never have
  been stated as a property of the rate.
* **Document 45's sensitivity finding is therefore back in play.** It observed that admitting
  low-gap arms collapses the ACS correlations; document 46 explained that away as a second
  regime; this shows the explanation was wrong. The correct statement is that those arms are
  **route artifacts of the operating-point sweep** and the exclusion is right to drop them, for
  a different reason than either document gave.
* **Taiwan, reported separately, was predicted correctly**: rate 0.885, predicted up, observed
  +0.68%. One arm, one non-Western population, and it is not evidence of anything on its own.

## The methodological point, which is the reason to run tests like this

A refinement derived from four in-sample populations, published in this repository, internally
consistent, and supported by a twenty-seed replication, **made the prediction worse than the
simpler rule it replaced and no better than a constant.**

Nothing in the in-sample data could have revealed that. Document 46's evidence is still
correct — those arms really are positive. The error was in what it was taken to mean, and only
a prediction registered before new data could expose it.

This is the fourth time in this project that an assumption survived until something forced it
to be computed. It is the first time one was caught by a test written in advance rather than by
noticing an inconsistency afterwards.
