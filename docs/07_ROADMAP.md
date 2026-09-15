# 07 --- Roadmap

Roadmap строится вокруг воспроизводимых milestone с проверяемым
результатом.

## MR-0 --- Repository baseline ✅

Результат:

-   структура документации;
-   baseline knowledge model;
-   базовый Python package;
-   baseline scoring engine;
-   тесты;
-   CI workflow.

Проверка:

``` bash
pytest
```

## MR-1 --- Domain model ✅

**Завершён:** 2026-09-14

Результат:

-   стабильный `SpeciesProfile`;
-   `EvidenceLevel` / `EvidenceRecord`;
-   стабильный `ForestSpot`;
-   `WeatherSnapshot`;
-   `Observation` для positive и negative search;
-   общий минимальный GeoJSON-compatible geometry contract;
-   JSON sample fixtures;
-   fail-fast validation;
-   JSON serialization/deserialization tests.

Проверка MR-1 slice:

``` bash
PYTHONPATH=src python -m pytest -q tests/domain
```

Результат проверки при завершении milestone:

``` text
36 passed
```

Дополнительно:

``` bash
python -m compileall -q src tests
```

Ограничение проверки: MR-1 тесты были прогнаны на накопительном domain
slice. После применения файлов к основному repository нужно также
запустить полный repository-level `pytest`, чтобы подтвердить отсутствие
integration regressions с baseline scoring и остальным кодом.

## MR-2 --- Austrian data-source proof of concept

**Статус:** in progress

### DEM / terrain block ✅

Завершены:

-   `ElevationProvider` / `ElevationWindow` contract;
-   live `AustrianElevationProvider`;
-   elevation validation against authoritative NÖ Atlas / DGM sample;
-   `TerrainFeatures` extraction: elevation / slope / aspect;
-   Horn 3x3 slope/aspect calculation;
-   EPSG:3857 local ground-scale correction;
-   persistent `CachedElevationProvider`;
-   atomic `.npz` cache writes;
-   namespace-based cache invalidation;
-   cross-process live cache-hit validation.

Проверка после MR-2.4:

``` text
84 passed in 0.21s
```

DEM / terrain pipeline:

``` text
authoritative DGM
        ↓
operational provider
        ↓
persistent local cache
        ↓
ElevationWindow
        ↓
elevation / slope / aspect
```

### Geology block ✅

Завершены:

-   выбран официальный GeoSphere Austria `GE.GeologicUnit_50k`;
-   реализованы `GeologyProvider`, `GeologyQueryResult`, `GeologyRecord`
    и live `AustrianGeologyProvider`;
-   подтверждён WGS84 ArcGIS REST point-query;
-   подтверждена source cardinality `0..N`;
-   проверен validation sample из 7 точек;
-   проверены edge cases с `0` и `3` intersecting features;
-   source-level geology отделена от будущей silicate/carbonate
    interpretation и scoring;
-   production live smoke подтверждён на `47.7200, 15.9000`.

Проверка после MR-2.5:

``` text
geology slice: 27 passed
full repository suite: 111 passed
```

### Осталось в MR-2

-   один forest layer;
-   один protected-area layer;
-   документированные лицензии для оставшихся выбранных источников.

Следующий блок:

``` text
BFW forest-mask source PoC
```

Definition of Done MR-2:

-   repeatable import/query workflow для выбранных P0 layers;
-   sample output сохраняется там, где это разрешает лицензия;
-   source / license / access limitations документированы;
-   operational data path проверен воспроизводимо.

## MR-3 --- Geospatial feature extraction

Результат:

-   интеграция уже реализованных elevation / slope / aspect;
-   forest mask;
-   geology class;
-   legal eligibility;
-   единый geospatial feature assembly для scoring.

Проверка:

-   известные test coordinates / fixtures;
-   expected feature assertions.

## MR-4 --- Weather pipeline

Результат:

-   rainfall history;
-   rolling 3/7/14/21/28-day totals;
-   temperature windows;
-   drought/history context.

Проверка:

-   deterministic calculations from fixture data.

## MR-5 --- Steinpilz v0.1 scoring

Результат:

-   habitat score;
-   current conditions score;
-   opportunity score;
-   confidence;
-   explanation.

Проверка:

-   scenario tests;
-   comparison against documented field observations.

## MR-6 --- Map MVP

Результат:

-   web-карта на MapLibre GL JS;
-   `basemap.at` как default presentation basemap;
-   собственный `mushroom-racing` analytical overlay поверх basemap;
-   candidate forest cells;
-   opportunity / habitat score visualization;
-   переключение релевантных аналитических слоёв;
-   spot details / explainability при выборе участка;
-   legal exclusions;
-   корректная attribution для basemap.at и других отображаемых
    источников.

Проверка:

-   карта воспроизводимо запускается локально;
-   basemap и analytical overlay загружаются независимо;
-   scoring core не зависит от доступности basemap;
-   перед интеграцией подтверждены актуальный production endpoint и
    условия использования basemap.at.

## MR-7 --- Field observation workflow

Результат:

-   positive reports;
-   negative reports;
-   observation persistence;
-   export.

## MR-8 --- Calibration

Результат:

-   prediction vs observation analysis;
-   weight adjustments;
-   calibration report;
-   documented model limitations.

## MR-9 --- GitHub portfolio release

Результат:

-   screenshots;
-   architecture diagram;
-   demo dataset;
-   reproducible setup;
-   release notes;
-   polished README.

## Позже

-   multiple species;
-   personalized models;
-   route planning;
-   confidence-aware recommendations;
-   statistical/ML calibration.
