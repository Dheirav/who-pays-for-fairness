"""Dataset loaders conforming to the FairnessDataset interface.

:func:`build` is the seam every experiment goes through, so adding a dataset means
adding a loader and a registry entry -- no experiment changes. That claim was made
when the interface was written and is only worth anything once a second dataset
exists to test it; ACS Income is that test.

Dataset names accept a suffix for loaders that take arguments, so a single
``--dataset`` string on the command line can select a population:

    adult              UCI Adult Census Income
    acs                ACS Income, California, 2018
    acs:WY             ACS Income, one state
    acs:CA,TX,NY       ACS Income, several states pooled
"""

from .base import DatasetLoader, FairnessDataset

__all__ = ["DatasetLoader", "FairnessDataset", "build", "AVAILABLE"]

AVAILABLE = ("adult", "acs[:STATE[,STATE...]]")


def build(name: str) -> DatasetLoader:
    """Resolve a dataset name to a loader.

    Args:
        name: ``"adult"``, or ``"acs"`` optionally suffixed with ``:`` and a
            comma-separated list of two-letter state codes.
    """
    key, _, argument = name.partition(":")
    key = key.strip().lower()

    if key == "adult":
        from .adult import AdultLoader

        return AdultLoader()

    if key == "acs":
        from .acs import ACSIncomeLoader

        states = [s.strip().upper() for s in argument.split(",") if s.strip()]
        return ACSIncomeLoader(states=states or None)

    raise KeyError(f"unknown dataset '{name}'; available: {AVAILABLE}")
