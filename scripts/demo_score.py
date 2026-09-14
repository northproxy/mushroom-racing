from mushroom_racing.models import SpotFeatures
from mushroom_racing.scoring import score_spot


sample = SpotFeatures(
    host_tree_score=0.95,
    soil_geology_score=0.90,
    moisture_score=0.85,
    temperature_season_score=0.80,
    terrain_score=0.90,
    forest_maturity_score=0.80,
    indicator_vegetation_score=0.90,
    observation_score=0.50,
    data_completeness=0.65,
    collecting_allowed=True,
    reasons=[
        "+ strong Fichte/Buche/Tanne suitability",
        "+ acidic/silicate geology",
        "+ recent rainfall supports moisture",
        "+ north-east slope",
        "- no calibrated field-history signal yet",
    ],
)

result = score_spot(sample)

print(f"Eligible: {result.eligible}")
print(f"Habitat: {result.habitat_score}/100")
print(f"Current conditions: {result.current_conditions_score}/100")
print(f"Opportunity: {result.opportunity_score}/100")
print(f"Confidence: {result.confidence}/100")
print("Reasons:")
for reason in result.reasons:
    print(f"  {reason}")
