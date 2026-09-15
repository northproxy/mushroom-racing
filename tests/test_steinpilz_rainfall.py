from datetime import datetime, timezone

import pytest

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.steinpilz_rainfall import (
    interpret_steinpilz_rainfall,
)


def make_weather(
    *,
    rain_3d_mm=None,
    rain_7d_mm=None,
    rain_14d_mm=None,
    rain_21d_mm=None,
    rain_28d_mm=None,
) -> WeatherSnapshot:
    return WeatherSnapshot(
        spot_id="test_spot",
        timestamp=datetime(
            2026,
            9,
            12,
            tzinfo=timezone.utc,
        ),
        source_id="test",
        rain_3d_mm=rain_3d_mm,
        rain_7d_mm=rain_7d_mm,
        rain_14d_mm=rain_14d_mm,
        rain_21d_mm=rain_21d_mm,
        rain_28d_mm=rain_28d_mm,
    )


def test_all_rainfall_inputs_unknown():
    result = interpret_steinpilz_rainfall(make_weather())

    assert result.primary_rainfall_context_mm is None
    assert result.rain_d01_03_mm is None
    assert result.rain_d04_07_mm is None
    assert result.rain_d08_14_mm is None
    assert result.rain_d15_21_mm is None
    assert result.rain_d22_28_mm is None
    assert result.moisture_score is None


def test_known_zero_rainfall_produces_zero_bins():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=0.0,
            rain_7d_mm=0.0,
            rain_14d_mm=0.0,
            rain_21d_mm=0.0,
            rain_28d_mm=0.0,
        )
    )

    assert result.primary_rainfall_context_mm == 0.0
    assert result.rain_d01_03_mm == 0.0
    assert result.rain_d04_07_mm == 0.0
    assert result.rain_d08_14_mm == 0.0
    assert result.rain_d15_21_mm == 0.0
    assert result.rain_d22_28_mm == 0.0


def test_complete_cumulative_totals_are_split_into_non_overlapping_bins():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=10.0,
            rain_7d_mm=15.0,
            rain_14d_mm=25.0,
            rain_21d_mm=30.0,
            rain_28d_mm=40.0,
        )
    )

    assert result.rain_d01_03_mm == 10.0
    assert result.rain_d04_07_mm == 5.0
    assert result.rain_d08_14_mm == 10.0
    assert result.rain_d15_21_mm == 5.0
    assert result.rain_d22_28_mm == 10.0


def test_control_like_values_are_split_correctly():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=28.3,
            rain_7d_mm=34.5,
            rain_14d_mm=53.9,
            rain_21d_mm=58.0,
            rain_28d_mm=95.9,
        )
    )

    assert result.rain_d01_03_mm == pytest.approx(28.3)
    assert result.rain_d04_07_mm == pytest.approx(6.2)
    assert result.rain_d08_14_mm == pytest.approx(19.4)
    assert result.rain_d15_21_mm == pytest.approx(4.1)
    assert result.rain_d22_28_mm == pytest.approx(37.9)


def test_missing_endpoint_makes_affected_bin_unknown():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=10.0,
            rain_7d_mm=None,
            rain_14d_mm=30.0,
        )
    )

    assert result.rain_d04_07_mm is None
    assert result.rain_d08_14_mm is None


def test_other_computable_bins_survive_missing_window():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=10.0,
            rain_7d_mm=None,
            rain_14d_mm=30.0,
            rain_21d_mm=40.0,
            rain_28d_mm=50.0,
        )
    )

    assert result.rain_d01_03_mm == 10.0
    assert result.rain_d04_07_mm is None
    assert result.rain_d08_14_mm is None
    assert result.rain_d15_21_mm == 10.0
    assert result.rain_d22_28_mm == 10.0


def test_missing_28_day_total_makes_primary_context_unknown():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=10.0,
            rain_7d_mm=15.0,
            rain_14d_mm=20.0,
            rain_21d_mm=25.0,
            rain_28d_mm=None,
        )
    )

    assert result.primary_rainfall_context_mm is None
    assert result.rain_d22_28_mm is None


def test_non_monotonic_totals_make_bin_unknown_and_add_reason():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=10.0,
            rain_7d_mm=20.0,
            rain_14d_mm=15.0,
            rain_21d_mm=25.0,
            rain_28d_mm=30.0,
        )
    )

    assert result.rain_d08_14_mm is None

    assert any(
        "14-day rainfall (15.00 mm) is lower than "
        "7-day rainfall (20.00 mm)" in reason
        for reason in result.reasons
    )


def test_rainfall_context_never_creates_moisture_score():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=30.0,
            rain_7d_mm=50.0,
            rain_14d_mm=80.0,
            rain_21d_mm=100.0,
            rain_28d_mm=120.0,
        )
    )

    assert result.moisture_score is None

    assert any(
        "not converted to moisture_score" in reason
        for reason in result.reasons
    )
