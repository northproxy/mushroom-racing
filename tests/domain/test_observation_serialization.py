import json
from pathlib import Path

import pytest

from mushroom_racing.domain import Observation


@pytest.mark.parametrize(
    "fixture_name",
    ["positive_observation.json", "negative_observation.json"],
)
def test_observation_fixture_round_trip(fixture_name: str) -> None:
    fixture_path = Path("data/samples/observations") / fixture_name
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))

    observation = Observation.from_dict(raw)
    serialized = observation.to_dict()

    assert serialized == raw
