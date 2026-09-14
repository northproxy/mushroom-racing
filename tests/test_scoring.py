from mushroom_racing.models import SpotFeatures
from mushroom_racing.scoring import score_spot


def good_features(**overrides):
    values = dict(
        host_tree_score=0.9,
        soil_geology_score=0.9,
        moisture_score=0.9,
        temperature_season_score=0.8,
        terrain_score=0.9,
        forest_maturity_score=0.8,
        indicator_vegetation_score=0.9,
        observation_score=0.5,
        data_completeness=0.7,
        collecting_allowed=True,
        reasons=["baseline test"],
    )
    values.update(overrides)
    return SpotFeatures(**values)


def test_good_spot_scores_high():
    result = score_spot(good_features())
    assert result.eligible is True
    assert result.opportunity_score >= 80
    assert result.habitat_score >= 80


def test_legal_exclusion_overrides_ecology():
    result = score_spot(good_features(collecting_allowed=False))
    assert result.eligible is False
    assert result.opportunity_score == 0
    assert "Hard exclusion" in result.reasons[0]


def test_confidence_tracks_data_completeness():
    result = score_spot(good_features(data_completeness=0.42))
    assert result.confidence == 42.0


def test_inputs_are_clamped():
    result = score_spot(good_features(host_tree_score=5, moisture_score=-3))
    assert 0 <= result.opportunity_score <= 100
