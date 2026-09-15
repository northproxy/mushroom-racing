# 02 — Data Sources

## Назначение

Этот документ является кратким registry внешних data layers проекта.

Подробная политика доверия, выбранные primary sources, лицензии, access strategy и текущий статус исследования фиксируются в:

```text
DATA_SOURCE_SELECTION.md
```

Если между этим registry и `DATA_SOURCE_SELECTION.md` возникает расхождение, для выбора/статуса источника приоритет имеет `DATA_SOURCE_SELECTION.md`.

Источник не считается production-integrated, пока:

1. понятны условия доступа и лицензия;
2. известно spatial/temporal resolution;
3. известна update frequency;
4. существует воспроизводимый API/download/import workflow;
5. ограничения источника документированы.

## Source registry

| Layer | Primary candidate / selected source | Needed fields | Status |
|---|---|---|---|
| Forest cover | BFW / Österreichische Waldinventur | forest mask, forest structure | candidate / research |
| Tree species | BFW / Waldinventur / remote-sensing products | Fichte, Buche, Tanne, Eiche, Kiefer, mix | candidate / research |
| Forest soil | BFW Bodenkarte Niederösterreich | soil type, pH proxies, humus, moisture context | candidate / research |
| General soil | eBOD / bodenkarte.at | soil properties where applicable | secondary / caution |
| Geology | GeoSphere Austria 1:50k GIS | bedrock, carbonate/silicate proxy | selected primary source |
| DEM | Land NÖ DGM 10 m; Geoland.at nationwide fallback | elevation, slope, aspect | authoritative selected; provider + terrain + persistent cache PoC validated |
| Hydrology | official/open GIS source TBD | streams, springs, drainage | research required |
| Weather | GeoSphere Austria Data Hub | rain, temperature, humidity, wind | selected primary source; PoC pending |
| Drought | GeoSphere-derived / documented project proxy | anomalies, deficit | research required |
| Protected areas | official Austrian GIS + Biosphärenpark Wienerwald | zone geometry, rules linkage | candidate / research |
| Roads/trails | official data + OSM fallback | access, trail, parking context | later research |
| User observations | mushroom-racing application data | positive + negative searches | planned |
| Presentation basemap | basemap.at | cartographic background only | selected; integration deferred to MR-6 |

## Важное ограничение: eBOD

`bodenkarte.at` полезна, но детальная eBOD-картография в первую очередь ориентирована на сельскохозяйственные почвы.

Она не должна автоматически использоваться как полная forest-soil map.

Для forest prediction предпочитаются forest-specific BFW data там, где они доступны и подходят по масштабу.

## DEM: зафиксированное решение

Authoritative source для стартовой области — официальный DGM, прежде всего **Land Niederösterreich DGM 10 m**, с **Geoland.at DGM Österreich 10 m** как nationwide fallback.

Полный большой GeoTIFF не является обязательной runtime dependency.

Operational strategy:

```text
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

## Presentation basemap: зафиксированное решение

Для web-карты default presentation basemap — **basemap.at**.

Она используется только как визуальная картографическая подложка:

```text
basemap.at
    ↓
MapLibre GL JS
    ↑
mushroom-racing analytical overlays
```

`basemap.at` **не является analytical source для scoring**. Elevation, geology, forest, weather, protected-area и legal features продолжают поступать из отдельно выбранных источников.

Лицензия: CC BY 4.0 с обязательной атрибуцией. Конкретный production endpoint будет повторно проверен перед MR-6 из-за перехода basemap.at к новой vector-tile инфраструктуре.

## Data-source metadata schema

Каждый production-integrated source должен иметь как минимум:

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

## Integration priority

### P0 — до первого GIS prototype

- DEM operational access + validation against official DGM;
- geology query/download;
- weather API PoC;
- forest mask;
- protected-area geometry + licensing.

### P1 — до meaningful Steinpilz scoring

- tree-species composition;
- forest soil / acidity proxy;
- scientific evidence set для `Boletus edulis`;
- drought context.

### P2 — calibration и usability

- canopy density / disturbance;
- hydrology;
- roads/trails/parking;
- field observations.

## Open questions

- какой operational DEM access method даст лучший баланс reproducibility/cost/availability;
- какой конкретный BFW tree-species layer доступен с подходящим resolution и license;
- доступна ли soil moisture с полезным spatial resolution;
- как надёжно связывать protected-area geometry с конкретными legal rules;
- какие конкретные GeoSphere resources использовать для historical/current weather pipeline.
