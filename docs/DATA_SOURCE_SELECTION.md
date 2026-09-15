# Data Source Selection — mushroom-racing

## Назначение

Этот документ фиксирует, **какие источники информации проект считает допустимыми и приоритетными**, а также какие источники планируется использовать для конкретных типов данных.

Документ не означает, что все перечисленные источники уже интегрированы.

Для каждого источника отдельно проверяются:

- лицензия;
- доступность для программной загрузки;
- пространственное и временное разрешение;
- географическое покрытие;
- стабильность доступа;
- ограничения и потенциальные ошибки.

Интеграция источника считается завершённой только после воспроизводимой проверки в соответствующем milestone.

---

# 1. Иерархия доверия к источникам

Проект использует следующую иерархию.

## Уровень A — официальный первичный источник

Предпочтительный вариант.

Примеры:

- GeoSphere Austria;
- BFW — Bundesforschungszentrum für Wald;
- федеральные и земельные Open Government Data порталы;
- официальные природоохранные органы;
- официальные тексты законов и постановлений.

Такие источники используются как основа для GIS, погоды, юридических ограничений и других объективных данных.

## Уровень B — научный источник

Используется прежде всего для экологических правил и модели вида.

Примеры:

- peer-reviewed статьи;
- монографии;
- научные базы данных;
- публикации университетов и исследовательских институтов.

Научный источник не заменяет GIS-данные, но может подтверждать, **почему конкретный признак должен участвовать в scoring**.

## Уровень C — экспертная эвристика

Допустима, если сильного источника пока нет.

Примеры:

- рекомендации опытных микологов;
- устойчивые полевые практики;
- собственные выводы из нескольких источников.

Такая информация должна быть явно помечена как:

```text
expert_heuristic
```

и не должна выглядеть как подтверждённый научный факт.

## Уровень D — собственное полевое наблюдение

Положительная или отрицательная проверка конкретного участка.

Пометка:

```text
field_observation
```

Наблюдение является реальным фактом поездки, но само по себе не доказывает универсальное экологическое правило.

## Уровень E — рабочая гипотеза

Используется только для исследования.

Пометка:

```text
working_hypothesis
```

Такая гипотеза не должна автоматически попадать в production scoring как подтверждённое правило.

---

# 2. Экология грибов и SpeciesProfile

## Основной принцип

Экологические свойства вида не должны выводиться из форумов, грибных карт или единичных находок.

Приоритет:

1. научные публикации;
2. профильные микологические базы и исследовательские институты;
3. официальные лесные/экологические публикации;
4. экспертные эвристики;
5. собственные наблюдения.

## Что нужно подтверждать источниками

Для `SpeciesProfile` важны:

- host trees / микоризные партнёры;
- почвенные предпочтения;
- связь с кислотностью и геологией;
- температурные условия;
- сезонность;
- высотные диапазоны;
- реакция на влажность и осадки;
- влияние структуры и возраста леса;
- растения-индикаторы.

## Решение на текущий момент

Конкретный набор научных источников для `Boletus edulis` **ещё не зафиксирован**.

Это отдельная исследовательская задача.

До её завершения существующие экологические правила считаются baseline knowledge и должны сохранять evidence level.

---

# 3. Лес и древесные породы

## Кандидат №1 — BFW / Österreichische Waldinventur

**Организация:** Bundesforschungszentrum für Wald (BFW)

Использование:

- forest cover;
- структура леса;
- древесные породы;
- Baumartenmischung;
- потенциально возраст/структура древостоя.

BFW сообщает, что Österreichische Waldinventur является долгосрочным мониторингом лесов Австрии, а современные remote-sensing методы позволяют создавать общенациональные тематические карты, включая Waldkarte и Baumartenmischungskarte.

### Статус

```text
primary candidate
```

### Что ещё нужно проверить

- конкретный downloadable/API layer;
- разрешение;
- формат;
- лицензия и право перераспространения;
- насколько карта Baumartenmischung подходит для feature extraction на уровне будущей ячейки/полигона.

### Решение

Для MR02 BFW является **первым источником, который исследуем для forest mask и tree species**.

---

# 4. Почва

## Кандидат №1 — BFW Bodenkarte Niederösterreich

Использование:

- soil type;
- лесные почвы;
- косвенные признаки кислотности;
- почвенные условия для habitat model.

