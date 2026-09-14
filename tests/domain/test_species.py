import pytest

from mushroom_racing.domain import EvidenceLevel, EvidenceRecord, SpeciesProfile


def test_species_profile_accepts_valid_data() -> None:
    profile = SpeciesProfile(
        species_id="boletus_edulis",
        latin_name="Boletus edulis",
        common_name="Steinpilz",
        german_name="Fichten-Steinpilz",
        host_trees=("Picea abies", "Fagus sylvatica"),
        preferred_temperature_min_c=10.0,
        preferred_temperature_max_c=16.0,
        rain_response_min_days=7,
        rain_response_max_days=20,
    )

    assert profile.species_id == "boletus_edulis"
    assert profile.host_trees == ("Picea abies", "Fagus sylvatica")


def test_species_profile_rejects_incomplete_range() -> None:
    with pytest.raises(ValueError, match="requires both minimum and maximum"):
        SpeciesProfile(
            species_id="boletus_edulis",
            latin_name="Boletus edulis",
            common_name="Steinpilz",
            german_name="Fichten-Steinpilz",
            preferred_temperature_min_c=10.0,
        )


def test_species_profile_rejects_invalid_month() -> None:
    with pytest.raises(ValueError, match="values 1..12"):
        SpeciesProfile(
            species_id="boletus_edulis",
            latin_name="Boletus edulis",
            common_name="Steinpilz",
            german_name="Fichten-Steinpilz",
            preferred_season_months=(9, 13),
        )


def test_confirmed_evidence_requires_source_id() -> None:
    with pytest.raises(ValueError, match="requires source_id"):
        EvidenceRecord(
            field_name="host_trees",
            level=EvidenceLevel.CONFIRMED_SOURCE,
        )
