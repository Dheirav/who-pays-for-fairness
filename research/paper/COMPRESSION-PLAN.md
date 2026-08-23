# Compression plan: Pass 1 manifest and Pass 2 rulings

Documentation only — no paper text changes in these passes. Pass 3 executes the rulings;
Pass 4 verifies every manifest entry still appears exactly once as a primary statement
(previews and pointers excepted); the raw extraction behind this file listed 169
number-bearing prose lines.

**Privileged locations** (allowed to restate facts without counting as duplication):
the abstract, the contributions list, and the surviving-claim box — their entire job is
summary. **Tables are primary homes by default** and are untouched in Pass 3.

## Part A — manifest of quantitative claims (grep-key → primary home)

### Core claim and sealed record
| claim | grep-key | primary home |
|---|---|---|
| 57 independent populations | `57 independent` | abstract + Setup (definition) |
| pool shrink 7.9–22.1% | `7.9--22.1` | §IV + tab:ablation |
| re-seal 9 of 10, constant 6 | `9 of 10` | §resealed + tab:resealed |
| seal 1: 4 of 8, bar 7 | `four of eight` | §sealed + tab:sealed + ledger |
| post-hoc 7 of 8; Maryland 0.508 | `seven of eight` | §sealed |
| doc46 arms +8.73/+6.85/+9.09 vs −16.48/−23.34/−23.32 | `+8.73` | §sealed (route paragraph) |
| sensitivity +0.905→+0.012 | `+0.012` | §sealed + tab:sensitivity |
| Minnesota miss 0.699, −0.04%, Colorado +0.63% | `0.699` | §resealed |
| Nebraska 0.014, −6.35% | `6.35` | §resealed |
| Taiwan sealed-aside, 0.885, +0.68% | `0.885` | §sealed |
| prior scorecard: 9/10 sealed, 5/10 post-hoc; FL 0.288 vs 0.284 | `5 of 10` | §crossover-history |
| ledger: 11 tests, bars and outcomes | (table) | tab:registered |

### Regime and theory
| claim | grep-key | primary home |
|---|---|---|
| r = −0.024 vs +0.585, 17 populations | `-0.024` | §Regime |
| 18/18 post-hoc + 9/9 pre-registered = 27/27 | `27 of 27` | §Regime |
| ζ ranges [−139, 4.1] vs [−39, 6662]; ν→0 | `6662` | §Regime |
| relaxed ordering 24/26 vs rate 25/26 | `24 of 26` | §Regime |

### Direction evidence
| claim | grep-key | primary home |
|---|---|---|
| single-factor r +0.801 (four arms, descriptive); 22↦1 at 0.03 vs 0.75 at 0.89 | `+0.801` | §V-A — *the +0.980 partial was deliberately removed per the council's Statistician (one degree of freedom); it survives in doc 23, not the paper* |
| HMDA purposes 0.555 −1.57% vs 0.871 +2.95%; r +0.803, ρ +0.900 | `0.871` | §V-B |
| two routes: 0.362–0.653 vs 0.353–0.637 (Oregon) | `0.362` | §V-C |
| dense sweeps +0.946/+0.905/+0.844; AL/KY bands 0.566/0.561 | `+0.946` | §V-C |
| domain table r's + Dutch gap 0.298, r +0.915 | `+0.915` | §V-D + tab:domains |
| within-pop ρ +0.96/+0.95/+0.78; pooled +0.487 vs +0.70 bar | `+0.487` | §Robustness |

### Who pays, subgroups, procedure
| claim | grep-key | primary home |
|---|---|---|
| rates split 0.50–0.58 vs people 0.66–0.74; cross-flow r +0.885 | `+0.885` | §IV-A + tab:whopays |
| exchange 2.68; HMDA +4.3% at 0.50; certs 0.018 vs 0.010 | `2.68` | §IV-A |
| sex 0.190→0.020; subgroup 0.315→0.178; 13.2×; r −0.671 | `13.2` | §VI + tab:intersectional |
| floor: 1.47→0.88, 19 arms, 16 below 1.0, r ≈ −0.99 | `1.47` | §Procedure |
| viable bands 0.895/0.859/≈0.51/0.056; LSAC 89% | `0.056` | §unusable (procedure refs it) |
| Connecticut r = −0.924 void example | `-0.924` | §Procedure |
| noise floor 2,500; COMPAS 1,584; LSAC 6,240 | `2{,}500` | §Small populations |

