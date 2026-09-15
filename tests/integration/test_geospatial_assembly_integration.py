"""
File: test_geospatial_assembly.py
Project: mushroom-racing

Purpose:
    Проверяет полный MR-3 assembly pipeline на воспроизводимом
    offline fixture, основанном на ранее проверенной Austrian
    control coordinate.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — regression test для unified geospatial feature assembly.

Inputs:
    Зафиксированные normalized outputs DEM, forest, geology и weather.

Outputs:
    Проверенный GeospatialFeatureSet.

Dependencies:
    pytest
    numpy
    mushroom_racing package

Used by:
    MR-3 validation.

Notes:
    Тест не выполняет сетевые запросы. Значения fixture представляют
    сохранённый снимок ранее проверенного live pipeline и не должны
    интерпретироваться как актуальное состояние внешних источников.
"""

from datetime import datetime, timezone

import numpy as np
import pytest

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.forest import ForestResult, ForestStatus
from mushroom_racing.geology import GeologyQueryResult, GeologyRecord
from mushroom_racing.geospatial_assembly import GeospatialFeatureAssembler
from mushroom_racing.terrain import ElevationWindow


CONTROL_LATITUDE = 47.7200
CONTROL_LONGITUDE = 15.9000
CONTROL_SPOT_ID = "control_spot"


class FixtureElevationProvider:
    """Возвращает локальный DEM fixture вместо remote source."""

    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        assert latitude == CONTROL_LATITUDE
        assert longitude == CONTROL_LONGITUDE
        assert radius_m == 10.0

        # Синтетическое 10 m DEM-окно с центральной высотой 1212 m.
        # Оно предназначено для проверки assembly, а не для повторной
        # authoritative validation реального slope/aspect.
        return ElevationWindow(
            values=np.asarray(
                [
                    [1214.0, 1214.0, 1213.0],
                    [1213.0, 1212.0, 1211.0],
                    [1212.0, 1211.0, 1210.0],
                ],
                dtype=np.float64,
            ),
            bounds=(0.0, 0.0, 30.0, 30.0),
            crs="EPSG:31259",
        )


class FixtureForestProvider:
    """Возвращает сохранённый forest-mask result control point."""

    def get_forest_status(
        self,
        latitude: float,
        longitude: float,
    ) -> ForestResult:
        assert latitude == CONTROL_LATITUDE
        assert longitude == CONTROL_LONGITUDE

        return ForestResult(status=ForestStatus.FOREST)


class FixtureGeologyProvider:
    """Возвращает сохранённый source-level geology result."""

    def get_geology(
        self,
        latitude: float,
        longitude: float,
    ) -> GeologyQueryResult:
        assert latitude == CONTROL_LATITUDE
        assert longitude == CONTROL_LONGITUDE

        return GeologyQueryResult(
            records=(
                GeologyRecord(
                    identifier="control-geology-1",
                    name="Gutenstein Formation",
                    description=None,
                    geologic_unit_type=None,
                    material="limestone",
                    representative_lithology="limestone",
                ),
            )
        )


def _weather_snapshot() -> WeatherSnapshot:
    return WeatherSnapshot(
        spot_id=CONTROL_SPOT_ID,
        timestamp=datetime(2026, 9, 12, tzinfo=timezone.utc),
        source_id="geosphere_spartacus_v3_1d_1km",
        rain_24h_mm=0.10000000149011612,
        rain_3d_mm=28.300000421702862,
        rain_7d_mm=34.50000051409006,
        rain_14d_mm=53.90000080317259,
        rain_21d_mm=58.00000086426735,
        rain_28d_mm=95.90000142902136,
        rain_90d_mm=None,
        rain_anomaly_value=None,
        rain_anomaly_method=None,
        avg_temp_7d_c=14.04,
        avg_temp_14d_c=15.20,
        avg_temp_20d_c=15.68,
        min_temp_c=None,
        max_temp_c=None,
        humidity_pct=None,
        wind_speed_m_s=None,
        soil_moisture_value=None,
        soil_moisture_method=None,
        drought_index_value=None,
        drought_index_method=None,
    )


def test_control_coordinate_builds_complete_geospatial_feature_set() -> None:
    assembler = GeospatialFeatureAssembler(
        elevation_provider=FixtureElevationProvider(),
        forest_provider=FixtureForestProvider(),
        geology_provider=FixtureGeologyProvider(),
    )

    features = assembler.assemble(
        spot_id=CONTROL_SPOT_ID,
        latitude=CONTROL_LATITUDE,
        longitude=CONTROL_LONGITUDE,
        weather=_weather_snapshot(),
        collecting_allowed=None,
    )

    assert features.spot_id == CONTROL_SPOT_ID
    assert features.latitude == CONTROL_LATITUDE
    assert features.longitude == CONTROL_LONGITUDE

    assert features.terrain.elevation_m == pytest.approx(1212.0)
    assert features.terrain.slope_deg > 0.0
    assert features.terrain.aspect_deg is not None

    assert features.forest.status is ForestStatus.FOREST

    assert len(features.geology.records) == 1
    assert features.geology.records[0].name == "Gutenstein Formation"
    assert features.geology.records[0].material == "limestone"
    assert (
        features.geology.records[0].representative_lithology
        == "limestone"
    )

    assert features.weather.rain_24h_mm == pytest.approx(0.1)
    assert features.weather.rain_14d_mm == pytest.approx(53.9)
    assert features.weather.rain_28d_mm == pytest.approx(95.9)

    assert features.weather.avg_temp_7d_c == pytest.approx(14.04)
    assert features.weather.avg_temp_14d_c == pytest.approx(15.20)
    assert features.weather.avg_temp_20d_c == pytest.approx(15.68)

    assert features.weather.rain_90d_mm is None
    assert features.weather.rain_anomaly_value is None
    assert features.weather.soil_moisture_value is None
    assert features.weather.drought_index_value is None

    assert features.collecting_allowed is None


def test_control_coordinate_keeps_source_data_uninterpreted() -> None:
    assembler = GeospatialFeatureAssembler(
        elevation_provider=FixtureElevationProvider(),
        forest_provider=FixtureForestProvider(),
        geology_provider=FixtureGeologyProvider(),
    )

    features = assembler.assemble(
        spot_id=CONTROL_SPOT_ID,
        latitude=CONTROL_LATITUDE,
        longitude=CONTROL_LONGITUDE,
        weather=_weather_snapshot(),
    )

    geology = features.geology.records[0]

    assert geology.material == "limestone"
    assert geology.representative_lithology == "limestone"

    # MR-3 хранит source-level geology.
    # Он не делает carbonate/silicate interpretation и не считает score.
    assert not hasattr(features, "is_carbonate")
    assert not hasattr(features, "geology_score")
    assert not hasattr(features, "habitat_score")
    assert not hasattr(features, "opportunity_score")
