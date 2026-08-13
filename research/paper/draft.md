# Satisfied, Not Solved: What a Demographic Parity Constraint Actually Does

*Working draft. Markdown for iteration; ACM LaTeX conversion once the content settles
(`pdflatex` is available, `pandoc` is not, so the conversion will be manual).*

**Status of each section is marked.** `[SETTLED]` means every number is in the repository
and re-derived by `tests/test_documented_claims.py`. `[PENDING]` means an experiment is
still running. Related work has now been checked against the sources; the evidence trail is
in [`reading-notes.md`](reading-notes.md).

---

## Abstract `[SETTLED, pending two inserts]`

Group-fairness constraints of the reduction family (Agarwal et al., 2018) reliably do what
they promise: on UCI Adult they drive the demographic parity violation from 0.186 to 0.018
for under two accuracy points, on any base classifier, without modifying the training data.
We audit what they do to *get* there, across Adult, 18 ACS Income populations spanning two
protected attributes, and a mortgage-lending dataset, and find four things the certifying
metric does not report and standard auditing does not reveal.

**(i)** Parity is reached by withdrawing favourable decisions rather than extending them:
on Adult every method in a six-method ablation shrinks the total by 7.9–22.1%, and 18 of 19
survey populations shrink it. On mortgage-approval data the same constraint *grows* the
pool by 4.3%. The parity metric reports the same success in both cases — 0.018 on the
population that destroyed a fifth of its favourable decisions, 0.010 on the one that
created more than it destroyed. A single-factor sweep, moving only the income cutoff on a
fixed population so that rows, features and groups are provably identical across arms,
locates the moderator: the direction tracks the task's **selection rate**, crossing over
between 0.25 and 0.60 (r = +0.801 and +0.964 in two states; +0.980 and +0.994 once the
confounded base-rate gap is partialled out).

**(ii)** A constraint on one attribute leaves intersectional subgroups worse off than any
group it was told about, in every sufficiently diverse population and more severely than
Adult suggests (9.0× against 13.2×).

**(iii)** Below roughly 2,500 test subjects the method's own randomness exceeds the entire
effect of the constraint.

**(iv)** Feature-attribution audits do not recover the mechanism. Three pre-registered
explanations of an apparent +151% attribution shift are each refuted by intervention, and
most of the shift proves to be credit reallocating between two collinear features.

The first of these is fixable by stating the missing objective outright. Adding a floor on
the overall selection rate — a linear moment constraint inside the base paper's own
framework, not a new method — preserves parity to the same tolerance while the exchange
rate falls from 1.47 favourable decisions destroyed per one created to 0.88, for 0.12
accuracy points, in all 19 populations and both protected-attribute arms.

> `[PENDING]` two sentences to insert once the running experiments land: what group ratio
> contributes to the magnitude of (i), and how the floor compares against group-wise
> thresholding and minimax group fairness.

---

## 1. Introduction `[SETTLED]`

A fairness-constrained classifier is usually certified by the quantity it was constrained
on. The constraint is imposed, the violation falls to some small ε, and the model ships.
This paper is about everything that number does not say.

Our starting point is not a criticism of the method. We reproduce Agarwal et al. (2018) on
UCI Adult and it does exactly what it claims: demographic parity violation falls from 0.186
to 0.018, on a decision tree and on a logistic regression alike, without a single row of
training data being altered. Across six in-processing mitigations the pattern holds. If the
question is "did the constraint bind", the answer is yes, everywhere we looked.

The question we ask instead is *how* it was satisfied — and the answer turns out to be
invisible to every tool ordinarily used to check.

**Contributions.**

1. A four-part audit of what a demographic parity constraint does beyond its own metric,
   run identically across 22 populations spanning two survey instruments and one
   administrative record of real lending decisions.
