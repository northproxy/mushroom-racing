"""
File: cache.py
Project: mushroom-racing

Purpose:
    Добавляет persistent local file cache поверх ElevationProvider.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — infrastructure layer для terrain data access.

Inputs:
    latitude, longitude, radius_m и wrapped ElevationProvider.

Outputs:
    ElevationWindow из локального cache либо wrapped provider.

Dependencies:
    Python standard library
    numpy
    mushroom_racing.terrain.elevation

Used by:
    MR-2 terrain pipeline;
    application/service layer.

Notes:
    Cache хранит нормализованные ElevationWindow, а не provider-specific
    HTTP payloads. Cache namespace используется для явной invalidation.
"""

from __future__ import annotations

import hashlib
import math
import os
from pathlib import Path
import tempfile

import numpy as np

from .elevation import ElevationProvider, ElevationWindow


_CACHE_FORMAT_VERSION = 1


class ElevationCacheError(RuntimeError):
    """Ошибка чтения или записи local elevation cache."""


class CachedElevationProvider:
    """Persistent file cache поверх произвольного ElevationProvider."""

    def __init__(
        self,
        provider: ElevationProvider,
        cache_dir: str | Path,
        *,
        namespace: str,
    ) -> None:
        if not namespace.strip():
            raise ValueError("Cache namespace must not be empty.")

        self._provider = provider
        self._cache_dir = Path(cache_dir)
        self._namespace = namespace

        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        self._validate_request(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
        )

        cache_path = self._cache_path(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
        )

        if cache_path.exists():
            return self._load(cache_path)

        window = self._provider.get_window(
            latitude,
            longitude,
            radius_m=radius_m,
        )

        self._store(cache_path, window)

        return window

    def _cache_path(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_m: float,
    ) -> Path:
        key_material = "\0".join(
            (
                str(_CACHE_FORMAT_VERSION),
                self._namespace,
                latitude.hex(),
                longitude.hex(),
                radius_m.hex(),
            )
        )

        digest = hashlib.sha256(
            key_material.encode("utf-8")
        ).hexdigest()

        return self._cache_dir / f"{digest}.npz"

    def _load(self, path: Path) -> ElevationWindow:
        try:
            with np.load(path, allow_pickle=False) as data:
                required_keys = {
                    "format_version",
                    "namespace",
                    "values",
                    "bounds",
                    "crs",
                    "has_nodata",
                    "nodata",
                }

                missing = required_keys.difference(data.files)
                if missing:
                    raise ElevationCacheError(
                        "Cached elevation window is missing fields: "
                        + ", ".join(sorted(missing))
                    )

                format_version = int(
                    data["format_version"].item()
                )
                if format_version != _CACHE_FORMAT_VERSION:
                    raise ElevationCacheError(
                        "Unsupported elevation cache format version: "
                        f"{format_version}."
                    )

                namespace = str(data["namespace"].item())
                if namespace != self._namespace:
                    raise ElevationCacheError(
                        "Cached elevation window belongs to a different "
                        "cache namespace."
                    )

                values = np.asarray(data["values"])

                bounds_array = np.asarray(
                    data["bounds"],
                    dtype=np.float64,
                )
                if bounds_array.shape != (4,):
                    raise ElevationCacheError(
                        "Cached elevation bounds must contain four values."
                    )

                bounds = tuple(
                    float(value)
                    for value in bounds_array
                )

                crs = str(data["crs"].item())

                has_nodata = bool(
                    data["has_nodata"].item()
                )
                nodata = (
                    float(data["nodata"].item())
                    if has_nodata
                    else None
                )

        except ElevationCacheError:
            raise
        except Exception as exc:
            raise ElevationCacheError(
                f"Failed to read elevation cache file: {path}"
            ) from exc

        try:
            return ElevationWindow(
                values=values,
                bounds=bounds,
                crs=crs,
                nodata=nodata,
            )
        except (TypeError, ValueError) as exc:
            raise ElevationCacheError(
                f"Cached elevation window is invalid: {path}"
            ) from exc

    def _store(
        self,
        path: Path,
        window: ElevationWindow,
    ) -> None:
        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{path.stem}.",
                suffix=".tmp",
                dir=self._cache_dir,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                np.savez_compressed(
                    temporary_file,
                    format_version=np.asarray(
                        _CACHE_FORMAT_VERSION,
                        dtype=np.int64,
                    ),
                    namespace=np.asarray(self._namespace),
                    values=window.values,
                    bounds=np.asarray(
                        window.bounds,
                        dtype=np.float64,
                    ),
                    crs=np.asarray(window.crs),
                    has_nodata=np.asarray(
                        window.nodata is not None,
                        dtype=np.bool_,
                    ),
                    nodata=np.asarray(
                        (
                            float(window.nodata)
                            if window.nodata is not None
                            else np.nan
                        ),
                        dtype=np.float64,
                    ),
                )

            os.replace(temporary_path, path)
            temporary_path = None

        except Exception as exc:
            raise ElevationCacheError(
                f"Failed to write elevation cache file: {path}"
            ) from exc

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _validate_request(
        *,
        latitude: float,
        longitude: float,
        radius_m: float,
    ) -> None:
        if not math.isfinite(latitude):
            raise ValueError("Latitude must be finite.")

        if not math.isfinite(longitude):
            raise ValueError("Longitude must be finite.")

        if not math.isfinite(radius_m):
            raise ValueError("radius_m must be finite.")

        if radius_m <= 0.0:
            raise ValueError("radius_m must be greater than zero.")
