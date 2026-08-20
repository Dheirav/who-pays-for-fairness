# The paper frame

Written before the experiments that followed it, because the shape of the argument decides
which experiments are worth running — and it earned that immediately, by making the
selection-rate question the obvious next thing to run. Thirteen documents exist; a paper
needs one claim they all serve, and everything that does not serve it is cut or deferred.

## The one sentence

> **A fairness constraint is satisfied in ways that neither the certifying metric nor the
> standard audit tools can describe — and for the largest of those, levelling down, theory
> says the direction is distribution-dependent while only measurement says which way, when,
> and from a quantity anyone can compute.**

The test of this framing is that it makes the project's *failures* load-bearing. Three
pre-registered explanations of the attribution shift were refuted and none replaced them.
Under any framing that owes the reader a mechanism, that is a hole. Under this one it is
the fourth instance of the thesis: the audit surface does not reveal what the constraint
did. Nothing has to be explained away.

## The abstract

> Group-fairness constraints of the reduction family (Agarwal et al., 2018) reliably do
> what they promise: on UCI Adult they drive the demographic parity violation from 0.186
> to 0.018 for under two accuracy points, on any base classifier, without modifying the
> training data. We audit what they do to get there, across Adult and 18 ACS Income
> populations spanning two protected attributes, and find four things the certifying
> metric does not report and standard auditing does not reveal. **(i)** Parity is reached
> by withdrawing favourable decisions rather than extending them — on Adult every method
> in a six-method ablation shrinks the total by 7.9–22.1%, and 18 of 19 survey populations
> shrink it — while the rate-level view understates the burden counted in people, with the
> divergence predicted by a cross-flow diagnostic (r = +0.885). On mortgage-approval data,
> the same constraint *grows* the pie by 4.3% at an exchange rate of 0.50. **The parity
> metric reports the same success in both cases**: 0.018 on the population that destroyed a
> fifth of its favourable decisions, 0.010 on the one that created more than it destroyed.
> A single-factor sweep — moving only the income cutoff on one fixed population, so that
> rows, features and groups are provably identical across arms — locates the moderator:
> the direction tracks the task's **selection rate**, crossing over between 0.25 and 0.60
> (r = +0.801, and +0.980 once the confounded base-rate gap is partialled out), from 22
> favourable decisions destroyed per one created at a rate of 0.03 to 0.75 at 0.89.
> **(ii)** A constraint on one attribute
> leaves intersectional subgroups worse off than any group it was told about, in every
> sufficiently diverse population and more severely than Adult suggests (9.0× against
> 13.2× in Mississippi). **(iii)** Below roughly 2,500 test subjects the method's own
> randomness exceeds the entire effect of the constraint. **(iv)** Feature-attribution
> audits do not recover the mechanism: three pre-registered explanations of an apparent
> +151% attribution shift are each refuted by intervention, and most of the shift proves
> to be credit reallocating between two collinear features. The first of these, however,
> is fixable by stating the missing objective outright. Adding a floor on the overall
> selection rate — a linear moment constraint inside the base paper's own framework, not a
> new method — preserves parity to the same tolerance while the exchange rate falls from
> 1.47 favourable decisions destroyed per one created to 0.88, for 0.12 accuracy points.
> **The exchange rate falls in all 19 populations and in both protected-attribute arms**,
> and in 16 of them lands below one, meaning the constrained model now creates more
> favourable decisions than it destroys. Fairness constraints do exactly what they are
> asked. The gap is between what is asked and what is meant, and nothing in the standard
> toolchain surfaces it.

## What each claim rests on

