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
    acs:MS:RAC1P       ...protected on race instead of the default sex
"""

from .base import DatasetLoader, FairnessDataset

__all__ = ["DatasetLoader", "FairnessDataset", "build", "AVAILABLE"]

AVAILABLE = ("adult", "acs[:STATE[,STATE...]][:ATTRIBUTE]", "hmda[:STATE:ATTRIBUTE[:PURPOSE]]",
             "compas[:race|sex]", "lawschool[:race|male]", "dutch", "taiwan",
             "ipums:COUNTRY:YEAR:SEX:THRESHOLD", "acsemp:STATE", "acscov:STATE")


def build(name: str) -> DatasetLoader:
    """Resolve a dataset name to a loader.

    Args:
        name: ``"adult"``, or ``"acs"`` optionally suffixed with ``:`` and a
            comma-separated list of two-letter state codes, optionally followed by
            a second ``:`` and the column to protect (default ``SEX``), optionally
            followed by a third ``:`` and the income cutoff in dollars
            (default ``50000``). ``"hmda"`` takes a state and a protected column.
    """
    key, _, argument = name.partition(":")
    key = key.strip().lower()

    if key == "adult":
        from .adult import AdultLoader

        return AdultLoader()

    if key == "acs":
        from .acs import PROTECTED, ACSIncomeLoader

        state_part, _, rest = argument.partition(":")
        attribute, _, rest = rest.partition(":")
        threshold, _, year = rest.partition(":")
        states = [s.strip().upper() for s in state_part.split(",") if s.strip()]
        options = {"threshold": int(threshold)} if threshold.strip() else {}
        # Survey year as an optional fourth segment ("acs:TX:SEX:50000:2014"), because the
        # cross-year design needs the same state at different wealth levels and the year is
        # part of the population's identity -- the loader's name already carries it.
        if year.strip():
            options["year"] = year.strip()
        return ACSIncomeLoader(
            states=states or None,
            protected=attribute.strip().upper() or PROTECTED,
            **options,
        )

    if key == "hmda":
        # Imported lazily, inside the branch that asks for it, for the same reason as the
        # ACS loader: this is individual work excluded from the submission bundle, and the
        # course code must neither import nor need it.
        from .hmda import RACE, HMDALoader

        state_part, _, rest = argument.partition(":")
        attribute, _, purpose = rest.partition(":")
        return HMDALoader(
            state=state_part.strip().upper() or "MS",
            protected=attribute.strip() or RACE,
            purpose=purpose.strip() or None,
        )

    if key == "compas":
        # Lazily imported for the same reason as ACS and HMDA: individual work, excluded
        # from the submission bundle, and the course code must neither import nor need it.
        from .compas import RACE as COMPAS_RACE, CompasLoader

        return CompasLoader(protected=argument.strip() or COMPAS_RACE)

    if key == "lawschool":
        from .lawschool import RACE as LAW_RACE, LawSchoolLoader

        return LawSchoolLoader(protected=argument.strip() or LAW_RACE)

    if key in ("acsemp", "acscov"):
        # Lazily imported like the other individual-work loaders.
        from .acs_tasks import ACSTaskLoader

        state, _, rest = argument.partition(":")
        attribute, _, year = rest.partition(":")
        return ACSTaskLoader(
            "employment" if key == "acsemp" else "coverage",
            state.strip().upper() or "AL",
            year=year.strip() or "2018",
            protected=attribute.strip().upper() or "SEX",
        )

    if key == "ipums":
        # Lazily imported like ACS and HMDA: individual work, excluded from the
        # submission bundle, and the course code must neither import nor need it.
        from .ipums import IPUMSIncomeLoader

        country, _, rest = argument.partition(":")
        year, _, rest = rest.partition(":")
        attribute, _, threshold = rest.partition(":")
        return IPUMSIncomeLoader(
            country.strip().upper(),
            year.strip(),
            protected=attribute.strip().upper() or "SEX",
            threshold=int(threshold) if threshold.strip() else None,
        )

    if key == "taiwan":
        from .taiwan import TaiwanCreditLoader

        return TaiwanCreditLoader()

    if key == "dutch":
        from .dutch import DutchLoader

        return DutchLoader()

    raise KeyError(f"unknown dataset '{name}'; available: {AVAILABLE}")
