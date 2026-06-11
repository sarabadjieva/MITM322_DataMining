from dataclasses import dataclass
from functools import cache

from src.etl.helpers.text_utils import normalize_text
from src.etl.helpers.const_vals import ALIASES, TOTAL_LABELS, AREA_LABELS


@dataclass
class Territory:
    level: str | None
    district: str | None
    municipality: str | None


def canonical_area_name(name):
    name = normalize_text(name)
    if not name:
        return None
    return ALIASES.get(name, name)


def is_total_row(name):
    name = normalize_text(name)
    return bool(name and name in TOTAL_LABELS)


@cache
def classify_territory(name, current_district=None) -> Territory:
    name = normalize_text(name)

    if not name:
        return Territory(None, current_district, None)

    if name in TOTAL_LABELS:
        return Territory("country", None, None)

    if current_district is None and name in AREA_LABELS:
        return Territory("district", name, None)

    if current_district is not None and name in AREA_LABELS:
        return Territory("municipality", current_district, name)

    if current_district:
        return Territory("municipality", current_district, name)

    return Territory("unknown", None, name)


def territory_metric_row(year, name, metric, value):
    return {
        "year": year,
        "territory_raw": name,
        "territory_level": classify_territory(name).level,
        "metric": metric,
        "value": value,
    }
