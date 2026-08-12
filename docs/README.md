# Results documentation

Every finding this project produced, what it means, and how it stands against the
base paper. Written to be read in order, but each file stands alone.

| # | Document | What it answers |
|---|---|---|
| 01 | [Setup and method](01-setup-and-method.md) | What was measured, on what, and why those choices |
| 02 | [Baseline](02-baseline.md) | How unfair is the unmitigated model? |
| 03 | [Base-paper reproduction](03-base-paper-reproduction.md) | Does Agarwal et al. (2018) do what it says on this data? |
| 04 | [Ablation](04-ablation.md) | Six mitigations, one table, three questions |
| 05 | [Who pays](05-who-pays.md) | Did the gap close by lifting anyone up, or by pulling people down? |
| 06 | [Proxy reliance (SHAP)](06-proxy-reliance-shap.md) | Do the mitigated models stop using stand-ins for sex? |
| 07 | [Intersectional](07-intersectional.md) | Does fixing sex leave a Sex×Race subgroup behind? |
| 08 | [Comparison with the base paper](08-vs-base-paper.md) | Consolidated: confirmed, extended, contradicted |
| 09 | [Proxy removal](09-proxy-removal.md) | If the model leans on a leaky feature, does deleting it help? *(negative control — deliberately not in-processing)* |
| 10 | [Epsilon sweep](10-epsilon-sweep.md) | Is levelling down just an artifact of a tight constraint? |
| 11 | [Replication across populations](11-replication-across-populations.md) | Which findings are about the method, and which about Adult? *(beyond the course submission)* |
| 12 | [Intersectional across populations](12-intersectional-across-populations.md) | Gerrymandering replicates and is worse than Adult — where there is a minority to hide in *(beyond the course submission)* |

## The short version

The base paper's algorithm works. It does what it claims: it drives the fairness
violation to near zero for a small accuracy cost, on any base classifier, without
touching the training data. Documents 02–04 confirm that.

Documents 05–07 are this project's own contribution, and they are less comfortable.
The same algorithm that scores best on the fairness metric also:

* closed the gap mostly by **taking approvals away from the advantaged group**, not by
  extending them to the disadvantaged one — every method shrank the total number of
  favourable decisions, by 8–22%;
* **increased** its reliance on sex proxies, doubling its use of `relationship` —
  the opposite of what the initiation document predicted SHAP would show;
* at the intersection of sex and race, operates on subgroups half of which are too
  small to measure at all;
* and cannot be talked out of any of it. Loosening the constraint changes the dose,
  not the mechanism (doc 10), and deleting the leaky feature makes the unmitigated
  model *more* biased while barely reducing how well sex can be recovered (doc 09).

None of that makes the method wrong. It makes the headline metric an incomplete
description of what the method did, which is a different and more useful claim.

[Document 11](11-replication-across-populations.md) then tests three of these findings
on nine other populations. One held cleanly, one held only under a condition that had
to be discovered, and one did not hold. Two failures out of three is the informative
outcome: a clean sweep would suggest the predictions had been fitted to the data they
came from. Nothing in documents 01–10 is retracted, and the course deliverables are
unaffected — the claim that failed appears in neither of them.

[Document 12](12-intersectional-across-populations.md) does the same for the
intersectional result, and it survives better than any other: the gerrymandering
Adult showed at 9.0× reaches 13.2× elsewhere. It gains one condition — it needs a
substantial minority to hide in, and where a population is 95% one race a constraint on
sex fixes the intersection by default. That relationship is the first in the project
whose two candidate explanations are not confounded with each other.

## Scope: purely in-processing

**All six methods in the ablation table modify only the objective given to the learner.**
No row is resampled, reweighted on disk, relabelled, or edited. `ExponentiatedGradient`
reweights examples *inside* its optimisation loop, per iteration — the dataset on disk is
never altered, which is what keeps it in-processing rather than making it Reweighing.

Two consequences of holding that line:

* **Reweighing (Kamiran & Calders 2012) is excluded**, though the specification offered it
  as an optional row. It is pre-processing, and reporting it alongside the others would
  break the single property that makes the table a controlled comparison.
* **Document 09 breaks the rule on purpose**, as a negative control. It deletes features to
  test whether the cheaper pre-processing alternative works — it does not — and its result
  is a defence of this scope, not a departure from it. Nothing in the ablation table comes
  from it.

Encoding (one-hot, standardisation) and listwise deletion of rows with missing values are
not interventions: they are applied identically to every method before any fairness work,
and alter no label or class balance. See [document 01](01-setup-and-method.md).

## Reading the numbers

* Unless stated otherwise, every figure is the mean over **5 random seeds**
  (0–4), each seed being an independent train/test split stratified on the
  `(sex, income)` interaction.
* **Demographic parity difference** and **equalized odds difference** are fair at
  **0**. **Disparate impact** is a ratio, fair at **1**, with 0.8 the conventional
  four-fifths threshold. They are not interchangeable and are never averaged together.
* Every metric is implemented from its definition in `src/metrics.py` and
  cross-checked against `fairlearn.metrics` on every run.
* The `fairlearn` and `scikit-learn` rows are exactly reproducible. The two PyTorch
  methods are seed-stable but not bit-reproducible, and can move by ±0.0001 between
  runs — see the reproducibility note in [document 04](04-ablation.md).
* "Privileged" = Male, "unprivileged" = Female, throughout. This is a statement about
  base rates in the data (31.2% vs 11.4% earn >$50K), not about individuals.

## Reproducing

```bash
python -m src.experiments.run_baseline       --seeds 0 1 2 3 4
python -m src.experiments.run_mitigation     --seeds 0 1 2 3 4
python -m src.experiments.run_pareto
python -m src.experiments.run_ablation       --seeds 0 1 2 3 4
python -m src.experiments.run_who_pays       --seeds 0 1 2 3 4
python -m src.experiments.run_shap           --seed 0
python -m src.experiments.run_intersectional --seeds 0 1 2
python -m src.experiments.run_proxy_removal   --seeds 0 1 2
python -m src.experiments.run_epsilon_sweep  --seeds 0 1 2
```

Correctness checks:

```bash
python -m tests.test_inprocessing   # the from-scratch method implementations
python -m tests.test_incidence      # the who-pays decomposition
```
