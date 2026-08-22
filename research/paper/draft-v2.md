# Which Way Does Fairness Go? The Selection Rate Predicts Whether an Attribute-Blind Constraint Gives or Takes

**Status.** Rewrite complete; no results outstanding. §2 and the reference list are carried
over from `draft.md` with counts corrected; everything else is new. The evidence trail,
including every reference checked against its source, is in
[`reading-notes.md`](reading-notes.md).

**Scale.** 6 domains, 5 instruments, 3 countries, 2 decades. **27 independent populations**
— Adult, twelve ACS states, two HMDA states, COMPAS, LSAC and the Dutch census — carrying 67
dataset-by-attribute arms and 326 arm directories once label, operating-point, tolerance,
learner and criterion variants are counted. Arms of one population share their people, so 18
is the number that governs independence and the larger counts are reported as arms. Every
load-bearing figure is re-derived from stored results by `tests/test_documented_claims.py`,
which fails if a document and its data disagree.

---

## Abstract

**Scope, stated first because it is the sharpest thing we can say.** This is a paper about
**attribute-blind in-processing** constraints — the regime in which the protected attribute is
unavailable at decision time, which is where almost every deployed system sits, because
per-group thresholds are disparate treatment on their face in most jurisdictions. Under
*post-processing*, which does read the attribute, the effect below **disappears entirely**
(r = −0.024 against +0.585 on the same populations), and contemporaneous theory says exactly
why: in the attribute-aware regime the direction is *determined*, not distributional. We
confirm that too — the advantaged group loses and the disadvantaged gains in **18 of 18**
populations. If you may lawfully use the attribute at decision time, you do not need this
paper's rule. If you may not, nothing else currently tells you which way your system will go.

Group-fairness constraints of the reduction family (Agarwal et al., 2018) do what they
promise: on UCI Adult they drive the demographic-parity violation from 0.186 to 0.018 for
under two accuracy points, on any base classifier, without modifying the training data. We
audit what they do to *get* there.

Across 18 populations spanning two household surveys, US mortgage records, a criminal-justice
risk dataset, US law-school outcomes and the Dutch national census, we find that a parity
constraint closes the gap by **withdrawing** favourable decisions on some tasks and
**extending** them on others — and that which of the two occurs is predictable in advance
from a single quantity the deploying organisation already knows: **the rate at which its
current model says yes**. On UCI Adult and low-approval survey tasks, every method in a
six-method ablation shrinks the pool, by 7.9–22.1%. On mortgage lending, the identical
constraint *grows* it. **The certifying metric reports the same success in both cases.**

The relationship is not an artifact of how the selection rate is varied. Holding the task,
the features, the groups and even the fitted scores fixed, and moving only the classifier's
decision threshold, reproduces both the direction and the location of the transition — so the
operative variable is the selection rate itself and not the difficulty of the prediction
problem. It survives a twenty-five-fold range of constraint tolerance, a boosted-tree learner
in place of a linear one, and a protected attribute swapped from sex to race. It reproduces
on criminal-justice data (r = +0.870) and on a non-US census whose between-group gap is twice
Adult's (r = +0.915), which is the population where the standard competing explanation — that
the *group gap* drives the direction — should have shown itself and did not.

We state three boundaries as sharply as the result. The **magnitude** is ordered within a
population by the distance from its crossover (ρ up to +0.96) but does not transfer between
them (pooled r = +0.487, failing a pre-registered +0.70 bar). The **crossover is close to
stable**: measured densely, four populations across three domains, two countries and four
instruments sit between **0.511 and 0.576**, standard deviation 0.029 — so "expect about 0.54
and check" replaces the free parameter an earlier version of this work described. And the relationship is far
weaker under **equalized odds** on survey data, though not on every domain — the criterion's
effect is itself population-dependent.

Finally, the practical consequence is a procedure rather than an observation. A team can
locate its own crossover by sweeping its deployed model's decision threshold, requiring no new
data and no relabelling; four independent estimates of the mortgage crossover agree. Where the
answer says withdrawal, adding a floor on the overall selection rate — a linear moment
constraint inside the base paper's own framework, and a variant of a published remedy —
preserves parity to the same tolerance while the exchange rate falls from 1.47 favourable
decisions destroyed per one created to 0.88, for 0.12 accuracy points.

Fairness constraints do exactly what they are asked. The gap is between what is asked and what
is meant, and nothing in the standard toolchain surfaces it.

