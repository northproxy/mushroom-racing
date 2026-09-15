# Data Source Selection --- mushroom-racing

## Назначение

Этот документ фиксирует, **какие источники информации проект считает
допустимыми и приоритетными**, а также какие источники планируется
использовать для конкретных типов данных.

Документ не означает, что все перечисленные источники уже интегрированы.

Для каждого источника отдельно проверяются:

-   лицензия;
-   доступность для программной загрузки;
-   пространственное и временное разрешение;
-   географическое покрытие;
-   стабильность доступа;
-   ограничения и потенциальные ошибки.

Интеграция источника считается завершённой только после воспроизводимой
проверки в соответствующем milestone.

------------------------------------------------------------------------

# 1. Иерархия доверия к источникам

Проект использует следующую иерархию.

## Уровень A --- официальный первичный источник

Предпочтительный вариант.

Примеры:

-   GeoSphere Austria;
-   BFW --- Bundesforschungszentrum für Wald;
-   федеральные и земельные Open Government Data порталы;
-   официальные природоохранные органы;
-   официальные тексты законов и постановлений.

Такие источники используются как основа для GIS, погоды, юридических
ограничений и других объективных данных.

## Уровень B --- научный источник

Используется прежде всего для экологических правил и модели вида.

Примеры:

-   peer-reviewed статьи;
-   монографии;
-   научные базы данных;
-   публикации университетов и исследовательских институтов.

Научный источник не заменяет GIS-данные, но может подтверждать, **почему
конкретный признак должен участвовать в scoring**.

## Уровень C --- экспертная эвристика

Допустима, если сильного источника пока нет.

Примеры:

-   рекомендации опытных микологов;
-   устойчивые полевые практики;
-   собственные выводы из нескольких источников.

Такая информация должна быть явно помечена как:

``` text
expert_heuristic
```

и не должна выглядеть как подтверждённый научный факт.

## Уровень D --- собственное полевое наблюдение

Положительная или отрицательная проверка конкретного участка.

Пометка:

``` text
field_observation
```

Наблюдение является реальным фактом поездки, но само по себе не
доказывает универсальное экологическое правило.

## Уровень E --- рабочая гипотеза

Используется только для исследования.

Пометка:

``` text
working_hypothesis
```

Такая гипотеза не должна автоматически попадать в production scoring как
подтверждённое правило.

------------------------------------------------------------------------

# 2. Экология грибов и SpeciesProfile

## Основной принцип

Экологические свойства вида не должны выводиться из форумов, грибных
карт или единичных находок.

Приоритет:

1.  научные публикации;
2.  профильные микологические базы и исследовательские институты;
3.  официальные лесные/экологические публикации;
4.  экспертные эвристики;
5.  собственные наблюдения.

## Что нужно подтверждать источниками

Для `SpeciesProfile` важны:

-   host trees / микоризные партнёры;
-   почвенные предпочтения;
-   связь с кислотностью и геологией;
-   температурные условия;
-   сезонность;
-   высотные диапазоны;
-   реакция на влажность и осадки;
-   влияние структуры и возраста леса;
-   растения-индикаторы.

## Решение на текущий момент

Конкретный набор научных источников для `Boletus edulis` **ещё не
зафиксирован**.

Это отдельная исследовательская задача.

До её завершения существующие экологические правила считаются baseline
knowledge и должны сохранять evidence level.

------------------------------------------------------------------------

# 3. Лес и древесные породы

## Выбранный forest-mask source --- Waldkarte BFW Österreich

**Организация:** Bundesforschungszentrum für Wald (BFW)

Использование:

-   forest / non-forest mask;
-   source-level подтверждение forestry land use;
-   будущая фильтрация candidate cells.

Для tree species BFW остаётся отдельным кандидатом; MR-2.6 валидирует
именно forest mask.

### Статус

``` text
selected primary source for forest mask
MR-2.6 operational point-query PoC: completed
production provider: AustrianForestProvider
```

### Проверенный access path

``` text
WGS84 coordinate
        ↓
AustrianForestProvider
        ↓
BFW Waldkarte WFS 2.0
        ↓
FES Intersects(gml:Point, geometry)
        ↓
ForestResult
        ↓
FOREST / NON_FOREST / UNKNOWN
```

