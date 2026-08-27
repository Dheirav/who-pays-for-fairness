"""Figures that show the whole record, rather than the 5% of it the originals showed.

**Individual work, beyond the course submission.**

The paper's two figures draw eight populations and seventy-two arms out of 161 populations,
and one of them draws a single state. Everything the paper is best-sampled on --- the fifty
randomly drawn populations of the landscape survey, the located crossovers, the sealed
direction cohorts, the sixty-six lending arms --- has no figure at all. A reader is asked to
accept a claim about scale on the strength of a hand-picked handful.

Three figures, none of which selects a population by hand:

* ``survey``    every one of the fifty populations drawn at random, with its natural
  operating rate and the verdict the audit returns. This is the paper's scope claim, and it
  is the only sampling frame here that was committed before any arm ran.
* ``crossovers`` every located crossover on one axis. It replaces the vertical band the old
  figure drew at (0.511, 0.576) --- the cluster the paper has since withdrawn --- with the
  measured span, and shows Florida entering twice at two different boundaries.
* ``calibration`` direction accuracy against effect size over the sealed cohorts and the
  lending coverage, which is the 95%-against-61% split the paper currently carries in prose.

Run:  python -m src.experiments.make_coverage_figures
      python -m src.experiments.make_coverage_figures --dataset survey
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "paper" / "ieee"
RES = ROOT / "research" / "results"

SHAPE_COLOUR = {"CLASSIC": "#4C72B0", "MONOTONE": "#55A868",
                "NON-MONOTONE": "#C44E52", "INVERTED": "#DD8452"}


def _style(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=7)


def survey() -> None:
    """Fifty populations drawn at random: where they sit, and what the audit returns."""
    frame = pd.read_csv(RES / "survey" / "survey_verdicts.csv")
    frame["shape"] = frame["verdict"].str.split(" (", regex=False).str[0]
    frame = frame.dropna(subset=["nat_rate"]).sort_values("nat_rate").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for shape, sub in frame.groupby("shape"):
        ax.scatter(sub["nat_rate"], sub.index, s=22, label=shape,
                   color=SHAPE_COLOUR.get(shape, "0.5"), zorder=3)
    # The band where located crossovers actually fall, which is where an unaided reading of
    # "often" against "rarely" has nothing to say.
    ax.axvspan(0.28, 0.65, color="0.90", zorder=0)
    ax.text(0.465, -3.4, "located crossovers fall in here", ha="center", va="top",
            fontsize=6.5, color="0.35")
    ax.set_ylim(-6, len(frame) + 1)
    inside = int(((frame.nat_rate >= 0.28) & (frame.nat_rate <= 0.65)).sum())
    ax.set_xlabel("baseline selection rate of the deployed model", fontsize=8)
    ax.set_ylabel("populations, sorted", fontsize=8)
    ax.set_xlim(0, 1); ax.set_yticks([])
    ax.legend(fontsize=6.5, frameon=False, ncol=2, loc="upper left",
              bbox_to_anchor=(0.015, 0.99))
    _style(ax)
    fig.suptitle(f"Fifty populations drawn at random from a frame fixed in advance: "
                 f"{inside} of {len(frame)} sit where the rate alone cannot be read",
                 fontsize=8.5, y=1.02)
    fig.savefig(OUT / "fig-survey.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}/fig-survey.pdf  ({len(frame)} populations, "
          f"{frame['shape'].nunique()} verdict classes)")


def crossovers() -> None:
    """Every located crossover, against the cluster the paper used to draw."""
    sys.path.insert(0, str(ROOT))
    from src.experiments.analyse_circularity import distances, load_sweeps

    frame = distances(load_sweeps()).sort_values("crossover").reset_index(drop=True)
    frame["label"] = (frame["pop"].str.replace("_levelling_up", "", regex=False)
                      .str.replace("acs_income_", "ACS ", regex=False)
                      .str.replace("acs_employment_", "ACS employment ", regex=False)
                      .str.replace("acs_coverage_", "ACS coverage ", regex=False)
                      .str.replace("ipums_income_", "IPUMS ", regex=False)
                      .str.replace("hmda_", "HMDA ", regex=False))

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.axvspan(0.511, 0.576, color="#C44E52", alpha=0.16, zorder=0)
    ax.text(0.5435, len(frame) + 0.3, "the cluster as first published", ha="center",
            va="bottom", fontsize=6.5, color="#C44E52")
    ax.scatter(frame["crossover"], frame.index, s=20, color="#4C72B0", zorder=3,
               label="located crossover")
    ax.scatter(frame["natural"], frame.index, s=14, marker="|", color="0.45", zorder=2,
               label="that population's own operating rate")
    for i, row in frame.iterrows():
        ax.plot([row["crossover"], row["natural"]], [i, i], color="0.8", lw=0.7, zorder=1)
    ax.set_yticks(range(len(frame)))
    ax.set_yticklabels(frame["label"], fontsize=5.5)
    ax.set_xlabel("selection rate", fontsize=8)
    ax.set_xlim(0, 1)
    ax.legend(fontsize=6.5, frameon=False, loc="lower right",
              bbox_to_anchor=(1.0, -0.02))
    ax.set_ylim(-1, len(frame) + 1.6)
    _style(ax)
    lo, hi = frame.crossover.min(), frame.crossover.max()
    fig.suptitle(f"Located crossovers span {lo:.2f} to {hi:.2f}, not a cluster "
                 f"--- and Florida 2018 appears twice, at two boundaries",
                 fontsize=8.5, y=1.01)
    fig.savefig(OUT / "fig-crossovers.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}/fig-crossovers.pdf  ({len(frame)} located crossovers, "
          f"span {lo:.3f}-{hi:.3f})")


def calibration() -> None:
    """Direction accuracy against effect size: the scope condition, drawn."""
    parts = []
    for name in ("third_direction", "lending_direction"):
        path = RES / name / f"{name}.csv"
        if path.exists():
            parts.append(pd.read_csv(path).assign(cohort=name))
    frame = pd.concat(parts, ignore_index=True)
    frame["correct"] = frame["predicted"] == frame["actual"]
    frame["magnitude"] = frame["pie"].abs()

    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for ok, sub in frame.groupby("correct"):
        ax.scatter(sub["magnitude"], sub["rate"], s=26, zorder=3,
                   color="#4C72B0" if ok else "#C44E52",
                   marker="o" if ok else "X",
                   label="rule correct" if ok else "rule wrong")
    ax.axvline(1.0, color="0.3", lw=0.9, ls="--", zorder=2)
    above = frame[frame.magnitude >= 1.0]; below = frame[frame.magnitude < 1.0]
    ax.text(0.985, 0.03, f"below the guard\n{int(below.correct.sum())}/{len(below)}"
            f" = {below.correct.mean():.0%}", fontsize=7, color="0.25", ha="right", va="bottom")
    ax.text(1.25, 0.03, f"above the guard\n{int(above.correct.sum())}/{len(above)}"
            f" = {above.correct.mean():.0%}", fontsize=7, color="0.25", ha="left", va="bottom")
    ax.set_ylim(-0.04, 1.0)
    ax.set_xscale("log")
    ax.set_xlabel("|change in the pool of favourable decisions| (percentage points, log)",
                  fontsize=8)
    ax.set_ylabel("baseline selection rate", fontsize=8)
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
    _style(ax)
    fig.suptitle("The rule is not wrong at small effects so much as undefined: "
                 "below one point it is a coin flip", fontsize=8.5, y=1.02)
    fig.savefig(OUT / "fig-calibration.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}/fig-calibration.pdf  ({len(frame)} sealed arms, "
          f"{above.correct.mean():.0%} above the guard against {below.correct.mean():.0%} below)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", default=None,
                    choices=["survey", "crossovers", "calibration"],
                    help="draw one figure instead of all three")
    args = ap.parse_args()
    for name, fn in (("survey", survey), ("crossovers", crossovers),
                     ("calibration", calibration)):
        if args.dataset in (None, name):
            fn()


if __name__ == "__main__":
    main()
