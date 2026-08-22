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
| `src/experiments/analyse_uncertainty.py` | cluster-bootstrap intervals for the headline correlations |
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

## What is planned next

[`NEXT.md`](NEXT.md) is the live handover: each remaining weakness, what closes it, what
would count as a failure, and which items need pre-registering.

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
| 21 | [The floor replicates](docs/21-the-floor-replicates.md) | The selection-rate floor holds across 19 arms from 10 populations; Adult was the extreme case, and one prediction failed |
| 22 | [Levelling down is not universal](docs/22-levelling-down-is-not-universal.md) | A second *domain*: on mortgage decisions the constraint levels up unprompted, and document 05 gains a scope condition |
| 23 | [What decides the direction](docs/23-the-selection-rate-sets-the-direction.md) | Move one number and the direction flips: levelling down happens below a selection rate of ~0.3 |
| 24 | [Group ratio is not the residual](docs/24-group-ratio-is-not-the-residual.md) | The candidate for the leftover magnitude is refuted, with the opposite sign; document 23 gains a second protected attribute |
| 25 | [Against the existing remedies](docs/25-against-the-existing-remedies.md) | The optimal DP classifier levels down too; minimax is not the remedy it is taken for |
| 26 | [The derivation does not earn its keep](docs/26-the-derivation-does-not-earn-its-keep.md) | A mechanism passes its pre-registered bars and is beaten by a constant; the identity survives |
| 27 | [The theory and the measurement agree](docs/27-the-theory-and-the-measurement-agree.md) | A 2026 theory anticipates the claim; its conditions never hold on data, and our rule proxies it at r = +0.935 |
| 28 | [How uncertain the correlations are](docs/28-how-uncertain-are-the-correlations.md) | Cluster-bootstrap intervals; the effect is not carried by the lending populations |
| 29 | [Where real decisions actually sit](docs/29-where-real-decisions-actually-sit.md) | The punchline was wrong: deployed systems span the crossover, from 0.02 in hiring to 0.84 in mortgages |
| 30 | [Novelty audit](docs/30-novelty-audit.md) | Every claim checked against 72 citing papers and five full texts: what is new, what is not |
| 31 | [The crossover on natural data](docs/31-the-crossover-on-natural-data.md) | A real lending product at 0.555 levels down while refinancing levels up — the transition observed, not manufactured |
| 32 | [The rate, not the task](docs/32-the-rate-not-the-task.md) | Move only the model's decision line: the direction reproduces in 4 of 5 populations, the crossover *location* in 3 of 5. Kentucky's routes disagree, Connecticut never crosses, and on lending the route fails outright |
| 33 | [The rule does not survive equalized odds](docs/33-the-rule-does-not-survive-equalized-odds.md) | **A failed pre-registration**, and it fails harder on five states than on two: +0.644 → +0.334. The claim is about criteria that constrain selection rates |
| 34 | [The crossover survives the tolerance](docs/34-the-crossover-survives-the-tolerance.md) | Identical crossover across a 25× range of ε, in 4 of 5 populations. Connecticut fails on a spread of 0.34 points — exposing that doc 23's T1 lacks the minimum-spread guard doc 33's E0 has |
| 35 | [What to actually do about it](docs/35-what-to-do-about-it.md) | The decision procedure, including how to measure your own crossover on the model you already have |
| 36 | [Not a property of linear models](docs/36-not-a-property-of-linear-models.md) | Boosted trees give the same crossover as logistic regression in **5 of 5** populations — the only test here that holds everywhere. Connecticut flips under trees where it never does under a linear model |
| 37 | [The guard that should have been there](docs/37-the-guard-that-should-have-been-there.md) | A correction to this project's own method: T1 fixes a correlation bar but no minimum movement. All 20 arm sets re-scored — three are void, none ever passed on noise |
| 38 | [The population counts were arm counts](docs/38-the-population-counts-were-arm-counts.md) | Every 'N populations' claim recomputed from its source file. 19 is 19 arms from 10 populations; 26 is 26 arms from 15. No measurement changes; the independence of the evidence does |
| 39 | [Three more instruments](docs/39-three-more-instruments.md) | COMPAS, LSAC bar passage and the Dutch census 2001. The rule reproduces on criminal justice (+0.870) and on a non-US census with twice Adult's group gap (+0.915). Document 15's 2,500-subject floor predicted COMPAS's noise correctly, on data it never saw |
| 40 | [The arms that were worse than doing nothing](docs/40-the-arms-that-were-worse-than-doing-nothing.md) | **Withdraws two headline results.** The operating-point sweep degrades the model, and on high-base-rate tasks most arms end up beaten by a constant. Alabama's +0.979 and LSAC's +0.968 are void; lending, which had failed, is rescued and now agrees with document 31's independent estimate |
| 41 | [Two scope tests, one void by my own error](docs/41-two-scope-tests-one-void-by-my-own-error.md) | Equalized odds moves the pool *more* than parity on COMPAS, so document 33's magnitude claim is ACS-specific. The post-processing arm is void: it produced an identical model at every operating point, and the apparent reversal was arithmetic |
| 42 | [Denser sweeps, and where the crossover sits](docs/42-denser-sweeps-and-where-the-crossover-sits.md) | Twelve points instead of six. Alabama and Kentucky **reverse** when their sweeps sit below the crossover, so the claim narrows to across the transition. But four populations across three domains and two countries agree on the crossover to within 0.08 — much tighter than 'population-specific' |
| 43 | [The rule belongs to one regime](docs/43-the-rule-is-about-one-regime-and-the-theory-says-which.md) | **A pre-registered test that failed, and explains itself.** Under post-processing the effect vanishes (r = −0.024 against +0.585). Post-processing is attribute-aware, where the theory says the direction is *determined* — and its prediction for that regime holds **18 of 18** |
| 44 | [How much, and where](docs/44-how-much-and-where-two-concessions-tested.md) | Two concessions tested instead of assumed. Magnitude is **ordered within** a population (ρ up to +0.96) and does **not transfer** across (pooled +0.487, fails). The crossover clusters at 0.511–0.576, sd 0.029 — so 'expect ~0.54' replaces 'measure it from scratch'. C2's two apparent predictors are collinear at +0.947 and mean nothing at n=4 |
| 45 | [Intervals, and what the exclusion was doing](docs/45-intervals-and-what-the-exclusion-threshold-was-doing.md) | Bootstrap intervals on every crossover: COMPAS's is six times wider than the Dutch census's and Oregon's bracket fails in 23% of resamples, so the cluster is 0.43–0.58 not 0.511–0.576. And a sensitivity sweep showing the 0.05 exclusion was doing real work |
| 46 | ~~[The relationship turns back up at the bottom](docs/46-the-relationship-turns-back-up-at-the-bottom.md) | What doc 45 was actually seeing. At 20 seeds the low-gap arms are **not** noise — all four ACS populations turn *positive* at a selection rate near 0.05. The relationship is bounded below as well as above, and the exclusion was concealing a second regime rather than manufacturing a result — **withdrawn by doc 47** |
| 47 | [The sealed prediction failed](docs/47-the-sealed-prediction-failed-and-took-document-46-with-it.md) | **4/8, bar was 7, constant not beaten.** A rule sealed before nine unseen populations ran. Doc 46's refinement — added two hours earlier from four in-sample populations — turned a 7/8 prediction into 4/8. The low-rate turn-up is a property of the operating-point *route*, not of the selection rate |

