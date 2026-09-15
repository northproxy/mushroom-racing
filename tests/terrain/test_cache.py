from pathlib import Path

import numpy as np
import pytest

from mushroom_racing.terrain import (
    CachedElevationProvider,
    ElevationCacheError,
    ElevationWindow,
)


class CountingElevationProvider:
    def __init__(self) -> None:
        self.calls = 0

    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        self.calls += 1

        return ElevationWindow(
            values=np.asarray(
                [
                    [100.0, 101.0, 102.0],
                    [103.0, 104.0, 105.0],
                    [106.0, 107.0, 108.0],
                ],
                dtype=np.float32,
            ),
            bounds=(0.0, 0.0, 30.0, 30.0),
            crs="EPSG:31259",
            nodata=-9999.0,
        )


class FailingElevationProvider:
    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> ElevationWindow:
        raise AssertionError(
            "Wrapped provider must not be called on cache hit."
        )


def test_cache_miss_calls_wrapped_provider(
    tmp_path: Path,
) -> None:
    provider = CountingElevationProvider()
    cached = CachedElevationProvider(
        provider,
        tmp_path,
        namespace="test-v1",
    )

    window = cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    assert provider.calls == 1
    assert window.values[1, 1] == pytest.approx(104.0)
    assert len(list(tmp_path.glob("*.npz"))) == 1


def test_second_identical_request_is_cache_hit(
    tmp_path: Path,
) -> None:
    provider = CountingElevationProvider()
    cached = CachedElevationProvider(
        provider,
        tmp_path,
        namespace="test-v1",
    )

    first = cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )
    second = cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    assert provider.calls == 1
    np.testing.assert_array_equal(
        second.values,
        first.values,
    )


def test_cache_persists_between_provider_instances(
    tmp_path: Path,
) -> None:
    writer = CachedElevationProvider(
        CountingElevationProvider(),
        tmp_path,
        namespace="test-v1",
    )

    expected = writer.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    reader = CachedElevationProvider(
        FailingElevationProvider(),
        tmp_path,
        namespace="test-v1",
    )

    actual = reader.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    np.testing.assert_array_equal(
        actual.values,
        expected.values,
    )
    assert actual.bounds == expected.bounds
    assert actual.crs == expected.crs
    assert actual.nodata == expected.nodata


def test_different_radius_creates_different_cache_entry(
    tmp_path: Path,
) -> None:
    provider = CountingElevationProvider()
    cached = CachedElevationProvider(
        provider,
        tmp_path,
        namespace="test-v1",
    )

    cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )
    cached.get_window(
        48.0,
        16.0,
        radius_m=30.0,
    )

    assert provider.calls == 2
    assert len(list(tmp_path.glob("*.npz"))) == 2


def test_different_namespace_does_not_reuse_cache(
    tmp_path: Path,
) -> None:
    first_provider = CountingElevationProvider()
    first = CachedElevationProvider(
        first_provider,
        tmp_path,
        namespace="source-v1",
    )

    first.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    second_provider = CountingElevationProvider()
    second = CachedElevationProvider(
        second_provider,
        tmp_path,
        namespace="source-v2",
    )

    second.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    assert first_provider.calls == 1
    assert second_provider.calls == 1
    assert len(list(tmp_path.glob("*.npz"))) == 2


def test_cache_preserves_read_only_window_values(
    tmp_path: Path,
) -> None:
    cached = CachedElevationProvider(
        CountingElevationProvider(),
        tmp_path,
        namespace="test-v1",
    )

    cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    window = cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    assert window.values.flags.writeable is False


def test_corrupted_cache_fails_fast(
    tmp_path: Path,
) -> None:
    cached = CachedElevationProvider(
        CountingElevationProvider(),
        tmp_path,
        namespace="test-v1",
    )

    cached.get_window(
        48.0,
        16.0,
        radius_m=20.0,
    )

    cache_file = next(tmp_path.glob("*.npz"))
    cache_file.write_bytes(b"not-a-valid-npz")

    with pytest.raises(
        ElevationCacheError,
        match="Failed to read elevation cache file",
    ):
        cached.get_window(
            48.0,
            16.0,
            radius_m=20.0,
        )


@pytest.mark.parametrize(
    ("latitude", "longitude", "radius_m", "message"),
    [
        (float("nan"), 16.0, 20.0, "Latitude must be finite"),
        (48.0, float("inf"), 20.0, "Longitude must be finite"),
        (48.0, 16.0, float("nan"), "radius_m must be finite"),
        (48.0, 16.0, 0.0, "radius_m must be greater than zero"),
        (48.0, 16.0, -1.0, "radius_m must be greater than zero"),
    ],
)
def test_rejects_invalid_requests(
    tmp_path: Path,
    latitude: float,
    longitude: float,
    radius_m: float,
    message: str,
) -> None:
    cached = CachedElevationProvider(
        CountingElevationProvider(),
        tmp_path,
        namespace="test-v1",
    )

    with pytest.raises(ValueError, match=message):
        cached.get_window(
            latitude,
            longitude,
            radius_m=radius_m,
        )


def test_rejects_empty_namespace(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="namespace must not be empty",
    ):
        CachedElevationProvider(
            CountingElevationProvider(),
            tmp_path,
            namespace="   ",
        )
