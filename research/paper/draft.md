# Satisfied, Not Solved: What a Demographic Parity Constraint Actually Does

*Working draft. Markdown for iteration; ACM LaTeX conversion once the content settles
(`pdflatex` is available, `pandoc` is not, so the conversion will be manual).*

**Every number below is in the repository and re-derived by
`tests/test_documented_claims.py`.** Related work has been checked against the sources; the
evidence trail, including the four references still unverified and why each is low-risk, is
in [`reading-notes.md`](reading-notes.md). No section is waiting on an experiment.

**Scale.** 26 populations — Adult, 21 ACS Income populations across twelve states and two
protected attributes, and four HMDA mortgage populations across two states and two
attributes — over 61 experimental arms once the label-threshold sweeps are counted.

---

## Abstract

Group-fairness constraints of the reduction family (Agarwal et al., 2018) reliably do what
they promise: on UCI Adult they drive the demographic parity violation from 0.186 to 0.018
for under two accuracy points, on any base classifier, without modifying the training data.
We audit what they do to *get* there, across 26 populations spanning a household survey, its
modern replacement, and an administrative record of real mortgage decisions.

**(i)** Parity is reached by withdrawing favourable decisions rather than extending them: on
Adult every method in a six-method ablation shrinks the total by 7.9–22.1%, and 18 of 19
survey populations shrink it. On mortgage data the same constraint *grows* the pool by 4.3%.
The parity metric reports the same success in both cases — 0.018 where a fifth of all
favourable decisions were destroyed, 0.010 where more were created than destroyed. That a
parity score does not separate those two outcomes is established (Maheshwari et al., 2023;
Ferry et al., 2023) and is the frame for this work, not a result of it. A
single-factor sweep, moving only the income cutoff on a fixed population so that rows,
features and groups are provably identical across arms, locates the moderator: **the
direction tracks the task's selection rate**, crossing over between 0.25 and 0.60. It
replicates across two protected attributes, five states, and fourteen further arms — four
populations — held out from a subsequent prediction (r = +0.901).

**(ii)** A constraint on one attribute leaves intersectional subgroups worse off than any
group it was told about, in every sufficiently diverse population and more severely than
Adult suggests (9.0× against 13.2×).

**(iii)** Below roughly 2,500 test subjects the method's own randomness exceeds the entire
effect of the constraint.

**(iv)** Feature-attribution audits do not recover the mechanism. Three explanations of an
apparent +151% attribution shift are each refuted or bounded, and most of the shift proves to
be credit reallocating between two collinear features.

Levelling down is a property of the objective rather than the algorithm, and can be removed
by stating the missing objective — a result anticipated in normative form by Mittelstadt et
al. (2023), whose minimum rate constraints we position ourselves against explicitly. Our
variant is an in-processing moment constraint requiring no protected attribute at prediction
time; the exchange rate falls from 1.47 favourable decisions destroyed per one created to
0.88 in all 19 survey populations, and the benefit tracks the damage at r ≈ −0.99. Against
the *optimal* DP classifier the same levelling down appears, so it is not a solver artifact;
against minimax group fairness, the established levelling-down remedy, we find it destroys
10% of favourable decisions on mortgage data at an exchange rate of 46.7.

---

## 1. Introduction

A fairness-constrained classifier is usually certified by the quantity it was constrained
on. The constraint is imposed, the violation falls to some small ε, and the model ships.
This paper is about everything that number does not say.

Our starting point is not a criticism of the method. We reproduce Agarwal et al. (2018) on
UCI Adult and it does exactly what it claims: demographic parity violation falls from 0.186
to 0.018, on a decision tree and on a logistic regression alike, without a single row of
training data being altered. Across six in-processing mitigations the pattern holds. If the
question is "did the constraint bind", the answer is yes, everywhere we looked.

The question we ask instead is *how* it was satisfied. That the certifying metric does not
answer it is not our observation — Maheshwari et al. (2023) and Ferry et al. (2023) both
report it, and §2 sets out what each established. We take it as given, and ask what sits
behind the number.

**Contributions.**