Успешный ответ без `wfs:member` означает `NON_FOREST`; forestry feature
означает `FOREST`; корректный, но непонятный source result ---
`UNKNOWN`. Transport / HTTP / malformed XML errors обрабатываются
fail-fast через `ForestProviderError`.

Live WFS показал, что `numberReturned="0"` может присутствовать при
реальном `wfs:member`, поэтому provider считает фактические members.

Контрольные live queries:

``` text
47.7200000, 15.9000000 -> FOREST
47.8520556, 16.7713333 -> NON_FOREST
```

Лицензия выбранного dataset: CC BY 4.0. Waldkarte не является
legal/access layer и не используется для вывода о праве доступа или
сбора грибов.

Подробности:

``` text
docs/data_sources/FOREST.md
```

### Tree species

BFW / Österreichische Waldinventur / remote-sensing products остаются
primary candidate для будущего tree-species layer.

``` text
status: candidate / research
```

------------------------------------------------------------------------

# 4. Почва

## Кандидат №1 --- BFW Bodenkarte Niederösterreich

Использование:

-   soil type;
-   лесные почвы;
-   косвенные признаки кислотности;
-   почвенные условия для habitat model.

BFW указывает, что новая Bodenkarte Niederösterreich объединяет
информацию сельскохозяйственной почвенной съёмки с данными более чем
1000 профильных точек на лесной территории.

### Ограничение

Текущая карта имеет обзорный масштаб и не должна автоматически
интерпретироваться как высокоточная характеристика конкретного
небольшого участка леса.

### Статус

``` text
primary candidate for regional soil context
```

------------------------------------------------------------------------

## Вторичный источник --- eBOD / bodenkarte.at

Использование возможно только там, где покрытие и назначение данных
подходят.

### Важное ограничение

Основная детальная почвенная картография eBOD ориентирована прежде всего
на сельскохозяйственные земли.

Поэтому eBOD **не используется как универсальная forest-soil карта**.

### Статус

``` text
secondary / caution
```

------------------------------------------------------------------------

# 5. Геология

## Выбранный основной источник --- GeoSphere Austria

GeoSphere Austria предоставляет GIS-сервисы геологических единиц
Австрии.

Особенно интересен harmonized layer геологических единиц масштаба
примерно 1:50 000.

Доступны REST/WFS-сервисы и polygon features; для ряда слоёв явно
указана лицензия:

``` text
CC BY 4.0
```

### Использование

-   representative lithology;
-   silicate/carbonate proxy;
-   bedrock class;
-   geology confidence;
-   habitat feature extraction.

### Статус

``` text
selected primary source
MR-2.5 operational point-query PoC: completed
production provider: AustrianGeologyProvider
```

### Проверенный MR-2.5 access path

``` text
WGS84 coordinate
        ↓
AustrianGeologyProvider
        ↓
GeoSphere GE.GeologicUnit_50k / ArcGIS REST
        ↓
GeologyQueryResult
        ↓
0..N GeologyRecord
```

Validation sample из 7 точек подтвердил machine-readable source fields.
Spatial edge cases подтвердили `0`, `1` и несколько intersecting
features. Provider сохраняет все records и не выбирает автоматически
"главную" geological unit.

Production live smoke на `47.7200, 15.9000` вернул
`Gutenstein Formation`, `material=limestone`,
`representativeLithology=limestone`.

Silicate/carbonate classification, acidity proxy и geology contribution
to habitat score намеренно отложены до отдельной
interpretation/specification задачи.

Подробности:

``` text
docs/data_sources/GEOLOGY.md
```

### Почему

-   официальный австрийский источник;
-   хорошее покрытие;
-   машинно-читаемый GIS;
-   подходит для воспроизводимого pipeline;
-   лицензия для выбранных слоёв ясна.

------------------------------------------------------------------------

# 6. Высота, slope и aspect

## Выбранные источники

Authoritative source для высоты и производных terrain features ---
официальный Digitales Geländemodell (DGM).

