# 02 --- Data Sources

## Назначение

Этот документ является кратким registry внешних data layers проекта.

Подробная политика доверия, выбранные primary sources, лицензии, access
strategy и текущий статус исследования фиксируются в:

``` text
DATA_SOURCE_SELECTION.md
```

Если между этим registry и `DATA_SOURCE_SELECTION.md` возникает
расхождение, для выбора/статуса источника приоритет имеет
`DATA_SOURCE_SELECTION.md`.

Источник не считается production-integrated, пока:

1.  понятны условия доступа и лицензия;
2.  известно spatial/temporal resolution;
3.  известна update frequency;
4.  существует воспроизводимый API/download/import workflow;
5.  ограничения источника документированы.

## Source registry

  ------------------------------------------------------------------------
  Layer           Primary candidate /     Needed fields    Status
                  selected source                          
  --------------- ----------------------- ---------------- ---------------
  Forest cover    BFW Waldkarte           forest /         selected
                                          non-forest mask  primary source;
                                                           MR-2.6
                                                           provider +
                                                           point
                                                           Intersects
                                                           validated

  Tree species    BFW / Waldinventur /    Fichte, Buche,   candidate /
                  remote-sensing products Tanne, Eiche,    research
                                          Kiefer, mix      

  Forest soil     BFW Bodenkarte          soil type, pH    candidate /
                  Niederösterreich        proxies, humus,  research
                                          moisture context 

  General soil    eBOD / bodenkarte.at    soil properties  secondary /
                                          where applicable caution

  Geology         GeoSphere Austria       raw geological   selected
                  `GE.GeologicUnit_50k`   unit, material,  primary source;
                                          representative   MR-2.5
                                          lithology        provider +
                                                           point-query PoC
                                                           validated

  DEM             Land NÖ DGM 10 m;       elevation,       authoritative
                  Geoland.at nationwide   slope, aspect    selected;
                  fallback                                 provider +
                                                           terrain +
                                                           persistent
                                                           cache PoC
                                                           validated

  Hydrology       official/open GIS       streams,         research
                  source TBD              springs,         required
                                          drainage         

  Weather         GeoSphere SPARTACUS v3 rain,            selected
                  daily 1 km grid         temperature      primary source;
                                                           provider +
                                                           rolling features +
                                                           WeatherSnapshot
                                                           validated

  Drought         GeoSphere-derived /     anomalies,       research
                  documented project      deficit          required
                  proxy                                    

  Protected areas official Austrian GIS + zone geometry,   candidate /
                  Biosphärenpark          rules linkage    research
                  Wienerwald                               

  Roads/trails    official data + OSM     access, trail,   later research
                  fallback                parking context  

  User            mushroom-racing         positive +       planned
  observations    application data        negative         
                                          searches         

  Presentation    basemap.at              cartographic     selected;
  basemap                                 background only  integration
                                                           deferred to
                                                           MR-6
  ------------------------------------------------------------------------

## Важное ограничение: eBOD

`bodenkarte.at` полезна, но детальная eBOD-картография в первую очередь
ориентирована на сельскохозяйственные почвы.

Она не должна автоматически использоваться как полная forest-soil map.

Для forest prediction предпочитаются forest-specific BFW data там, где
они доступны и подходят по масштабу.

## DEM: зафиксированное решение

Authoritative source для стартовой области --- официальный DGM, прежде
всего **Land Niederösterreich DGM 10 m**, с **Geoland.at DGM Österreich
10 m** как nationwide fallback.

Полный большой GeoTIFF не является обязательной runtime dependency.

Operational strategy:

``` text
lat/lon или bbox
        ↓
ElevationProvider
        ↓
small remote DEM window / tile
        ↓
local cache
        ↓
elevation / slope / aspect
```

Operational provider должен валидироваться против authoritative DGM.

## Geology: зафиксированное решение

Для operational geology point-query выбран официальный GeoSphere Austria
layer `GE.GeologicUnit_50k`.

``` text
WGS84 coordinate
        ↓
AustrianGeologyProvider
        ↓
GeoSphere ArcGIS REST point-query
        ↓
GeologyQueryResult
        ↓
0..N GeologyRecord
```

MR-2.5 подтвердил cardinality `0..N`. Provider не выбирает автоматически
одну "главную" geological unit. `material` и `representative_lithology`
сохраняются раздельно; silicate/carbonate classification и scoring
interpretation в source provider не выполняются.

