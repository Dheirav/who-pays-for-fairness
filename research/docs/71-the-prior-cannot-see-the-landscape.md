# 71 — The prior cannot see the landscape

**Individual work, beyond the course submission. Post-hoc diagnostic, labelled as such.**
Six operating-point sweeps, 54 arms, 26 Aug. Not a seal.

## The question

Pooling all four sealed direction cohorts gave a calibration in which the rule scored
**1 of 6 within 0.05 of its cohort's crossover** — worse than a coin. Document 69 had
already established that the near-crossover band is where inference lives, so a band in
which the rule is anti-predictive is not a detail.

The first explanation offered — and written into the paper and into `SEAL-DESIGN-4.md`
before this test ran — was that the transported prior simply lacks *resolution* at that
scale: with located crossovers spanning 0.28 to 0.65, being within 0.05 of 0.54 says little
about which side of one's own crossover one sits.

That explanation is testable. Sweep those six populations, locate each one's own crossover,
and ask whether the miss is explained by the arm sitting on the far side of it.

## The result

| population | signs by rate | shape | verdict |
|---|---|---|---|
| `acs_income_md_2018` | `-+++++++++` | classic, crossover 0.15–0.29 | **explained** |
| `acs_income_in_2014_t30000` | `++++-----+` | non-monotone, 2 flips | rule does not apply |
| `acs_income_mo_2014_t30000` | `++++------` | **inverted** (+ to −) | not a misplaced crossover |
| `hmda_ny_2018_race_improvement` | `+-----++` | non-monotone, 2 flips | rule does not apply |
| `hmda_md_2018_race_improvement` | `+------+` | non-monotone, 2 flips | rule does not apply |
| `hmda_il_2018_race_improvement` | `+----+++` | non-monotone, 2 flips | **control — rule was right** |

**Maryland is explained.** Its own crossover sits at 0.15–0.29, its natural rate of 0.508 is
well above that, the rule read against its own crossover says *up*, and it went up. The
transported prior said *down* only because 0.508 < 0.54, while Maryland's real boundary is
0.32 away from the prior. Resolution, exactly as proposed.

**The other five are not.** They are populations whose response has no single rising sign
change, so no directional rule applies to them at all — and one of them, Missouri, is
outright inverted.

## The control is what makes this readable

`hmda_il_2018_race_improvement` was included because the rule got it **right**. Its landscape
is non-monotone too. So non-monotonicity does not distinguish the misses from the hit: the
hit was luck, on a population where a directional rule has nothing to predict.

Had the control come back classic, the honest reading would have been that the rule fails
specifically where it misses. It did not, and the reading is different and better: **arms
sitting near a transported prior are disproportionately drawn from populations the rule was
never claimed to cover.**

## What it settles

**The dead band's cause is not resolution. It is that a transported prior cannot detect a
non-monotone landscape, because detecting one requires the sweep the prior exists to avoid.**
Algorithm 1 returns \textsc{non-monotone} on all five, and would have refused every one of
them. The procedure was never exposed; only the transported prior was.

This is an argument for the sweep-conditional claim and against the transported prior, and
it is sharper than any previous statement of that preference, which rested on the prior
scoring 9 of 10 and then 5 of 10 without a mechanism. Here is the mechanism.

## Two findings that came free

**Missouri 2014 is inverted at a $30,000 cutoff.** The paper attributes inversion to the
2022 nominal-label slide — a fixed dollar threshold sliding down an inflated distribution,
diagnosed and repaired by quantile-anchoring. This is 2014, a vintage the paper treats as
clean. The vintage account is therefore incomplete: it explains the 2022 inversions but is
not the only route to one.

**All three HMDA home-improvement sweeps are non-monotone, with the same `+ … − … +`
U-shape.** That is a domain observation, and it supplies a mechanism the paper currently
lacks: the HMDA sweep failed its held-out test at 2 of 4 and then at 2 of 6 across six
markets, and was recorded as "unreliable on mortgage data" without a reason. The reason is
that the improvement product's response is U-shaped, so a procedure assuming one rising
crossing cannot bracket it.

## What it does not settle, and this bounds every sentence above

**These six populations were chosen because they sit near a boundary.** That is a biased
sample by construction — the whole point was to examine the misses. Nothing here supports a
claim of the form "N% of populations are non-monotone", and in particular it does not
establish whether non-monotone landscapes are common in general or concentrated near
transported priors. Six of this project's 107 populations have been swept for this.

Answering that needs a fresh, unbiased draw: sweep a random sample of populations regardless
of where their natural rate falls, and count. Until then the honest statement is that
non-monotonicity is common **among near-boundary arms**, which is a much narrower claim and
the only one the data carries.
