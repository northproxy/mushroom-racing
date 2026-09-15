"""
File: steinpilz_geology.py
Project: mushroom-racing

Purpose:
    Выполняет species-specific baseline interpretation raw geology
    для Boletus edulis без подмены geology измеренными soil properties.

Created:
    2026-09-15

Last modified:
    2026-09-15

Status:
    active

Lifecycle:
    permanent — часть Steinpilz interpretation layer.

Inputs:
    GeologyQueryResult.

Outputs:
    SteinpilzGeologyInterpretation.

Dependencies:
    Python standard library
    mushroom_racing.geology

Used by:
    MR-5 Steinpilz interpretation pipeline.

Notes:
    Классификация является baseline heuristic.
    Она не определяет soil pH, carbonate content почвы или фактический
    forest-soil type.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from mushroom_racing.geology import GeologyQueryResult


class SteinpilzGeologyAffinity(str, Enum):
    """Baseline affinity raw geology для текущей Steinpilz model."""

    FAVOURABLE = "favourable"
    UNFAVOURABLE = "unfavourable"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SteinpilzGeologyInterpretation:
    """Результат species-specific interpretation raw geology."""

    affinity: SteinpilzGeologyAffinity
    reason: str


SILICATE_TERMS = (
    "granite",
    "granit",
    "gneiss",
    "gneis",
    "quartzite",
    "quarzit",
    "schist",
    "schiefer",
    "silicate",
    "silicatic",
    "sandstone",
    "sandstein",
)


CARBONATE_TERMS = (
    "limestone",
    "kalk",
    "dolomite",
    "dolomit",
    "carbonate",
    "karbonat",
)


def interpret_steinpilz_geology(
    geology: GeologyQueryResult,
) -> SteinpilzGeologyInterpretation:
    """Interpret raw geology as a cautious Steinpilz baseline proxy."""

    records = geology.records

    if not records:
        return SteinpilzGeologyInterpretation(
            affinity=SteinpilzGeologyAffinity.UNKNOWN,
            reason=(
                "No geology records are available; geology contribution "
                "remains unknown."
            ),
        )

    has_silicate = False
    has_carbonate = False

    for record in records:
        texts = (
            getattr(record, "material", None),
            getattr(record, "representative_lithology", None),
        )

        normalized = " ".join(
            value.strip().lower()
            for value in texts
            if isinstance(value, str) and value.strip()
        )

        if any(term in normalized for term in SILICATE_TERMS):
            has_silicate = True

        if any(term in normalized for term in CARBONATE_TERMS):
            has_carbonate = True

    if has_silicate and has_carbonate:
        return SteinpilzGeologyInterpretation(
            affinity=SteinpilzGeologyAffinity.MIXED,
            reason=(
                "Geology records contain both silicate-like and "
                "carbonate-like lithology; no single geology preference "
                "is assumed."
            ),
        )

    if has_silicate:
        return SteinpilzGeologyInterpretation(
            affinity=SteinpilzGeologyAffinity.FAVOURABLE,
            reason=(
                "Silicate-like bedrock is treated as a favourable "
                "Steinpilz baseline geology proxy."
            ),
        )

    if has_carbonate:
        return SteinpilzGeologyInterpretation(
            affinity=SteinpilzGeologyAffinity.UNFAVOURABLE,
            reason=(
                "Carbonate-like bedrock is treated as an unfavourable "
                "Steinpilz baseline geology proxy."
            ),
        )

    return SteinpilzGeologyInterpretation(
        affinity=SteinpilzGeologyAffinity.UNKNOWN,
        reason=(
            "Available geology records were not recognized by the current "
            "Steinpilz baseline geology rules."
        ),
    )
