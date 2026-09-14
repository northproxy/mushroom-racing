# 00 — Project Brief

## Project name

**mushroom-racing**

## Problem

Mushroom hunters often combine many weak signals:

- tree species;
- soil;
- moss and indicator plants;
- recent rainfall;
- temperature;
- slope exposure;
- local humidity;
- season;
- personal knowledge of productive spots.

These signals are usually kept mentally and are difficult to compare systematically.

The project asks:

> Can we turn that reasoning into an explainable, testable geospatial model?

## Initial scope

### Geography

Austria, beginning with approximately **150 km around Vienna**.

### Species

Version 0.x focuses on:

- **Boletus edulis / Fichten-Steinpilz**

Related Steinpilz species are documented but should not initially be merged into one ecological profile.

### Initial research zones

- Wechsel
- Semmering
- western Wienerwald
- later: Dunkelsteinerwald / Jauerling
- later: Waldviertel
- later: Rax / Schneeberg
- later: Rosaliengebirge
- later: Leithagebirge

## User problem

A user should eventually be able to:

1. choose a mushroom species;
2. choose a search radius or map area;
3. see candidate forest sectors;
4. rank them by current opportunity;
5. understand *why* each sector has that score;
6. avoid legally restricted areas;
7. record positive and negative field observations;
8. improve future predictions with accumulated evidence.

## Non-goals for the first version

The project does **not** initially attempt to:

- identify mushrooms from images;
- certify edibility;
- guarantee presence of fruiting bodies;
- create a black-box ML predictor;
- reveal private user hotspots publicly;
- optimize commercial harvesting.

## Success criteria for MVP

MVP is successful if it can:

- represent a forest spot;
- represent a species ecology profile;
- ingest or manually accept weather/geodata features;
- calculate explainable sub-scores;
- apply hard legal exclusions;
- produce a final opportunity score + confidence;
- store a field observation;
- compare candidate locations.

## Evidence policy

Every ecological rule should eventually be tagged as one of:

- `confirmed_source`
- `expert_heuristic`
- `field_observation`
- `working_hypothesis`

No working hypothesis should silently become a “fact”.

## Portfolio angle

The repository should visibly demonstrate:

- research → specification → implementation;
- explicit assumptions;
- reproducible milestones;
- testing and validation;
- gradual increase in model sophistication.
