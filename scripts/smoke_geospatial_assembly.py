"""
File: smoke_geospatial_assembly.py
Project: mushroom-racing

Purpose:
    Выполняет live end-to-end smoke test MR-3 для одной контрольной
    WGS84-координаты через реальные Austrian data providers.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    temporary

Lifecycle:
    temporary — удалить или перенести после завершения MR-3,
    когда live validation будет зафиксирована в документации.

Inputs:
    Live Austrian DEM, forest, geology и GeoSphere weather sources.

Outputs:
    GeospatialFeatureSet и краткий human-readable summary.

Dependencies:
    Python standard library
    httpx
    mushroom_racing package

Used by:
    Manual MR-3 validation.

Notes:
    Скрипт выполняет реальные сетевые запросы.
    Legal status намеренно остаётся unknown / None.
"""

from __future__ import annotations

from datetime import date, timedelta

import httpx

from mushroom_racing.forest import AustrianForestProvider
from mushroom_racing.geology import AustrianGeologyProvider
from mushroom_racing.geospatial_assembly import GeospatialFeatureAssembler
from mushroom_racing.providers.austrian_weather import AustrianWeatherProvider
from mushroom_racing.terrain import AustrianElevationProvider
from mushroom_racing.weather_snapshot import build_weather_snapshot


SPOT_ID = "control_spot"
LATITUDE = 47.7200
LONGITUDE = 15.9000

# Используем уже проверенную historical дату MR-2,
# чтобы smoke test был воспроизводимым и не зависел от availability
# самого свежего дня SPARTACUS.
AS_OF_DATE = date(2026, 9, 12)

# Для rain_28d нужно полное inclusive окно из 28 календарных дней.
WEATHER_START_DATE = AS_OF_DATE - timedelta(days=27)


def main() -> None:
    weather_provider = AustrianWeatherProvider()

    print("Loading weather...")
    weather_series = weather_provider.get_daily_series(
        LATITUDE,
        LONGITUDE,
        WEATHER_START_DATE,
        AS_OF_DATE,
    )

    weather_snapshot = build_weather_snapshot(
        spot_id=SPOT_ID,
        series=weather_series,
        as_of_date=AS_OF_DATE,
    )

    with httpx.Client(timeout=30.0) as client:
        elevation_provider = AustrianElevationProvider(client)
        forest_provider = AustrianForestProvider(client=client)
        geology_provider = AustrianGeologyProvider(client)

        assembler = GeospatialFeatureAssembler(
            elevation_provider=elevation_provider,
            forest_provider=forest_provider,
            geology_provider=geology_provider,
        )

        print("Loading terrain, forest and geology...")

        features = assembler.assemble(
            spot_id=SPOT_ID,
            latitude=LATITUDE,
            longitude=LONGITUDE,
            weather=weather_snapshot,
            collecting_allowed=None,
        )

    print()
    print("MR-3 LIVE SMOKE RESULT")
    print("======================")
    print(f"spot_id:      {features.spot_id}")
    print(f"coordinate:   {features.latitude}, {features.longitude}")
    print()

    print("Terrain")
    print(f"  elevation:  {features.terrain.elevation_m:.1f} m")
    print(f"  slope:      {features.terrain.slope_deg:.2f} deg")
    print(f"  aspect:     {features.terrain.aspect_deg}")
    print()

    print("Forest")
    print(f"  status:     {features.forest.status}")
    print()

    print("Geology")
    print(f"  records:    {len(features.geology.records)}")

    for index, record in enumerate(features.geology.records, start=1):
        print(f"  [{index}] name:       {record.name}")
        print(f"      material:         {record.material}")
        print(
            "      lithology:        "
            f"{record.representative_lithology}"
        )

    print()
    print("Weather")
    print(f"  source:     {features.weather.source_id}")
    print(f"  timestamp:  {features.weather.timestamp}")
    print(f"  rain 24h:   {features.weather.rain_24h_mm}")
    print(f"  rain 3d:    {features.weather.rain_3d_mm}")
    print(f"  rain 7d:    {features.weather.rain_7d_mm}")
    print(f"  rain 14d:   {features.weather.rain_14d_mm}")
    print(f"  rain 21d:   {features.weather.rain_21d_mm}")
    print(f"  rain 28d:   {features.weather.rain_28d_mm}")
    print(f"  temp 7d:    {features.weather.avg_temp_7d_c}")
    print(f"  temp 14d:   {features.weather.avg_temp_14d_c}")
    print(f"  temp 20d:   {features.weather.avg_temp_20d_c}")
    print()

    print("Legal")
    print(f"  collecting_allowed: {features.collecting_allowed}")

    print()
    print("PASS: live GeospatialFeatureSet assembled successfully.")


if __name__ == "__main__":
    main()
