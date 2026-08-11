# 08 — Consolidated comparison with the base paper

**Agarwal, Beygelzimer, Dudík, Langford & Wallach (2018), "A Reductions Approach to
Fair Classification", ICML.**

This document collects every finding in the project and sorts it into three piles:
what confirms the paper, what extends it, and what contradicts something. The
distinction matters, because it is easy to present an "extension" as though it were a
refutation, and easy to present a refutation of the *initiation document* as though it
were a refutation of the *paper*. Both errors are avoided here explicitly.

## A note on what is being compared

Absolute numbers are **not** compared against the paper's published figures. The
preprocessing differs (listwise deletion, two dropped columns), the split differs, and
the base classifiers differ. What is compared is whether the paper's **claims** hold
in shape and magnitude on an independent implementation. Where a claim is
characterised rather than quoted, it is characterised from the method's stated
structure, not from a remembered table.

---

## Pile 1 — Confirmed

| Paper's claim | Evidence here | Document |
|---|---|---|
| The reduction drives the fairness violation toward ε for a modest accuracy cost | DP: 0.161 → 0.019 (−88%) for 1.5 accuracy points on a decision tree | [03](03-base-paper-reproduction.md) |
| EO constraint likewise | EO: 0.083 → 0.036 (−57%) for 0.5 accuracy points | [03](03-base-paper-reproduction.md) |
| The base classifier is a black box — any cost-sensitive learner works | Identical wrapper, unmodified, on a depth-8 decision tree *and* on logistic regression; both worked | [03](03-base-paper-reproduction.md), [04](04-ablation.md) |
| The training data is never modified | Reweighting is internal to the objective; no row duplicated, dropped, relabelled, or edited in any of the six methods | [01](01-setup-and-method.md) |
| GridSearch traces a usable accuracy-vs-fairness frontier | 15-point sweep produces a clean frontier on both constraints | [03](03-base-paper-reproduction.md) |
| The output is a randomized classifier | Confirmed, and measured — see pile 2 | [05](05-who-pays.md) |

**The base paper's method works.** That is the honest headline, and nothing below
undoes it. On the problem it defines, it solves it well and cheaply.

---

## Pile 2 — Extended (outside the paper's frame, not against it)

Agarwal et al. is a paper about **feasibility and optimality**: given a constraint,
find the most accurate classifier that satisfies it. Every finding below is a question
that frame does not ask.

### 2.1 The constraint is satisfied — but who was moved to satisfy it?

The paper reports that the violation fell. It does not decompose *how*. A gap can
close by lifting the disadvantaged group or by lowering the advantaged one, and the
metric is identical either way.

**Result:** measured in rates, all five mitigations look even-handed (0.50–0.58 of the
closure paid by the privileged group). Measured in **people**, they are lopsided
(0.66–0.74), because the privileged group is 2.1× larger and equal rate movement is
unequal headcount. ExpGrad-DP: **909 men lost a favourable decision so that 316 women
could gain one.**

→ [Document 05](05-who-pays.md)

### 2.2 The accuracy cost is reported — the welfare cost is not

Demographic parity constrains a *ratio*, not a total. Every method here satisfied the
constraint while **reducing the total number of favourable decisions**, by 7.9% to
22.1%. Not one closed the gap primarily by extending favourable decisions downward.

This is invisible in accuracy, DP, EO, and disparate impact simultaneously. Nothing in
the paper's reported quantities would reveal it.

→ [Document 05](05-who-pays.md); Mittelstadt, Wachter & Russell (2023)

### 2.3 Randomization is proven necessary — its cost to individuals is not measured

The paper is explicit that the output is a distribution over classifiers, and the
randomization is what makes the optimality theory work. Two draws from the *same
fitted model* disagree on **3.18%** of subjects for ExpGrad-EO, against a total change
of 5.17% versus baseline — so **≈62% of the individual-level effect is re-sampling,
not fairness**. The same applicant applying twice can receive different answers.

This is a real cost that falls on individuals rather than on the aggregate, and it
does not appear in any group metric. It connects to predictive multiplicity (Marx,
Calmon & Ustun 2020; Cooper et al. 2024).

→ [Document 05](05-who-pays.md)

### 2.4 The method never needs the protected attribute at inference — but the model reconstructs it

The reduction's operational selling point is that the deployed classifier does not
require `sex`. True. But SHAP attribution shows that **ExpGrad-DP increases its
reliance on sex proxies by 9.7% over the unmitigated baseline**, and both
DP-constrained methods **more than doubled** their use of `relationship` (+108%) — a
feature whose levels are Husband and Wife.

The mechanism is not mysterious: to equalise selection rates across sex while
forbidden to read sex, the model must infer sex in order to compensate. **The
constraint creates demand for a reconstruction of the protected attribute.**

