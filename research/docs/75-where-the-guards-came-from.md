# 75 — Where the guards came from

**Individual work, beyond the course submission. A provenance audit of this project's own
method, not a new result.** No experiment was run. Every threshold the audit applies is
dated from the commit that introduced it and classified by when it was fixed relative to the
data it was applied to.

Reproduce: `.venv/bin/python -m src.experiments.analyse_verdicts --magnitude-sensitivity`
and `--sealed-sensitivity`.

---

## Why this document exists

The paper says, in one sentence inside a longer paragraph, that its remaining guards "all
come from the exploratory phase" and are "frozen verbatim in the third cohort's committed
protocol". That sentence is **not accurate for every guard**, and tuned constants are exactly
where a hostile reader should look. Three classes need separating:

- **E — exploratory.** Chosen while looking at the data it was first applied to.
- **C — confirmatory.** Committed before the arms it scored existed.
- **R — retrospective.** Applied backwards to results already scored under a different rule.

A guard is not one of these. A **(guard, result) pair** is. The same 2.0-point spread guard
is confirmatory for the equalized-odds test it was written for and retrospective for the
threshold sweep it was later imported into.

## The table

| Guard | Value | First committed | Origin | Class |
|---|---|---|---|---|
| Band span (T0) | 0.40 | 2026-08-13 `21b941c` | doc 23's pre-registration | **E** for docs 23–33; **C** for every later seal |
| Correlation bar (T1/T3) | 0.70 | 2026-08-13 `21b941c` | doc 23's pre-registration | **E** → **C** |
| Partial-*r* bar (T2) | 0.40 | 2026-08-13 `21b941c` | doc 23's pre-registration | **E** |
| Parity-gap floor (T4) | 0.05 | 2026-08-13 `21b941c` | doc 12's ground, fixed in doc 23 | **E** → **C** |
| Spread / void guard | 2.0 pts | 2026-08-20 `e658ed1` | doc 33's **E0**, written for the EO test | **C** there, **R** for doc 23 — see below |
| Noise floor | 2,500 | 2026-08-13 `21bd32e` | doc 15 (2026-08-12), COMPAS at 1,584 flipping sign across seeds | **E** → **C** for every seal |
| Advisory rate | 0.10 | 2026-08-22 `f64d9a7` | docs 32/47 — see below | **E** for docs 23–47, **C** for the 08-26 cohorts |
| Magnitude guard | 1.0 pt | 2026-08-23 `50d467f` | third cohort's Stage A seal | **C** for third-direction and lending |

## The three disclosures that matter

### 1. The spread guard is retrospective, and it helped the conjecture

Document 33's E0 required a 2.0-point spread before any correlation could count. Document 23's
T1, written a week earlier and carrying the headline, required no such thing — so an arm set
where the constraint barely moved the pool could produce a large \|r\| fitted to noise.
Connecticut returns **r = −0.924 on a spread of 0.10 points**, and T1 scored it as a
refutation.

Document 37 imported E0's guard backwards into T1 and re-scored every arm set ever judged
under it. **Three Connecticut arm sets moved from "refutes" to VOID.** That is a change in
the conjecture's favour, and it must be read as one.

What makes it defensible rather than merely convenient: doc 37 audited the *other*
direction too and found **no arm set that PASSED on noise**. The guard removed three
refutations and manufactured zero confirmations. A guard that could only ever help would be
a different object; this one was checked both ways.

### 2. The advisory boundary is a refuted clause, retained in a weaker role

Document 47's sealed prediction added a low-rate clause — below a selection rate of about
0.10, predict *up* — from early data, two hours before the seal. **It scored 4 of 8 and the
clause is why**; the refinement was withdrawn and the unrefined rule was re-sealed instead
(and passed, 9 of 10).

The same observation was later retained, but in a different role: arms below 0.10 are now
**excluded** rather than predicted. That is not the clause coming back. Refusing to score an
arm cannot manufacture a correct call, whereas predicting one can, so the weaker role is
conservative where the stronger one was not. But the lineage should be stated rather than
left for someone to find: the audit's advisory boundary descends from a refuted refinement.

