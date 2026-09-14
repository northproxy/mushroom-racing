from dataclasses import dataclass, field


@dataclass(slots=True)
class SpotFeatures:
    """Minimal feature set for the MR-0 scoring baseline.

    Values are normalized to the 0..1 range unless otherwise noted.
    """

    host_tree_score: float
    soil_geology_score: float
    moisture_score: float
    temperature_season_score: float
    terrain_score: float
    forest_maturity_score: float
    indicator_vegetation_score: float
    observation_score: float = 0.5
    data_completeness: float = 0.5
    collecting_allowed: bool = True
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScoreResult:
    eligible: bool
    habitat_score: float
    current_conditions_score: float
    opportunity_score: float
    confidence: float
    reasons: list[str]
