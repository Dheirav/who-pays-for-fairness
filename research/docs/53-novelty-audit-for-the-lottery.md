# 53 — Novelty audit for the lottery finding, and where it sits in the literature

**Individual work, beyond the course submission.** Document 30's audit predates
[document 51](51-the-cut-is-a-lottery.md), so the lottery claim had never been checked for
priority. This is that check: targeted web and arXiv searches over the vocabularies the
field uses (randomized fair classification, stochastic classifier derandomization,
predictive multiplicity, levelling down + arbitrariness, Fairlearn mixture behaviour),
with every near-hit read at abstract level and the two serious ones read in full. It is an
evening's sweep, lighter than document 30's citation-graph pass, and is labelled
accordingly.

## The claim being audited

On deep-tail cut arms, the fitted attribute-blind mitigation degenerates into a **uniform
lottery over predicted positives** — one flat keep-probability, correlation with the score
exactly zero — while lift arms remain graded tilts; the granted-below-line signature
separates the two 9 of 9; and therefore a parity certificate can be earned by random
discard.

## What is already known, and how each differs

| prior work | what it establishes | how the lottery claim differs |
|---|---|---|
| Agarwal & Deshpande, FAccT 2022 (*On the Power of Randomization in Fair Classification*) | Theory, **group-aware**: the optimal randomized fair classifier is a **randomized threshold classifier** — randomization concentrated at score boundaries | Opposite structure, opposite regime: we observe a fitted **attribute-blind** mitigation randomizing **globally and flat**, not at the boundary. The contrast strengthens the finding: what the practical optimiser returns on cut arms is far from the theory's optimal randomization structure |
| Cotter, Gupta & Narasimhan, NeurIPS 2019 (*On Making Stochastic Classifiers Deterministic*) | Stochastic classifiers from constrained optimisation are practically problematic; derandomization methods | The *concern* that fair classifiers randomize is prior art; the measured degeneracy into a flat lottery, and its confinement to cut arms, is not there |
| Long, Hsu, Alghamdi & Calmon, NeurIPS 2023 (*Individual Arbitrariness and Group Fairness*) | Fairness interventions worsen **predictive multiplicity across competing models/seeds**, and the harm is "masked by favorable group fairness and accuracy metrics" | Closest in spirit, different phenomenon: theirs is arbitrariness **between** retrained models; ours is deliberate randomization **inside one** fitted model's returned solution. Their masking framing anticipates half of our normative point and must be cited |
| Mittelstadt et al. 2023 | Levelling down "unnecessarily and arbitrarily harms" — arbitrariness as a normative charge | The charge exists rhetorically; the measurement that the harm literally *is* a uniform random draw does not |
| Agarwal et al. 2018; Fairlearn docs | ExpGrad returns a randomized mixture by design | The machinery, credited since document 11; no observation of degeneracy |

## Not found anywhere searched

* Any empirical report of a fitted fairness mitigation behaving as a **flat lottery over
  positives** (uniform keep-probability, zero score correlation) on real data.
* The **graded-tilt versus lottery dichotomy**, or any per-arm signature separating
  levelling direction from the mixture's probability profile.
* Any connection between mixture degeneracy and **which way the pool moves**.

Searches also turned up nothing in the Fairlearn issue tracker or documentation warning
that the mixture can collapse to original-versus-reject-everyone.

## What document 51 and the paper must now do

1. **Cite Long et al. 2023** wherever the lottery's normative point is made, delineating
   across-model multiplicity from within-model randomization — and the paper's
   small-populations section, which already cites Black et al. 2022 on multiplicity,
   gains the same citation.
2. **Cite Agarwal & Deshpande 2022** for the optimal structure, and state the contrast:
   theory's optimum randomizes at the boundary; the fitted reduction on cut arms
   randomizes globally, which is precisely why calling it a lottery is fair.
3. **Cite Cotter et al. 2019** if the finding is ever offered with a remedy attached, since
   derandomization is the existing tool a practitioner would reach for — noting that
   derandomizing a flat lottery amounts to re-choosing a threshold, which un-does the
   parity it bought.

## Verdict

**Probably ours, upgraded to: ours with three fences to build.** The specific observation,
the signature, and the direction connection appear nowhere searched; the neighbourhood is
occupied by across-model multiplicity, boundary-randomization theory, and derandomization
practice, each of which the write-up must cite and delineate. The residual risk is the
audit's own coverage — an evening against document 30's fuller sweep — and a
citation-graph pass over Long et al. and Agarwal & Deshpande's citers is the cheap
tightening if the lottery is promoted into the paper.

## Addendum, next day — the citation-graph pass, and the verdict holds

The pass document 30 would demand was run: **every citing paper of all three anchors
pulled from Semantic Scholar and screened by title and abstract** — Long et al. (15
citers), Agarwal & Deshpande (6), Cotter et al. (24) — plus the citers of a fourth anchor
found by a widened arXiv keyword pass, Grgić-Hlača et al. 2017 (44 citers), and ten
arXiv API queries under deliberately varied vocabulary ("randomized rejection", "random
tie-breaking", "uniform lottery", "randomly discard", "keep probability", and others).
Eighty-nine citing papers screened in all; one cleared at abstract level (ensemble
fairness composition, 2022 — fairness *of* ordinary ensembles, not degeneracy of
fairness-constrained mixtures); none observes the lottery, the signature, or the
direction connection.

The widened pass added a **fourth fence**: Grgić-Hlača et al. 2017 *advocate* randomized
classifier ensembles as a deliberate fairness device. That is the mirror of our finding —
designed randomness as a virtue versus randomness *emerging* as the degenerate way to buy
a certificate — and the write-up should engage it directly: the indictment is not
randomness per se, but uninformative randomness standing in for a measured closing of the
gap.

**Verdict as it now stands: ours, at citation-graph confidence, with four fences.** The
remaining risk is the irreducible kind — venue-only publications, non-English work,
vocabulary none of fourteen queries reached — which is the same residual document 30
accepted.
