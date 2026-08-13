# 17 — Neither explanation survives

**Individual work, beyond the course submission.** Tests the replacement explanation
offered in [document 16](16-planting-a-proxy.md). It fails.

## Where this stood

Document 06 measured that constraining demographic parity on Adult moves SHAP attribution
onto `relationship` by **+151%** and off `marital-status` by −23%, and explained it as the
model *selecting the best available reconstruction of sex*.

[Document 16](16-planting-a-proxy.md) planted a pure sex proxy and refuted that: the
constrained model used it **less** as it sharpened, monotonically. It offered a
replacement — `relationship` attracts the constrained model because it predicts income
well *within* each sex, and its sex-determining character is incidental — and flagged that
this was consistent with the evidence but untested, because only one property had been
varied.

## The 2-factor test

The planted column now carries two independent bits: one indicating sex, correct with
probability *strength*; one indicating the label, correct with probability *outcome*. Both
knobs verified separable before running — the sex knob moves leakage by **+0.136** while
leaving the within-sex outcome spread alone; the outcome knob moves that spread by
**+0.511** while leaving leakage unmoved. At its top setting the spread (0.53) is
comparable to Adult's `relationship` (0.438 / 0.473).

Alabama, 22,268 rows, three seeds per cell.

| outcome | sex | baseline share | constrained share | **excess** |
|---|---|---|---|---|
| 0.50 | 0.5 | 0.0242 | 0.0343 | +0.0101 |
| 0.50 | 1.0 | 0.0606 | 0.0471 | −0.0135 |
| 0.65 | 0.5 | 0.0964 | 0.0927 | −0.0038 |
| 0.65 | 1.0 | 0.0952 | 0.1013 | +0.0061 |
| 0.80 | 0.5 | 0.2063 | 0.1961 | −0.0103 |
| 0.80 | 1.0 | 0.2159 | 0.1874 | −0.0285 |

**R0 HOLDS** — the knobs move different things.
**R1 FAILS** — excess *falls* along the outcome dimension: −0.0204 at sex 0.5, −0.0150 at
sex 1.0. The bar was +0.02 in the other direction.
**R2 HOLDS** — the sex dimension does not raise it either, replicating document 16.

## What the table actually shows

Read the two share columns rather than the difference. Both models use the planted column
heavily once it carries outcome signal — a **0.21 attribution share** at the top setting,
making it one of the most-used features in the model. And the constrained model tracks the
unconstrained one almost exactly: the excess never exceeds **0.03** in absolute value in
any of the six cells, while the share itself ranges over an order of magnitude, 0.024 to
0.216.

**The demographic-parity constraint does not systematically change which features the
model leans on.** It reweights training examples, and the resulting model's attribution
profile follows the unconstrained one closely, whether the feature in question determines
sex, predicts the outcome, both, or neither.

> **Narrowed by [document 20](20-what-a-share-can-carry.md).** As stated, that sentence is
> broader than what was measured here. This experiment observed *one planted column* on one
> population — not a profile — and Adult is a counterexample under the same constraint:
> `relationship` moves +0.114 of share, nearly four times the 0.03 treated as "tracking
> almost exactly" below. The estimand cannot carry the general form either, because
> attribution *shares* are compositional and do not identify which features a model leans
> on. What this experiment does support: **on a planted column, under demographic parity at
> ε = 0.01, on one population, the constrained model's share tracks the unconstrained
> model's to within 0.03 across six cells spanning an order of magnitude in that share.**

That is a cleaner statement than either explanation it replaces, and it is a **negative
result**: two specific mechanisms were proposed and both were refuted by intervention.

## So the Adult shift has no identified mechanism

The +151% is real, reproducible, and now unexplained. Both candidate explanations were
specific enough to be tested and both were wrong. The honest position is that this project
cannot say why it happens.

## The next candidate, stated but not claimed

One observation is worth recording, **as a hypothesis with its premise measured and
nothing more**. Attribution moved between two features that are unusually redundant with
each other:

| pair, Adult | Cramér's V |
|---|---|
| **`relationship` ↔ `marital-status`** | **0.487** |
| `workclass` ↔ `occupation` | 0.217 |
| `relationship` ↔ `occupation` | 0.177 |
| `marital-status` ↔ `occupation` | 0.130 |
| `relationship` ↔ `race` | 0.097 |

| planted column, ACS | Cramér's V |
|---|---|
| `SYNTH` ↔ `OCCP` (its strongest partner) | 0.179 |

`relationship` and `marital-status` are twice as redundant as any other pair in Adult —
Husband implies Married-civ-spouse almost deterministically. Shapley values divide credit
between collinear features in a way that small weight changes can reallocate substantially
without the model's behaviour changing at all. The planted column has no comparable
partner, which would explain why nothing moved in either experiment.

**This is the third explanation, and it is not being accepted on weaker evidence than the
two that were rejected.** What is measured is the redundancy. What is *not* measured is
whether it causes the shift. The test is available and specific: plant a **pair** of
collinear columns, vary their mutual redundancy, and see whether attribution reallocates
between them under the constraint while the model's decisions stay fixed. Until that is
run, the Adult attribution shift is unexplained and should be described that way.

## What this changes

| claim | status |
|---|---|
| Document 06's measurements | **Stand.** Unchanged and re-verified |
| Document 06's mechanism (reconstruction-seeking) | Retracted in document 16 |
| Document 16's replacement (outcome-signal-seeking) | **Retracted here** |
| Document 16's core negative finding — a sharper sex proxy is used *less* | **Replicated** (R2) |
| The new statement — the constraint barely changes *which* features are used | **Narrowed in [document 20](20-what-a-share-can-carry.md)** to the planted column it was measured on. The general form is not supported by a share-based estimand, and Adult contradicts it |

The course submission is untouched. Document 06 reports attribution measurements, and
those are unchanged; what has been withdrawn twice is interpretation, and both retractions
live here.

## Limits

* **One population, one constraint, one base learner** — Alabama, demographic parity at
  ε = 0.01, logistic regression.
* **Three seeds and a sampled explainer.** The claim rests on excess staying near zero
  across six cells while the share itself moves by a factor of nine, not on any cell.
* **"Barely changes which features are used" is bounded by what SHAP measures.** Two
  models with near-identical attribution profiles can still differ in their decisions —
  and here they do: the constrained model's decisions differ enough to take DP from
  roughly 0.13 to under 0.02.