BFW указывает, что новая Bodenkarte Niederösterreich объединяет информацию сельскохозяйственной почвенной съёмки с данными более чем 1000 профильных точек на лесной территории.

### Ограничение

Текущая карта имеет обзорный масштаб и не должна автоматически интерпретироваться как высокоточная характеристика конкретного небольшого участка леса.

### Статус

```text
primary candidate for regional soil context
```

---

## Вторичный источник — eBOD / bodenkarte.at

Использование возможно только там, где покрытие и назначение данных подходят.

### Важное ограничение

Основная детальная почвенная картография eBOD ориентирована прежде всего на сельскохозяйственные земли.

Поэтому eBOD **не используется как универсальная forest-soil карта**.

### Статус

```text
secondary / caution
```

---

# 5. Геология

## Выбранный основной источник — GeoSphere Austria

GeoSphere Austria предоставляет GIS-сервисы геологических единиц Австрии.

Особенно интересен harmonized layer геологических единиц масштаба примерно 1:50 000.

Доступны REST/WFS-сервисы и polygon features; для ряда слоёв явно указана лицензия:

```text
CC BY 4.0
```

### Использование

- representative lithology;
- silicate/carbonate proxy;
- bedrock class;
- geology confidence;
- habitat feature extraction.

### Статус

```text
selected primary source
```

### Почему

- официальный австрийский источник;
- хорошее покрытие;
- машинно-читаемый GIS;
- подходит для воспроизводимого pipeline;
- лицензия для выбранных слоёв ясна.

---

# 6. Высота, slope и aspect

## Выбранные источники

Authoritative source для высоты и производных terrain features — официальный Digitales Geländemodell (DGM).

- **Land Niederösterreich DGM 10 m** — основной authoritative dataset для стартовой зоны;
- **Geoland.at DGM Österreich 10 m** — nationwide fallback.

Для MR02 operational access реализован `AustrianElevationProvider`. Он используется как transport/access layer и **не заменяет authoritative source**.

## Текущий статус MR02

```text
authoritative DEM source: selected
operational provider: AustrianElevationProvider — validated for MR02 PoC
elevation validation: completed on 4-point sample
terrain feature extraction: implemented
slope/aspect extraction: unit validated + live smoke tested
independent authoritative slope/aspect validation: not yet performed
local cache: implemented and live validated
```

Elevation provider проверен против `NÖ Atlas → Koordinaten / Höhe → Gelände` на четырёх контрольных точках. Максимальная absolute error в этой небольшой validation sample составила `2.80 m`; принятый критерий MR02 PoC — `<= 5 m` на выбранной sample.

Terrain feature extraction реализован поверх `ElevationWindow`:

```text
ElevationWindow
        ↓
central 3x3 neighborhood
        ↓
Horn gradient
        ↓
TerrainFeatures
    elevation_m
    slope_deg
    aspect_deg
```

Для окон `EPSG:3857` projected pixel resolution переводится в приблизительное ground distance через локальный scale factor Web Mercator. Для `EPSG:31259` resolution используется как метрическая напрямую. Неизвестный CRS обрабатывается fail-fast.

Live smoke test на точке `47.7200, 15.9000`:

```text
elevation: 1212.0 m
slope: 13.23°
aspect: 341.57°  # NNW
```

Расчёт slope/aspect подтверждён unit tests на синтетических DEM и live smoke test на реальном remote window. Это **не является независимой authoritative validation slope/aspect**.

Полная документация по DEM, operational provider, ограничениям, validation sample и terrain feature extraction вынесена в:

```text
docs/data_sources/DEM.md
```

### Решение

Полный GeoTIFF не является обязательной runtime dependency проекта. Обычный pipeline использует небольшие remote windows через `ElevationProvider` и persistent local cache через `CachedElevationProvider`.

Cache хранит нормализованные `ElevationWindow` в `.npz`, использует явный namespace для invalidation и атомарную запись через temporary file + `os.replace`. Повреждённый cache обрабатывается fail-fast.

MR-2.4 проверен unit tests и live persistent-cache smoke test: окно, записанное первым процессом через реальный remote provider, успешно прочитано вторым процессом без вызова wrapped remote provider.

---

# 7. Погода

## Выбранный основной источник — GeoSphere Austria Data Hub

GeoSphere Austria предоставляет Dataset API с режимами:

- historical;
- current;
- forecast.

Поддерживаются:

- station data;
- grid data;
- timeseries по координате.

