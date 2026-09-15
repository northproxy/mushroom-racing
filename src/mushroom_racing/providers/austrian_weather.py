"""
File: austrian_weather.py
Project: mushroom-racing

Purpose:
    Загружает суточные погодные данные GeoSphere Austria SPARTACUS v3
    для одной WGS84-координаты и нормализует их в WeatherSeries.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — production adapter для GeoSphere SPARTACUS weather data.

Inputs:
    WGS84 latitude/longitude и inclusive date range.

Outputs:
    WeatherSeries с DailyWeather records.

Dependencies:
    Python standard library
    mushroom_racing.providers.weather

Used by:
    Будущий weather feature extraction pipeline.

Notes:
    Provider не считает rolling-window features. GeoSphere null сохраняется
    как None. HTTP 200 с полностью пустыми weather values является NO_DATA,
    а не provider error.
"""

from __future__ import annotations

from datetime import date, datetime
import json
from json import JSONDecodeError
from math import isfinite
import socket
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

from mushroom_racing.providers.weather import (
    DailyWeather,
    WeatherProvider,
    WeatherProviderError,
    WeatherSeries,
)


class AustrianWeatherProvider(WeatherProvider):
    """GeoSphere Austria SPARTACUS v3 daily point-query provider."""

    BASE_URL = (
        "https://dataset.api.hub.geosphere.at/v1/timeseries/historical/"
        "spartacus-v3-1d-1km"
    )
    SOURCE_ID = "geosphere_spartacus_v3_1d_1km"
    PARAMETERS = ("RR", "TM24", "TN", "TX")
    TIMEOUT_SECONDS = 30

    _EXPECTED_UNITS = {
        "RR": "kg m-2",
        "TM24": "degC",
        "TN": "degC",
        "TX": "degC",
    }

    def get_daily_series(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> WeatherSeries:
        """Возвращает SPARTACUS daily series для одной координаты."""

        self._validate_query(latitude, longitude, start_date, end_date)

        query = urllib.parse.urlencode(
            {
                "parameters": ",".join(self.PARAMETERS),
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "lat_lon": f"{latitude},{longitude}",
            }
        )
        request = urllib.request.Request(
            f"{self.BASE_URL}?{query}",
            headers={"User-Agent": "mushroom-racing/0.x"},
        )

        payload = self._fetch_json(request)
        return self._parse_payload(
            payload,
            requested_latitude=float(latitude),
            requested_longitude=float(longitude),
        )

    @staticmethod
    def _validate_query(
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> None:
        for name, value, minimum, maximum in (
            ("latitude", latitude, -90.0, 90.0),
            ("longitude", longitude, -180.0, 180.0),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a real number")
            if not isfinite(float(value)):
                raise ValueError(f"{name} must be finite")
            if not minimum <= float(value) <= maximum:
                raise ValueError(f"{name} must be between {minimum} and {maximum}")

        if not isinstance(start_date, date) or isinstance(start_date, datetime):
            raise TypeError("start_date must be a date")
        if not isinstance(end_date, date) or isinstance(end_date, datetime):
            raise TypeError("end_date must be a date")
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

    @classmethod
    def _fetch_json(cls, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(
                request,
                timeout=cls.TIMEOUT_SECONDS,
            ) as response:
                status = getattr(response, "status", None)
                if status is not None and not 200 <= status < 300:
                    raise WeatherProviderError(
                        f"GeoSphere returned unexpected HTTP status {status}"
                    )
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise WeatherProviderError(
                f"GeoSphere HTTP error: {exc.code}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
            raise WeatherProviderError(
                f"GeoSphere request failed: {exc}"
            ) from exc

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as exc:
            raise WeatherProviderError(
                "GeoSphere returned malformed JSON"
            ) from exc

        if not isinstance(payload, dict):
            raise WeatherProviderError("GeoSphere response root must be an object")

        return payload

    @classmethod
    def _parse_payload(
        cls,
        payload: dict[str, Any],
        *,
        requested_latitude: float,
        requested_longitude: float,
    ) -> WeatherSeries:
        if payload.get("type") != "FeatureCollection":
            raise WeatherProviderError(
                "GeoSphere response must be a FeatureCollection"
            )

        timestamps_raw = payload.get("timestamps")
        if not isinstance(timestamps_raw, list):
            raise WeatherProviderError(
                "GeoSphere response timestamps must be a list"
            )

        timestamps = [cls._parse_timestamp(value) for value in timestamps_raw]

        features = payload.get("features")
        if not isinstance(features, list) or len(features) != 1:
            raise WeatherProviderError(
                "GeoSphere point query must return exactly one feature"
            )

        feature = features[0]
        if not isinstance(feature, dict):
            raise WeatherProviderError("GeoSphere feature must be an object")

        source_longitude, source_latitude = cls._parse_point_geometry(
            feature.get("geometry")
        )
        parameters = cls._parse_parameters(
            feature.get("properties"),
            expected_length=len(timestamps),
        )

        records = tuple(
            DailyWeather(
                timestamp=timestamp,
                precipitation_mm=cls._normalize_value(
                    parameters["RR"]["data"][index],
                    parameter="RR",
                ),
                mean_temperature_c=cls._normalize_value(
                    parameters["TM24"]["data"][index],
                    parameter="TM24",
                ),
                min_temperature_c=cls._normalize_value(
                    parameters["TN"]["data"][index],
                    parameter="TN",
                ),
                max_temperature_c=cls._normalize_value(
                    parameters["TX"]["data"][index],
                    parameter="TX",
                ),
            )
            for index, timestamp in enumerate(timestamps)
        )

        return WeatherSeries(
            requested_latitude=requested_latitude,
            requested_longitude=requested_longitude,
            source_latitude=source_latitude,
            source_longitude=source_longitude,
            source_id=cls.SOURCE_ID,
            records=records,
        )

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if not isinstance(value, str):
            raise WeatherProviderError(
                "GeoSphere timestamp must be a string"
            )

        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise WeatherProviderError(
                f"Invalid GeoSphere timestamp: {value!r}"
            ) from exc

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise WeatherProviderError(
                "GeoSphere timestamps must be timezone-aware"
            )

        return parsed

    @staticmethod
    def _parse_point_geometry(geometry: Any) -> tuple[float, float]:
        if not isinstance(geometry, dict) or geometry.get("type") != "Point":
            raise WeatherProviderError(
                "GeoSphere feature geometry must be a Point"
            )

        coordinates = geometry.get("coordinates")
        if (
            not isinstance(coordinates, list)
            or len(coordinates) < 2
        ):
            raise WeatherProviderError(
                "GeoSphere Point coordinates must contain longitude and latitude"
            )

        longitude, latitude = coordinates[0], coordinates[1]
        for name, value, minimum, maximum in (
            ("source longitude", longitude, -180.0, 180.0),
            ("source latitude", latitude, -90.0, 90.0),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise WeatherProviderError(f"{name} must be numeric")
            if not isfinite(float(value)):
                raise WeatherProviderError(f"{name} must be finite")
            if not minimum <= float(value) <= maximum:
                raise WeatherProviderError(
                    f"{name} is outside valid coordinate range"
                )

        return float(longitude), float(latitude)

    @classmethod
    def _parse_parameters(
        cls,
        properties: Any,
        *,
        expected_length: int,
    ) -> dict[str, dict[str, Any]]:
        if not isinstance(properties, dict):
            raise WeatherProviderError(
                "GeoSphere feature properties must be an object"
            )

        parameters = properties.get("parameters")
        if not isinstance(parameters, dict):
            raise WeatherProviderError(
                "GeoSphere properties.parameters must be an object"
            )

        parsed: dict[str, dict[str, Any]] = {}

        for parameter in cls.PARAMETERS:
            raw_parameter = parameters.get(parameter)
            if not isinstance(raw_parameter, dict):
                raise WeatherProviderError(
                    f"GeoSphere parameter {parameter} is missing or invalid"
                )

            unit = raw_parameter.get("unit")
            expected_unit = cls._EXPECTED_UNITS[parameter]
            if unit != expected_unit:
                raise WeatherProviderError(
                    f"Unexpected unit for {parameter}: {unit!r}; "
                    f"expected {expected_unit!r}"
                )

            data = raw_parameter.get("data")
            if not isinstance(data, list):
                raise WeatherProviderError(
                    f"GeoSphere parameter {parameter}.data must be a list"
                )
            if len(data) != expected_length:
                raise WeatherProviderError(
                    f"GeoSphere parameter {parameter} length does not match timestamps"
                )

            parsed[parameter] = raw_parameter

        return parsed

    @staticmethod
    def _normalize_value(value: Any, *, parameter: str) -> float | None:
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise WeatherProviderError(
                f"GeoSphere parameter {parameter} contains non-numeric data"
            )

        normalized = float(value)
        if not isfinite(normalized):
            raise WeatherProviderError(
                f"GeoSphere parameter {parameter} contains non-finite data"
            )

        # Для воды 1 kg/m² численно эквивалентен 1 mm слоя осадков.
        if parameter == "RR" and normalized < 0:
            raise WeatherProviderError(
                "GeoSphere precipitation must not be negative"
            )

        return normalized
