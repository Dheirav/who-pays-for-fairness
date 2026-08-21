# 12 — Intersectional fairness across ten populations

**Not in the initiation document, and beyond the course submission.** This is to
[document 07](../../docs/07-intersectional.md) what [document 11](11-replication-across-populations.md)
is to documents 05 and 06: a test of whether the finding is about the method or about
Adult.

## Why document 07 could not settle the question

Document 07 reported that constraining demographic parity on `sex` takes the sex gap
from 0.1897 to 0.0197 while the Sex × Race gap stays at 0.1776 — a model that looks
**9.0× fairer than it is**. That is fairness gerrymandering (Kearns et al., 2018), and the
reason it gets past an audit is the other half of the same story: Maheshwari et al. (2023)
report that these methods level down more at the intersection and that the harm "often goes
unnoticed in the overall performance of the model". Neither observation originates here.
On Adult it was also measured under bad conditions:

* **5 of 10 subgroups were too small to support a rate estimate**, and Female × Other
  had *no positive labels at all*.
* Only one population, so nothing distinguished "the constraint does this" from
  "Adult is like this".

ACS fixes the first problem — 3,064 to 45,222 rows per population, nine of them — and
supplies the second. Three arms (unconstrained, constrained on sex, constrained on the
Sex × Race intersection), three seeds, ten populations.

**Headline: the finding replicates, and Adult understated it.** But it holds only under
a condition Adult could not have revealed, and that condition is the interesting part.

---

## Finding 1 — gerrymandering replicates, and is worse elsewhere than on Adult

How much larger the Sex × Race gap is than the sex gap the ablation table would report,
after constraining on sex:

| population | gerrymandering ratio |
|---|---|
| MS | **13.2×** |
| OR | **12.9×** |
| AL | **10.8×** |
| **Adult** | **9.0×** |
| NM | 6.0× |
| VT | 1.4× |
| ND | 1.1× |
| WV | 1.2× |
| WY | 1.0× |
| UT | 1.0× |

Adult is **not** the extreme case. Three populations exceed it. The finding is not an
artifact of a 1994 dataset with unusual racial composition — where it appears, it
appears harder than it did on Adult.

## Finding 2 — but it needs a minority to hide in

The ten populations split cleanly, and the splitting variable is not the one this
project has been repeatedly burned by.

Share of the pre-existing intersectional gap that the **sex** constraint actually
removes, against how racially heterogeneous the population is:

| population | non-modal race share | baseline Sex × Race gap | after sex constraint | removed |
|---|---|---|---|---|
| WV | 5.5% | 0.116 | 0.012 | **89%** |
| WY | 8.7% | 0.157 | 0.029 | **81%** |
| ND | 9.1% | 0.147 | 0.025 | **83%** |
| UT | 10.5% | 0.236 | 0.034 | **86%** |
| OR | 13.6% | 0.269 | 0.285 | **−6%** |
| Adult | 14.0% | 0.315 | 0.178 | 44% |
| AL | 23.8% | 0.280 | 0.189 | 32% |
| NM | 26.9% | 0.207 | 0.180 | 13% |
| MS | 34.0% | 0.258 | 0.187 | 27% |

```
r(minority share, share of gap removed)  = −0.671
r(population size, share of gap removed) = −0.371
r(minority share, population size)       = +0.101   ← not confounded this time
```

> Below 12% minority the sex constraint removes **85%** of the intersectional gap.
> At or above 12% it removes **22%**.

**This is the first correlation in the project that is cleanly identified.** In
document 11 the two candidate explanations for P1 correlated at r = +0.794, so neither
could be read alone. Here they correlate at +0.101, and the diversity explanation beats
the size explanation on its own terms.

The mechanism follows: gerrymandering requires subgroups to gerrymander *between*. In a
population that is 95% one race, Sex × Race is very nearly Sex, so a constraint on sex
necessarily fixes both — not because the method is doing anything intersectional, but
because there is no intersection to speak of. **Where the population is genuinely
diverse, the sex constraint leaves roughly four fifths of the intersectional gap
standing.** Adult sits mid-range at 14.0% and therefore showed a middling version of an
effect that is much sharper at the ends.

Oregon is worth naming: constraining sex made its intersectional gap **worse**
(0.269 → 0.285). Fixing the marginal actively damaged the interior.

**VT is excluded from the correlations above.** Its baseline intersectional gap is
0.012 — essentially nothing to remove — so a percentage of it is the same
small-denominator artifact that broke the first version of P2 in document 11. It is
excluded on that stated ground and reported in the table regardless.

