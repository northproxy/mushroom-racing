from datetime import datetime, timezone

import pytest

from mushroom_racing.domain import Observation


def _valid_observation(**overrides: object) -> Observation:
    data: dict[str, object] = {
        "observation_id": "obs-001",
        "timestamp": datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
        "geometry": {"type": "Point", "coordinates": [16.0, 47.5]},
        "target_species_id": "boletus_edulis",
        "found_target_species": True,
        "species_confidence_pct": 90.0,
        "count": 2,
        "searched_minutes": 30.0,
    }
    data.update(overrides)
    return Observation(**data)  # type: ignore[arg-type]


def test_observation_accepts_negative_search_as_first_class_data() -> None:
    observation = _valid_observation(
        found_target_species=False,
        species_confidence_pct=None,
        count=0,
        searched_minutes=45.0,
        other_mushrooms_found=("Russula sp.",),
    )

    assert observation.found_target_species is False
    assert observation.count == 0
    assert observation.searched_minutes == 45.0


def test_observation_rejects_positive_count_for_negative_search() -> None:
    with pytest.raises(ValueError, match="count must be 0 or null"):
        _valid_observation(
            found_target_species=False,
            species_confidence_pct=None,
            count=1,
        )


def test_observation_rejects_zero_count_for_positive_find() -> None:
    with pytest.raises(ValueError, match="count must be positive or null"):
        _valid_observation(count=0)


def test_observation_rejects_species_confidence_without_find() -> None:
    with pytest.raises(ValueError, match="species_confidence_pct"):
        _valid_observation(
            found_target_species=False,
            species_confidence_pct=80.0,
            count=0,
        )


def test_observation_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        _valid_observation(timestamp=datetime(2026, 9, 14, 12, 0))


def test_observation_rejects_invalid_species_confidence() -> None:
    with pytest.raises(ValueError, match="species_confidence_pct"):
        _valid_observation(species_confidence_pct=101.0)


def test_observation_rejects_invalid_aspect() -> None:
    with pytest.raises(ValueError, match="aspect_deg"):
        _valid_observation(aspect_deg=360.0)
