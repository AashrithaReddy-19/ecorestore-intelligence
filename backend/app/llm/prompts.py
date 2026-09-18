"""Prompt templates for the explanation-generation LLM step.

The LLM is never asked to decide *what* to recommend — that is fixed by the
deterministic rule engine. It is only asked to phrase the already-retrieved
evidence and already-activated rules as clear prose, under hard
grounding constraints.
"""
from __future__ import annotations

import json

SYSTEM_PROMPT = """You are an environmental scientist writing for a biodiversity \
restoration report. You will be given:
1. A deterministic reasoning trace (rules that fired over structured ecosystem data).
2. Retrieved evidence chunks with source metadata.
3. A required JSON output schema.

Rules you MUST follow:
- Never invent evidence, sources, organisations, URLs, studies, or numerical results.
- Only cite sources that appear in the provided retrieved evidence list.
- If no retrieved evidence supports a specific numeric estimate, say so explicitly using \
this exact sentence: "A site-specific numerical estimate is not provided because the \
retrieved evidence does not establish one for these conditions."
- If information is insufficient, state the uncertainty rather than guessing.
- Output must be valid JSON matching the schema you are given. No extra commentary.
"""


def build_summary_prompt(
    variables: dict,
    reasoning_trace: list[str],
    evidence_by_intervention: dict[str, list[dict]],
) -> tuple[str, str]:
    user_prompt = (
        "Ecosystem variables considered:\n"
        f"{json.dumps(variables, indent=2, default=str)}\n\n"
        "Deterministic reasoning trace (already computed, do not contradict it):\n"
        f"{json.dumps(reasoning_trace, indent=2)}\n\n"
        "Retrieved evidence grouped by intervention (only cite these):\n"
        f"{json.dumps(evidence_by_intervention, indent=2, default=str)}\n\n"
        "Write a 2-3 sentence plain-language assessment_summary describing the site's "
        "biodiversity risk situation, grounded only in the variables and reasoning trace "
        "above. Return ONLY the summary text, no JSON, no preamble."
    )
    return SYSTEM_PROMPT, user_prompt


def build_chat_reply_prompt(
    user_message: str,
    collected_facts: dict,
    retrieved_evidence: list[dict],
    reasoning_trace: list[str],
) -> tuple[str, str]:
    user_prompt = (
        f"User message: {user_message}\n\n"
        f"Facts collected so far this conversation: {json.dumps(collected_facts, default=str)}\n\n"
        f"Retrieved evidence (only cite these, by source_id/organization): "
        f"{json.dumps(retrieved_evidence, default=str)}\n\n"
        f"Deterministic reasoning trace: {json.dumps(reasoning_trace)}\n\n"
        "Write a concise, evidence-grounded conversational reply (max 5 sentences) as an "
        "environmental scientist. Reference retrieved evidence naturally where relevant. "
        "Do not invent facts. Return ONLY the reply text."
    )
    return SYSTEM_PROMPT, user_prompt