Подробности:

``` text
docs/data_sources/GEOLOGY.md
```

## Forest mask: зафиксированное решение

Для operational forest-mask point-query выбран официальный **Waldkarte
BFW Österreich**.

``` text
WGS84 coordinate
        ↓
AustrianForestProvider
        ↓
BFW WFS 2.0
        ↓
FES Intersects(gml:Point, geometry)
        ↓
ForestResult
        ↓
FOREST / NON_FOREST / UNKNOWN
```

Для успешного запроса forestry feature означает `FOREST`, отсутствие
`wfs:member` --- `NON_FOREST`, а семантически неожиданный source result
--- `UNKNOWN`. Operational failures обрабатываются fail-fast через
`ForestProviderError`.

Provider использует фактические `wfs:member`: live PoC подтвердил, что
`numberReturned="0"` может быть возвращён при существующем member.

Production live smoke:

``` text
47.7200000, 15.9000000 -> FOREST
47.8520556, 16.7713333 -> NON_FOREST
```

Waldkarte не является legal/access layer.

Подробности:

``` text
docs/data_sources/FOREST.md
```

## Weather: зафиксированное решение

Для daily weather history выбран официальный **GeoSphere Austria
SPARTACUS v3** dataset:

``` text
spartacus-v3-1d-1km
```

Operational pipeline:

``` text
WGS84 coordinate
        ↓
AustrianWeatherProvider
        ↓
GeoSphere timeseries/historical API
        ↓
WeatherSeries / DailyWeather
        ↓
WeatherFeatures
        ↓
WeatherSnapshot
```

Проверенные parameters:

``` text
RR
TM24
TN
TX
```

`RR` приходит как `kg m-2` и нормализуется в `mm`; temperature parameters
приходят в `degC`.

Критическая source semantics:

``` text
HTTP 200 + all null
```

означает `NO_DATA`, а не нулевую погоду и не transport failure.

`0.0` сохраняется как известный ноль, `null` — как `None`.

Реализованы:

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

Неполное календарное окно возвращает `None`.

End-to-end live smoke на `47.7200, 15.9000` успешно построил
`WeatherSnapshot` через production provider.

После завершения блока:

``` text
full repository suite: 188 passed in 0.35s
```

Пока не реализованы:

-   rain 90d;
-   rainfall anomaly;
-   humidity;
-   wind;
-   soil moisture;
-   drought index;
-   hourly/current INCA integration.

Подробности:

``` text
docs/data_sources/WEATHER.md
```

## Presentation basemap: зафиксированное решение

Для web-карты default presentation basemap --- **basemap.at**.

Она используется только как визуальная картографическая подложка:

``` text
basemap.at
    ↓
MapLibre GL JS
    ↑
mushroom-racing analytical overlays
```

`basemap.at` **не является analytical source для scoring**. Elevation,
geology, forest, weather, protected-area и legal features продолжают
поступать из отдельно выбранных источников.

Лицензия: CC BY 4.0 с обязательной атрибуцией. Конкретный production
endpoint будет повторно проверен перед MR-6 из-за перехода basemap.at к
новой vector-tile инфраструктуре.

## Data-source metadata schema

Каждый production-integrated source должен иметь как минимум:

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

## Integration priority

### P0 --- до первого GIS prototype

-   DEM operational access + validation against official DGM ---
    completed through MR-2.4;
-   geology point-query --- completed through MR-2.5;
-   forest mask --- completed through MR-2.6;
-   weather API + provider + rolling features + WeatherSnapshot ---
    completed;
-   protected-area geometry + licensing --- deferred.

### P1 --- до meaningful Steinpilz scoring

-   tree-species composition;
-   forest soil / acidity proxy;
-   scientific evidence set для `Boletus edulis`;
-   drought context.

### P2 --- calibration и usability

-   canopy density / disturbance;
-   hydrology;
-   roads/trails/parking;
-   field observations.

## Open questions

-   какой operational DEM access method даст лучший баланс
    reproducibility/cost/availability;
-   какой конкретный BFW tree-species layer доступен с подходящим
    resolution и license;
-   доступна ли soil moisture с полезным spatial resolution;
-   как надёжно связывать protected-area geometry с конкретными legal
    rules;
-   нужен ли отдельный current/hourly weather source (например INCA) до
    MR-5 или достаточно daily SPARTACUS для первой scoring версии.
