# Research — individual work beyond the course submission

**Everything in this folder is work done by Dheirav alone, after the course
deliverable was complete.** It is not part of the team submission and no part of it is
required by the course specification.

The course deliverable is `bias_mitigation_report.pdf`, `bias_mitigation_plan.pptx`, and
[`docs/01`–`docs/10`](../docs/README.md). Those cover UCI Adult only and are complete on
their own terms. Nothing here is needed to read or assess them.

## The boundary, and how to verify it

The deliverables were finalised at commit `28bc8d1` (11 Aug, 23:49). **Every commit
after that point is this folder's work.** To list them:

```
git log --oneline 28bc8d1..HEAD
```

That command is given instead of a table of hashes because a table goes stale — and this
one did. It was written out by hand, then the history was rewritten to strip co-author
trailers, and six of the twelve hashes it named stopped existing. The rule survives
rewrites; individual hashes do not.

Each of those commits states what it did and why, and the messages are the substantive
record: what was predicted, what failed, and what was retracted.

Git history is the authoritative record of authorship here, not directory layout —
which matters because one part of this work **cannot** be moved into this folder.

## What could not be separated

These modules are individual work but live in `src/`, because they are inside the Python
package and moving them would break imports:

| file | |
|---|---|
| `src/datasets/acs.py` | ACS Income loader, both protected-attribute arms |
| `src/experiments/analyse_sweep.py` | P1/P2/P3 across populations |
| `src/experiments/analyse_arms.py` | the pre-registered two-arm analysis |
| `src/experiments/analyse_conflict.py` | the pre-registered DP/EO conflict analysis |
| `src/experiments/analyse_attribution.py` | the post-hoc decomposition of document 06's share |
| `src/experiments/analyse_levelling_up.py` | the pre-registered replication of document 19 |
| `src/datasets/hmda.py` | HMDA mortgage loader, both protected-attribute arms |
| `src/experiments/analyse_threshold.py` | the pre-registered income-threshold sweep |
| `src/experiments/analyse_ratio.py` | the pre-registered ratio x threshold design |
| `src/experiments/analyse_mechanism.py` | the pre-registered derivation of the crossover |
| `src/experiments/analyse_zeta.py` | the correspondence check against arXiv:2603.06901 |
| `src/baselines.py` | group-wise thresholds and minimax group fairness |
| `src/experiments/run_baselines.py` | the five-arm comparison against existing remedies |

They cannot be **moved** here, but they are **excluded from the submission bundle**:
`datasets.build` imports the ACS loader lazily, inside the branch that requests it, so
the course code neither imports nor needs any of them, and the HMDA loader is imported the
same way. `scripts/build_submission.py` drops every file in that table, and the resulting
bundle was unpacked and its suites run to confirm it stands alone.

Three shared files were also extended for this work — `src/results_io.py`,
`src/datasets/base.py`, `src/datasets/__init__.py` — and those changes improved the
course-side code as a side effect. They are not claimed as exclusively individual.

## The documents

| # | Document | What it answers |
|---|---|---|
| 11 | [Replication across populations](docs/11-replication-across-populations.md) | Which findings are about the method, and which about Adult? |
| 12 | [Intersectional across populations](docs/12-intersectional-across-populations.md) | Gerrymandering replicates, and is worse than Adult showed |
| 13 | [Separating ratio from size](docs/13-separating-ratio-from-size.md) | A second protected attribute breaks a confound, and retracts document 11's correction |
| 14 | [Why the conflict is unpredictable](docs/14-why-the-conflict-is-unpredictable.md) | P2's magnitude resisted prediction because the endpoint is independent of the starting point |
| 15 | [Arbitrariness at small scale](docs/15-arbitrariness-at-small-scale.md) | On small populations the method's own randomness exceeds the entire effect of the constraint |
| 16 | [Planting a proxy](docs/16-planting-a-proxy.md) | The intervention refutes document 06's mechanism: a planted proxy is used *less*, not more |
| 17 | [Neither explanation survives](docs/17-neither-explanation-survives.md) | The replacement fails too; the constraint barely changes which features are used |
| 18 | [The collinearity test is confounded](docs/18-the-collinearity-test-is-confounded.md) | The third candidate resisted a clean test; why the design cannot work |
| 19 | [Levelling up is expressible](docs/19-levelling-up-is-expressible.md) | Put "don't shrink the pie" in the objective and you get it, for 0.37 accuracy points |
| 20 | [What a share can carry](docs/20-what-a-share-can-carry.md) | Most of the +151% is credit moving inside one collinear pair; document 17's claim is narrowed |
| 21 | [The floor replicates](docs/21-the-floor-replicates.md) | The selection-rate floor holds across 19 populations; Adult was the extreme case, and one prediction failed |
| 22 | [Levelling down is not universal](docs/22-levelling-down-is-not-universal.md) | A second *domain*: on mortgage decisions the constraint levels up unprompted, and document 05 gains a scope condition |
| 23 | [What decides the direction](docs/23-the-selection-rate-sets-the-direction.md) | Move one number and the direction flips: levelling down happens below a selection rate of ~0.3 |
| 24 | [Group ratio is not the residual](docs/24-group-ratio-is-not-the-residual.md) | The candidate for the leftover magnitude is refuted, with the opposite sign; document 23 gains a second protected attribute |
| 25 | [Against the existing remedies](docs/25-against-the-existing-remedies.md) | The optimal DP classifier levels down too; minimax is not the remedy it is taken for |
| 26 | [The derivation does not earn its keep](docs/26-the-derivation-does-not-earn-its-keep.md) | A mechanism passes its pre-registered bars and is beaten by a constant; the identity survives |
| 27 | [The theory and the measurement agree](docs/27-the-theory-and-the-measurement-agree.md) | A 2026 theory anticipates the claim; its conditions never hold on data, and our rule proxies it at r = +0.927 |

