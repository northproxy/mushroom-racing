from dataclasses import dataclass, field


@dataclass(slots=True)
class SpotFeatures:
    """Minimal feature set for the baseline scoring model.

    Component values are normalized to the 0..1 range.

    None means that the corresponding information is unknown and must not
    be silently interpreted as a neutral, negative, or positive signal.
    """

    host_tree_score: float | None
    soil_geology_score: float | None
    moisture_score: float | None
    temperature_season_score: float | None
    terrain_score: float | None
    forest_maturity_score: float | None
    indicator_vegetation_score: float | None
    observation_score: float | None = None
    data_completeness: float | None = None
    collecting_allowed: bool | None = None
    ecologically_eligible: bool | None = None
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScoreResult:
    eligible: bool | None
    habitat_score: float | None
    current_conditions_score: float | None
    opportunity_score: float | None
    confidence: float
    reasons: list[str]
