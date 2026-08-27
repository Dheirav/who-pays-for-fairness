# 76 — Experiment 7.1: sealed, run, and it fails for the third time in the same way

**Individual work, beyond the course submission. Sealed at `4d1909b`, before any of the
sixteen arms existed.** Reproduce: `.venv/bin/python -m src.experiments.analyse_allocation_seal`

---

## The verdict

**S1 FAILS.** The rule scores 7 of 8 against a bar of 6 and beats the purpose-only null — and
a constant "up" also scores 7 of 8, so it is not beaten. Unguarded: 10 of 13 against the same
constant at 10 of 13. Both scorings were committed in advance; neither was chosen afterwards.

| | arms | rule | constant | purpose | survey | verdict |
|---|---:|---:|---:|---:|---:|---|
| S1, magnitude guard | 8 | 7 | **7** | 6 | 7 | fail |
| S2, unguarded | 13 | 10 | **10** | 9 | 10 | fail |

**The rule predicts `down` on 0 of 8 arms.** That single line is the whole result: with no
down-calls, a constant cannot be beaten, and the test cannot discriminate no matter how
accurate the rule is.

## Why, and the design error is mine

The cohort was built on a reading of the 2018 purpose arms: they span 0.555 to 0.901, which
straddles the published lending crossover of 0.660, so pairing a low-rate purpose with a
high-rate one should make the rule predict opposite directions inside one market. A constant
could not tie that.

The span was real. The *density* was not.

| purpose | year | n | range | median | below 0.660 |
|---|---|---:|---|---|---:|
| improvement | 2018 | 9 | 0.555–0.901 | 0.765 | **2 of 9** |
| improvement | 2021 | 8 | 0.682–0.913 | 0.824 | **0 of 8** |
| refinance | 2018 | 9 | 0.829–0.894 | 0.871 | 0 of 9 |
| refinance | 2021 | 8 | 0.915–0.950 | 0.936 | 0 of 8 |

Only the bottom two of nine 2018 improvement arms were below the crossover. I read the range
and inferred a straddle; the honest read was a 2-in-9 base rate, and building eight fresh arms
on that was optimistic rather than reasoned. **Then 2021 moved the instrument away entirely**:
approval rates rose across every purpose — improvement's median from 0.765 to 0.824, refinance
from 0.871 to 0.936 — so the low tail that made the design look viable did not survive the
year change.

That second part is not a design error, it is a finding. But it would not have mattered if the
first part had been read correctly.

## What the failure establishes, which is more than the pass would have

**1. US mortgage approval cannot test this rule, and that is now shown three ways.** The
state-level arms sit at 0.82 and above. The fifty-market coverage sits at 0.82 and above. And
now a fresh year at purpose level, chosen specifically to reach below the crossover, sits at
0.68 and above. The instrument is uniformly generous. Every arm the rule has ever seen on real
approvals is one where it predicts extension, so on this instrument the rule and "always up"
are the same rule. The paper's limitation can now say that as a measured fact across two
reporting years and two levels of aggregation rather than as an observation about one table.

**2. The rate beats the loan product, in both scorings.** 7 against 6 and 10 against 9. Small,
and on eight and thirteen arms it is not significant — but the purpose-only null is the sharp
alternative here, because purpose is what moves the rate, and it loses both times.

**3. The instrument moved between vintages.** 2021 approval is materially more generous than
2018 at every purpose. So "lending is different" may be a property of a *period* as much as of
a domain, which the paper currently does not consider — its lending crossover estimates all
come from one year.

**4. The rule was accurate and untested, which are different things.** 7 of 8 and 10 of 13 are
good absolute scores. They establish nothing, because a rule that only ever says one thing
cannot be distinguished from a constant that says the same thing. Reporting the accuracy
without the constant beside it would have been the exact defect this paper fails other cohorts
for.

## What would actually test it

Not another HMDA year. The instrument has now failed to supply below-crossover arms in 2018 at
two aggregations and in 2021 at the aggregation chosen to find them. Testing the direction rule
on real allocations needs a register whose approval rates reach below roughly 0.66 — a
non-US mortgage register, a credit product with a genuinely selective accept rate, or an
allocation domain that is not lending at all. That is the same conclusion the paper reached
before this experiment; the difference is that it is now a measurement rather than an
inference.
