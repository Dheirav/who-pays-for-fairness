# 44 — How much, and where: two concessions put to a test instead of assumed

**Individual work, beyond the course submission.** Both predictions were fixed in
`src/experiments/analyse_magnitude.py` and committed before either analysis ran. Both use arms
already on disk, which makes the pre-registration matter *more* rather than less: the data
existed, so nothing but a committed prediction stood between the model and the answer.

This project has been conceding two things without testing either. A concession that was never
attempted is weaker than one that was, and a referee is entitled to ask why not.

---

## M — magnitude, and it is half predictable

The claim in every draft so far: *the selection rate tells you which way, never how much.* The
model tested is the one a practitioner would guess — **the further a task sits from its own
crossover, the larger the effect.**

### M1 — within a population, it holds

| population | Spearman ρ | arms |
|---|---|---|
| South Carolina | **+0.964** | 11 |
| Dutch census | **+0.950** | 9 |
| COMPAS | **+0.783** | 12 |
| Oregon | +0.527 | 10 |

**Three of four clear the 0.70 bar**, and M1 required more than half. Inside a single
population, the signed distance from that population's crossover **orders the size of the
effect**, and does so strongly in three cases.

### M2 — across populations, it does not

**r = +0.487 against a bar of +0.70. FAILS.** One slope does not fit every domain: the same
distance from the crossover produces very different magnitudes in Dutch occupational data and
in COMPAS.

The naive alternative — *"magnitude is not predictable from anything we have"* — needed
|r| < 0.30 and does not get it. So it is beaten, and it is not replaced by anything usable.

### M3 — the parity gap adds a little

Adding the baseline parity gap to the predictor lifts the correlation from +0.487 to **+0.591**,
a gain of +0.105 against a 0.10 bar. It clears the bar it was given and is reported for
completeness, but a pooled correlation of +0.591 is not a forecasting tool and should not be
presented as one.

### What the concession becomes

Not *"magnitude is unpredictable"*, and not *"we can predict magnitude"*. The accurate
statement is:

> **Within a population, the distance from its crossover orders the size of the effect. Across
> populations, no single slope transfers.** So a team can say which of its own products or
> segments will be hit hardest, and cannot convert that into a number of decisions without
> running the constraint.

That is more useful than the old concession and more limited than it sounds, and it was
arrived at by a model that failed its main test.

---

## C — where the crossover sits, and whether 0.55 is a prior or a coincidence

[Document 32](32-the-rate-not-the-task.md) called the crossover "population-specific".
[Document 42](42-denser-sweeps-and-where-the-crossover-sits.md) found four populations agreeing
to within 0.08. Both cannot be right.

### C1 — they cluster

| population | domain | crossover |
|---|---|---|
| COMPAS | criminal justice | 0.511 |
| South Carolina | income | 0.530 |
| Oregon | income | 0.558 |
| Dutch census | occupational status | 0.576 |

**Standard deviation 0.029, against a bar of 0.05. Mean 0.544.**

Across three domains, two countries and four instruments — US income prediction, US criminal
justice and a Dutch occupational census — the crossover sits between **0.511 and 0.576**.
Document 32's "population-specific" was read off two six-point brackets whose apparent
difference was mostly the imprecision of six points.

**"Expect roughly 0.54, and check" is therefore a defensible instruction**, and a materially
different answer from a practitioner's own sweep is a reason to inspect the sweep before
believing it.

### C2 — and the residual explains nothing, at four populations

The screen returned two correlations above the 0.70 bar: crossover against between-group gap at
**+0.724**, and against sample size at **+0.865**.

**Neither means anything, and reporting them as findings would be the error this project has
already made twice.**

* The two "predictors" are collinear at **r = +0.947** — the Dutch census has both the largest
  gap and the largest sample, COMPAS the smallest of each — so with four points they cannot be
  separated from one another at all.
* Neither is distinguishable from chance: **p = 0.277** for the gap and **p = 0.135** for size.

The pre-registration called C2 a screen rather than a model and said so before the numbers
existed, which is the only reason those two correlations are being reported as noise rather
than written up as a formula for predicting the crossover. **Four populations cannot support
one**, and what the screen actually delivers is a hypothesis worth testing when there are
fifteen.

### C3 — lending

Every mortgage estimate sits above every non-lending one, 0.659–0.758 against 0.511–0.576. But
those three estimates come from a **single market** — Mississippi and Louisiana, 2018 —
measured three overlapping ways: the pooled arm contains Louisiana and refinance is a subset of
both. That is one population's worth of independent evidence. **"Lending is different" remains
a hypothesis**, and the honest statement is that this market does not join the cluster.

---

## What changes

* [Document 35](35-what-to-do-about-it.md) gains a prior — expect about 0.54 — and a sharper
  statement of what the magnitude result buys.
* Document 32's "population-specific" is superseded by document 42 and this one.
* The paper's magnitude limitation is rewritten from an assumption into a tested result with a
  failed model behind it.
* **No formula for predicting the crossover is claimed**, and C2's two correlations are recorded
  here so that nobody, including a later version of this project, mistakes them for one.
