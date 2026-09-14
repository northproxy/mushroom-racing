"""Общие helpers для GeoJSON-compatible geometry в domain-слое."""

from __future__ import annotations

from math import isfinite
from typing import Any, Mapping

SUPPORTED_GEOMETRY_TYPES = {"Point", "Polygon", "MultiPolygon"}


def validate_geojson_geometry(geometry: Mapping[str, Any]) -> None:
    """Проверяет минимальный 2D GeoJSON-контракт без GIS-зависимостей."""

    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geometry_type not in SUPPORTED_GEOMETRY_TYPES:
        raise ValueError("geometry type must be Point, Polygon, or MultiPolygon")
    if coordinates is None:
        raise ValueError("geometry must contain coordinates")

    if geometry_type == "Point":
        _validate_position(coordinates, "Point")
    elif geometry_type == "Polygon":
        _validate_polygon(coordinates)
    else:
        _validate_multipolygon(coordinates)


def copy_geojson_geometry(geometry: Mapping[str, Any]) -> dict[str, Any]:
    """Возвращает независимую JSON-совместимую копию geometry."""

    return {
        "type": geometry["type"],
        "coordinates": _copy_coordinates(geometry["coordinates"]),
    }


def parse_geojson_geometry(value: Any) -> Mapping[str, Any]:
    """Преобразует JSON-подобное значение во внутренний geometry mapping."""

    if not isinstance(value, Mapping):
        raise TypeError("geometry must be a mapping")

    geometry = {
        "type": value.get("type"),
        "coordinates": _copy_coordinates(value.get("coordinates")),
    }
    validate_geojson_geometry(geometry)
    return geometry


def _validate_position(value: Any, context: str) -> None:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{context} position must contain [longitude, latitude]")

    longitude = _coordinate_number(value[0], "longitude")
    latitude = _coordinate_number(value[1], "latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("longitude must be between -180 and 180")
    if not -90 <= latitude <= 90:
        raise ValueError("latitude must be between -90 and 90")


def _validate_polygon(value: Any) -> None:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("Polygon coordinates must contain at least one linear ring")

    for ring in value:
        if not isinstance(ring, (list, tuple)) or len(ring) < 4:
            raise ValueError("Polygon linear ring must contain at least four positions")
        for position in ring:
            _validate_position(position, "Polygon")
        if list(ring[0]) != list(ring[-1]):
            raise ValueError("Polygon linear ring must be closed")


def _validate_multipolygon(value: Any) -> None:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("MultiPolygon coordinates must contain at least one polygon")

    for polygon in value:
        _validate_polygon(polygon)


def _copy_coordinates(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return [_copy_coordinates(item) for item in value]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("geometry coordinates must contain only numbers and arrays")

    numeric = float(value)
    if not isfinite(numeric):
        raise ValueError("geometry coordinates must be finite")
    return numeric


def _coordinate_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")

    numeric = float(value)
    if not isfinite(numeric):
        raise ValueError(f"{field_name} must be finite")
    return numeric