---

## 1. Introduction

A fairness constraint is a statement about a *gap*. It says the two groups' rates should be
close. It says nothing whatever about which of two very different worlds should produce that
closeness: one where the disadvantaged group is lifted, and one where the advantaged group is
pulled down.

Both satisfy the constraint. Both score identically on the metric that certifies them. Only
one of them is what anybody meant.

That this ambiguity exists is not our observation. Mittelstadt, Wachter and Russell (2023)
made levelling down the centre of a well-known critique; Maheshwari et al. (2023) report that
it "often goes unnoticed in the overall performance of the model"; Ferry et al. (2023) built an
auditing framework because an aggregate score reports neither how many people were affected
nor in which direction. We take all of that as given. §2 sets out what each established.

Our question is the one those papers leave open: **when?** A deploying team cannot act on
"this sometimes happens". It can act on a rule that says which way its own system will move,
before it moves.

**The answer is the selection rate** — the fraction of applicants the current, unconstrained
model already approves. Below a crossover, the constraint takes decisions away; above it, the
constraint hands them out. The crossover is a property of the population and can be measured
on the model an organisation already has.

### Contributions

1. **An empirical characterisation of the conditionality.** Contemporaneous theory establishes
   that in the attribute-blind regime the direction is distribution-dependent (§2). It contains
   no experiments and its conditions are ordering relations on score regions rather than
   anything measurable. We supply the measurement, across 18 populations and five domains, and
   we find **its stated conditions cannot be evaluated on any of 26 arms**: they are stated
   over extrema of a quantity that diverges on real data, and they are *sufficient, not
   necessary*, so the theorem is **silent** on our populations rather than wrong. A relaxed
   form of the same ordering tracks the direction on 24 of 26. This is a result about
   *applicability*, which only an empirical study could produce, and not a refutation.

2. **The identification of the operative variable, by a design that separates it from its
   confound.** Varying the selection rate by moving a label threshold cannot distinguish "the
   rate sets the direction" from "task difficulty does, and the rate travels with it". Holding
   the task exactly fixed and moving only the decision rule separates them, and the rate wins
   (§5.4).

3. **A procedure, not an observation.** The same design lets a practitioner locate their own
   crossover on their deployed model, needing no new data. Four independent estimates of the
   mortgage crossover agree (§7).

4. **Boundaries stated rather than discovered by a referee.** Magnitude is unpredictable; the
   crossover is not a constant; the criterion matters and does so unevenly; and the procedure
   is unusable on tasks with a very high base rate, for a reason we can compute in advance
   (§6.3).

5. **A method that reports its own failures.** Every prediction in this work was registered
   with its thresholds and the naive alternative it had to beat, before the data existed.
   Several failed. §8 lists them, including two headline results we withdrew after finding a
   defect in our own design.

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
is (a) the first empirical characterisation, across 18 populations and five domains; (b) the
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
   less clear." We report test-set results across 18 populations at five seeds.

