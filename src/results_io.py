"""Where experiment outputs go, and why no two runs can collide.

Three separate overwrite bugs have occurred in this project, all silent:

1. every SHAP seed wrote to one filename, so seeds overwrote each other and the deck
   quoted whichever finished last;
2. every experiment wrote to a fixed path regardless of dataset, so the first ACS run
   destroyed the committed Adult results the report and deck are built from;
3. re-running an experiment with *different parameters* replaced the canonical result
   with a differently-scoped one -- running the baseline with ``--seeds 0`` silently
   turned the committed five-seed table into a one-seed table whose standard
   deviations were all NaN.

None raised an error. All produced plausible numbers. So the layout is now enforced
rather than followed by convention:

    results/
    ├── <experiment>_<kind>.csv                     Adult, canonical (what builders read)
    ├── <experiment>_<kind>__<signature>.csv        Adult, one per distinct parameter set
    ├── <experiment>.json                           provenance for the canonical copy
    └── <dataset>/                                  every non-Adult dataset
        └── ... the same three, isolated

**Dataset separates by directory. Parameters separate by filename.** The signature is
derived from the run's own arguments, so two runs that differ in any way that changes
the numbers land in different files and neither is lost. The canonical copy is the
most recent run and exists so ``scripts/build_deck.py`` and ``scripts/build_report.py``
have a stable path to read.

Overwriting the canonical copy with a *differently parameterised* run raises unless
``--force`` is passed. That is the guard the three bugs above needed: replacing a
result with a re-run of the same thing is fine and expected; replacing a five-seed
table with a one-seed table is what should stop you.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"

# Adult keeps the flat paths so every existing reference in the docs, deck and report
# stays valid. It was the only dataset when those were written.
FLAT_DATASET = "adult"


def output_dir(dataset_name: str) -> Path:
    """Directory for one dataset's results, created if needed."""
    path = RESULTS_DIR if dataset_name == FLAT_DATASET else RESULTS_DIR / dataset_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _compact(value: Any) -> str:
    """Render one parameter for a filename: short, readable, filesystem-safe."""
    if isinstance(value, (list, tuple)):
        numbers = [v for v in value if isinstance(v, int)]
        if numbers and numbers == list(range(min(numbers), max(numbers) + 1)):
            return f"{min(numbers)}-{max(numbers)}" if len(numbers) > 1 else str(numbers[0])
        return ",".join(str(v) for v in value)
    if isinstance(value, float):
        return f"{value:g}"
    return str(value).replace("/", "-").replace(" ", "")


def run_signature(params: dict[str, Any]) -> str:
    """A short, readable, order-independent slug identifying a parameter set.

    Readable rather than hashed on purpose: the point is that someone looking at the
    directory can tell ``ablation_summary__seeds0-4_eps0.01.csv`` from the one-seed
    run beside it without opening either.
    """
    parts = [
        f"{key}{_compact(value)}"
        for key, value in sorted(params.items())
        if value is not None and key != "dataset"
    ]
    return "_".join(parts) if parts else "default"


def _provenance_path(directory: Path, experiment: str) -> Path:
    return directory / f"{experiment}.json"


def check_overwrite(
    directory: Path, experiment: str, params: dict[str, Any], *, force: bool = False
) -> None:
    """Refuse to replace a canonical result produced with different parameters.

    Re-running the same configuration overwrites freely -- that is how results get
    regenerated. Running a *different* configuration into the same canonical filename
    is the accident this exists to stop.
    """
    path = _provenance_path(directory, experiment)
    if force or not path.exists():
        return

    previous = json.loads(path.read_text()).get("params", {})
    signature, previous_signature = run_signature(params), run_signature(previous)
    if signature == previous_signature:
        return

    raise SystemExit(
        f"\nRefusing to overwrite {directory}/{experiment}_*.csv\n"
        f"  existing results were produced with: {previous_signature}\n"
        f"  this run would produce:              {signature}\n\n"
        f"The archived copy for this run is written regardless, at\n"
        f"  {directory}/{experiment}_<kind>__{signature}.csv\n"
        f"so nothing is lost either way. Pass --force to also replace the canonical\n"
        f"copy that the report and deck read from.\n"
    )


def save(
    directory: Path,
    experiment: str,
    frames: dict[str, pd.DataFrame],
    *,
    params: dict[str, Any],
    force: bool = False,
    index: bool = True,
) -> list[Path]:
    """Write one experiment's outputs, archived by signature and canonically.

    Args:
        directory: from :func:`output_dir`.
        experiment: short name, e.g. ``"ablation"``.
        frames: ``{kind: frame}``, e.g. ``{"runs": ..., "summary": ...}``.
        params: the run's arguments, used for the signature and the guard.
        force: replace the canonical copy even if it came from a different run.
        index: whether frames carry a meaningful index.

    Returns every path written.
    """
    check_overwrite(directory, experiment, params, force=force)
    signature = run_signature(params)
    written: list[Path] = []

    for kind, frame in frames.items():
        use_index = index and not isinstance(frame.index, pd.RangeIndex)
        archived = directory / f"{experiment}_{kind}__{signature}.csv"
        canonical = directory / f"{experiment}_{kind}.csv"
        frame.to_csv(archived, index=use_index)
        frame.to_csv(canonical, index=use_index)
        written += [archived, canonical]

    _provenance_path(directory, experiment).write_text(
        json.dumps(
            {"experiment": experiment, "signature": signature, "params": params,
             "files": [p.name for p in written]},
            indent=2, default=str,
        )
    )
    return written


def describe(directory: Path, experiment: str) -> str:
    """One line naming which run the canonical files came from."""
    path = _provenance_path(directory, experiment)
    if not path.exists():
        return "no provenance recorded"
    return json.loads(path.read_text()).get("signature", "unknown")
