"""
File: geospatial_features.py
Project: mushroom-racing

Purpose:
    Определяет единый MR-3 contract для уже нормализованных
    geospatial features одной координаты / candidate spot.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — assembly contract между source-level feature extraction
    и будущим interpretation/scoring layer.

Inputs:
    TerrainFeatures, ForestResult, GeologyQueryResult, WeatherSnapshot
    и текущий legal status.

Outputs:
    GeospatialFeatureSet.

Dependencies:
    Python standard library
    mushroom_racing.domain.weather
    mushroom_racing.forest
    mushroom_racing.geology
    mushroom_racing.terrain

Used by:
    MR-3 geospatial feature assembly;
    позже — interpretation и scoring pipeline.

Notes:
    Этот модуль не выполняет data acquisition, geological interpretation
    или scoring. Неизвестные значения сохраняются как unknown / None.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from mushroom_racing.domain.weather import WeatherSnapshot
from mushroom_racing.forest import ForestResult
from mushroom_racing.geology import GeologyQueryResult
from mushroom_racing.terrain import TerrainFeatures


@dataclass(frozen=True, slots=True)
class GeospatialFeatureSet:
    """
    Единый набор уже нормализованных признаков для одной WGS84-точки.

    Объект сохраняет результаты предыдущих pipeline stages без повторной
    интерпретации или преобразования.
    """

    spot_id: str
    latitude: float
    longitude: float
    terrain: TerrainFeatures
    forest: ForestResult
    geology: GeologyQueryResult
    weather: WeatherSnapshot
    collecting_allowed: bool | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.spot_id, str):
            raise TypeError("spot_id must be a string")
        if not self.spot_id.strip():
            raise ValueError("spot_id must not be empty")

        _validate_coordinate(
            self.latitude,
            field_name="latitude",
            minimum=-90.0,
            maximum=90.0,
        )
        _validate_coordinate(
            self.longitude,
            field_name="longitude",
            minimum=-180.0,
            maximum=180.0,
        )

        if not isinstance(self.terrain, TerrainFeatures):
            raise TypeError("terrain must be a TerrainFeatures")
        if not isinstance(self.forest, ForestResult):
            raise TypeError("forest must be a ForestResult")
        if not isinstance(self.geology, GeologyQueryResult):
            raise TypeError("geology must be a GeologyQueryResult")
        if not isinstance(self.weather, WeatherSnapshot):
            raise TypeError("weather must be a WeatherSnapshot")

        if self.weather.spot_id != self.spot_id:
            raise ValueError(
                "weather.spot_id must match GeospatialFeatureSet.spot_id"
            )

        if (
            self.collecting_allowed is not None
            and not isinstance(self.collecting_allowed, bool)
        ):
            raise TypeError("collecting_allowed must be a bool or None")


def _validate_coordinate(
    value: float,
    *,
    field_name: str,
    minimum: float,
    maximum: float,
) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")

    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{field_name} must be between {minimum} and {maximum}"
        )
