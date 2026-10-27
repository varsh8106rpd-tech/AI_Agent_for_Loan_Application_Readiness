
import json

from agent.llm_assistant import generate_reviewer_questions


def test_no_findings_preserves_existing_questions():
    existing = ["Please provide income proof."]

    result = generate_reviewer_questions([], existing)

    assert result == existing


def test_fallback_when_ollama_is_unavailable(monkeypatch):
    import agent.llm_assistant as assistant

    def fail_chat(**kwargs):
        raise RuntimeError("Ollama unavailable")

    monkeypatch.setattr(assistant.ollama, "chat", fail_chat)

    existing = ["Please clarify the income discrepancy."]

    result = assistant.generate_reviewer_questions(
        ["Declared income differs from recorded income."],
        existing,
    )

    assert result == existing


def test_malformed_json_uses_fallback(monkeypatch):
    import agent.llm_assistant as assistant

    def malformed_chat(**kwargs):
        return {"message": {"content": "not valid JSON"}}

    monkeypatch.setattr(assistant.ollama, "chat", malformed_chat)

    existing = ["Please provide supporting income records."]

    result = assistant.generate_reviewer_questions(
        ["Declared income differs from recorded income."],
        existing,
    )

    assert result == existing


def test_invalid_response_structure_uses_fallback(monkeypatch):
    import agent.llm_assistant as assistant

    def invalid_chat(**kwargs):
        return {
            "message": {
                "content": json.dumps({"questions": "not a list"})
            }
        }

    monkeypatch.setattr(assistant.ollama, "chat", invalid_chat)

    existing = ["Please clarify the income discrepancy."]

    result = assistant.generate_reviewer_questions(
        ["Declared income differs from recorded income."],
        existing,
    )

    assert result == existing



def test_duplicate_questions_are_removed(monkeypatch):
    import json
    import agent.llm_assistant as assistant

    def duplicate_chat(**kwargs):
        return {
            "message": {
                "content": json.dumps({
                    "questions": [
                        "Could you clarify the income discrepancy?",
                        "Could you clarify the income discrepancy?",
                        "Could you confirm the recorded income?",
                    ]
                })
            }
        }

    monkeypatch.setattr(assistant.ollama, "chat", duplicate_chat)

    result = assistant.generate_reviewer_questions(
        ["Declared income differs from recorded income."],
        [],
    )

    assert result == [
        "Could you clarify the income discrepancy?",
        "Could you confirm the recorded income?",
    ]



def test_question_output_is_limited_to_three(monkeypatch):
    import agent.llm_assistant as assistant

    def excessive_chat(**kwargs):
        return {
            "message": {
                "content": json.dumps({
                    "questions": [
                        "Question one?",
                        "Question two?",
                        "Question three?",
                        "Question four?",
                        "Question five?",
                    ]
                })
            }
        }

    monkeypatch.setattr(assistant.ollama, "chat", excessive_chat)

    result = assistant.generate_reviewer_questions(
        ["Declared income differs from recorded income."],
        [],
    )

    assert len(result) <= 3
