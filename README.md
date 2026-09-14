# mushroom-racing 🍄

**Explainable geospatial mushroom-finding project for Austria.**

`mushroom-racing` is a learning and portfolio project that aims to estimate how promising a forest area is for a target mushroom species by combining:

- mushroom ecology;
- forest composition;
- soil and geology;
- elevation, slope and aspect;
- rainfall and temperature history;
- drought and soil-moisture context;
- legal/protected-area constraints;
- field observations.

The first target is **Steinpilz / Boletus edulis** in Austria, with an initial research area of roughly **150 km around Vienna**.

> The project does **not** claim to know where mushrooms are.  
> It builds an explainable probability model that can be tested and improved with real observations.

## Current status

**Phase: MR-1 — Domain model complete; next: MR-2 data-source PoC**

Implemented now:

- project structure;
- knowledge-model baseline;
- first explainable scoring prototype;
- stable MR-1 domain model (`SpeciesProfile`, `ForestSpot`, `WeatherSnapshot`, `Observation`);
- explicit evidence levels and missing-data semantics;
- JSON sample fixtures and serialization/validation tests;
- tests;
- GitHub Actions test workflow;
- MVP, data-source, schema and field-protocol documentation.

Not implemented yet:

- live weather ingestion;
- production GIS/data-source adapters;
- geospatial feature extraction pipeline;
- map UI;
- database;
- mobile/web frontend;
- ML model.

## Core idea

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

The app should eventually answer questions like:

> “Which forest sectors within driving distance are most promising for Steinpilz today, and why?”

A useful prediction must include **both score and explanation**.

Example:

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

## Documentation

Start here:

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

## Repository structure

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

## Quick start

Requires Python 3.12+.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run the tiny baseline demo:

```bash
python scripts/demo_score.py
```

## Project principles

- **Evidence before confidence.**
- **Explainable before clever.**
- **Rules before ML.**
- **No hidden assumptions.**
- **Negative field observations are data too.**
- **Legal exclusions are hard filters, not score penalties.**
- **A prediction always carries a confidence value.**

## GitHub goal

The repository is intended to demonstrate:

- structured technical research;
- geospatial/data thinking;
- Python fundamentals;
- test-driven iteration;
- explainable scoring;
- data modelling;
- documentation discipline;
- gradual transition from rule-based logic to calibrated models.

## Safety

Never rely on this project to determine whether a mushroom is edible.

Species identification and food safety are a separate problem from habitat prediction.
