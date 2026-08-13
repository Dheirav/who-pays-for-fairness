"""Build the course submission bundle from the repository, by exclusion.

The previous bundle was assembled by hand and went stale within four hours. It was
built at 20:38 and three commits landed after it, one of which fixed two real bugs in
submitted code and rebuilt both deliverables -- so the zip on disk contained a
superseded PDF, a superseded deck, the pre-fix ``metrics.py`` with the
``equalized_odds_difference`` NaN-ordering bug, and none of the tests pinning the fix.
Nothing announced this. It looked complete.

So the bundle is defined here as a *rule* rather than a file list: everything tracked by
git, minus what is explicitly excluded. A rule cannot silently fall behind the
repository, and anything added later is included by default rather than forgotten.

**What is excluded, and why:**

* ``research/`` -- individual work done after the deliverables were finalised. This is a
  team project completed by one person; the course requires the Adult work, and folding
  the rest in would credit the team for work it did not do. See ``research/README.md``.
* development scaffolding -- ``.git``, caches, the virtualenv.

``src/datasets/acs.py`` and the two cross-population analyses are individual work that
cannot be *moved* into ``research/`` -- they are inside the package -- but they can be
excluded from the bundle, and are. ``datasets.build`` imports the ACS loader lazily,
inside the branch that requests it, so the course code neither imports nor needs it.
Checked by unpacking the bundle without them and running the course suites, rather than
reasoned about: the first version of this file asserted the opposite and was wrong.

Usage:
    python -m scripts.build_submission
    python -m scripts.build_submission --output ~/Code/submission.zip --check
"""

from __future__ import annotations

import argparse
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Directories whose entire contents stay out of the bundle.
EXCLUDED_TREES = ("research/",)

# Individual research work that has to live inside the package for imports to resolve,
# and so cannot be moved into research/. It can still be excluded from the bundle:
# `datasets.build` imports the ACS loader lazily, inside the branch that asks for it, so
# its absence costs the course code nothing and `build("acs:WY")` simply raises. Verified
# by unpacking the bundle without these three and running the course suites.
EXCLUDED_FILES = (
    "src/datasets/acs.py",
    "src/datasets/hmda.py",
    "src/experiments/analyse_sweep.py",
    "src/experiments/analyse_arms.py",
    "src/experiments/analyse_conflict.py",
    "src/experiments/analyse_attribution.py",
    "src/experiments/analyse_levelling_up.py",
    "src/experiments/analyse_threshold.py",
    "src/experiments/analyse_ratio.py",
    "src/experiments/run_baselines.py",
    "src/baselines.py",
    "src/experiments/run_injection.py",
    "src/experiments/run_collinear.py",
    "src/experiments/run_levelling_up.py",
    "src/levelling_up.py",
    "tests/test_documented_claims.py",
    "tests/test_acs_threshold.py",
)

# Untracked by git (``data/`` is gitignored as a re-downloadable cache) but present in
# the previously submitted bundle, so it is included by default. Dropping it would change
# what is handed in -- a grader without network access would get a project that cannot
# run -- and that is not a change to make as a side effect of automating the build.
UNTRACKED_EXTRAS = ("data/adult.csv",)

# Files that must be present, or the bundle is not a submission. Checked rather than
# assumed, because the failure is silent: a bundle missing the report is still a
# perfectly valid zip.
REQUIRED = (
    "bias_mitigation_report.pdf",
    "bias_mitigation_plan.pptx",
    "README.md",
    "docs/README.md",
    "src/metrics.py",
    "results/ablation_summary.csv",
)


def tracked_files() -> list[str]:
    """Every file git tracks, which is the definition of "part of this project"."""
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line]


def is_excluded(path: str) -> bool:
    return path in EXCLUDED_FILES or any(
        path.startswith(tree) for tree in EXCLUDED_TREES
    )


def stale_against_head() -> list[str]:
    """Tracked files whose working copy differs from the last commit.

    A bundle built from a dirty tree cannot be reproduced from any commit, which is the
    property that makes the git history usable as an authorship record.
    """
    out = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    )
    paths = []
    for line in out.stdout.splitlines():
        if not line:
            continue
        # Renames are reported as "old -> new"; the destination is what would be
        # bundled, so exclusion must be judged on that rather than on where it came
        # from. Moving a file *into* research/ would otherwise read as a live change to
        # the submission.
        path = line[3:].split(" -> ")[-1]
        if not is_excluded(path):
            paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT.parent / "algorithmic-bias-mitigation-adult.zip")
    parser.add_argument("--check", action="store_true",
                        help="report what would be bundled without writing it")
    parser.add_argument("--no-data", action="store_true",
                        help="omit the cached dataset (re-downloadable via OpenML)")
    args = parser.parse_args()

    files = [f for f in tracked_files() if not is_excluded(f)]
    excluded = [f for f in tracked_files() if is_excluded(f)]

    if not args.no_data:
        for extra in UNTRACKED_EXTRAS:
            if (ROOT / extra).exists():
                files.append(extra)
            else:
                print(f"  note: {extra} absent; bundle will require a first-run download")

    missing = [name for name in REQUIRED if name not in files]
    if missing:
        raise SystemExit(f"refusing to build: required files absent -- {missing}")

    dirty = stale_against_head()
    if dirty:
        print(f"WARNING: {len(dirty)} uncommitted change(s) outside research/; the")
        print("         bundle will not correspond to any commit:")
        for name in dirty[:10]:
            print(f"           {name}")

    print(f"  {len(files)} files to bundle")
    print(f"  {len(excluded)} excluded as individual research work")
    if args.check:
        for name in sorted(excluded)[:8]:
            print(f"    excluded: {name}")
        print("  (--check: nothing written)")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in sorted(files):
            bundle.write(ROOT / name, arcname=name)

    size = args.output.stat().st_size / 1e6
    print(f"wrote {args.output}  ({size:.1f} MB, {len(files)} files)")


if __name__ == "__main__":
    main()
