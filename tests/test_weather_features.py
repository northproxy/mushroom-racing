"""
File: test_weather_features.py
Project: mushroom-racing

Purpose:
    Проверяет strict rolling weather feature extraction.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — unit tests для weather feature extraction.

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
    Missing calendar day или None внутри окна должны давать None,
    а не неполную сумму/среднее.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from mushroom_racing.providers.weather import DailyWeather, WeatherSeries
from mushroom_racing.weather_features import extract_weather_features


def _series(
    *,
    start: date,
    days: int,
    precipitation: float = 1.0,
    mean_temperature: float = 10.0,
) -> WeatherSeries:
    records = tuple(
        DailyWeather(
            timestamp=datetime.combine(
                start + timedelta(days=offset),
                datetime.min.time(),
                tzinfo=timezone.utc,
            ),
            precipitation_mm=precipitation,
            mean_temperature_c=mean_temperature,
            min_temperature_c=5.0,
            max_temperature_c=15.0,
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


def test_extracts_all_features_from_complete_28_day_series() -> None:
    series = _series(start=date(2026, 8, 16), days=28)

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_24h_mm == pytest.approx(1.0)
    assert features.rain_3d_mm == pytest.approx(3.0)
    assert features.rain_7d_mm == pytest.approx(7.0)
    assert features.rain_14d_mm == pytest.approx(14.0)
    assert features.rain_21d_mm == pytest.approx(21.0)
    assert features.rain_28d_mm == pytest.approx(28.0)
    assert features.avg_temp_7d_c == pytest.approx(10.0)
    assert features.avg_temp_14d_c == pytest.approx(10.0)
    assert features.avg_temp_20d_c == pytest.approx(10.0)


def test_windows_are_inclusive_of_as_of_date() -> None:
    start = date(2026, 9, 10)
    records = (
        DailyWeather(
            timestamp=datetime(2026, 9, 10, tzinfo=timezone.utc),
            precipitation_mm=1.0,
            mean_temperature_c=10.0,
            min_temperature_c=5.0,
            max_temperature_c=15.0,
        ),
        DailyWeather(
            timestamp=datetime(2026, 9, 11, tzinfo=timezone.utc),
            precipitation_mm=2.0,
            mean_temperature_c=20.0,
            min_temperature_c=5.0,
            max_temperature_c=25.0,
        ),
        DailyWeather(
            timestamp=datetime(2026, 9, 12, tzinfo=timezone.utc),
            precipitation_mm=4.0,
            mean_temperature_c=30.0,
            min_temperature_c=5.0,
            max_temperature_c=35.0,
        ),
    )
    series = WeatherSeries(
        requested_latitude=47.72,
        requested_longitude=15.9,
        source_latitude=47.7188,
        source_longitude=15.9003,
        source_id="test",
        records=records,
    )

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_24h_mm == pytest.approx(4.0)
    assert features.rain_3d_mm == pytest.approx(7.0)


def test_short_series_returns_none_for_larger_windows() -> None:
    series = _series(start=date(2026, 9, 10), days=3)

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_24h_mm == pytest.approx(1.0)
    assert features.rain_3d_mm == pytest.approx(3.0)
    assert features.rain_7d_mm is None
    assert features.rain_14d_mm is None
    assert features.rain_21d_mm is None
    assert features.rain_28d_mm is None
    assert features.avg_temp_7d_c is None
    assert features.avg_temp_14d_c is None
    assert features.avg_temp_20d_c is None


def test_missing_calendar_day_invalidates_affected_window() -> None:
    series = _series(start=date(2026, 9, 6), days=7)
    records = tuple(
        record
        for record in series.records
        if record.timestamp.date() != date(2026, 9, 10)
    )
    series = WeatherSeries(
        requested_latitude=series.requested_latitude,
        requested_longitude=series.requested_longitude,
        source_latitude=series.source_latitude,
        source_longitude=series.source_longitude,
        source_id=series.source_id,
        records=records,
    )

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_24h_mm == pytest.approx(1.0)
    assert features.rain_3d_mm is None
    assert features.rain_7d_mm is None


def test_none_precipitation_invalidates_only_precipitation_windows() -> None:
    series = _series(start=date(2026, 9, 6), days=7)
    records = list(series.records)
    target = records[3]
    records[3] = DailyWeather(
        timestamp=target.timestamp,
        precipitation_mm=None,
        mean_temperature_c=target.mean_temperature_c,
        min_temperature_c=target.min_temperature_c,
        max_temperature_c=target.max_temperature_c,
    )
    series = WeatherSeries(
        requested_latitude=series.requested_latitude,
        requested_longitude=series.requested_longitude,
        source_latitude=series.source_latitude,
        source_longitude=series.source_longitude,
        source_id=series.source_id,
        records=tuple(records),
    )

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_7d_mm is None
    assert features.avg_temp_7d_c == pytest.approx(10.0)


def test_none_mean_temperature_invalidates_only_temperature_windows() -> None:
    series = _series(start=date(2026, 9, 6), days=7)
    records = list(series.records)
    target = records[2]
    records[2] = DailyWeather(
        timestamp=target.timestamp,
        precipitation_mm=target.precipitation_mm,
        mean_temperature_c=None,
        min_temperature_c=target.min_temperature_c,
        max_temperature_c=target.max_temperature_c,
    )
    series = WeatherSeries(
        requested_latitude=series.requested_latitude,
        requested_longitude=series.requested_longitude,
        source_latitude=series.source_latitude,
        source_longitude=series.source_longitude,
        source_id=series.source_id,
        records=tuple(records),
    )

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_7d_mm == pytest.approx(7.0)
    assert features.avg_temp_7d_c is None


def test_zero_precipitation_is_counted_as_known_zero() -> None:
    series = _series(
        start=date(2026, 9, 10),
        days=3,
        precipitation=0.0,
    )

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_24h_mm == 0.0
    assert features.rain_3d_mm == 0.0


def test_extra_older_records_do_not_change_window() -> None:
    series = _series(start=date(2026, 8, 1), days=43)

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_28d_mm == pytest.approx(28.0)
    assert features.avg_temp_20d_c == pytest.approx(10.0)


def test_as_of_date_without_record_returns_none_for_all_features() -> None:
    series = _series(start=date(2026, 9, 1), days=10)

    features = extract_weather_features(
        series,
        as_of_date=date(2026, 9, 12),
    )

    assert features.rain_24h_mm is None
    assert features.rain_3d_mm is None
    assert features.rain_7d_mm is None
    assert features.rain_14d_mm is None
    assert features.rain_21d_mm is None
    assert features.rain_28d_mm is None
    assert features.avg_temp_7d_c is None
    assert features.avg_temp_14d_c is None
    assert features.avg_temp_20d_c is None


def test_duplicate_calendar_dates_fail_fast() -> None:
    first = DailyWeather(
        timestamp=datetime(2026, 9, 12, 0, tzinfo=timezone.utc),
        precipitation_mm=1.0,
        mean_temperature_c=10.0,
        min_temperature_c=5.0,
        max_temperature_c=15.0,
    )
    second = DailyWeather(
        timestamp=datetime(2026, 9, 12, 12, tzinfo=timezone.utc),
        precipitation_mm=2.0,
        mean_temperature_c=11.0,
        min_temperature_c=6.0,
        max_temperature_c=16.0,
    )
    series = WeatherSeries(
        requested_latitude=47.72,
        requested_longitude=15.9,
        source_latitude=47.7188,
        source_longitude=15.9003,
        source_id="test",
        records=(first, second),
    )

    with pytest.raises(ValueError, match="calendar date"):
        extract_weather_features(
            series,
            as_of_date=date(2026, 9, 12),
        )
