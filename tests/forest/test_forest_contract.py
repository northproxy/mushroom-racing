"""
File: tests/forest/test_forest.py
Project: mushroom-racing
Purpose: Проверить минимальный forest domain contract.
Created: 2026-09-15
Last modified: 2026-09-15
Status: test
Lifecycle: long-lived
Inputs: ForestStatus, ForestResult, ForestProvider.
Outputs: pytest assertions.
Dependencies: pytest, mushroom_racing.forest.
Used by: pytest.
Notes: Тесты не зависят от BFW, WFS или сети.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from mushroom_racing.forest import (
    ForestProvider,
    ForestResult,
    ForestStatus,
)


@pytest.mark.parametrize(
    ("status", "expected_value"),
    [
        (ForestStatus.FOREST, "forest"),
        (ForestStatus.NON_FOREST, "non_forest"),
        (ForestStatus.UNKNOWN, "unknown"),
    ],
)
def test_forest_status_values(
    status: ForestStatus,
    expected_value: str,
) -> None:
    assert status.value == expected_value


@pytest.mark.parametrize(
    "status",
    [
        ForestStatus.FOREST,
        ForestStatus.NON_FOREST,
        ForestStatus.UNKNOWN,
    ],
)
def test_forest_result_preserves_status(
    status: ForestStatus,
) -> None:
    result = ForestResult(status=status)

    assert result.status is status


def test_forest_result_is_immutable() -> None:
    result = ForestResult(status=ForestStatus.FOREST)

    with pytest.raises(FrozenInstanceError):
        result.status = ForestStatus.NON_FOREST  # type: ignore[misc]


def test_structural_forest_provider_contract() -> None:
    class FakeForestProvider:
        def get_forest_status(
            self,
            latitude: float,
            longitude: float,
        ) -> ForestResult:
            return ForestResult(status=ForestStatus.FOREST)

    provider: ForestProvider = FakeForestProvider()

    result = provider.get_forest_status(
        latitude=47.7200,
        longitude=15.9000,
    )

    assert result == ForestResult(status=ForestStatus.FOREST)
