# 03 --- Scoring Model

## Принцип проектирования

Первая модель --- **rule-based и explainable**.

Мы не начинаем с machine learning.

Модель разделяет:

1.  **Habitat Score** --- насколько участок подходит виду в принципе.
2.  **Current Conditions Score** --- насколько текущая погода
    поддерживает плодоношение.
3.  **Access / Legal Filter** --- можно ли использовать участок с точки
    зрения доступа и правил.
4.  **Confidence Score** --- насколько полны и надёжны входные данные.
5.  **Opportunity Score** --- итоговая рекомендация для текущей даты.

## Предлагаемые группы признаков

  Группа                          Начальный вес
  ----------------------------- ---------------
  деревья-хозяева                           25%
  почва + геология                          20%
  осадки + влажность                        20%
  температура + сезон                       10%
  высота + уклон + экспозиция               10%
  зрелость леса / disturbance                5%
  растения-индикаторы                        5%
  наблюдения                                 5%

Это **baseline weights**, а не научно подтверждённые параметры.

## Hard exclusions

Следующие факторы не просто уменьшают score:

-   сбор запрещён;
-   доступ запрещён;
-   участок находится в protected core zone, где сбор запрещён.

В таких случаях:

``` text
eligible = false
```

## Начальные экологические эвристики

### Положительные

``` text
Fichte dominant                  сильный положительный признак
Fichte + Buche/Tanne             очень сильный положительный признак
acidic silicate geology          положительный признак
Podsol / acidic soil             положительный признак
Moos                             положительный признак
Heidelbeere                      положительный признак
N / NE / NW slope after drought  положительный признак
shaded hollow                    положительный признак
```

### Отрицательные

``` text
Brennnessel                      отрицательный индикатор
dense Brombeere                  отрицательный индикатор
dense tall grass                 отрицательный индикатор
recent clearcut                  сильный отрицательный признак
dry exposed ridge                сильный отрицательный признак
carbonate-rich soil              отрицательный baseline-признак для B. edulis
```

## Задержка после осадков

Начальная рабочая кривая:

    Дней после значимого увлажнения                     Относительный timing score
  --------------------------------- ----------------------------------------------
                               0--3                                         низкий
                               4--6                                         растёт
                              7--10                                        хороший
                             10--16                                  очень хороший
                             17--20                                        хороший
                               \>20   зависит от последующих осадков и температуры

Само понятие «значимое увлажнение» должно учитывать предшествующую
засуху.

## Важное взаимодействие факторов

``` text
30 mm rain after a normal month
!=
30 mm rain after three months of drought
```

Поэтому scoring engine в дальнейшем потребуется корректировка по
drought/history context.

## Контракт объяснимости

Каждый итоговый score должен возвращать причины.

Пример:

``` json
{
  "opportunity_score": 84,
  "confidence": 67,
  "reasons": [
    ["positive", "Fichte/Buche/Tanne forest mix"],
    ["positive", "acidic silicate geology"],
    ["positive", "44 mm rainfall in 14 days"],
    ["positive", "north-east aspect"],
    ["negative", "strong 60-day rainfall deficit"]
  ]
}
```

## Baseline-код

Код в `src/mushroom_racing/scoring.py` намеренно остаётся простым.

Его задача --- зафиксировать:

-   интерфейсы;
-   тесты;
-   объяснимый результат;
-   стабильный baseline.

Это **ещё не валидированный биологический predictor**.

## Текущее состояние Steinpilz v0.1

MR-5 реализуется постепенно поверх уже существующего baseline scoring,
без переписывания работающей модели целиком.

Текущий pipeline:

``` text
GeospatialFeatureSet
        ↓
species-specific interpretation
        ↓
SpotFeatures
        ↓
score_spot()
        ↓
ScoreResult
```

### Missing-data semantics

Scoring components допускают:

``` text
float | None
```

`None` означает, что соответствующий признак неизвестен.

Он:

-   не превращается в `0.0`;
-   не получает искусственный neutral score `0.5`;
-   исключается из weighted average;
-   снижает Confidence через уменьшение coverage доступных признаков.

Если для score нет ни одного известного компонента:

``` text
score = None
```

Confidence рассчитывается отдельно от ecological suitability.

Высокий Opportunity Score при низком Confidence допустим и означает:

> известные признаки выглядят благоприятно, но входных данных пока мало.

### Legal и ecological eligibility

