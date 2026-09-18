from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.reasoning.engine import run_assessment

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def _to_response(assessment_id: str, result: dict) -> schemas.AssessmentResponse:
    from app.chat.clarification import CRITICAL_FIELDS, MAX_QUESTIONS_PER_TURN

    missing = result["missing_critical_fields"]
    clarifying_questions = [CRITICAL_FIELDS[f] for f in missing[:MAX_QUESTIONS_PER_TURN] if f in CRITICAL_FIELDS]

    return schemas.AssessmentResponse(
        assessment_id=assessment_id,
        assessment_summary=result["assessment_summary"],
        biodiversity_risk_level=result["biodiversity_risk_level"],
        confidence=result["confidence"],
        confidence_explanation=result["confidence_explanation"],
        variables_considered=result["variables_considered"],
        reasoning_trace=result["reasoning_trace"],
        recommendations=result["recommendations"],
        follow_up_monitoring_metrics=result["follow_up_monitoring_metrics"],
        missing_critical_fields=missing,
        clarifying_questions=clarifying_questions,
    )


@router.post("", response_model=schemas.AssessmentResponse)
def create_assessment(payload: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    assessment = crud.create_assessment(db, payload)
    result = run_assessment(payload.model_dump())
    crud.save_recommendations(db, assessment.id, result["recommendations"])
    assessment.latest_result = result
    db.add(assessment)
    db.commit()
    return _to_response(assessment.id, result)


@router.get("/{assessment_id}", response_model=schemas.AssessmentResponse)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = crud.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if not assessment.latest_result:
        raise HTTPException(status_code=404, detail="Assessment has no computed result")
    return _to_response(assessment.id, assessment.latest_result)
