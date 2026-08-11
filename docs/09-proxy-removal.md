# 09 — Proxy removal: does deleting the leaky feature remove the leak?

**Not in the initiation document.** This is the causal follow-up to document 06.

## The question

Document 06 established that the demographic-parity constraint makes the model rely
*more* on `relationship` — the feature whose Husband/Wife levels determine sex
outright for 45.9% of the dataset. The natural response from anyone who reads that
finding is: **then delete the column.**

Document 06 cannot answer whether that works, because it only observed where
attribution sat. This experiment deletes the feature and re-measures, which turns an
observation into something closer to a causal claim.

Each round removes one more feature, in the order document 06 ranked them (most
sex-determining first), so every round is the strongest available "just delete the
proxy" response to the previous one. Three seeds.

## The measurement that matters: leakage

The key addition is `FairnessDataset.attribute_leakage()` — a probe that tries to
predict `sex` from the *remaining* features and reports ROC AUC. This is the direct
measurement that SHAP can only approach sideways. If a model can still recover the
protected attribute at high AUC after you delete a proxy, then you removed a column
and not the information, and "the model does not use sex" is false in every sense
that matters.

## Results

| removed | features | **sex leakage AUC** | baseline acc | baseline DP | ExpGrad acc | ExpGrad DP | top feature |
|---|---|---|---|---|---|---|---|
| nothing | 11 | **0.934** | 0.8465 | 0.1897 | **0.8295** | **0.0197** | marital-status |
| −`relationship` | 10 | **0.868** | 0.8463 | **0.2054** | 0.8026 | 0.0172 | marital-status |
| −`relationship`, `marital-status` | 9 | 0.804 | 0.8171 | 0.1014 | 0.7946 | 0.0164 | capital-gain |
| −… , `occupation` | 8 | 0.691 | 0.8133 | 0.0932 | 0.7852 | 0.0182 | capital-gain |
| −… , `hours-per-week` | 7 | **0.625** | 0.8080 | 0.0761 | 0.7863 | 0.0186 | capital-gain |

Chance leakage is 0.500; the majority-class rate is 0.675.

## Finding 1 — deleting the worst proxy barely removes the information

Removing `relationship` — the single feature that *determines* sex for nearly half the
population — moves leakage from **0.934 to 0.868**. The model can still recover sex
almost as well as before.

That is because the information was never in that column alone. It is distributed
across `marital-status`, `occupation`, `hours-per-week` and the rest, and deleting any
one of them leaves the others. To push leakage down to 0.625 you must delete **four of
eleven features** — and at that point the probe's accuracy (0.676) is indistinguishable
from the majority-class rate (0.675), meaning you destroyed the feature set to get
there.

## Finding 2 — deleting the proxy made the unmitigated model *more* unfair

| | baseline DP |
|---|---|
| all features | 0.1897 |
| −`relationship` | **0.2054** |

The demographic parity gap **got worse**, by 8%, when the most sex-revealing feature
was removed. Attribution simply moved to `marital-status`, which remained the top
feature by attribution in both rounds.

This is the whack-a-mole result stated at its sharpest: the intervention that feels
most obviously correct — deleting the feature that encodes the protected attribute —
made the outcome worse on the metric it was meant to improve. Document 06 predicted
this would happen, from the observation that mitigated models relocate attribution
rather than shedding it; here it happens without any mitigation at all.

## Finding 3 — feature removal is strictly dominated by using the constraint

This is the practical conclusion.

| approach | accuracy | DP |
|---|---|---|
| **ExpGrad-DP on the full feature set** | **0.8295** | **0.0197** |
| Delete 4 proxies, no mitigation | 0.8080 | 0.0761 |

Deleting four features gives you **worse fairness and worse accuracy** than simply
applying the constraint and leaving the data alone. There is no axis on which the
deletion wins.

Worse, deletion makes the constraint *more expensive* to apply. ExpGrad's accuracy
falls from 0.8295 to 0.8026 as soon as `relationship` goes, because the reduction now
has less signal to work with while still being asked to equalise selection rates. The
cost of mitigation goes up and the benefit does not.

## What this means

**Fairness through unawareness fails, and it fails progressively rather than at a
threshold.** Removing the protected attribute does not work (document 02). Removing
the best proxy does not work either, and backfires. Removing four features finally
suppresses the leak, at a cost that a constraint-based method beats outright while
leaving every feature in place.

The reason to prefer in-processing over feature deletion is usually stated as
convenience. This is the stronger version: **deletion does not achieve the thing it is
supposed to achieve**, and the constraint does.

## Relation to the base paper

Agarwal et al. do not discuss feature selection; the reduction treats the feature set
as given. Nothing here contradicts them. What this adds is a defence of their approach
that the paper does not make for itself: the obvious cheaper alternative — drop the
offending columns — is measurably worse on both axes at once, and this is the
measurement showing it.

## Limits

* Three seeds. The direction is consistent across all three at every round; the
  `relationship`-removal effect on baseline DP is the smallest and would benefit from
  more.
* The removal order is fixed rather than greedy. A greedy search that re-ranked
  proxies after each removal might suppress leakage with fewer deletions — though it
  would still be deleting features to chase information that is distributed.
* The leakage probe is a linear model, so 0.625 is an upper bound on how much a linear
  attacker recovers, not on what any model could.
