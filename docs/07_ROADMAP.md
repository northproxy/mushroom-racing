# 07 — Roadmap

Roadmap строится вокруг воспроизводимых milestone с проверяемым результатом.

## MR-0 — Repository baseline ✅

Результат:

- структура документации;
- baseline knowledge model;
- базовый Python package;
- baseline scoring engine;
- тесты;
- CI workflow.

Проверка:

```bash
pytest
```

## MR-1 — Domain model ✅

**Завершён:** 2026-09-14

Результат:

- стабильный `SpeciesProfile`;
- `EvidenceLevel` / `EvidenceRecord`;
- стабильный `ForestSpot`;
- `WeatherSnapshot`;
- `Observation` для positive и negative search;
- общий минимальный GeoJSON-compatible geometry contract;
- JSON sample fixtures;
- fail-fast validation;
- JSON serialization/deserialization tests.

Проверка MR-1 slice:

```bash
PYTHONPATH=src python -m pytest -q tests/domain
```

Результат проверки при завершении milestone:

```text
36 passed
```

Дополнительно:

```bash
python -m compileall -q src tests
```

Ограничение проверки: MR-1 тесты были прогнаны на накопительном domain slice. После применения файлов к основному repository нужно также запустить полный repository-level `pytest`, чтобы подтвердить отсутствие integration regressions с baseline scoring и остальным кодом.

## MR-2 — Austrian data-source proof of concept

Результат:

- один воспроизводимый forest layer;
- один DEM access workflow;
- один geology layer;
- один protected-area layer;
- документированные лицензии.

Проверка:

- repeatable import/query script;
- sample output сохраняется там, где это разрешает лицензия;
- operational DEM access сверяется с authoritative DGM.

## MR-3 — Geospatial feature extraction

Результат:

- elevation;
- slope;
- aspect;
- forest mask;
- geology class;
- legal eligibility.

Проверка:

- известные test coordinates / fixtures;
- expected feature assertions.

## MR-4 — Weather pipeline

Результат:

- rainfall history;
- rolling 3/7/14/21/28-day totals;
- temperature windows;
- drought/history context.

Проверка:

- deterministic calculations from fixture data.

## MR-5 — Steinpilz v0.1 scoring

Результат:

- habitat score;
- current conditions score;
- opportunity score;
- confidence;
- explanation.

Проверка:

- scenario tests;
- comparison against documented field observations.

## MR-6 — Map MVP

Результат:

- candidate forest cells;
- score visualization;
- spot details;
- legal exclusions.

## MR-7 — Field observation workflow

Результат:

- positive reports;
- negative reports;
- observation persistence;
- export.

## MR-8 — Calibration

Результат:

- prediction vs observation analysis;
- weight adjustments;
- calibration report;
- documented model limitations.

## MR-9 — GitHub portfolio release

Результат:

- screenshots;
- architecture diagram;
- demo dataset;
- reproducible setup;
- release notes;
- polished README.

## Позже

- multiple species;
- personalized models;
- route planning;
- confidence-aware recommendations;
- statistical/ML calibration.
