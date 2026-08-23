# 58 — The third council, and the audit's own accounting

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**
Ten fresh review lenses (human factors, bank examiner, EU law, sociology of measurement,
ML systems, Goodhart adversary, pedagogy, replication lab, forecasting, hostile skeptic)
returned 6 minor / 4 major revisions and no rejects. The text-only and cheap-compute
fixes are applied; this records the three fixes that produced *numbers*.

## 1. What Algorithm 1 actually returns, totalled (`analyse_verdicts.py`)

The skeptic's cheap question: a procedure whose refusals are first-class should still
total how often it answers. Run over the 45 population-label pairs with stored sweeps,
with the deep-tail advisory rule (arms below rate 0.10 excluded from the shape call —
the council's ask to move that caution from prose into the algorithm):

| verdict | n |
|---|---|
| WITHDRAWAL | 20 |
| EXTENSION | 7 |
| NON-MONOTONE | 6 |
| VOID (flat or too few arms) | 10 |
| REFUSED (noise floor) | 1 |
| bracket, no natural arm | 1 |

The audit answers six times in ten. All 27 directional verdicts match the natural arm's
observed direction — a **consistency check, not validation**: the natural arm is part of
the curve being read. Encoding the advisory rule is what restores Alabama and South
Carolina to WITHDRAWAL (their leading `+` arms are the documented divergence arms);
TX/MA/IL 2018, Dutch, and the nominal-label 2022 curves stay genuinely NON-MONOTONE.

## 2. The lottery does not appear at natural operating points (`--probe-natural`)

The skeptic's strongest lottery objection: the 9/9 signature lived in the region the
limitations call unreliable. The control probes seven natural arms spanning both
directions (Adult, AL, OR, Dutch, FL, VA, MA). **No flat lottery anywhere**: every
natural-point mixture is graded — probability granted below the boundary (0.17–0.43 vs
0.00–0.07 on deep cut arms), keep probability rising in the person's own score
(+0.37 to +0.73 vs ≈ 0) — even Adult, which cuts a fifth of its pool. The lottery is a
severe-operating-point phenomenon. This narrows the paper's charge and sharpens the
audit: a flat mixture is a flag, not the expected cost of parity. Per-fit wall-clock was
recorded on the way (1.8–10.2 s at 15k–69k rows), which became the paper's cost
paragraph.

## 3. The sealed cohorts under the frozen gap floor (`--sealed-sensitivity`)

The exclusion floors were tuned in-sample, so the sealed cohorts are where their choice
must not matter. Re-scoring at floors 0.02/0.05/0.08/0.10: the re-seal keeps 8 of 10
arms at the frozen 0.05 floor and scores **7 correct against a best constant of 5 — the
margin survives**. The two arms the floor drops (IA, NE; gaps 0.016–0.017) are arms the
audit itself would refuse: the cohort's extreme-rate coverage came partly from
sub-floor-disparity arms, now said in the paper. At 0.08+ both cohorts thin below
scoreability.

## The statistics reframing (forecasting panel)

The 0.046 binomial answers "could a guesser do this"; the paired question — did the rule
beat the constant on the same ten arms — comes down to the five discordant calls, of
which the rule wins four: one-sided sign test p ≈ 0.19, sequential correction ≈ ×2 on
top. Both statistics now stand side by side in §resealed, and "strong evidence" is gone.
The attribute-aware 9/9 is relabelled a theory-consistency check (the theorem made its
prior ≈ 1).

## Also applied

EU legal correction (AI Act Art. 10(5) permits training-time bias-correction use; the
paper had the split backwards); Algorithm 1 gains INDETERMINATE and loses the
"far from 0.54 → inspect" non-step; strategic-robustness paragraph (the audited party's
degrees of freedom, closed by exporting the sealing discipline); all eleven ledger rows
now carry seal→score hash pairs (each ordering re-verified) plus the honest local-clock
limit; HMDA model documentation; definitions and protocol blocks; the predicted-labels
vs allocations limitation; data manifest with SHA-256 per input file
(`research/data-manifest.csv`); pytest repaired into the requirements and the four
never-executed in-processing tests fixed and passing.

## Not yet done, deliberately

The seal-story consolidation and any compression await the venue answer (Pass 3); the
worked end-to-end trace, the four-threshold version of the domains table, and the
derandomization test (does the direction survive extracting a deterministic classifier —
the only form a US lender could deploy) are queued; the third sealed cohort remains the
binding IPUMS design and is what the abstract now points to from the 9 of 10 itself.
