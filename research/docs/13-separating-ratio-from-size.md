# 13 — Separating group ratio from population size

**Not in the initiation document, and beyond the course submission.** This document
resolves the open question in [document 11](11-replication-across-populations.md), and
in doing so corrects that document's correction.

## The question left open

Document 11 found that P1's rate-to-people formula fails, and proposed a mechanism:
**cross-flow**, the share of individual movement running against the intended transfer.
It then dismissed group ratio as a confound, on the grounds that ratio and population
size correlate at r = +0.794 in the sex arm and Adult is both the largest population and
the most lopsided.

That dismissal could not be tested with the data available, because no population had a
high group ratio *and* a large sample. Building one required protecting a different
attribute.

## The design, fixed before the results existed

Protecting `RAC1P` on the same nine states spans a group ratio of **1.94 to 24.98**, and
inverts the confound — the racially homogeneous states are also the small ones, so
r(ratio, n) = **−0.567** there against **+0.794** on sex. Pooling gives 19 arms in
which the two vary nearly independently.

`src/experiments/analyse_arms.py` was written and committed **before the race sweep
finished**, with three predictions and their thresholds fixed in the docstring. This was
deliberate: document 11's error came from choosing what to correlate after seeing what
correlated, and the same person cannot be trusted to score their own test afterwards.

Dry-running it against partial data caught two faults worth recording. It printed a
confident verdict from **two of nine** race populations, and its verdict logic did not
implement its own stated prediction — it tested whether size *beat* ratio rather than
whether ratio *vanished*, and scored a pass with ratio sitting at +0.473. Both were
fixed before any complete result existed.

## The results

**A1 — HOLDS.** Pooled r(log ratio, n) = **−0.180**, under the 0.3 ceiling. The confound
is broken; partial correlations are interpretable.

**A3 — HOLDS.** Cross-flow is the strongest single predictor of the error *within each
arm separately*: **+0.885** on sex, **+0.689** on race. Not an artifact of pooling.

**A2 — PARTIAL, and this is the interesting one.**

| pooled, 19 arms | raw | partial |
|---|---|---|
| log group ratio vs error | +0.522 | **+0.548** (controlling for size) |
| population size vs error | −0.667 | **−0.683** (controlling for ratio) |
| cross-flow vs error | +0.778 | — |

A2 predicted ratio's partial correlation would vanish once size was held fixed. **It did
not.** At +0.548 it is barely changed from its raw value. Group ratio predicts the
formula's error independently of population size.

## What was actually wrong, and it was mine

Document 11 called group ratio **a confound**. That is the wrong word, and the mistake
is substantive rather than terminological.

Controlling for cross-flow instead of for size:

```
log ratio → error, controlling for cross-flow  = −0.038   (raw +0.522)
size      → error, controlling for cross-flow  = −0.306   (raw −0.667)

log ratio → cross-flow, controlling for size   = +0.787
size      → cross-flow, controlling for ratio  = −0.776
```

Group ratio's effect on the error collapses to **essentially nothing** once cross-flow
is held fixed, while its effect *on cross-flow* is strong and independent of size. That
is not the signature of a confound. It is the signature of a **cause acting through a
mediator**:

```
  group ratio  ─┐
                ├─→  cross-flow  ─→  formula error
  small sample ─┘
```

Both quantities independently raise cross-flow; cross-flow is what breaks the formula.
Document 11 conflated "acts through a mediator" with "is spurious", and those are
different claims. Its mechanism — cross-flow — was right, and is now much better
supported than it was. Its dismissal of group ratio was wrong.

## The sign that flipped twice

Worth setting out plainly, because it is the most instructive thing in this project:

| evidence | r(log ratio, error) | what I concluded |
|---|---|---|
| 9 states, sex arm | **+0.364** | error rises with group inequality |
| + Adult (10 populations) | **−0.557** | the first reading was an artifact; ratio is a confound |
| + race arm (19 arms, 10 populations) | **+0.522** | the first reading was directionally right |

The original reading was **correct**, and I corrected it into an error. Adult sits at
2.08 with a huge sample and a very low error, and with only ten populations it had
enough leverage to invert the sign by itself. Document 11 recorded that inversion as a
lesson about reading nine points without the tenth. The real lesson is stronger: ten
points were not enough either, and the confident correction was worse than the tentative
original, because it was stated with more certainty on no better evidence.

What made the difference was not more data of the same kind — it was data built
specifically to break the confound.

## What this changes

| document | status |
|---|---|
| 05 (who pays) | Adult measurements stand. Its replication note is accurate: the cross-flow condition is confirmed and strengthened |
| 11 (P1) | **The mechanism stands; the dismissal of group ratio is retracted.** See the amended correction section in that document |
| 12 (intersectional) | Unaffected |

**P1, restated for the third and hopefully last time:**

> The rate-to-people conversion is exact arithmetic when the mitigation performs a clean
> transfer. It degrades in proportion to cross-flow, and cross-flow rises both as the
> groups become more unequal in size and as the sample gets smaller — independently.
> Compute the cross-flow share to know whether to trust the conversion; group ratio and
> sample size predict it, but neither replaces measuring it.

**The course submission remains unaffected.** The P1 formula appears in neither
`bias_mitigation_report.pdf` nor `bias_mitigation_plan.pptx`.

## Limits

* **The race arm splits White against everyone else**, which is not a defensible claim
  about racial fairness and is not offered as one. It exists to vary two counts in a
  formula whose only inputs are counts. Its group *labels* carry no weight in any
  conclusion here; only the counts do.
* **Nineteen populations, three seeds each on the race arm.** Partial correlations on 19
  points are not precise, and the thresholds (0.3) were fixed by argument rather than
  estimated.
* **Mediation is inferred from partial correlations, not from an intervention.** The
  ordering ratio → cross-flow → error is consistent with the data and with the
  mechanism, but nothing here randomised anything.
* **One task, one year.** ACSIncome 2018 throughout.
