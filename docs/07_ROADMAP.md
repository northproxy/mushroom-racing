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

### Forest mask block ✅

Завершены:

-   выбран официальный `Waldkarte BFW Österreich` как primary
    forest-mask source;
-   подтверждён live WFS 2.0 access path и feature type
    `elu:ExistingLandUseObject`;
-   реализованы `ForestStatus`, `ForestResult`, `ForestProvider`,
    `ForestProviderError` и `AustrianForestProvider`;
-   зафиксирована семантика `FOREST / NON_FOREST / UNKNOWN`;
-   production query использует точный FES 2.0 `Intersects` с
    `gml:Point`;
-   positive control `47.7200, 15.9000` подтверждён как `FOREST`;
-   negative lake control `47.8520556, 16.7713333` подтверждён как
    `NON_FOREST`;
-   provider использует реальные `wfs:member`, а не ненадёжный
    `numberReturned`;
-   transport / HTTP / malformed XML errors обрабатываются fail-fast
    через `ForestProviderError`;
-   production live smoke подтверждён через `AustrianForestProvider`.

Проверка после MR-2.6:

``` text
forest slice: 27 passed
full repository suite: 146 passed
```

Подробности:

``` text
docs/data_sources/FOREST.md
```

### Осталось в MR-2

-   один protected-area layer;
-   документированные лицензии для оставшихся выбранных источников.

Следующий блок:

``` text
protected-area geometry + licensing PoC
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

## MR-6 --- Interactive Map MVP

Результат:

-   web-карта на MapLibre GL JS;
-   `basemap.at` как default presentation basemap;
-   собственный `mushroom-racing` analytical overlay поверх basemap;
-   выбор радиуса `50 / 100 / 150 / 200 km` от Вены;
-   overview analytical zones / candidate cells;
-   opportunity / habitat score visualization;
-   progressive spatial refinement при выборе региона;
-   более детальный analytical layer после zoom/selection;
-   spot details: Habitat / Current Conditions / Opportunity /
    Confidence;
-   weather context и explainability;
-   legal exclusions;
-   отображение наличия или отсутствия field observations;
-   корректная attribution для basemap.at и других отображаемых
    источников.

Архитектурный принцип:

``` text
large search area
        ↓
coarse analytical layer
        ↓ user selection
smaller region
        ↓
higher-resolution analytical layer
        ↓
local candidate sector
```

Размеры analytical cells заранее не фиксируются и должны соответствовать
resolution исходных данных, performance и полезности результата.

Проверка:

-   карта воспроизводимо запускается локально и через mobile browser;
-   пользователь может выбрать каждый предусмотренный radius;
-   basemap и analytical overlay загружаются независимо;
-   выбор зоны приводит к загрузке более детального слоя;
-   карточка сектора показывает score, confidence, reasons, weather
    context и legal status;
-   hard-excluded areas не отображаются как обычные перспективные
    sectors;
-   scoring core не зависит от доступности basemap;
-   перед интеграцией подтверждены актуальный production endpoint и
    условия использования basemap.at.

## MR-7 --- Field workflow, routes and offline handoff

Результат:

-   positive reports;
-   negative reports;
-   observation persistence;
-   observation history;
-   photo references;
-   статистика для проверенного сектора;
-   корректное состояние для сектора без observations;
-   candidate circular routes от legal start / parking point;
-   route length и приблизительное время;
-   маршруты проходят через несколько высоко оценённых candidate cells;
-   подтверждённые legal/access exclusions учитываются до экспорта;
-   GPX export с track и waypoints;
-   mobile open/share workflow в Organic Maps.

Разделение ответственности:

``` text
mushroom-racing
    scoring + candidate cells + routing + GPX
        ↓
Organic Maps
    offline basemap + GPS + imported track display
```

MVP contract для external navigation:

``` text
offline map
+ current GPS position
+ visible imported track
```

Полноценная turn-by-turn / voice navigation по импортированному GPX не
является обязательным требованием `mushroom-racing`.

Проверка:

-   positive и negative observations сохраняются и повторно загружаются;
-   фото или ссылки на фото связаны с observation без публикации
    приватных hotspot coordinates;
-   для выбранного сектора строится хотя бы один замкнутый candidate
    route;
-   route начинается и заканчивается в одной стартовой точке;
-   hard-excluded geometry не входит в маршрут;
-   GPX проходит basic parser/schema validation;
-   GPX открывается/importируется в актуальной версии Organic Maps после
    повторной проверки поддерживаемого mobile workflow.

## MR-8 --- Calibration

Результат:

-   prediction vs observation analysis;
-   weight adjustments;
-   calibration report;
-   documented model limitations.

Проверка:

-   positive и negative observations анализируются отдельно;
-   calibration не использует только успешные находки;
-   изменения weights имеют воспроизводимое обоснование;
-   baseline и calibrated model можно сравнить на одном observation set.

## MR-9 --- GitHub portfolio release

Результат:

-   screenshots;
-   architecture diagram;
-   demo dataset;
-   reproducible setup;
-   release notes;
-   polished README;
-   демонстрация полного workflow от map selection до GPX/field
    observation без публикации приватных hotspot-ов.

## Позже

-   multiple species;
-   personalized models;
-   более сложная route optimization;
-   confidence-aware recommendations;
-   statistical/ML calibration;
-   собственная offline navigation только если появится обоснованная
    необходимость.
