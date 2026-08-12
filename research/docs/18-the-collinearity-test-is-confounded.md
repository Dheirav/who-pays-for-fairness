# 18 — The third test is inconclusive, and why

**Individual work, beyond the course submission.** Tests the collinearity candidate from
[document 17](17-neither-explanation-survives.md). **The manipulation check failed, so
this is inconclusive rather than negative** — and the reason it failed is the interesting
part.

## The hypothesis

Documents 16 and 17 refuted two explanations for document 06's +151% attribution shift.
Document 17 recorded a third with its premise measured and explicitly not claimed:
attribution moved between Adult's two most redundant features (`relationship` ↔
`marital-status`, Cramér's V 0.487, against 0.217 for the next closest pair). Shapley
values divide credit between collinear features, and small weight changes can reallocate
that credit without the model's behaviour changing at all.

Adult's signature: the pair moves **0.183** in total magnitude while its combined share
moves only **0.045** — a ratio of about 4.

## The design, and the check that stopped it

Two columns planted, each indicating the label at probability 0.8; B copies A with
probability *redundancy* and is otherwise drawn independently. Alabama, three seeds.

The redundancy knob worked, and per-column informativeness held flat — V(column, label)
stayed at 0.386–0.394 throughout. But **K0 failed on its second half**:

| redundancy | V(A,B) | pair's combined share | swap | baseline accuracy |
|---|---|---|---|---|
| 0.0 | 0.106 | **0.376** | 0.0316 | 0.8501 |
| 0.5 | 0.537 | **0.265** | 0.0302 | 0.8329 |
| 1.0 | 1.000 | **0.198** | 0.0187 | 0.8215 |

The pair's total attribution share falls **47%** as redundancy rises, and baseline
accuracy falls with it. K3 failed for the same reason — behaviour did change, because the
model got worse.

## Why this is not a fixable bug

Each column is individually just as informative at every setting. The **pair** is not.
Two redundant columns carry less *joint* information than two independent ones, so the
model uses them less and fits worse. That is not an implementation error; it is what
redundancy means.

Which makes the confound structural:

> Hold each column's marginal informativeness fixed and raise redundancy, and the pair's
> joint informativeness necessarily falls. Hold the pair's joint informativeness fixed and
> raise redundancy, and each column's marginal informativeness must rise. **Both cannot be
> held at once.**

So `swap` falling from 0.0316 to 0.0187 is uninterpretable: it is exactly what you would
see if the pair were simply used less, which it was. Reporting that as "the third
explanation is refuted" would be claiming a result the design cannot deliver.

## What can be said, weakly

Normalising the swap by how much the pair is used at all removes the confound's most
obvious component:

| redundancy | swap ÷ pair share |
|---|---|
| 0.0 | 0.0842 |
| 0.5 | 0.1140 |
| 1.0 | 0.0943 |

No trend — up, then down, spanning a range comparable to the seed-to-seed spread. **K2
held**: what movement there is stays a swap rather than a net gain (0.0187 swap against
0.0180 net at full redundancy).

This is weak evidence *against* the collinearity hypothesis, and it is offered as weak.
Normalisation is a post-hoc adjustment chosen after seeing the confound, which is exactly
the move [document 13](13-separating-ratio-from-size.md) records going wrong, so it is
reported as a diagnostic rather than a verdict.

## What a valid test would require

Calibrate the per-column outcome strength *per redundancy level* so the pair's combined
attribution share is constant across settings, then vary redundancy. That holds the thing
the confound moves and isolates the thing the hypothesis is about. It needs a calibration
loop over trial fits before the real runs, which is a larger experiment than the three
already done here.

## Where this leaves document 06

Unchanged from [document 17](17-neither-explanation-survives.md): the +151% is real,
reproducible, and **unexplained**.

| candidate | status |
|---|---|
| reconstruction-seeking (document 06) | **Refuted** by intervention (document 16) |
| outcome-signal-seeking (document 16) | **Refuted** by intervention (document 17) |
| collinear reallocation (document 17) | **Untested.** The design was confounded; weak evidence against, no verdict |

Two refuted, one that resisted a clean test. The honest tally is that this project can say
what does *not* explain the shift, and cannot say what does.

## What still stands, unaffected

Document 17's positive finding is untouched by any of this and is the more useful result:
across six cells the constrained model's attribution tracked the unconstrained model's to
within 0.03 share while the share itself moved ninefold. **The demographic parity
constraint does not systematically change which features the model leans on.** The
question of why Adult's particular pair swapped is a question about SHAP on one dataset;
that finding is about the method.
