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

# Analysers whose population list IS the pre-registration. The guard below exists so that no
# module has its populations hardcoded *as a default a caller cannot change*; these are the
# opposite case. `analyse_sealed` names the eight populations its prediction was sealed over,
# `analyse_attribute_aware` the nine its bar was set against, and `analyse_resealed` the ten
# fresh states the monotone rule was re-sealed on, each committed before the arms existed.
# Making any of them configurable would let a later caller quietly change what was predicted,
# which is the failure the seal exists to prevent. `make_figures` renders whatever the
# analysers produced and selects nothing.
PREREGISTERED = {
    "analyse_sealed.py", "analyse_attribute_aware.py", "analyse_dense.py",
    "analyse_magnitude.py", "analyse_uncertainty_crossover.py", "make_figures.py",
    "analyse_resealed.py", "analyse_residual.py", "analyse_sealed_magnitude.py",
    "analyse_shapes.py", "analyse_race_shapes.py", "analyse_ipums_sealed.py",
}


class Skipped(Exception):
    """Raised by a test whose subject is absent from this copy of the project."""


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
        if path.name not in EXEMPT and path.name not in PREREGISTERED
        and "def main(" in path.read_text()
        and not any(flag in path.read_text() for flag in ('"--dataset"', '"--states"'))
    ]
    print(f"  {len([p for p in EXPERIMENTS if p.name not in EXEMPT])} runnable modules")
    assert not missing, f"no --dataset flag: {missing}"


def test_output_dir_separates_datasets() -> None:
    """Adult keeps the flat paths; every other dataset gets its own subdirectory.

    This is the original per-dataset guarantee, which is unchanged by the course/research
    split -- two datasets still must not share a directory. Where they now *live* is a
    separate invariant, checked below.
    """
    from src.results_io import output_dir

    adult = output_dir("adult")
    one = output_dir("acs_income_wy_2018")
    two = output_dir("acs_income_wy_2018_rac1p")
    print(f"  adult -> {adult.relative_to(ROOT)}/")
    print(f"  others -> {one.relative_to(ROOT)}/, {two.relative_to(ROOT)}/")
    assert adult == RESULTS, "adult must keep the flat results/ paths"
    assert len({adult, one, two}) == 3, "datasets must not share an output directory"
    assert one.parent == two.parent, "non-Adult datasets belong under one common root"


def test_course_and_research_results_cannot_reach_each_other() -> None:
    """The two roots must be disjoint, in both directions.

    The submission bundle is built by excluding ``research/`` wholesale, so the split is
    load-bearing in a way the earlier dataset split was not. A course result that landed
    under ``research/`` would be dropped from the submission; a research result that
    landed in ``results/`` would be submitted as team work. Neither fails loudly -- the
    first shows up as a missing file in a zip nobody re-opens, the second as an extra
    file nobody notices -- so the invariant is asserted rather than trusted.

    This is the fourth iteration of this routing rule. The previous three each shipped a
    silent overwrite.
    """
    from src.results_io import (
        RESEARCH_RESULTS_DIR,
        RESULTS_DIR,
        is_course_dataset,
        output_dir,
        research_dir,
    )

    course = output_dir("adult")
    print(f"  adult -> {course.relative_to(ROOT)}")
    assert course == RESULTS_DIR
    assert RESEARCH_RESULTS_DIR not in course.parents and course != RESEARCH_RESULTS_DIR, (
        "a course dataset was routed into research/, where the bundle would drop it"
    )

    for name in ["acs_income_ms_2018", "acs_income_ms_2018_rac1p", "acs_income_ca_2018"]:
        path = output_dir(name)
        assert not is_course_dataset(name)
        assert RESEARCH_RESULTS_DIR in path.parents, f"{name} escaped research/"
        assert path != RESULTS_DIR and RESULTS_DIR not in [path, *path.parents][:2], (
            f"{name} was routed into the submitted results root"
        )

    sweep = research_dir("sweep")
    assert RESEARCH_RESULTS_DIR in sweep.parents, "cross-population output escaped research/"
    print(f"  acs/sweep -> {sweep.relative_to(ROOT)}")

    # And the two roots must not nest, or "exclude research/" would also exclude results/.
    assert RESULTS_DIR not in RESEARCH_RESULTS_DIR.parents
    assert RESEARCH_RESULTS_DIR not in RESULTS_DIR.parents


def test_no_research_artefacts_are_left_in_the_submitted_results_root() -> None:
    """Nothing under ``results/`` may belong to a non-Adult population.

    Guards the migration itself, not the routing rule: the files were moved by hand, and
    one left behind would be shipped in the submission as though the team produced it.
    """
    strays = sorted(
        p.name for p in RESULTS.iterdir()
        if p.name.startswith("acs") or (p.is_dir() and p.name == "sweep")
    )
    print(f"  {len(list(RESULTS.iterdir()))} entries under results/")
    assert not strays, f"research artefacts still in the submitted results root: {strays}"


def test_dataset_name_distinguishes_the_protected_attribute() -> None:
    """Two configurations of one state must not share an output directory.

    ``output_dir`` namespaces by ``dataset.name``, so anything the name omits is
    invisible to it. Protecting race instead of sex changes the features, the groups
    and every metric downstream -- but it samples the same rows, so a name built from
    states and year alone is identical for both, and the second run silently overwrites
    the first. This is the same failure as the ACS-over-Adult clobber, one level down,
    and the guard in ``results_io`` cannot catch it: that compares CLI parameters, and
    these two runs differ in neither.
    """
    try:
        from src.datasets.acs import ACSIncomeLoader
    except ModuleNotFoundError:
        # The ACS loader is individual research work and is excluded from the course
        # submission bundle, so this invariant has nothing to check there. Skipping is
        # reported as a skip rather than a pass: a suite that prints PASS for a test it
        # did not run is worse than one that fails.
        raise Skipped("src/datasets/acs.py is not part of this bundle")

    from src.results_io import output_dir

    sex = ACSIncomeLoader(states=["MS"])
    race = ACSIncomeLoader(states=["MS"], protected="RAC1P")
    print(f"  sex -> {sex.name}\n  race -> {race.name}")
    assert sex.name != race.name, "protected attribute is missing from the dataset name"
    assert output_dir(sex.name) != output_dir(race.name)

    # The default must stay unsuffixed, or every committed ACS result is orphaned.
    assert sex.name == "acs_income_ms_2018", f"committed paths would move: {sex.name}"

    try:
        ACSIncomeLoader(states=["MS"], protected="AGEP")
    except KeyError:
        print("  unsupported attribute rejected")
    else:
        raise AssertionError("an unsupported protected attribute was accepted")


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
        test_course_and_research_results_cannot_reach_each_other,
        test_no_research_artefacts_are_left_in_the_submitted_results_root,
        test_dataset_name_distinguishes_the_protected_attribute,
        test_shap_writes_one_file_per_seed,
        test_no_dataset_specific_column_names_in_experiments,
        test_canonical_results_are_guarded_against_a_different_run,
    ]
    failures = skipped = 0
    for test in tests:
        print(f"\n{test.__name__}")
        try:
            test()
            print("  PASS")
        except Skipped as exc:
            skipped += 1
            print(f"  SKIP: {exc}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL: {exc}")
        except Exception as exc:                      # a crash is a failure, not an abort
            failures += 1
            print(f"  ERROR: {type(exc).__name__}: {exc}")

    ran = len(tests) - skipped
    tail = f" ({skipped} skipped)" if skipped else ""
    print(f"\n{ran - failures}/{ran} passed{tail}")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
