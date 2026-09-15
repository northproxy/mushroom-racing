from datetime import datetime, timezone

import numpy as np
import pytest

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.forest import ForestResult, ForestStatus
from mushroom_racing.geology import GeologyQueryResult
from mushroom_racing.geospatial_assembly import GeospatialFeatureAssembler
from mushroom_racing.terrain import ElevationWindow


class StubElevationProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[float, float, float]] = []

    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        self.calls.append((latitude, longitude, radius_m))

        return ElevationWindow(
            values=np.asarray(
                [
                    [100.0, 100.0, 100.0],
                    [100.0, 100.0, 100.0],
                    [100.0, 100.0, 100.0],
                ],
                dtype=np.float32,
            ),
            bounds=(0.0, 0.0, 30.0, 30.0),
            crs="EPSG:31259",
        )


class StubForestProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[float, float]] = []

    def get_forest_status(
        self,
        latitude: float,
        longitude: float,
    ) -> ForestResult:
        self.calls.append((latitude, longitude))
        return ForestResult(status=ForestStatus.FOREST)


class StubGeologyProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[float, float]] = []

    def get_geology(
        self,
        latitude: float,
        longitude: float,
    ) -> GeologyQueryResult:
        self.calls.append((latitude, longitude))
        return GeologyQueryResult(records=())


def _weather(
    *,
    spot_id: str = "test_spot",
) -> WeatherSnapshot:
    return WeatherSnapshot(
        spot_id=spot_id,
        timestamp=datetime(2026, 9, 15, tzinfo=timezone.utc),
        source_id="test_weather_source",
        rain_14d_mm=42.0,
    )


def test_assembler_builds_unified_feature_set() -> None:
    elevation_provider = StubElevationProvider()
    forest_provider = StubForestProvider()
    geology_provider = StubGeologyProvider()

    assembler = GeospatialFeatureAssembler(
        elevation_provider=elevation_provider,
        forest_provider=forest_provider,
        geology_provider=geology_provider,
    )

    weather = _weather()

    features = assembler.assemble(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        weather=weather,
    )

    assert features.spot_id == "test_spot"
    assert features.latitude == 47.72
    assert features.longitude == 15.90

    assert features.terrain.elevation_m == pytest.approx(100.0)
    assert features.terrain.slope_deg == pytest.approx(0.0)
    assert features.terrain.aspect_deg is None

    assert features.forest.status is ForestStatus.FOREST
    assert features.geology.records == ()
    assert features.weather is weather
    assert features.collecting_allowed is None


def test_assembler_passes_coordinate_to_all_providers() -> None:
    elevation_provider = StubElevationProvider()
    forest_provider = StubForestProvider()
    geology_provider = StubGeologyProvider()

    assembler = GeospatialFeatureAssembler(
        elevation_provider=elevation_provider,
        forest_provider=forest_provider,
        geology_provider=geology_provider,
        terrain_radius_m=20.0,
    )

    assembler.assemble(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        weather=_weather(),
    )

    assert elevation_provider.calls == [(47.72, 15.90, 20.0)]
    assert forest_provider.calls == [(47.72, 15.90)]
    assert geology_provider.calls == [(47.72, 15.90)]


def test_assembler_preserves_manual_legal_status() -> None:
    assembler = GeospatialFeatureAssembler(
        elevation_provider=StubElevationProvider(),
        forest_provider=StubForestProvider(),
        geology_provider=StubGeologyProvider(),
    )

    features = assembler.assemble(
        spot_id="test_spot",
        latitude=47.72,
        longitude=15.90,
        weather=_weather(),
        collecting_allowed=False,
    )

    assert features.collecting_allowed is False


def test_assembler_rejects_weather_for_different_spot_before_provider_calls() -> None:
    elevation_provider = StubElevationProvider()
    forest_provider = StubForestProvider()
    geology_provider = StubGeologyProvider()

    assembler = GeospatialFeatureAssembler(
        elevation_provider=elevation_provider,
        forest_provider=forest_provider,
        geology_provider=geology_provider,
    )

    with pytest.raises(
        ValueError,
        match="weather.spot_id must match requested spot_id",
    ):
        assembler.assemble(
            spot_id="test_spot",
            latitude=47.72,
            longitude=15.90,
            weather=_weather(spot_id="different_spot"),
        )

    assert elevation_provider.calls == []
    assert forest_provider.calls == []
    assert geology_provider.calls == []


@pytest.mark.parametrize(
    "terrain_radius_m",
    [
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
    ],
)
def test_assembler_rejects_invalid_terrain_radius(
    terrain_radius_m: float,
) -> None:
    with pytest.raises(ValueError):
        GeospatialFeatureAssembler(
            elevation_provider=StubElevationProvider(),
            forest_provider=StubForestProvider(),
            geology_provider=StubGeologyProvider(),
            terrain_radius_m=terrain_radius_m,
        )
