"""The two figures the paper's argument needs, and why these two.

**Individual work, beyond the course submission.**

The paper is about a sign change and contained no picture of one. Everything was tables, so a
reader had to reconstruct the central claim from numbers.

**Figure 1 -- the claim.** Every retained arm from every densely swept population: baseline
selection rate against the change in the pool of favourable decisions. What should be visible
in three seconds is that arms below the crossover sit under the zero line and arms above it sit
over, in five domains and two countries at once.

The y-axis is **symmetric-log**. A linear axis is dominated by COMPAS's -87% and flattens
every other population into a line, which hides the sign change in exactly the populations
where it is most carefully measured. Symlog keeps the sign readable across two orders of
magnitude, and the threshold below which it is linear is marked so nobody reads the compressed
region as data.

**Figure 2 -- the design.** Oregon measured two ways: by moving the *income cutoff*, which
changes the label and therefore the difficulty of the task, and by moving the *decision
threshold*, which changes neither. The two routes falling on the same curve is what separates
"the selection rate sets the direction" from "task difficulty does", and it is the hardest step
of the argument to follow in prose.

Run:  python -m src.experiments.make_figures
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")

OUT = Path(__file__).resolve().parents[2] / "research" / "paper" / "ieee"

# The crossover cluster from document 44: four populations, three domains, two countries.
CROSSOVER = (0.511, 0.576)

# Colour-blind safe, and ordered so the two non-US / non-income instruments stand out.
LABELS = {
    "acs_income_al_2018": "ACS Alabama", "acs_income_ky_2018": "ACS Kentucky",
    "acs_income_sc_2018": "ACS S. Carolina", "acs_income_or_2018": "ACS Oregon",
    "dutch_2001_sex": "Dutch census 2001", "compas_2016_race": "COMPAS",
    "hmda_ms_la_2018_race": "HMDA MS+LA", "hmda_la_2018_race": "HMDA Louisiana",
}

COLOURS = {
    "ACS income": "#4C72B0",
    "COMPAS": "#DD8452",
    "Dutch census": "#55A868",
    "HMDA lending": "#C44E52",
}


def family(name: str) -> str:
    if name.startswith("acs"):
        return "ACS income"
    if name.startswith("compas"):
        return "COMPAS"
    if name.startswith("dutch"):
        return "Dutch census"
    return "HMDA lending"


VIABLE_SPECS = {
    "acs_income_al_2018": "acs:AL", "acs_income_ky_2018": "acs:KY",
    "acs_income_sc_2018": "acs:SC", "acs_income_or_2018": "acs:OR",
    "dutch_2001_sex": "dutch", "compas_2016_race": "compas",
    "hmda_ms_la_2018_race": "hmda:MS,LA:derived_race",
    "hmda_la_2018_race": "hmda:LA:derived_race",
}


def viable_bands() -> dict[str, tuple[float, float]]:
    """Where a classifier worth deploying can put the selection rate, per population.

    Panels otherwise show large empty regions that read as missing data. They are not: no
    arm can exist there, because reaching that rate needs a model beaten by the trivial
    predictor. On Alabama the band stops at 0.566, which is *why* its sweep cannot cross the
    crossover -- so the unreachable region is evidence and belongs on the figure.
    """
    from .viable_points import points_for

    bands = {}
    for name, spec in VIABLE_SPECS.items():
        info = points_for(spec)
        bands[name] = (info["low"], info["high"])
    return bands


def gather() -> pd.DataFrame:
    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import HMDA_POINTS, load_points_for
    from .viable_points import points_for

    frames = []
    for spec in ["acs:AL", "acs:KY", "acs:SC", "acs:OR", "dutch", "compas"]:
        info = points_for(spec)
        kept, _ = apply_rules(load_points_for(info["dataset"], info["points"]),
                              majority_baseline(spec))
        kept = kept.copy()
        kept["population"] = info["dataset"]
        frames.append(kept)

    for spec, name in [("hmda:MS,LA:derived_race", "hmda_ms_la_2018_race"),
                       ("hmda:LA:derived_race", "hmda_la_2018_race")]:
        kept, _ = apply_rules(load_points_for(name, HMDA_POINTS), majority_baseline(spec))
        if len(kept):
            kept = kept.copy()
            kept["population"] = name
            frames.append(kept)

    frame = pd.concat(frames, ignore_index=True)
    frame["family"] = frame["population"].map(family)
    return frame


def figure_one(frame: pd.DataFrame) -> None:
    """Small multiples, one panel per population -- not one pooled scatter.

    A single scatter of every arm implies a single common curve, and document 44's M2
    explicitly rejects that: pooled across populations the relationship reaches r = +0.487
    against a +0.70 bar and fails. What holds is the relationship *within* a population
    (Spearman +0.96, +0.95, +0.78 in three of four). Small multiples show exactly that, and
    show the two populations where it reverses instead of averaging them away.
    """
    bands = viable_bands()
    order = (frame.groupby("population")["selection_rate"].max()
             .sort_values(ascending=False).index.tolist())
    ncols = 4
    nrows = int(np.ceil(len(order) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(7.2, 2.0 * nrows),
                             sharex=True, sharey=True)
    axes = np.atleast_1d(axes).ravel()

    for ax, name in zip(axes, order):
        rows = frame[frame["population"] == name].sort_values("selection_rate")
        colour = COLOURS[family(str(name))]
        low, high = bands.get(str(name), (0.0, 1.0))
        ax.axvspan(0, low, color="0.86", zorder=0)
        ax.axvspan(high, 1, color="0.86", zorder=0)
        ax.axhline(0, color="0.3", lw=0.9, zorder=1)
        ax.axvspan(*CROSSOVER, color="#C44E52", alpha=0.14, zorder=0)
        ax.plot(rows["selection_rate"], rows["pie"], "o-", color=colour,
                ms=3.4, lw=1.1, zorder=3)
        reverses = float(np.corrcoef(rows["selection_rate"], rows["pie"])[0, 1]) < 0
        ax.set_title(LABELS.get(str(name), str(name)), fontsize=8,
                     color="#8B3A3E" if reverses else "0.15", loc="left", pad=3)
        # Which side of the crossover this population is structurally unable to explore.
        # Alabama and Kentucky are cut off above it, the lending arms below it, and in both
        # cases the cause is the base rate rather than anything about the constraint.
        note = None
        if high < CROSSOVER[1]:
            note = "cannot reach above the crossover"
        elif low > CROSSOVER[0]:
            note = "cannot reach below the crossover"
        if note:
            ax.text(0.5, 0.055, note, transform=ax.transAxes, ha="center",
                    fontsize=6.0, style="italic",
                    color="#8B3A3E" if reverses else "0.4")
        ax.set_yscale("symlog", linthresh=3)
        ax.set_xlim(0, 1)
        ax.tick_params(labelsize=7)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    for ax in axes[len(order):]:
        ax.set_visible(False)

    fig.supxlabel("Baseline selection rate", fontsize=8.5, y=0.02)
    fig.supylabel("Change in favourable decisions (%)", fontsize=8.5, x=0.015)
    reversing = sum(
        1 for name in order
        if float(np.corrcoef(frame[frame["population"] == name]["selection_rate"],
                             frame[frame["population"] == name]["pie"])[0, 1]) < 0)
    fig.suptitle(
        f"In {len(order) - reversing} of {len(order)} populations the change in the pool "
        f"rises with the selection rate and crosses zero.\nThe {reversing} that reverse are "
        f"marked. Grey = selection rates no deployable classifier can reach on that "
        f"population, which\ncuts some off above the crossover and others below it. "
        f"Red band = the 0.51\u20130.58 cluster.",
        fontsize=8, y=1.0, ha="center")
    fig.tight_layout(rect=(0.02, 0.03, 1, 0.98))
    fig.savefig(OUT / "fig-crossover.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}/fig-crossover.pdf  ({len(frame)} arms, {len(order)} panels)")


def figure_two() -> None:
    from .analyse_calibration import apply_rules, majority_baseline
    from .analyse_operating_point import load_cutoffs, load_points_for
    from .viable_points import points_for

    info = points_for("acs:OR")
    decision, _ = apply_rules(load_points_for(info["dataset"], info["points"]),
                              majority_baseline("acs:OR"))
    label = load_cutoffs("OR")
    if label["n_test"].isna().any():
        label["n_test"] = label["n_test"].fillna(decision["n_test"].dropna().iloc[0])
    label["selection_rate"] = label["positives_base"] / label["n_test"]
    label = label[label["dp_base"] >= 0.05]

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.axhline(0, color="0.25", lw=1.0, zorder=1)
    ax.axvspan(*CROSSOVER, color="0.55", alpha=0.16, zorder=0)

    ax.plot(label.sort_values("selection_rate")["selection_rate"],
            label.sort_values("selection_rate")["pie"],
            "o-", color="#4C72B0", ms=6, lw=1.4, zorder=3,
            label="moving the income cutoff  (changes the label, and the task)")
    ax.plot(decision.sort_values("selection_rate")["selection_rate"],
            decision.sort_values("selection_rate")["pie"],
            "s--", color="#937860", ms=5, lw=1.4, zorder=3,
            label="moving the decision threshold  (changes neither)")

    ax.set_yscale("symlog", linthresh=5)
    ax.set_xlabel("Baseline selection rate")
    ax.set_ylabel("Change in\nfavourable decisions (%)")
    ax.set_title("Oregon, measured two ways", fontsize=10, loc="left", pad=8)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right", handletextpad=0.4)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="0.9", lw=0.6)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(OUT / "fig-two-routes.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}/fig-two-routes.pdf  "
          f"({len(label)} cutoff arms, {len(decision)} threshold arms)")


def main() -> None:
    frame = gather()
    figure_one(frame)
    figure_two()


if __name__ == "__main__":
    main()
