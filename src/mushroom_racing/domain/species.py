"""Domain-модель экологического профиля вида гриба."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

from .evidence import EvidenceRecord
from .parsing import (
    int_tuple,
    optional_float,
    optional_int,
    required_string,
    string_tuple,
)


@dataclass(frozen=True, slots=True)
class SpeciesProfile:
    """Стабильное описание экологических требований одного вида."""

    species_id: str
    latin_name: str
    common_name: str
    german_name: str
    host_trees: tuple[str, ...] = ()
    preferred_soils: tuple[str, ...] = ()
    preferred_ph_min: float | None = None
    preferred_ph_max: float | None = None
    preferred_geologies: tuple[str, ...] = ()
    preferred_elevation_min_m: float | None = None
    preferred_elevation_max_m: float | None = None
    preferred_temperature_min_c: float | None = None
    preferred_temperature_max_c: float | None = None
    preferred_season_months: tuple[int, ...] = ()
    rain_response_min_days: int | None = None
    rain_response_max_days: int | None = None
    positive_indicator_plants: tuple[str, ...] = ()
    negative_indicator_plants: tuple[str, ...] = ()
    habitat_notes: tuple[str, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.species_id, "species_id")
        _require_non_empty(self.latin_name, "latin_name")
        _require_non_empty(self.common_name, "common_name")
        _require_non_empty(self.german_name, "german_name")

        _validate_string_tuple(self.host_trees, "host_trees")
        _validate_string_tuple(self.preferred_soils, "preferred_soils")
        _validate_string_tuple(self.preferred_geologies, "preferred_geologies")
        _validate_string_tuple(
            self.positive_indicator_plants,
            "positive_indicator_plants",
        )
        _validate_string_tuple(
            self.negative_indicator_plants,
            "negative_indicator_plants",
        )
        _validate_string_tuple(self.habitat_notes, "habitat_notes")

        _validate_optional_range(
            self.preferred_ph_min,
            self.preferred_ph_max,
            "preferred_ph",
        )
        if self.preferred_ph_min is not None:
            if not 0 <= self.preferred_ph_min <= 14:
                raise ValueError("preferred_ph_min must be between 0 and 14")
            if not 0 <= self.preferred_ph_max <= 14:
                raise ValueError("preferred_ph_max must be between 0 and 14")

        _validate_optional_range(
            self.preferred_elevation_min_m,
            self.preferred_elevation_max_m,
            "preferred_elevation_m",
        )
        _validate_optional_range(
            self.preferred_temperature_min_c,
            self.preferred_temperature_max_c,
            "preferred_temperature_c",
        )
        _validate_optional_int_range(
            self.rain_response_min_days,
            self.rain_response_max_days,
            "rain_response_days",
            minimum_allowed=0,
        )

        if len(set(self.preferred_season_months)) != len(
            self.preferred_season_months
        ):
            raise ValueError("preferred_season_months must not contain duplicates")
        for month in self.preferred_season_months:
            if month < 1 or month > 12:
                raise ValueError("preferred_season_months must contain values 1..12")

    def to_dict(self) -> dict[str, Any]:
        """Возвращает JSON-совместимое представление профиля."""

        return {
            "species_id": self.species_id,
            "latin_name": self.latin_name,
            "common_name": self.common_name,
            "german_name": self.german_name,
            "host_trees": list(self.host_trees),
            "preferred_soils": list(self.preferred_soils),
            "preferred_ph_min": self.preferred_ph_min,
            "preferred_ph_max": self.preferred_ph_max,
            "preferred_geologies": list(self.preferred_geologies),
            "preferred_elevation_min_m": self.preferred_elevation_min_m,
            "preferred_elevation_max_m": self.preferred_elevation_max_m,
            "preferred_temperature_min_c": self.preferred_temperature_min_c,
            "preferred_temperature_max_c": self.preferred_temperature_max_c,
            "preferred_season_months": list(self.preferred_season_months),
            "rain_response_min_days": self.rain_response_min_days,
            "rain_response_max_days": self.rain_response_max_days,
            "positive_indicator_plants": list(self.positive_indicator_plants),
            "negative_indicator_plants": list(self.negative_indicator_plants),
            "habitat_notes": list(self.habitat_notes),
            "evidence": [item.to_dict() for item in self.evidence],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SpeciesProfile":
        """Создаёт профиль из JSON-подобного mapping."""

        return cls(
            species_id=required_string(data["species_id"], "species_id"),
            latin_name=required_string(data["latin_name"], "latin_name"),
            common_name=required_string(data["common_name"], "common_name"),
            german_name=required_string(data["german_name"], "german_name"),
            host_trees=string_tuple(data.get("host_trees", ()), "host_trees"),
            preferred_soils=string_tuple(
                data.get("preferred_soils", ()),
                "preferred_soils",
            ),
            preferred_ph_min=optional_float(
                data.get("preferred_ph_min"),
                "preferred_ph_min",
            ),
            preferred_ph_max=optional_float(
                data.get("preferred_ph_max"),
                "preferred_ph_max",
            ),
            preferred_geologies=string_tuple(
                data.get("preferred_geologies", ()),
                "preferred_geologies",
            ),
            preferred_elevation_min_m=optional_float(
                data.get("preferred_elevation_min_m"),
                "preferred_elevation_min_m",
            ),
            preferred_elevation_max_m=optional_float(
                data.get("preferred_elevation_max_m"),
                "preferred_elevation_max_m",
            ),
            preferred_temperature_min_c=optional_float(
                data.get("preferred_temperature_min_c"),
                "preferred_temperature_min_c",
            ),
            preferred_temperature_max_c=optional_float(
                data.get("preferred_temperature_max_c"),
                "preferred_temperature_max_c",
            ),
            preferred_season_months=int_tuple(
                data.get("preferred_season_months", ()),
                "preferred_season_months",
            ),
            rain_response_min_days=optional_int(
                data.get("rain_response_min_days"),
                "rain_response_min_days",
            ),
            rain_response_max_days=optional_int(
                data.get("rain_response_max_days"),
                "rain_response_max_days",
            ),
            positive_indicator_plants=string_tuple(
                data.get("positive_indicator_plants", ()),
                "positive_indicator_plants",
            ),
            negative_indicator_plants=string_tuple(
                data.get("negative_indicator_plants", ()),
                "negative_indicator_plants",
            ),
            habitat_notes=string_tuple(
                data.get("habitat_notes", ()),
                "habitat_notes",
            ),
            evidence=tuple(
                EvidenceRecord.from_dict(item)
                for item in data.get("evidence", ())
            ),
        )


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _validate_string_tuple(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        if not value.strip():
            raise ValueError(f"{field_name} must not contain empty values")


def _validate_optional_range(
    minimum: float | None,
    maximum: float | None,
    field_name: str,
) -> None:
    if (minimum is None) != (maximum is None):
        raise ValueError(f"{field_name} requires both minimum and maximum")
    if minimum is None or maximum is None:
        return
    if not isfinite(minimum) or not isfinite(maximum):
        raise ValueError(f"{field_name} values must be finite")
    if minimum > maximum:
        raise ValueError(f"{field_name} minimum must not exceed maximum")


def _validate_optional_int_range(
    minimum: int | None,
    maximum: int | None,
    field_name: str,
    minimum_allowed: int,
) -> None:
    if (minimum is None) != (maximum is None):
        raise ValueError(f"{field_name} requires both minimum and maximum")
    if minimum is None or maximum is None:
        return
    if minimum < minimum_allowed or maximum < minimum_allowed:
        raise ValueError(f"{field_name} values must be >= {minimum_allowed}")
    if minimum > maximum:
        raise ValueError(f"{field_name} minimum must not exceed maximum")
