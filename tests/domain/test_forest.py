from datetime import datetime, timezone

import pytest

from mushroom_racing.domain import ForestSpot


def _valid_spot(**overrides: object) -> ForestSpot:
    data: dict[str, object] = {
        "spot_id": "spot-001",
        "name": "Test forest spot",
        "geometry": {"type": "Point", "coordinates": [16.0, 47.5]},
        "region": "Niederösterreich",
        "country": "Austria",
        "elevation_min_m": 800.0,
        "elevation_max_m": 900.0,
        "dominant_aspect_deg": 30.0,
        "slope_deg": 15.0,
        "collecting_allowed": None,
        "static_data_confidence": 75.0,
        "last_updated": datetime(2026, 9, 14, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return ForestSpot(**data)  # type: ignore[arg-type]


def test_forest_spot_accepts_unknown_legal_status() -> None:
    spot = _valid_spot(collecting_allowed=None)

    assert spot.collecting_allowed is None


def test_forest_spot_rejects_inverted_elevation_range() -> None:
    with pytest.raises(ValueError, match="minimum must not exceed maximum"):
        _valid_spot(elevation_min_m=1000.0, elevation_max_m=900.0)


def test_forest_spot_rejects_invalid_aspect() -> None:
    with pytest.raises(ValueError, match="dominant_aspect_deg"):
        _valid_spot(dominant_aspect_deg=360.0)


def test_forest_spot_rejects_invalid_point_coordinates() -> None:
    with pytest.raises(ValueError, match="longitude"):
        _valid_spot(
            geometry={"type": "Point", "coordinates": [181.0, 47.5]},
        )


def test_forest_spot_rejects_naive_last_updated() -> None:
    with pytest.raises(ValueError, match="timezone"):
        _valid_spot(last_updated=datetime(2026, 9, 14, 12, 0))
