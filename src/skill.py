"""Forecast skill against a named baseline: the single definition of every scoring quantity.

**Individual work, beyond the course submission.**

Why this file exists
--------------------
The project's standing rule says a sealed prediction must name the naive baseline it has to
beat, not just the threshold it has to clear. That rule came from
[document 26](../research/docs/26-the-derivation-does-not-earn-its-keep.md), where a derived
rule cleared its pre-registered bar of 0.75 at 12/14 and was then beaten by a constant at
13/14. A significance test would have certified that result at p = 0.0065 against a
coin-flip null: significant, and worthless, because the alternative anyone would actually
have used did better.

Naming the baseline fixed that. It left a second gap, which this file closes.

**A bar reports a verdict and refuses to report a margin.** The re-seal scored 9 of 10
against a best constant of 6 and its bar said HOLDS, while the paired sign test on the same
outcome gives p ~ 0.19 — the two live in different sections and only one of them makes it
into a summary. Worse, a sharp count threshold does to a ten-arm cohort exactly what p<0.05
does to a small sample: Minnesota and Iowa are statistically indistinguishable (both near
zero, both splitting 3 of 5 across seeds) and the rubric scored one against the rule and one
for it. That is not a rubric bug to be patched with a further threshold; it is what any
sharp threshold does at this n.

So: keep the pre-registered baseline, and report the **skill margin with an interval on it**
instead of a pass/fail count. ``+3 arms, 95% CI [lo, hi]`` says what ``9 of 10, HOLDS`` says,
plus how fragile it is, and a one-arm swap moves the estimate rather than flipping a verdict.

What is legitimate to compute retrospectively, and what is not
--------------------------------------------------------------
``score()`` re-expresses an outcome that has already been scored under its own sealed rubric.
It introduces no new prediction and changes no verdict — the sealed counts stand as sealed,
and this is reported beside them, never instead of them.

``brier_skill()`` is **for future seals only**. Scoring an old cohort with probabilities
invented now would be fitting a confidence to a known outcome, which is the post-hoc move
this project forbids. A seal that wants the Brier route must commit its per-arm probabilities
in the sealed analyser, before the arms exist.

Run:  python -m src.experiments.analyse_skill
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, isnan
from typing import Sequence

import numpy as np

# Bootstrap resamples for the margin interval. Fixed so the interval is reproducible.
N_BOOT = 20_000
SEED = 0


@dataclass(frozen=True)
class Skill:
    """One cohort's skill against its best constant, with the interval that a count hides."""

    n: int
    correct: int
    constant_label: str
    constant_correct: int
    margin: int
    lo: float
    hi: float
    conf: float
    discordant: int
    rule_wins: int
    sign_p: float

    def line(self) -> str:
        return (f"{self.correct}/{self.n} vs constant {self.constant_correct}/{self.n}  "
                f"margin {self.margin:+d} arms, {self.conf:.0%} CI "
                f"[{self.lo:+.1f}, {self.hi:+.1f}]  "
                f"paired sign test p = {self.sign_p:.3f} "
                f"({self.rule_wins}/{self.discordant} discordant)")


def best_constant(actual: Sequence[str]) -> tuple[str, int]:
    """The baseline the rule has to beat: always predict whichever sign is commoner.

    Ties resolve to the alphabetically first label so the choice never depends on row order.
    """
    labels = sorted(set(actual))
    scores = {lab: sum(a == lab for a in actual) for lab in labels}
    best = max(scores.values())
    return next(lab for lab in labels if scores[lab] == best), best


def skill_margin(predicted: Sequence[str], actual: Sequence[str]) -> int:
    """Arms the rule gets right, minus arms the best constant gets right."""
    correct = sum(p == a for p, a in zip(predicted, actual))
    return correct - best_constant(actual)[1]


def margin_interval(predicted: Sequence[str], actual: Sequence[str], *,
                    conf: float = 0.95, n_boot: int = N_BOOT, seed: int = SEED,
                    refit_constant: bool = True) -> tuple[float, float]:
    """Percentile bootstrap interval on the skill margin, resampling *arms*.

    ``refit_constant`` re-derives the best constant inside each resample, which is the
    honest comparator: the baseline is a procedure a reader would apply to whatever data
    they saw, not a label fixed by the outcome we happened to observe. Holding the label
    fixed instead lets resamples that flip the majority sign score the rule against a
    baseline nobody would have chosen there, which inflates the *upper* end of the margin
    — on the re-seal, +7 rather than +5 — so it is flattering, and it is not the default.

    At n = 10 the resampled margin takes few distinct values; the interval is coarse by
    construction and should be read as such rather than as a smooth confidence bound.
    """
    pred = np.asarray(predicted, dtype=object)
    act = np.asarray(actual, dtype=object)
    n = len(act)
    if n == 0:
        return (float("nan"), float("nan"))
    fixed_label = best_constant(actual)[0]
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    margins = np.empty(n_boot)
    labels = sorted(set(act))
    for b in range(n_boot):
        take = idx[b]
        a_b, p_b = act[take], pred[take]
        correct_b = int(np.sum(p_b == a_b))
        if refit_constant:
            const_b = max(int(np.sum(a_b == lab)) for lab in labels)
        else:
            const_b = int(np.sum(a_b == fixed_label))
        margins[b] = correct_b - const_b
    tail = (1.0 - conf) / 2.0
    return (float(np.quantile(margins, tail)), float(np.quantile(margins, 1.0 - tail)))


