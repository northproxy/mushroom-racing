# 08 — Decision Log

Этот файл фиксирует только значимые архитектурные и моделирующие решения.

---

## ADR-001 — Сначала rule-based model, не ML

**Статус:** accepted

### Решение

Первая prediction model использует явные правила и веса.

### Почему

- модель проще понимать и тестировать;
- экологические предположения остаются видимыми;
- надёжного training dataset пока нет;
- реальные positive и negative observations позже позволят калибровать модель.

### Следствие

ML откладывается до накопления достаточного количества качественных положительных и отрицательных наблюдений.

---

## ADR-002 — Habitat отделяется от current conditions

**Статус:** accepted

### Решение

Не хранить один постоянный «mushroom score».

Использовать отдельно:

- Habitat Score;
- Current Conditions Score;
- Opportunity Score;
- Confidence.

### Почему

Отличный лес может быть бесперспективным во время засухи, а дождливая неделя не делает неподходящий habitat хорошим.

---

## ADR-003 — Legal restrictions являются hard filters

**Статус:** accepted

### Решение

Если сбор подтверждённо запрещён, участок не может быть рекомендован для сбора независимо от ecological score.

### Почему

Высокая экологическая оценка не должна отменять юридическое ограничение.

---

## ADR-004 — Negative observations сохраняются

**Статус:** accepted

### Решение

Проверенный участок, на котором target species не найден, является полноценным `Observation`.

### Почему

Обучение/калибровка только по успешным находкам создаёт selection bias.

---

## ADR-005 — Evidence level должен быть явным

**Статус:** accepted

### Решение

Экологические знания различают:

- `confirmed_source`;
- `expert_heuristic`;
- `field_observation`;
- `working_hypothesis`.

### Почему

Проект не должен выдавать гипотезу или эвристику за подтверждённый факт.

---

## ADR-006 — Authoritative DEM отделяется от operational access

**Статус:** accepted

### Решение

Authoritative elevation source — официальный Austrian Digital Elevation Model, для стартовой зоны прежде всего Land Niederösterreich DGM 10 m, с Geoland.at DGM Österreich как nationwide fallback.

Обычная работа приложения не требует скачивания полного DEM GeoTIFF. Elevation data получаются через небольшие remote windows/tiles и при необходимости кэшируются локально.

Код обращается к elevation через provider abstraction, поэтому способ доставки может измениться без изменения terrain feature extraction.

### Почему

- официальный GeoTIFF может быть очень большим;
- приложение обычно использует небольшую область вокруг candidate cell;
- authority источника и transport/access mechanism — разные ответственности;
- provider abstraction позволяет сочетать remote, COG/WCS и local GeoTIFF implementations;
- маленький cache снижает storage и bandwidth requirements.

### Validation

Operational provider принимается только после проверки на нескольких контрольных точках против authoritative DGM с зафиксированной допустимой погрешностью.

### Следствие

```text
authoritative DGM
        ↓
ElevationProvider
        ↓
small DEM window / tile
        ↓
local cache
        ↓
elevation / slope / aspect
```

Полный GeoTIFF остаётся полезным для offline validation и bulk processing, но не является runtime dependency.

---

## ADR-007 — Free-first, OCI-preferred, cloud-agnostic infrastructure

**Статус:** accepted

### Решение

Инфраструктура строится по принципу:

> **free-first, OCI-preferred, cloud-agnostic**.

Для development/MVP сначала используются бесплатные и open-source инструменты. Для первого cloud deployment предпочтительным кандидатом является Oracle Cloud Infrastructure Free Tier.

Domain model, feature extraction и scoring engine не зависят от Oracle-specific SDK/API.

### Почему

- learning/portfolio проект не должен создавать необязательные постоянные расходы;
- OCI может дать бесплатную инфраструктуру для небольшого backend/demo;
- cloud portability упрощает тестирование и уменьшает lock-in;
- бесплатность managed service сама по себе не является причиной менять более подходящую технологию.

### Предпочтительное использование OCI