1. **A four-part audit** of what a demographic parity constraint does beyond its own metric,
   run identically across 26 populations and 61 experimental arms, spanning two survey
   instruments and one administrative record of real lending decisions.
2. **The first empirical characterisation of a conditionality that theory predicts.**
   Contemporaneous theory establishes that in the attribute-blind regime the direction of
   levelling down is distribution-dependent; we show *which* property predicts it in practice.
   Levelling down is what parity constraints do below a selection rate of roughly 0.3, and
   above it the direction reverses. Established by a single-factor sweep holding population,
   instrument, features, group ratio and proxy structure provably fixed while only the label's
   cutoff moves, and replicated across two protected attributes, five states and a second
   lending domain. **This is our principal claim.**
3. **Evidence that it is not an artifact of the solver.** On Adult the theoretically optimal
   DP classifier — group-wise thresholding on the unconstrained score — destroys 18.8% of
   favourable decisions against the reduction's 20.5%, with better parity. At moderate
   selection rates the two diverge in sign, so the solver matters where the effect is mild
   and not where it is severe.
4. **An identity that says precisely what levelling down is.** Parity puts both groups on one
   common rate, so the pie is preserved exactly when that rate's position between the two
   original group rates equals the privileged group's population share. Levelling down is the
   optimiser choosing a compromise below the size-weighted one, and nothing else.
5. **An empirical comparison against the existing remedies**, including the finding that
   minimax group fairness — proposed in the literature as the answer to levelling down —
   levels down worse than the parity constraint does on data where the parity constraint does
   not level down at all.
6. **A methodological record.** Predictions registered before results; **three of our own
   pre-registered predictions failed**; two proposed mechanisms refuted by our own
   interventions; three claims corrected or retracted in place, including our own novelty
   claim for the remedy, which the literature had anticipated. Offered as a reason to believe
   the numbers rather than as process trivia.

**What we are not claiming.** Neither levelling down, nor the remedy for it, nor the point
that the certifying metric reports the same success either way is a new observation, and we
present none of them as one — see §2. They are the frame; the contribution sits underneath
them. We also do not claim a mechanism for
the moderator: we attempted a derivation, pre-registered it, and report in §4.5 that it does
not earn its keep.

---

## 2. Related work

> Every claim here has been checked against the source, with quoted passages recorded in
> [`reading-notes.md`](reading-notes.md). Four references remain unverified and are listed
> there with the reason each is low-risk.

**Whether levelling down is universal.** `[VERIFIED against arXiv:2603.06901]` A 2026
theory paper, *Fairness May Backfire: When Leveling-Down Occurs*, proves in a population-level
Bayes framework that the answer depends on the deployment regime. Where the protected
attribute is available at decision time, fairness "necessarily (weakly) improves outcomes for
the disadvantaged group and (weakly) worsens outcomes for the advantaged group". Where it is
not — the **attribute-blind** regime, which is ours throughout — "the impact of fairness is
distribution-dependent: fairness can benefit or harm either group ... leading to either
leveling up or leveling down."

**We therefore do not claim the conditionality itself.** It is established, contemporaneously
and independently, in theory. What that paper does not have is any empirical component: it
contains zero experiments and names no dataset, and its conditions are ordering relations on
score regions rather than a quantity a practitioner can measure. Our contribution against it
is (a) the first empirical characterisation, across 26 populations and two domains; (b) the
identification of the *operating selection rate* as the practical predictor, computable
before a model is built; and (c) the crossover located experimentally by a single-factor
design. It also explains our own failed derivation (§4.5): the governing condition is an
ordering condition on score regions, not the scalar threshold we predicted.

**Levelling down, and the remedy.** Mittelstadt, Wachter and Russell (2023) argue that
fairness interventions frequently equalise by degrading the better-off group, and that this
is a default rather than an accident of particular methods. **They also propose the
remedy**: §6, "Levelling up by design with minimum rate constraints", requires "that every
group has, at least, a minimal selection rate, precision, or recall", demonstrates it on
Adult with demographic parity, and reports that "levelling down does not occur" while parity
is still reached.

