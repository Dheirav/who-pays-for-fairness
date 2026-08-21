# Reading notes: what was checked, and what it changed

**Individual work, beyond the course submission.**

The paper draft's related-work section was originally written from background knowledge and
carried a warning saying so. This file records what was then actually read, what each read
confirmed or refuted, and the exact passages the positioning now rests on. Anything still
unverified is marked.

The reason for keeping this separately: §2 is the only part of the paper not backed by the
repository, so it needs its own evidence trail.

---

## 1. Mittelstadt, Wachter & Russell (2023) — **changed the paper**

*The Unfairness of Fair Machine Learning: Levelling down and strict egalitarianism by
default.* arXiv:2302.02404. **Read in full (49pp, text extracted).**

**What was expected:** a critique establishing that fairness methods level down, against
which our remedy would be positioned as new.

**What is actually there:** the remedy as well. §6 is titled *"Levelling up by design with
minimum rate constraints"*, with §6.1 *"Example 1: Demographic parity"*.

> "instead of enforcing that these properties be equalised across groups, we can instead
> require that **every group has, at least, a minimal selection rate**, precision, or
> recall. We refer to this type of minimum acceptable threshold ... as a 'minimum rate
> constraint' (MRC)."

> "Unlike enforcing egalitarian group fairness constraints, **levelling down does not
> occur**. Instead, the decision rate of the disadvantaged group steadily increases until it
> reaches parity with the advantaged group, followed by the decision rate for both groups
> increasing together."

**Consequence.** [Document 19](../docs/19-levelling-up-is-expressible.md)'s framing — that
levelling up "has to be part of the objective" and had never been tested — is wrong about
the literature and is corrected in place. The selection-rate floor is a **variant of a
published remedy**, not a discovery.

**What survives, verified against the same text:**

| difference | evidence |
|---|---|
| Ours is in-processing; theirs is post-processing needing the attribute at predict time | "We show how levelling up can be achieved through MRCs in practice by using **post-processing**. The family of post-processing methods we consider tune a separate offset for each group" |
| Ours floors the *population* rate alongside parity; theirs floors *each group's* rate instead of parity | "require that every group has, at least, a minimal selection rate" |
| Ours is held-out across 22 populations; theirs is Adult, on train | "We show the results on the **training set** ... Transferring them to the unseen test data introduces noise which would make the results less clear." |

**What they do not have — and this is now our headline.** Searched the full text: **zero
occurrences of "base rate".** Levelling down is treated as a default, not a conditional
phenomenon — it is in their title. Their only remark near prevalence is:

> "As expected, with the dataset being more than 75% negatively labelled, large drops in
> accuracy were required for the positive decision rate to approach 1."

That is about *accuracy cost*, not about direction. They were working at a selection rate of
roughly 0.24 — inside the levelling-down regime
[document 23](../docs/23-the-selection-rate-sets-the-direction.md) identifies — and never
ask whether it would reverse elsewhere.

---

## 2. Corbett-Davies, Pierson, Feller, Goel & Huq (2017) — **confirmed §7's bound argument**

*Algorithmic Decision Making and the Cost of Fairness.* arXiv:1701.08230. Abstract read.

> "for several past definitions of fairness, the optimal algorithms that result require
> detaining defendants above **race-specific risk thresholds**"

This is what §7 needs: group-wise thresholding is the *optimal* DP-constrained classifier,
so our `group_thresholds` arm is a **bound** rather than a rival, and a gap to it measures
the reduction's search cost rather than the constraint's cost. They also report tension
between the constraint and aggregate welfare, which is consistent with our claim (i).

---

## 3. Menon & Williamson (2018) — **confirmed, but cite second**

*The cost of fairness in binary classification.* FAT\* 2018 (PMLR v81).

> "for cost-sensitive fairness measures, the optimal classifier is an **instance-dependent
> thresholding of the class-probability function**"

Confirms the thresholding characterisation. Note the phrasing is *instance-dependent*
thresholding rather than explicitly *group-specific*, so **Corbett-Davies is the primary
citation** for the group-threshold claim and this is supporting. Do not attribute the
group-specific form to this paper alone.

---

## 4. Diana, Gill, Kearns, Kenthapadi & Roth (2021) — **confirmed the baseline is fair**

*Minimax Group Fairness.* arXiv:2011.03108. Abstract read.

Objective is "minimizing the maximum loss across all groups"; they give "provably convergent
oracle-efficient learning algorithms (or equivalently, **reductions to non-fair
learning**)". Our implementation is an iterative reweighting scheme in that family, and is
labelled in `src/baselines.py` as simplified rather than a reimplementation — which this
confirms is the honest description.