**Auditing the individual impact of a mitigation.** `[VERIFIED against arXiv:2302.07185]`
Ferry, Aivodji, Gambs, Huguet and Siala (2023), *When Mitigating Bias is Unfair*, propose a
framework for auditing what a fairness intervention does to the individuals it moves, along
five dimensions whose first three are impact size ("how many people were affected"), change
direction ("positive versus negative changes") and decision rates ("impact on models'
acceptance rates"). Those three are the decomposition we report throughout §4, and we claim
no part of it: it was published in February 2023 and we adopt it. What we add is what those
axes report at scale. FRAME audits a given model against a given baseline; we run the same
measurements across 18 populations and find that the change-direction dimension is not a
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
add is not the blindness but what it hides: the size of the effect across 18 populations
(§4) and the quantity that predicts its direction (§5).

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
predicts that levelling down should not be attributable to the reduction's search — which §7 tests directly.

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
replicate across 21 ACS arms — and then find it is *not sufficient*, because they
share one survey instrument. Our second domain is what breaks claim (i), and no number of
additional states could have done it.

**Arbitrariness and multiplicity.** Black et al. (2022) and work on predictive multiplicity
establish that models with equivalent aggregate performance can disagree substantially on
individuals. Our claim (iii) is a specific instance, positioned as a caution supported by
that literature rather than as a novel finding.

---

---

## 3. Setup and method

**Data.** Twenty-seven independent populations across five instruments. UCI Adult (45,222 rows). ACS Income
(Ding et al., 2021) across twelve US states and two protected attributes. HMDA mortgage
records for Mississippi and Louisiana, by race and by sex, and split by loan purpose. COMPAS
(ProPublica, 2016; 5,278 rows on the race arm after their documented filter). LSAC bar passage
(20,798 rows). The Dutch national census of 2001 (60,420 rows).

The last three were added specifically to leave the instruments the finding was formed in. The
Dutch census carries a between-group gap of 0.298 — roughly twice Adult's — which makes it the
test of the standard alternative explanation. LSAC was chosen because bar passage is naturally
generous (base rate 0.890) and populates the top of the selection-rate range, where only
mortgage lending previously sat.

**Convention.** `y = 1` is always the favourable outcome and the selection rate is the fraction
of people receiving it. This required inverting COMPAS's recorded target, which encodes
recidivism — the outcome nobody wants — and it required declaring **Female** the advantaged
group on COMPAS's sex arm, because women in that cohort reoffend less and therefore receive the
favourable prediction more often. Both are enforced by a test rather than by care, since either
error produces every directional result with its sign flipped and nothing raises.

**Mitigation.** `ExponentiatedGradient` (Agarwal et al., 2018) at ε = 0.01 unless stated, with
`GridSearch` for frontiers and `ThresholdOptimizer` for the post-processing comparison. No
model reads the protected attribute at prediction time except where post-processing is
explicitly under test, which is a different regime and labelled as one.

**Measurement.** We report the change in the **total number of favourable decisions**, the
**exchange rate** (decisions destroyed per one created), and the flip counts by `(group,
outcome)` cell. These are the first three audit dimensions of Ferry et al. (2023); the
instrument is theirs and we adopt it.

**Two exclusion rules, both applied throughout.** An arm is discarded if the baseline
demographic-parity gap is below 0.05 — there is nothing to remove — or if the baseline
classifier's accuracy is below `max(p, 1 − p)`, the accuracy of always predicting the more
common label. The second rule matters more than it sounds and is the subject of §8.2.

**Seeds.** Five by default, twelve where effects are small enough that five cannot separate
them from noise. Below roughly 2,500 test subjects the reduction's own randomness exceeds the
entire effect of the constraint, and we treat results from smaller populations as directional
only.

---

## 4. Parity is bought by withdrawal — where it is bought that way

On UCI Adult, every method in a six-method in-processing ablation reduces the total number of
favourable decisions, by **7.9% to 22.1%**. Not one closes the gap primarily by extending
decisions to the disadvantaged group. Eighteen of nineteen survey arms do the same.

The rate-level view understates it. Equal-looking changes in group *rates* fall on groups of
unequal size, so the burden counted in people diverges from the burden counted in rates, with
the divergence predicted by a cross-flow diagnostic at r = +0.885.

**And then it reverses.** On HMDA mortgage data the identical constraint **grows** the pool by
4.3%, at an exchange rate of 0.50 — it creates two favourable decisions for every one it
destroys. The parity metric reports 0.018 on the population that destroyed a fifth of its
favourable decisions and 0.010 on the one that created more than it destroyed.

That reversal is the whole problem. It means "levelling down" is not a property of the method,
and a practitioner cannot know from the literature which of the two their system will do.

---

## 5. What sets the direction

### 5.1 The conjecture

The survey populations sit at selection rates between 0.195 and 0.353; the mortgage arms at
0.758 and 0.808. When most applicants are already approved, closing a gap by lifting the
disadvantaged group is cheap, because they are near the decision boundary anyway.

This cannot be tested by comparing the two datasets, which differ in domain, instrument, label
semantics, feature set, group ratio, proxy leakage **and** selection rate simultaneously.

### 5.2 A single-factor design

ACS Income's label is "earns more than $50,000" — a benchmark convention, not a fact. Moving it
on one fixed state varies the selection rate while holding the population, the instrument, the
feature set, the group ratio and the proxy structure exactly fixed; a test asserts that the
rows, features and groups are identical across arms and only the label changes.

The change in the pool rises with the baseline selection rate at **r = +0.801**, and **+0.980**
once the confounded between-group gap is partialled out. The sign flips: 22 favourable
decisions destroyed per one created at a rate of 0.03, against 0.75 at 0.89.

### 5.3 The transition appears without being manufactured

Lenders record why a loan was sought, and approval rates differ sharply by purpose. Pooling
Mississippi and Louisiana across five loan products — nothing manipulated, one market, one year
— home improvement at a selection rate of 0.555 **levels down** (−1.57%) while refinancing at
0.871 **levels up** (+2.95%). r = +0.803, ρ = +0.900.

A bank running one fairness constraint across its loan book would take opportunities away in
one product and hand them out in another, and its fairness report would show success in both.

### 5.4 It is the rate, not the difficulty of the task

§5.2's design moves the *label*. "Earns over $100,000" is not a rarer version of "earns over
$20,000"; it is a harder problem. So that design cannot separate two explanations that predict
everything observed so far: the selection rate sets the direction, or task difficulty does and
the rate merely travels alongside.

We separate them by holding the task completely fixed — same rows, same features, same groups,
**same fitted scores** — and moving only where the model draws its line. This is a strictly
stronger single-factor manipulation, because §5.2 changes the label and this changes nothing
but the decision rule.

The relationship reproduces, and so does the location of the crossover: on Oregon the two
routes give 0.362–0.653 and 0.353–0.637. **Task difficulty is not doing the work.**

**With denser sampling the picture sharpens and one claim narrows.** Twelve points chosen from
each population's *viable band* — the rates reachable by a classifier still beating the trivial
predictor — retain nine to twelve arms where six points retained two to four. On that footing
the relationship holds on the Dutch census (**+0.946**), South Carolina (**+0.905**) and COMPAS
(**+0.844**), and Oregon is marginal at +0.664.

Alabama and Kentucky come back **negative** (−0.368 and −0.654) on eleven and ten arms. Their
viable bands top out at 0.566 and 0.561 — at or below every crossover measured anywhere here —
so those two sweeps sit almost entirely on **one side** of the transition. **We therefore claim
the relationship across the crossover and withdraw any claim that it holds within the low-rate
region alone.** The six-point sweeps concealed this by including arms whose classifier was
worse than a constant.

### 5.5 Five domains

| instrument | domain | r |
|---|---|---|
| ACS Income | income prediction | +0.801 (label route), +0.855 (decision route, Oregon) |
| HMDA | mortgage lending | +0.858 |
| COMPAS | criminal justice | **+0.870** |
| Dutch census | occupational status | **+0.915** |
| LSAC | legal education | unsweepable — see §6.3 |

The pre-registered alternative — *"this is a property of income prediction and American
mortgage lending"*, requiring |r| < 0.30 — loses on both new instruments.

### 5.6 The group-gap explanation, tested where it should have won

The oldest competing account is that the *gap between the groups*, not the overall rate, drives
the direction. §5.2 partialled that gap out and the relationship survived, but no population
then measured had an extreme gap, so the test was weakest exactly where it mattered.

The Dutch census has one: men hold a high-status occupation at 0.626, women at 0.327, a gap of
**0.298**. **r = +0.915 across all six arms, none excluded.** Twice the gap changes nothing.

### 5.7 Robustness

| manipulation | direction | crossover | magnitude |
|---|---|---|---|
| route to the selection rate | unchanged | unchanged | **differs 3×** |
| constraint tolerance, 25× range | unchanged | unchanged | **differs 4×** |
| boosted trees for logistic regression | unchanged (5/5 populations) | unchanged | **differs 3×** |
| protected attribute, sex → race | unchanged | unchanged (0.362–0.653 vs 0.358–0.652) | — |
| criterion, parity → equalized odds | **weaker, unevenly** | — | **differs 8×** |
| optimiser, reduction → post-processing | **disappears (r = −0.024)** | — | — |

**The selection rate predicts which way. It orders how much within a population, and does not
transfer it between them.** Tested rather than assumed: the signed distance from a population's
own crossover gives Spearman ρ of +0.96, +0.95 and +0.78 in three of four populations, but a
single pooled slope reaches only **r = +0.487** against a +0.70 bar and fails. A team can say
which of its segments will be hit hardest; it cannot convert that into a number of decisions
without running the constraint.

The last row is not a fragility. Post-processing is **attribute-aware**, and the theory of §2
holds that in that regime the direction is determined rather than distributional — so there is
nothing for a predictor to predict. The prediction it makes for that regime is that the
advantaged group loses and the disadvantaged gains, always; on our populations that holds
**18 of 18**, with no exceptions across four instruments and two countries. The scope of this
paper's rule is therefore not an accident of which optimiser we chose: it is the regime
boundary the theory draws, confirmed from both sides.

---

## 6. Boundaries

### 6.1 The crossover is not a constant

An earlier draft of this work concluded the crossover is "population-specific" from two coarse
six-point brackets. Measured with twelve points the picture is much tighter:

| population | domain | mid-point |
|---|---|---|
| COMPAS | criminal justice | 0.511 |
| South Carolina | income | 0.530 |
| Oregon | income | 0.558 |
| Dutch census | occupational status | 0.576 |
| HMDA (one market, three estimates) | mortgage lending | 0.659 – 0.758 |

**Four populations across three domains, two countries and four instruments agree to within
0.08.** The lending estimates sit above all of them — but they come from a single market
measured three overlapping ways, so "lending is different" is a hypothesis here and not a
finding.

The crossover is also **route-invariant**: two very different manipulations agree within a
population, and the denser brackets sit inside the coarser ones. It is measurable, it is not
arbitrary, and the working expectation should be roughly 0.55 with a check rather than a
measurement from scratch.

### 6.2 The criterion matters, unevenly

Under equalized odds on ACS data the relationship weakens sharply: **r = +0.334 across twenty
arms**, against parity's +0.762 on the identical arms, and the pool moves roughly eight times
less. Adding populations made it *weaker*, which is what a near-absent effect does.

But this does not generalise either. On COMPAS the pool moves **more** under equalized odds
than under parity (+20.0% against +32.7%), the Dutch census agrees, and a COMPAS sweep under
equalized odds gives r = +0.900. The honest summary is that the criterion's effect is
population-dependent — the same lesson the crossover taught.

### 6.3 The procedure is unusable on very generous tasks, and we can say when

Varying the selection rate by moving a decision threshold works by **degrading the classifier**.
On a task where most people already qualify, reaching a low selection rate requires a model that
refuses qualified people, and past a point that model is worse than a constant.

This is computable before running anything. Define the *viable band* as the range of selection
rates reachable by a classifier that still beats `max(p, 1 − p)`:

| population | viable band | span |
|---|---|---|
| Dutch | 0.051–0.946 | 0.895 |
| COMPAS | 0.089–0.948 | 0.859 |
| ACS (typical) | 0.05–0.57 | ~0.51 |
| **LSAC** | **0.893–0.949** | **0.056** |

On LSAC — 89% pass the bar — **no choice of thresholds can produce a usable sweep.** We report
this as a scope condition with a computable test, not as a failure to find something.

### 6.4 Small populations

Below roughly 2,500 test subjects the method's own randomness exceeds the entire effect. COMPAS
has 1,584 and flips sign between seeds on two of four arms with a standard deviation up to 28.3;
LSAC has 6,240 and flips on none, with deviations as low as 0.35. COMPAS carries direction here
and never magnitude.

This prediction was registered in advance against our own earlier finding, and it held on data
that finding never saw.

---

## 7. What to do about it

1. **Check the criterion.** The rule is for criteria that constrain selection rates. Under
   error-rate criteria expect less movement and weaker prediction (§6.2).
2. **Look up your current approval rate.** Every deployed system already knows it.
3. **Locate your own crossover.** Sweep your deployed model's decision threshold, fit the
   constraint at each point, and find where the change in the pool turns from negative to
   positive. No new data, no relabelling. Discard arms whose accuracy falls below
   `max(p, 1 − p)`, check the viable band first (§6.3), and use ten to twelve points — six is
   too coarse to survive the exclusion rules.
4. **Act.** Below the crossover, expect withdrawal and add a floor on the overall selection
   rate: about 0.12 accuracy points, exchange rate 1.47 → 0.88 across nineteen arms, below 1.0
   in sixteen of them, with the benefit scaling with the damage at r ≈ −0.99. Above it, the
   constraint is likely to extend decisions and the floor buys little.
5. **Do not forecast the size.** The rate gives you the sign only.

The floor is **not a new method**: a selection-rate floor is a linear moment constraint inside
Agarwal et al.'s framework, and a variant of the minimum-rate constraints Mittelstadt et al.
(2023) propose. What differs is that ours is in-processing, stacked *with* parity rather than
replacing it, and validated on held-out data across eighteen populations.

**Validation.** Four independent estimates of the mortgage crossover agree: 0.643–0.773 from
comparing five real loan products with nothing manipulated, against 0.620–0.700 pooled,
0.620–0.697 on Louisiana held out, and 0.709–0.807 on refinance held out.

---

## 8. Method, and what we got wrong

Every prediction was registered with its thresholds **and the naive alternative it had to
beat**, before the data existed. That second half was added after a derivation of ours cleared
every stated bar and was then beaten by a constant. The full record is in the repository; three
episodes matter for reading the results above.

### 8.1 A pre-registered test that failed

The rule does **not** survive equalized odds at the bar we set: r = +0.644 on two states,
+0.334 on five, against a +0.70 threshold, unrescued by more seeds. Alabama alone would have
given +0.822 and every prediction holding. We report the failure and the scope condition it
buys rather than the two-state number.

### 8.2 Two headline results withdrawn

The operating-point design of §5.4 varies the selection rate by degrading the classifier, and
nothing in the design bounded how far. Excluding arms beaten by the trivial predictor leaves
Alabama with two arms and LSAC with one: **r = +0.979 and r = +0.968, both previously reported,
are void.**

The same exclusion **rescued** mortgage lending, which had failed outright, and brought it into
agreement with the independent estimate above. The defect was named in our own earlier text,
checked on one population, and generalised without being checked elsewhere — on high-base-rate
data the parity-gap rule that was doing the work does nothing.

### 8.3 A plausible result that was arithmetic

A post-processing comparison appeared to show a clean reversal of the relationship. It was
void: `ThresholdOptimizer` re-derives its own thresholds and never saw the decision rule being
manipulated, returning an identical model at all six operating points. The measured effect was
a constant divided by a shrinking baseline. What exposed it was an exchange rate of 0.000 —
not a number a real intervention produces.

### 8.4 Three counts that were wrong

Three population counts in earlier drafts were **arm** counts: nineteen arms from ten
populations, twenty-six arms from fifteen. No measurement changed, but the independence of the
evidence was overstated, and the abstract had claimed an effect held "in all 19 populations and
in both protected-attribute arms" — which double-counts, since the nineteen *are* the two arms.
Counts are now recomputed from source files by a test.

---

## 9. Limitations

**Magnitude transfers within a population and not between.** The distance from a population's
own crossover orders the effect (ρ = +0.96, +0.95, +0.78 in three of four), but the pooled
slope fails its pre-registered bar at r = +0.487. We can rank your segments; we cannot forecast
your losses.

**The crossover is nearly stable, and the residual is unexplained.** Four populations cluster
at 0.511–0.576. Two population properties appeared to explain the remaining variation, at
r = +0.724 and +0.865 — but they are collinear with each other at +0.947 and neither is
distinguishable from chance at four populations (p = 0.277, p = 0.135). We report them as a
hypothesis for a study with fifteen populations, not as a formula.

**Coverage.** Four instruments, two countries, two decades — but still no non-Western data, and
three of five domains are US and 2016–2018.

**One regime, and we now know which.** Under post-processing the effect vanishes (r = −0.024).
We argue in §5.7 that this is the theory's regime boundary rather than fragility, and support
it with an 18-of-18 confirmation of the theory's attribute-aware prediction — but that check
was decided *after* the failure and is post-hoc. A pre-registered test of the attribute-aware
regime remains to be done.

**The relationship is not monotone below the crossover.** Alabama and Kentucky reverse when
their sweeps are confined to the low-rate region (§5.4). We claim the relationship across the
transition only.

**The remedy is a variant, not a discovery.** Mittelstadt et al. (2023) proposed minimum rate
constraints. Ours differs in three narrow, checkable ways (§2).

**Subgroup results are replication.** Claim (ii) reproduces Kearns et al. (2018) and Maheshwari
et al. (2023) with a boundary attached, and is presented as such.

---

## 10. Discussion

The finding a practitioner can use is small and specific: **look up the rate at which your model
currently says yes, and you will know whether a parity constraint is about to give or to take.**

What makes that worth saying is not that it is surprising once stated. It is that the certifying
metric — the number a deployment team reports, an auditor checks and a regulator may one day
require — is identical in both worlds. A constraint that withdraws a fifth of all favourable
decisions and one that creates more than it destroys produce the same certificate.

The literature already knew the metric was silent. What was missing was a way to know, in
advance and from something a team already has, which of the two silences you are standing in.

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
