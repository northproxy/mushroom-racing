"""
File: test_weather.py
Project: mushroom-racing

Purpose:
    Проверяет source-agnostic weather provider contract и missing-data semantics.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — unit tests для weather provider contract.

Inputs:
    Синтетические DailyWeather / WeatherSeries fixtures.

Outputs:
    Pytest assertions.

Dependencies:
    pytest
    Python standard library

Used by:
    pytest

Notes:
    Live GeoSphere API здесь намеренно не используется.
"""

from datetime import datetime, timezone

import pytest

from mushroom_racing.providers.weather import (
    DailyWeather,
    WeatherAvailability,
    WeatherSeries,
)


def _record(
    day: int,
    *,
    precipitation_mm: float | None = 1.0,
    mean_temperature_c: float | None = 10.0,
    min_temperature_c: float | None = 5.0,
    max_temperature_c: float | None = 15.0,
) -> DailyWeather:
    return DailyWeather(
        timestamp=datetime(2026, 9, day, tzinfo=timezone.utc),
        precipitation_mm=precipitation_mm,
        mean_temperature_c=mean_temperature_c,
        min_temperature_c=min_temperature_c,
        max_temperature_c=max_temperature_c,
    )


def _series(*records: DailyWeather) -> WeatherSeries:
    return WeatherSeries(
        requested_latitude=47.7200,
        requested_longitude=15.9000,
        source_latitude=47.718814849853516,
        source_longitude=15.900300979614258,
        source_id="geosphere_spartacus_v3_1d_1km",
        records=tuple(records),
    )


def test_daily_weather_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        DailyWeather(
            timestamp=datetime(2026, 9, 1),
            precipitation_mm=0.0,
            mean_temperature_c=10.0,
            min_temperature_c=5.0,
            max_temperature_c=15.0,
        )


def test_zero_precipitation_is_valid_known_value() -> None:
    record = _record(1, precipitation_mm=0.0)

    assert record.precipitation_mm == 0.0
    assert record.has_any_data is True
    assert record.has_complete_data is True


def test_none_is_preserved_as_missing_data() -> None:
    record = _record(1, precipitation_mm=None)

    assert record.precipitation_mm is None
    assert record.has_any_data is True
    assert record.has_complete_data is False


def test_negative_precipitation_is_rejected() -> None:
    with pytest.raises(ValueError, match="precipitation_mm"):
        _record(1, precipitation_mm=-0.1)


def test_min_temperature_must_not_exceed_max_temperature() -> None:
    with pytest.raises(ValueError, match="min_temperature_c"):
        _record(1, min_temperature_c=12.0, max_temperature_c=11.0)


def test_weather_series_reports_available_when_every_value_exists() -> None:
    series = _series(_record(1), _record(2))

    assert series.availability is WeatherAvailability.AVAILABLE


def test_weather_series_reports_partial_for_partial_nulls() -> None:
    series = _series(
        _record(1),
        _record(2, mean_temperature_c=None),
    )

    assert series.availability is WeatherAvailability.PARTIAL


def test_weather_series_reports_no_data_when_every_value_is_null() -> None:
    series = _series(
        _record(
            1,
            precipitation_mm=None,
            mean_temperature_c=None,
            min_temperature_c=None,
            max_temperature_c=None,
        ),
        _record(
            2,
            precipitation_mm=None,
            mean_temperature_c=None,
            min_temperature_c=None,
            max_temperature_c=None,
        ),
    )

    assert series.availability is WeatherAvailability.NO_DATA


def test_empty_weather_series_is_no_data() -> None:
    assert _series().availability is WeatherAvailability.NO_DATA


def test_requested_and_source_coordinates_are_kept_separately() -> None:
    series = _series(_record(1))

    assert series.requested_latitude == 47.7200
    assert series.requested_longitude == 15.9000
    assert series.source_latitude == pytest.approx(47.718814849853516)
    assert series.source_longitude == pytest.approx(15.900300979614258)


def test_weather_series_rejects_out_of_order_records() -> None:
    with pytest.raises(ValueError, match="ordered"):
        _series(_record(2), _record(1))


def test_weather_series_rejects_duplicate_timestamps() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        _series(_record(1), _record(1))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("requested_latitude", 91.0),
        ("requested_longitude", 181.0),
        ("source_latitude", -91.0),
        ("source_longitude", -181.0),
    ],
)
def test_weather_series_rejects_invalid_coordinates(field: str, value: float) -> None:
    kwargs = {
        "requested_latitude": 47.7200,
        "requested_longitude": 15.9000,
        "source_latitude": 47.718814849853516,
        "source_longitude": 15.900300979614258,
        "source_id": "geosphere_spartacus_v3_1d_1km",
        "records": (_record(1),),
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        WeatherSeries(**kwargs)


def test_weather_series_rejects_empty_source_id() -> None:
    with pytest.raises(ValueError, match="source_id"):
        WeatherSeries(
            requested_latitude=47.7200,
            requested_longitude=15.9000,
            source_latitude=47.718814849853516,
            source_longitude=15.900300979614258,
            source_id="   ",
            records=(_record(1),),
        )
