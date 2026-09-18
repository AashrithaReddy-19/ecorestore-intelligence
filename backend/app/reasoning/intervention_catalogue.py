"""Static catalogue of restoration interventions.

This is deterministic, curated data (not LLM output) that the rule engine
selects from. It is also mirrored into the `intervention_catalogue` DB table
on startup (see app.seed.seed_intervention_catalogue) so it can be queried
relationally.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Intervention:
    key: str
    name: str
    description: str
    default_time_horizon: str  # short | medium | long
    typical_metrics: list[str] = field(default_factory=list)
    typical_ecosystems: list[str] = field(default_factory=list)


INTERVENTION_CATALOGUE: dict[str, Intervention] = {
    "mangrove_buffer_restoration": Intervention(
        key="mangrove_buffer_restoration",
        name="Native mangrove buffer restoration",
        description=(
            "Replant native mangrove species (e.g. Avicennia, Rhizophora, Sonneratia "
            "depending on salinity zone) along the degraded edge to rebuild a "
            "continuous buffer between land use and open water."
        ),
        default_time_horizon="long",
        typical_metrics=["habitat_connectivity", "species_richness", "soil_organic_carbon", "pollution_risk"],
        typical_ecosystems=["mangrove", "coastal", "wetland"],
    ),
    "habitat_corridor_restoration": Intervention(
        key="habitat_corridor_restoration",
        name="Habitat corridor / connectivity restoration",
        description=(
            "Restore native vegetation strips linking fragmented habitat patches "
            "so wildlife can move, feed, and disperse between them."
        ),
        default_time_horizon="medium",
        typical_metrics=["habitat_connectivity", "species_richness"],
        typical_ecosystems=["forest", "grassland", "cropland", "mangrove", "wetland"],
    ),
    "pollinator_strips": Intervention(
        key="pollinator_strips",
        name="Native flowering / pollinator strips",
        description=(
            "Establish strips of native flowering plants along field margins to "
            "provide forage and nesting resources for pollinators."
        ),
        default_time_horizon="short",
        typical_metrics=["species_richness", "soil_biodiversity"],
        typical_ecosystems=["cropland", "grassland"],
    ),
    "legume_cover_crops": Intervention(
        key="legume_cover_crops",
        name="Legume cover crops and residue retention",
        description=(
            "Plant nitrogen-fixing legume cover crops between growing seasons and "
            "retain crop residue on the surface instead of removing or burning it."
        ),
        default_time_horizon="short",
        typical_metrics=["soil_organic_carbon", "soil_moisture", "soil_biodiversity"],
        typical_ecosystems=["cropland"],
    ),
    "agroforestry": Intervention(
        key="agroforestry",
        name="Agroforestry integration",
        description=(
            "Integrate native trees and shrubs into cropland or grazing land in "
            "rows or scattered arrangements to diversify structure and root depth."
        ),
        default_time_horizon="medium",
        typical_metrics=["soil_organic_carbon", "soil_moisture", "habitat_connectivity", "species_richness"],
        typical_ecosystems=["cropland", "grassland"],
    ),
    "riparian_buffer_restoration": Intervention(
        key="riparian_buffer_restoration",
        name="Riparian buffer restoration",
        description=(
            "Re-establish native vegetated buffers along waterways to intercept "
            "runoff and stabilise banks."
        ),
        default_time_horizon="medium",
        typical_metrics=["pollution_risk", "soil_moisture", "species_richness"],
        typical_ecosystems=["riparian", "wetland", "cropland", "grassland"],
    ),
    "rainwater_harvesting": Intervention(
        key="rainwater_harvesting",
        name="Rainwater harvesting / small water-retention structures",
        description=(
            "Build small-scale water-retention structures (e.g. farm ponds, check "
            "dams, contour trenches) to capture irregular rainfall for dry periods."
        ),
        default_time_horizon="short",
        typical_metrics=["soil_moisture"],
        typical_ecosystems=["cropland", "grassland", "dryland"],
    ),
    "integrated_pest_management": Intervention(
        key="integrated_pest_management",
        name="Reduced pesticide use / integrated pest management (IPM)",
        description=(
            "Replace routine pesticide applications with monitoring-based IPM "
            "(biological control, crop rotation, resistant varieties) to lower "
            "chemical pressure on non-target species."
        ),
        default_time_horizon="short",
        typical_metrics=["species_richness", "soil_biodiversity", "pollution_risk"],
        typical_ecosystems=["cropland"],
    ),
    "erosion_control_ground_cover": Intervention(
        key="erosion_control_ground_cover",
        name="Erosion control and native ground cover",
        description=(
            "Re-establish native, deep-rooted ground cover on exposed or degraded "
            "slopes to reduce surface runoff and sediment loss."
        ),
        default_time_horizon="short",
        typical_metrics=["soil_moisture", "pollution_risk"],
        typical_ecosystems=["cropland", "grassland", "riparian"],
    ),
    "pollution_control_monitoring": Intervention(
        key="pollution_control_monitoring",
        name="Pollution-control monitoring zones",
        description=(
            "Establish designated monitoring zones that track water quality, "
            "plastic/solid waste and effluent inputs near sensitive habitat."
        ),
        default_time_horizon="short",
        typical_metrics=["pollution_risk"],
        typical_ecosystems=["mangrove", "coastal", "wetland", "riparian"],
    ),
    "wetland_restoration": Intervention(
        key="wetland_restoration",
        name="Native wetland restoration",
        description=(
            "Re-flood and revegetate drained or degraded wetland areas with native "
            "hydrophytic species to restore natural hydrology."
        ),
        default_time_horizon="long",
        typical_metrics=["habitat_connectivity", "species_richness", "soil_moisture", "pollution_risk"],
        typical_ecosystems=["wetland", "mangrove", "riparian"],
    ),
}
