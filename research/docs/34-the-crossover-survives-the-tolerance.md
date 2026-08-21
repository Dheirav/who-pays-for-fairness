# 34 — The crossover is a property of the constraint, not of how tightly it is set

**Individual work, beyond the course submission.** **Post-hoc and labelled as such**: no
prediction was registered before this run. It re-runs an existing sweep at two further
constraint tolerances and reports whether the earlier conclusion moves. There is no bar to
clear here because the bars are document 23's, already fixed, and the question is only
whether they are still cleared.

## The objection this answers

Every result in documents 22, 23, 31 and 32 is measured at a single constraint tolerance,
ε = 0.01. That is a confound the project named itself: the plan deck's "Contribution 5 — is
it the constraint, or just a tight one?" says so in as many words, and
[document 23](23-the-selection-rate-sets-the-direction.md) never tested it.

If the crossover moves with ε, then "the direction of levelling down tracks the selection
rate" is a statement about one hyperparameter setting rather than about the constraint, and
the paper would be overclaiming.

## The design

Alabama's six income-cutoff arms, five seeds, re-run at **ε = 0.05** and **ε = 0.002** —
a twenty-five-fold range around the default. Nothing else changes. Arms are excluded by
document 23's rule (baseline parity gap below 0.05), which drops the same two arms at every
tolerance, so the three sweeps cover identical populations.

## The result

| ε | r | partial r | pie at rate 0.099 | pie at rate 0.760 | sign flips | crossover bracket |
|---|---|---|---|---|---|---|
| 0.05 (loose) | **+0.944** | +0.999 | −4.97% | +0.11% | yes | **0.252 – 0.598** |
| 0.01 (default) | **+0.801** | +0.980 | −22.05% | +0.80% | yes | **0.252 – 0.598** |
| 0.002 (tight) | **+0.784** | +0.976 | −22.16% | +0.85% | yes | **0.252 – 0.598** |

T0, T1, T2 and T3 hold at all three tolerances.

**The crossover bracket is identical across a twenty-five-fold range of ε.** The same arms
shrink the pool and the same arms grow it; no arm changes sign. The correlation stays well
above document 23's bar of +0.70 throughout, and the partial correlation holding the
base-rate gap fixed is above +0.97 in every case.

## What this establishes, and what it does not

**Established: the direction result is not an artifact of a tight constraint.** The objection
the project raised against itself does not hold. Loosening the tolerance five-fold or
tightening it five-fold leaves both the relationship and the location of the transition where
they were.

**Not established: the magnitude.** The size of the effect is strongly ε-dependent, and more
so than anything else measured here. At the lowest-rate arm the pool shrinks by 4.97% at
ε = 0.05 and by 22.16% at ε = 0.002. On the excluded arm at a selection rate of 0.03 the
range is wider still — 5.07%, 29.71%, 50.83% — though nothing rests on that arm.

Notice also that ε = 0.01 and ε = 0.002 give nearly the same magnitudes (−22.05% against
−22.16%) while ε = 0.05 gives a quarter of it. The relationship with ε is not linear: past
some point the constraint is binding as hard as it can and tightening it further changes
little.

## Extended to five populations

Oregon, Connecticut, Kentucky and South Carolina were added afterwards at both tolerances.

| state | ε = 0.05 | ε = 0.01 | ε = 0.002 | sign flip at every ε | spread |
|---|---|---|---|---|---|
| Alabama | +0.944 | +0.801 | +0.784 | yes | large |
| Oregon | +0.851 | +0.964 | +0.963 | yes | large |
| Kentucky | +0.817 | +0.802 | +0.799 | yes | 16.4 pts |
| South Carolina | +0.898 | +0.880 | +0.873 | yes | 14.5 pts |
| **Connecticut** | **−0.924** | **−0.130** | **−0.332** | **no** | **0.34 pts** |

**Four of five hold at every tolerance. Connecticut fails at all three.**

Connecticut fails for the same reason it fails every other test in this project, and the
reason is not the tolerance: its four arms span selection rates 0.306–0.821 and **all of them
level up**, by between 0.05% and 0.14% at ε = 0.05. No arm sits below the crossover, so there
is no sign change, and the correlation is fitted to a spread of a third of a percentage point.
Its sign is unstable across ε — −0.924, −0.130, −0.332 — which is what a correlation over
noise does.

**By sign, the rule is right about Connecticut at every tolerance**: high rates, pool grows,
four times over. The pre-registered T1 has no minimum-spread guard — document 33's E0, written
later, does — so it scores an uninformative arm set as a refutation. That defect belongs to
document 23's design and is recorded in
[document 32](32-the-rate-not-the-task.md).

**What survives unqualified:** in every population where the arms actually span the crossover,
the bracket does not move across a twenty-five-fold range of ε.

## Where this leaves the project's three manipulations

Three independent ways of moving the selection rate or the constraint now agree on the same
split:

| manipulation | direction | crossover location | magnitude |
|---|---|---|---|
| income cutoff → operating point ([doc 32](32-the-rate-not-the-task.md)) | same | same | **differs 3×** |
| ε across 25× (this document) | same | same | **differs 4×** |
| parity → equalized odds ([doc 33](33-the-rule-does-not-survive-equalized-odds.md)) | weaker | — | **differs 8×** |

**The selection rate predicts which way. It does not predict how much.** That is now the
project's most heavily replicated claim and also its clearest limit, and both halves should
be stated together wherever it appears.
