# 64 — The conventions hold their shape

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**
The fourth council economist's three compute items (`analyse_survey_design.py`), 25 Aug.

## 1. Design weights move the locations, not the ordering (`--weighted`)

Models fitted unweighted (the declared convention); every arm's evaluation read both
ways. Every bracket shifts **down** in design-weighted rate units, materially:

| state | unweighted bracket | weighted bracket |
|---|---|---|
| SC | 0.530–0.570 | 0.483–0.523 |
| OR | 0.550–0.590 | 0.514–0.555 |
| OH | 0.550–0.590 | 0.523–0.564 |
| PA | 0.600–0.640 | 0.583–0.623 |
| FL | 0.240–0.280 | **0.159–0.192** |

FL and PA remain the outliers — the located span *widens* under weighting (0.16–0.62).
So: the ordering and the cluster-breaking are weighting-robust; the numeric crossover
locations, including the 0.54 prior, are properties of the unweighted convention. For
the audit this is benign (a deployer's own pool needs no design weights); for
transported numbers the paper now says which convention each belongs to.

## 2. Household clustering widens the intervals, modestly (`--clustered`)

The doc-61 nested bootstrap rerun with the inner resample over SERIALNO households:
SC 0.470–0.587 (vs person-level 0.454–0.537), OR 0.491–0.584 (vs 0.514–0.604);
no-crossing 2–3%. The published person-level intervals understate sex-arm uncertainty
as the economist predicted, without dislodging any location.

## 3. Allocation acquitted as the 2022 mechanism (`--allocation`)

Hot-deck imputed income shares rose into 2022 (OH 0.234 → 0.277; AL/SC/NV ≈ 0.32).
Excluding flagged rows lifts base rates ≈ +0.03 **uniformly** — both vintages, both
labels (OH-2018 0.340→0.364; OH-2022@50k 0.416→0.445) — with sex gaps stable
(+0.005–0.014) and both Ohio model arms keeping their sign (2018: −2.10; 2022@60k:
−0.98). A level effect present everywhere is not a differential 2022 mechanism: the
quantile story of documents 57/62 stands, and the fourth candidate is acquitted like
the first two.

With this, the economist's major-revision list is discharged except what waits on
IPUMS; the anchoring critique already landed as document 62.
