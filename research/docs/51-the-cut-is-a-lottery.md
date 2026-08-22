# 51 — The cut is a lottery: what the optimiser actually does on the deep-tail arms

**Individual work, beyond the course submission. Post-hoc mechanism probe** — nothing here
was predicted in advance. Recomputed by `analyse_routes.py --probe-mixture`;
`research/results/routes/routes_mixture_probe.csv` holds every number below.

[Document 50](50-the-divergence-is-who-moves.md) established that deep-tail arms split into
lift arms and cut arms, and that no stored aggregate predicts which a given arm will be.
This probe looks past the aggregates at what the mitigated model actually *is*: ExpGrad
returns a randomized mixture, and each person's probability of approval under that mixture
shows which solution the optimiser found.

## The two solutions, and they are qualitatively different

**A lift arm is a graded tilt.** On Oregon at threshold 0.87, people below the line hold
real approval probability that rises with their score — 0.20 just under the threshold,
fading to 0.04 further down — with the unprivileged in each score band lifted two to three
times as often as the privileged. Above the line, positives are kept at ~0.87–0.91,
lightly trimmed, privileged more. The mixture behaves like an informed adjustment: who
moves depends on who they are and where they sit.

**A cut arm is a lottery.** On the Dutch census at threshold 0.965, *nobody* below 0.95
of either group receives any probability at all — four consecutive score bins at exactly
0.000 — and everyone above the threshold, both groups alike, is kept with one flat
probability near 0.65. COMPAS at 0.775 is the extreme case: keep-probability 0.135 for
everyone above the line, correlation with score exactly zero. The optimiser found no
useful tilt and fell back on the solution that always exists: discard a fixed fraction of
*all* positives at random, which shrinks the absolute gap multiplicatively. The parity
certificate is earned by a coin flip over the very people the model itself rates highest.

## The signature separates all nine arms

| arm | direction | granted below line | keep above | corr(P, score) above |
|---|---|---|---|---|
| OR @0.87 | up | 0.069 | 0.909 | +0.31 |
| AL @0.87 | up | 0.073 | 0.868 | +0.41 |
| KY @0.87 | up | 0.232 | 0.810 | +0.47 |
| SC @0.87 | up | 0.147 | 0.531 | +0.38 |
| CT @0.87 | up | 0.333 | 0.787 | +0.44 |
| Dutch @0.965 | down | 0.015 | 0.651 | +0.12 |
| Dutch @0.93 | down | 0.034 | 0.581 | +0.26 |
| COMPAS @0.775 | down | 0.000 | 0.135 | 0.00 |
| LSAC @0.995 | down (void) | 0.000 | 0.124 | 0.00 |

`granted below line` — mean mixture probability for people within 0.05 under the
threshold — separates perfectly: every lift arm at 0.069 or above, every cut arm at 0.034
or below. Nine of nine, including the matched pair (OR @0.87 and Dutch @0.965) that agrees
on every aggregate document 50 could compute and moves in opposite directions.

## What this is and is not

It **names the mechanism**: lift versus cut is graded-tilt versus lottery, and the
signature is measurable from any fitted mitigation. It gives auditors something concrete:
a mitigated model whose kept-positives probability is flat in the score is levelling down
*by random discard*, not by any judgment about who deserves what — which connects directly
to the paper's arbitrariness thread and is, arguably, the strongest reason yet to
distrust a parity certificate on a low-rate system.

It does **not** answer document 50's question of *when* each occurs: the signature is
post-fit, so it diagnoses rather than predicts. Why ExpGrad finds a tilt on the ACS
populations and collapses to the lottery on Dutch and COMPAS — with the geometry
candidates all dead — remains a property of the optimiser's feasible set, and after the
large-state landscapes of [document 52](52-the-campaign-answers-a-different-question.md),
plainly part of the same open question: what makes a population's response monotone,
liftable, or neither.
