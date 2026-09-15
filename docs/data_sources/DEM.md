# DEM / Terrain — data source and validation notes

## Назначение

Этот документ содержит подробную техническую документацию по DEM-источникам и terrain pipeline проекта `mushroom-racing`.

Краткий статус и выбор источников остаются в `docs/DATA_SOURCE_SELECTION.md`.

---

# 1. Authoritative source

Источником истины для высоты и производных terrain features считается официальный Digitales Geländemodell.

## Land Niederösterreich — DGM 10 m

Предпочтительный authoritative dataset для стартовой зоны.

```text
resolution: 10 x 10 m
format: GeoTIFF
crs: EPSG:31259
pixel_type: float32
nodata: -9999
license: CC BY 4.0
```

## Geoland.at — DGM Österreich 10 m

Общенациональный authoritative fallback.

```text
coverage: Austria
format: GeoTIFF
license: CC BY 4.0
```

---

# 2. Source of truth != access method

Проект разделяет:

```text
authoritative dataset
    = официальный DGM

operational access
    = небольшой remote window / tile

local cache
    = только реально запрошенные фрагменты
```

Operational provider не становится новым источником истины только потому, что через него удобнее получать данные.

Полный DEM GeoTIFF не является обязательной runtime dependency.

---

# 3. Provider contract

Terrain feature extraction не зависит от конкретного способа доставки DEM.

Текущий контракт:

```python
class ElevationProvider(Protocol):
    def get_window(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_m: float,
    ) -> "ElevationWindow":
        ...
```

`ElevationWindow` хранит нормализованный raster window и геопространственный контекст. Provider не привязан к `ForestSpot`.

Возможные реализации:

```text
AustrianElevationProvider
OfficialCogProvider
LocalGeoTiffProvider
```

---

# 4. Operational provider PoC — Austrian Elevation Service

Для MR02 как временный operational access layer реализован и проверен `AustrianElevationProvider`.

Pipeline:

```text
WGS84 lat/lon
        ↓
AustrianElevationProvider
        ↓
HTTP raster rows
        ↓
ElevationWindow
```

Provider **не считается authoritative source**.

Известные ограничения:

- сервис является сторонним prototype;
- underlying elevation data происходят из австрийского DGM / Geoland.at;
- данные преобразованы в `EPSG:3857`;
- значения высоты округлены до целых метров;
- HTTP availability внешнего сервиса не контролируется проектом;
- local cache реализован отдельным provider-wrapper и не меняет upstream source semantics;
- результаты должны периодически сверяться с authoritative DGM.

---

# 5. Direct remote access к официальному DGM

Сервер Land Niederösterreich для `DTM_10x10.zip` проверен на HTTP Range Requests.

Проверенный ответ:

```text
HTTP/1.1 206 Partial Content
Accept-Ranges: bytes
Content-Range: bytes 0-1023/1060848944
```

Это подтверждает поддержку частичной HTTP-загрузки официального архива.

Прямое чтение GeoTIFF через Rasterio/GDAL на основной Windows development-машине пока не используется: Windows Code Integrity policy блокирует нативный модуль Rasterio (`_err.cp314-win_amd64.pyd`).

Это ограничение development environment, а не authoritative dataset. Системная защита ради проекта не отключается.

---

# 6. Elevation validation against authoritative DGM

Operational provider вручную проверен против `NÖ Atlas → Koordinaten / Höhe → Gelände` на четырёх контрольных точках.

| WGS84 | Provider center | NÖ Atlas Gelände | Absolute error | Provider window |
|---|---:|---:|---:|---:|
| `47.95856, 16.44020` | 196.0 m | 198.10 m | 2.10 m | 196–199 m |
| `48.33000, 16.70000` | 164.0 m | 163.90 m | 0.10 m | 163–167 m |
| `48.05000, 16.15000` | 427.0 m | 427.80 m | 0.80 m | 423–434 m |
| `47.72000, 15.90000` | 1212.0 m | 1214.80 m | 2.80 m | 1209–1218 m |

Для этой validation sample:

```text
maximum absolute error: 2.80 m
mean absolute error: 1.45 m
RMSE: approximately 1.80 m
```

Критерий приёмки MR02 PoC:

```text
absolute elevation error <= 5 m
on the selected validation sample
```

Все четыре точки проходят критерий.

Это подтверждает пригодность operational provider для текущего PoC, но **не означает гарантированную точность ±5 m по всей Австрии** и не является основанием для systematic correction offset.

---

# 7. Terrain feature extraction — MR-2.3

Terrain feature extraction реализован поверх `ElevationWindow`.

Результат:

```python
@dataclass(frozen=True, slots=True)
class TerrainFeatures:
    elevation_m: float
    slope_deg: float
    aspect_deg: float | None
```

Для slope/aspect используется центральное соседство `3x3` и Horn gradient.

Semantics aspect:

```text
0°   = north
90°  = east
180° = south
270° = west
```

Для практически плоской поверхности:

```text
aspect_deg = None
```

а не искусственный `0°`.

## CRS handling

### EPSG:3857

