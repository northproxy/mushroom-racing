import pytest

from mushroom_racing.geology import (
    GeologyQueryResult,
    GeologyRecord,
)


def test_geology_record_stores_source_level_fields() -> None:
    record = GeologyRecord(
        identifier="https://example.test/geology/1",
        name="Gutenstein Formation",
        description="Gutensteiner Kalk (Anis)",
        geologic_unit_type="lithostratigraphic unit",
        material="limestone",
        representative_lithology="limestone",
    )

    assert record.identifier == "https://example.test/geology/1"
    assert record.name == "Gutenstein Formation"
    assert record.material == "limestone"
    assert record.representative_lithology == "limestone"


def test_geology_record_accepts_nullable_source_fields() -> None:
    record = GeologyRecord(
        identifier="https://example.test/geology/2",
        name=None,
        description=None,
        geologic_unit_type=None,
        material=None,
        representative_lithology=None,
    )

    assert record.name is None
    assert record.description is None
    assert record.geologic_unit_type is None
    assert record.material is None
    assert record.representative_lithology is None


@pytest.mark.parametrize(
    ("identifier", "expected_exception"),
    [
        ("", ValueError),
        ("   ", ValueError),
        (None, TypeError),
    ],
)
def test_geology_record_rejects_invalid_identifier(
    identifier: str,
    expected_exception: type[Exception],
) -> None:
    with pytest.raises(expected_exception):
        GeologyRecord(
            identifier=identifier,
            name=None,
            description=None,
            geologic_unit_type=None,
            material=None,
            representative_lithology=None,
        )


def test_geology_query_result_supports_zero_records() -> None:
    result = GeologyQueryResult(records=())

    assert result.records == ()


def test_geology_query_result_preserves_multiple_records() -> None:
    records = (
        GeologyRecord(
            identifier="feature-1",
            name=None,
            description=None,
            geologic_unit_type=None,
            material="limestone",
            representative_lithology="limestone",
        ),
        GeologyRecord(
            identifier="feature-2",
            name=None,
            description=None,
            geologic_unit_type=None,
            material="breccia",
            representative_lithology="breccia",
        ),
    )

    result = GeologyQueryResult(records=records)

    assert result.records == records
    assert len(result.records) == 2