## Finding 3 — constraining on the intersection does fix it

The same algorithm, given the intersection as its sensitive feature, removes
**74–88% of the gap in every population**, including the four where the sex constraint
achieved nothing:

| population | baseline gap | after sex | after Sex × Race |
|---|---|---|---|
| OR | 0.269 | 0.285 | **0.069** |
| AL | 0.280 | 0.189 | **0.032** |
| MS | 0.258 | 0.187 | **0.044** |
| Adult | 0.315 | 0.178 | **0.048** |
| NM | 0.207 | 0.180 | **0.045** |

This is not a new algorithm — fairlearn's reductions accept a multi-valued sensitive
feature directly. The contribution is the measurement, and the measurement says the
fix is available and nobody is applying it.

It costs roughly **twice to three times** the accuracy of the sex constraint:

| population | cost of sex constraint | cost of intersectional constraint |
|---|---|---|
| Adult | −0.017 | −0.034 |
| AL | −0.014 | −0.045 |
| MS | −0.010 | −0.036 |
| UT | −0.063 | −0.079 |

## Finding 4 — the worst-off subgroup is usually a minority *man*

After constraining on sex, the lowest selection rate of any measurable subgroup belongs
to:

| population | worst-off subgroup | rate |
|---|---|---|
| MS | **Male × Black** | 0.058 |
| Adult | **Male × Black** | 0.076 |
| AL | **Male × Black** | 0.103 |
| NM | Male × Amer-Indian | 0.128 |
| OR | Male × Two-or-more | 0.222 |

**In five of the ten populations the worst-off group after a sex constraint is a
minority man**, and in three of them it is Black men specifically — the same result
document 07 found on Adult, reproduced independently. A constraint that treats "male"
as the privileged category leaves the men it was not thinking about at the bottom. The
remaining populations put Female × White or Male × White last, which is what a
near-homogeneous population makes almost inevitable.

## Finding 5 — a methodological warning ACS makes unavoidable

`gap_inflation` is the share of the headline ten-cell gap contributed by subgroups too
small to support the estimate. On Adult it is **0.04**. On ACS it ranges **0.23 to
0.85**, because ACS splits race into nine codes where Adult uses five — American
Indian, Alaska Native and AIAN-combined are separate levels (RAC1P 3, 4, 5).

| population | gap_inflation, baseline |
|---|---|
| ND | 0.72 |
| WY | 0.56 |
| VT | 0.57 |
| AL | 0.39 |
| Adult | **0.04** |

In North Dakota and Wyoming, **most of the headline intersectional gap is arithmetic on
cells of one to ten people.** An intersectional analysis that prints a subgroup heatmap
without reliability gating is, on populations like these, mostly reporting sampling
noise — and it will look like a dramatic finding.

Every number in documents 07 and 12 is therefore quoted over reliable subgroups only.
`gap_inflation` is comparable *within* a dataset and not *across* Adult and ACS, since
the granularity of the race coding differs; that is a property of the data, not a
result.

`RAC1P` was deliberately **not** collapsed to Adult's five levels, even though that
would make the two comparable, because it is also a model feature — recoding it would
change the inputs and invalidate the committed sweep results in document 11.

---

## What this changes in documents 01–11

| document | status |
|---|---|
| 07 (intersectional) | **Strengthened, and scoped.** The gerrymandering result replicates and is worse than Adult in three populations. It now carries a stated condition: it requires a substantial minority, and Adult at 14% sits mid-range |
| 11 (replication) | Unaffected; different predictions |
| others | Untouched |

**The course submission remains unaffected.** `bias_mitigation_report.pdf` and
`bias_mitigation_plan.pptx` quote the Adult intersectional result, which is
re-verified here and, if anything, conservative.

## Limits

* **Three seeds per population.** The arm-to-arm differences are far larger than the
  seed-to-seed spread, but the per-population percentages carry real noise.
* **The 12% threshold is descriptive, not estimated.** Ten populations cannot locate a
  breakpoint; it is a summary of where these ten happen to fall, and the underlying
  relationship is presumably continuous.
* **One year, one task, one intersection.** Sex × Race only, ACSIncome 2018.
* **"Minority share" is a crude summary of heterogeneity.** A population with one large
  minority and one with three medium ones score alike and need not behave alike.
* **Finding 4 is about which subgroup ranks last, not about how much it lost.** It says
  the sex constraint does not protect minority men; it does not establish that the
  constraint made them worse off than they were.
