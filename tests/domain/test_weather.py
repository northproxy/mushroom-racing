from datetime import datetime, timezone

import pytest

from mushroom_racing.domain import WeatherSnapshot


def _valid_snapshot(**overrides: object) -> WeatherSnapshot:
    data: dict[str, object] = {
        "spot_id": "spot-001",
        "timestamp": datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
        "source_id": "test-weather-source",
        "rain_24h_mm": 0.0,
        "rain_14d_mm": 44.0,
        "avg_temp_14d_c": 13.1,
        "humidity_pct": 78.0,
    }
    data.update(overrides)
    return WeatherSnapshot(**data)  # type: ignore[arg-type]


def test_weather_snapshot_distinguishes_zero_rain_from_missing_data() -> None:
    snapshot = _valid_snapshot(rain_24h_mm=0.0, rain_3d_mm=None)

    assert snapshot.rain_24h_mm == 0.0
    assert snapshot.rain_3d_mm is None


def test_weather_snapshot_rejects_negative_rainfall() -> None:
    with pytest.raises(ValueError, match="rain_24h_mm"):
        _valid_snapshot(rain_24h_mm=-0.1)


def test_weather_snapshot_rejects_invalid_humidity() -> None:
    with pytest.raises(ValueError, match="humidity_pct"):
        _valid_snapshot(humidity_pct=101.0)


def test_weather_snapshot_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        _valid_snapshot(timestamp=datetime(2026, 9, 14, 12, 0))


def test_weather_snapshot_requires_method_for_soil_moisture() -> None:
    with pytest.raises(ValueError, match="soil_moisture requires both"):
        _valid_snapshot(soil_moisture_value=0.42)


def test_weather_snapshot_requires_value_for_drought_method() -> None:
    with pytest.raises(ValueError, match="drought_index requires both"):
        _valid_snapshot(drought_index_method="synthetic_index")


def test_weather_snapshot_rejects_inverted_temperature_range() -> None:
    with pytest.raises(ValueError, match="min_temp_c"):
        _valid_snapshot(min_temp_c=20.0, max_temp_c=10.0)
