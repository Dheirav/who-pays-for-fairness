"""Who pays for the fairness fix -- incidence analysis.

Every aggregate fairness metric in :mod:`src.metrics` is a *gap*, and a gap can be
closed from either end. "Demographic parity difference fell from 0.186 to 0.018" is
compatible with two opposite stories:

* **Levelling up**   -- the unprivileged group's selection rate rose to meet the
  privileged group's. Nobody was made worse off.
* **Levelling down** -- the privileged group's selection rate fell to meet the
  unprivileged group's. The gap closed by taking favourable outcomes away.

Mittelstadt, Wachter & Russell (2023), "The Unfairness of Fair Machine Learning",
argue that levelling down is the common case and that reporting only the gap conceals
it. Ferry, Aivodji, Gambs, Huguet & Siala (2023), "When Mitigating Bias is Unfair"
(arXiv:2302.07185), turn that argument into an audit, and their first three dimensions
-- impact size, direction of change, effect on acceptance rates -- are what this module
computes. It is written here rather than imported because the rest of the pipeline
needs the split per-rate and per-person, not because the split is new. It is worth
reporting because the two outcomes are not equally defensible: a bank that closes a
lending gap by denying more privileged applicants has satisfied the metric while
making the world worse.

The decomposition is exact, not a heuristic. Write the signed gap as

    gap = r_priv - r_unpriv

then the change in the gap between the baseline model and the mitigated model is

    closure = gap_before - gap_after
            = (r_priv_before - r_priv_after) + (r_unpriv_after - r_unpriv_before)
              \\_____ privileged loss _____/    \\____ unprivileged gain ____/

The two terms sum to the closure identically, so their ratio is a well-defined share.

Two things this module deliberately does *not* do:

* It does not treat a falling **FPR** as costless. A privileged applicant who loses a
  false positive loses a favourable outcome they had; that it was unearned is a
  separate normative question from whether they bear a cost.
* It does not stop at rates. :func:`flip_counts` reports how many individual test
  subjects had their decision reversed, which is the number a person affected by the
  system would care about and which rate-level analysis hides -- a group's selection
  rate can be unchanged while a third of its members swap places.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import group_breakdown

# Rates decomposed. All three are "favourable outcome" rates from the subject's point
# of view -- a higher value means more members of the group received the positive
# decision, whether or not they merited it.
RATES = ["selection_rate", "tpr", "fpr"]

# Thresholds for the verdict column. A closure that is 75%+ attributable to the
# privileged group losing ground is levelling down in substance, not just in part.
LEVELLING_DOWN_SHARE = 0.75
LEVELLING_UP_SHARE = 0.25


def _verdict(share_down: float, closure: float) -> str:
    if not np.isfinite(share_down):
        return "gap widened" if closure <= 0 else "undefined"
    if share_down >= LEVELLING_DOWN_SHARE:
        return "levelling down"
    if share_down <= LEVELLING_UP_SHARE:
        return "levelling up"
    return "mixed"


def decompose_gap(
    y_true, a, y_base, y_mit, *, privileged, unprivileged
) -> pd.DataFrame:
    """Split each closed fairness gap into privileged loss vs unprivileged gain.

    Returns one row per rate in :data:`RATES` with the signed gap before and after,
    the closure, the two contributions (which sum to the closure), the share of the
    closure borne by the privileged group, and a verdict.

    ``share_levelling_down`` is NaN when the gap did not close, since attributing a
    share of a non-existent improvement is meaningless. It can exceed 1 or go below 0:
    a value of 1.3 means the privileged group fell further than the gap closed,
    because the unprivileged group lost ground too.
    """
    kw = {"privileged": privileged, "unprivileged": unprivileged}
    before = group_breakdown(y_true, y_base, a, **kw)
    after = group_breakdown(y_true, y_mit, a, **kw)

    rows = []
    for rate in RATES:
        priv_before, priv_after = before.loc["privileged", rate], after.loc["privileged", rate]
        unp_before, unp_after = before.loc["unprivileged", rate], after.loc["unprivileged", rate]

        gap_before = priv_before - unp_before
        gap_after = priv_after - unp_after
        closure = gap_before - gap_after
        priv_loss = priv_before - priv_after
        unp_gain = unp_after - unp_before

        share_down = priv_loss / closure if closure > 0 else np.nan
        rows.append({
            "rate": rate,
            "priv_before": priv_before,
            "priv_after": priv_after,
            "unpriv_before": unp_before,
            "unpriv_after": unp_after,
            "gap_before": gap_before,
            "gap_after": gap_after,
            "closure": closure,
            "from_privileged_loss": priv_loss,
            "from_unprivileged_gain": unp_gain,
            "share_levelling_down": share_down,
            "verdict": _verdict(share_down, closure),
        })
    return pd.DataFrame(rows).set_index("rate")


def flip_counts(a, y_base, y_mit, *, privileged, unprivileged) -> pd.DataFrame:
    """Per-group counts of individuals whose decision the mitigation reversed.

    Rate-level analysis is blind to churn: a group can keep the same selection rate
    while every member inside it trades places. ``gained`` and ``lost`` are the two
    directions; ``net`` is what shows up in the selection rate, and ``churn`` is the
    total number of people whose outcome changed at all.
    """
    a = np.asarray(a)
    y_base = np.asarray(y_base).astype(int)
    y_mit = np.asarray(y_mit).astype(int)

    rows = []
    for label, value in (("privileged", privileged), ("unprivileged", unprivileged)):
        mask = a == value
        base, mit = y_base[mask], y_mit[mask]
        gained = int(np.sum((base == 0) & (mit == 1)))
        lost = int(np.sum((base == 1) & (mit == 0)))
        n = int(mask.sum())
        rows.append({
            "group": label,
            "n": n,
            "gained": gained,
            "lost": lost,
            "net": gained - lost,
            "churn": gained + lost,
            "pct_gained": 100.0 * gained / n if n else np.nan,
            "pct_lost": 100.0 * lost / n if n else np.nan,
            "pct_churn": 100.0 * (gained + lost) / n if n else np.nan,
        })
    return pd.DataFrame(rows).set_index("group")


def people_incidence(flips: pd.DataFrame) -> dict[str, float]:
    """Re-run the who-pays question in units of people rather than rates.

    :func:`decompose_gap` is population-size blind: it compares a privileged rate
    against an unprivileged rate, so an equal movement in both reads as a 50/50 split.
    On Adult the privileged group is 2.1x larger, so an equal *rate* movement is a
    very unequal *headcount* -- and headcount is what a person affected by the system
    experiences. Reporting only the rate decomposition would understate how lopsided
    the transfer is.

    ``lost_per_gained`` is the number of privileged subjects who lost a favourable
    decision for each unprivileged subject who gained one. Above 1 means the
    mitigation destroyed more favourable outcomes than it created.
    """
    lost = float(flips["lost"].sum())
    gained = float(flips["gained"].sum())
    priv_lost = float(flips.loc["privileged", "lost"])
    unpriv_gained = float(flips.loc["unprivileged", "gained"])
    denominator = priv_lost + unpriv_gained
    return {
        "people_share_levelling_down": priv_lost / denominator if denominator else np.nan,
        "lost_per_gained": lost / gained if gained else np.nan,
        "net_favourable_change": gained - lost,
    }


def churn_attribution(total_churn: float, floor: float) -> float:
    """Fraction of a method's individual-level effect that is its own randomness.

    A randomized classifier reassigns some subjects on every draw regardless of any
    fairness constraint. If 4.5% of subjects change decision under the mitigation but
    3.8% would change between two draws of the *same* fitted model, then most of the
    apparent effect is a coin flip, and citing the 4.5% as "the constraint changed
    these people's outcomes" is wrong. Returns 0 for deterministic methods.
    """
    if total_churn <= 0:
        return 0.0
    return float(min(floor / total_churn, 1.0))


def outcome_total(y_base, y_mit) -> dict[str, float]:
    """Did the mitigation shrink the pie?

    Demographic parity constrains the *ratio* of favourable outcomes, not the total.
    A method can satisfy it while handing out fewer positive decisions overall, which
    is the aggregate form of levelling down and is invisible in every metric the
    ablation table reports.
    """
    base_positive = int(np.sum(np.asarray(y_base).astype(int)))
    mit_positive = int(np.sum(np.asarray(y_mit).astype(int)))
    return {
        "positives_before": base_positive,
        "positives_after": mit_positive,
        "delta": mit_positive - base_positive,
        "pct_change": 100.0 * (mit_positive - base_positive) / base_positive
        if base_positive
        else np.nan,
    }


def disagreement(y_a, y_b) -> float:
    """Fraction of subjects on which two prediction vectors disagree.

    Used two ways: between a baseline and a mitigated model (how much the constraint
    moved), and between two draws from the *same* randomized classifier (how much of
    that movement is arbitrary rather than caused by the constraint).
    """
    y_a = np.asarray(y_a).astype(int)
    y_b = np.asarray(y_b).astype(int)
    return float(np.mean(y_a != y_b))
