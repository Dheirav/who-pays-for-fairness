# 19 — Levelling up, when you ask for it

**Individual work, beyond the course submission.** Tests the closing claim of
[document 05](../../docs/05-who-pays.md), which was stated and never checked.

## The claim

Document 05 found that every mitigation in the ablation closed the demographic-parity gap
partly by *withdrawing* favourable decisions. The total number of positive predictions
fell by 7.9% to 22.1%, and not one method closed the gap primarily by extending favourable
decisions to the disadvantaged group. It ended:

> "If you want the gap closed by levelling up, **that has to be part of the objective** —
> it will not happen by accident."

That is a claim about what is *expressible*. It is now tested.

## The construction, and what it is not

A single extra constraint: `P(h(x) = 1) ≥ target`, with the target set to the
unconstrained model's own selection rate — *don't hand out fewer favourable decisions than
the model you replaced*. It is stacked with `DemographicParity` and enforced in one game
rather than patched on afterwards (`src/levelling_up.py`).

**This is not a new method.** Agarwal et al. define constraints as linear in the
classifier's conditional moments, and a floor on the overall selection rate is exactly
that — a linear constraint on a moment whose conditioning event is the whole population.
It sits *inside* the base paper's framework. What is new is the question, not the
machinery, and the result below is a finding about objectives rather than about
algorithms.

## The result

Adult, five seeds, ε = 0.01 throughout.

| | baseline | ExpGrad-DP | **DP + floor** |
|---|---|---|---|
| accuracy | 0.8469 | 0.8282 | 0.8245 |
| **DP difference** | 0.1861 | **0.0178** | **0.0179** |
| disparate impact | 0.2996 | 0.8951 | **0.9148** |
| EO difference | 0.0949 | 0.2802 | 0.2625 |
| favourable decisions | 2784.8 | 2215.2 | **2767.4** |
| **change in the total** | — | **−20.5%** | **−0.6%** |

**Parity is satisfied to the same tolerance** — 0.0179 against 0.0178 — while the pie loss
falls from a fifth of all favourable decisions to essentially nothing.

The accuracy cost of adding the floor is **0.37 percentage points** (0.0187 → 0.0224
against baseline). That is the price of the whole thing.

## Who pays changes, which is the actual point

A variant that preserved the total while still taking from the same people would be
levelling down with compensation elsewhere. It is not:

| | ExpGrad-DP | **DP + floor** |
|---|---|---|
| share of the closure paid by the privileged group losing, in **rates** | 0.575 | **0.333** |
| the same, counted in **people** | 0.742 | **0.545** |
| favourable decisions **destroyed per one created** | **2.68** | **1.03** |

The rate-level share drops below 0.5, meaning most of the closed gap now comes from the
unprivileged group *gaining* rather than the privileged group losing. And the exchange
rate goes from **2.68 destroyed per one created to 1.03** — very nearly one for one.

Document 05's diagnosis was right, and so was its prescription: the reduction is agnostic
about *how* it satisfies a constraint because the constraint is all it is told. Tell it
one more thing and it satisfies that too.

## What this does not fix

**The DP/EO conflict is untouched.** EO difference is 0.2625 with the floor against 0.2802
without, both far above the baseline's 0.0949. That is consistent with
[document 14](14-why-the-conflict-is-unpredictable.md): the post-constraint EO violation
belongs to the constrained problem, and adding a selection-rate floor does not change what
demographic parity implies about error rates.

**It does not make the mitigation free.** It costs accuracy, slightly more than parity
alone, and it necessarily produces a *larger* model change than the plain constraint
because it must move more people to reach the same parity without withdrawing decisions.

**It is one dataset.** Adult, five seeds, one constraint, one base learner. The three
population-level documents in this folder exist because single-dataset findings are
exactly what should not be trusted, and this one has not been through that.

> **Addressed in [document 21](21-the-floor-replicates.md).** It has now been through that:
> nineteen populations, both protected-attribute arms. The finding **replicates** — the
> exchange rate fell in 19 of 19 populations — and the measurements above were re-verified
> exactly. Two corrections follow. **Adult is the extreme case, not the typical one:** its
> plain constraint destroys −20.5% of favourable decisions against a −6.1% mean elsewhere,
> and its exchange rate is 2.68 against 1.46, so quoting this page's numbers as
> representative overstates the typical case by roughly a factor of three. And **the floor
> does not merely protect the pie, it grows it**, in 18 of 19 populations — which is a
> larger change to the classifier than "don't shrink the pie" implies.

**The floor target is a choice.** Setting it at the unconstrained model's own selection
rate is defensible and makes the comparison to the ablation direct, but a regulator might
set it elsewhere, and nothing here explores that.

## Three bugs, and why the third is worth recording

Getting the constraint to bind took three fixes, each of which failed silently.

1. `_y_as_series` returns a bare ndarray in fairlearn 0.14 despite its name, so the
   failure surfaced inside the reduction rather than at the call site.
2. `UtilityParity.project_lambda` rebuilds its result with
   `pd.concat(keys=["+", "-"])`, which need not preserve `moment.index` order — so
   recombining per-moment vectors by position can attach a multiplier to the wrong
   constraint. Now aligned by label.
3. **Subclassing `Moment` rather than `ClassificationMoment`.**
   `Lagrangian._call_oracle` branches on that type: a `ClassificationMoment` gets
   `redY = 1 * (signed_weights > 0)`, so the oracle may flip labels toward satisfying the
   constraint, while anything else is refit against the original labels with reweighting
   only.

The third produced a model that fit without error, reported a **converged duality gap of
0.0**, and left demographic parity at **0.1844 against a baseline of 0.1867** — a
constraint that quietly did nothing while every diagnostic said it had succeeded. It was
caught by printing the multiplier vector and noticing it was near-uniform across all five
constraints, which is not what a solution looks like.

That is the same failure mode this project has now hit repeatedly and in four different
places: the ε bug in the epsilon sweep, two guards that could not report the outcome they
existed to detect, and now a constraint that converges to nothing. **In every case the
code ran, produced plausible numbers, and was wrong.**

## Where this leaves document 05

| claim | status |
|---|---|
| Every ablation method shrank the pie, 7.9%–22.1% | **Stands.** Re-verified |
| Levelling down is invisible in the fairness metrics | **Stands** |
| "If you want levelling up, it has to be part of the objective" | **Confirmed.** Put it in the objective and you get it, for 0.37 accuracy points |
