"""Skill margins with intervals, for every sealed cohort that has been scored.

**Individual work, beyond the course submission. Post-hoc re-expression, not a new test.**

Each cohort below has already been scored under its own sealed rubric, and those verdicts
stand exactly as sealed. This adds the quantity a pass/fail count cannot carry: how much
better than its named baseline the rule did, and how wide the uncertainty on that margin is
at these sample sizes. See ``src/skill.py`` for why.

Nothing here changes a verdict. Where a margin's interval spans zero, the sealed verdict is
still the sealed verdict — the interval is the honest statement of what a ten-arm cohort can
support, and it is what should be reported beside the count rather than instead of it.

Run:  python -m src.experiments.analyse_skill
"""

from __future__ import annotations

import pandas as pd

from ..results_io import RESEARCH_RESULTS_DIR, research_dir
from ..skill import score, score_pair


def _read(rel: str) -> pd.DataFrame | None:
    path = RESEARCH_RESULTS_DIR / rel
    return pd.read_csv(path) if path.exists() else None


def main() -> None:
    rows = []

    print("=" * 78)
    print("SKILL MARGINS  (sealed verdicts unchanged; this is the interval they omit)")
    print("=" * 78)

    # --- cohorts scored against the best constant ------------------------------------
    against_constant = [
        ("Re-seal, unrefined rule", "resealed/resealed.csv",
         lambda d: d, "predicted", "actual"),
        ("Seal 1, refined rule", "sealed/sealed.csv",
         lambda d: d[d["held_out"]], "predicted", "actual"),
        ("Cross-task shape seal", "task_shapes/task_shapes.csv",
         lambda d: d[d["observed"].isin(["HIGH", "LOW"])], "predicted", "observed"),
    ]
    for label, rel, keep, pcol, acol in against_constant:
        frame = _read(rel)
        if frame is None:
            print(f"\n{label}: no stored result")
            continue
        frame = keep(frame)
        if frame.empty:
            print(f"\n{label}: no scorable arms")
            continue
        s = score(frame[pcol].tolist(), frame[acol].tolist())
        print(f"\n{label}  (n = {s.n})")
        print(f"  baseline: always '{s.constant_label}'")
        print(f"  {s.line()}")
        rows.append({"cohort": label, "baseline": f"constant '{s.constant_label}'",
                     "n": s.n, "rule": s.correct, "null": s.constant_correct,
                     "margin": s.margin, "lo": s.lo, "hi": s.hi,
                     "discordant": s.discordant, "rule_wins": s.rule_wins,
                     "sign_p": s.sign_p})

    # --- cohorts that sealed their own nulls -----------------------------------------
    named = [
        ("Race cohort S1 (screen-gated)", "ipums_sealed/race_s1.csv"),
        ("Third cohort S1 (in-band, no verdict)", "ipums_sealed/s1.csv"),
    ]
    for label, rel in named:
        frame = _read(rel)
        if frame is None:
            print(f"\n{label}: no stored result")
            continue
        print(f"\n{label}  (n = {len(frame)})")
        for null_col, null_name in (("null_cutoff", "cutoff-only null"),
                                    ("null_half", "0.5-prior null")):
            if null_col not in frame.columns:
                continue
            s = score_pair(frame["rule"].astype(bool), frame[null_col].astype(bool), null_name)
            print(f"  {s.line()}")
            rows.append({"cohort": label, "baseline": null_name, "n": s.n,
                         "rule": s.rule_correct, "null": s.null_correct,
                         "margin": s.margin, "lo": s.lo, "hi": s.hi,
                         "discordant": s.discordant, "rule_wins": s.rule_wins,
                         "sign_p": s.sign_p})

    out = research_dir("skill")
    pd.DataFrame(rows).round(4).to_csv(out / "skill_margins.csv", index=False)
    print("\n" + "-" * 78)
    print("Read the intervals as coarse: at n <= 10 the resampled margin takes few distinct")
    print("values. An interval spanning zero does not overturn a sealed pass; it states what")
    print("the cohort can support, which is what a bare count conceals.")
    print(f"\nwrote {out}/skill_margins.csv")


if __name__ == "__main__":
    main()
