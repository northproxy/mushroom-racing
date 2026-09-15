"""
File: features.py
Project: mushroom-racing

Purpose:
    Вычисляет локальные terrain features из ElevationWindow:
    центральную высоту, уклон и экспозицию склона.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — часть terrain feature extraction layer.

Inputs:
    ElevationWindow с регулярной DEM-сеткой.

Outputs:
    TerrainFeatures: elevation_m, slope_deg, aspect_deg.

Dependencies:
    Python standard library
    numpy
    mushroom_racing.terrain.elevation

Used by:
    MR-2 terrain pipeline;
    позже — сборка SpotFeatures.

Notes:
    Для slope/aspect используется центральное окно 3x3 и Horn gradient.
    EPSG:3857 требует локальной поправки масштаба Web Mercator.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .elevation import ElevationWindow


_WEB_MERCATOR_RADIUS_M = 6_378_137.0
_FLAT_GRADIENT_EPSILON = 1e-12


class TerrainFeatureError(ValueError):
    """Ошибка вычисления terrain features из DEM-окна."""


@dataclass(frozen=True, slots=True)
class TerrainFeatures:
    """Локальные terrain features для центральной ячейки DEM."""

    elevation_m: float
    slope_deg: float
    aspect_deg: float | None


def extract_terrain_features(window: ElevationWindow) -> TerrainFeatures:
    """
    Вычисляет terrain features для центральной ячейки ElevationWindow.

    Для slope и aspect используется центральное соседство 3x3.
    Aspect задаётся как направление вниз по склону по часовой стрелке
    от географического севера:

        0°   = north
        90°  = east
        180° = south
        270° = west

    Для практически плоской поверхности aspect не определён и
    возвращается как None.
    """
    _validate_window_shape(window)

    center_row = window.height // 2
    center_col = window.width // 2

    patch = window.values[
        center_row - 1 : center_row + 2,
        center_col - 1 : center_col + 2,
    ]

    _validate_patch(patch, window.nodata)

    resolution_x_m, resolution_y_m = _ground_resolution_m(window)

    dz_dx, dz_dy = _horn_gradient(
        patch,
        resolution_x_m=resolution_x_m,
        resolution_y_m=resolution_y_m,
    )

    gradient = math.hypot(dz_dx, dz_dy)
    slope_deg = math.degrees(math.atan(gradient))

    if gradient <= _FLAT_GRADIENT_EPSILON:
        aspect_deg: float | None = None
    else:
        # Gradient показывает направление максимального подъёма.
        # Для aspect нам нужно противоположное направление — вниз по склону.
        #
        # atan2(east, north) даёт азимут по часовой стрелке от севера.
        aspect_deg = math.degrees(
            math.atan2(-dz_dx, -dz_dy)
        ) % 360.0

    return TerrainFeatures(
        elevation_m=float(window.values[center_row, center_col]),
        slope_deg=slope_deg,
        aspect_deg=aspect_deg,
    )


def _validate_window_shape(window: ElevationWindow) -> None:
    if window.height < 3 or window.width < 3:
        raise TerrainFeatureError(
            "Elevation window must be at least 3x3 "
            "to calculate slope and aspect."
        )

    if window.height % 2 == 0 or window.width % 2 == 0:
        raise TerrainFeatureError(
            "Elevation window dimensions must be odd "
            "to define a unique center cell."
        )


def _validate_patch(
    patch: np.ndarray,
    nodata: float | None,
) -> None:
    if patch.shape != (3, 3):
        raise TerrainFeatureError(
            "Central elevation neighborhood must be exactly 3x3."
        )

    if nodata is not None:
        if math.isnan(nodata):
            if np.isnan(patch).any():
                raise TerrainFeatureError(
                    "Central 3x3 elevation neighborhood contains nodata."
                )
        elif np.equal(patch, nodata).any():
            raise TerrainFeatureError(
                "Central 3x3 elevation neighborhood contains nodata."
            )

    if not np.isfinite(patch).all():
        raise TerrainFeatureError(
            "Central 3x3 elevation neighborhood contains "
            "non-finite values."
        )


def _ground_resolution_m(
    window: ElevationWindow,
) -> tuple[float, float]:
    crs = window.crs.strip().upper()

    if crs == "EPSG:31259":
        return window.resolution_x, window.resolution_y

    if crs == "EPSG:3857":
        latitude_rad = _web_mercator_center_latitude_rad(window)

        # Web Mercator имеет локальный scale factor sec(latitude).
        # Поэтому один projected metre соответствует примерно
        # cos(latitude) ground metres.
        ground_scale = math.cos(latitude_rad)

        if ground_scale <= 0.0:
            raise TerrainFeatureError(
                "Cannot derive a valid ground resolution "
                "from EPSG:3857 window."
            )

        return (
            window.resolution_x * ground_scale,
            window.resolution_y * ground_scale,
        )

    raise TerrainFeatureError(
        f"Unsupported CRS for terrain feature extraction: {window.crs!r}."
    )


def _web_mercator_center_latitude_rad(
    window: ElevationWindow,
) -> float:
    _, bottom, _, top = window.bounds
    center_y = (bottom + top) / 2.0

    # Для spherical Web Mercator:
    #
    #     latitude = atan(sinh(y / R))
    #
    # Это обратное преобразование EPSG:3857 -> geographic latitude.
    return math.atan(
        math.sinh(center_y / _WEB_MERCATOR_RADIUS_M)
    )


def _horn_gradient(
    patch: np.ndarray,
    *,
    resolution_x_m: float,
    resolution_y_m: float,
) -> tuple[float, float]:
    """
    Вычисляет dz/dx и dz/dy методом Horn по DEM-окну 3x3.

    Строки массива идут с севера на юг, столбцы — с запада на восток.
    dz/dx положителен при росте высоты на восток.
    dz/dy положителен при росте высоты на север.
    """
    (
        z1,
        z2,
        z3,
        z4,
        _z5,
        z6,
        z7,
        z8,
        z9,
    ) = map(float, patch.ravel())

    dz_dx = (
        (z3 + 2.0 * z6 + z9)
        - (z1 + 2.0 * z4 + z7)
    ) / (8.0 * resolution_x_m)

    dz_dy = (
        (z1 + 2.0 * z2 + z3)
        - (z7 + 2.0 * z8 + z9)
    ) / (8.0 * resolution_y_m)

    return dz_dx, dz_dy