Публично доступные без аутентификации данные Data Hub лицензируются как:

```text
CC BY 4.0
```

### Основные наборы для исследования

#### Station Data v2

Подходит для:

- precipitation;
- temperature;
- humidity;
- wind;
- исторических проверок и сравнения с grid data.

#### INCA

Высокодетализированная метеорологическая analysis/nowcasting система.

Потенциально подходит для текущего состояния конкретной территории лучше, чем одна метеостанция.

#### SPARTACUS daily

Gridded daily climate data примерно 1 km.

Подходит для:

- исторических осадков;
- температуры;
- rainfall history;
- климатического контекста.

### Статус

```text
selected primary source
```

### Предварительное решение по pipeline

Для MR03 исследовать комбинацию:

```text
historical context -> SPARTACUS / quality-checked station data
current conditions -> INCA / current station data
```

Окончательный выбор dataset/resource_id фиксируется только после proof of concept.

---

# 8. Drought / moisture context

## Текущий статус

Источник пока **не выбран окончательно**.

Кандидаты:

- производные показатели из GeoSphere rainfall history;
- anomaly datasets GeoSphere;
- доступные soil-moisture / drought products, если их пространственное разрешение подходит.

### Важное решение

В первой версии допустимо вычислять собственный простой drought proxy из истории осадков, если это будет явно документированная rule-based feature.

Нельзя называть такой proxy реальным `soil_moisture`, если он им не является.

### Статус

```text
research required
```

---

# 9. Protected areas и legal layer

## Основной принцип

Юридическая информация требует особенно строгого выбора источников.

Используются только:

- официальные GIS/OGD данные;
- официальные страницы природоохранных органов;
- официальные нормативные тексты.

Сторонние туристические карты могут использоваться для навигационной проверки, но не как source of truth для hard exclusion.

## Biosphärenpark Wienerwald

Официальный Biosphärenpark Wienerwald предоставляет карту Kernzonen и информацию о зональном устройстве.

### Использование

- geometry Kernzonen;
- protected-area context;
- проверка hard exclusions.

### Статус

```text
primary candidate
```

### Что ещё нужно проверить

- есть ли официальный downloadable GIS/WFS/API;
- лицензия геометрий;
- как связать geometry с юридическим правилом;
- какие ограничения действуют только для отдельных зон.

### Важное правило проекта

Сам факт попадания полигона в protected area **не означает автоматически**, что сбор запрещён.

Hard exclusion создаётся только при наличии подтверждённого юридического правила.

---

# 10. Hydrology

## Текущий статус

Источник ещё не выбран.

Нужны:

- streams;
- springs;
- drainage;
- distance-to-water features.

Приоритет будет отдаваться:

1. официальным австрийским OGD/GIS;
2. только затем OpenStreetMap как fallback для отдельных объектов.

```text
status: research required
```

---

# 11. Roads, trails и access

Для доступа потребуется отдельное сочетание источников.

Возможные данные:

- дороги;
- hiking trails;
- parking;
- public transport;
- forest road restrictions.

## Предварительное решение

OpenStreetMap может быть полезным operational source для дорог, троп и парковок, но **не является достаточным источником юридического права проезда или доступа**.

```text
status: later research
priority: P2
```

---

# 12. Field observations

## Источник

Собственная база mushroom-racing.

Сохраняются:

- positive observations;
- negative searched observations;
- environmental notes;
- timestamp;
- geometry;
- search effort.

### Evidence type

```text
field_observation
```

### Приватность

Точные координаты успешных мест считаются приватными пользовательскими данными и не должны попадать в публичные fixtures или showcase datasets.

---

# 13. Источники, которые нельзя использовать как primary source

Следующие типы источников могут помогать исследованию, но не должны напрямую определять production model без подтверждения:

- форумы;
- Reddit;
- Facebook-группы;
- грибные Telegram/WhatsApp-чаты;
- случайные блоги;
- YouTube-видео;
- коммерческие карты грибных мест;
- единичные anecdotal reports;
- AI-generated summaries без первичного источника.

Они могут использоваться для **формирования гипотез**, после чего гипотеза проверяется более сильным источником или полевыми данными.

---

# 14. Выбранный минимальный стек источников для MVP

На текущем этапе целевой набор выглядит так:

