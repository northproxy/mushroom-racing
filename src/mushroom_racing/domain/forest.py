"""Domain-модель статического лесного участка."""

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
    optional_datetime,
    optional_float,
    optional_string,
    required_string,
    string_tuple,
)


@dataclass(frozen=True, slots=True)
class ForestSpot:
    """Статические характеристики одного лесного участка или sample cell."""

    spot_id: str
    name: str
    geometry: Mapping[str, Any]
    region: str
    country: str
    elevation_min_m: float | None = None
    elevation_max_m: float | None = None
    dominant_aspect_deg: float | None = None
    slope_deg: float | None = None
    forest_type: str | None = None
    tree_species: tuple[str, ...] = ()
    geology: str | None = None
    soil_type: str | None = None
    soil_ph: float | None = None
    nutrient_level: str | None = None
    canopy_density_pct: float | None = None
    forest_age_class: str | None = None
    disturbance_level: str | None = None
    nearest_stream_m: float | None = None
    protected_area: str | None = None
    collecting_allowed: bool | None = None
    legal_notes: tuple[str, ...] = ()
    access_notes: tuple[str, ...] = ()
    static_data_confidence: float | None = None
    last_updated: datetime | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.spot_id, "spot_id")
        _require_non_empty(self.name, "name")
        _require_non_empty(self.region, "region")
        _require_non_empty(self.country, "country")
        validate_geojson_geometry(self.geometry)
        _validate_optional_range(
            self.elevation_min_m,
            self.elevation_max_m,
            "elevation_m",
        )
        _validate_optional_number(self.dominant_aspect_deg, "dominant_aspect_deg")
        if self.dominant_aspect_deg is not None:
            if not 0 <= self.dominant_aspect_deg < 360:
                raise ValueError("dominant_aspect_deg must be in range [0, 360)")

        _validate_optional_number(self.slope_deg, "slope_deg")
        if self.slope_deg is not None and not 0 <= self.slope_deg <= 90:
            raise ValueError("slope_deg must be between 0 and 90")

        _validate_optional_string(self.forest_type, "forest_type")
        _validate_string_tuple(self.tree_species, "tree_species")
        _validate_optional_string(self.geology, "geology")
        _validate_optional_string(self.soil_type, "soil_type")
        _validate_optional_number(self.soil_ph, "soil_ph")
        if self.soil_ph is not None and not 0 <= self.soil_ph <= 14:
            raise ValueError("soil_ph must be between 0 and 14")

        _validate_optional_string(self.nutrient_level, "nutrient_level")
        _validate_optional_percentage(self.canopy_density_pct, "canopy_density_pct")
        _validate_optional_string(self.forest_age_class, "forest_age_class")
        _validate_optional_string(self.disturbance_level, "disturbance_level")

        _validate_optional_number(self.nearest_stream_m, "nearest_stream_m")
        if self.nearest_stream_m is not None and self.nearest_stream_m < 0:
            raise ValueError("nearest_stream_m must be >= 0")

        _validate_optional_string(self.protected_area, "protected_area")
        _validate_string_tuple(self.legal_notes, "legal_notes")
        _validate_string_tuple(self.access_notes, "access_notes")
        _validate_optional_percentage(
            self.static_data_confidence,
            "static_data_confidence",
        )
        _validate_optional_aware_datetime(self.last_updated, "last_updated")

    def to_dict(self) -> dict[str, Any]:
        """Возвращает JSON-совместимое представление лесного участка."""

        return {
            "spot_id": self.spot_id,
            "name": self.name,
            "geometry": copy_geojson_geometry(self.geometry),
            "region": self.region,
            "country": self.country,
            "elevation_min_m": self.elevation_min_m,
            "elevation_max_m": self.elevation_max_m,
            "dominant_aspect_deg": self.dominant_aspect_deg,
            "slope_deg": self.slope_deg,
            "forest_type": self.forest_type,
            "tree_species": list(self.tree_species),
            "geology": self.geology,
            "soil_type": self.soil_type,
            "soil_ph": self.soil_ph,
            "nutrient_level": self.nutrient_level,
            "canopy_density_pct": self.canopy_density_pct,
            "forest_age_class": self.forest_age_class,
            "disturbance_level": self.disturbance_level,
            "nearest_stream_m": self.nearest_stream_m,
            "protected_area": self.protected_area,
            "collecting_allowed": self.collecting_allowed,
            "legal_notes": list(self.legal_notes),
            "access_notes": list(self.access_notes),
            "static_data_confidence": self.static_data_confidence,
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ForestSpot":
        """Создаёт лесной участок из JSON-подобного mapping."""

        return cls(
            spot_id=required_string(data["spot_id"], "spot_id"),
            name=required_string(data["name"], "name"),
            geometry=parse_geojson_geometry(data["geometry"]),
            region=required_string(data["region"], "region"),
            country=required_string(data["country"], "country"),
            elevation_min_m=optional_float(
                data.get("elevation_min_m"),
                "elevation_min_m",
            ),
            elevation_max_m=optional_float(
                data.get("elevation_max_m"),
                "elevation_max_m",
            ),
            dominant_aspect_deg=optional_float(
                data.get("dominant_aspect_deg"),
                "dominant_aspect_deg",
            ),
            slope_deg=optional_float(data.get("slope_deg"), "slope_deg"),
            forest_type=optional_string(data.get("forest_type"), "forest_type"),
            tree_species=string_tuple(data.get("tree_species", ()), "tree_species"),
            geology=optional_string(data.get("geology"), "geology"),
            soil_type=optional_string(data.get("soil_type"), "soil_type"),
            soil_ph=optional_float(data.get("soil_ph"), "soil_ph"),
            nutrient_level=optional_string(
                data.get("nutrient_level"),
                "nutrient_level",
            ),
            canopy_density_pct=optional_float(
                data.get("canopy_density_pct"),
                "canopy_density_pct",
            ),
            forest_age_class=optional_string(
                data.get("forest_age_class"),
                "forest_age_class",
            ),
            disturbance_level=optional_string(
                data.get("disturbance_level"),
                "disturbance_level",
            ),
            nearest_stream_m=optional_float(
                data.get("nearest_stream_m"),
                "nearest_stream_m",
            ),
            protected_area=optional_string(
                data.get("protected_area"),
                "protected_area",
            ),
            collecting_allowed=optional_bool(
                data.get("collecting_allowed"),
                "collecting_allowed",
            ),
            legal_notes=string_tuple(data.get("legal_notes", ()), "legal_notes"),
            access_notes=string_tuple(data.get("access_notes", ()), "access_notes"),
            static_data_confidence=optional_float(
                data.get("static_data_confidence"),
                "static_data_confidence",
            ),
            last_updated=optional_datetime(data.get("last_updated"), "last_updated"),
        )


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")



def _validate_optional_range(
    minimum: float | None,
    maximum: float | None,
    field_name: str,
) -> None:
    if (minimum is None) != (maximum is None):
        raise ValueError(f"{field_name} requires both minimum and maximum")
    if minimum is None or maximum is None:
        return
    _validate_optional_number(minimum, f"{field_name}_minimum")
    _validate_optional_number(maximum, f"{field_name}_maximum")
    if minimum > maximum:
        raise ValueError(f"{field_name} minimum must not exceed maximum")


def _validate_optional_number(value: float | None, field_name: str) -> None:
    if value is not None and not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


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


def _validate_optional_aware_datetime(
    value: datetime | None,
    field_name: str,
) -> None:
    if value is None:
        return
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone information")
