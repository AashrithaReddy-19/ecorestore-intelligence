"""SQLAlchemy ORM models.

Relationships (documented in full in README.md "Database schema" section):

  Assessment 1--1 EnvironmentalMetrics
  Assessment 1--N Recommendation
  Assessment 1--1 MRVBaseline
  MRVBaseline 1--N MRVObservation
  Conversation 1--N ConversationMessage
  Conversation N--1 Assessment (optional link)
  EvidenceSource 1--N EvidenceChunk
  Recommendation N--N EvidenceSource (via RecommendationEvidence association)
  InterventionCatalogue 1--N Recommendation (an intervention may be recommended many times)
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    ecosystem_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    land_use: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_input: Mapped[dict] = mapped_column(JSON, default=dict)
    latest_result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    metrics: Mapped["EnvironmentalMetric"] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    mrv_baseline: Mapped["MRVBaseline"] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )


class EnvironmentalMetric(Base):
    __tablename__ = "environmental_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"), unique=True)

    soil_organic_carbon_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_moisture_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_salinity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rainfall_pattern: Mapped[str | None] = mapped_column(String(100), nullable=True)
    temperature_trend: Mapped[str | None] = mapped_column(String(100), nullable=True)
    habitat_fragmentation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    human_impact: Mapped[list] = mapped_column(JSON, default=list)
    species_observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessment: Mapped["Assessment"] = relationship(back_populates="metrics")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    assessment_id: Mapped[str | None] = mapped_column(
        ForeignKey("assessments.id"), nullable=True
    )
    memory_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    collected_facts: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(20))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    retrieved_evidence: Mapped[list] = mapped_column(JSON, default=list)
    follow_up_questions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    organization: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500))
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str] = mapped_column(String(1000))
    topic_tags: Mapped[list] = mapped_column(JSON, default=list)
    ecosystem_tags: Mapped[list] = mapped_column(JSON, default=list)
    claim: Mapped[str] = mapped_column(Text)
    conditions: Mapped[list] = mapped_column(JSON, default=list)
    metrics_affected: Mapped[list] = mapped_column(JSON, default=list)

    chunks: Mapped[list["EvidenceChunk"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class EvidenceChunk(Base):
    __tablename__ = "evidence_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chunk_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("evidence_sources.source_id"))
    evidence_text: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)

    source: Mapped["EvidenceSource"] = relationship(back_populates="chunks")


class InterventionCatalogue(Base):
    __tablename__ = "intervention_catalogue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    intervention_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    default_time_horizon: Mapped[str] = mapped_column(String(20))
    typical_metrics: Mapped[list] = mapped_column(JSON, default=list)
    typical_ecosystems: Mapped[list] = mapped_column(JSON, default=list)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"))
    intervention_key: Mapped[str] = mapped_column(
        ForeignKey("intervention_catalogue.intervention_key")
    )
    priority: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(255))
    scientific_reasoning: Mapped[str] = mapped_column(Text)
    impacted_metrics: Mapped[list] = mapped_column(JSON, default=list)
    time_horizon: Mapped[str] = mapped_column(String(20))
    implementation_notes: Mapped[list] = mapped_column(JSON, default=list)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    limitations: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assessment: Mapped["Assessment"] = relationship(back_populates="recommendations")


class MRVBaseline(Base):
    __tablename__ = "mrv_baselines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"), unique=True)
    soil_organic_carbon_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_moisture_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    species_richness_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    habitat_connectivity_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    pollution_risk_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assessment: Mapped["Assessment"] = relationship(back_populates="mrv_baseline")
    observations: Mapped[list["MRVObservation"]] = relationship(
        back_populates="baseline",
        cascade="all, delete-orphan",
        order_by="MRVObservation.observed_at",
    )


class MRVObservation(Base):
    __tablename__ = "mrv_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    baseline_id: Mapped[str] = mapped_column(ForeignKey("mrv_baselines.id"))
    soil_organic_carbon_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_moisture_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    species_richness_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    habitat_connectivity_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    pollution_risk_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    baseline: Mapped["MRVBaseline"] = relationship(back_populates="observations")
