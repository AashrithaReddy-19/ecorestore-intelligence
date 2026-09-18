"""Reasoning engine orchestrator.

Pipeline: structured variables -> deterministic rules (app.reasoning.rules)
-> intervention aggregation -> evidence retrieval (app.rag.retrieval) ->
ranked, cited recommendations -> optional LLM prose polish
(app.llm.provider). The LLM step is additive only: if disabled or it fails,
template-composed text (fully grounded in the rule engine + retrieved
evidence) is used instead, so the pipeline never depends on an API key.
"""
from __future__ import annotations

from app.chat.clarification import missing_critical_fields
from app.llm.prompts import build_summary_prompt
from app.llm.provider import get_llm_provider
from app.rag.retrieval import retrieve_evidence
from app.reasoning.intervention_catalogue import INTERVENTION_CATALOGUE
from app.reasoning.rules import RuleResult, evaluate_rules

DIRECTION_MAP = {
    "soil_organic_carbon": "increase",
    "soil_moisture": "increase",
    "soil_biodiversity": "increase",
    "habitat_connectivity": "increase",
    "species_richness": "increase",
    "pollution_risk": "decrease",
}

METRIC_LABELS = {
    "soil_organic_carbon": "soil organic carbon",
    "soil_moisture": "soil moisture retention",
    "soil_biodiversity": "soil microbial and invertebrate biodiversity",
    "habitat_connectivity": "habitat connectivity",
    "species_richness": "species richness",
    "pollution_risk": "pollution risk",
}

METRIC_TO_MONITORING_FIELD = {
    "soil_organic_carbon": "soil_organic_carbon_percent",
    "soil_moisture": "soil_moisture_percent",
    "species_richness": "species_richness_index",
    "soil_biodiversity": "species_richness_index",
    "habitat_connectivity": "habitat_connectivity_index",
    "pollution_risk": "pollution_risk_index",
}

METRIC_EXPLANATIONS: dict[tuple[str, str], str] = {
    ("legume_cover_crops", "soil_organic_carbon"): (
        "Legume roots and retained crop residue add organic matter and fix nitrogen, "
        "building soil organic carbon over successive growing seasons."
    ),
    ("legume_cover_crops", "soil_moisture"): (
        "Cover crop canopy and residue reduce evaporation and improve infiltration, "
        "helping soil retain moisture between irregular rainfall events."
    ),
    ("agroforestry", "soil_moisture"): (
        "Tree root systems and canopy shade reduce evapotranspiration losses and "
        "improve water infiltration."
    ),
    ("agroforestry", "habitat_connectivity"): (
        "Scattered or hedgerow trees add vertical structure that many species use as "
        "stepping-stone habitat between larger patches."
    ),
    ("habitat_corridor_restoration", "habitat_connectivity"): (
        "Restored native vegetation strips physically reconnect isolated patches, "
        "reducing the distance and risk associated with cross-habitat movement."
    ),
    ("habitat_corridor_restoration", "species_richness"): (
        "Reconnected habitat allows species to recolonise patches and access a wider "
        "range of foraging and breeding resources."
    ),
    ("pollinator_strips", "species_richness"): (
        "Native flowering strips provide nectar, pollen and nesting resources that "
        "directly support pollinator abundance and diversity."
    ),
    ("mangrove_buffer_restoration", "habitat_connectivity"): (
        "A replanted mangrove buffer reconnects fragmented tidal habitat and restores "
        "nursery grounds for fish and crustaceans."
    ),
    ("mangrove_buffer_restoration", "soil_organic_carbon"): (
        "Mangrove root systems trap and store organic sediment, rebuilding blue-carbon "
        "stocks in the substrate."
    ),
    ("mangrove_buffer_restoration", "pollution_risk"): (
        "Root networks filter land-based runoff before it reaches open water, lowering "
        "pollutant and sediment loads."
    ),
    ("pollution_control_monitoring", "pollution_risk"): (
        "Dedicated monitoring zones make it possible to detect and respond to plastic, "
        "effluent, or aquaculture-related contamination before it spreads."
    ),
    ("riparian_buffer_restoration", "pollution_risk"): (
        "Vegetated riparian buffers intercept sediment and nutrient runoff before it "
        "reaches waterways."
    ),
    ("erosion_control_ground_cover", "soil_moisture"): (
        "Ground cover roots stabilise topsoil and slow surface runoff, keeping more "
        "rainfall infiltrating rather than washing away."
    ),
    ("integrated_pest_management", "species_richness"): (
        "Reducing routine pesticide applications lowers non-target mortality for "
        "pollinators and soil invertebrates."
    ),
    ("integrated_pest_management", "pollution_risk"): (
        "Lower and more targeted chemical use reduces agrochemical runoff into soil "
        "and adjacent water bodies."
    ),
    ("rainwater_harvesting", "soil_moisture"): (
        "Captured rainwater released gradually during dry spells keeps soil moisture "
        "more stable despite irregular rainfall."
    ),
    ("wetland_restoration", "habitat_connectivity"): (
        "Re-flooding and revegetating drained wetland reconnects hydrological flow "
        "paths that many wetland-dependent species rely on."
    ),
}

