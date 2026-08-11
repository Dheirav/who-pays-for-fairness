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
| Exponentiated Gradient (DP / EO constraints) | Implemented — base-paper deliverables 1–3 |
| GridSearch Pareto frontier | Implemented — base-paper deliverable 4 |
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
python -m src.experiments.run_baseline --include-protected   # give the model `sex`

python -m src.experiments.run_mitigation --seeds 0 1 2 3 4   # baseline + ExpGrad DP/EO
python -m src.experiments.run_pareto                         # GridSearch frontier (DP)
python -m src.experiments.run_pareto --constraint equalized_odds
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

## Mitigation results

Decision tree (depth 8), mean ± std over 5 seeds. Arrows mark the fair direction.

| Method | Accuracy | DP diff ↓ | EO diff ↓ | Disparate impact →1 |
|---|---|---|---|---|
| Baseline | 0.852 ± 0.003 | 0.161 ± 0.013 | 0.083 ± 0.023 | 0.309 ± 0.032 |
| ExpGrad (DP) | 0.836 ± 0.002 | **0.019 ± 0.007** | 0.277 ± 0.017 | **0.883 ± 0.042** |
| ExpGrad (EO) | 0.847 ± 0.003 | 0.113 ± 0.014 | **0.036 ± 0.024** | 0.457 ± 0.049 |

**The reduction works, and it is cheap.** The DP constraint cuts demographic parity
difference by 88% (0.161 → 0.019) for 1.5 percentage points of accuracy, and lifts
disparate impact from 0.31 to 0.88 — from failing the four-fifths rule badly to
clearing it. The EO constraint cuts equalized-odds difference by 57% for 0.5pp.

**But the two fairness criteria actively conflict.** Constraining demographic parity
makes equalized odds **3.3× worse** than doing nothing at all (0.083 → 0.277). A
model reported only on the metric it was optimised for looks like a clear success;
the same model is the worst of the three on the metric it ignored. This is the
sharpest result so far and it answers ablation question 3 directly — the ranking of
methods depends entirely on which metric you report.

Per-group rates (seed 0) show *how* DP is achieved: the privileged group's TPR falls
0.561 → 0.452 while the unprivileged group's rises 0.479 → 0.707. Parity comes partly
from lifting the disadvantaged group and partly from pulling the advantaged group
down — the decomposition that the "who pays" analysis in Future Work formalises.

### Pareto frontier

![GridSearch frontier under a demographic parity constraint](results/pareto_demographic_parity.png)

Sweeping 15 λ values gives **3 non-dominated models under DP** — the other 12 are
worse on both axes, so the trade-off is much lumpier than a frontier-only plot would
suggest. `ExpGrad (DP)` lands essentially on the frontier, so the game-playing
algorithm buys little over a plain grid *for this constraint*.

Under **equalized odds it is a different story**: only **1 of 15** grid points is
non-dominated, and it is the unmitigated baseline itself (the black ring around the
blue star in `results/pareto_equalized_odds.png`). Every other grid point is worse
than doing nothing on both axes, while `ExpGrad (EO)` reaches 0.849 accuracy at 0.021
EO difference. The default grid simply does not cover the useful λ region when the
constraint has four components (TPR and FPR × two groups) instead of one. Reporting
GridSearch and ExponentiatedGradient as interchangeable "Agarwal et al. 2018" rows
would hide that entirely.

## Structure

```
src/
├── datasets/
│   ├── base.py       # FairnessDataset + DatasetLoader interface
│   └── adult.py      # UCI Adult loader, cleaning decisions recorded in notes
├── metrics.py        # DP diff, EO diff, disparate impact, per-group breakdown
├── preprocessing.py  # split + encoding
├── models.py         # base classifiers (must support sample_weight)
├── mitigation.py     # ExponentiatedGradient, GridSearch, Pareto frontier
└── experiments/
    ├── run_baseline.py    # unmitigated reference
    ├── run_mitigation.py  # baseline vs ExpGrad (DP, EO), multi-seed
    └── run_pareto.py      # GridSearch sweep + frontier plot
results/              # generated tables and figures (.png + .pdf)
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

**Within a seed, all methods share one train/test split.** Differences between rows
then come from the mitigation rather than from resampling; the reported standard
deviations come from varying the split across seeds.

**`ExponentiatedGradient.predict` is stochastic and a `random_state` is fixed.** The
reduction returns a distribution over classifiers and samples one per call, so
identical feature vectors can receive different decisions. Fixing the seed makes
results reproducible but does not remove the behaviour — quantifying it is the
stochastic-instability item in Future Work.

**Figure colors were validated, not chosen by eye.** The Pareto plots use three
categorical hues checked against colorblind-separation, lightness and contrast
thresholds for a scatter's all-pairs requirement. The aqua slot falls below 3:1
against the surface, so every reference point carries a direct text label rather than
relying on color; marker shape gives a second, greyscale-safe channel for print. The
grid sweep is drawn in neutral ink because it is a population of models, not a fourth
named series.

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
