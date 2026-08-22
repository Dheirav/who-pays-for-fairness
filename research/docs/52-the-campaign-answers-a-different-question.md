# 52 — The sealed campaign is underpowered on its own question, and answers a harder one

**Individual work, beyond the course submission.** The residual test was sealed at `93c3446`
and the magnitude model at `f0f8056`, both before any of the 86 arms existed. Every outcome
below is scored by the committed analysers; `research/results/residual/` and
`research/results/sealed_magnitude/` hold the tables.

## The two sealed verdicts, exactly as the seals prescribe

**The residual test returns UNDERPOWERED.** Three new crossovers located against a
pre-registered minimum of six, so no verdict is claimed on either candidate predictor. R1
(gap) and R2 (size) remain unjudged, not failed.

**The magnitude model FAILS, decisively** — ledger failure number six. Frozen at MAE 10.6
against 13.9 in leave-one-population-out, it scored **4.50 against predict-zero's 0.77** on
the sixteen retained New York and Texas arms, with Spearman +0.05: no size information at
all. The model predicted effects of 3–8% from the band span; the observed effects are
almost all under 1%. The paper's concession — direction, never size — stands, and it is now
earned six times over.

## What the campaign found instead, and it is bigger than what it missed

**1. The crossover cluster did not survive contact with more states.** The three located
crossovers are Ohio at 0.556 (inside the old cluster), **Pennsylvania at 0.652** and
**Florida at 0.284** — both far outside 0.43–0.58, both with tight brackets, large spreads
and every guard passed, on the same instrument the cluster was built from. Seven located
crossovers now span **0.28 to 0.65**. "Expect about 0.54" was a four-population statement,
document 45 already widened it to 0.43–0.58, and tonight breaks it as anything tighter than
"population-specific, often near the middle".

**2. The within-population landscape is not always monotone.** Six states failed to bracket
a crossover, and the sign patterns say why (low rate to high, retained arms):

| state | pattern | reading |
|---|---|---|
| LA | −−−−−−−− rising | classic; crossover just above its sweepable window |
| NY | +−−−−−+ | U-shape; void by the spread guard (1.93 < 2) |
| TX | ++++−−−++ | U-shape, two sign changes, no bracket possible |
| IL | +−−−−−−+ | U-shape |
| NJ | ++++++ | levels up across the whole 0.29–0.70 window |
| VA | +++++++ | levels up everywhere, most at the edges |
| MA | ++++−+ | positive with one near-zero blip |

The monotone picture — down below one point, up above it — held on every population swept
before tonight (AL, KY, SC, OR, COMPAS, Dutch). On the large, richer states it is the
exception: two show clean monotone behaviour (OH, PA-with-late-crossover), while the rest
are U-shaped, flat-positive, or one-signed. These are mid-window arms of the trusted route,
not the deep-tail artifacts of document 50; the magnitudes are small (mostly under ±4%) but
the shapes are consistent within each state.

**3. The natural arms score the 0.54 rule at 5 of 10 — post-hoc, and internally
consistent.** Tonight's ten states also produced natural-operating-point arms, and scoring
the sealed direction rule on them (post-hoc: these arms were run for the residual campaign,
not selected for a direction test) gives:

| state | rate | pool | rule says | outcome |
|---|---|---|---|---|
| TX | 0.347 | +0.86% | down | miss |
| NY | 0.415 | −0.56% | down | ok |
| FL | 0.288 | +0.32% | down | miss |
| IL | 0.387 | −0.85% | down | ok |
| PA | 0.333 | −4.21% | down | ok |
| OH | 0.308 | −3.02% | down | ok |
| NJ | 0.517 | +0.88% | down | miss |
| VA | 0.438 | +3.00% | down | miss |
| MA | 0.492 | +0.66% | down | miss |
| LA | 0.291 | −9.62% | down | ok |

Each miss agrees with its own state's sweep: Florida turns up at 0.288 and its located
crossover is 0.284; Virginia's natural arm is positive and so is its entire sweep. So the
**within-population** relationship holds — a state's own crossover predicts its own natural
direction — while the **fixed 0.54 prior** does not transfer to these populations.

Combining every never-before-measured natural or cutoff arm this project has scored — the
ten sealed this morning (9 of 10) and tonight's ten (5 of 10, post-hoc) — the rule stands
at **14 of 20 against a best constant's 11**. That is a real edge and far from a law, and
the morning's own caveat, "the sealed evidence buys depth, not breadth", turns out to bind
*inside* the instrument: the sealed cohort was mid-size and mid-income states, tonight's
cohort is the largest and richest, and the prior travels worse toward them.

## What stands and what changes

* **Document 49's sealed result stands as scored** — committed rule, committed bar, 9 of
  10, constant beaten. What tonight narrows is its interpretation: the pass showed the
  prior transfers to populations *like those*, and tonight shows populations it transfers
  to less well, which is a scope statement the paper now has to carry.
* **The paper's crossover-stability section is rewritten** around the 0.28–0.65 span, the
  magnitude failure joins the ledger, and the accounting table gains the campaign.
* **The regime result, the who-pays accounting and the mechanism findings are untouched.**
* **The open question sharpens.** The residual question ("what predicts the crossover")
  stays open and is now harder, because locating a crossover at all assumes a monotone
  landscape, and a third of these states do not have one. What distinguishes the states
  that level up below 0.54 — richer, larger, natural rates 0.35–0.52 — from those that do
  not is the new top question, and it is exactly the kind that population properties might
  actually answer.

## Method note

The interim peek at nine of ten states happened only after the standing decision, recorded
in the session before looking, that Texas would finish and everything would be scored
regardless of what appeared. Texas completed during the peek itself; the final scoring above
is the committed procedure over the complete campaign.