-   **Land Niederösterreich DGM 10 m** --- основной authoritative
    dataset для стартовой зоны;
-   **Geoland.at DGM Österreich 10 m** --- nationwide fallback.

Для MR02 operational access реализован `AustrianElevationProvider`. Он
используется как transport/access layer и **не заменяет authoritative
source**.

## Текущий статус MR02

``` text
authoritative DEM source: selected
operational provider: AustrianElevationProvider — validated for MR02 PoC
elevation validation: completed on 4-point sample
terrain feature extraction: implemented
slope/aspect extraction: unit validated + live smoke tested
independent authoritative slope/aspect validation: not yet performed
local cache: implemented and live validated
```

Elevation provider проверен против
`NÖ Atlas → Koordinaten / Höhe → Gelände` на четырёх контрольных точках.
Максимальная absolute error в этой небольшой validation sample составила
`2.80 m`; принятый критерий MR02 PoC --- `<= 5 m` на выбранной sample.

Terrain feature extraction реализован поверх `ElevationWindow`:

``` text
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

Для окон `EPSG:3857` projected pixel resolution переводится в
приблизительное ground distance через локальный scale factor Web
Mercator. Для `EPSG:31259` resolution используется как метрическая
напрямую. Неизвестный CRS обрабатывается fail-fast.

Live smoke test на точке `47.7200, 15.9000`:

``` text
elevation: 1212.0 m
slope: 13.23°
aspect: 341.57°  # NNW
```

Расчёт slope/aspect подтверждён unit tests на синтетических DEM и live
smoke test на реальном remote window. Это **не является независимой
authoritative validation slope/aspect**.

Полная документация по DEM, operational provider, ограничениям,
validation sample и terrain feature extraction вынесена в:

``` text
docs/data_sources/DEM.md
```

### Решение

Полный GeoTIFF не является обязательной runtime dependency проекта.
Обычный pipeline использует небольшие remote windows через
`ElevationProvider` и persistent local cache через
`CachedElevationProvider`.

Cache хранит нормализованные `ElevationWindow` в `.npz`, использует
явный namespace для invalidation и атомарную запись через temporary
file + `os.replace`. Повреждённый cache обрабатывается fail-fast.

MR-2.4 проверен unit tests и live persistent-cache smoke test: окно,
записанное первым процессом через реальный remote provider, успешно
прочитано вторым процессом без вызова wrapped remote provider.

------------------------------------------------------------------------

# 7. Погода

## Выбранный основной источник --- GeoSphere Austria SPARTACUS v3

**Provider:** GeoSphere Austria  
**Dataset:** `spartacus-v3-1d-1km`  
**Тип:** gridded daily climate data  
**Spatial resolution:** примерно 1 km  
**Temporal resolution:** 1 day  
**Access:** GeoSphere Dataset API, `timeseries/historical` point-query  
**License:** CC BY 4.0

### Использование

Текущий production weather pipeline использует SPARTACUS v3 для:

-   daily precipitation;
-   daily mean temperature;
-   daily minimum temperature;
-   daily maximum temperature;
-   rolling rainfall history;
-   rolling mean-temperature windows;
-   построения domain `WeatherSnapshot`.

Проверенные source parameters:

``` text
RR    daily precipitation sum       kg m-2
TM24  daily mean air temperature    degC
TN    daily minimum air temperature degC
TX    daily maximum air temperature degC
```

Для воды `1 kg m-2` численно эквивалентен `1 mm`, поэтому provider
нормализует `RR` в `precipitation_mm` без изменения численного значения.

### Статус

``` text
selected primary source
MR-2 weather PoC: completed
production provider: AustrianWeatherProvider
weather feature extraction: implemented
WeatherSnapshot assembly: implemented
```

### Проверенный operational path

``` text
WGS84 coordinate
        ↓
AustrianWeatherProvider
        ↓
GeoSphere SPARTACUS v3 timeseries API
        ↓
WeatherSeries / DailyWeather
        ↓
weather feature extraction
        ↓
