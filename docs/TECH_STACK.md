# Technical Stack — mushroom-racing

## Статус документа

**Версия:** 0.2  
**Дата:** 2026-09-15  
**Статус:** accepted baseline  

## Назначение

Этот документ фиксирует предпочтительный технический стек проекта `mushroom-racing`.

Главный принцип инфраструктуры:

> **free-first, OCI-preferred, cloud-agnostic**.

Мы предпочитаем бесплатные и открытые инструменты, а для облачного размещения в первую очередь рассматриваем Oracle Cloud Infrastructure (OCI) Free Tier. При этом бизнес-логика, модель данных и scoring не должны зависеть от конкретного облачного провайдера.

---

## 1. Core

- **Python 3.12+** — основной язык backend, data pipeline и scoring.
- **dataclasses** — domain model на ранних этапах.
- **pytest** — тесты.
- **ruff** — linting и форматирование.
- **mypy** — статическая проверка типов, если будет добавлена в milestone качества кода.
- **Git + GitHub** — version control и repository hosting.
- **GitHub Actions** — CI.

### Принцип

Scoring core остаётся обычной Python-библиотекой и не зависит от:

- FastAPI;
- базы данных;
- frontend;
- Oracle SDK;
- конкретного GIS/data provider.

```text
providers
   ↓
domain
   ↓
feature extraction
   ↓
scoring
   ↓
application / API
```

---

## 2. Data / GIS

Предпочтительный Python GIS stack:

- **numpy** — численные вычисления;
- **pandas** — табличные данные;
- **shapely** — геометрия;
- **geopandas** — векторные геоданные;
- **rasterio** — растровые данные / DEM;
- **pyproj** — преобразования координатных систем.

Форматы:

- JSON — сериализация небольших структур;
- GeoJSON — небольшие географические fixtures и обмен;
- GeoPackage — локальные векторные данные;
- Parquet / GeoParquet — промежуточные и обработанные наборы данных;
- GeoTIFF / raster tiles — растровые источники и локальный cache.

Зависимости добавляются только тогда, когда они реально нужны текущему milestone.

---

## 3. External data access

Базовый HTTP-клиент:

- **httpx** — предпочтительный клиент для API и remote providers.

Внешние источники подключаются через provider adapters.

Пример:

```text
GeoSphere API
      ↓
GeoSphereWeatherProvider
      ↓
WeatherSnapshot
      ↓
feature extraction
      ↓
SpotFeatures
      ↓
scoring
```

Конкретный внешний API не должен быть частью контракта scoring engine.

---

## 4. Storage strategy

### Ранние milestones

До появления реальной необходимости в серверной БД используем:

- JSON / GeoJSON fixtures;
- Parquet / GeoParquet;
- GeoPackage;
- локальный файловый cache.

### Первый persistent storage

Предпочтительный локальный вариант:

- **SQLite / GeoPackage**.

Причины:

- не требует сервера;
- легко воспроизводится;
- удобно для тестов и локальной разработки;
- не создаёт лишнюю инфраструктуру раньше времени.

### Позже

Для полноценного spatial backend предпочтительным кандидатом остаётся:

- **PostgreSQL + PostGIS**.

Использование Oracle Database не является обязательным только потому, что OCI предлагает бесплатный Autonomous Database. Выбор БД должен определяться требованиями приложения и GIS-функциональностью.

---

## 5. Backend API

Когда появится необходимость в HTTP API:

- **FastAPI** — предпочтительный backend framework.

Пример будущих endpoints:

```text
GET  /spots/{id}
GET  /spots?bbox=...
GET  /scores?species=boletus_edulis
POST /observations
```

FastAPI не добавляется до milestone, где API действительно нужен.

---

## 6. Frontend / map

Для полноценного web MVP предпочтительный frontend stack:

- **TypeScript**;
- **React**;
- **Vite**;
- **MapLibre GL JS**.

MapLibre предпочтителен для:

