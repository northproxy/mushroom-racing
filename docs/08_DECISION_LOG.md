# 08 — Decision Log

Этот файл фиксирует только значимые архитектурные и моделирующие решения.

---

## ADR-001 — Сначала rule-based model, не ML

**Статус:** accepted

### Решение

Первая prediction model использует явные правила и веса.

### Почему

- модель проще понимать и тестировать;
- экологические предположения остаются видимыми;
- надёжного training dataset пока нет;
- реальные positive и negative observations позже позволят калибровать модель.

### Следствие

ML откладывается до накопления достаточного количества качественных положительных и отрицательных наблюдений.

---

## ADR-002 — Habitat отделяется от current conditions

**Статус:** accepted

### Решение

Не хранить один постоянный «mushroom score».

Использовать отдельно:

- Habitat Score;
- Current Conditions Score;
- Opportunity Score;
- Confidence.

### Почему

Отличный лес может быть бесперспективным во время засухи, а дождливая неделя не делает неподходящий habitat хорошим.

---

## ADR-003 — Legal restrictions являются hard filters

**Статус:** accepted

### Решение

Если сбор подтверждённо запрещён, участок не может быть рекомендован для сбора независимо от ecological score.

### Почему

Высокая экологическая оценка не должна отменять юридическое ограничение.

---

## ADR-004 — Negative observations сохраняются

**Статус:** accepted

### Решение

Проверенный участок, на котором target species не найден, является полноценным `Observation`.

### Почему

Обучение/калибровка только по успешным находкам создаёт selection bias.

---

## ADR-005 — Evidence level должен быть явным

**Статус:** accepted

### Решение

Экологические знания различают:

- `confirmed_source`;
- `expert_heuristic`;
- `field_observation`;
- `working_hypothesis`.

### Почему

Проект не должен выдавать гипотезу или эвристику за подтверждённый факт.

---

## ADR-006 — Authoritative DEM отделяется от operational access

**Статус:** accepted

### Решение

Authoritative elevation source — официальный Austrian Digital Elevation Model, для стартовой зоны прежде всего Land Niederösterreich DGM 10 m, с Geoland.at DGM Österreich как nationwide fallback.

Обычная работа приложения не требует скачивания полного DEM GeoTIFF. Elevation data получаются через небольшие remote windows/tiles и при необходимости кэшируются локально.

Код обращается к elevation через provider abstraction, поэтому способ доставки может измениться без изменения terrain feature extraction.

### Почему

- официальный GeoTIFF может быть очень большим;
- приложение обычно использует небольшую область вокруг candidate cell;
- authority источника и transport/access mechanism — разные ответственности;
- provider abstraction позволяет сочетать remote, COG/WCS и local GeoTIFF implementations;
- маленький cache снижает storage и bandwidth requirements.

### Validation

Operational provider принимается только после проверки на нескольких контрольных точках против authoritative DGM с зафиксированной допустимой погрешностью.

### Следствие

```text
authoritative DGM
        ↓
ElevationProvider
        ↓
small DEM window / tile
        ↓
local cache
        ↓
elevation / slope / aspect
```

Полный GeoTIFF остаётся полезным для offline validation и bulk processing, но не является runtime dependency.

---

## ADR-007 — Free-first, OCI-preferred, cloud-agnostic infrastructure

**Статус:** accepted

### Решение

Инфраструктура строится по принципу:

> **free-first, OCI-preferred, cloud-agnostic**.

Для development/MVP сначала используются бесплатные и open-source инструменты. Для первого cloud deployment предпочтительным кандидатом является Oracle Cloud Infrastructure Free Tier.

Domain model, feature extraction и scoring engine не зависят от Oracle-specific SDK/API.

### Почему

- learning/portfolio проект не должен создавать необязательные постоянные расходы;
- OCI может дать бесплатную инфраструктуру для небольшого backend/demo;
- cloud portability упрощает тестирование и уменьшает lock-in;
- бесплатность managed service сама по себе не является причиной менять более подходящую технологию.

### Предпочтительное использование OCI

- Compute — backend и небольшие data jobs;
- Object Storage — разрешённые GIS/data artifacts и cache;
- Resource Manager / Terraform — Infrastructure as Code;
- Monitoring / Logging — после появления постоянно работающего сервиса;
- Vault — secrets после появления credentials.

### Ограничения

- Free Tier quotas проверяются непосредственно перед deployment;
- никакой recurring paid resource не включается без отдельного решения;
- cloud deployment не является зависимостью для local development/testing.

### Следствие

```text
core / domain / scoring
        ↓
standard interfaces
        ↓
application adapters
        ↓
local / OCI / other cloud
```

---

## ADR-008 — Unknown data не приравниваются к отрицательному значению

