"""Deliverable 4: GridSearch sweep and the accuracy-vs-fairness Pareto frontier.

GridSearch fits one model per lambda on a fixed grid. Evaluating *all* of them --
not just the one fairlearn's selection rule returns -- traces the trade-off curve the
base paper reports, and shows how many grid points are dominated (a smooth frontier
in a plot can hide a lumpy underlying sweep).

The exponentiated-gradient and baseline models are overlaid as reference points, so
the plot answers "could a different lambda have done better than the reduction?"
rather than just showing a curve.

Usage:
    python -m src.experiments.run_pareto
    python -m src.experiments.run_pareto --constraint equalized_odds --grid-size 20
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..datasets import build as build_dataset
from ..metrics import evaluate
from ..mitigation import fit_exponentiated_gradient, fit_grid_search, pareto_frontier
from ..models import build
from ..preprocessing import prepare

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"

def output_dir(dataset) -> Path:
    """Per-dataset results directory.

    Results are namespaced by dataset name. A shared filename means running a second
    dataset overwrites the first one's committed numbers with no error and no warning
    -- which is exactly what happened the first time ACS was run, clobbering the Adult
    results that the report and deck read from. Adult keeps the flat ``results/`` paths
    so existing references stay valid; every other dataset gets its own subdirectory.
    """
    if dataset.name == "adult":
        return RESULTS_DIR
    path = RESULTS_DIR / dataset.name
    path.mkdir(parents=True, exist_ok=True)
    return path


# Validated categorical palette (slots 1-3, all-pairs pairlist, light surface).
# Capped at three hues deliberately: the full eight-slot order does not clear the
# all-pairs CVD floors that a scatter requires. The grid sweep is therefore drawn in
# neutral ink rather than taking a fourth hue -- it is a population of models, not a
# fourth named series.
COLOR = {"baseline": "#2a78d6", "expgrad_dp": "#eb6834", "expgrad_eo": "#1baf7a"}
MARKER = {"baseline": "*", "expgrad_dp": "s", "expgrad_eo": "^"}
LABEL = {
    "baseline": "Baseline (no mitigation)",
    "expgrad_dp": "ExpGrad (DP)",
    "expgrad_eo": "ExpGrad (EO)",
}
# Offset in points for each direct label, fanned so the three reference markers --
# which sit close together by construction -- do not overprint one another. The
# baseline's label is the longest, so it is the one pushed left of its marker.
LABEL_OFFSET = {
    "baseline": (-12, 8),
    "expgrad_dp": (10, -14),
    "expgrad_eo": (-10, 9),
}
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d4"

VIOLATION_COLUMN = {
    "demographic_parity": "demographic_parity_diff",
    "equalized_odds": "equalized_odds_diff",
}


def plot(sweep: pd.DataFrame, refs: pd.DataFrame, violation_col: str, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    dominated = sweep[~sweep["on_frontier"]]
    frontier = sweep[sweep["on_frontier"]].sort_values(violation_col)

    ax.scatter(
        dominated[violation_col], dominated["accuracy"],
        s=42, facecolor="none", edgecolor=MUTED, linewidth=1.2, alpha=0.55,
        label=f"GridSearch, dominated (n={len(dominated)})", zorder=2,
    )
    ax.plot(
        frontier[violation_col], frontier["accuracy"],
        color=INK, linewidth=2.0, alpha=0.7, zorder=3,
    )
    # Frontier points are drawn as wide open rings, not filled dots, so that a
    # reference model sitting at identical coordinates stays visible inside the ring.
    # This is not cosmetic: under the EO constraint the only non-dominated grid point
    # *is* the unmitigated baseline, and a filled marker would hide the very result
    # the plot exists to show.
    ax.scatter(
        frontier[violation_col], frontier["accuracy"],
        s=190, facecolor="none", edgecolor=INK, linewidth=2.2, zorder=4,
        label=f"GridSearch, Pareto frontier (n={len(frontier)})",
    )

    for _, row in refs.iterrows():
        method = row["method"]
        ax.scatter(
            row[violation_col], row["accuracy"],
            s=150 if method == "baseline" else 95,
            color=COLOR[method], marker=MARKER[method],
            edgecolor=SURFACE, linewidth=1.4, zorder=6, label=LABEL[method],
        )
        # Direct labels are required, not decorative: the aqua slot sits at 2.74:1
        # against this surface, below the 3:1 bar, so the palette's relief rule
        # applies. They also keep the figure readable in greyscale print.
        #
        # The offset is per method rather than shared. The three reference models
        # cluster in the top-left corner -- that is the whole point of the figure --
        # so a single offset put all three labels on top of each other and on top of
        # the markers they annotate.
        ax.annotate(
            LABEL[method], (row[violation_col], row["accuracy"]),
            textcoords="offset points", xytext=LABEL_OFFSET[method],
            fontsize=9, color=INK, zorder=7,
            ha="right" if LABEL_OFFSET[method][0] < 0 else "left",
        )

    # Headroom so the fanned direct labels are not clipped by the axes box.
    ax.margins(x=0.06, y=0.12)

    ax.set_xlabel(f"{violation_col.replace('_', ' ')}  (0 = fair)", fontsize=10, color=INK)
    ax.set_ylabel("Accuracy", fontsize=10, color=INK)
    ax.set_title(
        "Accuracy vs fairness on Adult: GridSearch frontier\n"
        "decision tree (depth 8), single split — up and to the left is better",
        fontsize=11.5, color=INK, loc="left", pad=12,
    )

    ax.grid(True, color=GRID, linewidth=0.7, alpha=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)

    # Legend below the axes rather than inside them: the sweep fills a different
    # corner for each constraint, so any in-axes placement collides with data on one
    # plot or the other.
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3,
        fontsize=8.5, frameon=False, labelcolor=INK, handletextpad=0.5,
        columnspacing=1.6,
    )

    fig.tight_layout()
    fig.savefig(out.with_suffix(".png"), facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(out.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="adult",
                        help="adult | acs | acs:WY | acs:CA,TX")
    parser.add_argument("--constraint", default="demographic_parity", choices=sorted(VIOLATION_COLUMN))
    parser.add_argument("--grid-size", type=int, default=15)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--model", default="decision_tree")
    args = parser.parse_args()

    violation_col = VIOLATION_COLUMN[args.constraint]

    dataset = build_dataset(args.dataset).load()
    split = prepare(dataset, random_state=args.seed)
    group_kw = {
        "privileged": dataset.privileged_value,
        "unprivileged": dataset.unprivileged_value,
    }

    print(f"fitting GridSearch ({args.constraint}, grid_size={args.grid_size}) ...", flush=True)
    gs = fit_grid_search(
        build(args.model, random_state=args.seed),
        split.X_train, split.y_train, split.a_train,
        constraint=args.constraint, grid_size=args.grid_size,
    )

    sweep_rows = []
    for i, predictor in enumerate(gs.predictors_):
        row = evaluate(
            split.y_test, predictor.predict(split.X_test), split.a_test,
            label=f"grid_{i:02d}", **group_kw,
        )
        row["grid_index"] = i
        sweep_rows.append(row)
    sweep = pd.DataFrame(sweep_rows)

    points = pareto_frontier(sweep["accuracy"], sweep[violation_col])
    sweep["on_frontier"] = [p.on_frontier for p in points]

    print("fitting reference models ...", flush=True)
    ref_rows = []
    baseline = build(args.model, random_state=args.seed)
    baseline.fit(split.X_train, split.y_train)
    ref_rows.append(evaluate(split.y_test, baseline.predict(split.X_test), split.a_test,
                             label="baseline", **group_kw))
    for constraint, label in (("demographic_parity", "expgrad_dp"), ("equalized_odds", "expgrad_eo")):
        model = fit_exponentiated_gradient(
            build(args.model, random_state=args.seed),
            split.X_train, split.y_train, split.a_train, constraint=constraint,
        )
        ref_rows.append(evaluate(split.y_test, model.predict(split.X_test, random_state=args.seed),
                                 split.a_test, label=label, **group_kw))
    refs = pd.DataFrame(ref_rows)

    cols = ["method", "accuracy", violation_col]
    print(f"\n=== GridSearch sweep ({len(sweep)} models, "
          f"{int(sweep['on_frontier'].sum())} on frontier) ===")
    print(sweep[[*cols, "on_frontier"]].round(4).to_string(index=False))
    print("\n=== reference models ===")
    print(refs[cols].round(4).to_string(index=False))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT = output_dir(dataset)
    out = OUT / f"pareto_{args.constraint}"
    sweep.to_csv(out.with_name(out.name + "_sweep.csv"), index=False)
    plot(sweep, refs, violation_col, out)
    print(f"\nwrote {out}.png / .pdf and {out.name}_sweep.csv")


if __name__ == "__main__":
    main()
