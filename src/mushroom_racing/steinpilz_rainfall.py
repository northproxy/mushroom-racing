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
    Этот слой пока только описывает доступный rainfall context.

    Он намеренно не преобразует rainfall в moisture_score, потому что
    текущие данные не содержат 90-day rainfall context, rainfall anomaly,
    measured soil moisture или drought index.

    Rolling rainfall windows являются вложенными и поэтому не должны
    независимо усредняться как пять отдельных ecological signals.

    Известный rainfall 0.0 mm является реальным наблюдением, а не
    missing value.
"""

from __future__ import annotations

from dataclasses import dataclass

from mushroom_racing.domain.weather import WeatherSnapshot


@dataclass(frozen=True, slots=True)
class SteinpilzRainfallInterpretation:
    """Species-specific description of available rainfall context."""

    score: float | None
    reasons: tuple[str, ...]


def interpret_steinpilz_rainfall(
    weather: WeatherSnapshot,
) -> SteinpilzRainfallInterpretation:
    """Describe available rolling rainfall windows.

    MR-5.3e intentionally does not derive an ecological moisture score
    from rainfall alone.

    Missing windows remain unknown. Known zero rainfall remains a real
    value. No rainfall threshold creates an ecological hard exclusion.
    """

    windows = (
        ("3-day", weather.rain_3d_mm),
        ("7-day", weather.rain_7d_mm),
        ("14-day", weather.rain_14d_mm),
        ("21-day", weather.rain_21d_mm),
        ("28-day", weather.rain_28d_mm),
    )

    reasons: list[str] = []

    for label, rainfall_mm in windows:
        if rainfall_mm is None:
            reasons.append(
                f"{label} rainfall is unknown; "
                "no rainfall context was inferred from this window."
            )
            continue

        reasons.append(
            f"{label} rainfall is {rainfall_mm:.2f} mm."
        )

    reasons.append(
        "Rainfall context is not converted to moisture_score in "
        "Steinpilz v0.1 because longer-term drought and soil-moisture "
        "context are not yet available."
    )

    return SteinpilzRainfallInterpretation(
        score=None,
        reasons=tuple(reasons),
    )
