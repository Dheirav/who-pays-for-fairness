"""Checksum the input data every result was computed from.

The review council's replication and systems panels made the same point from different
sides: "all seven data sources are public" is not a snapshot. folktables downloads ACS
PUMS per state on first use and PUMS files are revised in place; the 2022-inversion
episode is this project's own proof that a byte-different vintage is a different task.
This freezes what was actually on disk: one row per input file, SHA-256 and size, so an
independent run can verify it is reading the same bytes --- or know precisely that it
is not.

Run:  python scripts/data_manifest.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "research" / "data-manifest.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not DATA.is_dir():
        sys.exit(f"no data directory at {DATA}")
    rows = [{"file": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
             "sha256": sha256(path)}
            for path in sorted(DATA.rglob("*")) if path.is_file()]
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT, index=False)
    print(frame.to_string(index=False, max_colwidth=60))
    print(f"\n{len(frame)} files, {frame['bytes'].sum() / 1e9:.2f} GB")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
