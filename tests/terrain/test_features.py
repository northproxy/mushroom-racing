import math

import numpy as np
import pytest

from mushroom_racing.terrain import (
    ElevationWindow,
    TerrainFeatureError,
    extract_terrain_features,
)


def _window(
    values: list[list[float]] | np.ndarray,
    *,
    crs: str = "EPSG:31259",
    bounds: tuple[float, float, float, float] | None = None,
    nodata: float | None = None,
) -> ElevationWindow:
    array = np.asarray(values, dtype=np.float32)

    if bounds is None:
        height, width = array.shape
        bounds = (
            0.0,
            0.0,
            float(width * 10),
            float(height * 10),
        )

    return ElevationWindow(
        values=array,
        bounds=bounds,
        crs=crs,
        nodata=nodata,
    )


def test_extracts_flat_terrain() -> None:
    window = _window(
        [
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
        ]
    )

    features = extract_terrain_features(window)

    assert features.elevation_m == pytest.approx(100.0)
    assert features.slope_deg == pytest.approx(0.0)
    assert features.aspect_deg is None


def test_slope_rising_east_has_western_aspect() -> None:
    window = _window(
        [
            [100.0, 110.0, 120.0],
            [100.0, 110.0, 120.0],
            [100.0, 110.0, 120.0],
        ]
    )

    features = extract_terrain_features(window)

    assert features.elevation_m == pytest.approx(110.0)
    assert features.slope_deg == pytest.approx(45.0)
    assert features.aspect_deg == pytest.approx(270.0)


def test_slope_rising_north_has_southern_aspect() -> None:
    window = _window(
        [
            [120.0, 120.0, 120.0],
            [110.0, 110.0, 110.0],
            [100.0, 100.0, 100.0],
        ]
    )

    features = extract_terrain_features(window)

    assert features.elevation_m == pytest.approx(110.0)
    assert features.slope_deg == pytest.approx(45.0)
    assert features.aspect_deg == pytest.approx(180.0)


def test_diagonal_plane_has_expected_slope_and_aspect() -> None:
    window = _window(
        [
            [120.0, 130.0, 140.0],
            [110.0, 120.0, 130.0],
            [100.0, 110.0, 120.0],
        ]
    )

    features = extract_terrain_features(window)

    expected_slope = math.degrees(math.atan(math.sqrt(2.0)))

    assert features.elevation_m == pytest.approx(120.0)
    assert features.slope_deg == pytest.approx(expected_slope)
    assert features.aspect_deg == pytest.approx(225.0)


def test_web_mercator_resolution_is_corrected_to_ground_distance() -> None:
    web_mercator_radius_m = 6_378_137.0
    latitude_rad = math.radians(60.0)

    center_y = web_mercator_radius_m * math.log(
        math.tan(math.pi / 4.0 + latitude_rad / 2.0)
    )

    window = _window(
        [
            [100.0, 101.0, 102.0],
            [100.0, 101.0, 102.0],
            [100.0, 101.0, 102.0],
        ],
        crs="EPSG:3857",
        bounds=(
            0.0,
            center_y - 15.0,
            30.0,
            center_y + 15.0,
        ),
    )

    features = extract_terrain_features(window)

    # На 60° один projected 10 m pixel соответствует примерно 5 m
    # по поверхности. Перепад 1 m на 5 m даёт gradient = 0.2.
    expected_slope = math.degrees(math.atan(0.2))

    assert features.slope_deg == pytest.approx(expected_slope)
    assert features.aspect_deg == pytest.approx(270.0)


def test_rejects_window_smaller_than_three_by_three() -> None:
    window = _window(
        [
            [100.0, 100.0, 100.0],
        ]
    )

    with pytest.raises(
        TerrainFeatureError,
        match="at least 3x3",
    ):
        extract_terrain_features(window)


def test_rejects_even_window_dimensions() -> None:
    window = _window(
        [
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
        ]
    )

    with pytest.raises(
        TerrainFeatureError,
        match="must be odd",
    ):
        extract_terrain_features(window)


def test_rejects_nodata_inside_central_neighborhood() -> None:
    window = _window(
        [
            [100.0, 100.0, 100.0],
            [100.0, -9999.0, 100.0],
            [100.0, 100.0, 100.0],
        ],
        nodata=-9999.0,
    )

    with pytest.raises(
        TerrainFeatureError,
        match="contains nodata",
    ):
        extract_terrain_features(window)


def test_ignores_nodata_outside_central_neighborhood() -> None:
    values = np.full((5, 5), 100.0, dtype=np.float32)
    values[0, 0] = -9999.0

    window = _window(
        values,
        nodata=-9999.0,
    )

    features = extract_terrain_features(window)

    assert features.elevation_m == pytest.approx(100.0)
    assert features.slope_deg == pytest.approx(0.0)
    assert features.aspect_deg is None


def test_rejects_unsupported_crs() -> None:
    window = _window(
        [
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
            [100.0, 100.0, 100.0],
        ],
        crs="EPSG:4326",
    )

    with pytest.raises(
        TerrainFeatureError,
        match="Unsupported CRS",
    ):
        extract_terrain_features(window)
