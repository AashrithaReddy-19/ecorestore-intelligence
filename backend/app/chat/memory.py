"""Lightweight keyword-based fact extraction from free-text chat messages,
plus conversation memory (collected_facts) merging across turns.

This is intentionally simple pattern matching rather than a full NLP
pipeline: it only ever fills in fields it has clear textual evidence for, so
it never fabricates structured data from vague text.
"""
from __future__ import annotations

import re

ECOSYSTEM_KEYWORDS = {
    "mangrove": ["mangrove"],
    "coastal": ["coastal", "estuary", "estuarine"],
    "wetland": ["wetland", "marsh", "swamp"],
    "forest": ["forest", "woodland"],
    "grassland": ["grassland", "savanna", "pasture", "rangeland"],
    "cropland": ["cropland", "farmland", "farm", "field", "agricultural land"],
    "riparian": ["riparian", "riverbank", "streamside"],
    "dryland": ["dryland", "arid land", "semi-arid"],
}

# Order matters: checked in sequence against any sentence mentioning rain/rainfall,
# so phrasing like "rainfall is irregular" matches just as well as "irregular rainfall".
RAINFALL_KEYWORDS = {
    "irregular": ["irregular", "erratic", "unpredictable"],
    "low": ["drought", "dry spell", "little rain", "low", "scarce", "insufficient"],
    "high": ["heavy", "excess", "flooding", "high", "abundant"],
}

HUMAN_IMPACT_KEYWORDS = [
    "pesticide", "herbicide", "agrochemical", "pollution", "plastic", "construction",
    "clearing", "deforestation", "urbanization", "urbanisation", "aquaculture", "mining",
    "logging", "overgrazing", "grazing pressure", "encroachment", "effluent",
]

SPECIES_KEYWORDS = ["bird", "pollinator", "wildlife", "species", "biodiversity", "insect", "fish", "fauna"]

SOC_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*%?\s*(?:soil organic carbon|soc)\b", re.IGNORECASE)
PH_PATTERN = re.compile(r"ph\s*(?:of|is|:)?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
MOISTURE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*%?\s*(?:soil moisture|moisture)\b", re.IGNORECASE)


def extract_facts_from_text(text: str) -> dict:
    lower = text.lower()
    facts: dict = {}

    for ecosystem, keywords in ECOSYSTEM_KEYWORDS.items():
        if any(k in lower for k in keywords):
            facts["ecosystem_type"] = ecosystem
            break

    if "degraded" in lower or "cleared" in lower or "bare soil" in lower:
        facts.setdefault("land_use", "degraded")
    if "monoculture" in lower:
        facts["land_use"] = "monoculture"

    rain_sentences = [s for s in re.split(r"(?<=[.!?])\s+", lower) if "rain" in s]
    rain_text = " ".join(rain_sentences)
    if rain_text:
        for pattern, keywords in RAINFALL_KEYWORDS.items():
            if any(k in rain_text for k in keywords):
                facts["rainfall_pattern"] = pattern
                break

    if "salin" in lower:
        if "high salin" in lower:
            facts["soil_salinity"] = "high"
        elif "low salin" in lower:
            facts["soil_salinity"] = "low"
        else:
            facts["soil_salinity"] = "moderate"

    if "rising temperature" in lower or "warming" in lower or "getting hotter" in lower:
        facts["temperature_trend"] = "rising"

    if "fragmented" in lower or "fragmentation" in lower or "isolated patch" in lower:
        facts["habitat_fragmentation"] = "high"

    impacts = [kw for kw in HUMAN_IMPACT_KEYWORDS if kw in lower]
    if impacts:
        facts["human_impact"] = impacts

    if any(k in lower for k in SPECIES_KEYWORDS):
        sentences = re.split(r"(?<=[.!?])\s+", text)
        relevant = [s for s in sentences if any(k in s.lower() for k in SPECIES_KEYWORDS)]
        if relevant:
            facts["species_observations"] = " ".join(relevant).strip()

    soc_match = SOC_PATTERN.search(text)
    if soc_match:
        facts["soil_organic_carbon_percent"] = float(soc_match.group(1))

    ph_match = PH_PATTERN.search(text)
    if ph_match:
        facts["soil_ph"] = float(ph_match.group(1))

    moisture_match = MOISTURE_PATTERN.search(text)
    if moisture_match:
        facts["soil_moisture_percent"] = float(moisture_match.group(1))

    return facts


def merge_facts(existing: dict, new_facts: dict) -> dict:
    """Merge new facts into existing collected_facts, with lists unioned and
    scalars overwritten only when the new value is non-null."""
    merged = dict(existing or {})
    for key, value in (new_facts or {}).items():
        if value is None:
            continue
        if isinstance(value, list):
            current = merged.get(key) or []
            merged[key] = sorted(set(current) | set(value))
        else:
            merged[key] = value
    return merged


def summarize_memory(facts: dict) -> str:
    if not facts:
        return "No ecosystem details captured yet."
    parts = []
    if facts.get("location_name"):
        parts.append(f"location: {facts['location_name']}")
    if facts.get("ecosystem_type") or facts.get("land_use"):
        parts.append(f"ecosystem/land use: {facts.get('ecosystem_type') or facts.get('land_use')}")
    if facts.get("soil_organic_carbon_percent") is not None:
        parts.append(f"SOC: {facts['soil_organic_carbon_percent']}%")
    if facts.get("soil_salinity"):
        parts.append(f"salinity: {facts['soil_salinity']}")
    if facts.get("rainfall_pattern"):
        parts.append(f"rainfall: {facts['rainfall_pattern']}")
    if facts.get("habitat_fragmentation"):
        parts.append(f"fragmentation: {facts['habitat_fragmentation']}")
    if facts.get("human_impact"):
        parts.append(f"human pressures: {', '.join(facts['human_impact'])}")
    if facts.get("species_observations"):
        parts.append(f"species notes: {facts['species_observations'][:120]}")
    return "Captured so far — " + "; ".join(parts) + "."
