"""
File: weather_snapshot.py
Project: mushroom-racing

Purpose:
    Собирает domain WeatherSnapshot из нормализованного WeatherSeries
    и derived WeatherFeatures.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — assembly layer между weather data pipeline и domain model.

Inputs:
    spot_id, WeatherSeries и as_of_date.

Outputs:
    WeatherSnapshot.

Dependencies:
    Python standard library
    mushroom_racing.domain.weather
    mushroom_racing.providers.weather
    mushroom_racing.weather_features

Used by:
    Будущий geospatial/weather feature assembly и scoring pipeline.

Notes:
    Неизвестные поля остаются None. Daily min/max берутся только из
    записи за as_of_date. Rolling features рассчитываются strict policy:
    неполное окно или None внутри нужного окна -> соответствующий feature None.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.providers.weather import DailyWeather, WeatherSeries
from mushroom_racing.weather_features import extract_weather_features


def build_weather_snapshot(
    *,
    spot_id: str,
    series: WeatherSeries,
    as_of_date: date,
) -> WeatherSnapshot:
    """Строит domain WeatherSnapshot для указанной календарной даты."""

    if not isinstance(spot_id, str):
        raise TypeError("spot_id must be a string")
    if not spot_id.strip():
        raise ValueError("spot_id must not be empty")
    if not isinstance(series, WeatherSeries):
        raise TypeError("series must be a WeatherSeries")
    if not isinstance(as_of_date, date) or isinstance(as_of_date, datetime):
        raise TypeError("as_of_date must be a date")

    features = extract_weather_features(
        series,
        as_of_date=as_of_date,
    )
    daily_record = _find_record_for_date(series, as_of_date)

    return WeatherSnapshot(
        spot_id=spot_id,
        timestamp=datetime.combine(
            as_of_date,
            time.min,
            tzinfo=timezone.utc,
        ),
        source_id=series.source_id,
        rain_24h_mm=features.rain_24h_mm,
        rain_3d_mm=features.rain_3d_mm,
        rain_7d_mm=features.rain_7d_mm,
        rain_14d_mm=features.rain_14d_mm,
        rain_21d_mm=features.rain_21d_mm,
        rain_28d_mm=features.rain_28d_mm,
        rain_90d_mm=None,
        rain_anomaly_value=None,
        rain_anomaly_method=None,
        avg_temp_7d_c=features.avg_temp_7d_c,
        avg_temp_14d_c=features.avg_temp_14d_c,
        avg_temp_20d_c=features.avg_temp_20d_c,
        min_temp_c=(
            daily_record.min_temperature_c
            if daily_record is not None
            else None
        ),
        max_temp_c=(
            daily_record.max_temperature_c
            if daily_record is not None
            else None
        ),
        humidity_pct=None,
        wind_speed_m_s=None,
        soil_moisture_value=None,
        soil_moisture_method=None,
        drought_index_value=None,
        drought_index_method=None,
    )


def _find_record_for_date(
    series: WeatherSeries,
    target_date: date,
) -> DailyWeather | None:
    matching = tuple(
        record
        for record in series.records
        if record.timestamp.date() == target_date
    )

    if len(matching) > 1:
        raise ValueError(
            f"multiple weather records map to calendar date {target_date.isoformat()}"
        )

    return matching[0] if matching else None
