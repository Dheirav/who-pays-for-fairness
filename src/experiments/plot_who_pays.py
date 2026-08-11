"""Diverging bar chart: who lost and who gained under each mitigation.

The job of this data is **polarity** -- decisions taken away versus decisions granted
-- so the form is a diverging bar anchored at zero, warm pole left for loss and cool
pole right for gain. The whole point of the chart is that the two sides are not the
same length: every method destroyed more favourable decisions than it created, and a
diverging layout makes that readable at a glance in a way a table does not.

Counted in **people**, not rates. Document 05 explains why the two disagree: the
privileged group is 2.1x larger, so an equal rate movement is a very unequal
headcount, and the headcount is what a person subject to the system experiences.

The palette reuses the two poles already established in ``run_pareto`` so the repo's
figures read as one system. It passes the categorical validator against this surface:
worst adjacent pair dE 24.7 (protan), 33.6 (normal vision), both above the required
floors, and both poles clear 3:1 contrast against the surface.

Usage:
    python -m src.experiments.plot_who_pays
    python -m src.experiments.plot_who_pays --dataset acs_income_wy_2018
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def output_dir(dataset_name: str) -> Path:
    """Per-dataset results directory, matching the experiments' convention.

    Adult keeps the flat ``results/`` paths; every other dataset gets its own
    subdirectory, so plotting one dataset can never overwrite another's figure.
    """
    return RESULTS_DIR if dataset_name == "adult" else RESULTS_DIR / dataset_name

LOSS, GAIN = "#eb6834", "#2a78d6"
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d4"

ROW_ORDER = [
    "expgrad_eo",
    "prejudice_remover",
    "adversarial_debiasing",
    "expgrad_dp",
    "gridsearch_dp",
]
LABELS = {
    "expgrad_dp": "ExpGrad (DP)",
    "expgrad_eo": "ExpGrad (EO)",
    "gridsearch_dp": "GridSearch (DP)",
    "prejudice_remover": "Prejudice Remover",
    "adversarial_debiasing": "Adversarial Debiasing",
}

BAR_HEIGHT = 0.30      # data units; two bars per row
CORNER_PX = 4.0        # rounded data-end, per the mark spec
GAP_PX = 2.0           # surface gap between the two bars of a row


def _px_to_data(ax, px: float, axis: str) -> float:
    """Convert a pixel distance to data units on one axis."""
    origin = ax.transData.transform((0, 0))
    offset = ax.transData.inverted().transform(
        origin + ((px, 0) if axis == "x" else (0, px))
    )
    return abs(offset[0] if axis == "x" else offset[1])


def _rounded_bar(ax, value: float, centre: float, height: float, color: str) -> None:
    """A bar from zero to ``value`` with only its data-end rounded.

    The baseline end stays square so the two poles meet cleanly at the zero rule;
    rounding both ends would put a visible notch on the axis.
    """
    if value == 0:
        return
    rx = min(_px_to_data(ax, CORNER_PX, "x"), abs(value))
    ry = min(_px_to_data(ax, CORNER_PX, "y"), height / 2)
    sign = 1.0 if value > 0 else -1.0
    tip, shoulder = value, value - sign * rx
    low, high = centre - height / 2, centre + height / 2

    vertices = [
        (0, low), (shoulder, low),
        (tip, low), (tip, low + ry),          # quadratic corner
        (tip, high - ry),
        (tip, high), (shoulder, high),        # quadratic corner
        (0, high), (0, low),
    ]
    codes = [
        MplPath.MOVETO, MplPath.LINETO,
        MplPath.CURVE3, MplPath.CURVE3,
        MplPath.LINETO,
        MplPath.CURVE3, MplPath.CURVE3,
        MplPath.LINETO, MplPath.CLOSEPOLY,
    ]
    ax.add_patch(PathPatch(MplPath(vertices, codes), facecolor=color, edgecolor="none",
                           zorder=3))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="adult",
                        help="dataset name as written under results/ (e.g. adult, "
                             "acs_income_wy_2018)")
    args = parser.parse_args()

    out = output_dir(args.dataset)
    source = out / "who_pays_runs.csv"
    if not source.exists():
        raise SystemExit(f"no who-pays results at {source}; run run_who_pays first")
    runs = pd.read_csv(source)
    mean = runs.groupby("method").mean(numeric_only=True).reindex(ROW_ORDER)

    lost = mean["priv_lost"] + mean["unpriv_lost"]
    gained = mean["priv_gained"] + mean["unpriv_gained"]
    net = gained - lost

    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    positions = range(len(ROW_ORDER))
    # Right margin is wide enough that the net-change column never collides with a
    # bar's own value label -- the two sat on top of each other at 620.
    ax.set_xlim(-1150, 980)
    ax.set_ylim(-0.72, len(ROW_ORDER) - 0.28)

    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, colors=MUTED, labelsize=9)

    gap = _px_to_data(ax, GAP_PX, "y")
    offset = (BAR_HEIGHT + gap) / 2

    for y, method in zip(positions, ROW_ORDER):
        _rounded_bar(ax, -lost[method], y + offset, BAR_HEIGHT, LOSS)
        _rounded_bar(ax, gained[method], y - offset, BAR_HEIGHT, GAIN)
        ax.text(-lost[method] - 26, y + offset, f"{lost[method]:,.0f}", ha="right",
                va="center", fontsize=9, color=MUTED)
        ax.text(gained[method] + 26, y - offset, f"{gained[method]:,.0f}", ha="left",
                va="center", fontsize=9, color=MUTED)

    ax.axvline(0, color=INK, lw=1.1, zorder=4)

    ax.set_yticks(list(positions))
    ax.set_yticklabels([LABELS[m] for m in ROW_ORDER], fontsize=10, color=INK)
    ax.set_xticks([-1000, -750, -500, -250, 0, 250, 500])
    ax.set_xticklabels(["1,000", "750", "500", "250", "0", "250", "500"])
    ax.set_xlabel("people whose decision changed  (mean over 5 seeds, 13,567 test subjects)",
                  fontsize=9.5, color=MUTED, labelpad=9)

    # Net change as a selective direct label -- the number the chart exists to show.
    for y, method in zip(positions, ROW_ORDER):
        ax.text(960, y, f"net  {net[method]:+,.0f}", ha="right", va="center",
                fontsize=9.5, color=INK)

    handles = [
        plt.Line2D([], [], marker="s", ls="", ms=9, mfc=LOSS, mec=SURFACE, mew=1.4,
                   label="favourable decision taken away"),
        plt.Line2D([], [], marker="s", ls="", ms=9, mfc=GAIN, mec=SURFACE, mew=1.4,
                   label="favourable decision granted"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
              frameon=False, fontsize=9.5, labelcolor=MUTED, handletextpad=0.5,
              columnspacing=2.0)

    ax.set_title("Every mitigation destroyed more favourable decisions than it created",
                 fontsize=12.5, color=INK, pad=14, loc="left")

    fig.tight_layout()
    for extension in ("png", "pdf"):
        path = out / f"who_pays_incidence.{extension}"
        fig.savefig(path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
