"""Строгие helpers для разбора JSON-подобных domain-данных."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def required_string(value: Any, field_name: str) -> str:
    """Возвращает обязательную строку без неявного преобразования типов."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def optional_string(value: Any, field_name: str) -> str | None:
    """Возвращает optional-строку, сохраняя ``null`` как отсутствие данных."""

    if value is None:
        return None
    return required_string(value, field_name)


def string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    """Разбирает JSON-массив строк без приведения чисел и других типов."""

    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be a list or tuple")

    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"{field_name} must contain only strings")
        result.append(item)
    return tuple(result)


def int_tuple(value: Any, field_name: str) -> tuple[int, ...]:
    """Разбирает JSON-массив целых чисел без округления float-значений."""

    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be a list or tuple")

    result: list[int] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int):
            raise TypeError(f"{field_name} must contain only integers")
        result.append(item)
    return tuple(result)


def optional_float(value: Any, field_name: str) -> float | None:
    """Разбирает optional JSON number и запрещает строки/boolean как числа."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number or null")
    return float(value)


def optional_int(value: Any, field_name: str) -> int | None:
    """Разбирает optional integer без неявного округления или cast из строки."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer or null")
    return value


def required_bool(value: Any, field_name: str) -> bool:
    """Разбирает обязательный boolean."""

    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be boolean")
    return value


def optional_bool(value: Any, field_name: str) -> bool | None:
    """Разбирает optional boolean, сохраняя отличие ``false`` от ``null``."""

    if value is None:
        return None
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be boolean or null")
    return value


def required_datetime(value: Any, field_name: str) -> datetime:
    """Разбирает обязательный ISO 8601 timestamp из JSON-строки."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be an ISO 8601 string")
    return datetime.fromisoformat(value)


def optional_datetime(value: Any, field_name: str) -> datetime | None:
    """Разбирает optional ISO 8601 timestamp."""

    if value is None:
        return None
    return required_datetime(value, field_name)