**Not attributable to them:** our observation that the worst group *by error rate* on Adult
is Male, so minimax optimises for the privileged group there. That is ours, from our data,
and must be presented as an empirical observation about this dataset rather than as their
claim.

---

## 5. Kearns, Neel, Roth & Wu (2018) — **confirmed exactly**

*Preventing Fairness Gerrymandering.* arXiv:1711.05144.

> "a classifier appears to be fair on each individual group, but badly violates the fairness
> constraint on one or more structured subgroups"

Our claim (ii) is an empirical replication of precisely this, across populations, with a
minority-size condition attached. Cite without qualification — and never alone: Maheshwari
et al. (2023), in §12 below, cover what Kearns does not, that the intersectional harm is
larger under these methods and goes unnoticed in aggregate performance.

---

## 6. Ustun, Liu & Parkes (2019) — **confirmed**

*Fairness without Harm: Decoupled Classifiers with Preference Guarantees.* ICML 2019, PMLR
v97 — **not on arXiv**, cite the proceedings. Decoupled models per group under beneficence
and non-maleficence, such that each group prefers its own model to the pooled one.
Characterisation in our §2 stands.

---

## 7. Black, Raghavan & Barocas (2022) — **confirmed**

*Model Multiplicity: Opportunities, Concerns, and Solutions.* FAccT 2022. Models of
equivalent accuracy differing in individual predictions; "arbitrariness in model selection
that can impact individuals". Our claim (iii) is positioned as an instance supported by this
literature rather than as novel, which remains the right framing.

---

## 8. Goethals, Delaney, Mittelstadt & Russell (2024) — **new, and worth citing**

*Resource-constrained Fairness*, arXiv:2406.01290. **Two of the four authors also wrote
entry 1**, which sharpens the novelty claim considerably: the group best placed to connect
the selection rate to the direction of levelling down studied that axis, called it
"overlooked in previous evaluations", and did not make the connection. Not in the original draft; surfaced while checking whether the
selection-rate moderator was already known.

They study the *cost* of fairness as a function of the available budget, across six datasets
and selection rates from 1% to 100%, and state that "the level of available resources
significantly influences this cost, **a factor overlooked in previous evaluations**".

**This is complementary, not competing, and the distinction is structural.** In their setup
positive decisions are a fixed resource to be allocated, so the total is held constant by
construction and the direction we measure cannot arise. They vary the selection rate and
measure how much precision fairness costs; we let the total move and find that its
*direction* flips. Their own phrase — a factor overlooked in previous evaluations —
supports the claim that this axis is under-examined.

Cite in §4.4 as the nearest prior work on the selection-rate axis, and state the difference
explicitly.

---

## 9. Novelty checks that came back clean

Two further sweeps, run to probe the flanks that had not been checked at all.

**Does anyone already report that fairness constraints change feature attributions?** (§6.)
Nothing directly on point surfaced: the adjacent literature is about the *fairness of
explanations* rather than about what a constraint does to them. One adjacent observation is
worth citing if the search can be repeated — that SHAP distributes credit among correlated
features in ways that are "technically correct ... but socially misleading" — which is
independent support for [document 20](../docs/20-what-a-share-can-carry.md)'s compositional
argument.

**Is the selection-rate moderator known?** (§4.4.) No collision, but the sweep surfaced a
**phrasing risk that has been fixed in the draft**, and it is the most useful thing this
round produced.

The literature discusses base-rate **differences between groups** at length — unequal
prevalence forcing trade-offs is Kleinberg et al. and Chouldechova, and appears in every
tutorial on demographic parity. Our claim is about a different quantity: the **overall
level** of the selection rate, irrespective of any gap. A reviewer skimming §4.4 could
easily conflate the two and dismiss the finding as textbook.

The defence already exists in the experiment and simply was not being presented as one.
Document 23's T2 partials the between-group gap out, and the relationship strengthens rather
than weakens. **That control is the identification strategy, not a robustness check**, and
§4.4 now says so explicitly.

**Search availability.** Two further queries — on proxy-reliance measurement before and
after mitigation, and on Zietlow et al.'s levelling-down demonstration in computer vision —
could not be run; the search backend returned errors. Both remain open and neither is
load-bearing: the first is a novelty check on a *negative* result, and the second is a
vision paper cited by Mittelstadt et al. for a claim we already accept.

## Still unverified

| paper | why the risk is low |
|---|---|
| Martinez, Bertran & Sapiro (2020), *Minimax Pareto Fairness* | Cited alongside Diana et al. for the same objective, which is confirmed |
| Dwork, Immorlica, Kalai & Leiserson (2018), *Decoupled Classifiers* | Cited alongside Ustun et al. for the same construction, which is confirmed |
| Ding et al. (2021), *Retiring Adult* | Already used throughout this project; the ACS loader is built on it |
| Kleinberg et al. (2016); Chouldechova (2017) | Cited only for the impossibility result, which is not contested anywhere in the paper |

