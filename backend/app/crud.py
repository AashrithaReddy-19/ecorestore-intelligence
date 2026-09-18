"""Database CRUD helpers used by the routers."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app import models, schemas
from app.reasoning.intervention_catalogue import INTERVENTION_CATALOGUE

_KEY_BY_ACTION_NAME = {item.name: key for key, item in INTERVENTION_CATALOGUE.items()}


def create_assessment(db: Session, payload: schemas.AssessmentCreate) -> models.Assessment:
    assessment = models.Assessment(
        location_name=payload.location_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        ecosystem_type=payload.ecosystem_type,
        land_use=payload.land_use,
        raw_input=payload.model_dump(),
    )
    db.add(assessment)
    db.flush()

    metrics = models.EnvironmentalMetric(
        assessment_id=assessment.id,
        soil_organic_carbon_percent=payload.soil_organic_carbon_percent,
        soil_ph=payload.soil_ph,
        soil_moisture_percent=payload.soil_moisture_percent,
        soil_salinity=payload.soil_salinity,
        rainfall_pattern=payload.rainfall_pattern,
        temperature_trend=payload.temperature_trend,
        habitat_fragmentation=payload.habitat_fragmentation,
        human_impact=payload.human_impact,
        species_observations=payload.species_observations,
    )
    db.add(metrics)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db: Session, assessment_id: str) -> models.Assessment | None:
    return db.get(models.Assessment, assessment_id)


def save_recommendations(db: Session, assessment_id: str, recommendations: list[dict]) -> list[models.Recommendation]:
    db.query(models.Recommendation).filter_by(assessment_id=assessment_id).delete()
    saved = []
    for rec in recommendations:
        row = models.Recommendation(
            assessment_id=assessment_id,
            intervention_key=_KEY_BY_ACTION_NAME.get(rec["action"], "pollution_control_monitoring"),
            priority=rec["priority"],
            action=rec["action"],
            scientific_reasoning=rec["scientific_reasoning"],
            impacted_metrics=rec["impacted_metrics"],
            time_horizon=rec["time_horizon"],
            implementation_notes=rec["implementation_notes"],
            evidence=rec["evidence"],
            limitations=rec["limitations"],
        )
        db.add(row)
        saved.append(row)
    db.commit()
    return saved


def get_or_create_conversation(db: Session, conversation_id: str | None) -> models.Conversation:
    if conversation_id:
        convo = db.get(models.Conversation, conversation_id)
        if convo:
            return convo
    convo = models.Conversation(collected_facts={})
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


def add_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
    retrieved_evidence: list | None = None,
    follow_up_questions: list | None = None,
) -> models.ConversationMessage:
    message = models.ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        retrieved_evidence=retrieved_evidence or [],
        follow_up_questions=follow_up_questions or [],
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def update_conversation_memory(db: Session, conversation: models.Conversation, facts: dict, summary: str) -> None:
    conversation.collected_facts = facts
    conversation.memory_summary = summary
    db.add(conversation)
    db.commit()


def get_conversation(db: Session, conversation_id: str) -> models.Conversation | None:
    return db.get(models.Conversation, conversation_id)


def create_mrv_baseline(db: Session, payload: schemas.MRVBaselineCreate) -> models.MRVBaseline:
    existing = db.query(models.MRVBaseline).filter_by(assessment_id=payload.assessment_id).one_or_none()
    if existing:
        for field in (
            "soil_organic_carbon_percent", "soil_moisture_percent", "species_richness_index",
            "habitat_connectivity_index", "pollution_risk_index", "notes",
        ):
            setattr(existing, field, getattr(payload, field))
        db.commit()
        db.refresh(existing)
        return existing
    baseline = models.MRVBaseline(**payload.model_dump())
    db.add(baseline)
    db.commit()
    db.refresh(baseline)
    return baseline


def add_mrv_observation(db: Session, payload: schemas.MRVObservationCreate) -> models.MRVObservation:
    observation = models.MRVObservation(**payload.model_dump())
    db.add(observation)
    db.commit()
    db.refresh(observation)
    return observation


def get_mrv_for_assessment(db: Session, assessment_id: str) -> models.MRVBaseline | None:
    return db.query(models.MRVBaseline).filter_by(assessment_id=assessment_id).one_or_none()
