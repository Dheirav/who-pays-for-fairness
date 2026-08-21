# 22 — Levelling down is not universal

**Individual work, beyond the course submission.** The first result in this project from a
domain that is not a household survey.

## Why a second domain, and not a twentieth population

Documents 11–13 and 21 span nineteen arms drawn from ten populations, and nine of those are US state slices
of ACS — one survey instrument, one encoding, one sampling design, one synthetic income
threshold. "Replicates across populations" was earned. "Replicates across domains" was not,
and the two are different claims.

HMDA is a different kind of object: an administrative record of **real mortgage decisions**
reported by lenders under statute, not a survey of people. The label is an institution's
approve-or-deny, not a threshold applied to reported income. Mississippi was chosen because
it is where [document 12](12-intersectional-across-populations.md) found the strongest
intersectional result on ACS, so the same geography is measured through two unrelated
instruments.

Loader, feature whitelist and exclusions: `src/datasets/hmda.py`.

## The result

Mississippi 2018, five seeds, ε = 0.01, logistic regression — the protocol used everywhere
else in this project.

| race arm | baseline | ExpGrad-DP | DP + floor |
|---|---|---|---|
| accuracy | 0.8410 | 0.8083 | 0.8083 |
| **DP difference** | 0.1774 | **0.0103** | 0.0088 |
| equalized odds difference | 0.1062 | 0.1485 | 0.1492 |
| disparate impact | 0.7923 | 0.9878 | 0.9896 |
| **change in favourable decisions** | — | **+4.26%** | +4.42% |
| **destroyed per one created** | — | **0.496** | 0.485 |

| sex arm | baseline | ExpGrad-DP | DP + floor |
|---|---|---|---|
| accuracy | 0.8327 | 0.8208 | 0.8212 |
| **DP difference** | 0.0747 | **0.0280** | 0.0264 |
| equalized odds difference | 0.1085 | 0.0379 | 0.0360 |
| **change in favourable decisions** | — | **+1.05%** | +0.55% |
| **destroyed per one created** | — | **0.779** | 0.878 |

**The constraint levels up on its own, in both arms.** On race it removes 94% of the parity
violation while *increasing* the number of approvals by 4.26%, for 3.3 accuracy points. The
exchange rate is 0.50 — one favourable decision destroyed for every two created.

This is not noise. The across-seed standard deviation of the pie change is **0.17** on the
race arm and **0.29** on the sex arm, against effects of 4.26 and 1.05.

## What this does to document 05's finding

Document 05 measured that every mitigation on Adult shrank the total number of favourable
decisions, by 7.9% to 22.1%. [Document 21](21-the-floor-replicates.md) found the same
direction in all nineteen survey populations: 18 of 19 shrank the pie, and the one exception
(Vermont's sex arm, +0.29%) has a degenerate baseline.

Twenty populations pointing one way, and the twenty-first and twenty-second point the other.

**Nothing in documents 05 or 21 is retracted.** Those measurements were correct on the
populations they were taken from. What changes is their reach: *levelling down is a property
of the fairness-constrained problems this project had been looking at, not of demographic
parity constraints in general.* It is now a finding with a scope condition, and the
condition is not yet identified.

## The floor becomes a no-op, which is the right behaviour

The selection-rate floor of [document 19](19-levelling-up-is-expressible.md) does almost
nothing here: +4.26% against +4.42% on race, and on sex it is marginally *worse* (+1.05%
against +0.55%), within an across-seed spread of 0.29.

That is what should happen. The floor constrains `P(h(x)=1) ≥ baseline rate`, and a
constraint that is already satisfied does not bind. **The construction does not distort a
model that had no levelling-down problem to fix** — worth knowing, because a remedy that
made things worse where it was not needed would be much harder to recommend.

## A candidate explanation, and why it is not claimed

The obvious difference is where the task sits on the selection-rate scale. Every population
in documents 11–13 and 21 lands between **0.195 and 0.353**; HMDA's arms sit at **0.808 and
0.758**, entirely outside that range. When most applicants are already approved, closing a
gap by lifting the disadvantaged group costs little, because they sit near the boundary
already.

Tested post-hoc on the nineteen survey populations, the direction is consistent:

| | r |
|---|---|
| baseline selection rate vs pie change under the plain constraint | **+0.510** |
| baseline selection rate vs exchange rate | **−0.493** |

**This is offered as a conjecture and not as a finding**, for three reasons stated plainly:

* **It is post-hoc.** The hypothesis was formed after seeing the HMDA result, which is the
  move [document 13](13-separating-ratio-from-size.md) records going wrong.
* **The nineteen are not independent**, being nine states measured in two arms, so an
  r of 0.51 rests on far fewer than nineteen degrees of freedom.
* **The comparison is confounded, badly.** HMDA differs from ACS in domain, instrument,
  label semantics, feature set, group ratio (2.85 against 1.02–1.24), proxy leakage (0.830
  against 0.76–0.84) and selection rate *simultaneously*. Attributing the reversal to the
  last of those, on a range the survey data never covers, is exactly the inference this
  project has twice retracted.

## The test that would settle it

Vary the selection rate and **nothing else**. ACS Income's label is "income above $50,000",
a threshold chosen by the benchmark rather than by nature. Sweeping that threshold on one
fixed state moves the base rate from roughly 0.8 to roughly 0.1 while holding the
population, the instrument, the features, the group ratio and the proxy structure exactly
fixed.

If levelling down reverses as the threshold falls, the selection rate is the moderator. If
it does not, the reversal belongs to something else about HMDA and the conjecture above is
dead. This is a clean, cheap, single-factor design of the kind
[document 18](18-the-collinearity-test-is-confounded.md) could not achieve, and it has not
been run.

## One thing that did replicate

Document 14 found that the DP/EO conflict **reverses across protected attributes**. It does
so here too, in a domain it was not derived from: constraining demographic parity makes
equalized odds *worse* on the race arm (0.1062 → 0.1485) and *better* on the sex arm
(0.1085 → 0.0379).

That was not looked for, and it is the second time an arm-level reversal has appeared
without being sought.

## Limits

* **One state, one year, one domain.** Mississippi 2018. A second high-selection-rate
  population is needed before "high base rates reverse it" is even a candidate condition.
* **The two arms are not independent.** They are the same applications split two ways.
* **The whitelist is a judgement.** Thirty-six columns were excluded as post-decision or
  protected, each with a recorded reason. A different whitelist would give different
  numbers, and `denial_reason-1` — 99.2% predictive with a missingness gap of 0.000 —
  shows how much is riding on getting it right.
* **Sex-arm parity is not fully satisfied.** DP lands at 0.0280 against a requested
  ε = 0.01, from a baseline of only 0.0747.
