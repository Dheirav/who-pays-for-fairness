# 55 — Shape is not attribute-independent: every race arm is classic, and the seal fails

**Individual work, beyond the course submission.** Sealed at `aa6532b` before any race arm
existed; scored by the committed analyser; `research/results/race_shapes/race_shapes.csv`
holds the table. Zero failed runs across the campaign's 48.

## The verdict, exactly as sealed

**FAILS: 2 of 6 against a bar of 5, and the constant — always-classic, 6 of 6 — is not
beaten.** The prediction was that each race arm reproduces its state's sex-arm curve
family, because documents 50/51 read shape as a property of the label side (base rate,
reservoir), which the attribute swap holds fixed. It does not reproduce it:

| state | sex arm (2018) | race arm predicted | race arm observed | race spread | sex spread |
|---|---|---|---|---|---|
| TX | U-shaped | HIGH | **classic** | 39.9 | 2.8 |
| VA | all-positive | HIGH | **classic** | 23.5 | 7.0 |
| OH | classic | LOW | classic | 43.6 | 8.3 |
| FL | classic | LOW | classic | 15.4 | 3.7 |
| NJ | all-positive | HIGH | **classic** | 4.7 | 2.6 |
| IL | U-shaped | HIGH | **classic** | 30.8 | 2.6 |

## What the failure establishes

**The curve's shape is not determined by the task alone.** Same state, same people, same
label, same base rate — different protected attribute, different shape. The label-side
mechanism story, as sealed, is refuted by its own test, and the base-rate boundary of
document 54 loses its proposed mechanism along with its forward predictions.

**The misses are not noise; they all point the same way.** Every anomalous sex-arm shape
(U, all-positive) reverts to classic under race, and every race arm's effect dwarfs its
sex sibling's. What differs between the arms is the size of the disparity being corrected:
these states' sex gaps at the natural point run 0.07–0.12 and shrink toward the exclusion
floor across much of the sweep window, while their race gaps are far larger everywhere.

## The hypothesis this puts on the table — post-hoc, and treated as such

**The classic relationship is what the constraint does when it has a real gap to close;
the anomalous shapes are what the optimiser does when it does not.** One variable — gap
size — would then account for the week's entire anomaly collection: the U-shapes and
all-positive curves live on rich states' small sex gaps; the race arms' large gaps restore
classic behaviour with tenfold the signal; and the inverted 2022 arms sit exactly where
sex gaps had shrunk to the 0.04–0.06 floor. Document 45's finding — that sub-floor arms
poison correlations — would be the same phenomenon seen at arm level.

This unification was noticed in interim data, which is precisely how document 46 went
wrong, so it earns nothing here. Per the standing rule it gets its own seal, already
designed: the **2022 race arms** discriminate it against the vintage story directly (gap
story predicts classic, vintage story predicts inverted, on the same populations), with
the employment and coverage tasks carrying arms where the gap story and the old base-rate
story disagree.

## Bonus the campaign paid regardless

Six race arms, six classic crossings with strong signal — which means **six more located
crossovers** for the residual question that returned underpowered at three. A post-hoc
bracket pass over these arms is queued; if they bracket cleanly, the crossover-location
dataset roughly doubles.
