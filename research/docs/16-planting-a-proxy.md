# 16 — Planting a proxy: the mechanism was wrong

**Individual work, beyond the course submission.** This retracts the *mechanism* proposed
in [document 06](../../docs/06-proxy-reliance-shap.md) and carried forward as P3 in
[document 11](11-replication-across-populations.md). The measurements in both stand.

## The claim under test

Document 06 measured that constraining demographic parity on Adult moves SHAP attribution
off `marital-status` and onto `relationship` — from 0.075 to 0.189, a **+151%** increase —
and explained it in terms specific enough to be falsifiable:

> "it is selecting the best available reconstruction of the attribute it was forbidden to
> read. That is the mechanism, stated precisely enough to be checked."

Document 11 then found that ACS, which has no comparable feature, leaks sex at 0.76–0.84
against Adult's 0.936 with no overlap across nine populations — and read that as nine
confirmations of the mechanism.

It is not. It is nine confirmations of a **correlation**: populations without a strong
proxy leak less. The mechanism says something stronger and causal — *the constraint seeks
out reconstructions of the protected attribute* — and correlational evidence cannot reach
it. So the proxy was planted deliberately.

## The intervention

A synthetic column mirroring Adult's `relationship`: 46% of rows (Adult's Husband+Wife
share) take one of two sex-indicating levels, the rest an uninformative third, with the
indicating levels correct at probability *strength*. At strength 0.5 the column exists,
has the same cardinality and marginals, and says nothing about sex.

Alabama, 22,268 rows, four strengths, three seeds. Both models explained with the **same**
sampled explainer over identical background and instances — see the methodological note
below, which turns out to matter.

| strength | leakage AUC | baseline share | constrained share | **excess** |
|---|---|---|---|---|
| 0.50 | 0.8048 | 0.0314 | 0.0460 | **+0.0146** |
| 0.70 | 0.8281 | 0.0422 | 0.0500 | **+0.0078** |
| 0.85 | 0.8740 | 0.0560 | 0.0548 | **−0.0012** |
| 1.00 | 0.9415 | 0.0686 | 0.0600 | **−0.0086** |

**I0 HOLDS** — leakage rises 0.805 → 0.942. The manipulation worked; sex genuinely became
more recoverable.
**I1 HOLDS** — the unconstrained model leans on the column more as it sharpens,
0.031 → 0.069. It is a real, usable signal.
**I2 FAILS** — the constrained model's excess is **−0.0086** at full strength, against a
bar of +0.02.
**I3 holds, barely** — the excess at the null is +0.0146, inside the bar but the *largest*
value in the table.

## What it actually shows

The excess does not merely fail to rise. It **declines monotonically as the proxy gets
stronger**, and crosses zero. Read down that last column: +0.0146, +0.0078, −0.0012,
−0.0086.

**The better a feature reconstructs sex, the less the demographic-parity-constrained model
uses it, relative to the unconstrained one.** That is the opposite of the stated mechanism,
and in hindsight it is the mechanically sensible outcome: under a demographic parity
constraint the model must equalise selection rates across sexes, and a feature that
determines sex is precisely what it *cannot* lean on while doing so. Leaning on it would
generate the disparity the constraint forbids.

Because I3 holds only narrowly and the pattern is a trend rather than a null-versus-effect
contrast, the trend is the finding, not any single row.

## Then why does `relationship` rise on Adult?

Because it is **not a pure proxy**. The planted column carries information about income
*only* through sex, by construction. Adult's `relationship` carries a great deal of income
information on its own:

| feature | P(y=1) spread across levels, **within** males | within females |
|---|---|---|
| `relationship` | **0.438** | **0.473** |
| `marital-status` | 0.398 | 0.433 |

*(levels with n ≥ 100)*

A feature that only encoded sex would show near-zero spread inside a single sex group.
These show almost half. `relationship` is one of the strongest income predictors in the
dataset **and** happens to determine sex — and the constrained model leans on it for the
first property, not the second.

That reframes document 06's observation without discarding it. The attribution shift is
real and reproducible. What it shows is a model reweighting toward a feature that predicts
the outcome well within each group — which is exactly what a cost-sensitive reweighting
scheme should do — and the sex-determining character of that feature is **incidental
rather than sought**.

> **This replacement explanation was itself tested and refuted — see
> [document 17](17-neither-explanation-survives.md).** Planting a column carrying
> independent outcome signal does *not* make the constrained model favour it either: the
> excess falls along the outcome dimension too. Both candidate mechanisms are now
> rejected by intervention, and the Adult attribution shift is unexplained. The negative
> finding below stands and was replicated.

## What is retracted, and what survives

| claim | status |
|---|---|
| Document 06's measurements (+151% on `relationship`, proxy shares) | **Stand.** Re-verified, unchanged |
| Document 06's *mechanism* — "selecting the best available reconstruction of the attribute it was forbidden to read" | **RETRACTED.** A planted reconstruction is used *less*, not more |
| Document 11's P3 *measurement* — Adult leaks 0.936, ACS 0.76–0.84, no overlap | **Stands.** Nine populations, unchanged |
| Document 11's reading of P3 as confirming the mechanism | **Withdrawn.** It confirmed a correlation the mechanism predicts, and so would several other explanations |
| Document 09's finding that deleting proxies is strictly dominated | **Stands.** An earlier version of this row explained it by the deleted features carrying outcome signal; that explanation is itself refuted in [document 17](17-neither-explanation-survives.md), so the finding stands unexplained rather than newly explained |

The course submission is unaffected: document 06 is a measurement document, and its
numbers are unchanged. The sentence quoted at the top is an interpretation, and the
retraction lives here rather than in the deliverable, which is frozen.

## A methodological note that changed the answer

The first version of this experiment explained the linear baseline **exactly** and the
randomized ensemble by **sampling** — which is what `run_shap` does, and is defensible
when reporting each model's own reliance. It is not defensible when the estimand is the
*difference between them*, because a systematic gap between two estimators lands directly
on the result.

It does:

| | excess, matched explainers | excess, mismatched |
|---|---|---|
| strength 0.50 | +0.0146 | **+0.0381** |
| strength 1.00 | −0.0086 | 0.0000 |

The mismatch inflates the excess by **0.0165** on average — enough to have shown a
positive excess at every strength, and enough to clear the I2 bar at the null. The
declining trend survives both, so the conclusion is robust; the *levels* are not. Had
this been run the obvious way, the table would have read as weak support for the very
mechanism it refutes.

## Limits

* **One population, one constraint, one base learner.** Alabama, demographic parity at
  ε = 0.01, logistic regression. The Wyoming smoke test showed the same direction more
  sharply, but n = 3,064 is where [document 15](15-arbitrariness-at-small-scale.md) says
  not to trust these methods.
* **Three seeds**, and KernelExplainer is a sampled estimator, so individual cells carry
  real error. The monotone trend across four strengths is the evidence, not any cell.
* **The planted column is deliberately a pure proxy.** That is what makes it a clean test
  of the stated mechanism, and it is also why it cannot speak to features that are both
  proxy and predictor. The obvious follow-up is to plant a column that carries independent
  outcome signal *and* determines sex, and vary the two properties separately — which
  would test the replacement explanation rather than merely being consistent with it.
* **The replacement explanation is not itself tested here.** That `relationship` carries
  large within-sex outcome signal is measured; that this is *why* the constrained model
  moves onto it is inference.
