# 36 — Not a property of linear models

**Individual work, beyond the course submission.** **Post-hoc and labelled as such**: no
prediction was registered. This is a robustness check against a cheap objection, and it uses
document 23's bars because they were already fixed.

## The objection

Almost every result in this project uses logistic regression. "Levelling down is a property
of linear models, and your crossover is a property of a linear decision boundary" is a
one-line reviewer comment that currently has no answer.

## The design

Alabama's income-cutoff sweep re-run with `hist_gradient_boosting` — a boosted-tree learner
that is non-linear, fits interactions the logistic model cannot express, and honours
`sample_weight`, which is the hard requirement: the reduction mitigates by reweighting and
refitting, so a learner that ignored the weights would silently return an unmitigated model.

**Four cutoffs, not six.** The $10,000 and $100,000 arms were not run. The first attempt at
this sweep took 33 minutes for a single arm on a machine oversubscribed two-to-one — the
reduction refits the learner up to fifty times per seed, for each of three arms, at five
seeds — and it was stopped to free cores for higher-value work. The four that were run span
selection rates 0.107 to 0.765, which covers the crossover; the two omitted arms are the
extremes that document 23's own exclusion rule discards anyway.

## The result

| selection rate | boosted trees | logistic regression |
|---|---|---|
| 0.765 / 0.760 | **+0.92%** | +0.80% |
| 0.601 / 0.598 | **+1.72%** | +0.98% |
| 0.255 / 0.252 | **−7.00%** | −2.34% |
| 0.107 / 0.099 | **−21.14%** | −22.05% |

**T0** HOLDS — rates span 0.107–0.765, monotone in the cutoff.
**T1** HOLDS — **r = +0.902**, sign flips across the range.
**T2** HOLDS — partial **r = +1.000** holding the baseline parity gap fixed.
**T3** HOLDS — exchange rate **r = −0.944**, from 2.38 destroyed per created at the lowest
rate to 0.78 at the highest.

**The crossover bracket is 0.255–0.601, against logistic regression's 0.252–0.598 on the same
four arms.** It does not move.

## What this establishes

The objection does not hold. The relationship, the sign change and the location of the
crossover all survive replacing a linear model with a boosted-tree ensemble. Levelling down
is not an artifact of a linear decision boundary.

Note also that **no arm was excluded here**, where two were under logistic regression: the
boosted learner produces larger baseline parity gaps (0.085–0.122 against 0.074–0.129 on the
overlapping arms) because it fits the group structure more sharply. A stronger learner is
*more* unfair to begin with, not less, and has correspondingly more to lose.

## What it does not establish

**Magnitude, again.** At a selection rate of 0.255 the boosted model loses 7.00% of its
favourable decisions where the logistic model loses 2.34% — three times as much. At 0.107 the
two nearly coincide, −21.14% against −22.05%. So the learner is now the fourth manipulation
that leaves the direction and the crossover intact while moving the magnitude around, joining
the route ([document 32](32-the-rate-not-the-task.md)), the tolerance
([document 34](34-the-crossover-survives-the-tolerance.md)) and the criterion
([document 33](33-the-rule-does-not-survive-equalized-odds.md)).

**One learner, four arms per state.** This is a robustness check, not a second study, and it
is worth exactly what a robustness check is worth: it removes an objection rather than adding
a finding.

## It holds in every population tested

Oregon, Connecticut, Kentucky and South Carolina were added afterwards.

| state | r | sign flip |
|---|---|---|
| Alabama | +0.902 | yes |
| Oregon | +0.989 | yes |
| Connecticut | **+0.923** | **yes** |
| Kentucky | +0.935 | yes |
| South Carolina | +0.986 | yes |

**Five of five.** This is the only one of the project's four robustness tests that holds in
every population, and the correlations are the tightest of any sweep here.

Connecticut is worth singling out. Under logistic regression it is the exception to
everything — no sign change, a spread of a third of a percentage point, and a failure at every
tolerance ([document 34](34-the-crossover-survives-the-tolerance.md)). Under boosted trees it
**flips sign like every other state**. The stronger learner produces a larger baseline parity
gap and therefore has enough to remove for the effect to appear at all, where the linear model
on that population had almost nothing to work with. That supports the reading that
Connecticut's exceptionalism is a shortage of movement rather than a contrary direction.
