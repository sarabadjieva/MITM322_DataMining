import const_vals as cvals
from text_utils import normalize_text
from dataclasses import dataclass

@dataclass
class Territory:
    level: str | None
    oblast: str | None
    municipality: str | None

def canonical_area_name(name):
    name = normalize_text(name)
    if not name:
        return None
    return cvals.ALIASES.get(name, name)

def is_total_row(name):
    name = normalize_text(name)
    return name in cvals.TOTAL_LABELS

def is_oblast_row(name):
    canon = canonical_area_name(name)
    return canon in cvals.AREA_LABELS

def classify_territory(name, current_oblast=None) -> Territory:
    name = normalize_text(name)
    if not name:
        return Territory(None, current_oblast, None)

    if name in cvals.TOTAL_LABELS:
        return Territory("country", None, None)

    if current_oblast is None and name in cvals.AREA_LABELS:
        return Territory("oblast", name, None)

    if current_oblast is not None and name in cvals.AREA_LABELS:
        return Territory("municipality", current_oblast, name)

    if current_oblast:
        return Territory("municipality", current_oblast, name)

    return Territory("unknown", None, name)