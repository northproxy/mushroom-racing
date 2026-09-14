# 04 — Схема данных

## Назначение

Документ фиксирует логический контракт данных проекта.

На стадии MR-1 это **не физическая схема PostgreSQL/SQLite**. Сначала domain model определяет смысл полей и правила валидности; конкретное отображение в таблицы БД появится только тогда, когда persistent storage действительно понадобится.

Основное разделение остаётся прежним:

- `SpeciesProfile` — знания о виде;
- `ForestSpot` — относительно статические характеристики участка;
- `WeatherSnapshot` — динамическое состояние погоды для участка;
- `Observation` — положительный или отрицательный полевой поиск;
- `LegalZone` и `Source` — отдельные сущности будущего persistence/data-source слоя.

## Общие правила MR-1

### Явные единицы измерения

Если единица однозначна, она входит в имя поля:

```text
_m       метры
_m2      квадратные метры
_mm      миллиметры осадков
_c       градусы Celsius
_deg     градусы
_pct     проценты 0..100
_m_s     метры в секунду
_days    дни
```

Это уменьшает риск смешивания величин при feature extraction и scoring.

### `null` не равен нулю или `false`

Domain model сохраняет отсутствие данных явно.

Примеры:

```text
rain_24h_mm = 0.0
    известно, что за окно осадков не было

rain_24h_mm = null
    данных для окна нет

moss_present = false
    признак проверен и отсутствует

moss_present = null
    признак не записан / неизвестен

collecting_allowed = false
    подтверждён запрет

collecting_allowed = null
    юридический статус ещё не подтверждён
```

Неизвестное юридическое состояние нельзя автоматически считать разрешением.

### Время

`timestamp` и `last_updated` должны содержать timezone information.

### Geometry

`ForestSpot` и `Observation` используют минимальный GeoJSON-compatible 2D contract без зависимости domain-слоя от Shapely/GeoPandas.

Поддерживаются:

```text
Point
Polygon
MultiPolygon
```

Для Polygon/MultiPolygon domain проверяет базовую GeoJSON-структуру и замкнутость linear rings. Полная топологическая GIS-validation остаётся ответственностью будущего geospatial layer.

---

## Entity: EvidenceRecord

`EvidenceRecord` связывает экологическое утверждение с уровнем доказательности.

```yaml
field_name: string
level: confirmed_source | expert_heuristic | field_observation | working_hypothesis
source_id: string | null
note: string | null
```

Для `confirmed_source` поле `source_id` обязательно.

---

## Entity: SpeciesProfile

```yaml
species_id: string
latin_name: string
common_name: string
german_name: string
host_trees: [string]
preferred_soils: [string]
preferred_ph_min: number | null
preferred_ph_max: number | null
preferred_geologies: [string]
preferred_elevation_min_m: number | null
preferred_elevation_max_m: number | null
preferred_temperature_min_c: number | null
preferred_temperature_max_c: number | null
preferred_season_months: [integer]
rain_response_min_days: integer | null
rain_response_max_days: integer | null
positive_indicator_plants: [string]
negative_indicator_plants: [string]
habitat_notes: [string]
evidence: [EvidenceRecord]
```

Правила:

- paired ranges задаются либо целиком, либо не задаются;
- pH находится в диапазоне `0..14`;
- месяцы находятся в диапазоне `1..12` и не дублируются;
- текущий `boletus_edulis.json` является baseline fixture, а не научно подтверждённым species dataset;
- непроверенные экологические значения не должны автоматически получать `confirmed_source`.

---

## Entity: ForestSpot

```yaml
spot_id: string
name: string
geometry: GeoJSON-compatible geometry
region: string
country: string
elevation_min_m: number | null
elevation_max_m: number | null
dominant_aspect_deg: number | null
slope_deg: number | null
forest_type: string | null
tree_species: [string]
geology: string | null
soil_type: string | null
soil_ph: number | null
nutrient_level: string | null
canopy_density_pct: number | null
forest_age_class: string | null
disturbance_level: string | null
nearest_stream_m: number | null
protected_area: string | null
collecting_allowed: boolean | null
legal_notes: [string]
access_notes: [string]
static_data_confidence: number | null
last_updated: timezone-aware datetime | null
```

Правила:

