# 43 — The rule belongs to one regime, and the theory that names the regimes is right about it

**Individual work, beyond the course submission.** P1 was fixed in
`src/experiments/analyse_dense.py` and committed before any post-processed arm was run. The
check in the second half of this document was decided **after** P1 failed and is labelled
post-hoc.

## The objection this closes

Every directional result in this project comes from one optimiser: the reduction of Agarwal et
al. (2018). "This is a property of that algorithm, not of fairness constraints" had no answer,
and [document 41](41-two-scope-tests-one-void-by-my-own-error.md)'s attempt to answer it was
void by construction — `ThresholdOptimizer` re-derives its own thresholds and returned an
identical model at all six operating points.

The design document 41 named is used here instead: **vary the population, not the decision
rule.** Post-processing runs at each population's own natural operating point across eighteen
populations, and the correlation is taken across them.

## P1 — the prediction fails, decisively

| | r across 17 populations |
|---|---|
| the reduction (in-processing) | **+0.585** |
| post-processing | **−0.024** |

The bar was +0.70 and the naive alternative — *"the direction is a property of Agarwal's
reduction; under a structurally different optimiser there is no relationship"* — needed
|r| < 0.30 to win. **It won.** Not weakly: −0.024 is indistinguishable from no relationship at
all, on the same populations where the reduction gives +0.585.

Taken alone this is the most damaging result in the project. The selection rate does not
predict the direction under post-processing.

## Why it fails, and it is not fragility

Post-processing reads the protected attribute at prediction time. The reduction does not. That
is not an implementation detail — it is the distinction the theory paper this project has been
arguing with builds its result on.

*Fairness May Backfire* (arXiv:2603.06901) separates two regimes:

* **attribute-blind**, where the attribute is unavailable at decision time: "the impact of
  fairness is distribution-dependent: fairness can benefit or harm either group ... leading to
  either leveling up or leveling down";
* **attribute-aware**: fairness "**necessarily** (weakly) improves outcomes for the
  disadvantaged group and (weakly) worsens outcomes for the advantaged group".

Everything else in this project is attribute-blind, which is the regime where the theory says
the direction is distribution-dependent — and where a rule predicting which way it goes is
therefore a meaningful thing to look for.

**Post-processing is attribute-aware. In that regime the theory says there is nothing to
predict**, because the direction is determined rather than distributional. A correlation of
−0.024 is what "determined" looks like from the outside.

## The post-hoc check, and it is unanimous

If the theory is right about the attribute-aware regime, then under post-processing the
advantaged group should lose and the disadvantaged group should gain, everywhere, with no
exceptions.

**It does, in 18 of 18 populations** — Adult, twelve ACS states, two HMDA states, COMPAS, the
Dutch census and LSAC. Not a majority; every one.

**That check was decided after P1 failed and was post-hoc.** It has since been repeated as a
**confirmatory** test: nine populations that had never been post-processed — Taiwan 2005 and
the eight ACS states of the sealed prediction — with the bar set at *all nine* and committed
before any of them ran, because the theorem says "necessarily" and a majority is not the claim.

**It holds 9 of 9.** So the regime result now stands at **27 of 27**, of which nine were
predicted in advance. It remains a confirmation of an existing theoretical prediction rather
than a discovery, and not a rescue of P1.

## What this does to the project's position

Document 27 found that *Backfire*'s **conditions** — the ordering relations its theorem is
stated over — **cannot be evaluated on any of 26 arms**, because they are stated over extrema
that diverge on real data. They are *sufficient, not necessary*, so the theorem is **silent**
there rather than wrong, and a relaxed form of the same ordering tracks the direction on 24 of
26. This document finds that its **regime distinction** holds on **27 of 27**.

Those are not in tension and together they are a better position than either alone. The theory
is right about *which regime you are in mattering*, and wrong about *which quantity decides it
within a regime* — the second is precisely what an empirical paper can settle and a
population-level Bayes argument cannot.

**The scope of this project's claim narrows and sharpens.** It is a claim about **attribute-blind
in-processing constraints**: the regime where the theory says the direction is undetermined, and
where a practitioner therefore cannot know which way their system will go without measuring
something. That is the regime almost every deployed system is in, because per-group thresholds
are disparate treatment on their face in most jurisdictions.

Stated the other way round: **if you can legally use the protected attribute at decision time,
you do not need this project's rule** — the direction is determined, and post-processing will
lift the disadvantaged group and lower the advantaged one every time. If you cannot, the
direction is undetermined and the selection rate is the best predictor of it currently
available.

## What it costs

The paper can no longer say "fairness constraints" without qualification anywhere. Every claim
becomes a claim about attribute-blind in-processing, and the abstract, the contributions and
the discussion all need the qualifier.

That is a smaller claim than the one in the previous draft, and it is the first version of it
that is bounded on the side a reviewer would have attacked first.
