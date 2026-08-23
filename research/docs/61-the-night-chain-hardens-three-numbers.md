# 61 — The night chain hardens three numbers

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**
The three follow-on stages of the 24 Aug overnight chain, run sequentially after the
cross-task sweeps (document 60).

## 1. The located crossovers survive row resampling — except Dutch (`analyse_nested_bootstrap.py`)

Nested uncertainty for Table IV: five refitted seeds × 200 row bootstraps of the test
split, arms rebuilt per seed at fixed target rates 0.35–0.70, one bracket per
(seed, resample) pair.

| population | published mid | boot median | 95% CI | pairs with no crossing |
|---|---|---|---|---|
| COMPAS | 0.511 | 0.457 | 0.433–0.539 | 0% |
| SC | 0.530 | 0.525 | 0.454–0.537 | 2.8% |
| OR | 0.558 | 0.532 | 0.514–0.604 | 0.6% |
| Dutch | 0.576 | — | — | **100%** |

Three of four published locations sit inside their nested intervals; the anti-conservative
caveat can come off those rows. **Dutch fails to bracket in every single resample**: at
the denser view its mid-band signs interleave, which is the same verdict document 58's
table returned (NON-MONOTONE). The published 0.576 came from six arms that happened to
present a clean crossing; the paper's Dutch row is downgraded accordingly.

## 2. The lottery is in-class necessary, not an optimiser failure (`analyse_mixture_optimality.py`)

The paper left open whether the flat lottery is suboptimal within the blind constrained
class. Searched: the minimal richer class (two-threshold blind mixtures, parity weight
in closed form, exact grid over score quantiles extended into the 0.9975 tail to rule
out a grid-edge artifact). **On all 10 seed-arm pairs the feasible set is empty** — no
two-threshold blind mixture attains the lottery's parity gap and pool size at all, on
either signature arm. The charge therefore stays exactly as the paper narrowed it: the
wrong is the *unannounced* lottery under an indistinguishable certificate, not an
avoidable optimiser mistake — at those operating points the constraint itself admits no
score-informed blind solution of that size.

## 3. Where lift and cut actually live (`--probe-diff`)

Document 50's last cheap step, the decile-by-group grant table:

* **Lift (OR@0.87):** probability granted to the *unprivileged group across deciles
  3–8* (rising 0.004 → 0.038), plus a transfer inside decile 9 (privileged −0.042,
  unprivileged +0.024). The optimiser reaches into the mid-distribution and grades by
  score.
* **Cut (Dutch@0.965):** nothing granted below decile 9 in either group; decile 9
  slashed for both (privileged −0.182, unprivileged −0.128) — the lottery, seen from
  the inside.

The visible difference is *whether the unprivileged mid-deciles receive any mass at
all*. Combined with (2), the picture closes: where a mid-decile reservoir is usable the
optimiser uses it and grades; where no blind score-informed solution exists it cuts by
lottery. What *predicts* which case a population is in remains the open selector
question — but it now has a concrete object to explain, not six dead summaries.

## Chain hygiene

All stages sequential, memory-capped (6 GB), low priority beside a concurrent
unrelated workload; zero incidents; total chain wall-clock ≈ 2.6 hours, well under the
estimate.
