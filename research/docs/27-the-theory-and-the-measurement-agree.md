# 27 — The theory's conditions never hold, and its direction is still right

**Individual work, beyond the course submission.** **Post-hoc**: the directions were known
before this was written, so this is a correspondence check between a published theory and
existing measurements, not a prediction that could have failed.

Tests whether [arXiv:2603.06901](https://arxiv.org/abs/2603.06901), *Fairness May Backfire:
When Leveling-Down Occurs* (March 2026), predicts what
[document 23](23-the-selection-rate-sets-the-direction.md) measured. That paper proves the
direction is distribution-dependent in the attribute-blind regime — which is this project's
regime throughout — and so anticipates document 22 and 23's central claim theoretically.
The question this document answers is whether their *conditions* and our *rule* are the
same thing.

## What their condition is

For the attribute-blind regime, Theorem 3 defines

```
zeta(x) = (eta(x) - c) / nu_DM(x)
```

with `eta` the score, `c` the unconstrained threshold, `nu_DM` the constraint gradient —
positive on the **advantaged-like** region A, negative on the **disadvantaged-like** region
B. Over each region's extrema:

* `A_max <= B_min` → every group's rate weakly **falls** (levelling down)
* `B_max < A_min` → every group's rate weakly **rises** (levelling up)

For demographic parity the gradient is the group density ratio, so `nu` is estimable from a
probe predicting the protected attribute from the features. That makes the theorem
checkable, which is worth doing because **the paper contains no experiments** — zero
occurrences of "experiment", "dataset", "Adult" or "COMPAS" in its full text.

## Result 1 — the conditions are never satisfied

**Neither strict condition holds on any of the 26 populations.** Not one.

The reason is structural rather than incidental: `zeta` is a ratio that diverges as
`nu -> 0`, and every real dataset has points arbitrarily close to `nu = 0`. So the empirical
sup and inf of the two regions always overlap, by enormous margins — on Adult, A spans
[−139, 4.1] while B spans [−39, 6662].

The conditions are **sufficient, not necessary**, and the theorem is silent on every
population measured here. As stated, it cannot be applied to data.

## Result 2 — a relaxed ordering version does predict the direction

Replacing the unattainable extrema with 5th/95th percentiles, and comparing the two regions'
upper quantiles:

| rule | agrees with the measured direction |
|---|---|
| `A_max_q > B_max_q` → up (the relaxed theory condition) | **24 / 26** |
| `median(A) > median(B)` → up | **25 / 26** |
| selection rate > 0.5 → up (document 23's rule) | **25 / 26** |

Both misses are Vermont and Connecticut — the two smallest effects in the set, at +0.29%
and +0.56%, and Vermont is the population [document 12](12-intersectional-across-populations.md)
excluded for having essentially no baseline disparity to remove.

**The quantile choice was not pre-registered.** 5%/95% was tried first and the median added
afterwards; the median scores marginally better. Nothing here rests on which is used, and
both are reported because choosing between them after the fact would be selection.

## Result 3 — the selection rate is a proxy for their structural quantity

This is the one that matters.

```
r(selection rate, A_max_q - B_max_q) = +0.935
```

The two rules agree with each other on **25 of 26** populations.

So the theory's structural condition — an ordering of score-region quantiles, requiring the
joint distribution of the score and the group probe — and this project's empirical rule —
what fraction of applicants the system currently approves — **are measuring nearly the same
thing**.

## What this settles

| question | answer |
|---|---|
| Is the conditionality claim ours? | **No.** Established theoretically and independently, five months earlier |
| Does their theorem predict our data? | **Not as stated** — its conditions hold on 0 of 26 populations |
| Is its *direction structure* right? | **Yes**, once relaxed to an ordering: 24–25 of 26 |
| Is our rule a different phenomenon? | **No** — it proxies their quantity at r = +0.935 |
| Is our rule usable where theirs is not? | **Yes.** Theirs needs the joint score-and-group distribution; ours needs a historical approval rate |

The honest position: **their theory explains why, ours says how to tell, and they agree.**
Independent theory and independent measurement converging is stronger evidence than either
alone — and neither was derived from the other, which is checkable from the commit history
and their publication date.

## It also explains document 26

[Document 26](26-the-derivation-does-not-earn-its-keep.md) derived a curvature account,
predicted the crossover would sit at the mode of the score density, cleared its bars and was
beaten by a constant. The reason is now visible: the governing condition is an **ordering
relation between two regions**, not a scalar threshold on one distribution. A single-number
rule was the wrong object. The derivation had the right instinct — curvature of the score
distribution — aimed at the wrong quantity.

## Limits

* **Post-hoc throughout.** Nothing here could have failed in a way that surprised us.
* **Five seeds per population**, matching the rest of the project. An earlier version of
  this document ran a single seed and reported r = +0.927; averaging over five moves it to
  +0.935 and leaves every rule's score unchanged (24/26, 25/26, 25/26), so the single-seed
  figure was not a fluke.
* **`nu` is estimated** by a logistic probe rather than known. A better probe would change
  the numbers, though the probe is the same one used for leakage elsewhere.
* **The relaxation is ours, not theirs.** They make no claim about quantiles; showing their
  strict conditions fail is a finding about applicability, not a refutation of the theorem,
  which is stated over population distributions rather than samples.
* **Two misses**, both on near-zero effects.
