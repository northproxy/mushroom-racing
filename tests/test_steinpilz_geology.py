from types import SimpleNamespace

from mushroom_racing.steinpilz_geology import (
    SteinpilzGeologyAffinity,
    interpret_steinpilz_geology,
)


def geology_result(*records):
    return SimpleNamespace(records=records)


def geology_record(
    *,
    material=None,
    representative_lithology=None,
):
    return SimpleNamespace(
        material=material,
        representative_lithology=representative_lithology,
    )


def test_limestone_is_unfavourable_baseline_proxy():
    result = interpret_steinpilz_geology(
        geology_result(
            geology_record(
                material="limestone",
                representative_lithology="limestone",
            )
        )
    )

    assert result.affinity is SteinpilzGeologyAffinity.UNFAVOURABLE
    assert "Carbonate-like" in result.reason


def test_gneiss_is_favourable_baseline_proxy():
    result = interpret_steinpilz_geology(
        geology_result(
            geology_record(
                material="gneiss",
                representative_lithology="gneiss",
            )
        )
    )

    assert result.affinity is SteinpilzGeologyAffinity.FAVOURABLE
    assert "Silicate-like" in result.reason


def test_mixed_geology_is_not_collapsed_to_one_side():
    result = interpret_steinpilz_geology(
        geology_result(
            geology_record(material="gneiss"),
            geology_record(material="limestone"),
        )
    )

    assert result.affinity is SteinpilzGeologyAffinity.MIXED


def test_empty_geology_is_unknown():
    result = interpret_steinpilz_geology(
        geology_result()
    )

    assert result.affinity is SteinpilzGeologyAffinity.UNKNOWN


def test_unrecognized_geology_is_unknown():
    result = interpret_steinpilz_geology(
        geology_result(
            geology_record(
                material="unknown unit",
                representative_lithology="unclassified",
            )
        )
    )

    assert result.affinity is SteinpilzGeologyAffinity.UNKNOWN
