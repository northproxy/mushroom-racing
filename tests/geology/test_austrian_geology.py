import json

import httpx
import pytest

from mushroom_racing.geology import (
    AustrianGeologyProvider,
    GeologyProviderError,
)


def _provider_for_payload(
    payload: object,
) -> tuple[AustrianGeologyProvider, httpx.Client]:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    return AustrianGeologyProvider(client), client


def test_get_geology_returns_source_record() -> None:
    payload = {
        "features": [
            {
                "attributes": {
                    "identifier": "feature-1",
                    "name": "Gutenstein Formation",
                    "description": "Gutensteiner Kalk (Anis)",
                    "geologicUnitType": "lithostratigraphic unit",
                    "material": "limestone",
                    "representativeLithology": "limestone",
                }
            }
        ]
    }

    provider, client = _provider_for_payload(payload)

    result = provider.get_geology(47.7200, 15.9000)

    assert len(result.records) == 1

    record = result.records[0]
    assert record.identifier == "feature-1"
    assert record.name == "Gutenstein Formation"
    assert record.description == "Gutensteiner Kalk (Anis)"
    assert record.geologic_unit_type == "lithostratigraphic unit"
    assert record.material == "limestone"
    assert record.representative_lithology == "limestone"

    client.close()


def test_get_geology_returns_empty_result_when_no_feature_intersects() -> None:
    provider, client = _provider_for_payload({"features": []})

    result = provider.get_geology(50.0, 15.0)

    assert result.records == ()

    client.close()


def test_get_geology_preserves_multiple_intersecting_features() -> None:
    payload = {
        "features": [
            {
                "attributes": {
                    "identifier": "feature-1",
                    "name": None,
                    "description": None,
                    "geologicUnitType": "lithostratigraphic unit",
                    "material": "carbonate sedimentary rock",
                    "representativeLithology": "carbonate sedimentary rock",
                }
            },
            {
                "attributes": {
                    "identifier": "feature-2",
                    "name": None,
                    "description": None,
                    "geologicUnitType": "lithostratigraphic unit",
                    "material": "clay, breccia",
                    "representativeLithology": "breccia",
                }
            },
            {
                "attributes": {
                    "identifier": "feature-3",
                    "name": None,
                    "description": None,
                    "geologicUnitType": "lithogenetic unit",
                    "material": "clastic sedimentary material",
                    "representativeLithology": "clastic sedimentary material",
                }
            },
        ]
    }

    provider, client = _provider_for_payload(payload)

    result = provider.get_geology(47.71911677, 15.92898294)

    assert len(result.records) == 3
    assert [
        record.representative_lithology
        for record in result.records
    ] == [
        "carbonate sedimentary rock",
        "breccia",
        "clastic sedimentary material",
    ]

    client.close()


def test_get_geology_accepts_nullable_source_fields() -> None:
    payload = {
        "features": [
            {
                "attributes": {
                    "identifier": "feature-1",
                    "name": None,
                    "description": None,
                    "geologicUnitType": None,
                    "material": None,
                    "representativeLithology": None,
                }
            }
        ]
    }

    provider, client = _provider_for_payload(payload)

    result = provider.get_geology(48.0, 16.0)

    record = result.records[0]
    assert record.name is None
    assert record.description is None
    assert record.geologic_unit_type is None
    assert record.material is None
    assert record.representative_lithology is None

    client.close()


def test_get_geology_sends_wgs84_point_query() -> None:
    requested_url: str | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requested_url
        requested_url = str(request.url)
        return httpx.Response(200, json={"features": []})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianGeologyProvider(client)

    provider.get_geology(47.7200, 15.9000)

    assert requested_url is not None

    url = httpx.URL(requested_url)
    params = url.params

    assert params["geometry"] == "15.9,47.72"
    assert params["geometryType"] == "esriGeometryPoint"
    assert params["inSR"] == "4326"
    assert params["spatialRel"] == "esriSpatialRelIntersects"
    assert params["returnGeometry"] == "false"

    client.close()


def test_get_geology_wraps_http_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="server error")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianGeologyProvider(client)

    with pytest.raises(GeologyProviderError, match="failed to fetch geology"):
        provider.get_geology(48.0, 16.0)

    client.close()


def test_get_geology_rejects_arcgis_error() -> None:
    provider, client = _provider_for_payload(
        {
            "error": {
                "code": 400,
                "message": "Invalid query",
            }
        }
    )

    with pytest.raises(
        GeologyProviderError,
        match="ArcGIS error",
    ):
        provider.get_geology(48.0, 16.0)

    client.close()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"features": None},
        {"features": {}},
        {"features": [None]},
        {"features": [{}]},
    ],
)
def test_get_geology_rejects_malformed_response(
    payload: object,
) -> None:
    provider, client = _provider_for_payload(payload)

    with pytest.raises(GeologyProviderError, match="invalid geology response"):
        provider.get_geology(48.0, 16.0)

    client.close()


def test_get_geology_rejects_invalid_identifier() -> None:
    payload = {
        "features": [
            {
                "attributes": {
                    "identifier": None,
                    "name": None,
                    "description": None,
                    "geologicUnitType": None,
                    "material": None,
                    "representativeLithology": None,
                }
            }
        ]
    }

    provider, client = _provider_for_payload(payload)

    with pytest.raises(
        GeologyProviderError,
        match="identifier",
    ):
        provider.get_geology(48.0, 16.0)

    client.close()


def test_get_geology_rejects_non_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AustrianGeologyProvider(client)

    with pytest.raises(
        GeologyProviderError,
        match="expected JSON",
    ):
        provider.get_geology(48.0, 16.0)

    client.close()


@pytest.mark.parametrize(
    ("latitude", "longitude", "message"),
    [
        (91.0, 16.0, "latitude must be between"),
        (-91.0, 16.0, "latitude must be between"),
        (48.0, 181.0, "longitude must be between"),
        (48.0, -181.0, "longitude must be between"),
        (float("nan"), 16.0, "must be finite"),
        (48.0, float("inf"), "must be finite"),
    ],
)
def test_get_geology_rejects_invalid_coordinates(
    latitude: float,
    longitude: float,
    message: str,
) -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(500)
        )
    )
    provider = AustrianGeologyProvider(client)

    with pytest.raises(ValueError, match=message):
        provider.get_geology(latitude, longitude)

    client.close()
