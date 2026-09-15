import numpy as np
import pytest

from mushroom_racing.terrain import ElevationWindow


def test_elevation_window_exposes_dimensions_and_resolution() -> None:
    window = ElevationWindow(
        values=np.array(
            [
                [100.0, 101.0, 102.0],
                [99.0, 100.0, 101.0],
            ],
            dtype=np.float32,
        ),
        bounds=(0.0, 0.0, 30.0, 20.0),
        crs="EPSG:31259",
        nodata=-9999.0,
    )

    assert window.width == 3
    assert window.height == 2
    assert window.resolution_x == pytest.approx(10.0)
    assert window.resolution_y == pytest.approx(10.0)


def test_elevation_window_copies_and_freezes_values() -> None:
    source = np.array([[100.0, 101.0]], dtype=np.float32)
    window = ElevationWindow(
        values=source,
        bounds=(0.0, 0.0, 20.0, 10.0),
        crs="EPSG:31259",
    )

    source[0, 0] = 999.0

    assert window.values[0, 0] == pytest.approx(100.0)
    assert window.values.flags.writeable is False

    with pytest.raises(ValueError):
        window.values[0, 0] = 200.0


@pytest.mark.parametrize(
    ("values", "expected_exception", "message"),
    [
        (np.array([100.0], dtype=np.float32), ValueError, "two-dimensional"),
        (np.empty((0, 0), dtype=np.float32), ValueError, "must not be empty"),
        (np.array([[100]], dtype=np.int32), TypeError, "floating-point"),
    ],
)
def test_elevation_window_rejects_invalid_values(
    values: np.ndarray,
    expected_exception: type[Exception],
    message: str,
) -> None:
    with pytest.raises(expected_exception, match=message):
        ElevationWindow(
            values=values,
            bounds=(0.0, 0.0, 10.0, 10.0),
            crs="EPSG:31259",
        )


@pytest.mark.parametrize(
    "bounds",
    [
        (10.0, 0.0, 10.0, 20.0),
        (20.0, 0.0, 10.0, 20.0),
        (0.0, 20.0, 10.0, 20.0),
        (0.0, 30.0, 10.0, 20.0),
    ],
)
def test_elevation_window_rejects_invalid_bounds(
    bounds: tuple[float, float, float, float],
) -> None:
    with pytest.raises(ValueError):
        ElevationWindow(
            values=np.array([[100.0]], dtype=np.float32),
            bounds=bounds,
            crs="EPSG:31259",
        )


def test_elevation_window_rejects_empty_crs() -> None:
    with pytest.raises(ValueError, match="crs must not be empty"):
        ElevationWindow(
            values=np.array([[100.0]], dtype=np.float32),
            bounds=(0.0, 0.0, 10.0, 10.0),
            crs="   ",
        )


def test_elevation_window_requires_nan_nodata_marker() -> None:
    with pytest.raises(ValueError, match="NaN elevations require nodata=NaN"):
        ElevationWindow(
            values=np.array([[100.0, np.nan]], dtype=np.float32),
            bounds=(0.0, 0.0, 20.0, 10.0),
            crs="EPSG:31259",
        )


def test_elevation_window_accepts_nan_when_nodata_is_nan() -> None:
    window = ElevationWindow(
        values=np.array([[100.0, np.nan]], dtype=np.float32),
        bounds=(0.0, 0.0, 20.0, 10.0),
        crs="EPSG:31259",
        nodata=float("nan"),
    )

    assert np.isnan(window.values[0, 1])
