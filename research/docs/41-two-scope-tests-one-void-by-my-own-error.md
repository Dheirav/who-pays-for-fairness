# 41 — Two scope tests: equalized odds outside ACS, and a post-processing test I broke

**Individual work, beyond the course submission.** Both were run to close standing
objections. One produced a result. The other produced a plausible-looking reversal that turned
out to be a fault in how I set it up, and is reported as void.

---

## C1 — Equalized odds outside the ACS, where document 33's claim was formed

[Document 33](33-the-rule-does-not-survive-equalized-odds.md) found that under equalized odds
the selection rate predicts the direction far more weakly (+0.334 across five ACS states
against parity's +0.762) and that the pool moves roughly **eight times less**. Both claims came
from ACS data alone.

Sweeping the operating point under equalized odds on the two new instruments:

| instrument | r under EO | r under parity | arms retained |
|---|---|---|---|
| **COMPAS** | **+0.900** | +0.870 | 5 of 6 |
| LSAC | — | — | 1 of 6 — **void**, see [doc 40](40-the-arms-that-were-worse-than-doing-nothing.md) |

**On COMPAS the rule works at least as well under equalized odds as under parity.** That is the
opposite of what document 33 reports, and it is the third independent contradiction of that
document's magnitude claim on this dataset: the natural operating point moves **+20.0% under
parity and +32.7% under equalized odds** on the race arm, and −5.1% against −10.6% on sex. The
Dutch census agrees, +0.88% against +4.07%.

**What this costs document 33.** Its *correlation* finding stands where it was measured — under
equalized odds the ACS states genuinely give +0.334. Its **magnitude claim does not generalise**
and must be restated as an ACS observation rather than a property of the criterion. The scope
condition the project has been quoting — "the rule is for criteria that constrain selection
rates" — is now supported on ACS and **contradicted on COMPAS and Dutch**, and the honest
summary is that the criterion's effect depends on the population, which is the same lesson the
crossover taught.

---

## B1 — A second optimiser, and why the result is void

Every crossover result in this project comes from one optimiser: Agarwal et al.'s reduction.
"This is a property of that algorithm" had no answer, so the operating-point sweep was re-run
on Alabama and LSAC with **post-processing** (`ThresholdOptimizer`), which leaves the trained
model alone and moves per-group thresholds afterwards. It also reads the protected attribute at
prediction time, putting it in the **attribute-aware** regime that *Backfire*'s theory treats
separately — so the arm was worth having twice over.

The output looked like a clean reversal: on Alabama the pool changed by −70.2% at the highest
selection rate and **+740.5%** at the lowest, exactly inverting the relationship everywhere
else. On LSAC, +5.6% rising to **+684.5%**.

**It is an artifact of my own setup.** Counting the positives the post-processed model actually
produces:

| operating point | baseline positives | post-processed positives |
|---|---|---|
| 0.02 | 5,784 | **1,722** |
| 0.06 | 5,108 | **1,722** |
| 0.16 | 4,057 | **1,722** |
| 0.49 | 1,737 | **1,722** |
| 0.72 | 665 | **1,722** |
| 0.87 | 206 | **1,722** |

**The post-processed model is identical at every operating point.** `ThresholdOptimizer` is
configured with `predict_method="predict_proba"`, so it reads the estimator's *scores* and
derives its own per-group thresholds. It never sees the decision rule the sweep is
manipulating. The measured "pie change" is therefore a constant divided by a shrinking
baseline, and it inverts for arithmetic reasons that have nothing to do with fairness.

Both sweeps are **void**, and the reversal is not reported as a finding anywhere.

### Why this was nearly believed

The numbers were not obviously broken. A reversal under a structurally different optimiser is
a *plausible* result — post-processing and in-processing genuinely can behave differently, and
Backfire's theory gives a reason to expect the attribute-aware regime to differ. It would have
made an interesting paragraph.

What exposed it was the exchange rate reading **0.000** on five of six arms, which is not a
number a real intervention produces, and a pie change of +740%. Neither is subtle; both were
visible in the first printout and neither would have been questioned if the headline had been
less extreme.

### What a correct version needs

The operating point cannot be varied *inside* a post-processing method that re-derives its own
thresholds. Two designs would work and neither is a re-analysis:

1. **Vary the population instead of the decision rule.** Run post-processing at each
   population's *natural* operating point across many populations, and correlate across them —
   the design of documents 22 and 31 rather than of document 32.
2. **Vary the base model's training**, so that the scores themselves shift, rather than
   thresholding a fixed score vector.

The objection — "this may be a property of one optimiser" — therefore **remains open**, and is
recorded as such in `NEXT.md`. It has not been tested, and this document should not be cited as
having tested it.
