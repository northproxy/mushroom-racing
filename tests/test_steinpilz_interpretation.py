from types import SimpleNamespace
from typing import cast

import pytest

from mushroom_racing.forest import ForestResult, ForestStatus
from mushroom_racing.geospatial_features import GeospatialFeatureSet
from mushroom_racing.steinpilz_geology import SteinpilzGeologyAffinity
from mushroom_racing.steinpilz_interpretation import (
    _geology_score,
    interpret_steinpilz_features,
)


def make_features(
    forest_status: ForestStatus,
    *,
    collecting_allowed: bool | None = None,
    geology=None,
    terrain=None,
    weather=None,
) -> GeospatialFeatureSet:
    """Create a minimal MR-5 interpretation stub.

    Полная валидация GeospatialFeatureSet уже покрывается MR-3 tests.
    Здесь тестируется только species-specific interpretation boundary.
    """

    if geology is None:
        geology = SimpleNamespace(records=())

    if terrain is None:
        terrain = SimpleNamespace(
            elevation_m=1000.0,
            slope_deg=15.0,
            aspect_deg=0.0,
        )

    if weather is None:
        weather = SimpleNamespace(
            avg_temp_7d_c=None,
            avg_temp_14d_c=None,
            avg_temp_20d_c=None,
        )

    stub = SimpleNamespace(
        forest=ForestResult(status=forest_status),
        geology=geology,
        terrain=terrain,
        weather=weather,
        collecting_allowed=collecting_allowed,
    )

    return cast(GeospatialFeatureSet, stub)


def geology_record(
    *,
    material=None,
    representative_lithology=None,
):
    return SimpleNamespace(
        material=material,
        representative_lithology=representative_lithology,
    )


def test_forest_is_ecologically_eligible():
    result = interpret_steinpilz_features(
        make_features(ForestStatus.FOREST)
    )

    assert result.ecologically_eligible is True

    assert result.host_tree_score is None
    assert result.soil_geology_score is None
    assert result.moisture_score is None
    assert result.temperature_season_score is None
    assert result.terrain_score == 0.65

    assert "Forest cover confirmed" in result.reasons[0]


def test_non_forest_is_ecological_exclusion():
    result = interpret_steinpilz_features(
        make_features(ForestStatus.NON_FOREST)
    )

    assert result.ecologically_eligible is False
    assert "Ecological exclusion" in result.reasons[0]


def test_unknown_forest_is_not_exclusion():
    result = interpret_steinpilz_features(
        make_features(ForestStatus.UNKNOWN)
    )

    assert result.ecologically_eligible is None
    assert "unknown" in result.reasons[0].lower()


def test_legal_status_is_preserved():
    result = interpret_steinpilz_features(
        make_features(
            ForestStatus.FOREST,
            collecting_allowed=None,
        )
    )

    assert result.collecting_allowed is None


def test_missing_species_features_are_not_fabricated():
    result = interpret_steinpilz_features(
        make_features(ForestStatus.FOREST)
    )

    assert result.host_tree_score is None
    assert result.soil_geology_score is None
    assert result.forest_maturity_score is None
    assert result.indicator_vegetation_score is None
    assert result.observation_score is None


def test_favourable_geology_maps_to_positive_baseline_score():
    assert _geology_score(
        SteinpilzGeologyAffinity.FAVOURABLE
    ) == 0.75


def test_unfavourable_geology_maps_to_negative_baseline_score():
    assert _geology_score(
        SteinpilzGeologyAffinity.UNFAVOURABLE
    ) == 0.25


def test_mixed_geology_remains_unknown_for_scoring():
    assert _geology_score(
        SteinpilzGeologyAffinity.MIXED
    ) is None


def test_unknown_geology_remains_unknown_for_scoring():
    assert _geology_score(
        SteinpilzGeologyAffinity.UNKNOWN
    ) is None


def test_limestone_sets_unfavourable_geology_component():
    features = make_features(
        ForestStatus.FOREST,
        geology=SimpleNamespace(
            records=(
                geology_record(
                    material="limestone",
                    representative_lithology="limestone",
                ),
            )
        ),
    )

    result = interpret_steinpilz_features(features)

    assert result.soil_geology_score == 0.25
    assert any(
        "Carbonate-like" in reason
        for reason in result.reasons
    )


def test_unknown_geology_does_not_create_neutral_score():
    result = interpret_steinpilz_features(
        make_features(
            ForestStatus.FOREST,
            geology=SimpleNamespace(records=()),
        )
    )

    assert result.soil_geology_score is None


def test_terrain_component_is_added_to_spot_features():
    result = interpret_steinpilz_features(
        make_features(ForestStatus.FOREST)
    )

    assert result.terrain_score == 0.65
    assert any("Elevation" in reason for reason in result.reasons)
    assert any("Slope" in reason for reason in result.reasons)
    assert any("Aspect" in reason for reason in result.reasons)


def test_temperature_component_is_added_to_spot_features():
    result = interpret_steinpilz_features(
        make_features(
            ForestStatus.FOREST,
            weather=SimpleNamespace(
                avg_temp_7d_c=14.04,
                avg_temp_14d_c=15.20,
                avg_temp_20d_c=15.68,
            ),
        )
    )

    assert result.temperature_season_score == pytest.approx(0.80)
    assert any(
        "7-day mean temperature" in reason
        for reason in result.reasons
    )


def test_missing_temperature_does_not_create_neutral_score():
    result = interpret_steinpilz_features(
        make_features(ForestStatus.FOREST)
    )

    assert result.temperature_season_score is None
