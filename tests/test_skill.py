"""Guards for the skill-margin quantities.

**Individual work, beyond the course submission.**

Two jobs. The first four tests pin the arithmetic against hand-computable cases, because a
sign test and a paired bootstrap are exactly the kind of thing that silently returns a
plausible number when the pairing is wrong. The last two re-derive the paper's own reported
statistics from stored results, so that if a sealed cohort's CSV ever changes, this fails
rather than the paper quietly disagreeing with its data.

Run:  python -m tests.test_skill
"""

from __future__ import annotations

from math import isclose, isnan

import pandas as pd

from src.results_io import RESEARCH_RESULTS_DIR
from src.skill import (best_constant, brier, brier_skill, margin_interval, score,
                       score_pair, sign_test, skill_margin)


def test_best_constant_picks_the_majority_and_is_order_free():
    actual = ["down"] * 6 + ["up"] * 4
    assert best_constant(actual) == ("down", 6)
    assert best_constant(list(reversed(actual))) == ("down", 6)
    # A tie must not depend on row order: alphabetical, deterministically.
    assert best_constant(["up", "down"])[0] == "down"
    assert best_constant(["down", "up"])[0] == "down"


def test_margin_is_correct_minus_constant():
    predicted = ["down"] * 5 + ["up"] * 5
    actual = ["down"] * 6 + ["up"] * 4          # the sixth 'down' is the miss
    assert skill_margin(predicted, actual) == 9 - 6 == 3


def test_sign_test_drops_concordant_arms_and_is_exact():
    predicted = ["down"] * 5 + ["up"] * 5
    actual = ["down"] * 6 + ["up"] * 4
    disc, wins, p = sign_test(predicted, actual)
    # The constant says 'down' everywhere, so only the five 'up' calls are discordant.
    assert (disc, wins) == (5, 4)
    # One-sided exact: P(X >= 4 | n=5, p=0.5) = (5 + 1) / 32.
    assert isclose(p, 6 / 32, rel_tol=1e-12)
    # A rule that never disagrees with the constant carries no paired evidence at all.
    assert isnan(sign_test(["down"] * 4, ["down", "down", "up", "down"])[2])


def test_interval_brackets_the_point_estimate_and_refitting_caps_the_optimistic_tail():
    predicted = ["down"] * 5 + ["up"] * 5
    actual = ["down"] * 6 + ["up"] * 4
    lo, hi = margin_interval(predicted, actual, n_boot=20000, seed=1)
    assert lo <= skill_margin(predicted, actual) <= hi
    # Refitting is the conservative comparator, and the way it bites is on the upper end:
    # resamples that flip the majority sign must not credit the rule for beating a label
    # nobody would have chosen there.
    lo_fixed, hi_fixed = margin_interval(predicted, actual, n_boot=20000, seed=1,
                                         refit_constant=False)
    assert hi <= hi_fixed, (hi, hi_fixed)


def test_brier_rewards_hedging_where_the_rule_is_near_the_crossover():
    actual_up = [1, 1, 0, 0]
    confident_and_wrong = [0.95, 0.95, 0.95, 0.05]
    hedged_and_wrong = [0.95, 0.95, 0.55, 0.05]
    assert brier(hedged_and_wrong, actual_up) < brier(confident_and_wrong, actual_up)
    # A forecaster that only ever issues the base rate has no skill over it, by definition.
    assert isclose(brier_skill([0.5] * 4, actual_up), 0.0, abs_tol=1e-12)


def test_reseal_reproduces_the_papers_reported_statistics():
    path = RESEARCH_RESULTS_DIR / "resealed" / "resealed.csv"
    if not path.exists():
        print("  SKIP: re-seal has not been scored")
        return
    frame = pd.read_csv(path)
    s = score(frame["predicted"].tolist(), frame["actual"].tolist())
    assert (s.n, s.correct, s.constant_correct) == (10, 9, 6), (s.n, s.correct,
                                                                s.constant_correct)
    assert (s.discordant, s.rule_wins) == (5, 4), (s.discordant, s.rule_wins)
    # The paper reports p ~ 0.19 for this; anything else means the pairing changed.
    assert isclose(s.sign_p, 6 / 32, rel_tol=1e-9), s.sign_p


def test_race_cohort_beats_the_cutoff_null_and_loses_to_the_half_prior():
    path = RESEARCH_RESULTS_DIR / "ipums_sealed" / "race_s1.csv"
    if not path.exists():
        print("  SKIP: race cohort has not been scored")
        return
    frame = pd.read_csv(path)
    cutoff = score_pair(frame["rule"].astype(bool), frame["null_cutoff"].astype(bool), "cutoff")
    half = score_pair(frame["rule"].astype(bool), frame["null_half"].astype(bool), "half")
    # 'It is the rate': the rule beats the cutoff-only reading 8 to 5.
    assert (cutoff.rule_correct, cutoff.null_correct) == (8, 5)
    assert cutoff.margin == 3
    # And S1 fails by its own letter: a 0.50 prior edges the 0.54 prior 9 to 8.
    assert (half.rule_correct, half.null_correct) == (8, 9)
    assert half.margin == -1


def main() -> None:
    tests = [
        test_best_constant_picks_the_majority_and_is_order_free,
        test_margin_is_correct_minus_constant,
        test_sign_test_drops_concordant_arms_and_is_exact,
        test_interval_brackets_the_point_estimate_and_refitting_caps_the_optimistic_tail,
        test_brier_rewards_hedging_where_the_rule_is_near_the_crossover,
        test_reseal_reproduces_the_papers_reported_statistics,
        test_race_cohort_beats_the_cutoff_null_and_loses_to_the_half_prior,
    ]
    failures = 0
    for test in tests:
        print(f"\n{test.__name__}")
        try:
            test()
            print("  PASS")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL: {exc}")

    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