## The short version

Documents 01–10 are all measurements on one dataset. Ding et al. (2021), *Retiring
Adult*, argues the field should stop drawing conclusions from exactly that dataset. Until
a finding survives a population it was not derived from, "the constraint causes X" and
"Adult has property X" are indistinguishable. These documents test that, on 19 survey
populations across two protected attributes — and then, in document 22, on a domain that is
not a survey at all.

**Where this sits in the literature, after checking.** Three of this folder's claims turned
out to be anticipated, and all three were found by reading rather than assumed. The
selection-rate floor is a variant of Mittelstadt et al.'s minimum rate constraints
(document 19's correction). The intersectional result is Kearns et al.'s (2018) fairness
gerrymandering, and the reason it escapes an audit is Maheshwari et al.'s (2023) finding
that intersectional levelling down "often goes unnoticed in the overall performance of the
model" — what document 12 adds is ten populations and a minority-share condition, not the
observation. And the *conditionality* of levelling down — that it can go
either way rather than being a default — is proven in arXiv:2603.06901 (March 2026), five
months before this project reached it independently. What survives that collision is the
empirical half, and document 27 makes the case precisely: their conditions are satisfied on
**0 of 26** arms — fifteen populations — because the quantity they are stated over diverges on real data,
their direction is right once relaxed (24–25 of 26), and the overall selection rate proxies
their structural quantity at **r = +0.935** while requiring nothing but a historical
approval rate. Independent theory and independent measurement converging.

**What did not survive a second domain.** Every population above is a household survey. On
**HMDA mortgage decisions** — an administrative record of real lending outcomes rather than
a survey — the demographic parity constraint **levels up unprompted**, growing favourable
decisions by 4.3% at an exchange rate of 0.50 while removing 94% of the parity violation
(document 22). Twenty populations point one way and the twenty-first and twenty-second point
the other. Nothing in documents 05 or 21 is retracted; what changes is their reach.
Levelling down is a property of the fairness-constrained problems this project had been
looking at, not of demographic parity constraints in general. The parity metric reports the
same success either way — which is the frame this work inherited rather than something it
found. Maheshwari et al. (2023) report levelling down going unnoticed in a model's overall
performance, and Ferry et al. (2023) built an audit tool around the same gap. What document
22 adds is that the direction reverses, not that the metric is silent about it.

**What replicated.** The intersectional result is the strongest thing here, and it is a
replication in the strict sense: Kearns et al. (2018) named fairness gerrymandering and
Maheshwari et al. (2023) reported that the intersectional harm is the worse one and goes
unnoticed in aggregate performance. It appears in every sufficiently diverse population and
is *worse* than Adult showed — 9.0× there against 13.2× in Mississippi (document 12). It gains one condition,
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
holds: across **19 arms — ten populations under two protected attributes — the exchange rate fell in
every one**, from 1.47 to 0.88 in the sex arm and 1.59 to 0.79 in the race arm (document
21). Two things needed correcting. Adult is the **extreme** case rather than the typical
one — its −20.5% pie loss sits against a −6.1% mean elsewhere — and the floor does not
merely protect the pie, it *grows* it, in 18 of 19 arms. One of that document's five
pre-registered predictions failed, and the failure is recorded rather than repaired.

**The through-line, which is borrowed rather than found here.** A fairness metric describes
an outcome state, not a mechanism — the point Maheshwari et al. (2023) and Ferry et al.
(2023) both make ahead of this work. Every headline number in documents 02–04 is correct and
every finding above is invisible in it, which is why each one had to be measured separately
instead of read off the metric.
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
conversion's error at **r = +0.885** across nineteen arms. Both group inequality
and small samples raise it, independently — see
[document 13](docs/13-separating-ratio-from-size.md).

This note lives here rather than in `docs/05` so the course-side documents contain only
work within the course scope.