- `elevation_min_m <= elevation_max_m`;
- `dominant_aspect_deg` находится в `[0, 360)`;
- `slope_deg` находится в `0..90`;
- `soil_ph` находится в `0..14`;
- percentage-поля находятся в `0..100`;
- `nearest_stream_m >= 0`;
- `collecting_allowed = null` означает **unknown**, а не разрешение;
- `ForestSpot` не хранит постоянный mushroom/opportunity score.

`ForestSpot` проектируется как участок/cell. Point geometry допустима для fixtures и ранних sample records, Polygon/MultiPolygon — для реальных пространственных участков.

---

## Entity: WeatherSnapshot

```yaml
spot_id: string
timestamp: timezone-aware datetime
source_id: string
rain_24h_mm: number | null
rain_3d_mm: number | null
rain_7d_mm: number | null
rain_14d_mm: number | null
rain_21d_mm: number | null
rain_28d_mm: number | null
rain_90d_mm: number | null
rain_anomaly_value: number | null
rain_anomaly_method: string | null
avg_temp_7d_c: number | null
avg_temp_14d_c: number | null
avg_temp_20d_c: number | null
min_temp_c: number | null
max_temp_c: number | null
humidity_pct: number | null
wind_speed_m_s: number | null
soil_moisture_value: number | null
soil_moisture_method: string | null
drought_index_value: number | null
drought_index_method: string | null
```

Правила:

- precipitation и wind speed не могут быть отрицательными;
- `humidity_pct` находится в `0..100`;
- если заданы обе температуры, `min_temp_c <= max_temp_c`;
- `rain_anomaly`, `soil_moisture` и `drought_index` задаются как пара `value + method`;
- method обязателен, потому что шкала этих показателей зависит от dataset/методики;
- собственный rainfall-based drought proxy нельзя выдавать за измеренную `soil_moisture`.

---

## Entity: Observation

```yaml
observation_id: string
timestamp: timezone-aware datetime
geometry: GeoJSON-compatible geometry
target_species_id: string
found_target_species: boolean
user_id: string | null
species_confidence_pct: number | null
count: integer | null
photo_ref: string | null
searched_minutes: number | null
searched_area_m2_estimate: number | null
elevation_m: number | null
aspect_deg: number | null
forest_type: string | null
dominant_trees: [string]
secondary_trees: [string]
moss_present: boolean | null
blueberry_present: boolean | null
heather_present: boolean | null
nettle_present: boolean | null
blackberry_present: boolean | null
grass_density_class: string | null
soil_surface_moisture_class: string | null
soil_moisture_5cm_class: string | null
canopy_density_pct: number | null
forest_maturity_class: string | null
disturbance_class: string | null
other_mushrooms_found: [string]
notes: [string]
```

Правила:

- positive и negative search используют одну сущность;
- `found_target_species=false` является полноценным наблюдением;
- для negative observation `count` может быть `0` или `null`, но не положительным;
- для positive observation `count=0` недопустим; `null` означает, что количество не записали;
- `species_confidence_pct` имеет смысл только при `found_target_species=true`;
- `searched_minutes` и `searched_area_m2_estimate` хранят search effort независимо от результата;
- точные реальные координаты пользовательских hotspot-ов не должны попадать в публичные fixtures.

---

## Planned entity: LegalZone

`LegalZone` остаётся отдельной planned entity. MR-1 её не реализует, потому что текущий milestone требует четыре основные domain entities.

Предварительный контракт:

```yaml
zone_id:
name:
type:
geometry:
collecting_allowed:
max_quantity_kg:
off_trail_allowed:
vehicle_access:
seasonal_rules:
source_id:
last_checked:
```

Юридические hard exclusions создаются только из подтверждённых правил и authoritative geometry.

---

## Planned entity: Source

```yaml
source_id:
name:
provider:
url:
license:
coverage:
resolution:
update_frequency:
access_method:
last_verified:
known_limitations:
```

Фактический registry и политика выбора источников ведутся в `DATA_SOURCE_SELECTION.md`.

---

## Serialization contract

Все четыре MR-1 entity имеют явные `to_dict()` / `from_dict()` и JSON fixtures.

`from_dict()` работает fail-fast: значения неправильного JSON-типа не должны молча преобразовываться в строки, целые числа или boolean.

Scoring structures (`SpotFeatures`, `ScoreResult`) намеренно не являются частью этого domain contract и остаются отдельным слоем.
