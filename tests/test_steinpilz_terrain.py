from types import SimpleNamespace

import pytest

from mushroom_racing.steinpilz_terrain import (
    _aspect_score,
    _elevation_score,
    _slope_score,
    interpret_steinpilz_terrain,
)


def terrain(
    *,
    elevation_m=1000.0,
    slope_deg=15.0,
    aspect_deg=0.0,
):
    return SimpleNamespace(
        elevation_m=elevation_m,
        slope_deg=slope_deg,
        aspect_deg=aspect_deg,
    )


def test_core_elevation_band_gets_moderate_positive_score():
    assert _elevation_score(1000.0) == 0.70


def test_outer_elevation_is_not_hard_exclusion():
    assert _elevation_score(1700.0) == 0.50


def test_moderate_slope_gets_mild_positive_score():
    assert _slope_score(15.0) == 0.60


def test_steep_slope_gets_small_penalty():
    assert _slope_score(45.0) == 0.40


@pytest.mark.parametrize(
    "aspect_deg",
    [0.0, 30.0, 330.0],
)
def test_northern_aspects_get_only_weak_bonus(aspect_deg):
    assert _aspect_score(aspect_deg) == 0.60


@pytest.mark.parametrize(
    "aspect_deg",
    [135.0, 180.0, 225.0],
)
def test_southern_aspects_get_only_weak_penalty(aspect_deg):
    assert _aspect_score(aspect_deg) == 0.45


def test_control_coordinate_terrain_score():
    result = interpret_steinpilz_terrain(
        terrain(
            elevation_m=1212.0,
            slope_deg=13.23,
            aspect_deg=341.565,
        )
    )

    assert result.score == 0.65
    assert len(result.reasons) == 3
