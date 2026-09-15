"""Контракты данных для geological point-query."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class GeologyRecord:
    """Одна geological unit, возвращённая внешним источником."""

    identifier: str
    name: str | None
    description: str | None
    geologic_unit_type: str | None
    material: str | None
    representative_lithology: str | None

    def __post_init__(self) -> None:
        """Проверяет минимальные инварианты source-level записи."""
        if not isinstance(self.identifier, str):
            raise TypeError("identifier must be a string")
        if not self.identifier.strip():
            raise ValueError("identifier must not be empty")


@dataclass(frozen=True, slots=True)
class GeologyQueryResult:
    """Результат geology point-query с cardinality 0..N."""

    records: tuple[GeologyRecord, ...]


class GeologyProvider(Protocol):
    """Контракт источника geology-данных для WGS84-точки."""

    def get_geology(
        self,
        latitude: float,
        longitude: float,
    ) -> GeologyQueryResult:
        """Возвращает geological units, пересекающие WGS84-точку."""
        ...
