# 70 — The rate beats the product, on real approvals

**Individual work, beyond the course submission. Sealed test, scored against its own bar.**
Seal `0a71906`, anchored `6b76bc3`; scored `analyse_lending_direction.py`, 26 Aug.

## What this test was for

The paper's sharpest scope limit is that five of eight data sources are predicted labels
rather than allocations — in most of the record nobody receives anything. HMDA is the one
source recording a real approve-or-deny by a lender, and it is also where the sweep
protocol failed twice: 2 of 4, then 2 of 6 across six markets. What survived those failures
is the **natural-arm** reading at 7 of 8, and that route had never been sealed.

State-level lending rates cluster too high to test anything — Louisiana 0.794, Georgia
0.835, South Carolina 0.841, North Carolina 0.873 all sit above any located crossover, so
whole markets predict UP everywhere and a constant matches. Loan purposes supply the spread
instead: on pooled Mississippi–Louisiana, improvement sits at 0.555 and levels down while
refinance sits at 0.871 and levels up.

Sixteen (market × purpose) arms from **eight never-downloaded markets**, against the
transported prior 0.660 — the pooled Mississippi–Louisiana crossover, which none of these
eight helped locate.

## The result: S1 FAILS

| condition | outcome |
|---|---|
| at least 6 of 8 correct | **PASS** — 8 of 8 |
| strictly beats the best constant | **FAIL** — constant also 8 of 8 |
| paired sign test p < 0.05 | **FAIL** — undefined, 0 discordant arms |

The magnitude guard removed 8 of 16 arms, and every surviving arm went **up**. A constant
predicting "up" is therefore perfect and cannot be beaten. The same guard/discordance
conflict as document 69, in a starker form: there the guard left four discordant arms, here
it left none.

The transported prior 0.54 scored identically to 0.660 — again zero discordant arms — so
this cohort says nothing about which lending crossover is right.

## What it does establish, and it is the reason to keep it

Against the **purpose-only null** — predict DOWN for improvement and UP for refinance,
ignoring the measured rate — the rule wins:

| | correct | margin |
|---|---|---|
| rate rule | **8 / 8** | — |
| purpose-only null | 5 / 8 | **+3 arms, 95% CI [+1, +6]**, sign test p = 0.125 (3/3 discordant) |

**The loan product does not carry the prediction; the measured approval rate does.** This is
the lending analogue of document 67's "it is the rate, not label rarity", and it is the
first time the point has been made where the favourable decision is a real allocation rather
than a predicted label.

Stated at its true strength: three discordant arms, p = 0.125. Suggestive, not significant,
and reported as such. What makes it worth recording is not the p but the setting — every
earlier version of this argument was made on status-prediction benchmarks.

## What it settles

* The natural-arm route in lending is now **sealed** rather than post-hoc, and the rule went
  8 of 8 on scored arms. That the constant matched it is a property of the cohort's surviving
  arms, not of the rule.
* The **purpose-only confound is broken in the rate's favour**, on allocation data.
* The sealed design does **not** transfer to lending unchanged: rates cluster so high that
  even purpose-level spread leaves an all-positive surviving set once the magnitude guard
  applies. A future lending seal needs arms that are expected to sit *below* the crossover
  with effects above a point, and improvement lending at these rates does not supply them.

## What it does not settle

Nothing about the sweep procedure, which the six-market seal already found unreliable here
and which this cohort deliberately does not use. Nothing about which lending crossover is
correct. And nothing about whether the direction rule beats a constant in lending — on this
cohort's surviving arms it demonstrably does not, because there was no constant to beat.