def sign_test(predicted: Sequence[str], actual: Sequence[str]) -> tuple[int, int, float]:
    """Paired comparison against the constant, on the arms where the two disagree.

    Returns (discordant, rule_wins, one-sided exact p). Arms where the rule and the constant
    say the same thing carry no information about which is better, so they are dropped —
    which is why this is stricter than counting all n, and why the re-seal's 0.046 becomes
    0.19 here.
    """
    label = best_constant(actual)[0]
    pairs = [(p, a) for p, a in zip(predicted, actual) if p != label]
    d = len(pairs)
    if d == 0:
        return (0, 0, float("nan"))
    wins = sum(p == a for p, a in pairs)
    p_value = sum(comb(d, k) for k in range(wins, d + 1)) / 2 ** d
    return (d, wins, float(p_value))


def score(predicted: Sequence[str], actual: Sequence[str], *, conf: float = 0.95,
          n_boot: int = N_BOOT, seed: int = SEED, refit_constant: bool = True) -> Skill:
    """Everything a sealed cohort should report about how it did against its baseline."""
    predicted, actual = list(predicted), list(actual)
    correct = sum(p == a for p, a in zip(predicted, actual))
    label, const = best_constant(actual)
    lo, hi = margin_interval(predicted, actual, conf=conf, n_boot=n_boot, seed=seed,
                             refit_constant=refit_constant)
    d, wins, p = sign_test(predicted, actual)
    return Skill(n=len(actual), correct=correct, constant_label=label, constant_correct=const,
                 margin=correct - const, lo=lo, hi=hi, conf=conf,
                 discordant=d, rule_wins=wins, sign_p=p)


# ---------------------------------------------------------------- future seals only

def brier(probs: Sequence[float], actual_up: Sequence[int]) -> float:
    """Mean squared error of probabilistic sign calls. Lower is better; 0.25 is a coin."""
    p = np.asarray(probs, dtype=float)
    y = np.asarray(actual_up, dtype=float)
    return float(np.mean((p - y) ** 2))


def brier_skill(probs: Sequence[float], actual_up: Sequence[int],
                reference: float | None = None) -> float:
    """Brier skill score against a climatological reference. 0 means no better than it.

    ``reference`` is the constant probability a baseline forecaster would issue; left None it
    is the cohort's own rate of ``up``, which is the *best possible* constant and therefore
    the conservative comparator.

    This is the instrument that dissolves the Minnesota/Iowa problem without another
    threshold: a seal that commits, say, 0.55 on an arm sitting near the crossover and 0.95
    on one far from it is barely penalised for missing the first, because it said so in
    advance. It only works if the probabilities are sealed with the rule — see the module
    docstring.
    """
    y = np.asarray(actual_up, dtype=float)
    ref = float(np.mean(y)) if reference is None else float(reference)
    ref_brier = float(np.mean((ref - y) ** 2))
    if ref_brier == 0.0 or isnan(ref_brier):
        return float("nan")
    return 1.0 - brier(probs, actual_up) / ref_brier


# ---------------------------------------------------------------- named nulls

@dataclass(frozen=True)
class PairSkill:
    """A rule against one *named* null, rather than against whatever constant scored best.

    The race cohort already works this way — it seals a cutoff-only reading and a 0.5-prior
    reading and scores both — so its comparison needs a margin and an interval too.
    """

    name: str
    n: int
    rule_correct: int
    null_correct: int
    margin: int
    lo: float
    hi: float
    conf: float
    discordant: int
    rule_wins: int
    sign_p: float

    def line(self) -> str:
        return (f"vs {self.name}: {self.rule_correct}/{self.n} against {self.null_correct}"
                f"/{self.n}  margin {self.margin:+d} arms, {self.conf:.0%} CI "
                f"[{self.lo:+.1f}, {self.hi:+.1f}]  sign test p = "
                + (f"{self.sign_p:.3f}" if not isnan(self.sign_p) else "n/a")
                + f" ({self.rule_wins}/{self.discordant} discordant)")


def score_pair(rule_correct: Sequence[bool], null_correct: Sequence[bool], name: str, *,
               conf: float = 0.95, n_boot: int = N_BOOT, seed: int = SEED) -> PairSkill:
    """Paired skill of a rule over a named null, from the two correctness vectors.

    The bootstrap resamples arms and recomputes both scores on each resample, so the
    interval carries the fact that rule and null were graded on the *same* arms.
    """
    a = np.asarray(rule_correct, dtype=bool)
    b = np.asarray(null_correct, dtype=bool)
    n = len(a)
    rng = np.random.default_rng(seed)
    if n:
        idx = rng.integers(0, n, size=(n_boot, n))
        margins = a[idx].sum(axis=1) - b[idx].sum(axis=1)
        tail = (1.0 - conf) / 2.0
        lo, hi = float(np.quantile(margins, tail)), float(np.quantile(margins, 1.0 - tail))
    else:
        lo = hi = float("nan")
    disc = int(np.sum(a != b))
    wins = int(np.sum(a & ~b))
    p = (sum(comb(disc, k) for k in range(wins, disc + 1)) / 2 ** disc) if disc else float("nan")
    return PairSkill(name=name, n=n, rule_correct=int(a.sum()), null_correct=int(b.sum()),
                     margin=int(a.sum() - b.sum()), lo=lo, hi=hi, conf=conf,
                     discordant=disc, rule_wins=wins, sign_p=float(p))
