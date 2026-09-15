from datetime import datetime, timezone

import pytest

from mushroom_racing.steinpilz_temperature import (
    _score_temperature_c,
    interpret_steinpilz_temperature,
)
from mushroom_racing.domain.weather import WeatherSnapshot


def make_weather(
    *,
    avg_temp_7d_c=None,
    avg_temp_14d_c=None,
    avg_temp_20d_c=None,
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
        avg_temp_7d_c=avg_temp_7d_c,
        avg_temp_14d_c=avg_temp_14d_c,
        avg_temp_20d_c=avg_temp_20d_c,
    )


def test_all_temperature_windows_unknown_remain_unknown():
    result = interpret_steinpilz_temperature(make_weather())

    assert result.score is None
    assert len(result.reasons) == 3
    assert all(
        "unknown" in reason.lower()
        for reason in result.reasons
    )


def test_known_zero_temperature_is_not_treated_as_missing():
    result = interpret_steinpilz_temperature(
        make_weather(avg_temp_7d_c=0.0)
    )

    assert result.score == 0.20
    assert "0.00 °C" in result.reasons[0]


def test_single_known_window_is_sufficient():
    result = interpret_steinpilz_temperature(
        make_weather(avg_temp_14d_c=14.0)
    )

    assert result.score == 0.80


def test_partial_windows_use_only_known_values():
    result = interpret_steinpilz_temperature(
        make_weather(
            avg_temp_7d_c=14.0,
            avg_temp_20d_c=20.0,
        )
    )

    assert result.score == pytest.approx(0.60)


def test_favourable_temperature_range_gets_positive_score():
    assert _score_temperature_c(13.0) == 0.80


def test_cold_temperature_is_soft_negative_not_zero():
    assert _score_temperature_c(2.0) == 0.20


def test_hot_temperature_is_soft_negative_not_zero():
    assert _score_temperature_c(25.0) == 0.20


def test_mixed_temperature_windows_are_averaged():
    result = interpret_steinpilz_temperature(
        make_weather(
            avg_temp_7d_c=14.0,
            avg_temp_14d_c=17.0,
            avg_temp_20d_c=20.0,
        )
    )

    assert result.score == pytest.approx(0.60)


def test_reasons_identify_each_temperature_window():
    result = interpret_steinpilz_temperature(
        make_weather(
            avg_temp_7d_c=14.0,
            avg_temp_14d_c=15.0,
            avg_temp_20d_c=16.0,
        )
    )

    assert "7-day" in result.reasons[0]
    assert "14.00 °C" in result.reasons[0]

    assert "14-day" in result.reasons[1]
    assert "15.00 °C" in result.reasons[1]

    assert "20-day" in result.reasons[2]
    assert "16.00 °C" in result.reasons[2]
