"""Domain-типы для фиксации уровня доказательности данных."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from .parsing import optional_string, required_string


class EvidenceLevel(StrEnum):
    """Допустимые уровни доказательности в проекте."""

    CONFIRMED_SOURCE = "confirmed_source"
    EXPERT_HEURISTIC = "expert_heuristic"
    FIELD_OBSERVATION = "field_observation"
    WORKING_HYPOTHESIS = "working_hypothesis"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Связывает поле domain-модели с уровнем доказательности и источником."""

    field_name: str
    level: EvidenceLevel
    source_id: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.field_name.strip():
            raise ValueError("field_name must not be empty")

        if self.source_id is not None and not self.source_id.strip():
            raise ValueError("source_id must not be empty when provided")

        if self.note is not None and not self.note.strip():
            raise ValueError("note must not be empty when provided")

        # Подтверждённое утверждение должно быть трассируемым до конкретного источника.
        if self.level is EvidenceLevel.CONFIRMED_SOURCE and self.source_id is None:
            raise ValueError("confirmed_source evidence requires source_id")

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "level": self.level.value,
            "source_id": self.source_id,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvidenceRecord":
        return cls(
            field_name=required_string(data["field_name"], "field_name"),
            level=EvidenceLevel(required_string(data["level"], "level")),
            source_id=optional_string(data.get("source_id"), "source_id"),
            note=optional_string(data.get("note"), "note"),
        )
