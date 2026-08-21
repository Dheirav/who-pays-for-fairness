# 07 — Intersectional: does fixing sex leave a Sex × Race subgroup behind?

**Not in the initiation document.** This is the project's third contribution, and the
one with the clearest practical consequence.

## The question

Every method in document 04 is constrained on `sex` alone, and every metric in
document 01 compares exactly two groups. That is the field's default. Kearns et al.
(2018) identify its failure mode — **fairness gerrymandering**: a model can satisfy a
constraint on each marginal while the *cells inside* those marginals stay badly
unfair, because no marginal ever inspects a cell. Maheshwari et al. (2023) add the
part that makes it hard to catch: these methods level down *more* at the
intersection, and the damage "often goes unnoticed in the overall performance of the
model". Kearns says the subgroup can be left unfair; Maheshwari says the dashboard
will not show it. Both are measured here on Adult; neither observation is ours.

Three arms, identical splits, 3 seeds:

1. **baseline** — no constraint.
2. **expgrad_dp (sex)** — the standard setup, and the ablation's best DP performer.
3. **expgrad_dp (sex × race)** — the same algorithm, constrained on the intersection.
   Fairlearn's reductions accept a multi-valued sensitive feature directly, so this is
   not a new algorithm. The contribution is the measurement, not the method.

## Finding 1 — the measurement problem comes first

Sex × Race splits the test set into ten subgroups spanning three orders of magnitude:

| subgroup | n | positive labels |
|---|---|---|
| Male × White | 8,110 | 2,616 |
| Female × White | 3,576 | 435 |
| Female × Black | 650 | 42 |
| Male × Black | 643 | 131 |
| Male × Asian-Pac-Islander | 267 | 94 |
| Female × Asian-Pac-Islander | 123 | 21 |
| Male × Amer-Indian-Eskimo | 73 | 14 |
| Male × Other | 65 | 7 |
| Female × Amer-Indian-Eskimo | 39 | **3** |
| Female × Other | 21 | **0** |

**Five of the ten cannot support a rate estimate.** `Female × Other` has *no positive
labels at all*, so its true-positive rate is undefined by division — not by convention.
`src/metrics.py` returns NaN there rather than 0, which is why it shows as blank rather
than as a confident "this group has 0% TPR".

A ten-cell heatmap printed without this caveat is reporting sampling noise as
discrimination. The quantitative version:

| arm | gap over all 10 | gap over the 5 measurable | inflation |
|---|---|---|---|
| baseline | 0.3541 | 0.3145 | 0.0396 |
| expgrad_dp (sex) | 0.2207 | 0.1776 | 0.0431 |
| expgrad_dp (sex × race) | 0.1606 | **0.0481** | **0.1124** |

For the intersectionally-constrained arm, **70% of the apparent gap is contributed by
subgroups too small to measure.** Quoting 0.161 there instead of 0.048 would overstate
the residual unfairness by more than 3×.

Every gap quoted below is the **reliable** one, and the widest reliable gap in each arm
was checked for overlapping 95% Wilson intervals. In all three arms the intervals do
**not** overlap — these are real differences, not artifacts.

## Finding 2 — bias hides at the intersection, and the marginal conceals it

| arm | accuracy | **sex** DP gap | **Sex × Race** gap (reliable) | ratio |
|---|---|---|---|---|
| baseline | 0.8465 | 0.1897 | 0.3145 | 1.7× |
| **expgrad_dp (sex)** | 0.8295 | **0.0197** | **0.1776** | **9.0×** |
| expgrad_dp (sex × race) | 0.8129 | 0.0164 | 0.0481 | 2.9× |

**This is the headline.** Constraining on sex takes the sex gap from 0.190 to 0.020 —
a 90% reduction, essentially solved, and the number the ablation table reports. At the
intersection, the same model still carries a gap of **0.178, nine times larger than
the number on its own dashboard.**

The concrete cells, seed 0, after sex-only mitigation:

| subgroup | selection rate | 95% CI |
|---|---|---|
| Male × Asian-Pac-Islander | 0.307 | [0.255, 0.365] |
| Male × White | 0.177 | [0.169, 0.186] |
| Female × White | 0.151 | [0.140, 0.163] |
| Female × Black | 0.102 | [0.081, 0.127] |
| **Male × Black** | **0.092** | [0.072, 0.117] |

Black men are selected at 9.2%, Asian men at 30.7% — a **3.3× ratio**, in a model
whose sex-level demographic parity difference is 0.028. An auditor checking the
protected attribute the model was trained to protect would see a near-perfect score.

## Finding 3 — the sex constraint moved the worst-off group from Black women to Black men

| arm | worst-off subgroup | its selection rate |
|---|---|---|
| baseline | Female × Black | 0.052 |
| expgrad_dp (sex) | **Male × Black** | 0.076 |
| expgrad_dp (sex × race) | Female × White | 0.157 |

Before mitigation, Black women were at the bottom. The sex constraint raised women's
selection rates across the board — including Black women — but **Black men were
protected by no constraint at all**, and ended up at the bottom instead.

This is fairness gerrymandering in its exact form. Nothing was done *to* Black men; the
constraint simply had nothing to say about them, and equalising the sex marginal while
race went unconstrained left them as the residual. A group can be made worst-off by a
fairness intervention without ever appearing in it.

## Finding 4 — the intersectional constraint works, and it is the only arm that lifts the floor

Constraining on Sex × Race cuts the reliable intersectional gap from 0.178 to **0.048**
(a 73% reduction) for **1.7 additional accuracy points** (0.8295 → 0.8129).

More interestingly, and in contrast to every result in document 05, it is the only arm
where the **worst-off subgroup's absolute selection rate rises substantially**: 0.052 →
0.076 → **0.157**, tripling from the baseline. Constraining the intersection did not
merely redistribute between two large groups; it lifted the floor.

That is worth stating plainly because document 05 is otherwise a catalogue of levelling
down. The mechanism differs: with ten groups rather than two, the constraint cannot
satisfy itself by trimming one large group's numerator, because doing so would open
gaps against the eight it is not trimming.

## Relation to the base paper

Agarwal et al. (2018) is **not** limited to binary attributes — its formulation admits
multiple protected groups, and `fairlearn` implements that, which is why arm 3 required
no new algorithm. So this document does not identify a gap in the method.

What it identifies is a gap in **practice**. The paper's Adult experiments, the
initiation document, this project's own ablation, and the overwhelming majority of
applied fairness work all constrain a single binary attribute. This measurement shows
what that costs: a model can be declared fair on the attribute it was constrained on
while carrying a 9× larger gap one level down, and the group it leaves at the bottom
can be one that the intervention never mentioned.

One caution the paper *does* raise is relevant here: GridSearch scales poorly as the
number of protected groups grows, since the λ grid grows with it. That is why arm 3
uses ExponentiatedGradient rather than GridSearch — a practical consequence of the
paper's own analysis, encountered directly.

## Limits

* 3 seeds, not 5, because each seed fits two ExponentiatedGradient models.
* Race is used as recorded in the 1994 census extract, with five categories of very
  unequal size and an "Other" bucket. These are administrative categories, not natural
  kinds, and the smallest of them are why half this analysis is unmeasurable.
* `MIN_RELIABLE_DENOMINATOR = 30` is the conventional rule-of-thumb floor for a
  proportion estimate. The flag matters more than the exact cutoff, and the Wilson
  interval is reported for every subgroup regardless so a reader can apply their own
  threshold.
