# 72 — Every market in the country, and the sex gap that isn't there

**Individual work, beyond the course submission. Post-hoc coverage, labelled as such.**
Fifty-two arms over 26 new markets, 27 Aug. Not a seal.

## Why this ran

The paper's sharpest scope limit is that in five of its eight data sources nobody receives
anything: a "favourable decision" is a classifier's label over people whose incomes,
occupations or bar results already exist. HMDA is the single source recording a real
approve-or-deny by a lender, and the paper's lending evidence rested on eight markets when
it was drafted and twenty-four after 26 Aug.

This completes it: **all fifty US states, on both protected attributes.**

The natural-arm route is used and no sweep is run. That is deliberate. The sweep failed its
held-out test in lending twice — 2 of 4, then 2 of 6 across six markets — and
[document 71](71-the-prior-cannot-see-the-landscape.md) supplies the mechanism: the
home-improvement product's response is U-shaped, so a bracketing step assuming one rising
crossing cannot read it. The natural arm needs no bracket.

## What the race arms show

Forty markets carry a race arm. Their baseline approval rates run 0.823 to 0.942, median
0.877 — far above the 0.660 lending crossover, so the rule predicts **extension** for every
one of them.

| filter | n | levels up | share |
|---|---|---|---|
| all race arms | 40 | 30 | 75% |
| clearing the 0.05 parity floor | 31 | 25 | 81% |
| clearing the floor **and** the 1.0-point magnitude guard | **12** | **12** | **100%** |

The twelve that clear both of the audit's own gates:

```
PA 1.07   RI 1.15   MI 1.19   CO 1.29   OK 1.29   AL 1.47
TX 1.51   KS 1.62   AR 2.02   NC 2.47   VA 2.84   SC 4.22
```

Twelve of twelve, on real mortgage approvals. The paper's previous lending statement was
"the natural-arm direction holds 7 of 8", from one pooled market.

## What the sex arms show, which is nothing, and that is the finding

Twenty-six markets carry a sex arm. **Not one of them clears the audit's disparity floor.**

| | race | sex |
|---|---|---|
| median baseline parity gap | 0.0788 | **0.0131** |
| arms clearing the 0.05 floor | 31 / 40 | **0 / 26** |
| median \|pool change\| | 0.473% | **0.021%** |
| arms above the 1.0-point guard | 12 / 40 | **0 / 26** |

Read naively the sex arms look like a failure — they level up only 31% of the time where
the rule says up. They are not a failure. There is no gap for the constraint to close, so
the constraint does nothing, and the sign of a 0.02% movement is noise. **US mortgage
approval carries a substantial race gap and essentially no measurable sex gap**, and the
audit refuses all twenty-six without being told to.

This replicates, on twenty-six US states, precisely what the third cohort found in Brazil:
conditional sex gaps of 0.005–0.039 sitting below the audit's own floor, and the gates
refusing the cohort off-continent. Two countries, two instruments, the same refusal — which
is a much better argument for the floor than any amount of reasoning about it.

## What it settles

* The allocation evidence is no longer thin. Lending goes from 8 markets to **50 states**,
  and on the arms the audit will actually accept the direction rule is **12 of 12**.
* The disparity floor earns its place twice over. It refuses 26 arms here for the same
  reason it refused Brazil, and in both cases refusing was correct.
* The paper's "natural-arm direction holds 7 of 8" is superseded by a far larger sample at
  a similar rate: 25 of 31 on the parity floor alone, 12 of 12 with both gates.

## What it does not settle

**This is not a seal.** These are natural arms measured post-hoc, exactly as documents 65
and 70 record for the earlier markets. It is coverage, not a test, and it cannot become one
retroactively — a sealed lending result would now need fresh markets, and there are no
unmeasured US ones left. That would mean another country's mortgage register.

**One vintage, one country.** Every arm is HMDA 2018. Nothing here speaks to other years or
other jurisdictions, and the paper's vintage lesson applies with full force.

**The four original Mississippi and Louisiana arms are excluded** from these counts: they
were written under an older results schema without `n_test` and are not directly comparable.
They are unaffected and remain as the paper reports them.
