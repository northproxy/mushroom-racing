"""
File: weather_features.py
Project: mushroom-racing

Purpose:
    Вычисляет deterministic rolling weather features из нормализованного
    WeatherSeries без обращения к внешнему API.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — feature extraction layer для weather data.

Inputs:
    WeatherSeries и дата, для которой рассчитываются rolling features.

Outputs:
    WeatherFeatures с precipitation sums и mean-temperature averages.

Dependencies:
    Python standard library
    mushroom_racing.providers.weather

Used by:
    Будущая сборка WeatherSnapshot и scoring pipeline.

Notes:
    Окна календарные и inclusive: 7d = as_of_date + 6 предыдущих дней.
    Если хотя бы один календарный день отсутствует или нужное значение None,
    соответствующий derived feature возвращается как None.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from math import fsum

from mushroom_racing.providers.weather import DailyWeather, WeatherSeries


@dataclass(frozen=True, slots=True)
class WeatherFeatures:
    """Derived weather features для одной даты."""

    rain_24h_mm: float | None
    rain_3d_mm: float | None
    rain_7d_mm: float | None
    rain_14d_mm: float | None
    rain_21d_mm: float | None
    rain_28d_mm: float | None
    avg_temp_7d_c: float | None
    avg_temp_14d_c: float | None
    avg_temp_20d_c: float | None


def extract_weather_features(
    series: WeatherSeries,
    *,
    as_of_date: date,
) -> WeatherFeatures:
    """Вычисляет strict rolling features на указанную календарную дату."""

    if not isinstance(series, WeatherSeries):
        raise TypeError("series must be a WeatherSeries")
    if not isinstance(as_of_date, date):
        raise TypeError("as_of_date must be a date")

    records_by_date = _index_records_by_date(series.records)

    return WeatherFeatures(
        rain_24h_mm=_sum_precipitation(
            records_by_date,
            as_of_date=as_of_date,
            days=1,
        ),
        rain_3d_mm=_sum_precipitation(
            records_by_date,
            as_of_date=as_of_date,
            days=3,
        ),
        rain_7d_mm=_sum_precipitation(
            records_by_date,
            as_of_date=as_of_date,
            days=7,
        ),
        rain_14d_mm=_sum_precipitation(
            records_by_date,
            as_of_date=as_of_date,
            days=14,
        ),
        rain_21d_mm=_sum_precipitation(
            records_by_date,
            as_of_date=as_of_date,
            days=21,
        ),
        rain_28d_mm=_sum_precipitation(
            records_by_date,
            as_of_date=as_of_date,
            days=28,
        ),
        avg_temp_7d_c=_average_mean_temperature(
            records_by_date,
            as_of_date=as_of_date,
            days=7,
        ),
        avg_temp_14d_c=_average_mean_temperature(
            records_by_date,
            as_of_date=as_of_date,
            days=14,
        ),
        avg_temp_20d_c=_average_mean_temperature(
            records_by_date,
            as_of_date=as_of_date,
            days=20,
        ),
    )


def _index_records_by_date(
    records: tuple[DailyWeather, ...],
) -> dict[date, DailyWeather]:
    indexed: dict[date, DailyWeather] = {}

    for record in records:
        record_date = record.timestamp.date()
        if record_date in indexed:
            raise ValueError(
                f"multiple weather records map to calendar date {record_date.isoformat()}"
            )
        indexed[record_date] = record

    return indexed


def _window_records(
    records_by_date: dict[date, DailyWeather],
    *,
    as_of_date: date,
    days: int,
) -> tuple[DailyWeather, ...] | None:
    dates = tuple(
        as_of_date - timedelta(days=offset)
        for offset in range(days - 1, -1, -1)
    )

    if any(current_date not in records_by_date for current_date in dates):
        return None

    return tuple(records_by_date[current_date] for current_date in dates)


def _sum_precipitation(
    records_by_date: dict[date, DailyWeather],
    *,
    as_of_date: date,
    days: int,
) -> float | None:
    records = _window_records(
        records_by_date,
        as_of_date=as_of_date,
        days=days,
    )
    if records is None:
        return None

    values = tuple(record.precipitation_mm for record in records)
    if any(value is None for value in values):
        return None

    return fsum(value for value in values if value is not None)


def _average_mean_temperature(
    records_by_date: dict[date, DailyWeather],
    *,
    as_of_date: date,
    days: int,
) -> float | None:
    records = _window_records(
        records_by_date,
        as_of_date=as_of_date,
        days=days,
    )
    if records is None:
        return None

    values = tuple(record.mean_temperature_c for record in records)
    if any(value is None for value in values):
        return None

    numeric_values = tuple(value for value in values if value is not None)
    return fsum(numeric_values) / days