---

## Net effect on the paper

1. **The remedy demotes from headline to supporting**, and §2 now concedes it in the first
   paragraph rather than waiting for a reviewer.
2. **The selection-rate moderator promotes to the principal claim**, and survived a direct
   check against the two nearest candidates — Mittelstadt et al. (no base rates at all) and
   *Resource-constrained Fairness* (fixed budget, so direction is unobservable).
3. **§7's "bound, not rival" argument is safe**, on Corbett-Davies.
4. **One citation added**, one demoted to supporting, one warning removed.

---

## 9. "Fairness May Backfire: When Leveling-Down Occurs" (2026) — **changes the headline**

arXiv:2603.06901, March 2026. **Read in full (15pp, text extracted).** Found by running a
novelty check on the seven findings that had never had one. It is the closest work to this
project's principal claim and post-dates the assistant's training data, so it could only
have been found by searching.

**What it establishes.** A population-level (Bayes) framework, "distribution-free and
algorithm-agnostic", for two regimes:

* **Attribute-aware** (the protected attribute is available at decision time): fairness
  "necessarily (weakly) improves outcomes for the disadvantaged group and (weakly) worsens
  outcomes for the advantaged group."
* **Attribute-blind** (it is not): "the impact of fairness is **distribution-dependent**:
  fairness can benefit or harm either group and may shift both groups' outcomes in the same
  direction, **leading to either leveling up or leveling down**."

**Every population in this project is attribute-blind** — the protected attribute is dropped
from the feature matrix throughout (docs/01). So this project lives entirely inside the
regime they prove is two-sided.

**Consequence: our claim that levelling down is conditional rather than universal is
anticipated, theoretically, and by five months.** It must be cited and it must stop being
presented as the discovery.

**What is not in their paper.** Checked by term count over the full text:

| term | occurrences |
|---|---|
| "experiment" | **0** |
| "dataset" | **0** |
| "Adult", "COMPAS" | **0** |
| "base rate", "prevalence" | **0** |

It is pure theory with no empirical component. Their conditions are **ordering conditions on
score regions** — whether fairness deletes from the "advantaged-like side" (both groups'
rates weakly decrease) or adds on the "disadvantaged-like side" (both weakly increase),
governed by comparisons like `B_max ≤ A_min`. That is a statement about the geometry of the
score distribution, not about a scalar operating point a practitioner can read off.

**What therefore survives here:**

1. **The first empirical characterisation.** 26 arms from 15 populations, 61 arms with
   cutoff sweeps, two domains. They
   have none.
2. **A predictor that can actually be computed.** Their condition needs the joint score
   geometry; ours is "what fraction of applicants do you currently approve", which is
   available before any model is built.
3. **The crossover located** (0.25–0.60), and a single-factor design that moves one variable
   and verifies the rest are fixed.
4. **The domains.** Real mortgage decisions, where the effect is observed rather than derived.

**It also explains our own failure.** [Document 26](../docs/26-the-derivation-does-not-earn-its-keep.md)
derived a curvature account, predicted the crossover would sit at the mode of the score
density, and was beaten by a constant. This paper shows the true condition is an *ordering*
condition on score regions rather than a scalar threshold — which is precisely why a
single-number rule underperformed. The failed derivation was the right shape and the wrong
object.

**Net.** The headline narrows from "levelling down is conditional, and nobody has said so"
to "it is conditional — proven in theory contemporaneously — and here is what actually
predicts it, measured across 26 arms from 15 populations." Theory paired with independent empirics is a
normal and defensible pairing, but the framing has to change and the citation is mandatory.

---

## 10. The remaining citations, now checked

**Martinez, Bertran & Sapiro (2020), *Minimax Pareto Fairness*.** ICML, PMLR v119.
Confirmed: group fairness as multi-objective optimisation, a classifier that "achieves
minimax risk and is Pareto-efficient with respect to all groups, avoiding unnecessary harm".
Two details that matter for our §7. Their framing is explicitly harm-avoidance, so
describing minimax as a proposed remedy for levelling down is fair. And their method "does
not require test-time access to sensitive attributes", which makes it directly comparable to
our in-processing setup — unlike group-wise thresholding, which does. The baseline
comparison is like-for-like in a way the bound arm is not.

**Dwork, Immorlica, Kalai & Leiserson (2018).** The full title is *Decoupled Classifiers for
**Group-Fair** and Efficient Machine Learning*, PMLR 81:119–133 — our reference dropped
"Group-Fair" and should be corrected. Confirmed: a decoupling technique atop any black-box
learner producing a separate classifier per group, with transfer learning for small groups.

