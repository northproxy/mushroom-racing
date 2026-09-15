"""
File: geospatial_assembly.py
Project: mushroom-racing

Purpose:
    Собирает единый GeospatialFeatureSet для одной WGS84-точки
    из уже существующих provider contracts и WeatherSnapshot.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — orchestration layer между data providers,
    feature extraction и будущим scoring.

Inputs:
    spot_id;
    WGS84 latitude / longitude;
    ElevationProvider;
    ForestProvider;
    GeologyProvider;
    готовый WeatherSnapshot;
    optional manual legal status.

Outputs:
    GeospatialFeatureSet.

Dependencies:
    Python standard library
    mushroom_racing.domain.weather
    mushroom_racing.forest
    mushroom_racing.geology
    mushroom_racing.terrain
    mushroom_racing.geospatial_features

Used by:
    MR-3 geospatial feature pipeline;
    позже — application/scoring layer.

Notes:
    Модуль не выполняет ecological interpretation или scoring.
    WeatherSnapshot передаётся готовым и не загружается assembler-ом.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.forest import ForestProvider
from mushroom_racing.geology import GeologyProvider
from mushroom_racing.geospatial_features import GeospatialFeatureSet
from mushroom_racing.terrain import (
    ElevationProvider,
    extract_terrain_features,
)


@dataclass(frozen=True, slots=True)
class GeospatialFeatureAssembler:
    """
    Собирает source-level и derived features для одной точки.

    Конкретные Austrian providers намеренно не являются частью
    этого контракта: assembler зависит только от provider protocols.
    """

    elevation_provider: ElevationProvider
    forest_provider: ForestProvider
    geology_provider: GeologyProvider
    terrain_radius_m: float = 10.0

    def __post_init__(self) -> None:
        if (
            isinstance(self.terrain_radius_m, bool)
            or not isinstance(self.terrain_radius_m, (int, float))
        ):
            raise TypeError("terrain_radius_m must be a number")

        if not math.isfinite(self.terrain_radius_m):
            raise ValueError("terrain_radius_m must be finite")

        if self.terrain_radius_m <= 0:
            raise ValueError("terrain_radius_m must be greater than zero")

    def assemble(
        self,
        *,
        spot_id: str,
        latitude: float,
        longitude: float,
        weather: WeatherSnapshot,
        collecting_allowed: bool | None = None,
    ) -> GeospatialFeatureSet:
        """
        Собирает unified feature set для одной координаты.

        WeatherSnapshot должен относиться к тому же spot_id.
        Проверяем это до remote provider calls, чтобы не выполнять
        ненужные внешние запросы при заведомо некорректной сборке.
        """
        if not isinstance(weather, WeatherSnapshot):
            raise TypeError("weather must be a WeatherSnapshot")

        if weather.spot_id != spot_id:
            raise ValueError(
                "weather.spot_id must match requested spot_id"
            )

        elevation_window = self.elevation_provider.get_window(
            latitude,
            longitude,
            radius_m=self.terrain_radius_m,
        )
        terrain = extract_terrain_features(elevation_window)

        forest = self.forest_provider.get_forest_status(
            latitude,
            longitude,
        )
        geology = self.geology_provider.get_geology(
            latitude,
            longitude,
        )

        return GeospatialFeatureSet(
            spot_id=spot_id,
            latitude=latitude,
            longitude=longitude,
            terrain=terrain,
            forest=forest,
            geology=geology,
            weather=weather,
            collecting_allowed=collecting_allowed,
        )
