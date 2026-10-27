
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
