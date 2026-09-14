# 05 — MVP

## MVP question

Can the application rank a small set of candidate forest areas for Steinpilz and explain the result?

## MVP scope

### Input

For each candidate spot:

- tree suitability;
- geology/soil suitability;
- rainfall history;
- temperature context;
- aspect/elevation suitability;
- vegetation indicators;
- disturbance;
- legal status;
- data completeness.

### Output

```text
Spot: Mariensee / Kampstein sector
Habitat: 91/100
Current conditions: 84/100
Confidence: 63/100
Opportunity: 88/100

Why:
+ strong host-tree mix
+ acidic/silicate setting
+ favourable elevation
+ recent rainfall
+ north-east exposure
- drought history still uncertain
```

## MVP screens

### 1. Map / candidate list

- green / yellow / red candidate sectors;
- sort by Opportunity Score;
- filter by species;
- filter by distance later.

### 2. Spot detail

- final score;
- habitat score;
- current conditions;
- confidence;
- reasons;
- weather history;
- legal status;
- best search window.

### 3. Field report

- found / not found;
- species;
- count;
- location;
- moisture;
- vegetation;
- trees;
- photo;
- notes.

## MVP technical stages

### MVP-A — CLI baseline

- local sample data;
- score calculation;
- explanation;
- tests.

### MVP-B — static map prototype

- geospatial candidate cells;
- offline/sample GIS layers;
- score displayed geographically.

### MVP-C — live weather

- weather import;
- rolling rainfall aggregates;
- dynamic Current Conditions Score.

### MVP-D — field observations

- save positive and negative observations;
- display observation history.

### MVP-E — calibration

- compare predicted vs observed;
- adjust weights;
- document validation.

## Explicitly postponed

- accounts/auth;
- mobile app;
- image recognition;
- social sharing;
- advanced ML;
- route optimization.