**Статус:** accepted

### Решение

Domain model явно различает:

```text
unknown / missing
```

и

```text
known zero / false
```

Для optional данных используется `None` / JSON `null`, если значение неизвестно или не записано.

Примеры:

- `rain_24h_mm = 0.0` — известно, что осадков не было;
- `rain_24h_mm = null` — данных нет;
- `moss_present = false` — проверено, мха нет;
- `moss_present = null` — признак не проверен/не записан;
- `collecting_allowed = false` — подтверждён запрет;
- `collecting_allowed = null` — юридический статус неизвестен.

### Почему

Смешивание missing data с реальным нулём или `false` создаёт систематические ошибки:

- неизвестный legal status может ошибочно стать разрешением;
- пропущенный погодный показатель может выглядеть как нулевое значение;
- непроставленный полевой признак может ошибочно стать negative observation.

### Следствие

- provider adapters должны сохранять missingness, а не подставлять произвольные defaults;
- feature extraction/scoring обязаны отдельно решать, как работать с `None`;
- confidence может снижаться из-за отсутствующих данных, но отсутствие данных не должно тихо превращаться в отрицательный ecological signal.

---

## ADR-009 — basemap.at используется как default presentation basemap

**Статус:** accepted

### Решение

Для web-карты `mushroom-racing` базовой картографической подложкой по умолчанию является **basemap.at**.

Клиентская карта строится на **MapLibre GL JS**. Поверх базовой карты отображаются собственные аналитические слои `mushroom-racing`, например:

- opportunity / habitat score;
- forest / geology context;
- weather-derived layers;
- legal exclusions;
- observations.

`basemap.at` используется как **presentation basemap**, а не как источник признаков scoring model.

DEM, geology, forest, weather, protected areas и legal rules продолжают поступать из отдельно выбранных и валидированных authoritative sources.

### Почему

- basemap.at основана на официальных геоданных австрийских администраций;
- покрывает территорию Австрии;
- допускает свободное использование по CC BY 4.0 при корректной атрибуции;
- позволяет не создавать и не обслуживать собственную базовую карту;
- соответствует free-first подходу проекта;
- MapLibre уже выбран как предпочтительный frontend map renderer;
- разделение presentation и analytical data сохраняет прозрачность происхождения scoring features.

### Attribution

В публичной карте должна присутствовать корректная атрибуция basemap.at, например:

```text
Grundkarte: basemap.at
```

с ссылкой на `https://basemap.at/`.

### Ограничения и implementation note

На момент принятия ADR basemap.at находится в переходе к новой vector-tile инфраструктуре. Существующие raster/legacy products доступны, а новая vector basemap анонсирована как основной будущий формат.

Поэтому ADR фиксирует **поставщика и архитектурную роль**, но не фиксирует конкретный production endpoint.

Перед реализацией MR-6 необходимо повторно проверить:

- актуальный production endpoint;
- рекомендуемый MapLibre integration path;
- статус vector tiles;
- attribution requirements;
- условия доступности и технические ограничения сервиса.

### Следствие

```text
basemap.at
    ↓
presentation basemap
    ↓
MapLibre GL JS
    ↑
mushroom-racing analytical overlays
    ↑
validated analytical providers
```

Scoring core не зависит от basemap.at и остаётся работоспособным без frontend-карты.

---

## ADR-010 — Карта использует progressive spatial refinement

**Статус:** accepted

### Решение

Пользовательский map workflow строится иерархически: приложение не рассчитывает максимальное spatial resolution сразу для всей области поиска.

На обзорном уровне пользователь выбирает радиус от Вены:

```text
50 / 100 / 150 / 200 km
```

После этого приложение отображает coarse analytical layer. При выборе перспективной зоны загружается или рассчитывается более детальный слой для меньшей территории.

Принцип:

```text
large search area
        ↓
coarse analytical zones
        ↓ user selection / zoom
smaller region
        ↓
higher-resolution candidate cells
        ↓
local sector
```

Конкретный размер cells не фиксируется этим ADR и должен соответствовать resolution исходных данных, производительности и полезности результата.

### Почему

- нет необходимости вычислять детальные признаки для всей территории радиусом до 200 km;
- coarse-to-fine workflow уменьшает объём передаваемых и рассчитываемых данных;
- пользователь естественно переходит от выбора региона к конкретному лесному сектору;
- высокая оценка большого региона не должна создавать впечатление, что вся его территория одинаково перспективна;
- architecture остаётся совместимой с provider-based feature extraction и explainable scoring.

### Следствие

