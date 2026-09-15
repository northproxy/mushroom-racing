"""Контракты terrain-данных и provider-ы цифровой модели рельефа."""

from mushroom_racing.terrain.austrian_elevation import (
    AustrianElevationProvider,
    ElevationProviderError,
)
from mushroom_racing.terrain.elevation import ElevationProvider, ElevationWindow

__all__ = [
    "AustrianElevationProvider",
    "ElevationProvider",
    "ElevationProviderError",
    "ElevationWindow",
]