## The short version

Documents 01–10 are all measurements on one dataset. Ding et al. (2021), *Retiring
Adult*, argues the field should stop drawing conclusions from exactly that dataset. Until
a finding survives a population it was not derived from, "the constraint causes X" and
"Adult has property X" are indistinguishable. These documents test that, on 19 survey
populations across two protected attributes — and then, in document 22, on a domain that is
not a survey at all.

**Where this sits in the literature, after checking.** Two of this folder's claims turned
out to be anticipated, and both were found by reading rather than assumed. The
selection-rate floor is a variant of Mittelstadt et al.'s minimum rate constraints
(document 19's correction). And the *conditionality* of levelling down — that it can go
either way rather than being a default — is proven in arXiv:2603.06901 (March 2026), five
months before this project reached it independently. What survives that collision is the
empirical half, and document 27 makes the case precisely: their conditions are satisfied on
**0 of 26** populations because the quantity they are stated over diverges on real data,
their direction is right once relaxed (24–25 of 26), and the overall selection rate proxies
their structural quantity at **r = +0.927** while requiring nothing but a historical
approval rate. Independent theory and independent measurement converging.

**What did not survive a second domain.** Every population above is a household survey. On
**HMDA mortgage decisions** — an administrative record of real lending outcomes rather than
a survey — the demographic parity constraint **levels up unprompted**, growing favourable
decisions by 4.3% at an exchange rate of 0.50 while removing 94% of the parity violation
(document 22). Twenty populations point one way and the twenty-first and twenty-second point
the other. Nothing in documents 05 or 21 is retracted; what changes is their reach.
Levelling down is a property of the fairness-constrained problems this project had been
looking at, not of demographic parity constraints in general. The parity metric reports the
same success either way, which is the project's through-line stated as sharply as it gets.

**What replicated.** The intersectional result is the strongest thing here: fairness
gerrymandering appears in every sufficiently diverse population and is *worse* than Adult
showed — 9.0× there against 13.2× in Mississippi (document 12). It gains one condition,
that the effect needs a substantial minority to hide in, and that condition is the first
relationship in the project whose two candidate explanations are not confounded with each
other. In five of ten populations the worst-off subgroup after a sex constraint is a
minority man, and in three it is Black men specifically — document 07's Adult finding,
reproduced without being looked for.

**What needed conditions attached.** The rate-versus-people divergence holds when the
mitigation performs a clean transfer, and degrades in proportion to cross-flow, which
rises both with group inequality and with small samples (documents 11 and 13). The
DP/EO conflict is near-universal in direction across populations but **reverses** across
protected attributes, because the post-constraint EO violation is independent of the
pre-constraint one — the endpoint belongs to the constrained problem rather than to the
model it replaced, confirmed by two independently-derived solvers landing within 0.02 of
each other (document 14).

**What was refuted, including my own claims.** Document 11's confident correction of
itself was wrong and is retracted (document 13): the tentative first reading was right,
and group ratio is a genuine cause acting through cross-flow rather than a spurious
correlate. Document 06's proposed mechanism — that the constraint seeks reconstructions of
the protected attribute — is refuted by intervention: a planted proxy is used *less* as it
sharpens (document 16). Its replacement is refuted too (document 17). The third candidate,
collinear reallocation, resisted the intervention designed for it (document 18) but is
**partially supported** by re-aggregating the existing result: scoring Adult's two most
redundant features as one coalition takes the +151% down to +11.6% (document 20). Most of
the headline is credit moving between near-substitutes. The remaining +11.6% is
seed-consistent and still unexplained.

**What that produced instead.** Across six cells the constrained model's attribution
tracked the unconstrained model's to within 0.03 share while the share itself moved
ninefold. That was originally stated as *the demographic parity constraint does not
systematically change which features the model leans on*; document 20 narrows it to the
planted column it was measured on, because attribution *shares* are compositional and
cannot identify which features a model leans on — and because Adult contradicts the
general form. What survives is constraint-specific and interesting on its own: holding the
algorithm fixed, demographic parity raises the collinear pair's combined share while
equalized odds lowers it. And on small populations the method's own randomness exceeds the
entire effect of the constraint — in 5 of 38 randomized runs, all of them below 2,500 test
subjects (document 15).

**What could be fixed.** Document 05 ended by claiming that levelling up would have to be
part of the objective or it would not happen. It was never tested; it is now, and it holds
(document 19). Adding one linear constraint — a floor on the overall selection rate —
satisfies parity to the same tolerance while the pie loss falls from **−20.5% to −0.6%**,
and the exchange rate goes from **2.68 favourable decisions destroyed per one created to
1.03**. It costs 0.37 accuracy points. This is not a new method; a selection-rate floor is
a linear constraint on a conditional moment and sits inside the base paper's own
framework. The finding is about objectives, not algorithms.

That claim has since been through the same replication as everything else here, and it
holds: across **19 populations and both protected-attribute arms, the exchange rate fell in
every one**, from 1.47 to 0.88 in the sex arm and 1.59 to 0.79 in the race arm (document
21). Two things needed correcting. Adult is the **extreme** case rather than the typical
one — its −20.5% pie loss sits against a −6.1% mean elsewhere — and the floor does not
merely protect the pie, it *grows* it, in 18 of 19 populations. One of that document's five
pre-registered predictions failed, and the failure is recorded rather than repaired.

**The through-line.** A fairness metric describes an outcome state, not a mechanism. Every
headline number in documents 02–04 is correct and every finding above is invisible in it.
When this project tried to identify the *mechanism* behind one of those findings, three
candidate explanations were proposed and none survived. When it instead tried to *fix* one
of them by stating the missing objective outright, that worked immediately. The reduction
is agnostic about how it satisfies a constraint because the constraint is all it is told —
which is a limitation of what we ask for, not of the method.

## What this does not change

**Nothing in documents 01–10 is retracted.** The Adult measurements were correct and have
been re-verified. Two claims *added after* those documents were written have been scoped
or withdrawn, and both retractions are recorded in place rather than edited away.

The course deliverables are unaffected, and this was checked rather than assumed: the
formula that failed appears in neither the report nor the deck, and their who-pays
section is explicitly scoped to Adult ("the privileged group *here* is 2.1× larger").
Where the replication touches a deliverable claim at all, it strengthens it — the
"Black men become the residual" finding now replicates independently in Mississippi and
Alabama, and the report's reliability warning turns out to be understated rather than
overstated.

## Replication note for document 05

[Document 05](../docs/05-who-pays.md) reports that the burden of the fairness fix looks
near-even in *rates* and lopsided in *people*. That measurement is Adult, and it stands.

The **generalisation** of it — that the rate-to-people conversion is pure population
arithmetic — was claimed after that document was written and does not survive as stated.
It holds when the mitigation performs a **clean transfer**: privileged lose, unprivileged
gain, nobody moving the other way. Adult's cross-flow share is 0.045 and the conversion
predicts it to within 0.014; on populations under ~10,000 rows cross-flow reaches 0.3–0.4
and the error grows fivefold.

The diagnostic is the cross-flow share,
`(priv_gained + unpriv_lost) / (priv_lost + unpriv_gained)`, which correlates with the
conversion's error at **r = +0.885** across nineteen populations. Both group inequality
and small samples raise it, independently — see
[document 13](docs/13-separating-ratio-from-size.md).

This note lives here rather than in `docs/05` so the course-side documents contain only
work within the course scope.
