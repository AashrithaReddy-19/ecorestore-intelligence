from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.chat.clarification import (
    build_clarifying_questions,
    format_clarifying_message,
    has_enough_for_assessment,
    missing_critical_fields,
)
from app.chat.memory import extract_facts_from_text, merge_facts, summarize_memory
from app.database import get_db
from app.llm.prompts import build_chat_reply_prompt
from app.llm.provider import get_llm_provider
from app.rag.retrieval import retrieve_evidence
from app.reasoning.engine import run_assessment
from app.routers.assessments import _to_response

router = APIRouter(prefix="/api", tags=["chat"])

ASSESSMENT_CREATE_FIELDS = set(schemas.AssessmentCreate.model_fields.keys())


@router.post("/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    conversation = crud.get_or_create_conversation(db, payload.conversation_id)

    text_facts = extract_facts_from_text(payload.message)
    structured_facts = payload.structured_data.model_dump() if payload.structured_data else {}
    merged = merge_facts(conversation.collected_facts, text_facts)
    merged = merge_facts(merged, structured_facts)

    crud.add_message(db, conversation.id, "user", payload.message)

    if not has_enough_for_assessment(merged):
        questions = build_clarifying_questions(merged)
        reply = format_clarifying_message(questions)
        general_evidence = retrieve_evidence(
            query=payload.message, ecosystem_type=merged.get("ecosystem_type"), top_k=2
        )
        crud.add_message(
            db, conversation.id, "assistant", reply,
            retrieved_evidence=general_evidence, follow_up_questions=questions,
        )
        summary = summarize_memory(merged)
        crud.update_conversation_memory(db, conversation, merged, summary)
        return schemas.ChatResponse(
            conversation_id=conversation.id,
            reply=reply,
            follow_up_questions=questions,
            retrieved_evidence=[
                schemas.EvidenceRef(
                    source_id=e["source_id"], title=e["title"], organization=e["organization"],
                    year=e["year"], url=e["url"], retrieval_score=e["relevance_score"],
                )
                for e in general_evidence
            ],
            memory_summary=summary,
            collected_facts=merged,
            assessment=None,
        )

    assessment_payload = schemas.AssessmentCreate(
        **{k: v for k, v in merged.items() if k in ASSESSMENT_CREATE_FIELDS}
    )
    assessment = crud.create_assessment(db, assessment_payload)
    result = run_assessment(assessment_payload.model_dump())
    crud.save_recommendations(db, assessment.id, result["recommendations"])
    assessment.latest_result = result
    conversation.assessment_id = assessment.id
    db.add(assessment)
    db.commit()

    flat_evidence = []
    seen = set()
    for rec in result["recommendations"]:
        for e in rec["evidence"]:
            if e["source_id"] in seen:
                continue
            seen.add(e["source_id"])
            flat_evidence.append(e)

    top_rec = result["recommendations"][0] if result["recommendations"] else None
    reply = (
        f"{result['assessment_summary']} "
        + (f"Top recommendation: {top_rec['action']} ({top_rec['time_horizon']}-term). " if top_rec else "")
        + "See the Recovery Plan tab for the full ranked plan with evidence and limitations."
    )

    llm = get_llm_provider()
    if llm.enabled:
        system_prompt, user_prompt = build_chat_reply_prompt(
            payload.message, merged, flat_evidence, result["reasoning_trace"]
        )
        polished = llm.generate_text(system_prompt, user_prompt)
        if polished:
            reply = polished

    remaining_missing = missing_critical_fields(merged)
    follow_up_questions = build_clarifying_questions(merged) if remaining_missing else []

    crud.add_message(
        db, conversation.id, "assistant", reply,
        retrieved_evidence=flat_evidence, follow_up_questions=follow_up_questions,
    )
    summary = summarize_memory(merged)
    crud.update_conversation_memory(db, conversation, merged, summary)

    return schemas.ChatResponse(
        conversation_id=conversation.id,
        reply=reply,
        follow_up_questions=follow_up_questions,
        retrieved_evidence=[
            schemas.EvidenceRef(
                source_id=e["source_id"], title=e["title"], organization=e["organization"],
                year=e["year"], url=e["url"], retrieval_score=e["retrieval_score"],
            )
            for e in flat_evidence
        ],
        memory_summary=summary,
        collected_facts=merged,
        assessment=_to_response(assessment.id, result),
    )


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationOut)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return schemas.ConversationOut(
        id=conversation.id,
        memory_summary=conversation.memory_summary,
        collected_facts=conversation.collected_facts,
        messages=[
            schemas.ChatMessageOut(
                role=m.role, content=m.content, retrieved_evidence=m.retrieved_evidence,
                follow_up_questions=m.follow_up_questions, created_at=m.created_at,
            )
            for m in conversation.messages
        ],
    )
