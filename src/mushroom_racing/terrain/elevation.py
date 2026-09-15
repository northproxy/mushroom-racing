"""Контракты данных для небольших окон цифровой модели рельефа."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.floating[Any]]
Bounds = tuple[float, float, float, float]


@dataclass(frozen=True, slots=True)
class ElevationWindow:
    """Небольшой геопривязанный фрагмент цифровой модели рельефа.

    ``bounds`` задаётся как ``(left, bottom, right, top)`` в системе
    координат ``crs``. Окно считается axis-aligned: первая строка массива
    соответствует верхней части растра, поворот осей не поддерживается.
    """

    values: FloatArray
    bounds: Bounds
    crs: str
    nodata: float | None = None

    def __post_init__(self) -> None:
        """Проверяет базовые инварианты окна и защищает данные от изменения."""
        if not isinstance(self.values, np.ndarray):
            raise TypeError("values must be a numpy.ndarray")
        if self.values.ndim != 2:
            raise ValueError("values must be a two-dimensional array")
        if self.values.size == 0:
            raise ValueError("values must not be empty")
        if not np.issubdtype(self.values.dtype, np.floating):
            raise TypeError("values must contain floating-point elevations")
        if np.isinf(self.values).any():
            raise ValueError("values must not contain infinite elevations")

        left, bottom, right, top = self.bounds
        if not all(isfinite(value) for value in self.bounds):
            raise ValueError("bounds must contain only finite values")
        if left >= right:
            raise ValueError("bounds must satisfy left < right")
        if bottom >= top:
            raise ValueError("bounds must satisfy bottom < top")

        if not isinstance(self.crs, str):
            raise TypeError("crs must be a string")
        if not self.crs.strip():
            raise ValueError("crs must not be empty")

        if self.nodata is not None and np.isinf(self.nodata):
            raise ValueError("nodata must not be infinite")

        has_nan = bool(np.isnan(self.values).any())
        nodata_is_nan = self.nodata is not None and bool(np.isnan(self.nodata))
        if has_nan and not nodata_is_nan:
            raise ValueError("NaN elevations require nodata=NaN")

        # Копия не позволяет вызывающему коду менять окно через исходный массив.
        values = self.values.copy()
        values.setflags(write=False)
        object.__setattr__(self, "values", values)

    @property
    def width(self) -> int:
        """Количество столбцов растра."""
        return int(self.values.shape[1])

    @property
    def height(self) -> int:
        """Количество строк растра."""
        return int(self.values.shape[0])

    @property
    def resolution_x(self) -> float:
        """Размер пикселя по оси X в единицах CRS."""
        left, _, right, _ = self.bounds
        return (right - left) / self.width

    @property
    def resolution_y(self) -> float:
        """Размер пикселя по оси Y в единицах CRS."""
        _, bottom, _, top = self.bounds
        return (top - bottom) / self.height


class ElevationProvider(Protocol):
    """Контракт источника небольших DEM-окон вокруг географической точки."""

    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        """Возвращает DEM-окно вокруг WGS84-точки с заданным радиусом в метрах."""
        ...
