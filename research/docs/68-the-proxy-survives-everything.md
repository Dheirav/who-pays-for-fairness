# 68 — The proxy survives everything

**Individual work, beyond the course submission. Post-hoc analyses, labelled as such.**
The councils' last unfinished item (`analyse_zeta_extension.py`), 25 Aug.

The claim under test: the baseline selection rate operationalizes the theory's
untractable quantity (previously r = +0.935 on 26 arms, one probe, no interval).

| test | result |
|---|---|
| All 150 mappable populations, 3 seeds | rate 123/150, relaxed-ζ 120/150, agree 137/150; r(rate, sep) = **+0.850, CI [+0.813, +0.892]** |
| Sealed cohorts head-to-head (19 arms) | rate **18/19**, ζ 17/19, agree 18/19; r = +0.943 |
| Trim sensitivity (q = 0.025/0.05/0.10) | 24/26 at every trim; r = +0.930/+0.934/+0.940 |
| Second ν estimator (gradient-boosted probe) | identical 24/26; r = **+0.946** |

What it settles: the proxy relation is not an artifact of the 26 chosen arms, the 5/95
trim, or logistic misspecification; on the arms the sealed record actually scored, the
rate and the theory's relaxed ordering are near-interchangeable with the rate a nose
ahead. The statistician's and the rival theorist's shared demand is discharged, and
this table is the enclosure for any eventual letter to the theory's authors. One
denominator trap fired on the way (arms predating `n_test`) and the fix computes each
rate from its own fit.

With this, no compute item remains open anywhere in the project.
