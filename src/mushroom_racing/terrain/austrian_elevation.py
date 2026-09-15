"""Operational DEM-provider для Austrian Elevation Service."""

from __future__ import annotations

from collections import defaultdict
from math import ceil, cos, floor, isfinite, log, pi, radians, tan

import httpx
import numpy as np

from mushroom_racing.terrain.elevation import ElevationWindow

_WEB_MERCATOR_RADIUS_M = 6_378_137.0
_WEB_MERCATOR_MAX_LATITUDE = 85.05112878
_CELL_SIZE_M = 10
_STRIP_WIDTH_M = 20_000
_CRS = "EPSG:3857"
_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/maegger/{database}/master/{raster_y}.txt"
)


class ElevationProviderError(RuntimeError):
    """Ошибка получения или разбора elevation-данных внешнего provider-а."""


class AustrianElevationProvider:
    """Получает небольшие DEM-окна из Austrian Elevation Service.

    Сервис используется только как operational access layer для PoC. Его значения
    округлены до целых метров и не заменяют authoritative Austrian DGM при валидации.

    HTTP-клиент передаётся снаружи, чтобы жизненный цикл соединений оставался
    ответственностью application/infrastructure слоя и provider легко тестировался.
    """

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        """Возвращает DEM-окно вокруг WGS84-точки.

        ``radius_m`` интерпретируется как приблизительный радиус по поверхности.
        Для выбора ячеек EPSG:3857 учитывается локальный масштаб Web Mercator.
        """
        self._validate_request(latitude, longitude, radius_m)

        center_x, center_y = _wgs84_to_web_mercator(latitude, longitude)
        projected_radius_m = radius_m / cos(radians(latitude))
        cell_radius = max(1, ceil(projected_radius_m / _CELL_SIZE_M))

        center_cell_x = _snap_down(center_x, _CELL_SIZE_M)
        center_cell_y = _snap_down(center_y, _CELL_SIZE_M)

        x_coordinates = tuple(
            center_cell_x + offset * _CELL_SIZE_M
            for offset in range(-cell_radius, cell_radius + 1)
        )
        # ElevationWindow хранит первую строку как северную/верхнюю строку растра.
        y_coordinates = tuple(
            center_cell_y + offset * _CELL_SIZE_M
            for offset in range(cell_radius, -cell_radius - 1, -1)
        )

        values = np.empty(
            (len(y_coordinates), len(x_coordinates)),
            dtype=np.float32,
        )

        for row_index, raster_y in enumerate(y_coordinates):
            values[row_index, :] = self._load_row(raster_y, x_coordinates)

        left = float(x_coordinates[0])
        bottom = float(y_coordinates[-1])
        right = float(x_coordinates[-1] + _CELL_SIZE_M)
        top = float(y_coordinates[0] + _CELL_SIZE_M)

        return ElevationWindow(
            values=values,
            bounds=(left, bottom, right, top),
            crs=_CRS,
        )

    def _load_row(
        self,
        raster_y: int,
        x_coordinates: tuple[int, ...],
    ) -> np.ndarray:
        """Загружает одну строку DEM, при необходимости из нескольких strip-repo."""
        columns_by_database: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for column_index, raster_x in enumerate(x_coordinates):
            database = _snap_down(raster_x, _STRIP_WIDTH_M)
            columns_by_database[database].append((column_index, raster_x))

        row = np.empty(len(x_coordinates), dtype=np.float32)

        for database, columns in columns_by_database.items():
            elevations = self._fetch_row(database=database, raster_y=raster_y)
            for column_index, raster_x in columns:
                try:
                    row[column_index] = elevations[raster_x]
                except KeyError as exc:
                    raise ElevationProviderError(
                        f"elevation is missing for EPSG:3857 cell x={raster_x}, y={raster_y}"
                    ) from exc

        return row

    def _fetch_row(self, *, database: int, raster_y: int) -> dict[int, float]:
        url = _URL_TEMPLATE.format(database=database, raster_y=raster_y)

        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ElevationProviderError(
                f"failed to fetch elevation row x-strip={database}, y={raster_y}"
            ) from exc

        return _parse_elevation_row(response.text)

    @staticmethod
    def _validate_request(
        latitude: float,
        longitude: float,
        radius_m: float,
    ) -> None:
        if not all(isfinite(value) for value in (latitude, longitude, radius_m)):
            raise ValueError("latitude, longitude and radius_m must be finite")
        if not -_WEB_MERCATOR_MAX_LATITUDE <= latitude <= _WEB_MERCATOR_MAX_LATITUDE:
            raise ValueError(
                "latitude is outside the supported EPSG:3857 range"
            )
        if not -180.0 <= longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")
        if radius_m <= 0.0:
            raise ValueError("radius_m must be greater than zero")


def _wgs84_to_web_mercator(latitude: float, longitude: float) -> tuple[float, float]:
    """Преобразует WGS84 longitude/latitude в EPSG:3857 без GIS-зависимости."""
    longitude_rad = radians(longitude)
    latitude_rad = radians(latitude)
    x = _WEB_MERCATOR_RADIUS_M * longitude_rad
    y = _WEB_MERCATOR_RADIUS_M * log(tan(pi / 4.0 + latitude_rad / 2.0))
    return x, y


def _snap_down(value: float, grid_size: int) -> int:
    """Привязывает координату к нижней границе регулярной сетки."""
    return floor(value / grid_size) * grid_size


def _parse_elevation_row(text: str) -> dict[int, float]:
    """Разбирает строковый raster-row формата ``x elevation``."""
    elevations: dict[int, float] = {}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) != 2:
            raise ElevationProviderError(
                f"invalid elevation row at line {line_number}: expected two columns"
            )

        try:
            raster_x = int(parts[0])
            elevation = float(parts[1])
        except ValueError as exc:
            raise ElevationProviderError(
                f"invalid elevation row at line {line_number}: non-numeric value"
            ) from exc

        if not isfinite(elevation):
            raise ElevationProviderError(
                f"invalid elevation row at line {line_number}: non-finite elevation"
            )
        if raster_x in elevations:
            raise ElevationProviderError(
                f"invalid elevation row: duplicate x coordinate {raster_x}"
            )

        elevations[raster_x] = elevation

    if not elevations:
        raise ElevationProviderError("elevation row is empty")

    return elevations
