# Forest data source --- BFW Waldkarte Österreich

## Назначение

Документ фиксирует выбранный forest-mask source, operational access,
provider contract, live validation и ограничения MR-2.6.

## Source metadata

``` yaml
source_id: bfw_waldkarte_at
name: Waldkarte BFW Österreich
provider: Bundesforschungszentrum für Wald (BFW)
metadata_record_id: b87c2f56-ecd5-4703-baa3-8398e138a58c
layer_type: vector forest mask / INSPIRE Existing Land Use
license: CC BY 4.0
coverage: Austria
source_orthophotos: 2021-2024
update_frequency: annual
access_method: WFS 2.0; WMS; GeoPackage/GML download
operational_access: WFS 2.0
feature_type: elu:ExistingLandUseObject
dataset_crs_metadata: EPSG:3035
operational_query_crs: EPSG:4326
last_verified: 2026-09-15
cost: free
```

BFW forest definition в metadata следует Österreichische Waldinventur:
minimum unit 500 m², minimum width 10 m, minimum canopy/cover 30%.

## Роль в mushroom-racing

Waldkarte используется как forest/non-forest source. Она не определяет
право доступа, право сбора грибов или legal exclusions.

## Operational access

`AustrianForestProvider` выполняет WFS 2.0 POST с FES 2.0 `Intersects` и
`gml:Point` в EPSG:4326.

``` text
WGS84 coordinate
        ↓
WFS GetFeature
        ↓
FES Intersects(gml:Point, geometry)
        ↓
elu:ExistingLandUseObject
```

Ранний tiny-BBOX PoC был заменён точным point `Intersects` после live
проверки поддержки этого запроса.

## Domain contract

``` text
ForestStatus: FOREST / NON_FOREST / UNKNOWN
ForestResult: status
ForestProvider.get_forest_status(latitude, longitude) -> ForestResult
```

`ForestSpot` остаётся отдельной агрегированной domain entity.

## Семантика

``` text
0 actual wfs:member -> NON_FOREST
>=1 member with specificLandUse=forestry -> FOREST
members without confirmed forestry classification -> UNKNOWN

transport / HTTP / malformed XML -> ForestProviderError
```

Таким образом сохраняются принципы `unknown != false` и
`provider failure != source-level unknown`.

## Особенность WFS

Live responses показали, что `numberReturned="0"` может сосуществовать с
реальным `wfs:member`. Provider поэтому использует фактические members,
а не `numberReturned`.

## Validation

Positive forest control:

``` text
47.7200000, 15.9000000
actual wfs:member: 1
specificLandUse: forestry
result: FOREST
```

Negative lake control:

``` text
47.8520556, 16.7713333
actual wfs:member: 0
result: NON_FOREST
```

Production live smoke через `AustrianForestProvider` подтвердил те же
результаты.

## Tests at MR-2.6 completion

``` text
forest slice: 27 passed
full repository suite: 146 passed
```

Покрыты FOREST/NON_FOREST/UNKNOWN, multiple members, quirk
`numberReturned`, POST point-Intersects contract, malformed XML, HTTP и
transport failures, invalid coordinates/timeout и domain contract.

## Known limitations

-   validation sample пока очень мал и не подтверждает nationwide
    accuracy;
-   source отражает BFW mapping methodology, а не legal definition;
-   orthophoto/update cycle создаёт temporal lag для недавних изменений;
-   polygon boundary cases требуют отдельной будущей проверки;
-   tree species, structure, canopy и age не валидированы MR-2.6;
-   WFS остаётся operational dependency; GeoPackage полезен как будущий
    reproducible bulk fallback.

## MR-2.6 conclusion

``` text
source selected
license documented
WFS access validated
exact point query validated
provider implemented
positive + negative live controls validated
forest slice: 27 passed
full suite: 146 passed
```
