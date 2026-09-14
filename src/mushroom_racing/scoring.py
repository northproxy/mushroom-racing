from .models import ScoreResult, SpotFeatures


WEIGHTS = {
    "host_tree_score": 0.25,
    "soil_geology_score": 0.20,
    "moisture_score": 0.20,
    "temperature_season_score": 0.10,
    "terrain_score": 0.10,
    "forest_maturity_score": 0.05,
    "indicator_vegetation_score": 0.05,
    "observation_score": 0.05,
}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_spot(features: SpotFeatures) -> ScoreResult:
    """Calculate the initial explainable MR-0 score.

    This is a baseline engineering model, not a validated biological predictor.
    """
    if not features.collecting_allowed:
        return ScoreResult(
            eligible=False,
            habitat_score=0.0,
            current_conditions_score=0.0,
            opportunity_score=0.0,
            confidence=round(_clamp01(features.data_completeness) * 100, 1),
            reasons=["Hard exclusion: collecting is not allowed."],
        )

    values = {
        key: _clamp01(getattr(features, key))
        for key in WEIGHTS
    }

    habitat = (
        values["host_tree_score"] * 0.45
        + values["soil_geology_score"] * 0.35
        + values["forest_maturity_score"] * 0.10
        + values["indicator_vegetation_score"] * 0.10
    )

    current = (
        values["moisture_score"] * 0.50
        + values["temperature_season_score"] * 0.25
        + values["terrain_score"] * 0.15
        + values["observation_score"] * 0.10
    )

    weighted_total = sum(values[name] * weight for name, weight in WEIGHTS.items())

    return ScoreResult(
        eligible=True,
        habitat_score=round(habitat * 100, 1),
        current_conditions_score=round(current * 100, 1),
        opportunity_score=round(weighted_total * 100, 1),
        confidence=round(_clamp01(features.data_completeness) * 100, 1),
        reasons=list(features.reasons),
    )