GENERIC_METRIC_EXPLANATION = (
    "{intervention} is expected to influence {metric} through the mechanisms "
    "described in the scientific reasoning above."
)

IMPLEMENTATION_NOTES: dict[str, list[str]] = {
    "mangrove_buffer_restoration": [
        "Match species (e.g. Avicennia, Rhizophora, Sonneratia) to the site's tidal inundation and salinity zone.",
        "Prioritise replanting the most fragmented remaining patches first to maximise connectivity gains.",
        "Coordinate with local aquaculture operators on buffer easements where expansion is encroaching.",
    ],
    "habitat_corridor_restoration": [
        "Map existing habitat patches and identify the shortest viable corridor alignment between them.",
        "Use native, locally-sourced species for corridor planting to avoid introducing invasive competitors.",
    ],
    "pollinator_strips": [
        "Select a mix of native flowering species with staggered bloom times for season-long forage.",
        "Site strips along field margins or between plots to minimise loss of production area.",
    ],
    "legume_cover_crops": [
        "Select legume species suited to local rainfall and soil pH.",
        "Retain residue on the surface after termination rather than removing or burning it.",
    ],
    "agroforestry": [
        "Choose tree species compatible with existing crops for light and root competition.",
        "Stagger planting to phase in canopy cover without disrupting current yields.",
    ],
    "riparian_buffer_restoration": [
        "Establish a minimum vegetated buffer width appropriate to slope and waterway size.",
        "Use deep-rooted native species to stabilise banks.",
    ],
    "rainwater_harvesting": [
        "Size retention structures to typical dry-spell duration observed at the site.",
        "Position structures to also recharge shallow groundwater where feasible.",
    ],
    "integrated_pest_management": [
        "Establish pest monitoring thresholds before defaulting to chemical treatment.",
        "Introduce beneficial-insect habitat alongside reduced spraying.",
    ],
    "erosion_control_ground_cover": [
        "Prioritise slopes and bare patches with visible rilling or sediment loss.",
        "Use fast-establishing native groundcover species for early-season protection.",
    ],
    "pollution_control_monitoring": [
        "Set up recurring water-quality and solid-waste sampling points near sensitive habitat.",
        "Log findings against a baseline so trends are detectable over time.",
    ],
    "wetland_restoration": [
        "Assess and, where possible, restore natural hydrological inflow before revegetating.",
        "Use native hydrophytic species matched to the wetland's original composition.",
    ],
}

NO_NUMERIC_ESTIMATE_SENTENCE = (
    "A site-specific numerical estimate is not provided because the retrieved evidence "
    "does not establish one for these conditions."
)


def _variables_considered(data: dict) -> list[str]:
    out = []
    for key, value in data.items():
        if value is None or value == [] or value == "":
            continue
        out.append(f"{key}: {value}")
    return out


def _risk_level(rule_count: int, enough_data: bool) -> str:
    if rule_count >= 4:
        return "critical"
    if rule_count >= 2:
        return "high"
    if rule_count == 1:
        return "medium"
    return "low" if enough_data else "medium"