| claim | evidence | status |
|---|---|---|
| The method works as advertised | docs 02–04 | Solid. Background, not contribution |
| (i) Levelling down, and rate-vs-people | docs 05, 11, 13, 22, 23, 27 | Solid on survey data, 19 populations, diagnostic at r = +0.885. Reverses on mortgage data (doc 22), and **doc 23 identifies the moderator by single-factor sweep**: the selection rate, crossing over between 0.25 and 0.60. State the condition, never the bare claim. **The conditionality itself is anticipated by arXiv:2603.06901 (doc 27) — concede it in the first paragraph.** What survives: their conditions hold on 0/26 populations, ours proxies theirs at r = +0.927, and they have no experiments |
| (ii) Intersectional subgroups left behind | docs 07, 12 | **Strongest result in the project.** Replicates everywhere, with one stated condition |
| (iii) Arbitrariness below ~2,500 subjects | doc 15 | Solid but not novel — position as a caution, cite the multiplicity literature |
| (iv) Attribution audits do not recover it | docs 06, 16, 17, 18, 20 | Solid as a negative result. Do not oversell |
| The fix | docs 19, 21 | Strongest *useful* result. **Replicated across 19 populations, both arms, exchange rate down in 19/19.** Quote doc 21's typical numbers, not doc 19's Adult ones |
| Method: pre-registration and retraction | commit history, docs 13, 17, 20 | Underused. Belongs in the methods section as a reason to trust the numbers |

## What is cut

* **doc 14** (why the DP/EO conflict is unpredictable) — a genuinely separate paper. It
  answers a question this one does not ask.
* **doc 18** (the confounded collinearity design) — appendix. Its value is the structural
  argument for why the design cannot work, which is a methods note.
* **docs 16, 17, 20** — compressed into one paragraph of claim (iv). Three refuted
  explanations shown at length reads as confusion; shown in one paragraph it reads as
  rigour. The full record stays in the repository and is cited to it.
* **doc 09** (proxy removal) — one sentence inside claim (iv). It is a negative control,
  not a finding.

## Framing corrections to make while writing

* **The fix must not be sold as a discovery.** A constrained optimiser satisfies the
  constraints it is given; adding "do not shrink the pie" and getting an unshrunk pie is
  not surprising and a reviewer will say so. The finding is that **nobody asks**, and that
  the omission costs a fifth of all favourable decisions while every fairness metric
  reports success.
* **"19 populations" overstates the external validity.** They are US states sharing one
  survey instrument, one encoding and one threshold construction. Say "19 populations
  drawn from one survey" and stop leaning on the count.
* **Never quote Adult's fix numbers as typical.** −20.5% → −0.6% and 2.68 → 1.03 are the
  most extreme case in the study, roughly three times the typical effect (doc 21). Lead
  with 1.47 → 0.88 across 19 populations, which is smaller, unanimous, and defensible. The
  paper is about the audit surface being blind; getting caught overstating an effect on the
  one dataset everyone knows would be the worst possible way to lose that argument.
* **Neither the observation NOR the remedy is new.** `[VERIFIED, arXiv:2302.02404]`
  Mittelstadt, Wachter & Russell (2023) made levelling down the centre of a well-known
  critique — and their §6 proposes **minimum rate constraints**, a per-group selection-rate
  floor, demonstrated on Adult under demographic parity, reporting that levelling down does
  not occur. The selection-rate floor is a variant of a published remedy, not a discovery,
  and the paper must say so before a reviewer does. What survives: it is in-processing
  rather than post-processing (so no protected attribute at prediction time), it is a
  population-level floor stacked *with* parity rather than a per-group floor replacing it,
  and it is replicated on held-out data across 22 populations where they report Adult's
  training set. **Lead with the scope condition (doc 23), which they do not have.**

## Known before submission

1. ~~One dataset that is neither Adult nor ACS.~~ **Done** — HMDA Mississippi 2018, both
   arms (doc 22). It immediately paid for itself by breaking claim (i)'s universality,
   which nineteen more ACS states could never have done. ~~And the threshold sweep that
   would say why.~~ **Also done** (doc 23): the selection rate is the moderator and it
   survives partialling out the base-rate gap. What remains is a **second state** for the
   sweep — the crossover is currently a range from one population, and Adult sits an order
   of magnitude away from Alabama at a comparable rate, so the selection rate is clearly
   not the whole story.
2. The selection-rate floor benchmarked against minimax group fairness and decoupled
   classifiers, not only against plain ExpGrad.
3. More seeds and interval estimates on the small populations, or claim (iii) undercuts
   the rest of the paper's point estimates.

Target venue: FAccT or AIES. Not ICML/NeurIPS — there is no new algorithm here and the
theory content is thin, which is a description of the work rather than a complaint about it.
