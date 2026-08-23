# 60 — The boundary does not survive a change of question

**Individual work, beyond the course submission. Sealed test, scored as committed.**
Seal `d8bfae8` (externally timestamped before any arm existed); protocol in
`analyse_task_shapes.py`; sweeps 24 Aug, 42 runs.

## The design

Six race arms of two folktables tasks this project had never run — ACSEmployment
(AL/OH/PA) and ACSPublicCoverage (OH/PA/NY) — with the curve family called from the
label base rate against the sealed 0.365 boundary before any constraint was fitted.
Calls on both sides (HIGH ×4, LOW ×2), so the best constant could score at most 4 of 6.
The sex arms of coverage were screened out honestly first: all three fail the frozen
0.05 gap floor, and the earlier scratch screen's contrary note in NEXT.md was corrected
in the seal commit itself. On coverage, Non-White is the higher-rate group — the
designed inversion.

## The score

| population | p | predicted | observed | spread | signs |
|---|---|---|---|---|---|
| employment AL | 0.410 | HIGH | **LOW** (classic crossing) | 20.4 | `----++` |
| employment OH | 0.461 | HIGH | flat (3 arms survive) | 5.2 | `--+` |
| employment PA | 0.467 | HIGH | flat (2 arms survive) | 1.7 | `-+` |
| coverage OH | 0.333 | LOW | **HIGH** | 16.6 | `---+-` |
| coverage PA | 0.306 | LOW | **HIGH** | 11.5 | `--+-` |
| coverage NY | 0.401 | HIGH | **LOW** (all-negative) | 8.6 | `-----` |

**S1: 0 of 4 against bar 3 — FAILS, constant (2/4) not beaten.** Scored exactly as
committed; the two flat populations are the accuracy guard eating the generous-rate
arms of large employment states, counted to the floor as pre-registered (4 ≥
MIN_SCORED).

## What it settles

Every scored call was *wrong*, which is more informative than random: the boundary
carries signal on these tasks with the sign inverted, on both sides. Three shape seals
have now failed three different ways: cross-year (doc 54 — resolved as the nominal
label sliding, doc 57), cross-attribute (doc 55 — race arms classic where sex arms
were not), and now cross-task. The conclusion is one sentence: **the 0.365 base-rate
boundary is a property of the ACS income question, not of base rates.** Whatever
governs curve shape involves the task's structure, not the label's rarity — the open
question sharpens again, and the S3 shape component of the IPUMS protocol (income
tasks, real-anchored) remains the right next test of the boundary in the only domain
it has ever worked in.

Worth recording beside the failure: employment AL is a **clean classic crossing** at a
new task (its bracket sits in the 0.33–0.42 rate region — post-hoc, located, not
predicted), and every scored population's *natural-arm direction* went down at rates
0.31–0.47, as the direction rule expects below the crossover. The direction claim is
untouched by this seal; the shape claim shrinks to its home task.

## Accounting note

The six task populations share persons with the already-counted income populations of
the same states (employment AL contains income AL's workers), so **the independent
population count does not change**: these enter the record as arms of four states'
persons under new questions, and the paper's accounting table says so explicitly.