def _confidence(rule_count: int, missing_fields: list[str], avg_evidence_score: float, has_any_evidence: bool) -> tuple[float, str]:
    base = 0.5 + 0.1 * min(rule_count, 4)
    deduction = 0.08 * len(missing_fields)
    evidence_penalty = 0.0
    notes = []
    if not has_any_evidence:
        evidence_penalty = 0.15
        notes.append("no retrieved evidence matched the activated rules")
    elif avg_evidence_score < 0.35:
        evidence_penalty = 0.08
        notes.append("retrieved evidence had low relevance scores")
    confidence = max(0.15, min(0.95, round(base - deduction - evidence_penalty, 2)))
    explanation_parts = [f"{rule_count} reasoning rule(s) activated"]
    if missing_fields:
        explanation_parts.append(f"{len(missing_fields)} critical field(s) missing ({', '.join(missing_fields)})")
    else:
        explanation_parts.append("all critical fields were provided")
    if notes:
        explanation_parts.append(", ".join(notes))
    return confidence, "; ".join(explanation_parts) + "."


def run_assessment(data: dict) -> dict:
    """data: a plain dict of AssessmentCreate fields (already validated)."""
    triggered_rules: list[RuleResult] = evaluate_rules(data)
    missing_fields = missing_critical_fields(data)
    enough_data = len(missing_fields) <= 2

    reasoning_trace: list[str] = []
    variables = _variables_considered(data)
    reasoning_trace.append(f"Variables detected ({len(variables)}): " + "; ".join(variables) if variables else "Variables detected: none")

    all_signals = sorted({s for r in triggered_rules for s in r.signals})
    reasoning_trace.append(
        "Risk signals identified: " + (", ".join(all_signals) if all_signals else "none met the activation threshold")
    )

    if triggered_rules:
        for r in triggered_rules:
            reasoning_trace.append(f"Rule activated [{r.rule_id}] {r.name} — variables used: {', '.join(r.variables_used)}.")
    else:
        reasoning_trace.append("No multi-metric rule reached its activation threshold with the provided data.")

    # Aggregate interventions across triggered rules.
    intervention_support: dict[str, dict] = {}
    for rule in triggered_rules:
        for key in rule.interventions:
            entry = intervention_support.setdefault(
                key, {"rule_ids": [], "explanations": [], "query_terms": set(), "metrics_affected": set()}
            )
            entry["rule_ids"].append(rule.rule_id)
            entry["explanations"].append(rule.explanation)
            entry["query_terms"].update(rule.query_terms)
            entry["metrics_affected"].update(rule.metrics_affected)

    if not intervention_support:
        # Fallback baseline recommendation so the plan is never empty.
        intervention_support["pollution_control_monitoring"] = {
            "rule_ids": [],
            "explanations": [
                "No specific multi-metric risk pattern was triggered by the provided data; "
                "a baseline monitoring program is recommended to establish trend data before "
                "targeted interventions are prioritised."
            ],
            "query_terms": {"ecosystem monitoring", "baseline biodiversity monitoring"},
            "metrics_affected": {"pollution_risk"},
        }

    ecosystem_type = data.get("ecosystem_type") or data.get("land_use")

    recommendations = []
    evidence_scores: list[float] = []
    any_evidence = False
    evidence_by_intervention: dict[str, list[dict]] = {}

    for key, support in intervention_support.items():
        catalogue_entry = INTERVENTION_CATALOGUE.get(key)
        if catalogue_entry is None:
            continue
        query = " ".join(support["query_terms"]) or catalogue_entry.name
        evidence = retrieve_evidence(
            query=f"{query} {ecosystem_type or ''}".strip(),
            ecosystem_type=ecosystem_type,
            metrics=list(support["metrics_affected"] or catalogue_entry.typical_metrics),
            top_k=3,
        )
        evidence_by_intervention[key] = evidence
        if evidence:
            any_evidence = True
            evidence_scores.extend(e["relevance_score"] for e in evidence)

        # Only claim metrics this specific intervention plausibly affects: intersect what
        # the supporting rule(s) flagged with the catalogue's typical metrics for this
        # action, rather than the full union across every rule that happened to recommend it.
        relevant_metrics = support["metrics_affected"] & set(catalogue_entry.typical_metrics)
        metrics_for_this = sorted(relevant_metrics or catalogue_entry.typical_metrics)
        impacted_metrics = []
        for metric in metrics_for_this:
            explanation = METRIC_EXPLANATIONS.get(
                (key, metric),
                GENERIC_METRIC_EXPLANATION.format(intervention=catalogue_entry.name, metric=METRIC_LABELS.get(metric, metric)),
            )
            impacted_metrics.append(
                {
                    "metric": METRIC_LABELS.get(metric, metric),
                    "expected_direction": DIRECTION_MAP.get(metric, "stabilise"),
                    "explanation": explanation,
                }
            )

        limitations = [
            "Based on rule-based reasoning over the submitted variables and retrieved evidence; "
            "not a substitute for an on-site ecological survey.",
            NO_NUMERIC_ESTIMATE_SENTENCE,
        ]
        if not evidence:
            limitations.append(
                "No directly matching evidence was retrieved from the knowledge base for this "
                "specific action; the recommendation rests on the deterministic reasoning rules only."
            )
        if missing_fields:
            limitations.append(
                f"Assessment completeness is limited: {', '.join(missing_fields)} not provided."
            )

        reasoning_text = " ".join(dict.fromkeys(support["explanations"]))

        recommendations.append(
            {
                "intervention_key": key,
                "action": catalogue_entry.name,
                "scientific_reasoning": reasoning_text,
                "impacted_metrics": impacted_metrics,
                "time_horizon": catalogue_entry.default_time_horizon,
                "implementation_notes": IMPLEMENTATION_NOTES.get(key, []),
                "evidence": [
                    {
                        "source_id": e["source_id"],
                        "title": e["title"],
                        "organization": e["organization"],
                        "year": e["year"],
                        "url": e["url"],
                        "retrieval_score": e["relevance_score"],
                    }
                    for e in evidence
                ],
                "limitations": limitations,
                "_rank_key": (-len(support["rule_ids"]), -(sum(e["relevance_score"] for e in evidence) / len(evidence)) if evidence else 0),
            }
        )
        reasoning_trace.append(
            f"Retrieved {len(evidence)} evidence chunk(s) for '{catalogue_entry.name}'"
            + (f" (top score {max(e['relevance_score'] for e in evidence):.2f})" if evidence else " (none matched)")
        )

    recommendations.sort(key=lambda r: r["_rank_key"])
    for i, rec in enumerate(recommendations, start=1):
        rec["priority"] = i
        del rec["_rank_key"]
        del rec["intervention_key"]

    reasoning_trace.append(
        "Ranking rationale: interventions supported by more activated rules are ranked first; "
        "ties are broken by average retrieved-evidence relevance score."
    )

    avg_evidence_score = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.0
    confidence, confidence_explanation = _confidence(
        len(triggered_rules), missing_fields, avg_evidence_score, any_evidence
    )
    risk_level = _risk_level(len(triggered_rules), enough_data)

    follow_up_metrics = sorted(
        {
            METRIC_TO_MONITORING_FIELD[m]
            for support in intervention_support.values()
            for m in support["metrics_affected"]
            if m in METRIC_TO_MONITORING_FIELD
        }
    )

    summary = _build_summary(data, triggered_rules, risk_level)
    llm = get_llm_provider()
    if llm.enabled:
        system_prompt, user_prompt = build_summary_prompt(data, reasoning_trace, evidence_by_intervention)
        polished = llm.generate_text(system_prompt, user_prompt)
        if polished:
            summary = polished

    return {
        "assessment_summary": summary,
        "biodiversity_risk_level": risk_level,
        "confidence": confidence,
        "confidence_explanation": confidence_explanation,
        "variables_considered": variables,
        "reasoning_trace": reasoning_trace,
        "recommendations": recommendations,
        "follow_up_monitoring_metrics": follow_up_metrics,
        "missing_critical_fields": missing_fields,
    }


def _build_summary(data: dict, triggered_rules: list[RuleResult], risk_level: str) -> str:
    location = data.get("location_name") or "the assessed site"
    ecosystem = data.get("ecosystem_type") or data.get("land_use") or "ecosystem"
    if triggered_rules:
        signal_summary = "; ".join(r.name for r in triggered_rules[:3])
        return (
            f"{location} ({ecosystem}) shows a {risk_level} biodiversity risk profile. "
            f"Key patterns identified: {signal_summary}. "
            f"{len(triggered_rules)} multi-metric rule(s) activated across the submitted variables, "
            "producing the ranked recommendations below."
        )
    return (
        f"{location} ({ecosystem}) shows a {risk_level} biodiversity risk profile based on the "
        "variables provided. No high-confidence multi-metric risk pattern was triggered; the "
        "recommendation below is a baseline monitoring step pending more complete data."
    )
