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


HABITAT_WEIGHTS = {
    "host_tree_score": 0.45,
    "soil_geology_score": 0.35,
    "forest_maturity_score": 0.10,
    "indicator_vegetation_score": 0.10,
}


CURRENT_CONDITIONS_WEIGHTS = {
    "moisture_score": 0.50,
    "temperature_season_score": 0.25,
    "terrain_score": 0.15,
    "observation_score": 0.10,
}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _weighted_average(
    values: dict[str, float | None],
    weights: dict[str, float],
) -> float | None:
    """Return a weighted average using only known component values."""

    weighted_sum = 0.0
    available_weight = 0.0

    for name, weight in weights.items():
        value = values[name]

        if value is None:
            continue

        weighted_sum += _clamp01(value) * weight
        available_weight += weight

    if available_weight == 0.0:
        return None

    return weighted_sum / available_weight


def _calculate_confidence(
    values: dict[str, float | None],
    data_completeness: float | None,
) -> float:
    """Calculate confidence separately from ecological suitability."""

    total_weight = sum(WEIGHTS.values())

    available_weight = sum(
        weight
        for name, weight in WEIGHTS.items()
        if values[name] is not None
    )

    coverage = available_weight / total_weight

    if data_completeness is not None:
        coverage *= _clamp01(data_completeness)

    return round(coverage * 100, 1)


def _combine_eligibility(
    collecting_allowed: bool | None,
    ecologically_eligible: bool | None,
) -> bool | None:
    """Combine legal and ecological eligibility without hiding unknowns."""

    if collecting_allowed is False or ecologically_eligible is False:
        return False

    if collecting_allowed is True and ecologically_eligible is True:
        return True

    return None


def _to_percent(value: float | None) -> float | None:
    if value is None:
        return None

    return round(value * 100, 1)


def score_spot(features: SpotFeatures) -> ScoreResult:
    """Calculate the explainable baseline score.

    Missing input data lower confidence but are not interpreted as negative
    ecological evidence.
    """

    if features.collecting_allowed is False:
        return ScoreResult(
            eligible=False,
            habitat_score=0.0,
            current_conditions_score=0.0,
            opportunity_score=0.0,
            confidence=0.0,
            reasons=["Hard exclusion: collecting is not allowed."],
        )

    if features.ecologically_eligible is False:
        return ScoreResult(
            eligible=False,
            habitat_score=0.0,
            current_conditions_score=0.0,
            opportunity_score=0.0,
            confidence=0.0,
            reasons=list(features.reasons),
        )

    values: dict[str, float | None] = {
        name: getattr(features, name)
        for name in WEIGHTS
    }

    habitat = _weighted_average(values, HABITAT_WEIGHTS)

    current_conditions = _weighted_average(
        values,
        CURRENT_CONDITIONS_WEIGHTS,
    )

    opportunity = _weighted_average(values, WEIGHTS)

    confidence = _calculate_confidence(
        values,
        features.data_completeness,
    )

    return ScoreResult(
        eligible=_combine_eligibility(
            features.collecting_allowed,
            features.ecologically_eligible,
        ),
        habitat_score=_to_percent(habitat),
        current_conditions_score=_to_percent(current_conditions),
        opportunity_score=_to_percent(opportunity),
        confidence=confidence,
        reasons=list(features.reasons),
    )
