# Citation and claim verification, 27 Aug

Prompted by an external reviewer finding `ferry2023` wrong. Every reference checked against
a primary or publisher record; every claim the paper makes *about* a source checked against
that source's text. Nothing here was verified from memory.

## References — 20 of 20

| key | verdict |
|---|---|
| `agarwal2018` | ✓ ICML 2018, PMLR v80 60–69 |
| `mittelstadt2023` | **fixed** — journal is Mich. Tech. L. Rev. **vol. 30, no. 1, 2024**; 2023 is the preprint |
| `ferry2023` | **fixed** — arXiv 2302.07185 is **Krco, Laugel, Grari, Loubes, Detyniecki**, subtitle *multiplicity and arbitrariness*; not Ferry et al. |
| `maheshwari2023` | ✓ EMNLP 2023 |
| `backfire2026` | ✓ Yang, Chang, Chen |
| `kearns2018` | ✓ ICML 2018, PMLR v80 2564–2572 |
| `ding2021` | ✓ NeurIPS 2021, 6478–6490 |
| `goethals2024` | ✓ arXiv 2406.01290 |
| `propublica2016` | ✓ Angwin, Larson, Mattu, Kirchner, 2016 |
| `corbett2017` | ✓ KDD 2017, 797–806 |
| `diana2021` | ✓ AIES 2021, 66–76 |
| `long2023` | ✓ NeurIPS 2023 |
| `agarwal2022` | ✓ FAccT 2022 |
| `cotter2019` | ✓ NeurIPS 2019 — order *Cotter, Gupta, Narasimhan*, per the proceedings |
| `grgic2017` | ✓ arXiv 1706.10208 |
| `black2022` | ✓ FAccT 2022 |
| `barocas2016` | ✓ Cal. L. Rev. 104(3) 671–732 |
| `ricci2009` | ✓ 557 U.S. 557 (2009) |
| `broome1990` | **fixed** — pages **87–102**, not 87–101 |
| `stone2011` | ✓ OUP 2011 |

## Quotations — all verbatim, one fixed

Mittelstadt's minimum-rate-constraint sentence; Maheshwari's "often goes unnoticed in the
overall performance of the model"; Ding's $50,000-threshold sentence; both of the theory
paper's regime statements, where our ellipsis correctly marks the omitted clause.

**Fixed:** Goethals wrote "a factor overlooked in **prior** evaluations"; we had "previous".

## Negative claim — holds

Ding et al. contain **zero** occurrences of "selection rate", "acceptance rate",
"leveling down" or "levelling down". Checked against the extracted text.

## Characterisations — all accurate

| source | our claim | source's own words |
|---|---|---|
| `backfire2026` | Theorem 3 states conditions over the extrema of ζ(x) = (η(x)−c)/ν(x); sufficient not necessary | ζ defined exactly so, with A/B the sup and inf where ν is positive and negative; conditions are implications |
| `corbett2017` | optimal constrained classifier is group-specific risk thresholds | "the optimal algorithms that result require detaining defendants above race-specific risk thresholds" |
| `kearns2018` | marginal constraints satisfiable while subgroups badly treated | "fair on each individual group, but badly violates the fairness constraint on structured subgroups" |
| `diana2021` | minimises the worst group's error rather than equalising | "minimizing the maximum loss across all groups rather than equalizing group losses" |
| `long2023` | fairness interventions exacerbate predictive multiplicity | "fairness interventions… can exacerbate predictive multiplicity" |
| `goethals2024` | positive decisions are a fixed resource, total constant by construction | "we formalize the notion of resources, as the proportion of instances predicted as positive" |
| `agarwal2022` | aware-regime optimum randomises at group-specific boundaries | characterises it as a group-dependent threshold classifier; the threshold *form* is Hardt / Corbett-Davies / Menon–Williamson, which the paper cites separately — the division is correct |
| `cotter2019` | the standard derandomization remedy | "how well a stochastic classifier can be approximated by a deterministic one" |
| `grgic2017` | randomness advocated as a fairness device | proposes ensembles of random classifiers |
| `broome1990` | claims-based; a lottery among equal claims can be what fairness requires | fairness requires claims satisfied in proportion to strength, with weighted lotteries the surrogate for indivisible goods |
| `ricci2009` | per-group thresholds face direct disparate-treatment exposure | race-conscious action to avoid disparate impact is itself subject to disparate-treatment claims |

## One imprecision left standing, deliberately

`stone2011` is cited jointly with `broome1990` for "a lottery among relevantly equal claims
can be exactly what fairness requires". That is exactly Broome. Stone's argument is
different in mechanism — lotteries exclude bad reasons rather than give surrogate
satisfaction to claims — so the joint citation is right about the literature and loose
about Stone. Not worth a fix; worth knowing if a philosopher reviews it.

## Rate

**Four errors in twenty entries**, all found only because they were checked. None would have
been caught by a build, a test, or a reading.
