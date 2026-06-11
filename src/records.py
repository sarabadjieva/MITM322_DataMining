from dataclasses import asdict, dataclass

@dataclass(slots=True)
class TerritoryMetricRecord:
    year: int
    territory_raw: str
    territory_level: str
    metric: str
    value: float

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class TerritoryMeasureRecord:
    year: int
    territory_raw: str
    territory_level: str
    measure: str
    value: float

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class AgeMetricRecord:
    group_name: str
    age_group: str
    year: int
    metric: str
    value: float

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class AgeMatrixRecord:
    year: int
    residence_group: str
    female_age_group: str
    male_age_group: str
    value: float

    def to_dict(self):
        return asdict(self)

def make_territory_metric_record(
        year,
        territory_raw,
        territory_level,
        metric,
        value):
    return TerritoryMetricRecord(
        year=year,
        territory_raw=territory_raw,
        territory_level=territory_level,
        metric=metric,
        value=value,
    )


def make_territory_measure_record(
        year,
        territory_raw,
        territory_level,
        measure,
        value):
    return TerritoryMeasureRecord(
        year=year,
        territory_raw=territory_raw,
        territory_level=territory_level,
        measure=measure,
        value=value
    )


def make_age_metric_record(
        group_name,
        age_group,
        year,
        metric,
        value):
    return AgeMetricRecord(
        group_name=group_name,
        age_group=age_group,
        year=year,
        metric=metric,
        value=value,
    )


def make_age_matrix_record(
        year,
        residence_group,
        female_age_group,
        male_age_group,
        value):
    return AgeMatrixRecord(
        year=year,
        residence_group=residence_group,
        female_age_group=female_age_group,
        male_age_group=male_age_group,
        value=value
    )