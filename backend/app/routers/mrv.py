from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/mrv", tags=["mrv"])

METRIC_FIELDS = [
    ("soil_organic_carbon_percent", "Soil organic carbon (%)"),
    ("soil_moisture_percent", "Soil moisture (%)"),
    ("species_richness_index", "Species richness index"),
    ("habitat_connectivity_index", "Habitat connectivity index"),
    ("pollution_risk_index", "Pollution risk index (lower is better)"),
]
LOWER_IS_BETTER = {"pollution_risk_index"}


@router.post("/baselines", response_model=dict)
def create_baseline(payload: schemas.MRVBaselineCreate, db: Session = Depends(get_db)):
    assessment = crud.get_assessment(db, payload.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    baseline = crud.create_mrv_baseline(db, payload)
    return {"baseline_id": baseline.id, "assessment_id": baseline.assessment_id}


@router.post("/observations", response_model=dict)
def create_observation(payload: schemas.MRVObservationCreate, db: Session = Depends(get_db)):
    observation = crud.add_mrv_observation(db, payload)
    return {"observation_id": observation.id, "baseline_id": observation.baseline_id}


@router.get("/{assessment_id}", response_model=schemas.MRVTrackerOut)
def get_mrv(assessment_id: str, db: Session = Depends(get_db)):
    baseline = crud.get_mrv_for_assessment(db, assessment_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="No baseline recorded for this assessment yet")

    latest_observation = baseline.observations[-1] if baseline.observations else None

    comparisons: list[schemas.MRVMetricComparison] = []
    for field, label in METRIC_FIELDS:
        baseline_value = getattr(baseline, field)
        latest_value = getattr(latest_observation, field) if latest_observation else None
        delta = None
        trend = "insufficient_data"
        if baseline_value is not None and latest_value is not None:
            delta = round(latest_value - baseline_value, 3)
            if abs(delta) < 1e-9:
                trend = "no_change"
            elif field in LOWER_IS_BETTER:
                trend = "improved" if delta < 0 else "declined"
            else:
                trend = "improved" if delta > 0 else "declined"
        comparisons.append(
            schemas.MRVMetricComparison(
                metric=label, baseline_value=baseline_value, latest_value=latest_value,
                delta=delta, trend=trend,
            )
        )

    if not baseline.observations:
        summary = (
            "Only a baseline has been recorded. No follow-up observation exists yet, so no "
            "improvement or decline can be claimed for this site."
        )
    else:
        improved = sum(1 for c in comparisons if c.trend == "improved")
        declined = sum(1 for c in comparisons if c.trend == "declined")
        summary = (
            f"Comparing baseline to the latest of {len(baseline.observations)} follow-up "
            f"observation(s): {improved} metric(s) improved, {declined} declined, based on "
            "entered values only."
        )

    return schemas.MRVTrackerOut(
        assessment_id=assessment_id,
        baseline={
            "recorded_at": baseline.recorded_at,
            **{f: getattr(baseline, f) for f, _ in METRIC_FIELDS},
            "notes": baseline.notes,
        },
        observations=[
            {
                "observed_at": obs.observed_at,
                **{f: getattr(obs, f) for f, _ in METRIC_FIELDS},
                "notes": obs.notes,
            }
            for obs in baseline.observations
        ],
        comparisons=comparisons,
        summary=summary,
    )
