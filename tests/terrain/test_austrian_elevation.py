from math import atan, degrees, exp, pi

import httpx
import numpy as np
import pytest

from mushroom_racing.terrain import (
    AustrianElevationProvider,
    ElevationProviderError,
)

_WEB_MERCATOR_RADIUS_M = 6_378_137.0


def _wgs84_for_projected_point(x: float, y: float) -> tuple[float, float]:
    """Возвращает тестовую WGS84-точку для заранее выбранной EPSG:3857 точки."""
    longitude = degrees(x / _WEB_MERCATOR_RADIUS_M)
    latitude = degrees(2.0 * atan(exp(y / _WEB_MERCATOR_RADIUS_M)) - pi / 2.0)
    return latitude, longitude


def test_get_window_returns_remote_elevation_grid() -> None:
    latitude, longitude = _wgs84_for_projected_point(1_822_642.0, 6_141_614.0)
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        raster_y = int(request.url.path.rsplit("/", 1)[-1].removesuffix(".txt"))
        body = "\n".join(
            f"{x} {200 + ((x - 1_822_620) // 10) + ((raster_y - 6_141_590) // 10)}"
            for x in range(1_822_600, 1_822_690, 10)
        )
        return httpx.Response(200, text=body)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianElevationProvider(client)

    window = provider.get_window(
        latitude,
        longitude,
        radius_m=10.0,
    )

    assert window.crs == "EPSG:3857"
    assert window.values.dtype == np.float32
    assert window.values.shape == (5, 5)
    assert window.resolution_x == pytest.approx(10.0)
    assert window.resolution_y == pytest.approx(10.0)
    assert len(requested_urls) == 5
    assert all("/maegger/1820000/master/" in url for url in requested_urls)

    client.close()


def test_get_window_orders_rows_from_north_to_south() -> None:
    latitude, longitude = _wgs84_for_projected_point(1_822_642.0, 6_141_614.0)

    def handler(request: httpx.Request) -> httpx.Response:
        raster_y = int(request.url.path.rsplit("/", 1)[-1].removesuffix(".txt"))
        body = "\n".join(
            f"{x} {raster_y}"
            for x in range(1_822_600, 1_822_690, 10)
        )
        return httpx.Response(200, text=body)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianElevationProvider(client)

    window = provider.get_window(latitude, longitude, radius_m=10.0)

    assert window.values[0, 0] > window.values[-1, 0]
    assert window.bounds == pytest.approx(
        (1_822_620.0, 6_141_590.0, 1_822_670.0, 6_141_640.0)
    )

    client.close()


def test_get_window_fails_when_requested_cell_is_missing() -> None:
    latitude, longitude = _wgs84_for_projected_point(1_822_642.0, 6_141_614.0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="1822640 250\n")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianElevationProvider(client)

    with pytest.raises(ElevationProviderError, match="elevation is missing"):
        provider.get_window(latitude, longitude, radius_m=10.0)

    client.close()


def test_get_window_wraps_http_errors() -> None:
    latitude, longitude = _wgs84_for_projected_point(1_822_642.0, 6_141_614.0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="not found")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianElevationProvider(client)

    with pytest.raises(ElevationProviderError, match="failed to fetch elevation row"):
        provider.get_window(latitude, longitude, radius_m=10.0)

    client.close()


def test_get_window_rejects_malformed_remote_row() -> None:
    latitude, longitude = _wgs84_for_projected_point(1_822_642.0, 6_141_614.0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="1822640 not-a-number\n")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianElevationProvider(client)

    with pytest.raises(ElevationProviderError, match="non-numeric value"):
        provider.get_window(latitude, longitude, radius_m=10.0)

    client.close()


@pytest.mark.parametrize(
    ("latitude", "longitude", "radius_m", "message"),
    [
        (90.0, 16.0, 10.0, "supported EPSG:3857 range"),
        (48.0, 181.0, 10.0, "longitude must be between"),
        (48.0, 16.0, 0.0, "radius_m must be greater than zero"),
        (48.0, 16.0, float("nan"), "must be finite"),
    ],
)
def test_get_window_rejects_invalid_requests(
    latitude: float,
    longitude: float,
    radius_m: float,
    message: str,
) -> None:
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(500)))
    provider = AustrianElevationProvider(client)

    with pytest.raises(ValueError, match=message):
        provider.get_window(latitude, longitude, radius_m=radius_m)

    client.close()
