# MR-1 Domain model — final cumulative slice

Этот пакет содержит итоговый результат MR-1:

- `EvidenceLevel` / `EvidenceRecord`;
- `SpeciesProfile`;
- `ForestSpot`;
- `WeatherSnapshot`;
- `Observation`;
- общий GeoJSON-compatible geometry contract;
- строгий JSON parsing без неявного cast плохих типов;
- JSON fixtures;
- validation и serialization tests;
- обновления `04_DATABASE_SCHEMA.md`, `07_ROADMAP.md`, `08_DECISION_LOG.md` и `README.md`.

## Главные semantics

- `None` / JSON `null` означает unknown/missing, а не ноль или `false`.
- `collecting_allowed=None` не является разрешением.
- `rain_24h_mm=0.0` отличается от отсутствующих погодных данных.
- `false` и `null` у field-observation признаков различаются.
- positive и negative search используют одну сущность `Observation`.
- search effort хранится независимо от результата поиска.
- все timestamps domain-уровня должны быть timezone-aware.
- явные физические единицы входят в имена полей там, где это возможно.

## Geometry

`ForestSpot` и `Observation` используют `Point`, `Polygon` или `MultiPolygon` в минимальном 2D GeoJSON-compatible формате.

Domain layer проверяет структуру и базовые coordinate constraints, но не зависит от Shapely/GeoPandas. Полная GIS topology validation остаётся задачей geospatial layer.

## Fixtures

Все публичные fixtures синтетические. Они не содержат реальных приватных mushroom hotspots.

`boletus_edulis.json` — baseline model fixture. Экологические значения без зафиксированного научного источника не выдаются за `confirmed_source`.

## Validation

В этом cumulative slice выполнено:

```bash
PYTHONPATH=src python -m pytest -q tests/domain
```

Результат:

```text
36 passed
```

Также выполнено:

```bash
python -m compileall -q src tests
```

`ruff` в текущем execution environment не установлен, поэтому linting не заявляется как выполненный.

## Integration note

Scoring baseline намеренно не входит в этот пакет и не изменяется.

После копирования файлов в основной repository необходимо дополнительно запустить полный:

```bash
pytest
```

Это подтвердит отсутствие integration regressions между MR-1 domain model и существующим baseline scoring/repository code.
