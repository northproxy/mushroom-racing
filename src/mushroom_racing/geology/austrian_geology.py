"""Operational geology-provider для GeoSphere Austria."""

from __future__ import annotations

from math import isfinite
from typing import Any

import httpx

from mushroom_racing.geology.geology import (
    GeologyQueryResult,
    GeologyRecord,
)


_SERVICE_URL = (
    "https://gis.geosphere.at/maps/rest/services/"
    "inspire/GE_GeologicUnit_50k/MapServer/0/query"
)

_OUT_FIELDS = (
    "identifier,"
    "name,"
    "description,"
    "geologicUnitType,"
    "material,"
    "representativeLithology"
)


class GeologyProviderError(RuntimeError):
    """Ошибка получения или разбора geology-данных внешнего provider-а."""


class AustrianGeologyProvider:
    """Получает geological units из GeoSphere Austria GE.GeologicUnit_50k.

    Provider возвращает source-level данные без интерпретации lithology,
    выбора "главной" geological unit или преобразования в habitat score.

    HTTP-клиент передаётся снаружи, чтобы жизненный цикл соединений оставался
    ответственностью application/infrastructure слоя и provider легко тестировался.
    """

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get_geology(
        self,
        latitude: float,
        longitude: float,
    ) -> GeologyQueryResult:
        """Возвращает geological units, пересекающие WGS84-точку."""
        self._validate_request(latitude, longitude)

        params = {
            "f": "json",
            "geometry": f"{longitude},{latitude}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": _OUT_FIELDS,
            "returnGeometry": "false",
        }

        try:
            response = self._client.get(_SERVICE_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GeologyProviderError(
                "failed to fetch geology for "
                f"latitude={latitude}, longitude={longitude}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise GeologyProviderError(
                "invalid geology response: expected JSON"
            ) from exc

        return _parse_geology_response(payload)

    @staticmethod
    def _validate_request(
        latitude: float,
        longitude: float,
    ) -> None:
        if not all(isfinite(value) for value in (latitude, longitude)):
            raise ValueError("latitude and longitude must be finite")
        if not -90.0 <= latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        if not -180.0 <= longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")


def _parse_geology_response(payload: Any) -> GeologyQueryResult:
    """Преобразует ArcGIS response в source-level geology contract."""
    if not isinstance(payload, dict):
        raise GeologyProviderError(
            "invalid geology response: expected JSON object"
        )

    if "error" in payload:
        raise GeologyProviderError("GeoSphere returned an ArcGIS error")

    features = payload.get("features")

    if not isinstance(features, list):
        raise GeologyProviderError(
            "invalid geology response: 'features' must be a list"
        )

    records: list[GeologyRecord] = []

    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            raise GeologyProviderError(
                f"invalid geology response: feature {index} must be an object"
            )

        attributes = feature.get("attributes")

        if not isinstance(attributes, dict):
            raise GeologyProviderError(
                f"invalid geology response: feature {index} "
                "must contain attributes object"
            )

        try:
            record = GeologyRecord(
                identifier=_required_string(
                    attributes,
                    "identifier",
                    feature_index=index,
                ),
                name=_optional_string(
                    attributes,
                    "name",
                    feature_index=index,
                ),
                description=_optional_string(
                    attributes,
                    "description",
                    feature_index=index,
                ),
                geologic_unit_type=_optional_string(
                    attributes,
                    "geologicUnitType",
                    feature_index=index,
                ),
                material=_optional_string(
                    attributes,
                    "material",
                    feature_index=index,
                ),
                representative_lithology=_optional_string(
                    attributes,
                    "representativeLithology",
                    feature_index=index,
                ),
            )
        except (TypeError, ValueError) as exc:
            raise GeologyProviderError(
                f"invalid geology response: feature {index} "
                "contains invalid attributes"
            ) from exc

        records.append(record)

    return GeologyQueryResult(records=tuple(records))


def _required_string(
    attributes: dict[str, Any],
    field: str,
    *,
    feature_index: int,
) -> str:
    """Возвращает обязательное непустое строковое source-поле."""
    value = attributes.get(field)

    if not isinstance(value, str) or not value.strip():
        raise GeologyProviderError(
            f"invalid geology response: feature {feature_index} "
            f"field {field!r} must be a non-empty string"
        )

    return value


def _optional_string(
    attributes: dict[str, Any],
    field: str,
    *,
    feature_index: int,
) -> str | None:
    """Возвращает nullable строковое source-поле без скрытой нормализации."""
    value = attributes.get(field)

    if value is None:
        return None

    if not isinstance(value, str):
        raise GeologyProviderError(
            f"invalid geology response: feature {feature_index} "
            f"field {field!r} must be a string or null"
        )

    return value
