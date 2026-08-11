# 02 — Baseline: how unfair is the unmitigated model?

Before any mitigation, establish what is being mitigated. Both base classifiers,
5 seeds, mean ± std.

## Results

| model | Accuracy | DP diff | EO diff | Disparate impact |
|---|---|---|---|---|
| decision_tree | 0.8518 ± 0.0036 | 0.1556 ± 0.0125 | 0.0799 ± 0.0323 | 0.3061 ± 0.0320 |
| logistic_regression | 0.8465 ± 0.0028 | 0.1897 ± 0.0068 | 0.1057 ± 0.0349 | 0.2896 ± 0.0320 |

*(fair at 0 for the two differences, at 1 for disparate impact)*

## What this says

**The bias is severe by the standard legal yardstick.** Disparate impact of 0.29–0.31
means the female selection rate is under a third of the male rate. The US EEOC
"four-fifths rule" flags anything below 0.8. This model is at roughly 0.3 — not
marginally non-compliant, but off by a factor of nearly three.

**The models did this without being shown `sex`.** The protected attribute is not in
the feature matrix. The model reconstructed the disparity from proxies, which is the
concrete demonstration that fairness through unawareness fails. Document 06 identifies
which proxies and by how much.

**Accuracy is not where the problem is.** Both models sit near 85%, which is
respectable for Adult. A reader looking only at accuracy would conclude the pipeline
is healthy. This is the ordinary case: bias does not announce itself in the metric
teams actually monitor.

## The one comparison that matters later

Note that the decision tree is **both more accurate and less unfair** than logistic
regression on every metric here. That is convenient, and it is worth being clear that
it does not generalise — it is a property of this hypothesis class on this data, not a
rule. The consequence for reading the rest of these documents is that the base-paper
track (tree, document 03) and the ablation (logistic regression, document 04) have
**different baselines**, and their numbers must not be compared across that boundary.

## Relation to the base paper

Agarwal et al. (2018) do not dwell on the unconstrained baseline; it is the starting
point their trade-off curves depart from. Nothing here contradicts them. The purpose
of this document is to fix the reference point that documents 03–07 measure against,
and to record the two facts that shape everything after:

1. the disparity is large (DI ≈ 0.3), and
2. it exists **despite** the protected attribute being absent from the features —
   so any method that claims to fix it by not looking at `sex` has already been shown
   insufficient before it starts.
