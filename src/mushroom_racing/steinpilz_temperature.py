"""
File: steinpilz_temperature.py
Project: mushroom-racing

Purpose:
    Интерпретирует температурный контекст для Boletus edulis
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
    SteinpilzTemperatureInterpretation.

Dependencies:
    Python standard library
    mushroom_racing.domain.weather

Used by:
    MR-5 Steinpilz scoring pipeline.

Notes:
    Температурные диапазоны являются soft working hypotheses
    Steinpilz v0.1 и должны позже калиброваться по evidence
    и observations.

    Отсутствующие температурные окна остаются unknown и не
    интерпретируются как 0 или нейтральный сигнал.

    Rainfall, drought, humidity, seasonality и timing-after-rain
    здесь намеренно не моделируются.
"""

from __future__ import annotations

from dataclasses import dataclass

from mushroom_racing.domain.weather import WeatherSnapshot


@dataclass(frozen=True, slots=True)
class SteinpilzTemperatureInterpretation:
    """Species-specific interpretation of available temperature windows."""

    score: float | None
    reasons: tuple[str, ...]


def _score_temperature_c(temperature_c: float) -> float:
    """Map mean temperature to a soft Steinpilz v0.1 score."""

    if temperature_c < 5.0:
        return 0.20

    if temperature_c < 8.0:
        return 0.40

    if temperature_c < 10.0:
        return 0.60

    if temperature_c <= 16.0:
        return 0.80

    if temperature_c <= 19.0:
        return 0.60

    if temperature_c <= 22.0:
        return 0.40

    return 0.20


def interpret_steinpilz_temperature(
    weather: WeatherSnapshot,
) -> SteinpilzTemperatureInterpretation:
    """Interpret available rolling mean temperatures.

    Each known temperature window contributes independently.
    Missing windows are excluded rather than replaced with a fabricated
    value. The final score is the arithmetic mean of known window scores.
    """

    windows = (
        ("7-day", weather.avg_temp_7d_c),
        ("14-day", weather.avg_temp_14d_c),
        ("20-day", weather.avg_temp_20d_c),
    )

    scores: list[float] = []
    reasons: list[str] = []

    for label, temperature_c in windows:
        if temperature_c is None:
            reasons.append(
                f"{label} mean temperature is unknown; "
                "no temperature score was inferred from this window."
            )
            continue

        score = _score_temperature_c(temperature_c)
        scores.append(score)
        reasons.append(
            f"{label} mean temperature {temperature_c:.2f} °C "
            f"maps to Steinpilz v0.1 temperature score {score:.2f}."
        )

    if not scores:
        return SteinpilzTemperatureInterpretation(
            score=None,
            reasons=tuple(reasons),
        )

    return SteinpilzTemperatureInterpretation(
        score=sum(scores) / len(scores),
        reasons=tuple(reasons),
    )
