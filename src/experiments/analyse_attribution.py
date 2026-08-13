"""What an attribution *share* can and cannot tell you about what a model leans on.

**Individual work, beyond the course submission.**

**This is post-hoc and is not pre-registered.** Every number below is recomputed from
results already committed by ``run_shap``, and the analysis was written after looking at
them. Documents 13 and 18 both record what goes wrong when a quantity chosen after seeing
the data is then reported as a test, so nothing here is offered as one. It is descriptive:
it decomposes a number the documents already quote, and the only claim it supports is
about what that number can bear.

The problem with the estimand
-----------------------------
``explain.aggregate_attributions`` returns ``series / series.sum()`` -- every attribution
figure in documents 06, 16 and 17 is a **share of the model's total attribution mass**.
That choice is defended in ``src/explain.py`` and the defence is sound: the six methods
emit scores on different scales, and raw mean-|SHAP| is not comparable across them.

But shares are compositional. They sum to one, so no feature's share can move without some
other feature's share moving to pay for it, and a change in one feature's share is
consistent with at least three different underlying stories:

1. that feature's absolute attribution rose while the others held still;
2. that feature held still while others fell, so its share rose mechanically;
3. the total mass changed and the feature held its absolute position.

Document 06 reports `relationship` gaining +151% of share under a demographic parity
constraint, and document 17 builds on the same estimand. Shares cannot distinguish those
three stories, so "which features the model leans on" is not identified by share movements
alone. That is a limit on the measure, not an error in the measurement.

What this module computes
-------------------------
Three decompositions of a committed result, none of which need a re-run:

* **a collinear pair as one coalition.** On Adult the pair given to ``--pair`` is
  `relationship` and `marital-status`, the dataset's two most redundant features
  (Cramér's V 0.487, document 17). If the constraint merely reallocates credit between
  them, scoring them as a single coalition should absorb the effect. Document 18 already
  reports the aggregate signature -- the pair moves 0.183 in magnitude while its combined
  share moves 0.045 -- and what is added here is the per-seed spread, which decides
  whether the residual is a real effect or noise.

* **the same coalition across every mitigation**, which document 18 does not report, and
  which separates a property of the constraint from a property of the algorithm.

* **the donor decomposition**: which features actually gave up share. A pure swap inside
  the collinear pair predicts that the pair's other half funds essentially all of the
  gain. On Adult it does not.

The pair is an argument rather than a constant because which two features are redundant is
a fact about the dataset, not about this analysis.

Run:  python -m src.experiments.analyse_attribution --pair relationship marital-status
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..results_io import output_dir, research_dir

BASELINE = "baseline"

DEFAULT_SEEDS = [0, 1, 2, 3, 4]


def load_seed_shares(source: Path, seeds: list[int]) -> dict[int, pd.DataFrame]:
    """Per-seed attribution shares, as committed by ``run_shap``."""
    frames = {}
    for seed in seeds:
        path = source / f"shap_feature_shares_seed{seed}.csv"
        if path.exists():
            frames[seed] = pd.read_csv(path, index_col=0)
    if not frames:
        raise FileNotFoundError(
            f"no shap_feature_shares_seed*.csv in {source}; run run_shap for this dataset"
        )
    return frames


def pct_change(after: float, before: float) -> float:
    return 100.0 * (after / before - 1.0) if before else float("nan")


def pair_by_seed(
    frames: dict[int, pd.DataFrame], method: str, pair: list[str]
) -> pd.DataFrame:
    """Per-seed movement of the collinear pair, individually and as one coalition.

    The per-seed view is the point. The committed summary file averages the shares and
    then takes one ratio, which cannot say whether the coalition-level residual holds in
    every split or is carried by one of them.
    """
    first, second = pair
    rows = []
    for seed, frame in frames.items():
        before, after = frame[BASELINE], frame[method]
        rows.append({
            "seed": seed,
            "first_before": before[first],
            "first_after": after[first],
            "first_pct": pct_change(after[first], before[first]),
            "second_before": before[second],
            "second_after": after[second],
            "pair_before": before[pair].sum(),
            "pair_after": after[pair].sum(),
            "pair_pct": pct_change(after[pair].sum(), before[pair].sum()),
        })
    return pd.DataFrame(rows).set_index("seed")


def pair_across_methods(mean_shares: pd.DataFrame, pair: list[str]) -> pd.DataFrame:
    """The single-feature and coalition views side by side, for every mitigation."""
    first = pair[0]
    pair_before = mean_shares.loc[pair, BASELINE].sum()
    rows = []
    for method in mean_shares.columns:
        if method == BASELINE:
            continue
        rows.append({
            "method": method,
            "first_pct": pct_change(mean_shares.loc[first, method],
                                    mean_shares.loc[first, BASELINE]),
            "pair_pct": pct_change(mean_shares.loc[pair, method].sum(), pair_before),
        })
    return pd.DataFrame(rows).set_index("method")


def donors(mean_shares: pd.DataFrame, method: str) -> pd.DataFrame:
    """Which features gave up share, and what fraction of the total each supplied.

    Share is zero-sum, so this cannot say that one feature's loss *became* another's
    gain -- that pairing is not identifiable from compositional data. It can say how
    concentrated the losses were, which is what the collinear-swap account predicts.
    """
    delta = (mean_shares[method] - mean_shares[BASELINE]).sort_values()
    lost = delta[delta < 0]
    frame = lost.to_frame("share_given_up")
    frame["pct_of_all_given_up"] = 100.0 * frame["share_given_up"] / frame["share_given_up"].sum()
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="adult")
    parser.add_argument("--pair", nargs=2, required=True, metavar=("FEATURE", "FEATURE"),
                        help="the two redundant features to score as one coalition")
    parser.add_argument("--method", default="expgrad_dp",
                        help="the mitigated column to decompose against the baseline")
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS)
    args = parser.parse_args()

    source = output_dir(args.dataset)
    frames = load_seed_shares(source, args.seeds)
    mean_shares = pd.read_csv(source / "shap_feature_shares.csv", index_col=0)
    first, second = args.pair

    print(f"=== {args.dataset}, {len(frames)} seeds. "
          f"Post-hoc decomposition of a committed result ===\n")

    per_seed = pair_by_seed(frames, args.method, args.pair)
    print(f"--- `{first}` and `{second}` under {args.method}, per seed ---")
    print(per_seed.round(4).to_string())
    print(f"\n  {first} alone: {per_seed['first_pct'].mean():+.1f}% "
          f"(sd {per_seed['first_pct'].std():.1f})")
    print(f"  the pair together: {per_seed['pair_pct'].mean():+.1f}% "
          f"(sd {per_seed['pair_pct'].std():.1f}), "
          f"same sign in {int((per_seed['pair_pct'] > 0).sum())}/{len(per_seed)} seeds")
    print("\n  Scoring the two redundant features as one coalition is what separates a")
    print("  model that leans somewhere new from credit moving between near-substitutes.")

    across = pair_across_methods(mean_shares, args.pair)
    print("\n--- the same coalition, every mitigation ---")
    print(across.round(1).to_string())
    print("\n  If the coalition moves in different directions under different constraints")
    print("  with the algorithm held fixed, the movement is not a pure artifact of how")
    print("  Shapley divides credit: the pair's redundancy is a property of the dataset")
    print("  and is identical in every row of that table.")

    given_up = donors(mean_shares, args.method)
    print(f"\n--- who gave up share under {args.method} ---")
    print(given_up.round(4).to_string())
    if second in given_up.index:
        supplied = given_up.loc[second, "pct_of_all_given_up"]
        others = [f for f in given_up.index if f not in args.pair]
        print(f"\n  `{second}` supplied {supplied:.0f}% of all the share released. A pure")
        print("  swap inside the pair predicts nearly all of it.")
        if others:
            print(f"  The next largest donor is `{others[0]}`, which is outside the pair.")

    out = research_dir("attribution")
    stem = f"attribution_{args.dataset}"
    per_seed.to_csv(out / f"{stem}_pair_by_seed.csv")
    across.to_csv(out / f"{stem}_pair_across_methods.csv")
    given_up.to_csv(out / f"{stem}_donors_{args.method}.csv")
    print(f"\nwrote {out}/{stem}_*.csv")


if __name__ == "__main__":
    main()
