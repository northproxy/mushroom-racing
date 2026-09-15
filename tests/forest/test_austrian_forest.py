"""
File: tests/forest/test_austrian_forest.py
Project: mushroom-racing
Purpose: Проверить AustrianForestProvider без сетевых запросов.
Created: 2026-09-15
Last modified: 2026-09-15
Status: test
Lifecycle: long-lived
Inputs: Синтетические BFW WFS responses.
Outputs: pytest assertions.
Dependencies: pytest, httpx, mushroom_racing.forest.
Used by: pytest.
Notes: Unit tests не требуют доступа к BFW WFS.
"""

from __future__ import annotations

import math

import httpx
import pytest

from mushroom_racing.forest import (
    AustrianForestProvider,
    ForestProviderError,
    ForestStatus,
)


WFS_NS = "http://www.opengis.net/wfs/2.0"
ELU_NS = "http://inspire.ec.europa.eu/schemas/elu/4.0"
XLINK_NS = "http://www.w3.org/1999/xlink"


def _response(xml: str, status_code: int = 200) -> httpx.Response:
    request = httpx.Request(
        "POST",
        "https://example.test/wfs",
    )
    return httpx.Response(
        status_code,
        content=xml.encode("utf-8"),
        request=request,
    )


def _client_for_response(response: httpx.Response) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return response

    return httpx.Client(
        transport=httpx.MockTransport(handler),
    )


def _feature_collection(member_xml: str = "") -> str:
    return f"""
    <wfs:FeatureCollection
        xmlns:wfs="{WFS_NS}"
        xmlns:elu="{ELU_NS}"
        xmlns:xlink="{XLINK_NS}"
        numberReturned="0">
        {member_xml}
    </wfs:FeatureCollection>
    """


def _forestry_member() -> str:
    return f"""
    <wfs:member>
        <elu:ExistingLandUseObject>
            <elu:specificLandUse
                xlink:href="https://example.test/registry/forestry"
            />
        </elu:ExistingLandUseObject>
    </wfs:member>
    """


def _non_forestry_member() -> str:
    return f"""
    <wfs:member>
        <elu:ExistingLandUseObject>
            <elu:specificLandUse
                xlink:href="https://example.test/registry/agriculture"
            />
        </elu:ExistingLandUseObject>
    </wfs:member>
    """


def test_returns_forest_for_forestry_member() -> None:
    response = _response(
        _feature_collection(_forestry_member())
    )
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    result = provider.get_forest_status(47.72, 15.90)

    assert result.status is ForestStatus.FOREST


def test_uses_actual_members_even_when_number_returned_is_zero() -> None:
    response = _response(
        _feature_collection(_forestry_member())
    )
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    result = provider.get_forest_status(47.72, 15.90)

    assert result.status is ForestStatus.FOREST


def test_returns_non_forest_when_response_has_no_members() -> None:
    response = _response(_feature_collection())
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    result = provider.get_forest_status(
        47.8520556,
        16.7713333,
    )

    assert result.status is ForestStatus.NON_FOREST


def test_returns_unknown_for_unrecognized_land_use() -> None:
    response = _response(
        _feature_collection(_non_forestry_member())
    )
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    result = provider.get_forest_status(47.72, 15.90)

    assert result.status is ForestStatus.UNKNOWN


def test_returns_forest_when_any_member_is_forestry() -> None:
    response = _response(
        _feature_collection(
            _non_forestry_member() + _forestry_member()
        )
    )
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    result = provider.get_forest_status(47.72, 15.90)

    assert result.status is ForestStatus.FOREST


def test_uses_point_intersects_request() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request

        return httpx.Response(
            200,
            content=_feature_collection().encode("utf-8"),
            request=request,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
    )
    provider = AustrianForestProvider(client=client)

    provider.get_forest_status(47.72, 15.90)

    assert captured_request is not None
    assert captured_request.method == "POST"
    assert captured_request.headers["content-type"] == "application/xml"

    request_xml = captured_request.content.decode("utf-8")

    assert "<fes:Intersects>" in request_xml
    assert (
        "<fes:ValueReference>geometry</fes:ValueReference>"
        in request_xml
    )
    assert (
        '<gml:Point srsName="urn:ogc:def:crs:EPSG::4326">'
        in request_xml
    )
    assert "<gml:pos>47.72 15.9</gml:pos>" in request_xml
    assert "bbox" not in request_xml.lower()


def test_raises_provider_error_for_malformed_xml() -> None:
    response = _response("<not-valid")
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    with pytest.raises(
        ForestProviderError,
        match="parse BFW forest response",
    ):
        provider.get_forest_status(47.72, 15.90)


def test_raises_provider_error_for_http_error() -> None:
    response = _response(
        "Service unavailable",
        status_code=503,
    )
    client = _client_for_response(response)
    provider = AustrianForestProvider(client=client)

    with pytest.raises(
        ForestProviderError,
        match="retrieve BFW forest data",
    ):
        provider.get_forest_status(47.72, 15.90)


def test_raises_provider_error_for_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
    )
    provider = AustrianForestProvider(client=client)

    with pytest.raises(
        ForestProviderError,
        match="retrieve BFW forest data",
    ):
        provider.get_forest_status(47.72, 15.90)


@pytest.mark.parametrize(
    ("latitude", "longitude", "message"),
    [
        (91.0, 16.0, "latitude"),
        (-91.0, 16.0, "latitude"),
        (47.0, 181.0, "longitude"),
        (47.0, -181.0, "longitude"),
        (math.nan, 16.0, "latitude"),
        (47.0, math.inf, "longitude"),
    ],
)
def test_rejects_invalid_coordinates(
    latitude: float,
    longitude: float,
    message: str,
) -> None:
    provider = AustrianForestProvider()

    with pytest.raises(ValueError, match=message):
        provider.get_forest_status(latitude, longitude)


@pytest.mark.parametrize(
    "timeout_s",
    [
        0.0,
        -1.0,
        math.nan,
        math.inf,
    ],
)
def test_rejects_invalid_timeout(timeout_s: float) -> None:
    with pytest.raises(ValueError, match="timeout_s"):
        AustrianForestProvider(timeout_s=timeout_s)
