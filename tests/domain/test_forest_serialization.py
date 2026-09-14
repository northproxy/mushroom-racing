import json
from pathlib import Path

from mushroom_racing.domain import ForestSpot


def test_forest_spot_fixture_round_trip() -> None:
    fixture_path = Path("data/samples/forest_spots/sample_forest_spot.json")
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))

    spot = ForestSpot.from_dict(raw)
    serialized = spot.to_dict()

    assert serialized == raw
    assert spot.collecting_allowed is None
    assert spot.geometry["type"] == "Point"
