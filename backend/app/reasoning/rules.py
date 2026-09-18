"""Deterministic multi-metric biodiversity reasoning rules.

This module implements the "do not rely only on LLM prompting" requirement:
every rule below is a plain Python predicate over structured ecosystem
variables. Each rule requires at least three connected variables to fire,
mirroring how a field ecologist would triangulate risk before proposing an
intervention. The LLM (see app.llm) is only used afterwards, to turn the
activated rules + retrieved evidence into prose.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RuleResult:
    rule_id: str
    name: str
    variables_used: list[str]
    signals: list[str]
    interventions: list[str]
    explanation: str
    metrics_affected: list[str]
    query_terms: list[str] = field(default_factory=list)


def _text(v) -> str:
    return (v or "").strip().lower()


def _list_text(v) -> list[str]:
    if not v:
        return []
    return [_text(item) for item in v]


def _contains_any(haystack: str, needles: list[str]) -> bool:
    return any(n in haystack for n in needles)


def _list_contains_any(items: list[str], needles: list[str]) -> bool:
    return any(_contains_any(item, needles) for item in items)


# ---------------------------------------------------------------------------
# Signal detectors — each returns True/False plus doesn't consume a variable
# unless the underlying field was actually provided.
# ---------------------------------------------------------------------------


def low_soil_organic_carbon(data: dict) -> bool | None:
    soc = data.get("soil_organic_carbon_percent")
    if soc is None:
        return None
    return soc < 1.5


def monoculture_land_use(data: dict) -> bool | None:
    lu = data.get("land_use")
    if lu is None:
        return None
    return _contains_any(_text(lu), ["monoculture", "cropland", "single crop", "row crop", "plantation"])


def low_or_irregular_rainfall(data: dict) -> bool | None:
    r = data.get("rainfall_pattern")
    if r is None:
        return None
    return _contains_any(_text(r), ["irregular", "low", "erratic", "decreasing", "drought", "unpredictable"])


def high_rainfall(data: dict) -> bool | None:
    r = data.get("rainfall_pattern")
    if r is None:
        return None
    return _contains_any(_text(r), ["high", "heavy", "excess", "intense"])


def high_habitat_fragmentation(data: dict) -> bool | None:
    f = data.get("habitat_fragmentation")
    if f is None:
        return None
    return _text(f) == "high"


def low_species_observations(data: dict) -> bool | None:
    s = data.get("species_observations")
    if s is None:
        return None
    return _contains_any(_text(s), ["low", "decline", "declining", "sparse", "absent", "rare", "few"])


def has_human_disturbance(data: dict) -> bool | None:
    hi = data.get("human_impact")
    if hi is None:
        return None
    items = _list_text(hi)
    if not items:
        return False
    return _list_contains_any(
        items,
        ["construction", "clearing", "urbanization", "urbanisation", "development", "encroachment",
         "aquaculture", "pollution", "plastic", "pesticide", "mining", "logging", "grazing pressure"],
    )


def coastal_or_mangrove_ecosystem(data: dict) -> bool | None:
    e = data.get("ecosystem_type")
    if e is None:
        return None
    return _contains_any(_text(e), ["mangrove", "coastal", "estuar", "wetland"])


def high_salinity(data: dict) -> bool | None:
    s = data.get("soil_salinity")
    if s is None:
        return None
    return _text(s) == "high"


def aquaculture_expansion(data: dict) -> bool | None:
    hi = data.get("human_impact")
    if hi is None:
        return None
    items = _list_text(hi)
    if not items:
        return False
    return _list_contains_any(items, ["aquaculture"])


def pollution_pressure(data: dict) -> bool | None:
    hi = data.get("human_impact")
    if hi is None:
        return None
    items = _list_text(hi)
    if not items:
        return False
    return _list_contains_any(items, ["plastic", "pollution", "effluent", "waste", "chemical runoff"])


def pesticide_pressure(data: dict) -> bool | None:
    hi = data.get("human_impact")
    if hi is None:
        return None
    items = _list_text(hi)
    if not items:
        return False
    return _list_contains_any(items, ["pesticide", "herbicide", "agrochemical"])


def degraded_vegetation_cover(data: dict) -> bool | None:
    lu = data.get("land_use")
    if lu is None:
        return None
    return _contains_any(_text(lu), ["degraded", "cleared", "bare", "eroded", "denuded"])


def rising_temperature(data: dict) -> bool | None:
    t = data.get("temperature_trend")
    if t is None:
        return None
    return _contains_any(_text(t), ["rising", "increasing", "warming"])


def low_soil_moisture(data: dict) -> bool | None:
    m = data.get("soil_moisture_percent")
    if m is None:
        return None
    return m < 20


# ---------------------------------------------------------------------------
# Rules — each combines >=3 distinct input variables.
# ---------------------------------------------------------------------------


def evaluate_rules(data: dict) -> list[RuleResult]:
    results: list[RuleResult] = []

    # Rule 1: Low SOC + monoculture land use + low/irregular rainfall
    soc, mono, rain = (
        low_soil_organic_carbon(data),
        monoculture_land_use(data),
        low_or_irregular_rainfall(data),
    )
    if soc and mono and rain:
        results.append(
            RuleResult(
                rule_id="R1_soil_carbon_monoculture_rainfall",
                name="Depleted soil carbon under monoculture with unreliable rainfall",
                variables_used=["soil_organic_carbon_percent", "land_use", "rainfall_pattern"],
                signals=["low_soil_organic_carbon", "monoculture_land_use", "low_or_irregular_rainfall"],
                interventions=["legume_cover_crops", "agroforestry", "rainwater_harvesting"],
                explanation=(
                    "Soil organic carbon is below 1.5%, land use is monoculture/cropland, and "
                    "rainfall is low or irregular. Together these reduce soil moisture retention, "
                    "microbial habitat, and pollinator forage, compounding biodiversity loss."
                ),
                metrics_affected=["soil_organic_carbon", "soil_moisture", "soil_biodiversity"],
                query_terms=["soil organic carbon", "cover crops", "monoculture", "soil moisture retention"],
            )
        )

    # Rule 2: High fragmentation + low species observations + human disturbance
    frag, species, disturb = (
        high_habitat_fragmentation(data),
        low_species_observations(data),
        has_human_disturbance(data),
    )
    if frag and species and disturb:
        results.append(
            RuleResult(
                rule_id="R2_fragmentation_species_disturbance",
                name="Isolated habitat patches with declining species activity under human pressure",
                variables_used=["habitat_fragmentation", "species_observations", "human_impact"],
                signals=["high_habitat_fragmentation", "low_species_observations", "human_disturbance"],
                interventions=["habitat_corridor_restoration", "pollinator_strips"],
                explanation=(
                    "Habitat fragmentation is high, species/pollinator observations are low, and "
                    "human disturbance is present nearby. This combination points to restricted "
                    "wildlife movement and isolation of remaining habitat patches."
                ),
                metrics_affected=["habitat_connectivity", "species_richness"],
                query_terms=["habitat fragmentation", "wildlife corridor", "connectivity restoration"],
            )
        )

    # Rule 3: Mangrove/coastal + high salinity + aquaculture expansion + low biodiversity
    coastal, salinity, aqua = (
        coastal_or_mangrove_ecosystem(data),
        high_salinity(data),
        aquaculture_expansion(data),
    )
    if coastal and salinity and aqua and species:
        results.append(
            RuleResult(
                rule_id="R3_mangrove_salinity_aquaculture",
                name="Mangrove edge degradation from salinity stress and aquaculture expansion",
                variables_used=["ecosystem_type", "soil_salinity", "human_impact", "species_observations"],
                signals=["coastal_or_mangrove_ecosystem", "high_salinity", "aquaculture_expansion", "low_species_observations"],
                interventions=["mangrove_buffer_restoration", "pollution_control_monitoring", "habitat_corridor_restoration"],
                explanation=(
                    "The site is a mangrove/coastal ecosystem with high soil salinity, active "
                    "aquaculture expansion, and low biodiversity observations. This threatens "
                    "nursery habitat for fish and crustaceans, coastal resilience, and blue-carbon "
                    "storage, and prioritises the most fragmented remaining patches for protection."
                ),
                metrics_affected=["habitat_connectivity", "species_richness", "pollution_risk", "soil_organic_carbon"],
                query_terms=["mangrove restoration", "aquaculture impact", "blue carbon", "coastal resilience"],
            )
        )

    # Rule 3b: pollution pressure variant (plastic pollution) in coastal/mangrove settings
    pollution = pollution_pressure(data)
    if coastal and pollution and species:
        results.append(
            RuleResult(
                rule_id="R3b_coastal_pollution",
                name="Coastal pollution pressure on low-biodiversity habitat",
                variables_used=["ecosystem_type", "human_impact", "species_observations"],
                signals=["coastal_or_mangrove_ecosystem", "pollution_pressure", "low_species_observations"],
                interventions=["pollution_control_monitoring", "mangrove_buffer_restoration"],
                explanation=(
                    "The ecosystem is coastal/mangrove, plastic or waste pollution pressure is "
                    "present, and species observations are low. Water-quality and solid-waste "
                    "monitoring alongside buffer replanting is warranted before biodiversity can "
                    "recover."
                ),
                metrics_affected=["pollution_risk", "species_richness"],
                query_terms=["marine plastic pollution", "coastal water quality", "mangrove buffer"],
            )
        )

    # Rule 4: High rainfall + degraded vegetation cover + erosion risk (fragmentation or disturbance)
    heavy_rain, degraded = high_rainfall(data), degraded_vegetation_cover(data)
    if heavy_rain and degraded and (frag or disturb):
        results.append(
            RuleResult(
                rule_id="R4_rainfall_erosion",
                name="Erosion risk from heavy rainfall on degraded, disturbed cover",
                variables_used=["rainfall_pattern", "land_use", "habitat_fragmentation" if frag else "human_impact"],
                signals=["high_rainfall", "degraded_vegetation_cover", "fragmentation_or_disturbance"],
                interventions=["riparian_buffer_restoration", "erosion_control_ground_cover"],
                explanation=(
                    "Rainfall is high, vegetation cover is degraded, and the site is further "
                    "stressed by fragmentation or human disturbance, raising sediment runoff risk "
                    "into waterways and downstream aquatic habitat."
                ),
                metrics_affected=["pollution_risk", "soil_moisture", "species_richness"],
                query_terms=["riparian buffer", "erosion control", "sediment runoff", "ground cover"],
            )
        )

    # Rule 5: Pesticide pressure + monoculture + low species observations -> IPM + pollinator strips
    pesticide = pesticide_pressure(data)
    if pesticide and mono and species:
        results.append(
            RuleResult(
                rule_id="R5_pesticide_monoculture_species",
                name="Pesticide pressure on monoculture cropland with declining pollinators",
                variables_used=["human_impact", "land_use", "species_observations"],
                signals=["pesticide_pressure", "monoculture_land_use", "low_species_observations"],
                interventions=["integrated_pest_management", "pollinator_strips", "legume_cover_crops"],
                explanation=(
                    "Pesticide/agrochemical use is reported, land use is monoculture cropland, and "
                    "pollinator/species observations are low. Reducing chemical pressure and adding "
                    "flowering refuge habitat directly targets pollinator decline."
                ),
                metrics_affected=["species_richness", "soil_biodiversity", "pollution_risk"],
                query_terms=["integrated pest management", "pollinator decline", "pesticide biodiversity"],
            )
        )

    # Rule 6: Rising temperature + low soil moisture + irregular rainfall -> water retention
    moisture = low_soil_moisture(data)
    if rising_temperature(data) and moisture and rain:
        results.append(
            RuleResult(
                rule_id="R6_temperature_moisture_rainfall",
                name="Compounding heat and moisture stress under unreliable rainfall",
                variables_used=["temperature_trend", "soil_moisture_percent", "rainfall_pattern"],
                signals=["rising_temperature", "low_soil_moisture", "low_or_irregular_rainfall"],
                interventions=["rainwater_harvesting", "agroforestry"],
                explanation=(
                    "Temperature trend is rising, soil moisture is low, and rainfall is irregular. "
                    "This combination increases drought stress on vegetation and soil fauna unless "
                    "water is actively retained on site."
                ),
                metrics_affected=["soil_moisture", "soil_organic_carbon"],
                query_terms=["water retention structures", "rainwater harvesting", "drought resilience agriculture"],
            )
        )

    # Rule 7: Wetland/mangrove ecosystem + high fragmentation + low moisture-linked degradation
    wetland_like = coastal
    if wetland_like and frag and (degraded or disturb):
        results.append(
            RuleResult(
                rule_id="R7_wetland_fragmentation_degradation",
                name="Wetland hydrology disruption under fragmentation and degradation",
                variables_used=["ecosystem_type", "habitat_fragmentation", "land_use" if degraded else "human_impact"],
                signals=["coastal_or_mangrove_ecosystem", "high_habitat_fragmentation", "degradation_or_disturbance"],
                interventions=["wetland_restoration", "habitat_corridor_restoration"],
                explanation=(
                    "The ecosystem is wetland/mangrove/coastal, fragmentation is high, and the site "
                    "shows degradation or active disturbance, consistent with disrupted natural "
                    "hydrology that native wetland restoration can help rebuild."
                ),
                metrics_affected=["habitat_connectivity", "soil_moisture", "species_richness"],
                query_terms=["wetland restoration", "hydrology restoration", "fragmented wetland"],
            )
        )

    return results
