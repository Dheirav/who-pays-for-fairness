# 25 — Against the remedies that already exist

**Individual work, beyond the course submission.** Documents 19, 21 and 23 measure the
selection-rate floor only against plain `ExponentiatedGradient` — the method whose behaviour
motivated it. This compares it against two established alternatives, on three populations
chosen to span the selection-rate range, five seeds each.

The arms, and two asymmetries that must be read with the table:

* **`group_thresholds`** — per-group thresholds on the unconstrained score. Corbett-Davies
  et al. (2017) characterise this as the *optimal* DP-constrained classifier, so it is a
  **bound**, not a rival. It **uses the protected attribute at prediction time**; nothing
  else here does.
* **`minimax`** — minimise the worst group's error (Martinez et al. 2020; Diana et al.
  2021). It does not target parity and its parity numbers are not failures at something it
  attempted.

## The results

| Adult — selection rate 0.205 | accuracy | DP diff | pie | destroyed per created |
|---|---|---|---|---|
| baseline | 0.8469 | 0.1861 | — | — |
| `expgrad_dp` | 0.8282 | 0.0178 | −20.45% | 2.68 |
| `expgrad_dp_floor` | 0.8245 | 0.0179 | **−0.62%** | **1.03** |
| `group_thresholds` | 0.8270 | 0.0050 | **−18.83%** | 2.48 |
| `minimax` | 0.8464 | 0.1839 | +1.45% | 0.49 |

| ACS Alabama, sex — 0.252 | accuracy | DP diff | pie | destroyed per created |
|---|---|---|---|---|
| baseline | 0.7880 | 0.1293 | — | — |
| `expgrad_dp` | 0.7747 | 0.0218 | −2.34% | 1.14 |
| `expgrad_dp_floor` | 0.7748 | 0.0204 | +4.26% | 0.80 |
| `group_thresholds` | 0.7704 | 0.0078 | +3.33% | 0.83 |
| `minimax` | 0.7808 | 0.1082 | **+33.66%** | 0.03 |

| HMDA Mississippi, race — 0.808 | accuracy | DP diff | pie | destroyed per created |
|---|---|---|---|---|
| baseline | 0.8410 | 0.1774 | — | — |
| `expgrad_dp` | 0.8083 | 0.0103 | +4.26% | 0.50 |
| `expgrad_dp_floor` | 0.8083 | 0.0088 | +4.42% | 0.49 |
| `group_thresholds` | 0.8237 | 0.0054 | +0.84% | 0.82 |
| `minimax` | 0.8253 | 0.1567 | **−10.01%** | **46.71** |

## Levelling down is not the solver's fault — on Adult

On Adult the **theoretically optimal** DP classifier destroys **18.8%** of favourable
decisions, against the reduction's 20.5%, at a comparable exchange rate (2.48 against 2.68)
and with *better* parity (0.0050 against 0.0178).

This closes the most obvious objection to
[document 05](../../docs/05-who-pays.md): that levelling down is an artifact of a particular
solver searching badly. It is not. Solve the constrained problem exactly, with the
protected attribute in hand, and the same thing happens. **At Adult's selection rate,
levelling down is a property of the constraint.**

**But not everywhere, and that is new.** On Alabama at 0.252 the two disagree in *sign*: the
reduction destroys 2.34% while the optimal classifier creates 3.33%. So at moderate
selection rates the solver does matter, and the reduction is the worse of the two. The
statement that survives is narrower than the headline: levelling down is intrinsic to the
constraint where it is severe, and partly attributable to the solver where it is mild.

## Minimax group fairness is not a levelling-down remedy

It is proposed as one — minimising the worst group's error can never require harming
another group to equalise. What it does on these populations is erratic, and on HMDA it is
worse than the thing it is meant to fix:

* **HMDA:** destroys **10.0%** of favourable decisions at an exchange rate of **46.7**, the
  worst number recorded anywhere in this project — while barely touching parity
  (0.1567 against a baseline 0.1774). Meanwhile the parity constraint on the same data
  *creates* 4.3%.
* **Alabama:** hands out **33.7% more** favourable decisions while leaving parity at 0.1082
  from a baseline of 0.1293.
* **Adult:** does essentially nothing — accuracy 0.8464 against the baseline's 0.8469,
  parity 0.1839 against 0.1861.

The reason is visible in the objective. Minimax minimises the worst group's **error rate**,
and worst-off-by-error is not worst-off-by-outcome. On Adult the higher-error group is
**Male** (0.1869 against Female's 0.0743), because the male base rate sits nearer 50% and is
harder to fit — so the method optimises for the *privileged* group and correctly concludes
there is little to do. On HMDA, where 81% of applicants are approved, reducing the worst
group's error means predicting "deny" more often, and the pool shrinks.

This is the paper's own thesis appearing in a baseline: a fairness criterion whose stated
aim ("do not make anyone worse off") diverges from what its objective actually optimises,
with nothing in its own metric to reveal the difference.

## What the floor is, after this

Not the best at parity — `group_thresholds` beats it everywhere (0.0050 against 0.0179 on
Adult). Not the cheapest — `minimax` costs almost nothing because it does almost nothing.

**It is the only arm that satisfies parity *and* preserves or grows the pool of favourable
decisions *without needing the protected attribute at prediction time*.** On Adult that
combination is unique to it: the optimal classifier matches its parity but destroys 18.8%,
and doing better than the optimal classifier on the pie is possible only because the floor
is solving a *different* constrained problem, not the same one better.

That is a narrower claim than document 19 made, and it is the one supported by evidence.

## Limits

* **Three populations**, one per selection-rate regime, five seeds.
* **`minimax` is a simplified implementation** — the standard reweighting scheme, not
  either paper's exact algorithm; see `src/baselines.py`. Its erratic behaviour may partly
  be the implementation. The Adult diagnosis (worst-by-error is Male) does not depend on
  the implementation and was verified separately.
* **`group_thresholds` picks its common rate on the training split** over a fixed grid, so
  it is optimal in-sample and only approximately so out of sample. That is why the
  reduction occasionally beats it on accuracy (0.8282 against 0.8270 on Adult).
* **No post-processing MRC arm.** Mittelstadt et al.'s construction is a per-group floor
  applied by post-processing; the closest thing here is `group_thresholds`, which is not the
  same thing. A direct MRC comparison is the obvious next baseline and has not been run.
