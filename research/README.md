# Research — individual work beyond the course submission

**Everything in this folder is work done by Dheirav alone, after the course
deliverable was complete.** It is not part of the team submission and no part of it is
required by the course specification.

The course deliverable is `bias_mitigation_report.pdf`, `bias_mitigation_plan.pptx`, and
[`docs/01`–`docs/10`](../docs/README.md). Those cover UCI Adult only and are complete on
their own terms. Nothing here is needed to read or assess them.

## The boundary, and how to verify it

The deliverables were finalised at commit `28bc8d1` (11 Aug, 23:49). **Every commit after
that point is this folder's work**, and each states what it did and why:

| commit | |
|---|---|
| `d182ef3` | ACS Income loader; every experiment made dataset-parameterised |
| `f8dda3a`, `227583c` | result-overwrite guards and `results_io` |
| `339a4ff`, `19ed0c8` | replication across ten populations |
| `8eff189` | protected attribute made selectable and part of the dataset identity |
| `34a4638` | cross-flow made reproducible; the confound quantified |
| `2c7f312` | intersectional replication |
| `6df9d45`, `2168d09` | pre-registered two-arm analysis |
| `55368f5` | the retraction |

Git history is the authoritative record of authorship here, not directory layout —
which matters because one part of this work **cannot** be moved into this folder.

## What could not be separated

These modules are individual work but live in `src/`, because they are inside the Python
package and moving them would break imports:

| file | |
|---|---|
| `src/datasets/acs.py` | ACS Income loader, both protected-attribute arms |
| `src/experiments/analyse_sweep.py` | P1/P2/P3 across populations |
| `src/experiments/analyse_arms.py` | the pre-registered two-arm analysis |
| `src/experiments/analyse_conflict.py` | the pre-registered DP/EO conflict analysis |

They cannot be **moved** here, but they are **excluded from the submission bundle**:
`datasets.build` imports the ACS loader lazily, inside the branch that requests it, so
the course code neither imports nor needs any of them. `scripts/build_submission.py`
drops all four, and the resulting bundle was unpacked and its suites run to confirm it
stands alone.

Three shared files were also extended for this work — `src/results_io.py`,
`src/datasets/base.py`, `src/datasets/__init__.py` — and those changes improved the
course-side code as a side effect. They are not claimed as exclusively individual.

## The documents

| # | Document | What it answers |
|---|---|---|
| 11 | [Replication across populations](docs/11-replication-across-populations.md) | Which findings are about the method, and which about Adult? |
| 12 | [Intersectional across populations](docs/12-intersectional-across-populations.md) | Gerrymandering replicates, and is worse than Adult showed |
| 13 | [Separating ratio from size](docs/13-separating-ratio-from-size.md) | A second protected attribute breaks a confound, and retracts document 11's correction |
| 14 | [Why the conflict is unpredictable](docs/14-why-the-conflict-is-unpredictable.md) | P2's magnitude resisted prediction because the endpoint is independent of the starting point |
| 15 | [Arbitrariness at small scale](docs/15-arbitrariness-at-small-scale.md) | On small populations the method's own randomness exceeds the entire effect of the constraint |
| 16 | [Planting a proxy](docs/16-planting-a-proxy.md) | The intervention refutes document 06's mechanism: a planted proxy is used *less*, not more |

## The short version

Documents 01–10 are all measurements on one dataset. Ding et al. (2021), *Retiring
Adult*, argues the field should stop drawing conclusions from exactly that dataset.
Until a finding survives a population it was not derived from, "the constraint causes X"
and "Adult has property X" are indistinguishable.

**Document 11** stated three predictions in advance and tested them on nine US states.
One held cleanly (proxy relocation needs a proxy worth relocating onto — Adult leaks sex
at 0.9364 against 0.76–0.84 everywhere else, no overlap). One held only under a condition
that had to be discovered. One did not hold at all.

**Document 12** replicates the intersectional result and finds it *stronger* elsewhere:
the fairness gerrymandering Adult showed at 9.0× reaches 13.2× in Mississippi. It gains
one condition — the effect needs a substantial minority to hide in. Below 12% minority a
sex constraint removes 85% of the intersectional gap; at or above it, 22%. That is the
first relationship in the project whose two candidate explanations are not confounded
with each other.

**Document 13** builds a second protected attribute for the sole purpose of breaking a
confound document 11 could not escape, with the analysis written and committed *before
the data existed*. It returned a result its author predicted wrongly, and the outcome is
a retraction: document 11's tentative first reading was right and its confident
correction was wrong.

## What this does not change

**Nothing in documents 01–10 is retracted.** The Adult measurements were correct and have
been re-verified. Two claims *added after* those documents were written have been scoped
or withdrawn, and both retractions are recorded in place rather than edited away.

The course deliverables are unaffected, and this was checked rather than assumed: the
formula that failed appears in neither the report nor the deck, and their who-pays
section is explicitly scoped to Adult ("the privileged group *here* is 2.1× larger").
Where the replication touches a deliverable claim at all, it strengthens it — the
"Black men become the residual" finding now replicates independently in Mississippi and
Alabama, and the report's reliability warning turns out to be understated rather than
overstated.

## Replication note for document 05

[Document 05](../docs/05-who-pays.md) reports that the burden of the fairness fix looks
near-even in *rates* and lopsided in *people*. That measurement is Adult, and it stands.

The **generalisation** of it — that the rate-to-people conversion is pure population
arithmetic — was claimed after that document was written and does not survive as stated.
It holds when the mitigation performs a **clean transfer**: privileged lose, unprivileged
gain, nobody moving the other way. Adult's cross-flow share is 0.045 and the conversion
predicts it to within 0.014; on populations under ~10,000 rows cross-flow reaches 0.3–0.4
and the error grows fivefold.

The diagnostic is the cross-flow share,
`(priv_gained + unpriv_lost) / (priv_lost + unpriv_gained)`, which correlates with the
conversion's error at **r = +0.885** across nineteen populations. Both group inequality
and small samples raise it, independently — see
[document 13](docs/13-separating-ratio-from-size.md).

This note lives here rather than in `docs/05` so the course-side documents contain only
work within the course scope.
