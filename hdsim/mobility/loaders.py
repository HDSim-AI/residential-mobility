"""PSID loaders.

No survey data ships with this package. PSID requires registration and agreement to its conditions
of use before download, so the loaders read files you obtain yourself.

    PSID    https://psidonline.isr.umich.edu

`load_example()` returns a family built into the package, which is enough for a first run without
any download.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from hdsim.core import Household, Member

from .config import label_for

HOUSEHOLD_KEY = "HOUSEID"
PERSON_KEY = "PERSONID"
TARGET = "MOVED_RECENTLY"


def _to_household(household_id: str, rows: list[dict]) -> Household:
    members = [
        Member(person_id=int(row.get(PERSON_KEY, i + 1)), record=row, label=label_for(row))
        for i, row in enumerate(sorted(rows, key=lambda r: r.get(PERSON_KEY, 0)))
    ]
    # Moving is a property of the family, not of each person, so any member carrying the flag
    # gives the household's answer.
    truth = None
    for row in rows:
        value = row.get(TARGET)
        if value is not None:
            try:
                truth = bool(int(float(value)))
            except (TypeError, ValueError):
                truth = bool(value)
            break
    return Household(household_id=str(household_id), members=members, ground_truth=truth)


def load_csv(path: str | Path, *, household_key: str = HOUSEHOLD_KEY,
             min_members: int = 1, max_households: int | None = None) -> list[Household]:
    """Read a person-level PSID extract and group it into families."""
    import pandas as pd

    frame = pd.read_csv(path, low_memory=False)
    if household_key not in frame.columns:
        raise KeyError(
            f"{household_key!r} is not a column in {path}. "
            f"Found: {', '.join(list(frame.columns)[:10])}..."
        )
    households = []
    for household_id, group in frame.groupby(household_key, sort=True):
        rows = group.where(group.notna(), None).to_dict("records")
        if len(rows) < min_members:
            continue
        households.append(_to_household(str(household_id), rows))
        if max_households and len(households) >= max_households:
            break
    return households


def load_psid(path: str | Path, **kwargs) -> list[Household]:
    """Load a prepared PSID panel extract."""
    return load_csv(path, **kwargs)


def load_jsonl(path: str | Path) -> Iterator[Household]:
    """Read families already in hdsim's own format, one JSON object per line."""
    for line in Path(path).read_text().splitlines():
        if line.strip():
            yield Household.from_dict(json.loads(line))


def load_example() -> Household:
    """A three-person renting family, for a first run without a download.

    Representative values, not a real record: no PSID data is redistributed here.
    """
    rows = [
        {"HOUSEID": "example", "PERSONID": 1, "AGE": 31, "SEX": 1, "RELATION_TO_HEAD": 1,
         "EMPLOYMENT_STATUS": 1, "WTR_COLLEGE_DEGREE": 1, "CURRENTLY_ENROLLED": 5,
         "HEALTH_SELF": 2, "HOMEOWN": 5, "YEARS_EDUCATION": 16},
        {"HOUSEID": "example", "PERSONID": 2, "AGE": 30, "SEX": 2, "RELATION_TO_HEAD": 2,
         "EMPLOYMENT_STATUS": 1, "WTR_COLLEGE_DEGREE": 1, "CURRENTLY_ENROLLED": 5,
         "HEALTH_SELF": 1, "HOMEOWN": 5, "YEARS_EDUCATION": 16},
        {"HOUSEID": "example", "PERSONID": 3, "AGE": 4, "SEX": 2, "RELATION_TO_HEAD": 3,
         "EMPLOYMENT_STATUS": None, "CURRENTLY_ENROLLED": 5, "HEALTH_SELF": 1, "HOMEOWN": 5},
    ]
    return _to_household("example", rows)