Pixel resolution в Web Mercator задан в projected metres и не равен ground metres.

Используется локальная поправка:

```text
ground_resolution ≈ projected_resolution * cos(latitude)
```

Latitude центра окна получается обратным преобразованием Web Mercator Y.

### EPSG:31259

Resolution используется напрямую как метрическая.

### Другие CRS

Unsupported CRS обрабатывается fail-fast.

---

# 8. MR-2.3 validation

Unit tests покрывают:

- flat plane;
- slope rising east;
- slope rising north;
- diagonal plane;
- Web Mercator scale correction;
- слишком маленькое окно;
- чётные dimensions;
- nodata в центральном `3x3`;
- nodata вне центрального `3x3`;
- unsupported CRS.

Результат нового блока:

```text
10 passed
```

Полный repository regression suite после MR-2.3:

```text
71 passed in 0.15s
```

## Live smoke test

Контрольная точка:

```text
47.7200, 15.9000
```

Центральная матрица:

```text
[[1211. 1211. 1211.]
 [1212. 1212. 1213.]
 [1213. 1214. 1215.]]
```

Результат:

```text
elevation: 1212.0 m
slope: 13.225887604858007°
aspect: 341.565051177078°  # NNW
```

Высота в матрице растёт преимущественно к югу и востоку, поэтому направление спуска к северу и западу согласуется с рассчитанным NNW aspect.

Slope/aspect подтверждены unit tests и live smoke test, но **ещё не сравнивались независимо с authoritative slope/aspect product**.

---

# 9. Persistent local cache — MR-2.4

Local cache реализован как отдельный `CachedElevationProvider`, который оборачивает любой объект, совместимый с `ElevationProvider`.

Архитектура:

```text
remote provider
        ↓
CachedElevationProvider
        ↓
ElevationProvider contract
        ↓
ElevationWindow
        ↓
terrain feature extraction
```

Cache хранит **нормализованный `ElevationWindow`**, а не provider-specific HTTP payload. Благодаря этому feature extraction не зависит от способа доставки DEM.

## Cache key

Ключ строится из:

```text
cache format version
cache namespace
latitude
longitude
radius_m
```

Python-класс wrapped provider намеренно не входит в cache key.

Идентичность и версия источника задаются явно через namespace, например:

```text
austrian-elevation-v1
```

При несовместимой смене source/grid/normalization semantics namespace должен быть изменён, что обеспечивает явную invalidation старого cache.

## Storage format

Cache entries сохраняются как compressed NumPy `.npz`.

Основные свойства:

- `np.load(..., allow_pickle=False)`;
- сохраняются `values`, `bounds`, `crs`, `nodata`;
- записывается cache format version и namespace;
- reconstructed object снова проходит validation `ElevationWindow`;
- corrupted или несовместимый cache обрабатывается fail-fast.

Запись выполняется атомарно:

```text
temporary file
      ↓
complete npz write
      ↓
os.replace(...)
      ↓
final cache entry
```

Это снижает риск появления частично записанного cache entry.

## MR-2.4 tests

Unit tests покрывают:

- cache miss вызывает wrapped provider;
- повторный identical request даёт cache hit;
- cache сохраняется между разными provider instances;
- другой `radius_m` создаёт другой entry;
- другой namespace не переиспользует entry;
- loaded `ElevationWindow.values` остаётся read-only;
- corrupted cache fail-fast;
- invalid request parameters fail-fast;
- пустой namespace запрещён.

После MR-2.4 полный repository suite:

```text
84 passed in 0.21s
```

## Live persistent-cache validation

Контрольная точка:

```text
47.7200, 15.9000
radius_m = 20.0
```

Первый процесс получил окно через реальный `AustrianElevationProvider` и записал cache entry.

Второй отдельный процесс использовал wrapped provider, который намеренно выбрасывал исключение при любом вызове remote path. Запрос успешно завершился через cache:

```text
TerrainFeatures(
    elevation_m=1212.0,
    slope_deg=13.225887604858007,
    aspect_deg=341.565051177078,
)

persistent cache hit: OK
```

Это подтверждает persistent cache hit между процессами и отсутствие вызова remote provider на cache hit.


---

# 10. Текущий статус

```text
authoritative DEM source: selected
operational provider: AustrianElevationProvider — validated for MR02 PoC
elevation validation: completed on 4-point sample
terrain feature extraction: implemented
slope/aspect extraction: unit validated + live smoke tested
independent authoritative slope/aspect validation: not yet performed
local cache: implemented + unit validated + cross-process live validated
```

---

# 11. Следующий шаг

DEM pipeline для текущего MR02 PoC завершён:

```text
authoritative source selection
        ↓
operational remote provider
        ↓
elevation validation
        ↓
terrain feature extraction
        ↓
persistent local cache
```

Следующий P0 data-source block:

```text
GeoSphere geology query / download PoC
```

Дальнейшие улучшения DEM — например tile-aware cache, authoritative slope/aspect comparison или официальный COG/WCS access — выполняются только при появлении отдельной потребности и не блокируют следующий MR02 source layer.
