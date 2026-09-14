"""Domain-модель полевого наблюдения пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any, Mapping

from .geometry import (
    copy_geojson_geometry,
    parse_geojson_geometry,
    validate_geojson_geometry,
)
from .parsing import (
    optional_bool,
    optional_float,
    optional_int,
    optional_string,
    required_bool,
    required_datetime,
    required_string,
    string_tuple,
)


@dataclass(frozen=True, slots=True)
class Observation:
    """Положительное или отрицательное полевое наблюдение одного поиска."""

    observation_id: str
    timestamp: datetime
    geometry: Mapping[str, Any]
    target_species_id: str
    found_target_species: bool
    user_id: str | None = None
    species_confidence_pct: float | None = None
    count: int | None = None
    photo_ref: str | None = None
    searched_minutes: float | None = None
    searched_area_m2_estimate: float | None = None
    elevation_m: float | None = None
    aspect_deg: float | None = None
    forest_type: str | None = None
    dominant_trees: tuple[str, ...] = ()
    secondary_trees: tuple[str, ...] = ()
    moss_present: bool | None = None
    blueberry_present: bool | None = None
    heather_present: bool | None = None
    nettle_present: bool | None = None
    blackberry_present: bool | None = None
    grass_density_class: str | None = None
    soil_surface_moisture_class: str | None = None
    soil_moisture_5cm_class: str | None = None
    canopy_density_pct: float | None = None
    forest_maturity_class: str | None = None
    disturbance_class: str | None = None
    other_mushrooms_found: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.observation_id, "observation_id")
        _validate_aware_datetime(self.timestamp, "timestamp")
        validate_geojson_geometry(self.geometry)
        _require_non_empty(self.target_species_id, "target_species_id")
        _validate_optional_string(self.user_id, "user_id")
        _validate_optional_percentage(
            self.species_confidence_pct,
            "species_confidence_pct",
        )
        _validate_optional_non_negative_int(self.count, "count")
        _validate_optional_string(self.photo_ref, "photo_ref")
        _validate_optional_non_negative_number(
            self.searched_minutes,
            "searched_minutes",
        )
        _validate_optional_non_negative_number(
            self.searched_area_m2_estimate,
            "searched_area_m2_estimate",
        )
        _validate_optional_number(self.elevation_m, "elevation_m")
        _validate_optional_number(self.aspect_deg, "aspect_deg")
        if self.aspect_deg is not None and not 0 <= self.aspect_deg < 360:
            raise ValueError("aspect_deg must be in range [0, 360)")

        _validate_optional_string(self.forest_type, "forest_type")
        _validate_string_tuple(self.dominant_trees, "dominant_trees")
        _validate_string_tuple(self.secondary_trees, "secondary_trees")
        _validate_optional_string(self.grass_density_class, "grass_density_class")
        _validate_optional_string(
            self.soil_surface_moisture_class,
            "soil_surface_moisture_class",
        )
        _validate_optional_string(
            self.soil_moisture_5cm_class,
            "soil_moisture_5cm_class",
        )
        _validate_optional_percentage(self.canopy_density_pct, "canopy_density_pct")
        _validate_optional_string(self.forest_maturity_class, "forest_maturity_class")
        _validate_optional_string(self.disturbance_class, "disturbance_class")
        _validate_string_tuple(self.other_mushrooms_found, "other_mushrooms_found")
        _validate_string_tuple(self.notes, "notes")

        if not self.found_target_species:
            if self.species_confidence_pct is not None:
                raise ValueError(
                    "species_confidence_pct requires found_target_species=true"
                )
            if self.count not in (None, 0):
                raise ValueError(
                    "count must be 0 or null when found_target_species=false"
                )
        elif self.count == 0:
            raise ValueError(
                "count must be positive or null when found_target_species=true"
            )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает JSON-совместимое представление наблюдения."""

        return {
            "observation_id": self.observation_id,
            "timestamp": self.timestamp.isoformat(),
            "geometry": copy_geojson_geometry(self.geometry),
            "target_species_id": self.target_species_id,
            "found_target_species": self.found_target_species,
            "user_id": self.user_id,
            "species_confidence_pct": self.species_confidence_pct,
            "count": self.count,
            "photo_ref": self.photo_ref,
            "searched_minutes": self.searched_minutes,
            "searched_area_m2_estimate": self.searched_area_m2_estimate,
            "elevation_m": self.elevation_m,
            "aspect_deg": self.aspect_deg,
            "forest_type": self.forest_type,
            "dominant_trees": list(self.dominant_trees),
            "secondary_trees": list(self.secondary_trees),
            "moss_present": self.moss_present,
            "blueberry_present": self.blueberry_present,
            "heather_present": self.heather_present,
            "nettle_present": self.nettle_present,
            "blackberry_present": self.blackberry_present,
            "grass_density_class": self.grass_density_class,
            "soil_surface_moisture_class": self.soil_surface_moisture_class,
            "soil_moisture_5cm_class": self.soil_moisture_5cm_class,
            "canopy_density_pct": self.canopy_density_pct,
            "forest_maturity_class": self.forest_maturity_class,
            "disturbance_class": self.disturbance_class,
            "other_mushrooms_found": list(self.other_mushrooms_found),
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Observation":
        """Создаёт наблюдение из JSON-подобного mapping."""

        return cls(
            observation_id=required_string(data["observation_id"], "observation_id"),
            timestamp=required_datetime(data["timestamp"], "timestamp"),
            geometry=parse_geojson_geometry(data["geometry"]),
            target_species_id=required_string(
                data["target_species_id"],
                "target_species_id",
            ),
            found_target_species=required_bool(
                data["found_target_species"],
                "found_target_species",
            ),
            user_id=optional_string(data.get("user_id"), "user_id"),
            species_confidence_pct=optional_float(
                data.get("species_confidence_pct"),
                "species_confidence_pct",
            ),
            count=optional_int(data.get("count"), "count"),
            photo_ref=optional_string(data.get("photo_ref"), "photo_ref"),
            searched_minutes=optional_float(
                data.get("searched_minutes"),
                "searched_minutes",
            ),
            searched_area_m2_estimate=optional_float(
                data.get("searched_area_m2_estimate"),
                "searched_area_m2_estimate",
            ),
            elevation_m=optional_float(data.get("elevation_m"), "elevation_m"),
            aspect_deg=optional_float(data.get("aspect_deg"), "aspect_deg"),
            forest_type=optional_string(data.get("forest_type"), "forest_type"),
            dominant_trees=string_tuple(
                data.get("dominant_trees", ()),
                "dominant_trees",
            ),
            secondary_trees=string_tuple(
                data.get("secondary_trees", ()),
                "secondary_trees",
            ),
            moss_present=optional_bool(data.get("moss_present"), "moss_present"),
            blueberry_present=optional_bool(
                data.get("blueberry_present"),
                "blueberry_present",
            ),
            heather_present=optional_bool(
                data.get("heather_present"),
                "heather_present",
            ),
            nettle_present=optional_bool(
                data.get("nettle_present"),
                "nettle_present",
            ),
            blackberry_present=optional_bool(
                data.get("blackberry_present"),
                "blackberry_present",
            ),
            grass_density_class=optional_string(
                data.get("grass_density_class"),
                "grass_density_class",
            ),
            soil_surface_moisture_class=optional_string(
                data.get("soil_surface_moisture_class"),
                "soil_surface_moisture_class",
            ),
            soil_moisture_5cm_class=optional_string(
                data.get("soil_moisture_5cm_class"),
                "soil_moisture_5cm_class",
            ),
            canopy_density_pct=optional_float(
                data.get("canopy_density_pct"),
                "canopy_density_pct",
            ),
            forest_maturity_class=optional_string(
                data.get("forest_maturity_class"),
                "forest_maturity_class",
            ),
            disturbance_class=optional_string(
                data.get("disturbance_class"),
                "disturbance_class",
            ),
            other_mushrooms_found=string_tuple(
                data.get("other_mushrooms_found", ()),
                "other_mushrooms_found",
            ),
            notes=string_tuple(data.get("notes", ()), "notes"),
        )


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _validate_aware_datetime(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone information")


def _validate_optional_number(value: float | None, field_name: str) -> None:
    if value is not None and not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _validate_optional_non_negative_number(
    value: float | None,
    field_name: str,
) -> None:
    _validate_optional_number(value, field_name)
    if value is not None and value < 0:
        raise ValueError(f"{field_name} must be >= 0")


def _validate_optional_non_negative_int(value: int | None, field_name: str) -> None:
    if value is not None and value < 0:
        raise ValueError(f"{field_name} must be >= 0")


def _validate_optional_percentage(value: float | None, field_name: str) -> None:
    _validate_optional_number(value, field_name)
    if value is not None and not 0 <= value <= 100:
        raise ValueError(f"{field_name} must be between 0 and 100")


def _validate_optional_string(value: str | None, field_name: str) -> None:
    if value is not None and not value.strip():
        raise ValueError(f"{field_name} must not be empty when provided")


def _validate_string_tuple(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        if not value.strip():
            raise ValueError(f"{field_name} must not contain empty values")
