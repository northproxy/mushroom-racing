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

  -----------------------------------------------------------------------------
  Layer             Primary candidate /     Needed fields     Status
                    selected source                           
  ----------------- ----------------------- ----------------- -----------------
  Forest cover      BFW / Österreichische   forest mask,      candidate /
                    Waldinventur            forest structure  research

  Tree species      BFW / Waldinventur /    Fichte, Buche,    candidate /
                    remote-sensing products Tanne, Eiche,     research
                                            Kiefer, mix       

  Forest soil       BFW Bodenkarte          soil type, pH     candidate /
                    Niederösterreich        proxies, humus,   research
                                            moisture context  

  General soil      eBOD / bodenkarte.at    soil properties   secondary /
                                            where applicable  caution

  Geology           GeoSphere Austria       raw geological    selected primary
                    `GE.GeologicUnit_50k`   unit, material,   source; MR-2.5
                                            representative    provider +
                                            lithology         point-query PoC
                                                              validated

  DEM               Land NÖ DGM 10 m;       elevation, slope, authoritative
                    Geoland.at nationwide   aspect            selected;
                    fallback                                  provider +
                                                              terrain +
                                                              persistent cache
                                                              PoC validated

  Hydrology         official/open GIS       streams, springs, research required
                    source TBD              drainage          

  Weather           GeoSphere Austria Data  rain,             selected primary
                    Hub                     temperature,      source; PoC
                                            humidity, wind    pending

  Drought           GeoSphere-derived /     anomalies,        research required
                    documented project      deficit           
                    proxy                                     

  Protected areas   official Austrian GIS + zone geometry,    candidate /
                    Biosphärenpark          rules linkage     research
                    Wienerwald                                

  Roads/trails      official data + OSM     access, trail,    later research
                    fallback                parking context   

  User observations mushroom-racing         positive +        planned
                    application data        negative searches 

  Presentation      basemap.at              cartographic      selected;
  basemap                                   background only   integration
                                                              deferred to MR-6
  -----------------------------------------------------------------------------

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
-   forest mask;
-   protected-area geometry + licensing;
-   weather API PoC.

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
-   какие конкретные GeoSphere resources использовать для
    historical/current weather pipeline.
