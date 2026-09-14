# MR-1 — итоговое сравнение изменений

## Что было до финализации

Cumulative slice v4 уже содержал:

- `EvidenceLevel` / `EvidenceRecord`;
- `SpeciesProfile`;
- `ForestSpot`;
- `WeatherSnapshot`;
- `Observation`;
- JSON fixtures;
- 29 domain tests.

## Что изменено при финализации

### 1. Fail-fast JSON parsing

Добавлен внутренний `domain/parsing.py`.

До изменения некоторые `from_dict()` использовали конструкции вроде:

```python
str(value)
int(value)
float(value)
```

Из-за этого повреждённые данные могли тихо преобразоваться, например `null -> "None"` или `1.5 -> 1`.

Теперь JSON-like input проверяется строго:

- required string должен быть строкой;
- numeric string не считается JSON number;
- boolean не считается числом;
- integer не округляется из float;
- массив строк не принимает числа с автоматическим `str(...)`.

Публичный domain contract при этом не изменён.

### 2. Geometry contract усилен

`Point`, `Polygon`, `MultiPolygon` теперь имеют минимальную структурную 2D validation:

- longitude/latitude проверяются по допустимым диапазонам;
- Polygon содержит linear rings;
- linear ring содержит минимум четыре positions;
- linear ring должен быть замкнут;
- MultiPolygon содержит корректные polygons.

Shapely/GeoPandas по-прежнему не являются зависимостью domain layer.

### 3. Дополнительные tests

Добавлены проверки:

- malformed required string;
- malformed evidence record;
- numeric string в weather JSON;
- float вместо integer count;
- valid Polygon;
- invalid unclosed Polygon;
- valid MultiPolygon.

Итог:

```text
36 passed
```

### 4. Документация синхронизирована с реальным contract

Обновлены:

- `docs/02_DATA_SOURCES.md`;
- `docs/04_DATABASE_SCHEMA.md`;
- `docs/07_ROADMAP.md`;
- `docs/08_DECISION_LOG.md`;
- `README.md`.

Зафиксированы:

- явные units в именах полей;
- `null != 0/false`;
- timezone-aware timestamps;
- MR-1 domain schema;
- `EvidenceRecord`;
- `ADR-008` о missing/unknown semantics;
- MR-1 как завершённый milestone;
- устранено старое `DEM = TODO` в кратком source registry.

## Что намеренно не изменено

- baseline `SpotFeatures`;
- `ScoreResult`;
- `score_spot()`;
- scoring weights;
- external provider implementations;
- database/storage implementation;
- GIS feature extraction.

## Проверка

В cumulative slice выполнены:

```bash
PYTHONPATH=src python -m pytest -q tests/domain
python -m compileall -q src tests
```

Результат pytest:

```text
36 passed
```

`ruff` в execution environment отсутствует, поэтому linting не заявляется как выполненный.

## После копирования в основной repository

Обязательно выполнить полный repository-level тест:

```bash
pytest
```

Это отдельная integration-проверка существующего baseline scoring с новым domain package.
