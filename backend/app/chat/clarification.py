"""Missing-data detection and focused clarifying-question generation.

Only the highest-value missing fields are asked about, and never more than
three per turn, per the product requirement.
"""
from __future__ import annotations

from collections import OrderedDict

# Ordered by information value for a first-pass biodiversity risk read.
CRITICAL_FIELDS: "OrderedDict[str, str]" = OrderedDict(
    [
        (
            "ecosystem_type",
            "the land-use or ecosystem type (e.g. mangrove, cropland, grassland, forest, wetland)",
        ),
        (
            "soil_condition",
            "soil organic carbon level or general soil condition (e.g. degraded, healthy, sandy, saline)",
        ),
        (
            "rainfall_pattern",
            "the rainfall pattern or water availability (e.g. regular, irregular, low, high)",
        ),
        (
            "human_impact",
            "the major human pressures on the site (e.g. pesticide use, pollution, clearing, construction, aquaculture)",
        ),
        (
            "species_observations",
            "what you have observed about local wildlife, birds, or pollinator activity",
        ),
    ]
)

MAX_QUESTIONS_PER_TURN = 3


def _has_soil_condition(facts: dict) -> bool:
    return any(
        facts.get(k) is not None
        for k in ("soil_organic_carbon_percent", "soil_ph", "soil_moisture_percent", "soil_salinity")
    )


def missing_critical_fields(facts: dict) -> list[str]:
    missing: list[str] = []
    if not facts.get("ecosystem_type") and not facts.get("land_use"):
        missing.append("ecosystem_type")
    if not _has_soil_condition(facts):
        missing.append("soil_condition")
    if not facts.get("rainfall_pattern"):
        missing.append("rainfall_pattern")
    if not facts.get("human_impact"):
        missing.append("human_impact")
    if not facts.get("species_observations"):
        missing.append("species_observations")
    return missing


def build_clarifying_questions(facts: dict, max_questions: int = MAX_QUESTIONS_PER_TURN) -> list[str]:
    missing = missing_critical_fields(facts)
    questions = []
    for field in missing[:max_questions]:
        questions.append(CRITICAL_FIELDS[field])
    return questions


def format_clarifying_message(questions: list[str]) -> str:
    if not questions:
        return ""
    lines = ["To make an evidence-grounded assessment, please share:"]
    for i, q in enumerate(questions, start=1):
        lines.append(f"{i}. {q}")
    return "\n".join(lines)


def has_enough_for_assessment(facts: dict) -> bool:
    """A minimal viable assessment needs at least 3 substantive variables."""
    provided = sum(
        1
        for k in (
            "ecosystem_type",
            "land_use",
            "soil_organic_carbon_percent",
            "soil_ph",
            "soil_moisture_percent",
            "soil_salinity",
            "rainfall_pattern",
            "temperature_trend",
            "habitat_fragmentation",
            "human_impact",
            "species_observations",
        )
        if facts.get(k)
    )
    return provided >= 3
