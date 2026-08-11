# Algorithmic (In-Processing) Bias Mitigation on Adult Census Income

Detection and mitigation of algorithmic bias in an income-prediction classifier
using **purely in-processing** fairness methods — the training data is never
modified, only the optimisation problem given to the learner.

Course project for a Responsible AI class. The full specification is in
[`INITIATION_DOC.md`](INITIATION_DOC.md).

## Status

| Component | State |
|---|---|
| Dataset interface + Adult loader | Implemented |
| Fairness metrics (DP diff, EO diff, disparate impact) | Implemented, cross-checked against `fairlearn` |
| Multi-seed baseline experiment | Implemented |
| Exponentiated Gradient (DP / EO constraints) | Not yet implemented |
| GridSearch Pareto frontier | Not yet implemented |
| Prejudice Remover, Adversarial Debiasing | Not yet implemented |

## The problem

Predict whether income exceeds $50K/yr from US census features. The protected
attribute is `sex`.

Standard ERM minimises `E[1{h(x) != y}]` with no reference to the protected
attribute `a`. But the base rates differ sharply across groups, so the model
reproduces that gap through correlated features. The project instead solves

```
min_h  E[1{h(x) != y}]   subject to   φ(h) <= ε
```

where `φ` is a fairness violation measure. The dataset `D` is untouched; only the
feasible region changes.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m src.experiments.run_baseline                       # 5 seeds, both models
python -m src.experiments.run_baseline --seeds 0 1 2         # fewer seeds
python -m src.experiments.run_baseline --include-protected   # give the model `sex`
```

Adult is downloaded from OpenML on first run and cached to `data/`.

## Baseline results

Unmitigated ERM, 30% test split, mean over 3 seeds, **protected attribute excluded
from the features**:

| Model | Accuracy | DP diff ↓ | EO diff ↓ | Disparate impact →1 |
|---|---|---|---|---|
| Decision tree (depth 8) | 0.852 | 0.156 | 0.080 | 0.306 |
| Logistic regression | 0.847 | 0.190 | 0.106 | 0.290 |

Group base rates: `P(y=1 | Male) = 0.312` vs `P(y=1 | Female) = 0.114`.

Two things worth noting before any mitigation is applied:

1. **Disparate impact is ≈ 0.30**, far below the 0.8 "four-fifths rule" threshold.
   The bias is large, not marginal.
2. **This happens with `sex` removed from the model's inputs.** Fairness through
   unawareness does not work here — `relationship`, `marital-status` and
   `hours-per-week` carry the signal. This is the motivation for in-processing
   methods, and it is worth reporting as a result rather than an aside.

Note also that per-group *accuracy* is higher for the unprivileged group (0.93 vs
0.82) while its selection rate is far lower — a reminder that aggregate accuracy
parity and fairness are different properties.

## Structure

```
src/
├── datasets/
│   ├── base.py       # FairnessDataset + DatasetLoader interface
│   └── adult.py      # UCI Adult loader, cleaning decisions recorded in notes
├── metrics.py        # DP diff, EO diff, disparate impact, per-group breakdown
├── preprocessing.py  # split + encoding
├── models.py         # base classifiers (must support sample_weight)
└── experiments/
    └── run_baseline.py
results/              # generated tables
```

## Design decisions

Recorded because each is a judgment call a reader could reasonably question.

**Experiments are written against a dataset interface, not against Adult.**
Loaders return a `FairnessDataset`; no experiment references an Adult column name.
This costs little now and is what makes the multi-dataset extension below a loader
swap rather than a rewrite. Only Adult is implemented.

**Two base classifiers are carried, not one.** The initiation document specifies a
decision tree. But Prejudice Remover and Adversarial Debiasing cannot wrap one —
they need a differentiable/linear model by construction. Reporting a tree for some
ablation rows and a linear model for others would vary the hypothesis class *and*
the mitigation simultaneously, so the table would not isolate the effect it claims
to. Logistic regression is therefore carried alongside as the
comparable-across-all-methods base, and the confound is stated rather than hidden.

**Tree depth is capped at 8.** An unbounded tree hits ~100% training accuracy on
Adult, which would confound the accuracy cost of *mitigation* with the accuracy cost
of *overfitting*.

**Encoding is fitted separately from the estimator, not bundled in a `Pipeline`.**
`ExponentiatedGradient` refits its base estimator with `sample_weight`, which a
`Pipeline` will not route to the final step without extra plumbing. Handing the
reduction a bare estimator over pre-encoded arrays keeps the reweight-and-retrain
loop working unmodified. The encoder is still fitted on the training split only.

**Splits are stratified on the `(a, y)` interaction, not on `y` alone.** Fairness
metrics are computed from four cells, the smallest being (Female, >50K). Left
unstratified, that cell's size varies across seeds and injects sampling noise that
is easily mistaken for model instability.

**Metrics are implemented from their definitions and cross-checked against
`fairlearn`** on every run. A privileged/unprivileged orientation slip produces
plausible-looking numbers that are silently wrong; the assertion catches it.

**Every experiment runs over multiple seeds.** One run cannot support a claim about
stability, and stability is one of the questions the ablation asks.

## Future work

Not implemented — recorded so the design choices above have visible motivation.

- **Multi-dataset generalisation.** Re-run the identical experiment across ACS /
  `folktables` state slices (Ding et al. 2021, *Retiring Adult*). A single-dataset
  fairness result cannot distinguish a property of the *method* from a property of
  one 1994 census extract. This is what the loader interface exists for.
- **Who pays for the constraint.** Decompose baseline → mitigated prediction flips
  by `(a, y)` cell. A constraint satisfied by lowering the privileged group's true
  positive rate is indistinguishable, at the aggregate metric, from one satisfied by
  raising the unprivileged group's — "levelling down" (Mittelstadt et al. 2023).
  `metrics.group_breakdown` is the starting point.
- **Stochastic-classifier instability.** `ExponentiatedGradient` returns a
  distribution over classifiers, so identical feature vectors can receive different
  decisions on different calls. Quantifying that churn tests whether a group-fairness
  fix introduces an individual-level harm (cf. Cooper et al. 2024 on variance and
  arbitrariness in fair classification).
- **Intersectional constraints.** Enforcing parity on `sex` and on `race`
  separately does not imply parity on `sex × race` (fairness gerrymandering, Kearns
  et al. 2018).
- **Fairness generalisation gap.** Report φ(h) on train *and* test as ε tightens;
  constraints can be satisfied in-sample and violated out-of-sample.

## References

- Agarwal, Beygelzimer, Dudík, Langford & Wallach (2018). *A Reductions Approach to
  Fair Classification.* ICML. — base paper
- Kamishima et al. (2012). *Fairness-Aware Classifier with Prejudice Remover
  Regularizer.*
- Zhang, Lemoine & Mitchell (2018). *Mitigating Unwanted Biases with Adversarial
  Learning.*
- Ding, Hardt, Miller & Schmidt (2021). *Retiring Adult: New Datasets for Fair
  Machine Learning.* NeurIPS.
