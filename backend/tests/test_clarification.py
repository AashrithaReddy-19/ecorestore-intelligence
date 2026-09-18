from app.chat.clarification import (
    build_clarifying_questions,
    format_clarifying_message,
    has_enough_for_assessment,
    missing_critical_fields,
)
from app.chat.memory import extract_facts_from_text, merge_facts


def test_missing_fields_detected_on_empty_input():
    missing = missing_critical_fields({})
    assert "ecosystem_type" in missing
    assert "rainfall_pattern" in missing
    assert "human_impact" in missing


def test_max_three_questions_per_turn():
    questions = build_clarifying_questions({})
    assert len(questions) <= 3


def test_clarifying_message_matches_required_style():
    questions = build_clarifying_questions({})
    message = format_clarifying_message(questions)
    assert message.startswith("To make an evidence-grounded assessment, please share:")
    assert "1." in message


def test_has_enough_for_assessment_threshold():
    assert not has_enough_for_assessment({"ecosystem_type": "mangrove"})
    assert has_enough_for_assessment(
        {"ecosystem_type": "mangrove", "rainfall_pattern": "irregular", "habitat_fragmentation": "high"}
    )


def test_extract_facts_from_vague_text_declining_biodiversity():
    facts = extract_facts_from_text("Biodiversity is declining on my land.")
    # Vague text alone should not fabricate structured fields it has no evidence for.
    assert "ecosystem_type" not in facts
    assert "rainfall_pattern" not in facts


def test_extract_facts_from_descriptive_text():
    facts = extract_facts_from_text(
        "This is a mangrove site with irregular rainfall and pesticide use nearby; bird activity is low."
    )
    assert facts.get("ecosystem_type") == "mangrove"
    assert facts.get("rainfall_pattern") == "irregular"
    assert "pesticide" in facts.get("human_impact", [])
    assert "bird" in facts.get("species_observations", "").lower()


def test_merge_facts_unions_lists_and_keeps_existing_scalars():
    existing = {"ecosystem_type": "mangrove", "human_impact": ["pollution"]}
    new = {"human_impact": ["aquaculture"], "rainfall_pattern": "irregular"}
    merged = merge_facts(existing, new)
    assert merged["ecosystem_type"] == "mangrove"
    assert set(merged["human_impact"]) == {"pollution", "aquaculture"}
    assert merged["rainfall_pattern"] == "irregular"