WeatherSnapshot
```

Provider сохраняет отдельно:

``` text
requested coordinate
source grid coordinate
```

поскольку GeoSphere возвращает ближайшую grid-point, которая может
немного отличаться от запрошенной координаты.

### Missing-data semantics

Live PoC подтвердил важное поведение API:

``` text
HTTP 200
```

не гарантирует наличие weather data.

Для точки вне эффективного покрытия API может вернуть одну grid-point,
но все значения параметров будут:

``` json
null
```

Поэтому:

``` text
0.0  !=  None
```

`0.0` означает известное нулевое значение, например отсутствие осадков.

`None` означает, что данных нет.

`WeatherAvailability` различает:

``` text
AVAILABLE
PARTIAL
NO_DATA
```

Полностью пустой, но структурно корректный ответ не является transport
error и нормализуется как `NO_DATA`.

### Fail-fast

`WeatherProviderError` используется для operational/source contract
errors, например:

-   network / timeout;
-   HTTP error;
-   malformed JSON;
-   неожиданная структура payload;
-   отсутствующий обязательный parameter;
-   несоответствие длины timestamps и parameter arrays;
-   неожиданная unit;
-   невозможная source geometry;
-   non-numeric / non-finite values.

Missing weather value (`null`) сам по себе ошибкой не является.

### Rolling features

Реализованы deterministic calendar windows:

``` text
rain_24h_mm
rain_3d_mm
rain_7d_mm
rain_14d_mm
rain_21d_mm
rain_28d_mm

avg_temp_7d_c
avg_temp_14d_c
avg_temp_20d_c
```

Окна inclusive по `as_of_date`.

Пример:

``` text
7d = as_of_date + 6 предыдущих календарных дней
```

Используется strict completeness policy:

-   отсутствующий календарный день делает соответствующий derived feature
    `None`;
-   `None` внутри precipitation window делает только rainfall feature
    `None`;
-   `None` внутри mean-temperature window делает только temperature
    feature `None`;
-   известный `0.0` участвует в расчёте как нормальное значение.

### Live validation

Основная контрольная точка:

``` text
47.7200, 15.9000
```

GeoSphere source grid:

``` text
47.718814849853516, 15.900300979614258
```

Проверены:

-   mountain control point --- valid data;
-   Vienna control point --- valid data;
-   Munich outside-effective-coverage case --- HTTP 200 + all `null`;
-   historical January 1961 --- valid historical data without missing values.

End-to-end smoke для `2026-09-12`:

``` text
rain_24h_mm   ≈ 0.1
rain_3d_mm    ≈ 28.3
rain_7d_mm    ≈ 34.5
rain_14d_mm   ≈ 53.9
rain_21d_mm   ≈ 58.0
rain_28d_mm   ≈ 95.9

