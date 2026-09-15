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
        ecologically_eligible=True,
        reasons=["baseline test"],
    )
    values.update(overrides)
    return SpotFeatures(**values)


def test_good_spot_scores_high():
    result = score_spot(good_features())

    assert result.eligible is True
    assert result.opportunity_score is not None
    assert result.opportunity_score >= 80
    assert result.habitat_score is not None
    assert result.habitat_score >= 80


def test_legal_exclusion_overrides_ecology():
    result = score_spot(good_features(collecting_allowed=False))

    assert result.eligible is False
    assert result.opportunity_score == 0
    assert "Hard exclusion" in result.reasons[0]


def test_unknown_legal_status_is_not_hard_exclusion():
    result = score_spot(good_features(collecting_allowed=None))

    assert result.eligible is None
    assert result.opportunity_score is not None
    assert result.opportunity_score > 0
    assert result.reasons == ["baseline test"]


def test_confidence_tracks_data_completeness():
    result = score_spot(good_features(data_completeness=0.42))

    assert result.confidence == 42.0


def test_inputs_are_clamped():
    result = score_spot(
        good_features(
            host_tree_score=5,
            moisture_score=-3,
        )
    )

    assert result.opportunity_score is not None
    assert 0 <= result.opportunity_score <= 100


def test_missing_component_is_not_treated_as_zero():
    result = score_spot(
        good_features(
            host_tree_score=None,
            data_completeness=None,
        )
    )

    assert result.habitat_score is not None
    assert result.opportunity_score is not None
    assert result.opportunity_score > 0
    assert result.confidence == 75.0


def test_missing_observation_does_not_use_artificial_neutral_value():
    with_observation = score_spot(
        good_features(
            observation_score=0.5,
            data_completeness=None,
        )
    )

    without_observation = score_spot(
        good_features(
            observation_score=None,
            data_completeness=None,
        )
    )

    assert without_observation.opportunity_score is not None
    assert without_observation.confidence == 95.0
    assert with_observation.confidence == 100.0


def test_all_ecological_components_missing_produces_unknown_scores():
    result = score_spot(
        SpotFeatures(
            host_tree_score=None,
            soil_geology_score=None,
            moisture_score=None,
            temperature_season_score=None,
            terrain_score=None,
            forest_maturity_score=None,
            indicator_vegetation_score=None,
            observation_score=None,
            data_completeness=None,
            collecting_allowed=None,
        )
    )

    assert result.eligible is None
    assert result.habitat_score is None
    assert result.current_conditions_score is None
    assert result.opportunity_score is None
    assert result.confidence == 0.0

def test_ecological_exclusion_overrides_score():
    result = score_spot(
        good_features(
            ecologically_eligible=False,
            reasons=["Ecological exclusion: non-forest."],
        )
    )

    assert result.eligible is False
    assert result.opportunity_score == 0.0
    assert "Ecological exclusion" in result.reasons[0]


def test_unknown_ecological_eligibility_is_not_exclusion():
    result = score_spot(
        good_features(
            ecologically_eligible=None,
        )
    )

    assert result.eligible is None
    assert result.opportunity_score is not None
    assert result.opportunity_score > 0