2. The identification of a **moderator** for the most-discussed of those effects. Levelling
   down is not what parity constraints do; it is what they do below a selection rate of
   roughly 0.3. We establish this by a single-factor sweep in which the population, the
   instrument, the features, the group ratio and the proxy structure are held provably
   fixed and only the label's cutoff moves.
3. Evidence that the effect is **not an artifact of the solver**: the theoretically optimal
   DP classifier — group-wise thresholding on the unconstrained score — levels down as
   well. `[PENDING: full seed run]`
4. A remedy that is not a new method: one additional linear moment constraint, inside the
   base paper's own framework, whose benefit scales with the severity of the problem
   (r ≈ −0.99 between damage done and damage recovered) and which is inert where the
   problem is absent.
5. A methodological record — predictions registered before results, three of our own
   mechanistic explanations refuted, two of our own claims retracted in place — offered as
   a reason to believe the numbers rather than as process trivia.

**What we are not claiming.** Levelling down is not a new observation, and we do not
present it as one. Our contribution to it is scale, a quantitative diagnostic, and a scope
condition that the existing literature does not have.

---

## 2. Related work `[VERIFIED — see reading-notes.md]`

> **Verification status.** Every claim in this section has now been checked against the
> source, and the evidence trail — including the passages quoted — is in
> [`reading-notes.md`](reading-notes.md). Four references remain unverified and are listed
> there with the reason each is low-risk. One check changed the paper substantially (§2,
> first entry); one added a citation that was missing.

**Levelling down, and the remedy.** `[VERIFIED against arXiv:2302.02404]`
Mittelstadt, Wachter and Russell (2023) argue that fairness interventions frequently
equalise by degrading the better-off group, and that this is a default rather than an
accident of particular methods. **They also propose the remedy**: §6, "Levelling up by
design with minimum rate constraints", requires "that every group has, at least, a minimal
selection rate, precision, or recall", demonstrates it on Adult with demographic parity,
and reports that "levelling down does not occur" while parity is still reached.

We therefore claim neither the observation nor the remedy as novel, and say so here rather
than letting a reviewer discover it. Our contribution relative to that paper is four
things, each narrow and each checkable:

1. **A scope condition they do not have.** They treat levelling down as a default. We show
   the direction *reverses* above a selection rate located experimentally by a
   single-factor sweep. They note in passing that Adult is "more than 75% negatively
   labelled" — as a remark about accuracy cost, not as a condition — and nowhere connect
   label prevalence to the direction of the effect. This is our principal claim.
2. **In-processing rather than post-processing.** Their MRC is achieved by post-processing
   that tunes "a separate offset for each group", which requires the protected attribute at
   prediction time. Ours is a moment constraint inside the reduction; no model here reads
   the attribute when predicting. In jurisdictions where per-group thresholds are disparate
   treatment on their face, that difference is the whole difference.
3. **A population-level floor stacked with parity**, rather than a per-group floor that
   replaces it — so parity is still enforced to ε and the pie is preserved simultaneously.
4. **Held-out replication.** They report Adult, and explicitly on the training set:
   "Transferring them to the unseen test data introduces noise which would make the results
   less clear." We report test-set results across 22 populations, two protected attributes,
   two survey instruments and one administrative record, at five seeds.

**Remedies that avoid harm.** Minimax group fairness (Martinez et al., 2020; Diana et al.,
2021) minimises the worst group's error rather than equalising anything, and decoupled
classifiers with preference guarantees (Dwork et al., 2018; Ustun et al., 2019) seek
solutions no group would reject. These are the natural comparison for our selection-rate
floor and we benchmark against them in §7 rather than only against the unconstrained
reduction. `[PENDING: results]`

**The shape of the optimal fair classifier.** Corbett-Davies et al. (2017) show that "for
several past definitions of fairness, the optimal algorithms that result require detaining
defendants above **race-specific risk thresholds**"; Menon and Williamson (2018) give the
corresponding characterisation as an instance-dependent thresholding of the
class-probability function. This matters twice for us: it
gives us a principled *bound* rather than merely another baseline, and it predicts that
levelling down should not be attributable to the reduction's search procedure — which our
§7 comparison tests directly.