We therefore claim neither the observation nor the remedy as novel, and say so here rather
than letting a reviewer discover it. Our contribution relative to that paper is four things,
each narrow and each checkable:

1. **A scope condition they do not have.** They treat levelling down as a default. We show
   the direction *reverses* above a selection rate located experimentally. They note in
   passing that Adult is "more than 75% negatively labelled" — as a remark about accuracy
   cost, not as a condition — and nowhere connect label prevalence to the direction of the
   effect. This is our principal claim.
2. **In-processing rather than post-processing.** Their MRC is achieved by post-processing
   that tunes "a separate offset for each group", which requires the protected attribute at
   prediction time. Ours is a moment constraint inside the reduction; no model here reads the
   attribute when predicting. Where per-group thresholds are disparate treatment on their
   face, that difference is the whole difference.
3. **A population-level floor stacked with parity**, rather than a per-group floor that
   replaces it — so parity is still enforced to ε and the pie is preserved simultaneously.
4. **Held-out replication.** They report Adult, and explicitly on the training set:
   "Transferring them to the unseen test data introduces noise which would make the results
   less clear." We report test-set results across 26 populations at five seeds.

**Auditing the individual impact of a mitigation.** `[VERIFIED against arXiv:2302.07185]`
Ferry, Aivodji, Gambs, Huguet and Siala (2023), *When Mitigating Bias is Unfair*, propose a
framework for auditing what a fairness intervention does to the individuals it moves, along
five dimensions whose first three are impact size ("how many people were affected"), change
direction ("positive versus negative changes") and decision rates ("impact on models'
acceptance rates"). Those three are the decomposition we report throughout §4, and we claim
no part of it: it was published in February 2023 and we adopt it. What we add is what those
axes report at scale. FRAME audits a given model against a given baseline; we run the same
measurements across 26 populations and find that the change-direction dimension is not a
property of the method being audited but of the population it is applied to, reversing at a
selection rate their framework does not measure — the full text contains no occurrence of
"selection rate" or "base rate". Their dimensions are what make our claim (i) legible; the
reversal is ours.

**What the certifying metric does not report.** That a fairness score cannot distinguish a
gap closed by lifting the disadvantaged group from one closed by withdrawing from the
advantaged group is established, and is the frame for everything below rather than a finding
of ours. Maheshwari, Bellet, Denis and Keller (2023) report that levelling down under
intersectional fairness "often goes unnoticed in the overall performance of the model";
Ferry et al. (2023) build FRAME around the same gap, auditing impact size, change direction
and effect on acceptance rates because the aggregate metric reports none of them. What we
add is not the blindness but what it hides: the size of the effect across 26 populations
(§4.1–4.3) and the quantity that predicts its direction (§4.4).

**Remedies that avoid harm.** Minimax group fairness (Martinez et al., 2020; Diana et al.,
2021) minimises the worst group's error rather than equalising anything, and decoupled
classifiers with preference guarantees (Dwork et al., 2018; Ustun et al., 2019) seek
solutions no group would reject. We benchmark against these in §7 rather than only against
the unconstrained reduction.

**The shape of the optimal fair classifier.** Corbett-Davies et al. (2017) show that "for
several past definitions of fairness, the optimal algorithms that result require detaining
defendants above race-specific risk thresholds"; Menon and Williamson (2018) give the
corresponding characterisation as an instance-dependent thresholding of the class-probability
function. This gives us a principled *bound* rather than merely another baseline, and it
predicts that levelling down should not be attributable to the reduction's search — which §7
tests directly.

**The selection-rate axis.** The nearest prior work to §4.4 is Goethals, Delaney,
Mittelstadt and Russell (2024), *Resource-constrained Fairness* — note that two of its four
authors also wrote the levelling-down paper above. It studies the cost of fairness as a function of the available budget
across six datasets and rates from 1% to 100%, and reports that "the level of available
resources significantly influences this cost, a factor overlooked in previous evaluations".
The difference is structural: in their setting positive decisions are a fixed resource, so
the total is constant by construction and the directional effect we measure cannot arise.
They vary the selection rate and measure how much fairness *costs*; we let the total move and
find that its *sign* changes. That the same group studied this axis, named it as overlooked,
and did not connect it to direction is the clearest evidence we can offer that the connection
is not obvious.

**Fairness gerrymandering, and why it survives an audit.** Kearns et al. (2018) show that
constraints imposed on marginal groups can be satisfied while structured subgroups are badly
treated. Maheshwari et al. (2023) supply the half that Kearns does not: they report that
fairness-promoting methods "tend to level down more in intersectional fairness", and that the
damage is concealed by aggregate performance (§2). Kearns is the failure mode; Maheshwari is
the reason an auditor reading aggregate numbers does not see it. Our
claim (ii) is an empirical replication of both, across populations, and what it adds is
scope and a boundary rather than an observation — 9.0× on Adult against 13.2× in
Mississippi, and a minority-share condition below which the effect does not appear at all.

**Dataset monoculture.** Ding et al. (2021) argue the field should stop drawing conclusions
from UCI Adult and supply ACS-derived replacements. We take that seriously enough to
replicate across 21 ACS populations — and then find it is *not sufficient*, because they
share one survey instrument. Our second domain is what breaks claim (i), and no number of
additional states could have done it.

**Arbitrariness and multiplicity.** Black et al. (2022) and work on predictive multiplicity
establish that models with equivalent aggregate performance can disagree substantially on
individuals. Our claim (iii) is a specific instance, positioned as a caution supported by
that literature rather than as a novel finding.

---

## 3. Setup and method

**Data.** UCI Adult (45,222 rows after listwise deletion; Male 30,527 at 31.25% positive,
Female 14,695 at 11.36%); ACS Income (Ding et al., 2021) across twelve states, nine of them
in both a sex and a race arm; HMDA mortgage applications for Mississippi and Louisiana, 2018,
in both arms.

**Protocol.** Five random seeds throughout, each an independent train/test split stratified
on the *(protected attribute, label)* interaction rather than the label alone — fairness
metrics are read from four cells and the smallest drifts between seeds otherwise, producing
variance that reads as model instability but is sampling noise.

**The protected attribute is removed from the feature matrix.** Fairness through unawareness
is carried as a control, not as a method. No model here can read the attribute directly; any
gap that survives is one the model rebuilt from proxies, which is what claim (iv) measures.

**Metrics** are implemented from their definitions and cross-checked against `fairlearn` on
every run, because a privileged/unprivileged orientation slip produces plausible and silently
wrong numbers. Rates with an empty denominator return undefined, never zero, so an
unmeasurable subgroup cannot masquerade as a perfectly fair one — claim (ii) depends on this.

**Pre-registration, and what it caught.** Where a result could have gone either way, the
predictions and their numerical thresholds were written and committed before the experiment
ran; the ordering is verifiable in the commit history. It is why we can report that three of
our own predictions failed — a mis-specified test of the remedy (§7), a refuted account of
the effect's magnitude (§4.6), and a mechanism that cleared its bars while being beaten by a
constant (§4.5). It is also, twice, what caught tests specified so that passing them did not
mean what it appeared to mean.

---

## 4. The constraint's effect on outcomes

### 4.1 Parity is bought by withdrawal

Demographic parity fixes a relationship between two selection rates and is silent on the
level at which they meet. On Adult, every one of six in-processing mitigations closed the gap
partly by withdrawing favourable decisions, reducing their total by 7.9% to 22.1%. For the
reduction under a parity constraint the figure is −20.5%, at an exchange rate of **2.68
favourable decisions destroyed for every one created**.

This is invisible in the certifying metric, which records only that the violation fell to
0.018 — the blind spot §2 attributes to Maheshwari et al. and Ferry et al., here in its
aggregate form. What this section supplies is its size on Adult. The measurements behind it — how many people were moved, in which direction, and
what happened to the acceptance rate — are FRAME's audit dimensions (§2); what follows is
what they report once they are run across populations rather than on a single model.

### 4.2 It replicates across populations, with a diagnostic

Across 19 survey populations, 18 shrink the pool of favourable decisions; the single
exception has a degenerate baseline. The rate-level and people-level pictures diverge, and
the divergence is predicted by a cross-flow diagnostic at **r = +0.885**.

### 4.3 A second domain reverses it

Every population above is a household survey. On HMDA mortgage decisions — an administrative
record of real lending outcomes — the same constraint removes 94% of the parity violation
while **increasing** approvals by 4.26%, at an exchange rate of 0.50. The sex arm agrees
(+1.05%, exchange 0.78), and a second state replicates both. Across-seed standard deviations
are 0.17 and 0.29, so the effects clear their own noise by 25× and 3.6×.

The parity metric reports 0.010 here and 0.018 on Adult: same success, opposite outcome. The
result is the reversal; that the metric does not distinguish the two is the known frame (§2).

### 4.4 What sets the direction

The two datasets differ in seven respects at once, so the comparison identifies nothing. ACS
Income's label is "earns more than $50,000" — a cutoff chosen by the benchmark. Moving it on
a fixed state varies the base rate while holding the population, instrument, features, group
ratio and proxy structure fixed; we assert in test code that rows, features and groups are
unchanged across arms and only the label moves.

| cutoff | selection rate | change in favourable decisions | destroyed per created |
|---|---|---|---|
| $100,000 | 0.030 | −29.71% | 22.03 |
| $70,000 | 0.099 | −22.05% | 2.18 |
| $50,000 | 0.252 | −2.34% | 1.14 |
| $30,000 | 0.598 | +0.98% | 0.83 |
| $20,000 | 0.760 | +0.80% | 0.75 |
| $10,000 | 0.890 | +0.08% | 0.89 |

The direction flips, with the crossover between 0.25 and 0.60. Oregon replicates it more
sharply (r = +0.964 against Alabama's +0.801) despite starting nearer the crossover; four
states of a *second* protected attribute reproduce it at +0.874 to +0.991; and fourteen
further arms, drawn from four populations run after and held out from the prediction in
§4.5, give r = +0.901 — [+0.752, +0.974] when the bootstrap resamples populations rather
than arms.

**The moderator is the selection-rate *level*, not the between-group base-rate *gap*, and
the distinction carries the contribution.** That unequal base rates across groups force
trade-offs is long established (Kleinberg et al., 2016; Chouldechova, 2017) and is standard
textbook material. Our claim is about a different quantity: the overall proportion of the
population receiving a favourable decision, irrespective of any gap. The two are confounded
in this design by construction — the gap must vanish as the level approaches 0 or 1 — so we
partial the gap out, and the relationship *strengthens*, from r = +0.801 to +0.980 in Alabama
and +0.964 to +0.994 in Oregon. That control is not a robustness check appended to the
result; it is the identification strategy, and it is what separates this claim from the one
the field already has.

The sweep places both datasets it was not fitted to: Adult at 0.205 shrinks, HMDA at 0.808
grows. It does not fit them tightly — Alabama loses 2.34% at 0.252 where Adult loses 20.5% at
0.205 — so the selection rate sets the direction but not the magnitude.

### 4.5 An identity that clarifies, and a mechanism we do not have

Demographic parity puts both groups on one common rate *s*, so the constrained total *is* *s*,
while the unconstrained total is the size-weighted average of the two group rates. Writing λ
for where *s* falls between them, the pie is preserved **exactly when λ = p**, with *p* the
privileged group's share. Levelling down is λ < p and nothing else — the optimiser choosing a
compromise below the size-weighted one. This holds to 0.076 percentage points across all
fourteen held-out arms and requires no assumptions.

It localises the question without answering it. We attempted a mechanism — under group-wise
thresholding, calibration and a location shift, levelling down is a curvature effect and the
crossover sits at the mode of the score density — pre-registered it with its thresholds, and
tested it on fourteen arms from four populations, run afterwards. It passes its stated bars,
predicting the
sign in 12 of 14, and is nonetheless **beaten by the constant rule "levelling up iff the
selection rate exceeds 0.5" (13 of 14)**. The measured mode moves inversely with the
selection rate (r = −0.802), so it carries almost no independent information; controlling for
the selection rate, curvature's partial correlation with λ − p is −0.182.

We report the attempt as unsuccessful, and the flip as an empirical regularity. The
methodological lesson is recorded with it: we fixed a threshold but not a **baseline to
beat**, so clearing it did not mean what it appeared to mean.

### 4.6 The residual is not group ratio

The obvious candidate for the leftover magnitude was the group ratio, which prior work in this
project found to be a genuine cause of the rate-versus-people divergence. We pre-registered
the prediction that a larger ratio means more levelling down, and crossed four populations
spanning a 4.4× range of ratios with five cutoffs.

**It is refuted, with the opposite sign** — partial r = +0.535 holding the selection rate
fixed, against a predicted −0.40. We do not claim the reverse: the ratio factor has only four
distinct levels, enough to refute a predicted direction and not enough to assert its opposite.
The magnitude of levelling down remains unexplained, and we report it that way.

---

## 5. Subgroups

A constraint imposed on one marginal attribute says nothing about structure inside the groups.
Evaluating every Sex × Race cell, the worst-off subgroup after a sex constraint is treated
worse than either marginal group was before it. The effect appears in every sufficiently
diverse population and is **worse than Adult suggests** — 9.0× on Adult against 13.2× in
Mississippi. It gains one condition: the effect needs a substantial minority to hide in.

In five of ten populations the worst-off subgroup after a sex constraint is a minority man,
and in three it is Black men specifically — a finding first observed on Adult and then
reproduced without being looked for.

---

## 6. What attribution audits can and cannot see

The protected attribute is not in the feature matrix, so the model reaches it through proxies.
The natural audit is feature attribution, and the natural expectation — which we recorded in
advance — is that a fairness constraint reduces reliance on those proxies.

It does not. On Adult, constraining demographic parity moves SHAP attribution *onto*
`relationship`, whose levels determine sex outright for 46% of rows, by **+151%**.

We then failed, three times, to explain it. The proposed mechanism — that the constraint
seeks the best available reconstruction of the protected attribute — was refuted by
intervention: a *planted* proxy was used **less** as it sharpened, monotonically. Its
replacement, that the constraint is attracted to within-group outcome signal, was refuted by
a two-factor version of the same intervention. The third candidate, collinear reallocation,
resisted a clean test for a structural reason: holding each column's marginal informativeness
fixed while raising redundancy necessarily lowers the pair's joint informativeness.

Re-aggregation then showed most of the headline is measurement, not behaviour. Attribution
*shares* are compositional; scoring Adult's two most redundant features as a single coalition
takes the effect from **+155% to +11.6%**. The residual is positive in 5 of 5 seeds and is
constraint-specific — demographic parity raises the pair's combined share (+11.7%, +14.2%)
while equalized odds lowers it (−26.4%) — which a pure artifact of Shapley credit allocation
should not be, since the pair's redundancy is a property of the dataset.

**We report this as a negative result, and the practical lesson is the transferable part:** a
feature-attribution audit of a fairness-constrained model can move by an order of magnitude
without the model's behaviour changing correspondingly. The +151% is real, reproducible, and
unexplained, and attribution did not reveal the mechanism in any of our attempts.

---

## 7. Stating the missing objective

Levelling down is a property of the objective, not of the algorithm. The reduction is
agnostic about *how* it satisfies a constraint because the constraint is all it is told.
**This much is Mittelstadt et al.'s (2023) argument, and their minimum rate constraints are
its constructive form**; what follows is a variant and a much larger evaluation, not a
discovery.

We add one constraint: `P(h(x) = 1) ≥ τ`, with τ the unconstrained model's own selection rate
— *do not hand out fewer favourable decisions than the model you are replacing*. Agarwal et
al. define constraints as linear in the classifier's conditional moments, and a floor on the
overall selection rate is exactly that, so this needs no new machinery. Unlike a per-group
floor applied by post-processing, it requires no protected attribute at prediction time.

On Adult, parity is satisfied to the same tolerance (0.0179 against 0.0178) while the pie loss
falls from **−20.5% to −0.6%** and the exchange rate from **2.68 to 1.03**, for 0.37 accuracy
points. Across 19 survey populations and both arms, the exchange rate falls in **19 of 19**,
from 1.47 to 0.88 and 1.59 to 0.79, and the number of populations creating more favourable
decisions than they destroy goes from 1 to 16. The extra accuracy cost averages 0.12–0.15
points.

**The remedy scales with the disease.** Across the threshold sweep, the amount the floor
recovers tracks the amount the plain constraint destroys at **r = −0.994** and **−0.995** in
two states. Where the constraint destroys 29.7% of favourable decisions the floor turns that
into +1.2%; where nothing is wrong it does nothing, to within a tenth of a percentage point.
That is what makes it applicable by default rather than after diagnosis.

**Against the existing remedies.** Three populations spanning the selection-rate range, five
seeds.

*Group-wise thresholding*, the optimal DP-constrained classifier, is carried as a **bound**
rather than a rival — it uses the protected attribute at prediction time, which nothing else
here does. On Adult it destroys **18.8%** of favourable decisions against the reduction's
20.5%, at a comparable exchange rate and with better parity, which closes the objection that
levelling down is a solver artifact. At Alabama's moderate rate the two disagree in sign, so
the solver matters where the effect is mild and not where it is severe.

*Minimax group fairness* is proposed in the literature as the answer to levelling down. It is
not one here. On HMDA it **destroys 10.0% of favourable decisions at an exchange rate of
46.7** — the worst figure anywhere in our data — while barely moving parity, on the same
population where the parity constraint *creates* 4.3%. The reason is in its objective: minimax
minimises the worst group's **error**, and worst-off-by-error is not worst-off-by-outcome. On
Adult the higher-error group is Male, so the method optimises for the privileged group and
concludes correctly that there is little to do. This is our own thesis appearing inside a
baseline — a criterion whose stated aim diverges from what it optimises, with nothing in its
metric to say so.

**What the floor is, after this comparison:** not the best at parity, and not the cheapest. It
is the only arm that satisfies parity *and* preserves the pool of favourable decisions
*without* requiring the protected attribute at prediction time.

---

## 8. Limitations

* **Two lending populations, one year.** The reversal in §4.3 rests on HMDA 2018 for
  Mississippi and Louisiana. A second high-selection-rate *domain*, not merely a second
  state, is needed before the crossover is quoted as a property of tasks in general.
* **The magnitude is unexplained.** The selection rate sets the direction, not the size; an
  order of magnitude of variation at comparable rates remains open after one candidate was
  refuted (§4.6) and one derivation failed to earn its keep (§4.5).
* **No direct comparison against a post-processing MRC.** Mittelstadt et al.'s construction
  is a per-group floor applied by post-processing. The closest arm here is group-wise
  thresholding, which is not the same thing. This is the most obvious missing baseline.
* **The mechanism behind §6 is unidentified**, and we say so rather than offering a fourth
  story. Our record with plausible mechanistic accounts is three proposed, two refuted by
  intervention and one bounded by re-aggregation.
* **HMDA's feature set is a judgement.** Thirty-six columns were excluded as post-decision or
  protected. `denial_reason` is 99.2% predictive of the outcome with a missingness gap of
  exactly zero; a different exclusion list would give different numbers.
* **Minimax is a simplified implementation** — the standard reweighting scheme rather than
  either paper's exact algorithm — so its erratic behaviour may be partly implementation. The
  Adult diagnosis, that the higher-error group is Male, does not depend on it.
* **Five seeds**, which our own claim (iii) suggests is too few on the smallest populations.

---

## 9. Discussion

Fairness constraints do exactly what they are asked. Every finding above follows from the
constraint being satisfied precisely as specified, by a solver doing its job. The gap is
between what was asked and what was meant, and none of the standard toolchain surfaces it:
not the certifying metric, which reports the same success for opposite outcomes; not marginal
parity, which is silent on subgroups; not a point estimate, which hides run-to-run variation
exceeding the effect; and not feature attribution, which moved ninefold without telling us
why.

The practical reading is narrow and, we think, actionable. If a deployment cares whether the
pool of favourable decisions shrinks, that has to be written into the objective, where it
costs a fraction of an accuracy point. If it cares about subgroups, marginal parity will not
deliver them. And the direction depends on the task's selection rate, which across the
domains these methods are proposed for **spans the entire range**: résumé screening operates
near 0.02, US mortgage lending near 0.84. Two organisations can deploy the identical
constraint in good faith and get opposite effects on the total number of opportunities
granted, with nothing in the fairness report distinguishing the two.

We close on what we could not do. We can say *when* the direction flips and not *why*. Our
own derivation of the crossover cleared the bars we set for it and was beaten by a constant,
which we report because a fairness literature that publishes only its successful mechanisms
is subject to precisely the criticism this paper makes of fairness metrics: the summary looks
the same whether or not the thing beneath it worked.

---

## References

- Agarwal, Beygelzimer, Dudík, Langford & Wallach (2018). *A Reductions Approach to Fair
  Classification.* ICML. — the base paper; reproduced in this work.
- *Fairness May Backfire: When Leveling-Down Occurs in Fair Machine Learning* (2026).
  arXiv:2603.06901 — **read in full**; proves the conditionality we characterise empirically.
- Black, Raghavan & Barocas (2022). *Model Multiplicity: Opportunities, Concerns, and
  Solutions.* FAccT. — verified.
- Chouldechova (2017); Kleinberg, Mullainathan & Raghavan (2016). — impossibility results.
- Corbett-Davies, Pierson, Feller, Goel & Huq (2017). *Algorithmic Decision Making and the
  Cost of Fairness.* KDD. — verified.
- Diana, Gill, Kearns, Kenthapadi & Roth (2021). *Minimax Group Fairness.* — verified.
- Ding, Hardt, Miller & Schmidt (2021). *Retiring Adult.* NeurIPS.
- Dwork, Immorlica, Kalai & Leiserson (2018). *Decoupled Classifiers.* FAT*.
- Ferry, Aivodji, Gambs, Huguet & Siala (2023). *When Mitigating Bias is Unfair: A
  Comprehensive Study on the Impact of Bias Mitigation Algorithms.* arXiv:2302.07185, SaTML.
  — **read in full**; its first three audit dimensions are the decomposition we use in §4.
- Kamiran & Calders (2012). *Data preprocessing techniques for classification without
  discrimination.* — excluded from our ablation as pre-processing; cited for scope.
- Kamishima, Akaho, Asoh & Sakuma (2012). *Fairness-Aware Classifier with Prejudice Remover
  Regularizer.* — implemented from the paper in this work.
- Kearns, Neel, Roth & Wu (2018). *Preventing Fairness Gerrymandering.* ICML. — verified.
- Maheshwari, Bellet, Denis & Keller (2023). *Fair Without Leveling Down.* EMNLP. —
  verified; the source for the concealment half of claim (ii), that intersectional levelling
  down "often goes unnoticed in the overall performance of the model".
- Martinez, Bertran & Sapiro (2020). *Minimax Pareto Fairness.* ICML.
- Menon & Williamson (2018). *The Cost of Fairness in Binary Classification.* FAT\*. —
  verified; cite Corbett-Davies for the *group-specific* threshold form.
- Mittelstadt, Wachter & Russell (2023). *The Unfairness of Fair Machine Learning: Levelling
  down and strict egalitarianism by default.* arXiv:2302.02404 — **read in full**; §6 is our
  closest prior work.
- Goethals, Delaney, Mittelstadt & Russell (2024). *Resource-constrained Fairness.*
  arXiv:2406.01290 — verified; nearest prior work on the selection-rate axis.
- Ustun, Liu & Parkes (2019). *Fairness without Harm: Decoupled Classifiers with Preference
  Guarantees.* ICML, PMLR v97 — verified; **not on arXiv**, cite the proceedings.
- Zhang, Lemoine & Mitchell (2018). *Mitigating Unwanted Biases with Adversarial Learning.*
  AIES. — implemented from the paper in this work.