- собственных GIS-слоёв;
- polygon/cell visualization;
- score overlays;
- protected-area layers;
- интерактивных карточек участков.

### Presentation basemap

Default presentation basemap для web MVP — **basemap.at**.

Архитектурное разделение:

```text
basemap.at
    ↓
presentation only
    ↓
MapLibre GL JS
    ↑
mushroom-racing analytical overlays
```

`basemap.at` не используется как источник признаков scoring model. DEM, geology, forest, weather и legal layers поступают через собственные validated providers.

Конкретный production endpoint basemap.at не фиксируется в stack заранее: перед MR-6 необходимо проверить актуальный production interface, поскольку basemap.at находится в переходе к новой vector-tile инфраструктуре.

Mapbox и Google Maps не являются обязательными зависимостями проекта.

Frontend остаётся отдельным слоем и не содержит scoring logic.

---

## 7. Cloud infrastructure

### Стратегия

> **Free-first / OCI-preferred / cloud-agnostic.**

Для первого публичного или удалённого deployment в первую очередь рассматриваем **Oracle Cloud Infrastructure Free Tier**.

На момент фиксации решения Oracle документирует Always Free ресурсы, среди которых присутствуют:

- AMD Compute;
- Arm-based Ampere A1 Compute;
- Block Storage;
- Object Storage;
- Archive Storage;
- Autonomous Database;
- Resource Manager (Terraform);
- Monitoring;
- Notifications;
- Logging;
- Vault;
- networking и load-balancing resources.

Конкретные квоты и доступность ресурсов могут меняться и должны проверяться перед deployment.

### Предпочтительное использование OCI

**Compute**

- небольшой FastAPI/backend instance;
- scheduled data jobs;
- development/demo environment.

**Object Storage**

- derived GIS artifacts;
- GeoJSON / Parquet datasets;
- DEM tile/window cache;
- экспорт и промежуточные результаты, если лицензия источника разрешает хранение/перераспространение.

**Resource Manager / Terraform**

- reproducible Infrastructure as Code;
- portfolio-friendly deployment documentation.

**Monitoring / Logging**

- использовать после появления постоянно работающего backend.

**Vault**

- API keys и secrets после появления внешних сервисов, требующих credentials.

### Что не делаем

Приложение не должно зависеть от Oracle-specific SDK внутри domain/scoring слоя.

```text
mushroom-racing core
        ↓
standard interfaces
        ↓
infrastructure adapters
        ↓
OCI / another cloud / local machine
```

Таким образом OCI можно заменить без переписывания модели и scoring engine.

---

## 8. Infrastructure evolution

Предполагаемая эволюция:

```text
local development
    ↓
files + SQLite / GeoPackage
    ↓
FastAPI
    ↓
OCI Free Tier VM + Object Storage
    ↓
PostgreSQL/PostGIS when justified
    ↓
production-grade deployment only if needed
```

Мы не вводим заранее:

- Kubernetes;
- Kafka;
- Redis;
- Celery;
- Airflow;
- сложную microservice architecture;
- обязательный managed database;
- ML infrastructure.

Они добавляются только при наличии конкретной задачи, которую невозможно разумно решить текущим stack.

---

## 9. Cost policy

Для development и MVP действует правило:

1. сначала проверить бесплатный/open-source вариант;
2. затем проверить Free Tier облачного сервиса;
3. платный ресурс допускается только после явного решения;
4. recurring cost не должен появляться незаметно;
5. перед включением платного сервиса стоимость и причина фиксируются в `08_DECISION_LOG.md`.

---

## 10. Текущее решение

Для ближайших milestones используем:

```text
Python 3.12+
pytest
standard library where sufficient
httpx when remote API integration begins
GIS libraries only when MR02/MR03 requires them
local files / GeoPackage for data
GitHub Actions for CI
OCI Free Tier as preferred future cloud target
```

Это baseline, а не неизменяемый список технологий. Любое существенное изменение stack должно иметь конкретную причину и, при архитектурном влиянии, отдельный ADR.
