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
minority-size condition attached. Cite without qualification.

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

## 8. *Resource-constrained Fairness* (2024) — **new, and worth citing**

arXiv:2406.01290. Not in the original draft; surfaced while checking whether the
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