| Layer | Primary source | Status |
|---|---|---|
| Species ecology | scientific literature / specialist sources | research required |
| Forest mask | BFW | candidate |
| Tree species | BFW | candidate |
| Forest soil | BFW | candidate |
| Geology | GeoSphere Austria 1:50k GIS | selected |
| DEM | Land Niederösterreich DGM 10 m / Geoland.at | authoritative selected; provider + terrain + persistent cache PoC validated |
| Weather history | GeoSphere Data Hub | selected |
| Current weather | GeoSphere INCA / station data | selected for PoC |
| Drought | GeoSphere-derived / own documented proxy | research required |
| Protected areas | official Austrian GIS + BPWW | candidate |
| Legal rules | official legal / authority sources | mandatory |
| Hydrology | official OGD/GIS | research required |
| Roads/trails | official data + OSM fallback | later |
| Observations | mushroom-racing database | planned |
| Presentation basemap | basemap.at | selected for MR-6 |

---

# 14A. Presentation basemap

## Выбранный источник — basemap.at

Для пользовательской web-карты выбран **basemap.at** как default presentation basemap.

Роль этого источника принципиально отделена от analytical data sources:

```text
authoritative analytical sources
        ↓
feature extraction / scoring
        ↓
mushroom-racing overlays
        ↓
MapLibre GL JS
        ↓
basemap.at as presentation background
```

### Почему выбран basemap.at

- официальный австрийский картографический продукт;
- покрытие всей территории Австрии;
- free-first совместимость;
- лицензия CC BY 4.0;
- подходит для отображения собственных GIS overlays;
- позволяет не создавать и не обслуживать собственную базовую карту.

### Ограничение роли

Данные basemap.at не используются для вычисления:

- habitat score;
- current conditions score;
- opportunity score;
- legal eligibility;
- confidence.

Если визуально доступный объект basemap.at нужен как analytical feature, для него отдельно выбирается и валидируется соответствующий primary source.

### Attribution

Публичный frontend обязан отображать корректную атрибуцию basemap.at, например:

```text
Grundkarte: basemap.at
```

с ссылкой на `https://basemap.at/`.

### Access strategy

На момент фиксации решения basemap.at находится в переходе к новой vector-tile инфраструктуре. Поэтому:

- `basemap.at` фиксируется как выбранный presentation provider;
- конкретный endpoint не фиксируется до MR-6;
- перед frontend integration повторно проверяются production status, MapLibre integration path, license/attribution и технические ограничения;
- scoring/backend не должны зависеть от доступности basemap service.

### Статус

```text
selected for presentation
integration: deferred to MR-6
```

---

# 15. Приоритет исследования

## P0 — подтвердить до первого GIS prototype

1. DEM access + terrain feature + persistent cache PoC — **completed through MR-2.4**.
2. GeoSphere geology query/download.
3. GeoSphere weather API.
4. Forest-mask source BFW.
5. Protected-area geometry + licensing.

## P1 — подтвердить до meaningful Steinpilz scoring

1. BFW tree-species layer.
2. forest-soil source.
3. scientific evidence set для `Boletus edulis`.
4. drought-context source или формально определённый proxy.

## P2 — usability и calibration

1. hydrology;
2. roads/trails/parking;
3. canopy / disturbance;
4. user observations.

---

# 16. Definition of Done для выбора источника

Источник может получить статус `selected` для production integration только если зафиксированы:

```yaml
source_id:
name:
provider:
url:
layer_type:
license:
coverage:
resolution:
update_frequency:
access_method:
api_or_download:
last_verified:
known_limitations:
```

Дополнительно должна существовать воспроизводимая проверка:

- API request;
- download procedure;
- либо documented manual import.

Если одно из критических свойств неизвестно, источник остаётся `candidate` или `research required`.

---

# 17. Следующий конкретный шаг

DEM operational access, elevation validation, terrain feature extraction и persistent local cache завершены для текущего MR02 PoC.

Завершённая DEM-цепочка:

```text
WGS84 coordinate
        ↓
AustrianElevationProvider
        ↓
CachedElevationProvider
        ↓
ElevationWindow
        ↓
TerrainFeatures
    elevation / slope / aspect
```

Проверки:

```text
elevation validation: 4 control points against NÖ Atlas
terrain extraction: synthetic DEM unit tests + live smoke test
persistent cache: cross-process live cache hit
full repository suite: 84 passed
```

Следующий P0-блок:

```text
GeoSphere geology query / download PoC
```

После geology:

```text
1. GeoSphere weather
2. BFW forest mask
3. protected areas
```
