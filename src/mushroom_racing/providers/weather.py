"""
File: weather.py
Project: mushroom-racing

Purpose:
    Определяет source-agnostic контракт суточных погодных данных для weather providers.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — базовый provider contract для weather data layer.

Inputs:
    Нормализованные суточные погодные значения от внешних provider adapters.

Outputs:
    DailyWeather, WeatherSeries и интерфейс WeatherProvider.

Dependencies:
    Python standard library

Used by:
    Будущие GeoSphere/INCA weather providers и weather feature extraction.

Notes:
    Этот модуль намеренно не содержит HTTP-клиента, GeoSphere-specific parsing
    или rolling-window calculations. Missing data сохраняются как None.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite


class WeatherProviderError(RuntimeError):
    """Ошибка operational/provider-уровня при получении или разборе погодных данных."""


class WeatherAvailability(str, Enum):
    """Доступность полезных значений внутри нормализованной weather series."""

    AVAILABLE = "available"
    PARTIAL = "partial"
    NO_DATA = "no_data"


def _validate_coordinate(value: float, *, minimum: float, maximum: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    if not isfinite(float(value)):
        raise ValueError(f"{name} must be finite")
    if not minimum <= float(value) <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")


def _validate_optional_number(value: float | None, *, name: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number or None")
    if not isfinite(float(value)):
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class DailyWeather:
    """Нормализованные суточные погодные значения для одной source grid/station point."""

    timestamp: datetime
    precipitation_mm: float | None
    mean_temperature_c: float | None
    min_temperature_c: float | None
    max_temperature_c: float | None

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")

        _validate_optional_number(self.precipitation_mm, name="precipitation_mm")
        _validate_optional_number(self.mean_temperature_c, name="mean_temperature_c")
        _validate_optional_number(self.min_temperature_c, name="min_temperature_c")
        _validate_optional_number(self.max_temperature_c, name="max_temperature_c")

        if self.precipitation_mm is not None and self.precipitation_mm < 0:
            raise ValueError("precipitation_mm must be >= 0")

        if (
            self.min_temperature_c is not None
            and self.max_temperature_c is not None
            and self.min_temperature_c > self.max_temperature_c
        ):
            raise ValueError("min_temperature_c must be <= max_temperature_c")

    @property
    def has_any_data(self) -> bool:
        """True, если хотя бы один weather parameter известен."""

        return any(
            value is not None
            for value in (
                self.precipitation_mm,
                self.mean_temperature_c,
                self.min_temperature_c,
                self.max_temperature_c,
            )
        )

    @property
    def has_complete_data(self) -> bool:
        """True, если известны все четыре baseline weather parameter."""

        return all(
            value is not None
            for value in (
                self.precipitation_mm,
                self.mean_temperature_c,
                self.min_temperature_c,
                self.max_temperature_c,
            )
        )


@dataclass(frozen=True, slots=True)
class WeatherSeries:
    """Нормализованный результат point-query за диапазон дат."""

    requested_latitude: float
    requested_longitude: float
    source_latitude: float
    source_longitude: float
    source_id: str
    records: tuple[DailyWeather, ...]

    def __post_init__(self) -> None:
        _validate_coordinate(
            self.requested_latitude,
            minimum=-90.0,
            maximum=90.0,
            name="requested_latitude",
        )
        _validate_coordinate(
            self.requested_longitude,
            minimum=-180.0,
            maximum=180.0,
            name="requested_longitude",
        )
        _validate_coordinate(
            self.source_latitude,
            minimum=-90.0,
            maximum=90.0,
            name="source_latitude",
        )
        _validate_coordinate(
            self.source_longitude,
            minimum=-180.0,
            maximum=180.0,
            name="source_longitude",
        )

        if not isinstance(self.source_id, str):
            raise TypeError("source_id must be a string")
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")

        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        if not all(isinstance(record, DailyWeather) for record in self.records):
            raise TypeError("records must contain DailyWeather values")

        timestamps = [record.timestamp for record in self.records]
        if timestamps != sorted(timestamps):
            raise ValueError("records must be ordered by timestamp")
        if len(timestamps) != len(set(timestamps)):
            raise ValueError("records must not contain duplicate timestamps")

    @property
    def availability(self) -> WeatherAvailability:
        """Вычисляет availability без дублирования состояния в объекте."""

        if not self.records or not any(record.has_any_data for record in self.records):
            return WeatherAvailability.NO_DATA

        if all(record.has_complete_data for record in self.records):
            return WeatherAvailability.AVAILABLE

        return WeatherAvailability.PARTIAL


class WeatherProvider(ABC):
    """Source-agnostic interface для получения нормализованного daily weather series."""

    @abstractmethod
    def get_daily_series(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> WeatherSeries:
        """Возвращает суточные погодные данные для точки и inclusive date range."""