**Zietlow et al. (2022), *Leveling Down in Computer Vision*.** CVPR, pp. 10410–10421 — one
of the two searches that had errored, now retried. Confirmed: existing fairness approaches
in vision "improve fairness by degrading the performance of classifiers across all groups,
with increased degradation on the best performing groups", with a bias–variance argument for
why methods designed for low-capacity models should not be used with high-capacity ones.
**Chris Russell is a co-author here as well as on entries 1 and 8** — three of our most
relevant references share an author, which is worth knowing before writing the related work.

**Ding et al. (2021) and Kleinberg / Chouldechova** remain formally unread and are the last
two. Both are low-risk for the reason recorded earlier: the ACS loader is built directly on
the first, and the second is cited only for an impossibility result the paper never
contests.

---

## 11. The punchline was asserted, never measured — and it was wrong

Checked at last, and it does not hold. See
[document 29](../docs/29-where-real-decisions-actually-sit.md).

Every draft claimed lending, hiring and admissions are low-selection-rate settings, so the
harmful regime is the deployed regime. Published figures:

| domain | selection rate |
|---|---|
| résumé screening, applicant to interview (2024) | **0.02–0.03** |
| elite university admission | 0.04–0.10 |
| university admission, all four-year US institutions | 0.66–0.73 |
| US mortgage lending, HMDA 2023 aggregate | **~0.84** |

They **span the range and straddle the crossover**. The corrected argument is stronger: two
organisations can deploy the identical constraint in good faith and get opposite effects,
with identical fairness reports. It also validates the data — our HMDA populations sit at
0.758 and 0.808 against a national aggregate of ~0.84, so they are representative rather
than an unusually permissive slice.

This is the third claim in this project that felt too obvious to check and was wrong. The
other two were the novelty of the remedy and the novelty of the conditionality.

---

## 12. Systematic novelty audit — 72 citing papers screened

Recorded in full as [document 30](../docs/30-novelty-audit.md). Method: the citation graph of
the three closest works (72 unique citing papers), all screened by abstract, five read in
full, plus about a dozen searches across six vocabularies for the same quantity.

**Two further collisions found, neither on the headline:**

**FRAME — Ferry et al. (2023), *When Mitigating Bias is Unfair*, arXiv:2302.07185, SaTML.**
Its first three dimensions are **Impact Size** ("how many people were affected"),
**Change Direction** ("positive versus negative changes") and **Decision Rates** ("impact on
models' acceptance rates"). That is document 05's who-pays decomposition, published February
2023. It must be cited there. What FRAME does *not* do is use the acceptance rate as a
*predictor* of direction — it reports the rate a debiased model ends up at, one of five
descriptive dimensions. Zero occurrences of "selection rate" or "base rate" in the full text.

**Maheshwari, Bellet, Denis & Keller (2023), *Fair Without Leveling Down*, EMNLP.** Reports
that "popular fairness-promoting approaches tend to level down more in intersectional
fairness" and that "this often goes unnoticed in the overall performance of the model". That
is adjacent both to our claim (ii) and to the paper's organising thesis, and it means **the
thesis sentence is not itself novel** and should be framed as the organising idea rather
than a finding. Zero occurrences of "selection rate" or "base rate".

**The headline survived.** Across all 72 citing papers, four full texts searched directly,
and a dozen re-phrased queries, nothing was found that identifies the overall selection rate
as the predictor of direction, locates a crossover, or tests *Backfire*'s conditions on data.

**Coverage limit, stated rather than glossed.** Semantic Scholar's index lags for recent
work — *Backfire* itself has zero recorded citations at five months old — so anything from
the last few months that does not yet cite these three papers would be missed. This is a
serious sweep, not a proof of absence.

---

## 13. arXiv listing scan — the blind spot citations cannot cover

Citation-graph traversal misses work too new to have been cited, which is the case that
matters most here: the assistant's training data ends May 2026, and *Backfire* has zero
recorded citations at five months old. So the listings were scanned directly.

* Seven keyword queries across the field's vocabularies for this quantity — 170 papers.
* A broad sweep of every `cs.CY` and `cs.LG` abstract mentioning fairness, newest first —
  **563 papers, 2025-10-29 to 2026-08-19**, the day before the audit.

**730 distinct papers screened. Zero** contain both direction-change language and a rate
quantity in the abstract. The filter matches 13 and 15 papers on those conditions
separately, so it is discriminating rather than broken, and the intersection is genuinely
empty. The only on-topic 2026 paper in the whole sweep is *Backfire*, already read.

This covers the post-cutoff window directly rather than by inference, which is the specific
reassurance that was missing.
