"""
File: src/mushroom_racing/forest/forest.py
Project: mushroom-racing
Purpose: Определить domain contract для классификации лесного покрытия.
Created: 2026-09-15
Last modified: 2026-09-15
Status: production
Lifecycle: long-lived
Inputs: Географические координаты.
Outputs: ForestResult с явным ForestStatus.
Dependencies: Python standard library.
Used by: Forest providers, scoring pipeline.
Notes: Domain layer не зависит от конкретного источника данных или протокола доступа.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ForestStatus(str, Enum):
    """Статус лесного покрытия для географической точки."""

    FOREST = "forest"
    NON_FOREST = "non_forest"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ForestResult:
    """Нормализованный результат определения лесного покрытия."""

    status: ForestStatus


class ForestProviderError(RuntimeError):
    """Ошибка получения или разбора данных forest provider."""


class ForestProvider(Protocol):
    """Контракт источника данных о лесном покрытии."""

    def get_forest_status(
        self,
        latitude: float,
        longitude: float,
    ) -> ForestResult:
        """Вернуть нормализованный статус лесного покрытия для точки."""
        ...