**The selection-rate axis.** The nearest prior work to our §4.4 is *Resource-constrained
Fairness* (2024), which studies the cost of fairness as a function of the available budget
across six datasets and rates from 1% to 100%, and reports that "the level of available
resources significantly influences this cost, a factor overlooked in previous evaluations".
The difference is structural rather than incremental: in their setting positive decisions
are a fixed resource, so the total is constant by construction and the directional effect we
measure cannot arise. They vary the selection rate and measure how much fairness *costs*; we
let the total move and find that its *sign* changes.

**Fairness gerrymandering.** Kearns et al. (2018) show that constraints imposed on marginal
groups can be satisfied while structured subgroups are badly treated. Our claim (ii) is an
empirical replication of exactly that phenomenon across populations, with a size condition
attached.

**Dataset monoculture.** Ding et al. (2021) argue the field should stop drawing conclusions
from UCI Adult and supply ACS-derived replacements. We take that seriously enough to
replicate on 19 ACS populations — and then find that this is *not sufficient*, because 18
of them share one survey instrument. Our second domain is what breaks claim (i), and no
number of additional states could have done it.

**Arbitrariness and multiplicity.** Black et al. (2022) and work on predictive multiplicity
establish that models with equivalent aggregate performance can disagree substantially on
individuals. Our claim (iii) is a specific instance: below a sample-size threshold, the
run-to-run variation of the fairness intervention exceeds the intervention's own effect. We
position this as a caution supported by that literature rather than as a novel finding.

---

## 3. Setup and method `[SETTLED]`

**Data.** UCI Adult (45,222 rows after listwise deletion; Male 30,527 at 31.25% positive,
Female 14,695 at 11.36%); ACS Income (Ding et al., 2021) for nine states in two
protected-attribute arms; HMDA 2018 mortgage applications for Mississippi in two arms.

**Protocol.** Five random seeds throughout, each an independent train/test split stratified
on the *(protected attribute, label)* interaction rather than the label alone — fairness
metrics are read from four cells and the smallest drifts between seeds otherwise, producing
variance that reads as model instability but is sampling noise.

**The protected attribute is removed from the feature matrix.** Fairness through unawareness
is carried as a control, not as a method. No model here can read the attribute directly; any
gap that survives is one the model rebuilt from proxies, which is what claim (iv) measures.

**Metrics** are implemented from their definitions and cross-checked against `fairlearn` on
every run, because a privileged/unprivileged orientation slip produces plausible and
silently wrong numbers. Rates with an empty denominator return undefined, never zero, so
that an unmeasurable subgroup cannot masquerade as a perfectly fair one — claim (ii)
depends on this.

**Pre-registration.** Where a result could have gone either way, the predictions and their
numerical thresholds were written and committed before the experiment was run. This is not
decoration: it is why we can report that one of our own predictions failed (§4.3), that
three of our proposed mechanisms were refuted (§6), and that two earlier claims of ours
were retracted. The commit history is the record.

---

## 4. The constraint's effect on outcomes `[SETTLED except 4.4]`

### 4.1 Parity is bought by withdrawal

Demographic parity fixes a relationship between two selection rates and is silent on the
level at which they meet. On Adult, every one of six in-processing mitigations closed the
gap partly by withdrawing favourable decisions, reducing their total by 7.9% to 22.1%. For
the reduction under a parity constraint the figure is −20.5%, at an exchange rate of **2.68
favourable decisions destroyed for every one created**.

This is invisible in the certifying metric, which records only that the violation fell to
0.018.

### 4.2 It replicates across populations, with a diagnostic

Across 19 survey populations, 18 shrink the pool of favourable decisions; the single
exception has a degenerate baseline. The rate-level and people-level pictures diverge, and
the divergence is predicted by a cross-flow diagnostic at **r = +0.885**.

