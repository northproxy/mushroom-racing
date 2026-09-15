# mushroom-racing 🍄

**Объяснимый геопространственный проект для оценки перспективности грибных мест в Австрии.**

`mushroom-racing` — учебный и портфельный проект, цель которого — оценивать, насколько перспективен конкретный лесной участок для целевого вида грибов, объединяя:

- экологию грибов;
- состав леса;
- почвы и геологию;
- высоту, уклон и экспозицию склона;
- историю осадков и температуры;
- контекст засухи и влажности почвы;
- юридические ограничения и охраняемые территории;
- полевые наблюдения.

Первый целевой вид — **Steinpilz / Boletus edulis** в Австрии. Начальная область исследования — примерно **150 км вокруг Вены**.

> Проект **не утверждает, что знает, где находятся грибы**.  
> Он строит объяснимую вероятностную модель, которую можно проверять и улучшать на основе реальных наблюдений.

## Текущее состояние

**Фаза: MR-3 — Geospatial feature extraction завершён; следующий этап — MR-4 weather context extension / подготовка MR-5 scoring**

Сейчас реализованы:

- структура проекта;
- стабильная domain model MR-1 (`SpeciesProfile`, `ForestSpot`, `WeatherSnapshot`, `Observation`);
- явные evidence levels и правила представления отсутствующих данных;
- production PoC для Austrian DEM / terrain, geology, forest mask и daily weather;
- `AustrianElevationProvider`, `AustrianGeologyProvider`, `AustrianForestProvider`, `AustrianWeatherProvider`;
- persistent local DEM cache;
- terrain extraction: elevation / slope / aspect;
- weather rolling features и `WeatherSnapshot`;
- единый `GeospatialFeatureSet`;
- provider-agnostic `GeospatialFeatureAssembler`;
- offline integration fixture для unified feature assembly;
- live end-to-end pipeline:
  `coordinate → providers → normalized features → GeospatialFeatureSet`;
- GitHub Actions workflow для запуска тестов;
- полный test suite: `210 passed in 0.38s`.

Текущие ограничения:

- protected-area geometry и automated legal-rule resolution отложены;
- `collecting_allowed` остаётся `None`, пока статус не подтверждён вручную;
- tree-species и forest-soil layers ещё не интегрированы;
- rain 90d / rainfall anomaly / drought context ещё не реализованы;
- scoring Steinpilz v0.1 ещё не подключён к новому unified feature pipeline;
- интерфейс карты, persistence observations и route generation ещё не реализованы.

## Основная идея

```text
Species knowledge
        ↓
Static geodata
        ↓
Dynamic weather
        ↓
Legal/access filters
        ↓
Explainable scoring engine
        ↓
Field observations
        ↓
Calibration
        ↓
Map + recommendations
```


Текущий geospatial pipeline разделён на независимые ответственности:

```text
data acquisition
        ↓
normalized / derived source features
        ↓
GeospatialFeatureSet
        ↓
ecological interpretation
        ↓
scoring
```

MR-3 намеренно не выполняет species-specific interpretation и не вычисляет score.

В перспективе приложение должно отвечать на вопросы вроде:

> «Какие лесные участки в пределах доступного расстояния сегодня наиболее перспективны для Steinpilz и почему?»

Полезный прогноз должен содержать **и score, и объяснение**.

Пример:

```text
Opportunity score: 84/100
Confidence: 67/100

+ Fichte/Buche/Tanne mix
+ acidic silicate geology
+ 44 mm rainfall over 14 days
+ north-east slope
+ elevation 980–1150 m
- severe rainfall deficit over the previous 60 days
```

## Документация

Начинать лучше отсюда:

1. [`docs/00_PROJECT_BRIEF.md`](docs/00_PROJECT_BRIEF.md)
2. [`docs/01_KNOWLEDGE_MODEL.md`](docs/01_KNOWLEDGE_MODEL.md)
3. [`docs/02_DATA_SOURCES.md`](docs/02_DATA_SOURCES.md)
4. [`docs/DATA_SOURCE_SELECTION.md`](docs/DATA_SOURCE_SELECTION.md)
5. [`docs/03_SCORING_MODEL.md`](docs/03_SCORING_MODEL.md)
6. [`docs/04_DATABASE_SCHEMA.md`](docs/04_DATABASE_SCHEMA.md)
7. [`docs/05_MVP.md`](docs/05_MVP.md)
8. [`docs/06_FIELD_PROTOCOL.md`](docs/06_FIELD_PROTOCOL.md)
9. [`docs/07_ROADMAP.md`](docs/07_ROADMAP.md)
10. [`docs/08_DECISION_LOG.md`](docs/08_DECISION_LOG.md)
11. [`docs/09_GITHUB_SHOWCASE.md`](docs/09_GITHUB_SHOWCASE.md)
12. [`docs/11_GITHUB_SETUP.md`](docs/11_GITHUB_SETUP.md)
13. [`docs/TECH_STACK.md`](docs/TECH_STACK.md)

## Структура репозитория

```text
mushroom-racing/
├── .github/
│   └── workflows/
│       └── tests.yml
├── assets/
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── docs/
├── notebooks/
├── scripts/
├── src/
│   └── mushroom_racing/
├── tests/
├── .editorconfig
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Быстрый старт

Требуется Python 3.12+.

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Установить зависимости для разработки:

```bash
python -m pip install -e ".[dev]"
```

Запустить тесты:

```bash
pytest
```

Запустить небольшой baseline demo:

```bash
python scripts/demo_score.py
```

## Принципы проекта

- **Сначала доказательства, потом уверенность.**
- **Сначала объяснимость, потом сложность.**
- **Сначала правила, потом ML.**
- **Никаких скрытых предположений.**
- **Отрицательные полевые наблюдения — тоже данные.**
- **Юридические ограничения — hard filters, а не штрафы score.**
- **Любой прогноз должен иметь показатель confidence.**

## Цель GitHub-репозитория

Репозиторий должен демонстрировать:

- структурированное техническое исследование;
- мышление в терминах geospatial/data задач;
- владение основами Python;
- разработку с опорой на тесты;
- explainable scoring;
- проектирование структуры данных;
- дисциплину документации;
- постепенный переход от rule-based логики к откалиброванным моделям.

## Безопасность

Нельзя использовать этот проект для определения съедобности гриба.

Определение вида и безопасность употребления грибов — отдельная задача, не связанная напрямую с прогнозированием habitat suitability.
