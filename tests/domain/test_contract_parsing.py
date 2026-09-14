from datetime import datetime, timezone

import pytest

from mushroom_racing.domain import (
    EvidenceRecord,
    ForestSpot,
    Observation,
    SpeciesProfile,
    WeatherSnapshot,
)


def test_species_from_dict_rejects_non_string_identifier() -> None:
    data = {
        "species_id": None,
        "latin_name": "Boletus edulis",
        "common_name": "Steinpilz",
        "german_name": "Fichten-Steinpilz",
    }

    with pytest.raises(TypeError, match="species_id must be a string"):
        SpeciesProfile.from_dict(data)


def test_evidence_from_dict_rejects_non_string_field_name() -> None:
    data = {
        "field_name": None,
        "level": "working_hypothesis",
        "source_id": None,
        "note": None,
    }

    with pytest.raises(TypeError, match="field_name must be a string"):
        EvidenceRecord.from_dict(data)


def test_weather_from_dict_rejects_numeric_string() -> None:
    data = {
        "spot_id": "spot-001",
        "timestamp": "2026-09-14T12:00:00+00:00",
        "source_id": "test-source",
        "rain_24h_mm": "0.0",
    }

    with pytest.raises(TypeError, match="rain_24h_mm must be a number or null"):
        WeatherSnapshot.from_dict(data)


def test_observation_from_dict_rejects_float_count() -> None:
    data = {
        "observation_id": "obs-001",
        "timestamp": "2026-09-14T12:00:00+00:00",
        "geometry": {"type": "Point", "coordinates": [16.0, 47.5]},
        "target_species_id": "boletus_edulis",
        "found_target_species": True,
        "count": 1.5,
    }

    with pytest.raises(TypeError, match="count must be an integer or null"):
        Observation.from_dict(data)


def test_forest_spot_accepts_structurally_valid_polygon() -> None:
    spot = ForestSpot(
        spot_id="spot-poly",
        name="Polygon spot",
        geometry={
            "type": "Polygon",
            "coordinates": [
                [
                    [16.0, 47.5],
                    [16.1, 47.5],
                    [16.1, 47.6],
                    [16.0, 47.5],
                ]
            ],
        },
        region="Niederösterreich",
        country="Austria",
        last_updated=datetime(2026, 9, 14, tzinfo=timezone.utc),
    )

    assert spot.geometry["type"] == "Polygon"


def test_forest_spot_rejects_unclosed_polygon_ring() -> None:
    with pytest.raises(ValueError, match="linear ring must be closed"):
        ForestSpot(
            spot_id="spot-poly",
            name="Polygon spot",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [16.0, 47.5],
                        [16.1, 47.5],
                        [16.1, 47.6],
                        [16.0, 47.6],
                    ]
                ],
            },
            region="Niederösterreich",
            country="Austria",
        )


def test_forest_spot_accepts_structurally_valid_multipolygon() -> None:
    spot = ForestSpot(
        spot_id="spot-multi",
        name="MultiPolygon spot",
        geometry={
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [16.0, 47.5],
                        [16.1, 47.5],
                        [16.1, 47.6],
                        [16.0, 47.5],
                    ]
                ]
            ],
        },
        region="Niederösterreich",
        country="Austria",
    )

    assert spot.geometry["type"] == "MultiPolygon"