### Crossover history and campaigns
| claim | grep-key | primary home |
|---|---|---|
| crossovers 0.511/0.530/0.558/0.576 + intervals; FL 0.284 / OH 0.556 / PA 0.652 | (table) | tab:crossover |
| cluster 0.43–0.58 → span 0.28–0.65 | `0.28 to` | §crossover-history |
| residual seal: ρ≥0.70, floor 6, 3 located, underpowered; +0.724/+0.865/+0.947 | `underpowered` | §crossover-history + ledger |
| magnitude seal MAE 4.50 vs 0.77 | `4.50` | ledger |
| shape seal 4/6; race seal 2/6; 2022 inversion; 2019 acquittal | `2019--2022` | ledger + Limitations (vintage) |
| lottery: 0.65 / 0.135 keep, corr 0, 9/9 signature | `0.135` | §lottery |
| tail divergence rates 0.027–0.142, 15/15 clear bar | `0.142` | Limitations (primary, by design) |

### Setup constants
Row counts (45,222 / 5,278 / 20,798 / 60,420 / 30,000), ε = 0.01, exclusions 0.05 and
max(p,1−p), $50,000 knob, LSAC base rate 0.890, 55 checks / 28 doc-form — all single-homed
already; no action.

## Amendment after the verification re-pass (six caught gaps)

A mechanical audit-of-the-audit flagged 47 uncovered lines; most were adjacent-line
key placement or blanket-covered, and six were genuine manifest gaps, added here:

| claim | grep-key | primary home |
|---|---|---|
| ablation headline: parity 0.186 → 0.015 under two accuracy points | `0.015` | §IV + tab:ablation |
| pre-registered instrument alternative, bar \|r\| < 0.30, loses both | `< 0.30` | §V-D |
| HMDA held-out residue: r ≥ +0.80 all four, +0.995 refinance | `+0.995` | ledger residue sentence |
| EO residue: +0.644 two states, +0.822 Alabama alone | `+0.822` | ledger residue sentence |
| withdrawn results: +0.979 / +0.968 void; exclusion rescued lending | `+0.979` | ledger residue sentences |
| derivation: cleared bars, beaten 12 correct against 13 of 14 | `against 13` | derivation paragraph |
| post-processing arithmetic artifact, exchange rate 0.000 | `0.000` | ledger residue sentence |

Also two robustness fixes to the checking itself:
* **Spelling variants**: the abstract writes `7.9--22.1` while §IV writes `7.9\% to
  22.1\%`; Pass 4 must grep both spellings for range claims (added keys: `to 22.1`,
  `0.66 and 0.74`, `0.018`, `22 decisions`, `0.178`).
* **A missed duplication for Part B's small-dedups list**: the Dutch gap 0.298 appears in
  both Setup ("carries a between-group gap of 0.298") and §V-D (where it does its
  argumentative work). Home: §V-D; Setup's sentence trims to the qualitative "roughly
  twice Adult's".

## Part B — Pass 3 rulings (the cuts)

1. **§"Method, and What We Got Wrong" (lines ~853–958) largely dissolves into the ledger.**
   - HMDA held-out episode → delete prose; unique residue (r ≥ +0.80 throughout, +0.995
     refinance, three estimates agree) becomes one sentence after the ledger.
   - EO episode → delete prose; unique residue (+0.644 two states, +0.822 Alabama-alone)
     one sentence.
   - Withdrawn results episode → keep as two sentences (unique: +0.979/+0.968 void, the
     exclusion rescuing lending).
   - Derivation episode → **keep intact** (unique content: 12 v. 13, why no mechanism) but
     relocated beside the ledger.
   - Post-processing-arithmetic episode (exchange 0.000) → keep, one sentence.
   - The surviving-claim box → **keep verbatim** (privileged).
   - Section header disappears; ledger + residue + box move into §Boundaries tail.
   - Estimated saving: ~0.6 pp.
2. **§sealed narrative compresses around its table** (~0.4 pp): the story told once —
   bar, outcome, refinement lesson, route paragraph — with tab:sealed and tab:resealed
   merged into a two-panel table sharing one caption. Taiwan clause stays. Sensitivity
   table stays (unique numbers) with two-sentence framing.
3. **Limitations become pointers** (~0.3 pp): sealed-record item → 3 sentences + refs;
   crossover item → 2 sentences + ref; regime item → 1 sentence + ref. The vintage item
   and the tail-divergence item are primary homes and stay full.
4. **Intersectional section tightens by a third** (~0.2 pp): measurement-hazard paragraph
   compresses to two sentences; replication sentence keeps 13.2× and r = −0.671.
5. **Small dedups**: LSAC 0.056 stated once (§unusable), procedure line references it;
   `24 of 26` disappears from the derivation episode (Regime is home); crossover-history's
   re-seal recap keeps only the prior-scorecard framing (9/10 vs 5/10), dropping clauses
   that restate §resealed.

**Not cut, ever:** any table row, any ledger row, any number lacking a second home, the
surviving-claim box, the vintage caveat, the abstract (venue-pending), citations.

Expected outcome: ~9 pages ± a quarter, all 169 manifest lines accounted for.
