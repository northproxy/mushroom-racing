"""
File: steinpilz_interpretation.py
Project: mushroom-racing

Purpose:
    Преобразует species-agnostic GeospatialFeatureSet в текущий
    scoring contract для Boletus edulis.

Created:
    2026-09-15

Last modified:
    2026-09-16

Status:
    active

Lifecycle:
    permanent — species-specific interpretation layer между MR-3
    geospatial features и scoring engine.

Inputs:
    GeospatialFeatureSet.

Outputs:
    SpotFeatures для baseline scoring engine.

Dependencies:
    Python standard library
    mushroom_racing.forest
    mushroom_racing.geospatial_features
    mushroom_racing.models
    mushroom_racing.steinpilz_geology
    mushroom_racing.steinpilz_terrain
    mushroom_racing.steinpilz_temperature

Used by:
    MR-5 Steinpilz scoring pipeline.

Notes:
    Текущая версия интерпретирует forest eligibility, raw geology,
    terrain и temperature context.

    Geology используется только как species-specific baseline proxy.
    Она не подменяет soil type, soil pH или другие измеренные свойства
    почвы.

    Terrain используется как мягкий baseline signal. Влияние aspect
    намеренно ограничено, потому что drought context пока отсутствует.

    Числовые отображения geology affinity, terrain и temperature rules являются
    working hypotheses Steinpilz v0.1 и должны позже калиброваться.
"""

from __future__ import annotations

from mushroom_racing.forest import ForestStatus
from mushroom_racing.geospatial_features import GeospatialFeatureSet
from mushroom_racing.models import SpotFeatures
from mushroom_racing.steinpilz_geology import (
    SteinpilzGeologyAffinity,
    interpret_steinpilz_geology,
)
from mushroom_racing.steinpilz_terrain import interpret_steinpilz_terrain
from mushroom_racing.steinpilz_temperature import (
    interpret_steinpilz_temperature,
)

def _geology_score(
    affinity: SteinpilzGeologyAffinity,
) -> float | None:
    """Map geology affinity to a conservative v0.1 scoring component."""

    if affinity is SteinpilzGeologyAffinity.FAVOURABLE:
        return 0.75

    if affinity is SteinpilzGeologyAffinity.UNFAVOURABLE:
        return 0.25

    return None


def interpret_steinpilz_features(
    features: GeospatialFeatureSet,
) -> SpotFeatures:
    """Build current Steinpilz-specific scoring features.

    Forest-mask data determine basic ecological eligibility.

    Raw geology is interpreted separately as a cautious species-specific
    proxy. Mixed or unknown geology does not create a fabricated neutral
    score and therefore remains None.

    Terrain contributes a mild baseline score from elevation, slope and
    aspect. Aspect influence remains deliberately weak until drought context
    is available.
    """

    forest_status = features.forest.status

    if forest_status is ForestStatus.FOREST:
        ecologically_eligible: bool | None = True
        reasons = [
            "Forest cover confirmed; forest presence alone does not "
            "establish Steinpilz habitat suitability."
        ]

    elif forest_status is ForestStatus.NON_FOREST:
        ecologically_eligible = False
        reasons = [
            "Ecological exclusion: source confirms non-forest land cover."
        ]

    else:
        ecologically_eligible = None
        reasons = [
            "Forest cover is unknown; no ecological exclusion was applied."
        ]

    geology = interpret_steinpilz_geology(features.geology)
    soil_geology_score = _geology_score(geology.affinity)

    terrain = interpret_steinpilz_terrain(features.terrain)
    temperature = interpret_steinpilz_temperature(features.weather)

    reasons.append(geology.reason)
    reasons.extend(terrain.reasons)
    reasons.extend(temperature.reasons)

    return SpotFeatures(
        host_tree_score=None,
        soil_geology_score=soil_geology_score,
        moisture_score=None,
        temperature_season_score=temperature.score,
        terrain_score=terrain.score,
        forest_maturity_score=None,
        indicator_vegetation_score=None,
        observation_score=None,
        data_completeness=None,
        collecting_allowed=features.collecting_allowed,
        ecologically_eligible=ecologically_eligible,
        reasons=reasons,
    )
