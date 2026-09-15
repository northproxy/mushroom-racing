# WEATHER — GeoSphere Austria SPARTACUS v3

## Назначение

Документ фиксирует выбранный weather source, operational access,
нормализацию, missing-data semantics и проверки, выполненные в MR-2.

## Источник

``` yaml
source_id: geosphere_spartacus_v3_1d_1km
name: SPARTACUS v3 daily 1 km
provider: GeoSphere Austria
layer_type: gridded daily weather
license: CC BY 4.0
coverage: Austria / effective SPARTACUS grid coverage
resolution: approximately 1 km
temporal_resolution: 1 day
access_method: GeoSphere Dataset API
api_mode: timeseries/historical
last_verified: 2026-09-15
```

Dataset:

``` text
spartacus-v3-1d-1km
```

Operational endpoint pattern:

``` text
https://dataset.api.hub.geosphere.at/v1/timeseries/historical/spartacus-v3-1d-1km
```

## Используемые parameters

``` text
RR    daily precipitation sum
TM24  daily mean of air temperature
TN    daily minimum of air temperature
TX    daily maximum of air temperature
```

Проверенные units:

``` text
RR    kg m-2
TM24  degC
TN    degC
TX    degC
```

Для воды:

``` text
1 kg m-2 = 1 mm
```

поэтому `RR` нормализуется в `precipitation_mm` без изменения численного
значения.

## Provider contract

Source-agnostic слой:

``` text
WeatherProvider
        ↓
WeatherSeries
        ↓
DailyWeather[]
```

Основные структуры:

``` text
DailyWeather
    timestamp
    precipitation_mm | None
    mean_temperature_c | None
    min_temperature_c | None
    max_temperature_c | None
```

``` text
WeatherSeries
    requested_latitude
    requested_longitude
    source_latitude
    source_longitude
    source_id
    records
```

GeoSphere implementation:

``` text
AustrianWeatherProvider
```

## Requested coordinate и source coordinate

GeoSphere `timeseries` возвращает ближайшую raster/grid point.

Поэтому provider сохраняет отдельно:

``` text
requested coordinate
source coordinate
```

Контрольный пример:

``` text
requested:
47.7200, 15.9000

source:
47.718814849853516, 15.900300979614258
```

Это важно для explainability, debugging и будущей оценки spatial
uncertainty.

## Missing-data semantics

Главное правило:

``` text
None != 0.0
```

`0.0` означает известный ноль.

Например:

``` text
precipitation_mm = 0.0
```

означает, что осадков не было.

``` text
precipitation_mm = None
```

означает, что данных нет.

Live PoC для Munich подтвердил source edge case:

``` text
HTTP 200
grid point returned
all requested weather values = null
```

Такой ответ не является transport error.

Он нормализуется как:

``` text
WeatherAvailability.NO_DATA
```

Доступны состояния:

``` text
AVAILABLE
PARTIAL
NO_DATA
```

## Fail-fast provider errors

`WeatherProviderError` используется для:

-   network / timeout;
-   HTTP errors;
-   malformed JSON;
-   неправильного FeatureCollection contract;
-   неожиданного числа features;
-   неправильной Point geometry;
-   отсутствующих обязательных parameters;
-   несовпадения длины timestamps и parameter arrays;
-   неожиданных units;
-   non-numeric или non-finite values;
-   отрицательных precipitation values.

`null` weather value сам по себе не является ошибкой.

## Floating-point values

GeoSphere может возвращать значения вида:

``` text
26.30000039190054
```

Provider не округляет их.

Округление относится к presentation layer.

## Weather feature extraction

Над normalized daily series реализованы calendar rolling windows.

Rainfall:

``` text
rain_24h_mm
rain_3d_mm
rain_7d_mm
rain_14d_mm
rain_21d_mm
rain_28d_mm
```

Temperature:

``` text
avg_temp_7d_c
avg_temp_14d_c
avg_temp_20d_c
```

Окна inclusive по `as_of_date`.

Пример:

``` text
7d = as_of_date + 6 предыдущих календарных дней
```

Используется strict completeness policy.

Если отсутствует хотя бы один календарный день, соответствующий
derived feature:

``` text
None
```

Если `RR=None`, ломаются только precipitation windows, содержащие этот
день.

Если `TM24=None`, ломаются только mean-temperature windows, содержащие
этот день.

Known `0.0` остаётся нормальным значением и участвует в вычислении.

## WeatherSnapshot assembly

Pipeline:

``` text
WeatherSeries
        ↓
WeatherFeatures
        ↓
WeatherSnapshot
```

Заполняются:

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

min_temp_c
max_temp_c
```

`min_temp_c` и `max_temp_c` относятся к `as_of_date`.

Пока остаются `None`:

``` text
rain_90d_mm
rain_anomaly_value
rain_anomaly_method
humidity_pct
wind_speed_m_s
soil_moisture_value
soil_moisture_method
drought_index_value
drought_index_method
```

Неизвестные значения не заменяются defaults.

## Live validation

### Mountain control point

``` text
47.7200, 15.9000
```

Результат:

``` text
valid daily RR / TM24 / TN / TX
WeatherAvailability.AVAILABLE
```

### Vienna control point

``` text
48.2082, 16.3738
```

Результат:

``` text
valid daily data
different source grid cell
```

### Outside-effective-coverage case

Munich:

``` text
48.1372, 11.5756
```

Результат:

``` text
HTTP 200
all RR / TM24 / TN / TX values = null
WeatherAvailability.NO_DATA
```

### Historical depth

На основной контрольной точке проверен:

``` text
1961-01-01 .. 1961-01-31
```

Получены полноценные daily values без `null`.

## End-to-end smoke

Для:

``` text
coordinate: 47.7200, 15.9000
as_of_date: 2026-09-12
source range: 2026-08-16 .. 2026-09-12
```

получен:

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

min_temp_c     ≈ 8.5
max_temp_c     ≈ 16.0
```

## Tests

После полного weather pipeline:

``` text
188 passed in 0.35s
```

Проверены:

-   provider contract;
-   timezone-aware timestamps;
-   `0.0` vs `None`;
-   `AVAILABLE / PARTIAL / NO_DATA`;
-   GeoSphere parsing;
-   query construction;
-   unit validation;
-   malformed payloads;
-   transport errors;
-   partial null;
-   all-null;
-   rolling windows;
-   missing calendar days;
-   WeatherSnapshot assembly;
-   end-to-end live smoke.

## Ограничения

SPARTACUS v3 — daily gridded dataset примерно 1 km.

Это значит:

-   он не описывает микроклимат конкретного склона с метровой точностью;
-   source grid point может отличаться от requested coordinate;
-   последние дни могут пересчитываться после GeoSphere quality control;
-   hourly/current weather пока не интегрирован;
-   soil moisture и drought context пока не реализованы.

SPARTACUS не должен интерпретироваться как измерение непосредственно на
точке пользователя.

## Следующие weather-задачи

Необходимость этих задач должна определяться scoring requirements:

``` text
rain 90d
rainfall anomaly / deficit
drought proxy or authoritative drought source
current/hourly INCA
humidity
wind
```

Они не добавляются автоматически только потому, что доступны.
