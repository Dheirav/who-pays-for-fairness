"""Guards against experiments overwriting each other's results.

This bug class has bitten twice, and both times it was silent:

* ``run_shap`` wrote every seed to one filename, so each seed overwrote the last and
  the deck quoted whichever finished last;
* every experiment wrote to a fixed path regardless of dataset, so the first ACS run
  destroyed the committed Adult results the report and deck are built from.

Neither raised an error. Both produced plausible numbers. The first was caught by
noticing the deck disagreed with the docs, the second by noticing two different
datasets reporting *identical* figures. Relying on noticing is not a control, so the
invariants are asserted here instead.

Run:  python -m tests.test_output_isolation
"""

from __future__ import annotations

import ast
import re

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = sorted((ROOT / "src" / "experiments").glob("*.py"))
RESULTS = ROOT / "results"

# Modules that legitimately hold no results-writing code.
EXEMPT = {"__init__.py", "methods.py"}


def test_no_experiment_writes_a_file_to_the_shared_root() -> None:
    """No module may write a *file* directly into ``results/``.

    The bug is a result file landing in the shared root, where the next dataset
    overwrites it. Creating a *subdirectory* there is the opposite -- it is how
    namespacing works -- so the two are distinguished by whether the literal looks
    like a filename. ``RESULTS_DIR / "who_pays_runs.csv"`` is the bug;
    ``RESULTS_DIR / "sweep"`` is a namespace for an analysis that deliberately spans
    every dataset and therefore belongs to none of them.
    """
    offenders = []
    for path in EXPERIMENTS:
        if path.name in EXEMPT:
            continue
        source = path.read_text()
        for match in re.finditer(r'RESULTS_DIR\s*/\s*f?"([^"]+)"', source):
            target = match.group(1)
            if "." not in target:            # a directory, not a result file
                continue
            offenders.append(f"{path.name}: RESULTS_DIR / \"{target}\"")
    print(f"  scanned {len(EXPERIMENTS)} modules")
    assert not offenders, (
        "these write to the shared results root and would clobber another dataset:\n  "
        + "\n  ".join(offenders)
    )


def test_every_experiment_can_be_pointed_at_its_populations() -> None:
    """A runnable module must accept ``--dataset``, or ``--states`` if it spans many.

    Cross-population analyses belong to no single dataset by construction, so
    requiring ``--dataset`` of them would be requiring the wrong thing. What must hold
    is that no module has its populations hardcoded.
    """
    missing = [
        path.name
        for path in EXPERIMENTS
        if path.name not in EXEMPT
        and "def main(" in path.read_text()
        and not any(flag in path.read_text() for flag in ('"--dataset"', '"--states"'))
    ]
    print(f"  {len([p for p in EXPERIMENTS if p.name not in EXEMPT])} runnable modules")
    assert not missing, f"no --dataset flag: {missing}"


def test_output_dir_separates_datasets() -> None:
    """Adult keeps the flat paths; anything else gets its own subdirectory."""
    from src.results_io import output_dir

    adult = output_dir("adult")
    other = output_dir("acs_income_wy_2018")
    print(f"  adult -> {adult.name}/   other -> {other.relative_to(RESULTS)}/")
    assert adult == RESULTS, "adult must keep the flat results/ paths"
    assert other != RESULTS and other.parent == RESULTS
    assert adult != other, "two datasets must not share an output directory"


def test_shap_writes_one_file_per_seed() -> None:
    """The per-seed filename must interpolate the seed, or seeds overwrite each other.

    Checked on the f-string AST node rather than on string literals: an f-string is
    parsed into alternating constants and ``FormattedValue`` holes, so the
    interpolation never appears as a literal and a literal-based check would pass a
    hardcoded name and fail a correct one.
    """
    tree = ast.parse((ROOT / "src" / "experiments" / "run_shap.py").read_text())
    interpolated = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.JoinedStr):
            continue
        text = "".join(
            part.value for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
        if not text.startswith("shap_"):
            continue
        holes = [ast.unparse(p.value) for p in node.values
                 if isinstance(p, ast.FormattedValue)]
        interpolated.append((text, holes))

    print(f"  per-seed write targets: {interpolated}")
    assert interpolated, "run_shap writes no f-string-named shap_* file"
    for text, holes in interpolated:
        assert any("seed" in hole for hole in holes), (
            f"'{text}' does not interpolate the seed, so seeds would overwrite it"
        )


def test_no_dataset_specific_column_names_in_experiments() -> None:
    """Column names belong to the dataset, not to the experiment.

    Hardcoding ``"race"`` or ``"relationship"`` is what made the experiments
    Adult-only despite the interface claiming otherwise.
    """
    banned = ["relationship", "marital-status", "hours-per-week", "native-country",
              "education-num", "capital-gain"]
    offenders = []
    for path in EXPERIMENTS:
        source = path.read_text()
        # Strip docstrings and comments: prose may name Adult's columns freely.
        code = ast.unparse(ast.parse(source))
        for name in banned:
            if f'"{name}"' in code or f"'{name}'" in code:
                offenders.append(f"{path.name}: {name!r}")
    print(f"  checked {len(banned)} Adult column names")
    assert not offenders, (
        "dataset-specific column names in experiment code:\n  " + "\n  ".join(offenders)
    )


def test_canonical_results_are_guarded_against_a_different_run() -> None:
    """Replacing a five-seed table with a one-seed table must raise, not succeed.

    This is the third overwrite bug: same experiment, same dataset, different
    parameters, one canonical filename. It is the one that silently turned the
    committed baseline into a single-seed table with NaN standard deviations.
    """
    import tempfile

    from src.results_io import check_overwrite, run_signature, save

    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        frame = pd.DataFrame({"a": [1, 2]})
        five = {"seeds": [0, 1, 2, 3, 4]}
        one = {"seeds": [0]}

        save(directory, "demo", {"summary": frame}, params=five)
        print(f"  wrote canonical for {run_signature(five)}")

        try:
            check_overwrite(directory, "demo", one)
        except SystemExit:
            print(f"  refused to overwrite it with {run_signature(one)}")
        else:
            raise AssertionError("a differently-parameterised run was allowed to overwrite")

        # Same parameters must still overwrite freely -- that is how results regenerate.
        check_overwrite(directory, "demo", five)
        # And --force must win.
        check_overwrite(directory, "demo", one, force=True)
        print("  same-params re-run allowed; --force allowed")

        archived = sorted(p.name for p in directory.glob("demo_*__*.csv"))
        assert archived, "the archived per-signature copy was not written"
        print(f"  archived: {archived}")


def main() -> None:
    tests = [
        test_no_experiment_writes_a_file_to_the_shared_root,
        test_every_experiment_can_be_pointed_at_its_populations,
        test_output_dir_separates_datasets,
        test_shap_writes_one_file_per_seed,
        test_no_dataset_specific_column_names_in_experiments,
        test_canonical_results_are_guarded_against_a_different_run,
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
        except Exception as exc:                      # a crash is a failure, not an abort
            failures += 1
            print(f"  ERROR: {type(exc).__name__}: {exc}")

    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