The paper makes no claim about feature reliance, so this contradicts nothing in it. It
does qualify a claim the field routinely makes on the method's behalf: not requiring
`sex` at inference is a property of the API, not of the model's reasoning.

→ [Document 06](06-proxy-reliance-shap.md)

### 2.5 Two method families the paper does not compare against

The paper benchmarks against Zafar et al. This project adds Kamishima's Prejudice
Remover and Zhang et al.'s Adversarial Debiasing under identical data, base
classifier, split, and metrics — implemented from their papers, verified against
degenerate cases. Result: **Prejudice Remover is the most *efficient* method**
(11.7 parity points per accuracy point, ~30% better than ExpGrad-DP) while reaching a
higher floor (DP 0.065 vs 0.018), and carries a disparate-treatment caveat the
reductions rows do not.

→ [Document 04](04-ablation.md)

### 2.6 Single-attribute constraints, multi-attribute reality

The paper's formulation admits multiple protected groups, so this is not a gap in the
method — it is a gap in how the method is used, in the paper's own Adult experiments
and in nearly all applied work since.

**Result:** constraining on `sex` takes the sex gap to 0.020 while leaving a
**0.178 gap at Sex × Race — 9× larger than the number on the dashboard.** Black men are
selected at 9.2% against Asian men at 30.7% in a model whose sex-level DP difference is
0.028. And the sex constraint **moved the worst-off subgroup from Black women to Black
men**, who were protected by no constraint at all and became the residual.

Constraining on the intersection instead fixes it (0.178 → 0.048) for 1.7 accuracy
points, and is the only arm in the entire project that **lifts the floor** — the
worst-off subgroup's selection rate triples, 0.052 → 0.157.

A separate finding: **five of the ten Sex × Race subgroups are too small to measure**,
one having zero positive labels. 70% of the intersectionally-constrained arm's apparent
gap comes from those cells. Most published intersectional heatmaps on Adult are
reporting sampling noise.

→ [Document 07](07-intersectional.md)

---

## Pile 3 — Contradicted

**Nothing in the base paper is contradicted by this project.** Two predictions *are*
contradicted, and both come from the initiation document, not from Agarwal et al.

### 3.1 "Adversarial training is typically higher-variance than convex/Lagrangian approaches"

*(Initiation document, section 5)*

**False on this data, and inverted.** Adversarial Debiasing is the **most** stable
method in the study (accuracy std 0.0011). GridSearch — a deterministic sweep with no
adversary and no minibatching — is the **least** stable, by 6× on accuracy and 3× on
disparate impact.

The cause is model *selection*, not stochastic training: GridSearch takes a discrete
argmax over a coarse 15-point λ grid, and a small change in the data flips which grid
point wins, moving the answer discontinuously. Adversarial Debiasing has no selection
step.

**This does touch the base paper indirectly.** GridSearch is presented there as the
practical alternative for binary protected attributes, and its frontier is its selling
point. This result suggests that its *variance across resamples* should be reported
alongside that frontier, because the frontier looks smooth while the selection on it
is fragile. That is a caution, not a refutation.

→ [Document 04](04-ablation.md)

### 3.2 "SHAP … to visually show reliance on `sex` and its proxies **shrinking** post-mitigation"

*(Initiation document, section 6)*

**False for the two best DP methods, which increased proxy reliance** (+9.7% and
+7.3%). Only Adversarial Debiasing reduced it meaningfully (−12.9%), and even it
retains 47.6% of attribution on proxies.

The prediction assumed mitigation works by *removing* the model's access to
sex-related signal. For constraint-based reductions it works by *using* that signal to
compensate. The stretch goal was worth doing precisely because its stated expectation
was wrong.

→ [Document 06](06-proxy-reliance-shap.md)

---

## What a practitioner should take from this

1. **Use the reduction.** It works, it is cheap, it wraps anything, and it leaves your
   data alone. Piles 1 and 2 do not argue against it.
2. **Do not report the gap alone.** Report the decomposition. "DP fell from 0.186 to
   0.018" and "909 men lost approval so 316 women could gain it, and 570 fewer people
   were approved overall" are both true, and only the second describes what happened.
3. **Say which metric.** Four of five mitigations here made equalized odds *worse than
   no mitigation at all* while improving demographic parity. "We made the model fair"
   is not a well-formed claim on data with unequal base rates — it cannot be, by the
   impossibility results.
4. **Do not treat the absence of `sex` from the feature list as evidence of anything.**
   The proxies carry it, and tightening a fairness constraint made the model lean on
   them harder.
5. **If you use a randomized classifier, quantify its arbitrariness floor** before
   attributing individual-level changes to your fairness intervention. Here it
   accounted for the majority of one method's effect.
