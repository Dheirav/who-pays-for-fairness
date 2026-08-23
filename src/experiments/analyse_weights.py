"""Weighted versus unweighted label rates and gaps, per state-year: the nonresponse test.

**Individual work, beyond the course submission. Post-hoc diagnostic** — the first of the
review council's three candidate mechanisms for the 2022 inversion (document 57). The
Census Bureau's pandemic-era nonresponse corrections live in ``PWGTP``; if that mechanism
drove the inversion, weighting should move 2022's rates and gaps substantially more than
2018's. It does not: the deltas are comparable across vintages, which exculpates the
suspect at label level and leaves the real-threshold mechanism, confirmed separately.

Run:  python -m src.experiments.analyse_weights --states AL OH SC NV MN CO FL PA
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ..results_io import research_dir

# state -> years measured in this project's record (2018 baseline plus every extra vintage)
DEFAULT_CASES = [("AL", "2018"), ("AL", "2022"), ("OH", "2018"), ("OH", "2019"),
                 ("OH", "2022"), ("SC", "2018"), ("SC", "2022"), ("NV", "2014"),
                 ("NV", "2019"), ("NV", "2022"), ("MN", "2018"), ("CO", "2018"),
                 ("FL", "2018"), ("PA", "2018")]


def main() -> None:
    from folktables import ACSDataSource
    from folktables.acs import adult_filter

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", nargs="*", default=None,
                        help="restrict to these states (default: the document-57 cases)")
    args = parser.parse_args()
    cases = [c for c in DEFAULT_CASES if args.states is None or c[0] in args.states]

    rows = []
    for state, year in cases:
        source = ACSDataSource(survey_year=year, horizon="1-Year", survey="person",
                               root_dir="data/acs")
        frame = adult_filter(source.get_data(states=[state], download=True))
        y = (frame["PINCP"] > 50000).astype(int).to_numpy()
        w = frame["PWGTP"].to_numpy().astype(float)
        male = (frame["SEX"] == 1).to_numpy()
        rows.append({
            "state": state, "year": year,
            "p_unweighted": float(y.mean()),
            "p_weighted": float(np.average(y, weights=w)),
            "gap_unweighted": float(y[male].mean() - y[~male].mean()),
            "gap_weighted": float(np.average(y[male], weights=w[male])
                                  - np.average(y[~male], weights=w[~male])),
        })
    frame = pd.DataFrame(rows)
    frame["d_p"] = frame["p_weighted"] - frame["p_unweighted"]
    frame["d_gap"] = frame["gap_weighted"] - frame["gap_unweighted"]
    print(frame.round(3).to_string(index=False))
    print("\nby year, mean |d_p| and |d_gap| — the nonresponse signature would be a "
          "2022 excess:")
    print(frame.groupby("year")[["d_p", "d_gap"]].apply(lambda g: g.abs().mean())
          .round(3).to_string())

    OUT = research_dir("weights")
    frame.round(6).to_csv(OUT / "weights.csv", index=False)
    print(f"\nwrote {OUT}/weights.csv")


if __name__ == "__main__":
    main()
