# Geology --- data source and validation notes

## Назначение

Этот документ содержит подробную техническую документацию по geology
source и operational point-query pipeline проекта `mushroom-racing`.

Краткий статус и политика выбора источников остаются в
`docs/DATA_SOURCE_SELECTION.md`.

------------------------------------------------------------------------

# 1. Выбранный primary source

Для MR-2.5 выбран официальный слой GeoSphere Austria:

``` text
dataset: GE.GeologicUnit_50k
provider: GeoSphere Austria
layer_type: polygon Feature Layer
scale: 1:50 000
coverage: Austria
crs: EPSG:4326
access: ArcGIS REST / OGC API Features / WFS
license: CC BY 4.0
last_verified: 2026-09-15
```

MR-2.5 использует ArcGIS REST point-query как минимальный operational
access path.

------------------------------------------------------------------------

# 2. Source facts != model interpretation

``` text
GeoSphere source feature
        ↓
GeologyRecord
        ↓
future geology interpretation
        ↓
silicate / carbonate / other derived features
        ↓
habitat scoring
```

В MR-2.5 намеренно не реализованы `is_silicate`, `is_carbonate`, acidity
proxy, geology suitability и geology score.

------------------------------------------------------------------------

# 3. Provider contract

``` python
@dataclass(frozen=True, slots=True)
class GeologyRecord:
    identifier: str
    name: str | None
    description: str | None
    geologic_unit_type: str | None
    material: str | None
    representative_lithology: str | None

@dataclass(frozen=True, slots=True)
class GeologyQueryResult:
    records: tuple[GeologyRecord, ...]

class GeologyProvider(Protocol):
    def get_geology(self, latitude: float, longitude: float) -> GeologyQueryResult:
        ...
```

`identifier` обязателен; остальные source fields nullable. Source
cardinality --- `0..N`.

------------------------------------------------------------------------

# 4. Operational provider --- AustrianGeologyProvider

``` text
WGS84 latitude / longitude
        ↓
AustrianGeologyProvider
        ↓
esriGeometryPoint / EPSG:4326
        ↓
esriSpatialRelIntersects
        ↓
GeoSphere GE.GeologicUnit_50k
        ↓
response validation
        ↓
GeologyQueryResult
```

HTTP client передаётся provider-у снаружи. Polygon geometry в текущий
runtime result не загружается (`returnGeometry=false`).

------------------------------------------------------------------------

# 5. Validation sample --- MR-2.5b

  --------------------------------------------------------------------------------------------------
  Label          Coordinate           representativeLithology   material        geologicUnitType
  -------------- -------------------- ------------------------- --------------- --------------------
  DEM control    `47.7200, 15.9000`   limestone                 limestone       lithostratigraphic
                                                                                unit

  Waldviertel    `48.6000, 15.3000`   granodiorite              granodiorite    lithodemic unit

  Muehlviertel   `48.5000, 14.5000`   anthropogenic material    anthropogenic   artificial ground
                                                                material        

  Semmering      `47.6300, 15.8300`   dolomite                  dolomite        lithologic unit

  Wechsel        `47.5000, 16.0000`   paragneiss                paragneiss      lithodemic unit

  Northern       `47.8500, 16.5000`   mica schist               mica schist     lithologic unit
  Burgenland                                                                    

  Vienna Basin   `48.1000, 16.6000`   silt                      clay, sand,     lithogenetic unit
                                                                silt            
  --------------------------------------------------------------------------------------------------

Sample подтвердил, что `name` может быть `null`, `material` и
`representativeLithology` не взаимозаменяемы, а источник может
возвращать `artificial ground`.

------------------------------------------------------------------------

# 6. Spatial edge cases --- MR-2.5c

``` text
outside coverage
50.00000000, 15.00000000
feature count: 0
```

`0 features` является нормальным source result и не означает
отрицательный habitat signal.

На реальной polygon boundary:

``` text
47.71911677, 15.92898294
feature count: 3

carbonate sedimentary rock
breccia
clastic sedimentary material
```

Поэтому provider сохраняет все intersecting records и не использует
скрытое правило `features[0]`.

------------------------------------------------------------------------

# 7. Production implementation --- MR-2.5d

Добавлены:

``` text
src/mushroom_racing/geology/geology.py
src/mushroom_racing/geology/austrian_geology.py
src/mushroom_racing/geology/__init__.py
tests/geology/test_geology.py
tests/geology/test_austrian_geology.py
```

Tests используют `httpx.MockTransport`.

``` text
geology slice: 27 passed
full repository regression: 111 passed
```

------------------------------------------------------------------------

# 8. Production live smoke

``` text
coordinate: 47.7200, 15.9000
name: Gutenstein Formation
description: Gutensteiner Kalk (Anis)
geologic_unit_type: lithostratigraphic unit
material: limestone
representative_lithology: limestone
```

Production provider совпал по содержанию с предварительным live PoC.

------------------------------------------------------------------------

# 9. Известные ограничения

-   validation sample мала и не является полной валидацией geological
    units Австрии;
-   surface geology не является soil chemistry;
-   multiple features возможны на boundaries;
-   отсутствие feature не является отрицательным habitat signal;
-   `representativeLithology` --- source classification, а не готовая
    mushroom-habitat category;
-   silicate/carbonate mapping пока не специфицирован и не валидирован;
-   polygon geometry не входит в текущий runtime contract;
-   HTTP availability GeoSphere остаётся внешней зависимостью.

------------------------------------------------------------------------

# 10. Текущий статус

``` text
primary source: GeoSphere Austria GE.GeologicUnit_50k
license: CC BY 4.0
operational provider: AustrianGeologyProvider
point-query: implemented
source cardinality: 0..N
validation sample: 7 ordinary points
spatial edge cases: validated
unit tests: 27 passed
full repository regression: 111 passed
production live smoke: passed
interpretation/scoring: intentionally deferred
```

------------------------------------------------------------------------

# 11. Следующий шаг

Geology source-access block для текущего MR-2 PoC завершён.

Следующий P0 data-source block:

``` text
BFW forest-mask source PoC
```

Geology interpretation (`silicate`, `carbonate`, acidity proxy и habitat
contribution) выполняется позже как отдельная feature-extraction/model
specification задача.
