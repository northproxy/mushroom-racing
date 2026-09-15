"""
File: test_austrian_weather_provider.py
Project: mushroom-racing

Purpose:
    Проверяет parsing, normalization и fail-fast semantics AustrianWeatherProvider.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — unit tests для GeoSphere SPARTACUS provider.

Inputs:
    Синтетические GeoSphere JSON payloads.

Outputs:
    Pytest assertions.

Dependencies:
    pytest
    Python standard library

Used by:
    pytest

Notes:
    Unit tests не выполняют live network requests.
"""

from copy import deepcopy
from datetime import date
import json
import urllib.error

import pytest

from mushroom_racing.providers.austrian_weather import AustrianWeatherProvider
from mushroom_racing.providers.weather import (
    WeatherAvailability,
    WeatherProviderError,
)


class FakeResponse:
    def __init__(self, payload: object, *, status: int = 200) -> None:
        self.status = status
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self._raw


def _payload() -> dict:
    return {
        "media_type": "application/json",
        "type": "FeatureCollection",
        "version": "v1",
        "timestamps": [
            "2026-09-10T00:00+00:00",
            "2026-09-11T00:00+00:00",
            "2026-09-12T00:00+00:00",
        ],
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [15.900300979614258, 47.718814849853516],
                },
                "properties": {
                    "parameters": {
                        "RR": {
                            "name": "daily precipitation sum",
                            "unit": "kg m-2",
                            "data": [26.30000039190054, 1.9000000283122065, 0.0],
                        },
                        "TM24": {
                            "name": "daily mean of air temperature ",
                            "unit": "degC",
                            "data": [9.00000013411045, 8.700000129640102, 11.9],
                        },
                        "TN": {
                            "name": "daily minimum of air temperature",
                            "unit": "degC",
                            "data": [6.9, 7.3, 8.5],
                        },
                        "TX": {
                            "name": "daily maximum of air temperature",
                            "unit": "degC",
                            "data": [13.3, 10.4, 16.0],
                        },
                    }
                },
            }
        ],
        "datapoints": 12,
    }


def _patch_response(monkeypatch: pytest.MonkeyPatch, payload: object) -> None:
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda request, timeout: FakeResponse(payload),
    )


def test_provider_parses_spartacus_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_response(monkeypatch, _payload())

    result = AustrianWeatherProvider().get_daily_series(
        47.7200,
        15.9000,
        date(2026, 9, 10),
        date(2026, 9, 12),
    )

    assert result.source_id == "geosphere_spartacus_v3_1d_1km"
    assert result.requested_latitude == 47.7200
    assert result.requested_longitude == 15.9000
    assert result.source_latitude == pytest.approx(47.718814849853516)
    assert result.source_longitude == pytest.approx(15.900300979614258)
    assert len(result.records) == 3
    assert result.records[0].precipitation_mm == pytest.approx(
        26.30000039190054
    )
    assert result.records[2].precipitation_mm == 0.0
    assert result.availability is WeatherAvailability.AVAILABLE


def test_provider_builds_expected_query(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return FakeResponse(_payload())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    AustrianWeatherProvider().get_daily_series(
        47.7200,
        15.9000,
        date(2026, 9, 10),
        date(2026, 9, 12),
    )

    assert "parameters=RR%2CTM24%2CTN%2CTX" in captured["url"]
    assert "start=2026-09-10" in captured["url"]
    assert "end=2026-09-12" in captured["url"]
    assert "lat_lon=47.72%2C15.9" in captured["url"]
    assert captured["timeout"] == 30


def test_all_null_payload_becomes_no_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    for parameter in payload["features"][0]["properties"]["parameters"].values():
        parameter["data"] = [None, None, None]
    _patch_response(monkeypatch, payload)

    result = AustrianWeatherProvider().get_daily_series(
        48.1372,
        11.5756,
        date(2026, 9, 10),
        date(2026, 9, 12),
    )

    assert result.availability is WeatherAvailability.NO_DATA
    assert all(record.precipitation_mm is None for record in result.records)


def test_partial_null_payload_becomes_partial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["features"][0]["properties"]["parameters"]["TM24"]["data"][1] = None
    _patch_response(monkeypatch, payload)

    result = AustrianWeatherProvider().get_daily_series(
        47.7200,
        15.9000,
        date(2026, 9, 10),
        date(2026, 9, 12),
    )

    assert result.records[1].mean_temperature_c is None
    assert result.availability is WeatherAvailability.PARTIAL


def test_zero_precipitation_remains_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_response(monkeypatch, _payload())

    result = AustrianWeatherProvider().get_daily_series(
        47.7200,
        15.9000,
        date(2026, 9, 10),
        date(2026, 9, 12),
    )

    assert result.records[-1].precipitation_mm == 0.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("latitude", 91.0),
        ("longitude", 181.0),
    ],
)
def test_provider_rejects_invalid_requested_coordinates(
    field: str,
    value: float,
) -> None:
    kwargs = {
        "latitude": 47.7200,
        "longitude": 15.9000,
        "start_date": date(2026, 9, 10),
        "end_date": date(2026, 9, 12),
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        AustrianWeatherProvider().get_daily_series(**kwargs)


def test_provider_rejects_reversed_date_range() -> None:
    with pytest.raises(ValueError, match="start_date"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 12),
            date(2026, 9, 10),
        )


def test_provider_wraps_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(request, timeout):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr("urllib.request.urlopen", fail)

    with pytest.raises(WeatherProviderError, match="request failed"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )


def test_provider_rejects_malformed_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class InvalidJsonResponse(FakeResponse):
        def read(self) -> bytes:
            return b"{not-json"

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda request, timeout: InvalidJsonResponse({}),
    )

    with pytest.raises(WeatherProviderError, match="malformed JSON"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )


def test_provider_rejects_timestamp_parameter_length_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["features"][0]["properties"]["parameters"]["RR"]["data"].pop()
    _patch_response(monkeypatch, payload)

    with pytest.raises(WeatherProviderError, match="length"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )


def test_provider_rejects_unexpected_unit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["features"][0]["properties"]["parameters"]["RR"]["unit"] = "mm"
    _patch_response(monkeypatch, payload)

    with pytest.raises(WeatherProviderError, match="Unexpected unit"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )


def test_provider_rejects_missing_parameter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    del payload["features"][0]["properties"]["parameters"]["TX"]
    _patch_response(monkeypatch, payload)

    with pytest.raises(WeatherProviderError, match="TX"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )


def test_provider_rejects_non_point_geometry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["features"][0]["geometry"] = {
        "type": "Polygon",
        "coordinates": [],
    }
    _patch_response(monkeypatch, payload)

    with pytest.raises(WeatherProviderError, match="Point"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )


def test_provider_rejects_negative_precipitation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["features"][0]["properties"]["parameters"]["RR"]["data"][0] = -0.1
    _patch_response(monkeypatch, payload)

    with pytest.raises(WeatherProviderError, match="precipitation"):
        AustrianWeatherProvider().get_daily_series(
            47.7200,
            15.9000,
            date(2026, 9, 10),
            date(2026, 9, 12),
        )
