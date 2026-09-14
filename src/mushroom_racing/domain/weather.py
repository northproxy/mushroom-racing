"""Domain-модель нормализованного погодного снимка для лесного участка."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any, Mapping

from .parsing import (
    optional_float,
    optional_string,
    required_datetime,
    required_string,
)


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    """Нормализованные погодные признаки участка на конкретный момент времени."""

    spot_id: str
    timestamp: datetime
    source_id: str
    rain_24h_mm: float | None = None
    rain_3d_mm: float | None = None
    rain_7d_mm: float | None = None
    rain_14d_mm: float | None = None
    rain_21d_mm: float | None = None
    rain_28d_mm: float | None = None
    rain_90d_mm: float | None = None
    rain_anomaly_value: float | None = None
    rain_anomaly_method: str | None = None
    avg_temp_7d_c: float | None = None
    avg_temp_14d_c: float | None = None
    avg_temp_20d_c: float | None = None
    min_temp_c: float | None = None
    max_temp_c: float | None = None
    humidity_pct: float | None = None
    wind_speed_m_s: float | None = None
    soil_moisture_value: float | None = None
    soil_moisture_method: str | None = None
    drought_index_value: float | None = None
    drought_index_method: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.spot_id, "spot_id")
        _require_non_empty(self.source_id, "source_id")
        _validate_aware_datetime(self.timestamp, "timestamp")

        for field_name, value in (
            ("rain_24h_mm", self.rain_24h_mm),
            ("rain_3d_mm", self.rain_3d_mm),
            ("rain_7d_mm", self.rain_7d_mm),
            ("rain_14d_mm", self.rain_14d_mm),
            ("rain_21d_mm", self.rain_21d_mm),
            ("rain_28d_mm", self.rain_28d_mm),
            ("rain_90d_mm", self.rain_90d_mm),
        ):
            _validate_optional_non_negative(value, field_name)

        for field_name, value in (
            ("rain_anomaly_value", self.rain_anomaly_value),
            ("avg_temp_7d_c", self.avg_temp_7d_c),
            ("avg_temp_14d_c", self.avg_temp_14d_c),
            ("avg_temp_20d_c", self.avg_temp_20d_c),
            ("min_temp_c", self.min_temp_c),
            ("max_temp_c", self.max_temp_c),
            ("soil_moisture_value", self.soil_moisture_value),
            ("drought_index_value", self.drought_index_value),
        ):
            _validate_optional_finite(value, field_name)

        if (
            self.min_temp_c is not None
            and self.max_temp_c is not None
            and self.min_temp_c > self.max_temp_c
        ):
            raise ValueError("min_temp_c must not exceed max_temp_c")

        _validate_optional_percentage(self.humidity_pct, "humidity_pct")
        _validate_optional_non_negative(self.wind_speed_m_s, "wind_speed_m_s")

        _validate_value_and_method_pair(
            self.rain_anomaly_value,
            self.rain_anomaly_method,
            "rain_anomaly",
        )
        _validate_value_and_method_pair(
            self.soil_moisture_value,
            self.soil_moisture_method,
            "soil_moisture",
        )
        _validate_value_and_method_pair(
            self.drought_index_value,
            self.drought_index_method,
            "drought_index",
        )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает JSON-совместимое представление погодного снимка."""

        return {
            "spot_id": self.spot_id,
            "timestamp": self.timestamp.isoformat(),
            "source_id": self.source_id,
            "rain_24h_mm": self.rain_24h_mm,
            "rain_3d_mm": self.rain_3d_mm,
            "rain_7d_mm": self.rain_7d_mm,
            "rain_14d_mm": self.rain_14d_mm,
            "rain_21d_mm": self.rain_21d_mm,
            "rain_28d_mm": self.rain_28d_mm,
            "rain_90d_mm": self.rain_90d_mm,
            "rain_anomaly_value": self.rain_anomaly_value,
            "rain_anomaly_method": self.rain_anomaly_method,
            "avg_temp_7d_c": self.avg_temp_7d_c,
            "avg_temp_14d_c": self.avg_temp_14d_c,
            "avg_temp_20d_c": self.avg_temp_20d_c,
            "min_temp_c": self.min_temp_c,
            "max_temp_c": self.max_temp_c,
            "humidity_pct": self.humidity_pct,
            "wind_speed_m_s": self.wind_speed_m_s,
            "soil_moisture_value": self.soil_moisture_value,
            "soil_moisture_method": self.soil_moisture_method,
            "drought_index_value": self.drought_index_value,
            "drought_index_method": self.drought_index_method,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WeatherSnapshot":
        """Создаёт погодный снимок из JSON-подобного mapping."""

        return cls(
            spot_id=required_string(data["spot_id"], "spot_id"),
            timestamp=required_datetime(data["timestamp"], "timestamp"),
            source_id=required_string(data["source_id"], "source_id"),
            rain_24h_mm=optional_float(data.get("rain_24h_mm"), "rain_24h_mm"),
            rain_3d_mm=optional_float(data.get("rain_3d_mm"), "rain_3d_mm"),
            rain_7d_mm=optional_float(data.get("rain_7d_mm"), "rain_7d_mm"),
            rain_14d_mm=optional_float(data.get("rain_14d_mm"), "rain_14d_mm"),
            rain_21d_mm=optional_float(data.get("rain_21d_mm"), "rain_21d_mm"),
            rain_28d_mm=optional_float(data.get("rain_28d_mm"), "rain_28d_mm"),
            rain_90d_mm=optional_float(data.get("rain_90d_mm"), "rain_90d_mm"),
            rain_anomaly_value=optional_float(
                data.get("rain_anomaly_value"),
                "rain_anomaly_value",
            ),
            rain_anomaly_method=optional_string(
                data.get("rain_anomaly_method"),
                "rain_anomaly_method",
            ),
            avg_temp_7d_c=optional_float(
                data.get("avg_temp_7d_c"),
                "avg_temp_7d_c",
            ),
            avg_temp_14d_c=optional_float(
                data.get("avg_temp_14d_c"),
                "avg_temp_14d_c",
            ),
            avg_temp_20d_c=optional_float(
                data.get("avg_temp_20d_c"),
                "avg_temp_20d_c",
            ),
            min_temp_c=optional_float(data.get("min_temp_c"), "min_temp_c"),
            max_temp_c=optional_float(data.get("max_temp_c"), "max_temp_c"),
            humidity_pct=optional_float(data.get("humidity_pct"), "humidity_pct"),
            wind_speed_m_s=optional_float(
                data.get("wind_speed_m_s"),
                "wind_speed_m_s",
            ),
            soil_moisture_value=optional_float(
                data.get("soil_moisture_value"),
                "soil_moisture_value",
            ),
            soil_moisture_method=optional_string(
                data.get("soil_moisture_method"),
                "soil_moisture_method",
            ),
            drought_index_value=optional_float(
                data.get("drought_index_value"),
                "drought_index_value",
            ),
            drought_index_method=optional_string(
                data.get("drought_index_method"),
                "drought_index_method",
            ),
        )


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _validate_aware_datetime(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone information")


def _validate_optional_finite(value: float | None, field_name: str) -> None:
    if value is not None and not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _validate_optional_non_negative(value: float | None, field_name: str) -> None:
    _validate_optional_finite(value, field_name)
    if value is not None and value < 0:
        raise ValueError(f"{field_name} must be >= 0")


def _validate_optional_percentage(value: float | None, field_name: str) -> None:
    _validate_optional_finite(value, field_name)
    if value is not None and not 0 <= value <= 100:
        raise ValueError(f"{field_name} must be between 0 and 100")


def _validate_value_and_method_pair(
    value: float | None,
    method: str | None,
    field_name: str,
) -> None:
    if (value is None) != (method is None):
        raise ValueError(f"{field_name} requires both value and method")
    if method is not None and not method.strip():
        raise ValueError(f"{field_name}_method must not be empty")
