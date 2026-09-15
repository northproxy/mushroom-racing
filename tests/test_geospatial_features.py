from datetime import datetime, timezone

import pytest

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.forest import ForestResult, ForestStatus
from mushroom_racing.geology import GeologyQueryResult, GeologyRecord
from mushroom_racing.geospatial_features import GeospatialFeatureSet
from mushroom_racing.terrain import TerrainFeatures


def _weather(
    *,
    spot_id: str = "test_spot",
    rain_14d_mm: float | None = 42.0,
) -> WeatherSnapshot:
    return WeatherSnapshot(
        spot_id=spot_id,
        timestamp=datetime(2026, 9, 15, tzinfo=timezone.utc),
        source_id="test_weather_source",
        rain_14d_mm=rain_14d_mm,
    )


def _terrain() -> TerrainFeatures:
    return TerrainFeatures(
        elevation_m=850.0,
        slope_deg=12.0,
        aspect_deg=30.0,
    )


def test_geospatial_feature_set_preserves_normalized_inputs() -> None:
    terrain = _terrain()
    forest = ForestResult(status=ForestStatus.FOREST)
    geology = GeologyQueryResult(records=())
    weather = _weather()

    features = GeospatialFeatureSet(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        terrain=terrain,
        forest=forest,
        geology=geology,
        weather=weather,
        collecting_allowed=None,
    )

    assert features.terrain is terrain
    assert features.forest is forest
    assert features.geology is geology
    assert features.weather is weather


def test_geospatial_feature_set_preserves_unknown_forest_status() -> None:
    features = GeospatialFeatureSet(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        terrain=_terrain(),
        forest=ForestResult(status=ForestStatus.UNKNOWN),
        geology=GeologyQueryResult(records=()),
        weather=_weather(),
    )

    assert features.forest.status is ForestStatus.UNKNOWN


def test_geospatial_feature_set_preserves_unknown_legal_status() -> None:
    features = GeospatialFeatureSet(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        terrain=_terrain(),
        forest=ForestResult(status=ForestStatus.FOREST),
        geology=GeologyQueryResult(records=()),
        weather=_weather(),
        collecting_allowed=None,
    )

    assert features.collecting_allowed is None


def test_geospatial_feature_set_preserves_missing_weather_value() -> None:
    features = GeospatialFeatureSet(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        terrain=_terrain(),
        forest=ForestResult(status=ForestStatus.FOREST),
        geology=GeologyQueryResult(records=()),
        weather=_weather(rain_14d_mm=None),
    )

    assert features.weather.rain_14d_mm is None


def test_geospatial_feature_set_preserves_multiple_geology_records() -> None:
    records = (
        GeologyRecord(
            identifier="feature-1",
            name="Unit A",
            description=None,
            geologic_unit_type=None,
            material="limestone",
            representative_lithology="limestone",
        ),
        GeologyRecord(
            identifier="feature-2",
            name="Unit B",
            description=None,
            geologic_unit_type=None,
            material="breccia",
            representative_lithology="breccia",
        ),
    )

    features = GeospatialFeatureSet(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        terrain=_terrain(),
        forest=ForestResult(status=ForestStatus.FOREST),
        geology=GeologyQueryResult(records=records),
        weather=_weather(),
    )

    assert features.geology.records == records
    assert len(features.geology.records) == 2


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (91.0, 15.90),
        (-91.0, 15.90),
        (47.72, 181.0),
        (47.72, -181.0),
        (float("nan"), 15.90),
        (47.72, float("inf")),
    ],
)
def test_geospatial_feature_set_rejects_invalid_coordinates(
    latitude: float,
    longitude: float,
) -> None:
    with pytest.raises(ValueError):
        GeospatialFeatureSet(
            spot_id="test_spot",
            latitude=latitude,
            longitude=longitude,
            terrain=_terrain(),
            forest=ForestResult(status=ForestStatus.FOREST),
            geology=GeologyQueryResult(records=()),
            weather=_weather(),
        )


def test_geospatial_feature_set_rejects_weather_from_different_spot() -> None:
    with pytest.raises(
        ValueError,
        match="weather.spot_id must match",
    ):
        GeospatialFeatureSet(
            spot_id="test_spot",
            latitude=47.72,
            longitude=15.90,
            terrain=_terrain(),
            forest=ForestResult(status=ForestStatus.FOREST),
            geology=GeologyQueryResult(records=()),
            weather=_weather(spot_id="different_spot"),
        )