### 4.3 A second domain reverses it

Every population above is a household survey. On HMDA mortgage decisions — an
administrative record of real lending outcomes — the same constraint removes 94% of the
parity violation while **increasing** approvals by 4.26%, at an exchange rate of 0.50. The
sex arm agrees (+1.05%, exchange 0.78). Across-seed standard deviations are 0.17 and 0.29,
so the effects clear their own noise by 25× and 3.6×.

The parity metric reports 0.010 here and 0.018 on Adult. **Same success, opposite outcome.**

### 4.4 What sets the direction

The two datasets differ in seven respects at once, so the comparison identifies nothing.
ACS Income's label is "earns more than $50,000" — a cutoff chosen by the benchmark. Moving
it on a fixed state varies the base rate while holding the population, instrument, features,
group ratio and proxy structure fixed; we assert in test code that rows, features and groups
are unchanged across arms and only the label moves.

| cutoff | selection rate | change in favourable decisions | destroyed per created |
|---|---|---|---|
| $100,000 | 0.030 | −29.71% | 22.03 |
| $70,000 | 0.099 | −22.05% | 2.18 |
| $50,000 | 0.252 | −2.34% | 1.14 |
| $30,000 | 0.598 | +0.98% | 0.83 |
| $20,000 | 0.760 | +0.80% | 0.75 |
| $10,000 | 0.890 | +0.08% | 0.89 |