### 3. The headline seal applies almost none of these guards

`analyse_resealed.py` scores all ten populations raw. No parity-gap floor, no magnitude
guard, no advisory exclusion. The one guard it does invoke is the 2,500 noise floor, and it
invokes it only to record that **all ten states clear it anyway** — Nebraska, the smallest,
leaves about 3,200 test subjects. So no arm was removed by any guard. **The 9-of-10 result
has nowhere to hide an exclusion**, which makes it the cleanest scoring in the paper, and it
is worth saying plainly because the rest of this document lists places where guards do bite.

**A correction to this document's own method, while it is auditing everyone else's.** The
first draft of the table above dated the noise floor and the advisory boundary to
2026-08-23, from the commits introducing the constants named `NOISE_FLOOR` and
`ADVISORY_RATE`, and classified both as retrospective. Both datings were wrong: they caught
a *re-encoding* in a second module, not an introduction. The 2,500 floor is document 15's,
from 2026-08-12, and was committed as `SMALL_POPULATION` in a pre-registration on 08-13; the
0.10 boundary was committed on 08-22 with the sealed clause that used it. Searching for a
constant's name rather than its value is exactly the mistake this document exists to catch,
and it was made here first.

Applying the parity-gap floor to it post-hoc, which no protocol asked for:

| gap floor | retained | correct | best constant | beats it |
|---|---:|---:|---:|---|
| 0.02 | 8 | 7 | 5 | yes |
| 0.05 | 8 | 7 | 5 | yes |
| 0.08 | 5 | 4 | 4 | no |
| 0.10 | 2 | 2 | 2 | no |

The margin survives at the two lower floors and becomes **untestable** at the two higher
ones, where the cohort falls to five arms and then two. That is running out of data, not
being refuted, and it should be described as running out of data.

## The 1.0-point guard is operational, not natural

The paper reports that the rule is correct on 21 of 22 sealed arms above one point and 11 of
18 below, and calls the guard "measured, not assumed". That is evidence **a floor exists**.
It is not evidence the floor belongs at 1.0, and the two claims read alike unless the sweep
is shown. Swept over the same forty sealed arms:

| floor | above | below | separation |
|---|---|---|---:|
| 0.25 | 29/34 | 3/6 | +35% |
| 0.50 | 26/30 | 6/10 | +27% |
| 0.75 | 22/26 | 10/14 | +13% |
| **1.00** | **21/22** | **11/18** | **+34%** |
| 1.25 | 17/18 | 15/22 | +26% |
| 1.50 | 15/16 | 17/24 | +23% |
| 2.00 | 11/11 | 21/29 | +28% |
| 3.00 | 9/9 | 23/31 | +26% |
| 5.00 | 8/8 | 24/32 | +25% |

**Every floor from 0.25 to 5.00 separates**, by +13% to +35%. The best is 0.25 at +35%; the
committed 1.00 gives +34%. The dip at 0.75 is a small-bin artefact, and its presence is the
useful part of the table: it shows the separation estimate is noisy at forty arms, so no
value in this range can be argued to be *the* right one.

So: **the existence of a floor is measured; its location is operational.** One point is a
round number fixed in a protocol before the cohorts ran, which the data neither singles out
nor contradicts. The paper should say that rather than let "measured, not assumed" carry an
implication about the value.

Post-hoc, and labelled: the cohorts were scored at 1.0 exactly as pre-registered. Nothing
here re-scores them.

---

## What this changes in the paper

1. The provenance sentence is corrected — the spread guard did not come from the exploratory
   phase, and the noise floor and advisory boundary postdate the re-seal.
2. The retrospective guard's **direction of benefit** is stated: three refutations voided,
   zero confirmations created.
3. The advisory boundary's descent from a refuted clause is stated.
4. "Measured, not assumed" is narrowed to the guard's existence, with the value named as
   operational.
5. The re-seal's freedom from all of these guards is stated as the point in its favour that
   it is.