- API/frontend должны поддерживать запрос analytical data для текущего bbox / selected region;
- детальность feature extraction может зависеть от уровня карты;
- overview score и local-sector score являются разными spatial aggregates и не должны молча смешиваться;
- legal hard exclusions применяются на каждом уровне, где соответствующая geometry доступна;
- scoring core остаётся независимым от MapLibre и presentation basemap.

---

## ADR-011 — Organic Maps используется как внешний offline navigation layer через GPX

**Статус:** accepted

### Решение

`mushroom-racing` не реализует собственную полноценную offline-навигацию в MVP.

Приложение отвечает за:

- выбор перспективного сектора;
- построение candidate circular route;
- legal/access filtering;
- route waypoints;
- экспорт маршрута в GPX.

Дальнейшее использование маршрута в лесу передаётся внешнему mobile client — **Organic Maps**.

Предпочтительный workflow:

```text
mushroom-racing routing
        ↓
GPX track + waypoints
        ↓
mobile OS open/share action
        ↓
Organic Maps
        ↓
offline map + GPS + imported track
```

### Почему

- Organic Maps уже решает задачу offline basemap и отображения GPS position;
- проекту не нужно создавать собственные offline map packages и navigation engine;
- GPX является переносимым стандартным форматом;
- scope MVP уменьшается без потери основного field workflow;
- routing intelligence остаётся ответственностью `mushroom-racing`, а отображение offline-карты — внешнего клиента.

### MVP contract

Обязательный contract:

```text
offline map
+ current GPS position
+ visible imported track
```

Не является обязательным:

```text
turn-by-turn navigation
voice guidance
```

`mushroom-racing` не должен зависеть от того, поддерживает ли внешнее приложение полноценную turn-by-turn navigation по произвольному импортированному GPX.

### Приватность

GPX не должен автоматически включать точные приватные координаты успешных hotspot-ов.

Waypoints могут описывать:

- parking / legal start;
- entry point;
- high-opportunity sector;
- terrain/environment context;
- return point.

Добавление точной private observation coordinate требует отдельного явного действия пользователя.

### Ограничения

Capabilities Organic Maps являются внешней зависимостью и могут меняться.

Перед реализацией MR-7 необходимо повторно проверить:

- актуальный GPX import workflow;
- mobile open/share behavior;
- поддержку track и waypoint;
- ограничения отображения импортированного маршрута.

### Следствие

В MVP не реализуются:

- собственные offline tiles;
- offline map package management;
- GPS navigation engine;
- voice guidance;
- собственная turn-by-turn navigation.

Полноценная собственная offline-навигация добавляется только при появлении отдельной подтверждённой необходимости.

---

## ADR-012 — Acquisition, assembly, interpretation и scoring разделены

**Статус:** accepted

### Решение

Geospatial pipeline проекта разделяется на отдельные ответственности:

```text
external data sources
        ↓
provider acquisition
        ↓
normalized / derived source features
        ↓
GeospatialFeatureSet
        ↓
ecological interpretation
        ↓
scoring
```

`GeospatialFeatureSet` является assembly contract и не выполняет
species-specific interpretation или scoring.

Он сохраняет уже нормализованные результаты предыдущих слоёв, включая:

- `TerrainFeatures`;
- `ForestResult`;
- `GeologyQueryResult`;
- `WeatherSnapshot`;
- текущий legal status (`collecting_allowed`).

### Почему

Разделение предотвращает смешивание:

- source acquisition;
- normalization;
- domain interpretation;
- scoring rules.

Это особенно важно для geology: source-level `material` и
`representative_lithology` не должны автоматически превращаться в
`silicate/carbonate` classification внутри provider или assembly layer.

Аналогично:

- `ForestStatus.UNKNOWN` не превращается в `NON_FOREST`;
- weather `None` не превращается в `0`;
- `collecting_allowed=None` не превращается в разрешение или запрет;
- наличие feature не означает автоматически положительный или
  отрицательный ecological signal.

### Следствие

MR-3 отвечает только за получение единого непротиворечивого набора
признаков.

Species-specific interpretation и scoring выполняются отдельным слоем
после `GeospatialFeatureSet`.

Недопустимо добавлять в MR-3 contract без отдельного архитектурного
решения такие поля, как:

```text
is_carbonate
is_silicate
geology_score
terrain_score
weather_score
habitat_score
current_conditions_score
opportunity_score
confidence
eligible
```

Будущая архитектура:

```text
providers
    ↓
normalized source contracts
    ↓
GeospatialFeatureAssembler
    ↓
GeospatialFeatureSet
    ↓
species-specific interpretation
    ↓
explainable scoring
```

### Validation

Решение подтверждено MR-3:

```text
full repository suite: 210 passed in 0.38s
offline integration fixture: PASS
live GeospatialFeatureSet smoke: PASS
```
