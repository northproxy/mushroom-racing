import json
from pathlib import Path

from mushroom_racing.domain import WeatherSnapshot


FIXTURE = (
    Path(__file__).parents[2]
    / "data"
    / "samples"
    / "weather"
    / "sample_weather_snapshot.json"
)


def test_weather_snapshot_fixture_round_trip() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    snapshot = WeatherSnapshot.from_dict(data)

    assert snapshot.to_dict() == data
    assert snapshot.rain_24h_mm == 0.0
    assert snapshot.soil_moisture_value is None
