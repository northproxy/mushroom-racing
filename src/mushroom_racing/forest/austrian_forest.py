"""
File: src/mushroom_racing/forest/austrian_forest.py
Project: mushroom-racing
Purpose: Получать forest-mask classification из официального BFW Waldkarte WFS.
Created: 2026-09-15
Last modified: 2026-09-15
Status: production
Lifecycle: long-lived
Inputs: Географические координаты WGS84.
Outputs: ForestResult.
Dependencies: httpx, mushroom_racing.forest.forest.
Used by: Austrian forest-mask data pipeline.
Notes: Использует точечный FES Intersects и фактические wfs:member,
       а не numberReturned.
"""

from __future__ import annotations

from math import isfinite
from xml.etree import ElementTree

import httpx

from mushroom_racing.forest.forest import (
    ForestProviderError,
    ForestResult,
    ForestStatus,
)


WFS_URL = (
    "https://haleconnect.com/ows/services/"
    "org.1037.63590ee1-ed40-4c0d-b3ab-50e60af80522_wfs"
)

FEATURE_TYPE = "elu:ExistingLandUseObject"
FORESTRY_SUFFIX = "/forestry"

_WFS_NS = "http://www.opengis.net/wfs/2.0"
_ELU_NS = "http://inspire.ec.europa.eu/schemas/elu/4.0"
_FES_NS = "http://www.opengis.net/fes/2.0"
_GML_NS = "http://www.opengis.net/gml/3.2"
_XLINK_NS = "http://www.w3.org/1999/xlink"

_NAMESPACES = {
    "wfs": _WFS_NS,
    "elu": _ELU_NS,
    "xlink": _XLINK_NS,
}


class AustrianForestProvider:
    """Forest-mask provider на основе BFW Waldkarte Österreich."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        timeout_s: float = 10.0,
    ) -> None:
        if not isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError("timeout_s must be finite and > 0")

        self._client = client
        self._timeout_s = timeout_s

    def get_forest_status(
        self,
        latitude: float,
        longitude: float,
    ) -> ForestResult:
        """Вернуть forest status для координаты WGS84."""

        _validate_coordinates(latitude, longitude)

        request_xml = _build_request_xml(
            latitude=latitude,
            longitude=longitude,
        )

        try:
            response = self._post(request_xml)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ForestProviderError(
                "Failed to retrieve BFW forest data"
            ) from exc

        try:
            root = ElementTree.fromstring(response.content)
        except ElementTree.ParseError as exc:
            raise ForestProviderError(
                "Failed to parse BFW forest response"
            ) from exc

        members = root.findall("wfs:member", _NAMESPACES)

        if not members:
            return ForestResult(status=ForestStatus.NON_FOREST)

        if any(_member_is_forestry(member) for member in members):
            return ForestResult(status=ForestStatus.FOREST)

        return ForestResult(status=ForestStatus.UNKNOWN)

    def _post(self, request_xml: str) -> httpx.Response:
        content = request_xml.encode("utf-8")
        headers = {"Content-Type": "application/xml"}

        if self._client is not None:
            return self._client.post(
                WFS_URL,
                content=content,
                headers=headers,
                timeout=self._timeout_s,
            )

        return httpx.post(
            WFS_URL,
            content=content,
            headers=headers,
            timeout=self._timeout_s,
        )


def _validate_coordinates(latitude: float, longitude: float) -> None:
    if not isfinite(latitude):
        raise ValueError("latitude must be finite")
    if not isfinite(longitude):
        raise ValueError("longitude must be finite")
    if not -90 <= latitude <= 90:
        raise ValueError("latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ValueError("longitude must be between -180 and 180")


def _build_request_xml(
    latitude: float,
    longitude: float,
) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<wfs:GetFeature
    service="WFS"
    version="2.0.0"
    xmlns:wfs="{_WFS_NS}"
    xmlns:fes="{_FES_NS}"
    xmlns:gml="{_GML_NS}"
    xmlns:elu="{_ELU_NS}">
    <wfs:Query
        typeNames="{FEATURE_TYPE}"
        srsName="urn:ogc:def:crs:EPSG::4326">
        <fes:Filter>
            <fes:Intersects>
                <fes:ValueReference>geometry</fes:ValueReference>
                <gml:Point srsName="urn:ogc:def:crs:EPSG::4326">
                    <gml:pos>{latitude} {longitude}</gml:pos>
                </gml:Point>
            </fes:Intersects>
        </fes:Filter>
    </wfs:Query>
</wfs:GetFeature>
"""


def _member_is_forestry(member: ElementTree.Element) -> bool:
    specific_land_use = member.find(
        ".//elu:specificLandUse",
        _NAMESPACES,
    )
    if specific_land_use is None:
        return False

    href = specific_land_use.get(
        f"{{{_XLINK_NS}}}href"
    )

    return (
        href is not None
        and href.rstrip("/").endswith(FORESTRY_SUFFIX)
    )
