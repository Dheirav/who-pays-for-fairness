# 74 — What the sweep buys that one fit does not

**Individual work, beyond the course submission. Post-hoc accounting, labelled as such.**

Reproduce: `.venv/bin/python -m src.experiments.analyse_circularity`

---

## The objection

The sharpest one raised against this paper, and the one it had been asserting an answer to
rather than showing one:

> Locating a crossover requires sweeping the constraint across operating points. A team
> that can afford that sweep could instead fit the constrained model **once**, at the
> operating point it actually uses, and read the pool change directly. What has prediction
> bought over measurement?

The objection is right that a single fit answers the question it asks, and it is right that
the sweep is strictly more expensive. It is wrong that the question a single fit answers is
the question a deploying team has.

A single fit returns a **point**: what this constraint did, at this threshold, on this run.
The sweep returns a **neighbourhood**: whether that point is near a sign change, whether the
sign is stable across the thresholds the team could plausibly choose, and whether the
population admits a stable sign at all.

Three measurements separate them. Two of the three are the answer; the third is reported
because it is real but does not carry weight, and saying so is cheaper than being caught.

---

## 1. One fit's answer does not travel

For every adjacent pair of arms in a stored sweep — both above the paper's own 1.0-point
magnitude floor, so this is not a story about noise — does the sign at one arm hold at the
other?

| rate moved by | pairs | sign flipped |
|---|---:|---:|
| < 0.05 | 205 | 15% |
| 0.05–0.10 | 372 | 7% |
| 0.10–0.20 | 58 | 14% |
| > 0.20 | 4 | 100% |
| **any move** | **639** | **11%** |

**69 of 639 adjacent pairs disagree on the sign.** A single fit implicitly asserts that its
answer describes the constraint rather than the threshold; on this evidence that assertion
fails about one time in nine, on effects large enough to read.

**The caveat, which cuts against the headline.** These sweeps were deliberately densified
around located crossovers. The narrow-gap bins therefore oversample the boundary, and the
per-band rates are not a random sample of threshold moves a team might make. The 11% is a
property of this arm set, not an estimate of a population quantity. What survives the caveat
is the qualitative claim, which is all that is needed: the sign is not a fixed property of a
population and a constraint, and one fit cannot tell you which of the two it measured.

## 2. Populations sit close to their own boundary

Twenty-two arms have both a located crossover and a natural operating arm, from **21
disjoint person samples** under the paper's own independence rule.

| natural rate is within | samples | share |
|---|---:|---:|
| 0.05 of its crossover | 6 of 21 | 29% |
| 0.10 | 11 of 21 | 52% |
| 0.15 | 15 of 21 | 71% |
| 0.20 | 16 of 21 | 76% |

**Half of them sit within ten points of the sign change.** Florida 2018 sits at 0.288 with a
crossover at 0.284 — on the boundary. Texas 2014 is four points away, Alabama three, Utah
five.

This is the answer to the objection, and it is a claim about *decisions*, not precision. For
a team within reach of its own crossover, the difference between a constraint that withdraws
favourable decisions and one that extends them is not a fact about the population that must
be accepted. It is a threshold the team already controls. One fit reports the withdrawal and
the team's options are to accept it or abandon the constraint. The sweep reports the
withdrawal **and the distance to the sign change**, which is a third option that a single
measurement cannot produce because a single measurement has no second point to compare
against.

**And the boundary is not even a property of a state.** Florida 2018 appears twice, once per
protected attribute: the same people, read by sex, cross at 0.284; read by race, at 0.439. A
crossover belongs to a (population, attribute) pair. There is nothing to transport here even
within one sample, which is the anti-circularity point in its sharpest form — the sweep is
not recovering a constant that could have been looked up.

## 3. Where one fit's sign is unreliable on its own terms — the weak one

Seed agreement on the sign, binned by distance from the population's crossover:

| distance | arms | all 5 seeds agree | mean \|pool %\| |
|---|---:|---:|---:|
| < 0.05 | 40 | 82% | 3.14 |
| 0.05–0.10 | 32 | 94% | 7.08 |
| 0.10–0.20 | 51 | 98% | 9.03 |
| > 0.20 | 66 | 82% | 11.70 |

Sub-1.0-point arms are unanimous on the sign **55%** of the time — a coin flip, consistent
with the 61% figure the paper already reports for directional accuracy below the floor.

**Why this is the weakest of the three, stated rather than buried.** Two reasons. First, the
pattern is not monotone: the far bin drops back to 82%, and inspection shows why — three of
its five non-unanimous arms are sub-1.0-point effects, so the magnitude floor is doing the
work that distance appears to be doing. The two quantities correlate at r = +0.648, which
the paper already reports. Second and more damaging: **repeated fits at one operating point
would expose this too.** A team that can afford a sweep can certainly afford five seeds at
its own threshold, and that would tell it its sign is unstable without locating any
crossover.

So section 3 is a reason to distrust a single fit. It is not a reason that requires a sweep.
Sections 1 and 2 are.

---

## What this changes in the paper

The circularity objection now has a demonstrated answer rather than an asserted one, and the
answer is narrower than the assertion was. The sweep does not buy a better estimate of what
the constraint will do at today's threshold — one fit, repeated across seeds, gets that. It
buys **shape**: how far the answer travels, how near the boundary sits, and whether the
population has a boundary at all.

Stated as a limitation rather than a win: if a team is far from its crossover, its landscape
is monotone, and its effect is well above a point, then one fit and a handful of seeds tell
it what it needs, and the sweep is a more expensive route to the same decision. **5 of these
21 samples (24%) sit more than 0.20 from their crossover** and are in that position on the
distance criterion.

That 24% is an over-estimate of how often the sweep is wasted, and the reason matters. All
21 samples here *have* a located crossover, which means they already passed the monotonicity
screen. The 22% of populations that admit no directional rule at all (document 73) never
enter this table, and for those the sweep is the only thing standing between a team and a
confident wrong answer. Counted against every population rather than against the ones with
clean landscapes, the share that could have skipped the sweep is nearer a fifth.

The sweep earns its cost on the rest — and a team cannot know which group it is in without
running it.

That last sentence is the whole answer. The sweep is not circular because its output is not
the thing one fit measures; and the only way to learn that you did not need it is to do it.
