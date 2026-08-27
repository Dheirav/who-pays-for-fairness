#!/usr/bin/env python3
"""Run many arms concurrently, with each worker pinned to one BLAS thread.

Two measured facts motivate this, both from 27 Aug:

* **One thread per worker is faster than four, dramatically so on HMDA.** The reduction
  fits its base learner thousands of times on small matrices; HMDA's one-hot encoding makes
  each one wide but the arithmetic per call trivial, so spawning and synchronising four
  BLAS threads costs an order of magnitude more than it saves. Measured on one market:
  43.05 s at four threads against 4.53 s at one, reproducibly. ACS is unaffected (3.71 s
  against 3.59 s), so pinning costs nothing there and wins hugely here.
* **Concurrency across arms is near-linear.** Four ACS arms take 19.32 s one at a time and
  4.93 s together: 3.9x on four cores.

Before this existed every run in the project was sequential with threading left on, which
cost roughly an order of magnitude on lending work and three-quarters of the machine on
everything else.

The worker count defaults to the core count. It is deliberately not raised beyond it: the
4-processor cap in this machine's .wslconfig is a considered choice, documented there.

    python scripts/run_many.py --specs acs:WY acs:VT --seeds 0 1 2 3 4
    python scripts/run_many.py --file specs.txt --workers 4
"""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")

# One thread per worker. Set for the child only; the parent's environment is untouched.
PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
          "NUMEXPR_NUM_THREADS": "1"}


def run_one(spec: str, seeds: list[str], extra: list[str]) -> tuple[str, bool, float, str]:
    env = {**os.environ, **PINNED}
    start = time.time()
    proc = subprocess.run(
        [PY, "-m", "src.experiments.run_levelling_up", "--dataset", spec,
         "--seeds", *seeds, *extra],
        cwd=ROOT, capture_output=True, text=True, env=env)
    note = ""
    if proc.returncode != 0:
        lines = (proc.stderr or proc.stdout).strip().splitlines()
        note = lines[-1][:150] if lines else "no output"
    return spec, proc.returncode == 0, time.time() - start, note


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", nargs="*", default=[])
    ap.add_argument("--file", help="file of dataset specs, one per line, # for comments")
    ap.add_argument("--seeds", nargs="+", default=["0", "1", "2", "3", "4"])
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--model", default=None, help="passed through, e.g. logistic_regression@0.42")
    args, unknown = ap.parse_known_args()

    specs = list(args.specs)
    if args.file:
        for line in pathlib.Path(args.file).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                specs.append(line)
    if not specs:
        sys.exit("no specs given")

    extra = list(unknown) + (["--model", args.model] if args.model else [])
    print(f"{len(specs)} arms, {args.workers} workers, 1 BLAS thread each", flush=True)
    t0 = time.time()
    ok = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, (spec, good, secs, note) in enumerate(
                pool.map(lambda s: run_one(s, args.seeds, extra), specs), 1):
            ok += good
            print(f"  [{i}/{len(specs)}] {spec:<34} {'ok' if good else 'FAIL'} {secs:6.0f}s"
                  + (f"  {note}" if note else ""), flush=True)
    print(f"\n{ok}/{len(specs)} ok in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
