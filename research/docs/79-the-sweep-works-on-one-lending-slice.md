# 79 — The audit returns a verdict on a lending sweep, on the right object this time

**Individual work, beyond the course submission. Not a seal — a sweep read by Algorithm 1's
frozen guards.** Reproduce:
`.venv/bin/python -m src.experiments.analyse_verdicts --dataset hmda_tx_2021_race_manufactured`

---

## What was run, and why it is a different object from 7.1b and 7.2

Every lending test before this compared *populations at their natural rates* — the
cross-population object the paper says does not transport, and the one document 77 mistook for
the claim. This is a **within-population operating-point sweep**: one market held fixed (Texas
2021, manufactured housing, race arm), the decision threshold moved across the frozen lending
grid, six arms plus the natural arm. That is the object the paper's monotonicity claim is
*actually about*, and it had never been run to a verdict on real allocations, because document
71 found the earlier lending sweeps returning U-shaped and the audit refusing them.

## The verdict

**Algorithm 1 returns WITHDRAWAL.** Sorted by selection rate, the kept arms give signs
`- - - - +` — a single sign change — bracketing a crossover at **0.448–0.495**. The natural
operating rate is 0.448, below the bracket, so the audit predicts withdrawal, and the natural
arm withdrew (−1.68%).

| threshold | selection rate | pool change |
|---|---:|---:|
| @0.92 | 0.021 | −16.7% |
| @0.85 | 0.060 | −20.2% |
| @0.75 | 0.143 | −31.3% |
| @0.65 | 0.267 | −18.4% |
| @0.55 | 0.395 | −6.5% |
| @0.45 | 0.495 | **+2.4%** |
| natural | 0.448 | −1.7% |

One crossing, negative below it and positive above, on decisions actually made about people.

## What this does and does not establish

**It establishes that the sweep is not uniformly unreliable on lending.** Document 71's
finding — bracketing fails because lending sweeps come back non-monotone — was drawn from
home-improvement and purpose sweeps. On manufactured housing the sweep returns a clean single
crossing that the audit accepts. So the correct statement is narrower than the paper currently
makes: the sweep is unreliable *on the lending sweeps tried before this*, not on lending as
such. The paper should soften "the sweep is unreliable on mortgage data" to match.

**It is the first within-population confirmation of the phenomenon on real allocations.** The
paper's central empirical claim is that within a population Δpool rises with the selection rate
and crosses zero once. Every prior demonstration was on predicted labels (ACS, the survey) or
on the wrong cross-population object. This is that claim, on its own terms, on mortgage
approvals.

**It does not establish that the direction was predictable in advance here.** The natural
arm's direction was already measured before this sweep ran, so the audit agreeing with it is a
consistency check on the audit's reading of its own curve — not a forecast. The paper already
draws this distinction for the ACS verdicts and it applies identically here.

**And it is one market.** One monotone sweep does not make the sweep reliable on lending; it
makes it *not uniformly unreliable*. The honest generalisation is: on the one lending slice
that reaches below a crossover, run on the largest available market, the audit's sweep behaved
exactly as the paper says a well-shaped population should. Whether that holds on a second
manufactured market is untested, and — given how the last two "it holds on ten, let me add
six" results went — should stay untested-in-print rather than asserted.

## Where the lending record stands now

Six attempts, and they no longer all point the same way:

1. six-market sweep — sweep unreliable, refused;
2. sealed lending cohort — every arm up, constant tied;
3. 7.1 purpose split — nothing below the crossover;
4. 7.1b dwelling split — transported 0.660 badly placed, lost to a constant;
5. 7.2 located-vs-transported — located value lost in its own dead band;
6. **this sweep — the audit returns WITHDRAWAL, a clean single crossing, natural arm agrees.**

The transported-prior claim is dead on real approvals: no fixed crossover predicted direction
across five attempts. The **sweep-conditional** claim — measure this population's own curve —
is confirmed on one real-allocation market and refused-or-untested on the rest. That is a
sharper and more defensible position than the paper held this morning, and it is the position
the paper argues for: measure, do not transport.

## Lending is now closed

This was framed before it ran as closing lending either way, and it does. A directional
verdict was the best available outcome and it is the one that landed, but the framing holds
regardless: no further lending cohort is planned, because the informative question left —
does the within-population sweep hold on a *second* manufactured market — is one the project's
own recent history says should be answered by more data only if someone other than the author
is choosing which markets, and there is no such person here.
