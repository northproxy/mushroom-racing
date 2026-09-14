import json
from pathlib import Path

from mushroom_racing.domain import SpeciesProfile


FIXTURE_PATH = (
    Path(__file__).parents[2]
    / "data"
    / "samples"
    / "species"
    / "boletus_edulis.json"
)


def test_species_profile_round_trip() -> None:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    profile = SpeciesProfile.from_dict(raw)
    restored = SpeciesProfile.from_dict(profile.to_dict())

    assert restored == profile


def test_species_fixture_is_json_serializable() -> None:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    profile = SpeciesProfile.from_dict(raw)

    serialized = json.dumps(profile.to_dict(), ensure_ascii=False)

    assert "boletus_edulis" in serialized
