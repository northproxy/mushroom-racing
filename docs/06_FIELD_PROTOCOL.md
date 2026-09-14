# 06 — Field Protocol

## Purpose

Field observations must be structured enough to improve the model.

A casual note such as “found 3 mushrooms near Semmering” is useful personally but weak as training data.

## Before entering the forest

Record:

- date/time;
- target sector;
- weather;
- recent rain;
- planned elevation band;
- legal/access check.

## At each searched sector

Record:

- GPS position;
- elevation;
- slope/aspect if available;
- dominant trees;
- secondary trees;
- canopy;
- moss;
- Heidelbeere;
- Heidekraut;
- Brennnessel;
- Brombeere;
- grass density;
- surface moisture;
- moisture a few cm below the surface;
- disturbance / logging;
- search duration.

## Positive observation

Record:

- target species;
- confidence in identification;
- count;
- photo;
- microhabitat;
- nearby host tree;
- approximate local radius searched.

## Negative observation

Negative observations are mandatory for model quality.

Record:

- `found_target_species = false`;
- searched minutes;
- approximate area;
- whether other mushrooms were present;
- soil moisture;
- forest indicators.

## Search behaviour

After a first confirmed find:

1. note exact environmental pattern;
2. avoid rushing directly uphill;
3. inspect approximately the same elevation;
4. follow similar aspect and host-tree composition;
5. record both finds and searched empty segments.

## Data quality

A field report should later receive a quality flag:

- `high`
- `medium`
- `low`

High-quality observations have:

- precise position;
- species confidence;
- search effort;
- environmental details;
- no obvious legal/location ambiguity.