- Compute — backend и небольшие data jobs;
- Object Storage — разрешённые GIS/data artifacts и cache;
- Resource Manager / Terraform — Infrastructure as Code;
- Monitoring / Logging — после появления постоянно работающего сервиса;
- Vault — secrets после появления credentials.

### Ограничения

- Free Tier quotas проверяются непосредственно перед deployment;
- никакой recurring paid resource не включается без отдельного решения;
- cloud deployment не является зависимостью для local development/testing.

### Следствие

```text
core / domain / scoring
        ↓
standard interfaces
        ↓
application adapters
        ↓
local / OCI / other cloud
```

---

## ADR-008 — Unknown data не приравниваются к отрицательному значению

**Статус:** accepted

### Решение

Domain model явно различает:

```text
unknown / missing
```

и

```text
known zero / false
```

Для optional данных используется `None` / JSON `null`, если значение неизвестно или не записано.

Примеры:

- `rain_24h_mm = 0.0` — известно, что осадков не было;
- `rain_24h_mm = null` — данных нет;
- `moss_present = false` — проверено, мха нет;
- `moss_present = null` — признак не проверен/не записан;
- `collecting_allowed = false` — подтверждён запрет;
- `collecting_allowed = null` — юридический статус неизвестен.

### Почему

Смешивание missing data с реальным нулём или `false` создаёт систематические ошибки:

- неизвестный legal status может ошибочно стать разрешением;
- пропущенный погодный показатель может выглядеть как нулевое значение;
- непроставленный полевой признак может ошибочно стать negative observation.

### Следствие

- provider adapters должны сохранять missingness, а не подставлять произвольные defaults;
- feature extraction/scoring обязаны отдельно решать, как работать с `None`;
- confidence может снижаться из-за отсутствующих данных, но отсутствие данных не должно тихо превращаться в отрицательный ecological signal.

---

## ADR-009 — basemap.at используется как default presentation basemap

**Статус:** accepted

### Решение

Для web-карты `mushroom-racing` базовой картографической подложкой по умолчанию является **basemap.at**.

Клиентская карта строится на **MapLibre GL JS**. Поверх базовой карты отображаются собственные аналитические слои `mushroom-racing`, например:

- opportunity / habitat score;
- forest / geology context;
- weather-derived layers;
- legal exclusions;
- observations.

`basemap.at` используется как **presentation basemap**, а не как источник признаков scoring model.

DEM, geology, forest, weather, protected areas и legal rules продолжают поступать из отдельно выбранных и валидированных authoritative sources.

### Почему

- basemap.at основана на официальных геоданных австрийских администраций;
- покрывает территорию Австрии;
- допускает свободное использование по CC BY 4.0 при корректной атрибуции;
- позволяет не создавать и не обслуживать собственную базовую карту;
- соответствует free-first подходу проекта;
- MapLibre уже выбран как предпочтительный frontend map renderer;
- разделение presentation и analytical data сохраняет прозрачность происхождения scoring features.

### Attribution

В публичной карте должна присутствовать корректная атрибуция basemap.at, например:

```text
Grundkarte: basemap.at
```

с ссылкой на `https://basemap.at/`.

### Ограничения и implementation note

На момент принятия ADR basemap.at находится в переходе к новой vector-tile инфраструктуре. Существующие raster/legacy products доступны, а новая vector basemap анонсирована как основной будущий формат.

Поэтому ADR фиксирует **поставщика и архитектурную роль**, но не фиксирует конкретный production endpoint.

Перед реализацией MR-6 необходимо повторно проверить:

- актуальный production endpoint;
- рекомендуемый MapLibre integration path;
- статус vector tiles;
- attribution requirements;
- условия доступности и технические ограничения сервиса.

### Следствие

```text
basemap.at
    ↓
presentation basemap
    ↓
MapLibre GL JS
    ↑
mushroom-racing analytical overlays
    ↑
validated analytical providers
```

Scoring core не зависит от basemap.at и остаётся работоспособным без frontend-карты.