The direction flips, with the crossover between 0.25 and 0.60. Oregon replicates it more
sharply (r = +0.964 against Alabama's +0.801) despite starting nearer the crossover.

**The moderator is the selection-rate *level*, not the between-group base-rate *gap*, and
the distinction carries the contribution.** That unequal base rates across groups force
trade-offs is long established (Kleinberg et al., 2016; Chouldechova, 2017) and is
standard textbook material. Our claim is about a different quantity: the overall proportion
of the population receiving a favourable decision, irrespective of any gap. The two are
confounded in this design by construction — the gap must vanish as the level approaches 0
or 1 — so we partial the gap out, and the relationship *strengthens*, from r = +0.801 to
+0.980 in Alabama and +0.964 to +0.994 in Oregon. That control is not a robustness check
appended to the result; it is the identification strategy, and it is what separates this
claim from the one the field already has.

The sweep places both datasets it was not fitted to: Adult at 0.205 shrinks, HMDA at 0.808
grows. It does not fit them tightly — Alabama loses 2.34% at 0.252 where Adult loses 20.5%
at 0.205 — so the selection rate sets the direction but not the magnitude.

### 4.5 The residual is not group ratio `[SETTLED]`

The obvious candidate for the leftover magnitude was the group ratio, which prior work in
this project found to be a genuine cause of the rate-versus-people divergence. We
pre-registered the prediction that a larger ratio means more levelling down, and crossed
four populations spanning a 4.4× range of ratios with five cutoffs.

**It is refuted, with the opposite sign** — partial r = +0.535 holding the selection rate
fixed, against a predicted −0.40. We do not claim the reverse: the ratio factor has only
four distinct levels, which is enough to refute a predicted direction and not enough to
assert its opposite. The magnitude of levelling down remains unexplained, and we report it
that way.

The same experiment does strengthen §4.4 substantially. The selection-rate result was
derived on two states of one protected attribute; it holds in four states of a *second*
attribute at within-state correlations of +0.874, +0.933, +0.969 and +0.991 — every one
above the sex arm's weaker state. Six populations, two protected attributes, one direction.

It also extends §7's range: the worst levelling down we measure anywhere is Mississippi at a
$70,000 cutoff, destroying **62% of all favourable decisions** at 17.6 per one created, and
the floor returns it to −2.2%.

---

## 5. Subgroups `[SETTLED]`

A constraint imposed on one marginal attribute says nothing about structure inside the
groups. Evaluating every Sex × Race cell, the worst-off subgroup after a sex constraint is
treated worse than either marginal group was before it. The effect appears in every
sufficiently diverse population and is **worse than Adult suggests** — 9.0× on Adult against
13.2× in Mississippi. It gains one condition: the effect needs a substantial minority to
hide in.

In five of ten populations the worst-off subgroup after a sex constraint is a minority man,
and in three it is Black men specifically — a finding first observed on Adult and then
reproduced without being looked for.

---

## 6. What attribution audits can and cannot see `[SETTLED]`

The protected attribute is not in the feature matrix, so the model reaches it through
proxies. The natural audit is feature attribution, and the natural expectation — which we
recorded in advance — is that a fairness constraint reduces reliance on those proxies.

It does not. On Adult, constraining demographic parity moves SHAP attribution *onto*
`relationship`, whose levels determine sex outright for 46% of rows, by **+151%**.

We then failed, three times, to explain it.

1. The proposed mechanism — that the constraint seeks the best available reconstruction of
   the protected attribute — was refuted by intervention: a *planted* proxy was used **less**
   as it sharpened, monotonically.
2. Its replacement — that the constraint is attracted to within-group outcome signal — was
   refuted by a two-factor version of the same intervention.
3. The third candidate, collinear reallocation, resisted a clean test for a structural
   reason: holding each column's marginal informativeness fixed while raising redundancy
   necessarily lowers the pair's joint informativeness. Both cannot be held at once.

Re-aggregation then showed most of the headline is measurement, not behaviour. Attribution
*shares* are compositional; scoring Adult's two most redundant features as a single
coalition takes the effect from **+155% to +11.6%**. The residual is positive in 5 of 5
seeds and is constraint-specific — demographic parity raises the pair's combined share
(+11.7%, +14.2%) while equalized odds lowers it (−26.4%) — which a pure artifact of Shapley
credit allocation should not be, since the pair's redundancy is a property of the dataset.

**We report this as a negative result.** The +151% is real, reproducible, and unexplained,
and the practical lesson is the one that matters for auditing: a feature-attribution audit
of a fairness-constrained model can move by an order of magnitude without the model's
behaviour changing correspondingly, and did not reveal the mechanism in any of our attempts.

---

## 7. Stating the missing objective `[SETTLED except the comparison]`

Levelling down is a property of the objective, not of the algorithm. The reduction is
agnostic about *how* it satisfies a constraint because the constraint is all it is told.

We add one more: `P(h(x) = 1) ≥ τ`, with τ the unconstrained model's own selection rate —
*do not hand out fewer favourable decisions than the model you are replacing*. This is not
a new method. Agarwal et al. define constraints as linear in the classifier's conditional
moments, and a floor on the overall selection rate is exactly that.

On Adult, parity is satisfied to the same tolerance (0.0179 against 0.0178) while the pie
loss falls from **−20.5% to −0.6%** and the exchange rate from **2.68 to 1.03**, for 0.37
accuracy points. Across 19 populations and both arms, the exchange rate falls in **19 of
19**, from 1.47 to 0.88 and 1.59 to 0.79, and the number of populations creating more
favourable decisions than they destroy goes from 1 to 16. The extra accuracy cost averages
0.12–0.15 points.

**The remedy scales with the disease.** Across the threshold sweep, the amount the floor
recovers tracks the amount the plain constraint destroys at **r = −0.994** and **−0.995** in
two states. Where the constraint destroys 29.7% of favourable decisions the floor turns
that into +1.2%; where nothing is wrong it does nothing, to within a tenth of a percentage
point. That is what makes it applicable by default rather than after diagnosis.

> `[PENDING]` Comparison against group-wise thresholding (the optimal DP classifier, and
> therefore a bound — it uses the protected attribute at prediction time, which nothing else
> here does) and minimax group fairness. A single-seed run already indicates that the
> optimal DP classifier levels down as well, which would rule out the solver as the cause.

---

## 8. Limitations `[SETTLED]`

* **One administrative domain, one state, one year.** The reversal in §4.3 rests on HMDA
  Mississippi 2018. A second high-selection-rate domain is needed before the crossover is
  quoted as a property of tasks in general.
* **Two states carry the threshold sweep**, both ACS and both sex-arm.
* **The selection rate is a moderator, not a determinant.** An order of magnitude of
  variation at comparable rates is unexplained. `[PENDING: §4.5]`
* **The mechanism behind §6 is unidentified**, and we say so rather than offering a fourth
  story. Our record with plausible mechanistic accounts in this project is three proposed
  and three refuted.
* **HMDA's feature set is a judgement.** Thirty-six columns were excluded as post-decision
  or protected. `denial_reason` is 99.2% predictive of the outcome with a missingness gap
  of exactly zero; a different exclusion list would give different numbers.
* **Five seeds**, which our own §5 result suggests is too few on the smallest populations.

---

## 9. Discussion `[DRAFT]`

Fairness constraints do exactly what they are asked. Every finding above follows from the
constraint being satisfied precisely as specified, by a solver doing its job. The gap is
between what was asked and what was meant, and none of the standard toolchain surfaces it:
not the certifying metric, which reports the same success for opposite outcomes; not
marginal parity, which is silent on subgroups; not a point estimate, which hides
run-to-run variation exceeding the effect; and not feature attribution, which moved
ninefold without telling us why.

The practical reading is narrow and, we think, actionable. If a deployment cares whether
the pool of favourable decisions shrinks, that has to be written into the objective, where
it costs a fraction of an accuracy point. If it cares about subgroups, marginal parity will
not deliver them. And if the task's selection rate is low, the constraint's default
behaviour is to take decisions away — which is, in the domains where these methods are most
often proposed, exactly the regime they operate in.

---

## References `[VERIFIED except four — see reading-notes.md]`

- Agarwal, Beygelzimer, Dudík, Langford & Wallach (2018). *A Reductions Approach to Fair
  Classification.* ICML. — the base paper; verified in this repository.
- Black, Raghavan & Barocas (2022). *Model Multiplicity: Opportunities, Concerns, and
  Solutions.* FAccT. — verified.
- Chouldechova (2017); Kleinberg, Mullainathan & Raghavan (2016). — impossibility results.
- Corbett-Davies, Pierson, Feller, Goel & Huq (2017). *Algorithmic Decision Making and the
  Cost of Fairness.* KDD.
- Diana, Gill, Kearns, Kenthapadi & Roth (2021). *Minimax Group Fairness.*
- Ding, Hardt, Miller & Schmidt (2021). *Retiring Adult.* NeurIPS.
- Dwork, Immorlica, Kalai & Leiserson (2018). *Decoupled Classifiers.* FAT*.
- Kamiran & Calders (2012). *Data preprocessing techniques for classification without
  discrimination.* — excluded from our ablation as pre-processing; cited for scope.
- Kamishima, Akaho, Asoh & Sakuma (2012). *Fairness-Aware Classifier with Prejudice Remover
  Regularizer.* — implemented from the paper in this repository.
- Kearns, Neel, Roth & Wu (2018). *Preventing Fairness Gerrymandering.* ICML.
- Martinez, Bertran & Sapiro (2020). *Minimax Pareto Fairness.* ICML.
- Menon & Williamson (2018). *The Cost of Fairness in Binary Classification.* FAT*.
- Mittelstadt, Wachter & Russell (2023). *The Unfairness of Fair Machine Learning.*
- Ustun, Liu & Parkes (2019). *Fairness without Harm: Decoupled Classifiers with Preference
  Guarantees.* ICML, PMLR v97 — verified; **not on arXiv**, cite the proceedings.
- Zhang, Lemoine & Mitchell (2018). *Mitigating Unwanted Biases with Adversarial Learning.*
  AIES. — implemented from the paper in this repository.
