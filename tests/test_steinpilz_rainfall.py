from datetime import datetime, timezone

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


def test_all_rainfall_windows_unknown_remain_unscored():
    result = interpret_steinpilz_rainfall(make_weather())

    assert result.score is None

    assert all(
        "unknown" in reason.lower()
        for reason in result.reasons[:5]
    )


def test_known_zero_rainfall_is_not_treated_as_missing():
    result = interpret_steinpilz_rainfall(
        make_weather(rain_3d_mm=0.0)
    )

    assert result.score is None
    assert "3-day rainfall is 0.00 mm." in result.reasons


def test_partial_rainfall_windows_preserve_missingness():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=12.0,
            rain_14d_mm=35.0,
        )
    )

    assert "3-day rainfall is 12.00 mm." in result.reasons
    assert "14-day rainfall is 35.00 mm." in result.reasons

    assert any(
        "7-day rainfall is unknown" in reason
        for reason in result.reasons
    )

    assert any(
        "21-day rainfall is unknown" in reason
        for reason in result.reasons
    )

    assert any(
        "28-day rainfall is unknown" in reason
        for reason in result.reasons
    )


def test_all_supported_rainfall_windows_are_described():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=28.3,
            rain_7d_mm=34.5,
            rain_14d_mm=53.9,
            rain_21d_mm=58.0,
            rain_28d_mm=95.9,
        )
    )

    assert "3-day rainfall is 28.30 mm." in result.reasons
    assert "7-day rainfall is 34.50 mm." in result.reasons
    assert "14-day rainfall is 53.90 mm." in result.reasons
    assert "21-day rainfall is 58.00 mm." in result.reasons
    assert "28-day rainfall is 95.90 mm." in result.reasons


def test_rainfall_context_does_not_create_moisture_score():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=30.0,
            rain_7d_mm=50.0,
            rain_14d_mm=80.0,
            rain_21d_mm=100.0,
            rain_28d_mm=120.0,
        )
    )

    assert result.score is None


def test_dry_rainfall_context_is_not_a_hard_exclusion():
    result = interpret_steinpilz_rainfall(
        make_weather(
            rain_3d_mm=0.0,
            rain_7d_mm=0.0,
            rain_14d_mm=0.0,
            rain_21d_mm=0.0,
            rain_28d_mm=0.0,
        )
    )

    assert result.score is None

    assert all(
        "exclusion" not in reason.lower()
        for reason in result.reasons
    )


def test_reason_explains_why_rainfall_is_not_scored():
    result = interpret_steinpilz_rainfall(
        make_weather(rain_14d_mm=40.0)
    )

    assert any(
        "not converted to moisture_score" in reason
        for reason in result.reasons
    )
