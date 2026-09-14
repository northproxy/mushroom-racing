# 08 — Decision Log

This file records important architectural and modelling decisions.

---

## ADR-001 — Start rule-based, not ML

**Status:** accepted

### Decision

The first prediction engine will use explicit rules and weights.

### Why

- easier to understand;
- easier to test;
- ecological assumptions remain visible;
- no trustworthy training dataset exists yet;
- field observations can later calibrate the model.

### Consequence

ML is postponed until enough positive **and negative** observations exist.

---

## ADR-002 — Separate habitat from current conditions

**Status:** accepted

### Decision

Do not store one permanent “mushroom score”.

Use:

- Habitat Score;
- Current Conditions Score;
- Opportunity Score;
- Confidence.

### Why

A perfect forest can be useless during drought, while a rainy week cannot make an unsuitable forest ideal.

---

## ADR-003 — Legal restrictions are hard filters

**Status:** accepted

### Decision

If collecting is prohibited, the area is ineligible for a collecting recommendation.

### Why

A high ecological score must never override legal restrictions.

---

## ADR-004 — Store negative observations

**Status:** accepted

### Decision

A searched location with no target mushroom is a first-class observation.

### Why

Training only on successful finds creates selection bias.

---

## ADR-005 — Keep evidence level explicit

**Status:** accepted

### Decision

Ecological knowledge should distinguish:

- confirmed source;
- expert heuristic;
- field observation;
- working hypothesis.

### Why

The project should not overstate certainty.

---

## ADR-006 — Separate authoritative DEM from operational access

**Status:** accepted

### Decision

The authoritative elevation source is an official Austrian Digital Elevation Model, initially Land Niederösterreich DGM 10 m for the Vienna-area prototype, with Geoland.at DGM Österreich as the nationwide fallback.

Normal application operation must not require downloading the full DEM GeoTIFF. Elevation data should be obtained through small remote windows or tiles and cached locally when practical.

The code must access elevation data through a provider abstraction so that transport can change without changing terrain feature extraction.

### Why

- the authoritative GeoTIFF can be very large;
- the application usually needs only a small area around candidate forest cells;
- downloading the whole country or federal state is unnecessary for interactive use;
- source authority and delivery mechanism are different concerns;
- a provider abstraction allows remote, COG/WCS, or local GeoTIFF implementations to coexist;
- small cached windows reduce bandwidth and storage requirements.

### Validation

An operational elevation provider is acceptable only if its output can be checked against the authoritative DGM.

Validation should use multiple control points and record an acceptable numerical tolerance before the provider is treated as production-ready.

### Consequence

The terrain pipeline is conceptually split into:

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

The full official GeoTIFF remains useful for offline validation and bulk processing, but it is not a required runtime dependency.

If an official subset-friendly service such as COG or WCS becomes available, it should be preferred over a third-party operational provider.

## ADR-007 — Free-first, OCI-preferred, cloud-agnostic infrastructure

**Status:** accepted

### Решение

Инфраструктура проекта строится по принципу:

> **free-first, OCI-preferred, cloud-agnostic**.

Для development и MVP в первую очередь используются бесплатные и open-source инструменты. Для первого облачного deployment предпочтительным кандидатом является Oracle Cloud Infrastructure Free Tier.

При этом domain model, feature extraction и scoring engine не должны зависеть от Oracle-specific SDK или других OCI-specific API.

### Почему

- проект является learning/portfolio проектом и не должен создавать необязательные постоянные расходы;
- OCI предоставляет Always Free ресурсы, достаточные для небольшого backend, хранения артефактов, Infrastructure as Code и мониторинга;
- возможность бесплатного deployment полезна для публичного demo;
- жёсткая привязка core logic к одному cloud provider усложнит переносимость и тестирование;
- бесплатность конкретного managed-сервиса сама по себе не является причиной менять технологически более подходящий компонент.

### Предпочтительное использование OCI

- Compute — backend и небольшие data jobs;
- Object Storage — разрешённые к хранению GIS/data artifacts и cache;
- Resource Manager / Terraform — Infrastructure as Code;
- Monitoring / Logging — после появления постоянно работающего сервиса;
- Vault — secrets, когда они появятся.

Oracle Autonomous Database может использоваться для экспериментов, но не становится основной БД автоматически. Для spatial persistence PostgreSQL/PostGIS остаётся кандидатом, если его функциональность будет лучше соответствовать требованиям приложения.

### Ограничения

- актуальные Free Tier квоты проверяются перед deployment;
- доступность Always Free Compute может зависеть от региона и текущей capacity;
- никакой платный recurring resource не включается без отдельного осознанного решения;
- cloud deployment не является зависимостью для локальной разработки и тестов.

### Следствие

Целевая граница выглядит так:

```text
core / domain / scoring
        ↓
standard interfaces
        ↓
application adapters
        ↓
local / OCI / other cloud
```

Подробный baseline stack описан в `TECH_STACK.md`.