avg_temp_7d_c  ≈ 14.04
avg_temp_14d_c ≈ 15.20
avg_temp_20d_c ≈ 15.68
```

Полный repository test suite после weather pipeline:

``` text
188 passed in 0.35s
```

### Ограничения

SPARTACUS v3 сейчас используется как основной daily weather history
source.

Пока не реализованы:

-   `rain_90d_mm`;
-   rainfall anomaly;
-   humidity;
-   wind;
-   soil moisture;
-   drought index;
-   INCA/current-hourly integration.

Эти поля остаются `None`, а не заменяются искусственными значениями.

Последние дни SPARTACUS могут пересчитываться GeoSphere после
quality-control исходных station observations, поэтому недавние данные
не следует считать immutable.

Подробности:

``` text
docs/data_sources/WEATHER.md
```

------------------------------------------------------------------------

# 8. Drought / moisture context

## Текущий статус

Источник пока **не выбран окончательно**.

Кандидаты:

-   производные показатели из GeoSphere rainfall history;
-   anomaly datasets GeoSphere;
-   доступные soil-moisture / drought products, если их пространственное
    разрешение подходит.

### Важное решение

В первой версии допустимо вычислять собственный простой drought proxy из
истории осадков, если это будет явно документированная rule-based
feature.

Нельзя называть такой proxy реальным `soil_moisture`, если он им не
является.

### Статус

``` text
research required
```

------------------------------------------------------------------------

# 9. Protected areas и legal layer

## Основной принцип

Юридическая информация требует особенно строгого выбора источников.

Используются только:

-   официальные GIS/OGD данные;
-   официальные страницы природоохранных органов;
-   официальные нормативные тексты.

Сторонние туристические карты могут использоваться для навигационной
проверки, но не как source of truth для hard exclusion.

## Biosphärenpark Wienerwald

Официальный Biosphärenpark Wienerwald предоставляет карту Kernzonen и
информацию о зональном устройстве.

### Использование

-   geometry Kernzonen;
-   protected-area context;
-   проверка hard exclusions.

### Статус

``` text
primary candidate
```

### Что ещё нужно проверить

-   есть ли официальный downloadable GIS/WFS/API;
-   лицензия геометрий;
-   как связать geometry с юридическим правилом;
-   какие ограничения действуют только для отдельных зон.

### Важное правило проекта

Сам факт попадания полигона в protected area **не означает
автоматически**, что сбор запрещён.

Hard exclusion создаётся только при наличии подтверждённого юридического
правила.

------------------------------------------------------------------------

# 10. Hydrology

## Текущий статус

Источник ещё не выбран.

Нужны:

-   streams;
-   springs;
-   drainage;
-   distance-to-water features.

Приоритет будет отдаваться:

1.  официальным австрийским OGD/GIS;
2.  только затем OpenStreetMap как fallback для отдельных объектов.

``` text
status: research required
```

------------------------------------------------------------------------

# 11. Roads, trails и access

Для доступа потребуется отдельное сочетание источников.

Возможные данные:

-   дороги;
-   hiking trails;
-   parking;
-   public transport;
-   forest road restrictions.

## Предварительное решение

OpenStreetMap может быть полезным operational source для дорог, троп и
парковок, но **не является достаточным источником юридического права
проезда или доступа**.

``` text
status: later research
priority: P2
```

------------------------------------------------------------------------

# 12. Field observations

## Источник

Собственная база mushroom-racing.

Сохраняются:

-   positive observations;
-   negative searched observations;
-   environmental notes;
-   timestamp;
-   geometry;
-   search effort.

### Evidence type

``` text
field_observation
```

### Приватность

Точные координаты успешных мест считаются приватными пользовательскими
данными и не должны попадать в публичные fixtures или showcase datasets.

------------------------------------------------------------------------

# 13. Источники, которые нельзя использовать как primary source

Следующие типы источников могут помогать исследованию, но не должны
напрямую определять production model без подтверждения:

-   форумы;
-   Reddit;
-   Facebook-группы;
-   грибные Telegram/WhatsApp-чаты;
-   случайные блоги;
-   YouTube-видео;
-   коммерческие карты грибных мест;
-   единичные anecdotal reports;
-   AI-generated summaries без первичного источника.

Они могут использоваться для **формирования гипотез**, после чего
гипотеза проверяется более сильным источником или полевыми данными.

------------------------------------------------------------------------

# 14. Выбранный минимальный стек источников для MVP

На текущем этапе целевой набор выглядит так:

  -----------------------------------------------------------------------
  Layer                   Primary source          Status
  ----------------------- ----------------------- -----------------------
  Species ecology         scientific literature / research required
                          specialist sources      

  Forest mask             BFW Waldkarte           selected; MR-2.6

  Tree species            BFW                     candidate

  Forest soil             BFW                     candidate

  Geology                 GeoSphere Austria       selected; MR-2.5
                          `GE.GeologicUnit_50k`   provider + point-query
                                                  PoC validated

  DEM                     Land Niederösterreich   authoritative selected;
                          DGM 10 m / Geoland.at   provider + terrain +
                                                  persistent cache PoC
                                                  validated

  Weather history         GeoSphere SPARTACUS v3  selected; provider +
                          daily 1 km grid         rolling features +
                                                  WeatherSnapshot
                                                  validated

  Current weather         GeoSphere INCA /        later research
                          station data            

  Drought                 GeoSphere-derived / own research required
                          documented proxy        

  Protected areas         official Austrian GIS + candidate
                          BPWW                    

  Legal rules             official legal /        mandatory
                          authority sources       

  Hydrology               official OGD/GIS        research required

  Roads/trails            official data + OSM     later
                          fallback                

  Observations            mushroom-racing         planned
                          database                

  Presentation basemap    basemap.at              selected for MR-6
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 14A. Presentation basemap

## Выбранный источник --- basemap.at

Для пользовательской web-карты выбран **basemap.at** как default
presentation basemap.

Роль этого источника принципиально отделена от analytical data sources:

``` text
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

