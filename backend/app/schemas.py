"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TimeHorizon(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class Direction(str, Enum):
    increase = "increase"
    decrease = "decrease"
    stabilise = "stabilise"


# ---------------------------------------------------------------------------
# Assessment input
# ---------------------------------------------------------------------------


class AssessmentCreate(BaseModel):
    location_name: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    ecosystem_type: str | None = None
    land_use: str | None = None
    soil_organic_carbon_percent: float | None = Field(default=None, ge=0, le=100)
    soil_ph: float | None = Field(default=None, ge=0, le=14)
    soil_moisture_percent: float | None = Field(default=None, ge=0, le=100)
    soil_salinity: str | None = None
    rainfall_pattern: str | None = None
    temperature_trend: str | None = None
    habitat_fragmentation: str | None = None
    human_impact: list[str] = Field(default_factory=list)
    species_observations: str | None = None

    @field_validator("human_impact", mode="before")
    @classmethod
    def _coerce_human_impact(cls, v: Any) -> Any:
        if v is None:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


class EvidenceRef(BaseModel):
    source_id: str
    title: str
    organization: str
    year: int | None = None
    url: str
    retrieval_score: float


class ImpactedMetric(BaseModel):
    metric: str
    expected_direction: Direction
    explanation: str


class Recommendation(BaseModel):
    priority: int
    action: str
    scientific_reasoning: str
    impacted_metrics: list[ImpactedMetric]
    time_horizon: TimeHorizon
    implementation_notes: list[str]
    evidence: list[EvidenceRef]
    limitations: list[str]


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assessment_id: str
    assessment_summary: str
    biodiversity_risk_level: RiskLevel
    confidence: float
    confidence_explanation: str
    variables_considered: list[str]
    reasoning_trace: list[str]
    recommendations: list[Recommendation]
    follow_up_monitoring_metrics: list[str]
    missing_critical_fields: list[str] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    structured_data: AssessmentCreate | None = None


class ChatMessageOut(BaseModel):
    role: str
    content: str
    retrieved_evidence: list[dict] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    follow_up_questions: list[str] = Field(default_factory=list)
    retrieved_evidence: list[EvidenceRef] = Field(default_factory=list)
    memory_summary: str
    collected_facts: dict[str, Any]
    assessment: AssessmentResponse | None = None


class ConversationOut(BaseModel):
    id: str
    memory_summary: str | None
    collected_facts: dict[str, Any]
    messages: list[ChatMessageOut]


# ---------------------------------------------------------------------------
# Evidence search
# ---------------------------------------------------------------------------


class EvidenceSearchResult(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    organization: str
    year: int | None
    url: str
    evidence_text: str
    relevance_score: float


# ---------------------------------------------------------------------------
# MRV
# ---------------------------------------------------------------------------


class MRVBaselineCreate(BaseModel):
    assessment_id: str
    soil_organic_carbon_percent: float | None = None
    soil_moisture_percent: float | None = None
    species_richness_index: float | None = Field(default=None, ge=0, le=100)
    habitat_connectivity_index: float | None = Field(default=None, ge=0, le=100)
    pollution_risk_index: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class MRVObservationCreate(BaseModel):
    baseline_id: str
    soil_organic_carbon_percent: float | None = None
    soil_moisture_percent: float | None = None
    species_richness_index: float | None = Field(default=None, ge=0, le=100)
    habitat_connectivity_index: float | None = Field(default=None, ge=0, le=100)
    pollution_risk_index: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class MRVMetricComparison(BaseModel):
    metric: str
    baseline_value: float | None
    latest_value: float | None
    delta: float | None
    trend: str  # "improved" | "declined" | "no_change" | "insufficient_data"


class MRVTrackerOut(BaseModel):
    assessment_id: str
    baseline: dict[str, Any]
    observations: list[dict[str, Any]]
    comparisons: list[MRVMetricComparison]
    summary: str