Legal status и ecological eligibility не смешиваются.

``` text
collecting_allowed=False
    → hard legal exclusion

collecting_allowed=None
    → legal status unknown
    → не automatic allow
    → не hard exclusion

ecologically_eligible=False
    → ecological exclusion

ecologically_eligible=None
    → ecological eligibility unknown
    → не exclusion
```

Общий `eligible` становится `True` только когда legal и ecological
eligibility известны и оба равны `True`.

### Forest interpretation

Forest mask используется как prerequisite:

``` text
FOREST
    → ecologically_eligible=True

NON_FOREST
    → ecologically_eligible=False

UNKNOWN
    → ecologically_eligible=None
```

`FOREST` сам по себе не даёт положительный Habitat Score, поскольку
forest mask не содержит tree-species composition или forest maturity.

### Geology interpretation

Raw `GeologyQueryResult` интерпретируется только после
`GeospatialFeatureSet`.

Baseline affinity:

``` text
FAVOURABLE
UNFAVOURABLE
MIXED
UNKNOWN
```

Текущий v0.1 mapping:

``` text
FAVOURABLE    → soil_geology_score = 0.75
UNFAVOURABLE  → soil_geology_score = 0.25
MIXED         → None
UNKNOWN       → None
```

Это **working hypothesis**, а не научно подтверждённая шкала.

Geology является только bedrock proxy и не должна интерпретироваться как
измеренный soil pH, soil type или carbonate content почвы.

### Terrain interpretation

Текущий terrain component использует:

``` text
elevation
slope
aspect
```

Все thresholds являются мягкими v0.1 working hypotheses.

Aspect имеет намеренно слабое влияние, потому что его значение особенно
зависит от moisture/drought context, которого в текущем scoring ещё нет.

Для контрольной точки:

``` text
elevation: 1212 m
slope:     13.23°
aspect:    341.565° / NNW
```

текущий baseline даёт:

``` text
terrain_score = 0.65
```

### Temperature interpretation

MR-5.3d temperature slice реализован отдельным species-specific
interpreter поверх `WeatherSnapshot`.

Используются доступные rolling mean temperature windows:

``` text
avg_temp_7d_c
avg_temp_14d_c
avg_temp_20d_c
```

Каждое известное окно независимо преобразуется в soft v0.1 score.
Отсутствующие окна исключаются из расчёта и не подменяются нулём или
neutral value.

Если все три temperature windows отсутствуют:

``` text
temperature_season_score = None
```

Если доступна только часть окон, итоговый temperature score считается
только по известным значениям.

Текущий soft mapping:

``` text
temperature < 5 °C       → 0.20
5 ≤ temperature < 8 °C   → 0.40
8 ≤ temperature < 10 °C  → 0.60
10 ≤ temperature ≤ 16 °C → 0.80
16 < temperature ≤ 19 °C → 0.60
19 < temperature ≤ 22 °C → 0.40
temperature > 22 °C      → 0.20
```

Это **working hypothesis Steinpilz v0.1**, а не научно подтверждённая
температурная шкала. Значения должны позже проверяться и калиброваться
по evidence и observations.

Rainfall, drought, humidity, seasonality и timing-after-rain в этом
temperature slice намеренно не моделируются.

Для контрольной точки:

``` text
avg_temp_7d_c:  ~14.04
avg_temp_14d_c: ~15.20
avg_temp_20d_c: ~15.68
```

текущий baseline даёт:

``` text
temperature_season_score = 0.80
```

### Пока не реализовано в Steinpilz interpretation

Следующие признаки по-прежнему остаются неизвестными и не имитируются:

``` text
host tree score
forest soil / pH
forest maturity
indicator vegetation
field observation contribution
rainfall / moisture score
90-day rainfall context
rainfall anomaly
soil moisture
drought index
```

Следующий шаг MR-5 --- отдельный rainfall / moisture interpretation
slice.

### Текущая validation

После MR-5.3d temperature slice:

``` text
full repository suite: 255 passed in 0.39s
```

Это подтверждает текущие contracts и scenario semantics, но не является
биологической validation модели.

## Стратегия validation

Будущие изменения модели нужно оценивать по:

-   положительным наблюдениям;
-   отрицательным наблюдениям после реального поиска;
-   calibration по регионам;
-   calibration по сезонам;
-   calibration по видам.

Нельзя оценивать модель только на известных грибных находках, потому что
это создаёт сильный selection bias.
