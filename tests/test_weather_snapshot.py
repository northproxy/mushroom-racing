"""
File: test_weather_snapshot.py
Project: mushroom-racing

Purpose:
    Проверяет assembly WeatherSeries -> WeatherFeatures -> WeatherSnapshot.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — unit tests для weather snapshot assembly.

Inputs:
    Синтетические WeatherSeries.

Outputs:
    Pytest assertions.

Dependencies:
    pytest
    Python standard library

Used by:
    pytest

Notes:
    Тесты подтверждают, что unknown остаётся None и domain contract
    не изменяется.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.providers.weather import DailyWeather, WeatherSeries
from mushroom_racing.weather_snapshot import build_weather_snapshot


def _series(
    *,
    start: date,
    days: int,
    precipitation_mm: float = 1.0,
    mean_temperature_c: float = 10.0,
) -> WeatherSeries:
    records = tuple(
        DailyWeather(
            timestamp=datetime(
                (start + timedelta(days=offset)).year,
                (start + timedelta(days=offset)).month,
                (start + timedelta(days=offset)).day,
                tzinfo=timezone.utc,
            ),
            precipitation_mm=precipitation_mm,
            mean_temperature_c=mean_temperature_c,
            min_temperature_c=5.0 + offset,
            max_temperature_c=15.0 + offset,
        )
        for offset in range(days)
    )

    return WeatherSeries(
        requested_latitude=47.7200,
        requested_longitude=15.9000,
        source_latitude=47.718814849853516,
        source_longitude=15.900300979614258,
        source_id="geosphere_spartacus_v3_1d_1km",
        records=records,
    )


def test_builds_domain_weather_snapshot() -> None:
    series = _series(start=date(2026, 8, 16), days=28)

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert isinstance(snapshot, WeatherSnapshot)
    assert snapshot.spot_id == "control_spot"
    assert snapshot.source_id == "geosphere_spartacus_v3_1d_1km"
    assert snapshot.timestamp == datetime(
        2026,
        9,
        12,
        tzinfo=timezone.utc,
    )


def test_populates_rolling_features() -> None:
    series = _series(start=date(2026, 8, 16), days=28)

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert snapshot.rain_24h_mm == pytest.approx(1.0)
    assert snapshot.rain_3d_mm == pytest.approx(3.0)
    assert snapshot.rain_7d_mm == pytest.approx(7.0)
    assert snapshot.rain_14d_mm == pytest.approx(14.0)
    assert snapshot.rain_21d_mm == pytest.approx(21.0)
    assert snapshot.rain_28d_mm == pytest.approx(28.0)
    assert snapshot.avg_temp_7d_c == pytest.approx(10.0)
    assert snapshot.avg_temp_14d_c == pytest.approx(10.0)
    assert snapshot.avg_temp_20d_c == pytest.approx(10.0)


def test_populates_daily_min_and_max_for_as_of_date() -> None:
    series = _series(start=date(2026, 9, 10), days=3)

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert snapshot.min_temp_c == pytest.approx(7.0)
    assert snapshot.max_temp_c == pytest.approx(17.0)


def test_unimplemented_features_remain_none() -> None:
    series = _series(start=date(2026, 8, 16), days=28)

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert snapshot.rain_90d_mm is None
    assert snapshot.rain_anomaly_value is None
    assert snapshot.rain_anomaly_method is None
    assert snapshot.humidity_pct is None
    assert snapshot.wind_speed_m_s is None
    assert snapshot.soil_moisture_value is None
    assert snapshot.soil_moisture_method is None
    assert snapshot.drought_index_value is None
    assert snapshot.drought_index_method is None


def test_short_series_preserves_missing_rolling_features() -> None:
    series = _series(start=date(2026, 9, 10), days=3)

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert snapshot.rain_24h_mm == pytest.approx(1.0)
    assert snapshot.rain_3d_mm == pytest.approx(3.0)
    assert snapshot.rain_7d_mm is None
    assert snapshot.rain_28d_mm is None
    assert snapshot.avg_temp_7d_c is None
    assert snapshot.avg_temp_20d_c is None


def test_missing_as_of_record_keeps_daily_values_none() -> None:
    series = _series(start=date(2026, 9, 1), days=10)

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert snapshot.rain_24h_mm is None
    assert snapshot.min_temp_c is None
    assert snapshot.max_temp_c is None


def test_none_daily_min_max_are_preserved() -> None:
    series = _series(start=date(2026, 9, 12), days=1)
    original = series.records[0]
    replacement = DailyWeather(
        timestamp=original.timestamp,
        precipitation_mm=original.precipitation_mm,
        mean_temperature_c=original.mean_temperature_c,
        min_temperature_c=None,
        max_temperature_c=None,
    )
    series = WeatherSeries(
        requested_latitude=series.requested_latitude,
        requested_longitude=series.requested_longitude,
        source_latitude=series.source_latitude,
        source_longitude=series.source_longitude,
        source_id=series.source_id,
        records=(replacement,),
    )

    snapshot = build_weather_snapshot(
        spot_id="control_spot",
        series=series,
        as_of_date=date(2026, 9, 12),
    )

    assert snapshot.min_temp_c is None
    assert snapshot.max_temp_c is None


def test_rejects_empty_spot_id() -> None:
    series = _series(start=date(2026, 9, 12), days=1)

    with pytest.raises(ValueError, match="spot_id"):
        build_weather_snapshot(
            spot_id="   ",
            series=series,
            as_of_date=date(2026, 9, 12),
        )
