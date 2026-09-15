"""
File: steinpilz_terrain.py
Project: mushroom-racing

Purpose:
    Выполняет осторожную species-specific interpretation terrain features
    для Boletus edulis.

Created:
    2026-09-16

Last modified:
    2026-09-16

Status:
    active

Lifecycle:
    permanent — часть Steinpilz interpretation layer.

Inputs:
    TerrainFeatures.

Outputs:
    SteinpilzTerrainInterpretation.

Dependencies:
    Python standard library
    mushroom_racing.terrain

Used by:
    MR-5 Steinpilz interpretation pipeline.

Notes:
    Числовые thresholds являются baseline working hypotheses.

    Aspect имеет только слабое влияние, поскольку текущая версия ещё
    не содержит drought context. Terrain score не является доказательством
    пригодности habitat сам по себе.
"""

from __future__ import annotations

from dataclasses import dataclass

from mushroom_racing.terrain import TerrainFeatures


@dataclass(frozen=True, slots=True)
class SteinpilzTerrainInterpretation:
    """Результат baseline terrain interpretation."""

    score: float
    reasons: tuple[str, ...]


def _elevation_score(elevation_m: float) -> float:
    """Return a mild v0.1 elevation contribution."""

    if 650.0 <= elevation_m <= 1300.0:
        return 0.70

    if 400.0 <= elevation_m < 650.0:
        return 0.60

    if 1300.0 < elevation_m <= 1500.0:
        return 0.60

    return 0.50


def _slope_score(slope_deg: float) -> float:
    """Keep slope influence deliberately weak in v0.1."""

    if slope_deg <= 25.0:
        return 0.60

    if slope_deg <= 40.0:
        return 0.50

    return 0.40


def _aspect_score(aspect_deg: float) -> float:
    """Return a weak aspect contribution without drought context."""

    if aspect_deg >= 292.5 or aspect_deg < 67.5:
        return 0.60

    if 67.5 <= aspect_deg < 112.5:
        return 0.55

    if 247.5 <= aspect_deg < 292.5:
        return 0.55

    return 0.45


def interpret_steinpilz_terrain(
    terrain: TerrainFeatures,
) -> SteinpilzTerrainInterpretation:
    """Interpret elevation, slope and aspect as a mild terrain signal."""

    elevation = _elevation_score(terrain.elevation_m)
    slope = _slope_score(terrain.slope_deg)
    aspect = _aspect_score(terrain.aspect_deg)

    # Elevation получает наибольший baseline-вес.
    # Aspect ограничен, потому что его значение сильно зависит
    # от текущего moisture/drought context, которого в v0.1 пока нет.
    score = (
        elevation * 0.50
        + slope * 0.20
        + aspect * 0.30
    )

    reasons = (
        (
            f"Elevation {terrain.elevation_m:.0f} m contributes "
            f"{elevation:.2f} to the Steinpilz terrain baseline."
        ),
        (
            f"Slope {terrain.slope_deg:.1f}° contributes "
            f"{slope:.2f} to the terrain baseline."
        ),
        (
            f"Aspect {terrain.aspect_deg:.1f}° has only weak influence "
            f"without drought context and contributes {aspect:.2f}."
        ),
    )

    return SteinpilzTerrainInterpretation(
        score=round(score, 3),
        reasons=reasons,
    )
