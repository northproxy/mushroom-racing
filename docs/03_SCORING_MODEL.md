# 03 — Scoring Model

## Design principle

The first model is **rule-based and explainable**.

We do not start with machine learning.

The model separates:

1. **Habitat Score** — how suitable the place is in general.
2. **Current Conditions Score** — whether current weather supports fruiting.
3. **Access / Legal Filter** — whether the place can be used.
4. **Confidence Score** — how complete/reliable the input data are.
5. **Opportunity Score** — final recommendation for the current date.

## Proposed feature groups

| Group | Initial weight |
|---|---:|
| host trees | 25% |
| soil + geology | 20% |
| rainfall + moisture | 20% |
| temperature + season | 10% |
| elevation + slope + aspect | 10% |
| forest maturity / disturbance | 5% |
| indicator vegetation | 5% |
| observations | 5% |

These are **baseline weights**, not validated scientific parameters.

## Hard exclusions

The following do not merely reduce score:

- collection prohibited;
- access prohibited;
- protected core zone where collecting is forbidden.

For those cases:

```text
eligible = false
```

## Initial ecological heuristics

### Positive

```text
Fichte dominant                  strong positive
Fichte + Buche/Tanne             very strong positive
acidic silicate geology          positive
Podsol / acidic soil             positive
Moos                             positive
Heidelbeere                      positive
N / NE / NW slope after drought  positive
shaded hollow                    positive
```

### Negative

```text
Brennnessel                      negative indicator
dense Brombeere                  negative indicator
dense tall grass                 negative indicator
recent clearcut                  strong negative
dry exposed ridge                strong negative
carbonate-rich soil              negative for B. edulis baseline
```

## Timing after rainfall

Initial working curve:

| Days after meaningful wetting | Relative timing score |
|---:|---:|
| 0–3 | low |
| 4–6 | rising |
| 7–10 | good |
| 10–16 | very good |
| 17–20 | good |
| >20 | depends on subsequent rain/temp |

The “meaningful wetting event” itself must consider prior drought.

## Important interaction

```text
30 mm rain after a normal month
!=
30 mm rain after three months of drought
```

The scoring engine will therefore eventually require a drought/history correction.

## Explainability contract

Every final score should return reasons.

Example:

```json
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

## Baseline code

The code in `src/mushroom_racing/scoring.py` is intentionally simple.

Its job is to establish:

- interfaces;
- tests;
- explainable output;
- a stable baseline.

It is **not** yet a validated biological predictor.

## Validation strategy

Later model changes should be measured against:

- positive observations;
- negative searched observations;
- calibration by region;
- calibration by season;
- calibration by species.

Avoid evaluating only on known mushroom finds because that produces severe selection bias.
