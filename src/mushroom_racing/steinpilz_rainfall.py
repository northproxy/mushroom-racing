"""
File: steinpilz_rainfall.py
Project: mushroom-racing

Purpose:
    Интерпретирует доступный rainfall context для Boletus edulis
    из нормализованного WeatherSnapshot.

Created:
    2026-09-16

Last modified:
    2026-09-16

Status:
    active

Lifecycle:
    permanent — species-specific interpretation layer для MR-5.

Inputs:
    WeatherSnapshot.

Outputs:
    SteinpilzRainfallInterpretation.

Dependencies:
    Python standard library
    mushroom_racing.domain.weather

Used by:
    MR-5 Steinpilz scoring pipeline.

Notes:
    Этот слой описывает доступный rainfall context и раскладывает
    вложенные rolling totals на непересекающиеся временные интервалы.

    Он намеренно не преобразует rainfall в moisture_score, потому что
    текущие данные не содержат 90-day rainfall context, rainfall anomaly,
    measured soil moisture или drought index.

    rain_28d_mm используется как primary rainfall context. Это
    explainable approximation к multi-week antecedent rainfall context,
    а не биологический threshold.

    Известный rainfall 0.0 mm является реальным наблюдением, а не
    missing value. Неконсистентные cumulative totals не исправляются
    молча: соответствующий derived bin остаётся unknown.
"""

from __future__ import annotations

from dataclasses import dataclass

from mushroom_racing.domain.weather import WeatherSnapshot


RAINFALL_TOLERANCE_MM = 1e-6


@dataclass(frozen=True, slots=True)
class SteinpilzRainfallInterpretation:
    """Species-specific description of available rainfall context."""

    primary_rainfall_context_mm: float | None

    rain_d01_03_mm: float | None
    rain_d04_07_mm: float | None
    rain_d08_14_mm: float | None
    rain_d15_21_mm: float | None
    rain_d22_28_mm: float | None

    moisture_score: float | None

    reasons: tuple[str, ...]


def _rainfall_difference(
    *,
    earlier_label: str,
    earlier_mm: float | None,
    later_label: str,
    later_mm: float | None,
    reasons: list[str],
) -> float | None:
    """Return rainfall in the interval between two cumulative windows."""

    if earlier_mm is None or later_mm is None:
        return None

    difference = later_mm - earlier_mm

    if difference < -RAINFALL_TOLERANCE_MM:
        reasons.append(
            "Inconsistent rainfall totals: "
            f"{later_label} rainfall ({later_mm:.2f} mm) is lower than "
            f"{earlier_label} rainfall ({earlier_mm:.2f} mm)."
        )
        return None

    # Tiny negative values within tolerance are floating-point noise.
    if difference < 0.0:
        return 0.0

    return difference


def interpret_steinpilz_rainfall(
    weather: WeatherSnapshot,
) -> SteinpilzRainfallInterpretation:
    """Build an explainable rainfall-support context.

    MR-5.3f intentionally does not derive an ecological moisture score
    from rainfall alone.

    The 28-day cumulative total is retained as the primary descriptive
    rainfall context. Nested totals are transformed into non-overlapping
    bins for explanation and QA only.

    Missing endpoints produce unknown derived bins. Inconsistent
    cumulative totals are reported explicitly and are never silently
    corrected into valid rainfall.
    """

    reasons: list[str] = []

    rain_d01_03_mm = weather.rain_3d_mm

    rain_d04_07_mm = _rainfall_difference(
        earlier_label="3-day",
        earlier_mm=weather.rain_3d_mm,
        later_label="7-day",
        later_mm=weather.rain_7d_mm,
        reasons=reasons,
    )
    rain_d08_14_mm = _rainfall_difference(
        earlier_label="7-day",
        earlier_mm=weather.rain_7d_mm,
        later_label="14-day",
        later_mm=weather.rain_14d_mm,
        reasons=reasons,
    )
    rain_d15_21_mm = _rainfall_difference(
        earlier_label="14-day",
        earlier_mm=weather.rain_14d_mm,
        later_label="21-day",
        later_mm=weather.rain_21d_mm,
        reasons=reasons,
    )
    rain_d22_28_mm = _rainfall_difference(
        earlier_label="21-day",
        earlier_mm=weather.rain_21d_mm,
        later_label="28-day",
        later_mm=weather.rain_28d_mm,
        reasons=reasons,
    )

    if weather.rain_28d_mm is None:
        reasons.append("Primary 28-day rainfall context is unknown.")
    else:
        reasons.append(
            "Primary 28-day rainfall context is "
            f"{weather.rain_28d_mm:.2f} mm."
        )

    reasons.append(
        "Rainfall context is not converted to moisture_score in "
        "Steinpilz v0.1 because longer-term drought and soil-moisture "
        "context are not yet available."
    )

    return SteinpilzRainfallInterpretation(
        primary_rainfall_context_mm=weather.rain_28d_mm,
        rain_d01_03_mm=rain_d01_03_mm,
        rain_d04_07_mm=rain_d04_07_mm,
        rain_d08_14_mm=rain_d08_14_mm,
        rain_d15_21_mm=rain_d15_21_mm,
        rain_d22_28_mm=rain_d22_28_mm,
        moisture_score=None,
        reasons=tuple(reasons),
    )