-   официальный австрийский картографический продукт;
-   покрытие всей территории Австрии;
-   free-first совместимость;
-   лицензия CC BY 4.0;
-   подходит для отображения собственных GIS overlays;
-   позволяет не создавать и не обслуживать собственную базовую карту.

### Ограничение роли

Данные basemap.at не используются для вычисления:

-   habitat score;
-   current conditions score;
-   opportunity score;
-   legal eligibility;
-   confidence.

Если визуально доступный объект basemap.at нужен как analytical feature,
для него отдельно выбирается и валидируется соответствующий primary
source.

### Attribution

Публичный frontend обязан отображать корректную атрибуцию basemap.at,
например:

``` text
Grundkarte: basemap.at
```

с ссылкой на `https://basemap.at/`.

### Access strategy

На момент фиксации решения basemap.at находится в переходе к новой
vector-tile инфраструктуре. Поэтому:

-   `basemap.at` фиксируется как выбранный presentation provider;
-   конкретный endpoint не фиксируется до MR-6;
-   перед frontend integration повторно проверяются production status,
    MapLibre integration path, license/attribution и технические
    ограничения;
-   scoring/backend не должны зависеть от доступности basemap service.

### Статус

``` text
selected for presentation
integration: deferred to MR-6
```

------------------------------------------------------------------------

# 15. Приоритет исследования

## P0 --- подтвердить до первого GIS prototype

1.  DEM access + terrain feature + persistent cache PoC --- **completed
    through MR-2.4**.
2.  GeoSphere geology point-query PoC --- **completed through MR-2.5**.
3.  BFW forest-mask source PoC --- **completed through MR-2.6**.
4.  GeoSphere SPARTACUS weather API + provider + rolling features ---
    **completed**.
5.  Protected-area geometry + licensing --- **deferred until the core
    application workflow is operational**.

## P1 --- подтвердить до meaningful Steinpilz scoring

1.  BFW tree-species layer.
2.  forest-soil source.
3.  scientific evidence set для `Boletus edulis`.
4.  drought-context source или формально определённый proxy.

## P2 --- usability и calibration

1.  hydrology;
2.  roads/trails/parking;
3.  canopy / disturbance;
4.  user observations.

------------------------------------------------------------------------

# 16. Definition of Done для выбора источника

Источник может получить статус `selected` для production integration
только если зафиксированы:

``` yaml
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

-   API request;
-   download procedure;
-   либо documented manual import.

Если одно из критических свойств неизвестно, источник остаётся
`candidate` или `research required`.

------------------------------------------------------------------------

# 17. Текущее состояние MR-2 и следующий шаг

Для текущего MR-2 завершены operational PoC для:

``` text
DEM / terrain
geology
forest mask
weather
```

Weather pipeline:

``` text
WGS84 coordinate
        ↓
AustrianWeatherProvider
        ↓
GeoSphere SPARTACUS v3
        ↓
WeatherSeries / DailyWeather
        ↓
WeatherFeatures
        ↓
WeatherSnapshot
```

Проверки weather block:

``` text
live source access: PASS
multiple Austrian grid cells: PASS
outside-effective-coverage null semantics: PASS
historical 1961 data: PASS
rolling feature extraction: PASS
WeatherSnapshot assembly: PASS
full repository suite: 188 passed in 0.35s
end-to-end live smoke: PASS
```

Protected-area geometry + automated legal-rule resolution сознательно
отложены.

До возвращения к legal automation действует правило:

``` text
legal status = unknown unless manually confirmed
```

Protected-area membership не становится hard filter автоматически.

Следующий инженерный этап:

``` text
MR-3 — geospatial feature extraction / unified feature assembly
```
