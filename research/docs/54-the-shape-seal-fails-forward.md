# 54 — The shape seal fails forward, and the 2022 curves come out upside down

**Individual work, beyond the course submission.** The seal was committed at `391cd17`
before any of the eight arms existed; `research/results/shapes/shapes.csv` is the scored
table, and every sweep sits in `research/results/acs_income_*_201[4]*` and `*_2022*`.

## The verdict, exactly as sealed

**FAILS: 4 of 6 scored, against a bar of 5, and the best constant (always-LOW, 5 of 6) is
not beaten.** Two of the eight arms are excluded as flat under the pre-registered rules —
SC-2022 by the spread guard, NV-2022 with only three arms surviving the gap floor (its sex
gaps hover at 0.038–0.049). Six scored meets the pre-registered minimum, so the verdict
stands and is a failure.

## Where the rule was right, and it is the striking half

The **backward direction was perfect**. All three 2014 calls landed, including the two
within-state flips no constant could express: Texas, U-shaped in 2018, is a clean classic
crossing in 2014 (`--++++++`); New York likewise (`-------++`); Nevada-2014 classic
(`----+++`); Virginia-2014 all-positive as called. Four of four on the 2014 side, with the
base rate correctly ordering which states flip.

## Where it failed, and what the failure uncovered

The **forward direction (2022) failed completely — because the 2022 curves are a shape the
project had never seen.** Every 2022 population, including NV-2022's below-floor arms,
runs *positive at low selection rates and negative at high ones*:

| population | signs (low rate to high) | reading |
|---|---|---|
| AL-2022 | `+++-----` | inverted crossing |
| OH-2022 | `+------` | inverted |
| SC-2022 | `++------` | inverted, flat by spread |
| NV-2022 (all 7 arms) | `+++----` at rates 0.245→0.659 | inverted |

This is not the U the boundary predicted, and not the classic S: it is the central
within-population relationship **with its sign flipped**. In 2014 and 2018 data the
constraint takes at low rates and gives at high ones; in these four 2022 populations it
does the opposite. The sealed rubric's family classifier counts sign changes, so it filed
the inverted crossings as "LOW", which is why the constant scored 5 of 6 — a rubric
artifact disclosed here: "LOW" for AL-2022 and OH-2022 means *inverted*, not *classic*.

## Two suspects, named before anyone gets attached to either (post-hoc)

* **The RELP shim.** The 2019+ files rename and recode the relationship column; our loader
  maps `RELSHIPP` onto `RELP` as unordered levels. The proxy structure of the feature set
  therefore differs across the boundary, and document 16 showed proxy structure can matter.
* **The 2022 vintage itself.** A post-pandemic labour market, and an inflation-eroded
  \$50,000 label that sits much lower in the real income distribution than it did in 2018.

The discriminating diagnostic is cheap and is queued: **Nevada 2019** — the first
`RELSHIPP` year, pre-pandemic economy. Classic 2019 curves acquit the shim and indict the
2020s economy; inverted 2019 curves indict the shim era. A drop-the-column variant on one
2022 state is the follow-up if 2019 is ambiguous.

**Addendum, next day — both diagnostics ran, and the shim is acquitted.** NV-2019 showed
no inversion but also no signal (spread 1.3, void), an acquittal too thin to lean on. So
Ohio-2019 was swept — the signal-rich lineage, classic in 2018 and inverted in 2022 — and
it is **cleanly classic**: signs `-------++`, crossover bracketed at 0.577–0.631, spread
8.0, gaps healthy throughout. The 2019 file carries the recoded column and a pre-pandemic
economy, and behaves normally; therefore the recoding does not produce the inversion, and
whatever does arrived **between 2019 and 2022, in the world rather than in this pipeline**.
Ohio's crossover also drifts upward along the way (0.556 → ~0.60) before vanishing into
the 2022 inversion — recorded as trajectory, not theory. The 2020s-vintage caveat stands,
now with its cause narrowed to the era itself; identifying the mechanism needs 2021/2023
arms or economic covariates, and is deliberately left for a design that postdates this
data, per the corollary of document 56.

## What this changes

* **The base-rate boundary is not a law of shape.** It ordered the 2014/2018 world
  perfectly — eleven populations, two sealed flips — and the 2022 world broke it. Like
  every transfer claim in this project, it is now scoped: within the data vintage it was
  fitted on, not across vintages.
* **The within-population direction claim acquires a vintage caveat.** Every prior result
  here uses 2018-or-earlier data (Adult 1994, Dutch 2001, COMPAS 2016, ACS 2018, Taiwan
  2005, HMDA 2018, LSAC 1990s). Four 2022 populations inverting is the first evidence the
  *relationship itself* may be time-dependent — or artefactual, per the shim suspect —
  and no claim about 2022-era deployments should be made until the diagnostic runs.
* **The ledger gains its seventh failure**, and the paper's ledger table is updated,
  because "nothing is omitted" is a sentence that has to stay true.
