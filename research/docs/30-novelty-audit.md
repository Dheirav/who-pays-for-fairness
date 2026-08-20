# 30 — Novelty audit: what is actually new, claim by claim

**Individual work, beyond the course submission.** Written because three claims in this
project had already turned out to be anticipated, each found by chance rather than by
looking, and an ad-hoc search is not evidence of absence.

## Method, so the coverage can be judged

1. **Citation graph.** Pulled every paper citing the three closest works — Mittelstadt et
   al. (2023), *Fairness May Backfire* (2026) and Goethals et al. (2024) — from Semantic
   Scholar. **72 unique citing papers.**
2. **Screened all 72** by title and abstract against four signal categories: conditionality
   language, rate/prevalence vocabulary, levelling-up/down vocabulary, and empirical
   vocabulary. Five scored three or more categories and were read.
3. **Full text read** for five papers: Mittelstadt (49pp), Backfire (15pp), FRAME,
   *Fair Without Leveling Down*, and Goethals.
4. **Roughly a dozen targeted searches**, deliberately varying vocabulary — selection rate,
   acceptance rate, base rate, prevalence, budget, capacity — because the field does not use
   one term for this quantity.

**What this does not cover.** Semantic Scholar's citation index lags, particularly for very
recent work; *Backfire* itself has zero recorded citations and is five months old. Anything
published in the last few months that does not yet cite these three papers would be missed.
The audit is a serious sweep, not a guarantee.

## The verdict, claim by claim

| # | claim | status |
|---|---|---|
| A | Fairness constraints level down | **Established.** Mittelstadt 2023; Zietlow 2022 (vision); Maheshwari 2023 |
| B | The certifying metric hides it | **Established.** Maheshwari 2023: levelling down "goes unnoticed in the overall performance"; FRAME 2023 |
| C | Who-pays / incidence decomposition (doc 05) | **Substantially anticipated.** FRAME's first three dimensions are impact size, change direction, and effect on acceptance rates |
| D | The direction is conditional and can reverse | **Anticipated**, theoretically. *Backfire* 2026, attribute-blind regime |
| **E** | **The selection rate predicts the direction, with a crossover, measured** | **Not found.** See below |
| **F** | ***Backfire*'s conditions hold on 0 of 26 real populations** | **Not found**, and zero papers cite that work |
| **G** | **The selection rate proxies their structural quantity, r = +0.935** | **Not found** |
| H | The remedy: a selection-rate floor | **Anticipated.** Mittelstadt §6, minimum rate constraints |
| I | The remedy's benefit scales with the damage (r ≈ −0.99) and is inert otherwise | Not found |
| J | Intersectional subgroups left behind, empirically | **Largely anticipated.** Kearns et al. empirical study across four datasets; Maheshwari 2023 |
| K | Below ~2,500 subjects, method randomness exceeds the constraint | **Anticipated.** Cooper/Barocas 2023; FRAME. The specific threshold may be ours |
| L | Attribution audits move an order of magnitude without behaviour changing | Not found |
| M | The *optimal* DP classifier levels down too | Not found |
| N | Minimax group fairness levels down worse than the constraint it replaces | Not found |
| O | The identity: the pool is preserved exactly when λ = p | Not found |
| P | Deployed domains straddle the crossover (0.02 hiring to 0.84 mortgages) | Not found as an argument |

## On the headline claim specifically

**E is the paper.** It survived:

* every one of the 72 papers citing the three closest works;
* full-text search of Mittelstadt (**zero occurrences of "base rate"**), *Backfire* (**zero
  occurrences of "base rate" or "prevalence"**, and zero experiments), FRAME (**zero
  occurrences of "selection rate" or "base rate"**), and *Fair Without Leveling Down*
  (**zero of either**);
* Goethals et al., who study the same axis, call it "a factor overlooked in previous
  evaluations", and cannot observe the direction because their setup fixes the pool as a
  budget;
* about a dozen searches across six different vocabularies for the same quantity.

The nearest thing found in a different direction is Bello et al.'s subgroup-separability
work, which identifies a *different* property of the data as predictive of bias — the same
shape of contribution, on another quantity, and worth citing as related.

## What must change in the write-up

* **Document 05's incidence decomposition must cite FRAME.** Impact size, change direction
  and decision rates are its dimensions D1–D3, published February 2023. Ours adds the
  exchange rate and the rate-versus-people contrast; the decomposition itself is not new.
* **Claim (ii) must cite Maheshwari et al. as well as Kearns.** They report levelling down
  being worse under intersectional fairness and going unnoticed, which is adjacent to both
  our claim (ii) and our central thesis.
* **The thesis sentence — "the metric reports the same success either way" — is not novel**
  and should be presented as the organising frame rather than as a finding. Maheshwari says
  it for intersectional fairness; FRAME says it for individual impact.

## What survives, stated plainly

The paper is: **a theory published in March 2026 says the direction can go either way; we
show which way it goes, when, from a quantity computable in advance, on 26 populations —
and that the theory's own conditions are satisfied by none of them.**

Everything else in this project is supporting material, replication, or negative results,
and should be presented as such.
