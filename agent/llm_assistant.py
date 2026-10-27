import json
import re
import ollama


STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "do", "does", "did", "can", "could", "would", "should",
    "will", "may", "might", "please", "you", "your", "we", "our",
    "i", "me", "my", "it", "its", "this", "that", "these", "those",
    "to", "of", "for", "from", "in", "on", "at", "by", "with",
    "and", "or", "but", "if", "then", "than", "as", "what", "when",
    "where", "why", "how", "which", "who", "whom", "provide",
    "explain", "clarify", "confirm", "supporting", "documentation",
    "information", "regarding", "related", "about", "any", "there",
    "specific", "following", "actual", "supplied", "shown",
}

FORBIDDEN_TOPICS = {
    "approve", "approved", "approval",
    "reject", "rejected", "rejection",
    "creditworthiness",
}


def _tokens(text: str) -> set:
    """Convert text into meaningful lowercase tokens."""
    words = re.findall(r"[a-z0-9]+", str(text).lower())
    return {
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    }


def _is_grounded(question: str, findings: list) -> bool:
    """Check whether a question relates to a verified finding."""
    question_tokens = _tokens(question)

    if question_tokens & FORBIDDEN_TOPICS:
        return False

    finding_tokens = set()
    for finding in findings:
        finding_tokens.update(_tokens(finding))

    return bool(question_tokens & finding_tokens)


def _clean_questions(questions: list, findings: list) -> list:
    """Validate and deduplicate questions, limiting output to three."""
    cleaned = []
    seen = set()

    for question in questions:
        if not isinstance(question, str):
            continue

        question = question.strip()

        if not question or len(question) > 300:
            continue

        if not _is_grounded(question, findings):
            continue

        normalized = " ".join(question.lower().split())

        if normalized in seen:
            continue

        seen.add(normalized)
        cleaned.append(question)

        if len(cleaned) >= 3:
            break

    return cleaned


def generate_reviewer_questions(
    findings: list,
    existing_questions: list,
) -> list:
    """Generate reviewer questions without making loan decisions."""

    fallback = list(dict.fromkeys(
        question.strip()
        for question in existing_questions
        if isinstance(question, str) and question.strip()
    ))

    if not findings:
        return fallback

    prompt_data = {
        "verified_findings": findings,
        "existing_questions": fallback,
    }

    system_prompt = """
You assist a human reviewer of synthetic loan applications.

1. Use only facts explicitly stated in verified findings.
2. Never assume why a discrepancy occurred.
3. Do not invent facts or calculate financial figures.
4. Ask concise clarification or documentation questions.
5. Never approve or reject a loan or assess creditworthiness.
6. Return at most three distinct questions.
7. Return valid JSON with a "questions" list of strings.
"""

    try:
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        prompt_data,
                        ensure_ascii=False,
                    ),
                },
            ],
            format="json",
            options={
                "temperature": 0,
                "num_predict": 250,
            },
        )

        content = response["message"]["content"]
        result = json.loads(content)

        if not isinstance(result, dict):
            return fallback

        generated = result.get("questions")

        if not isinstance(generated, list):
            return fallback

        validated = _clean_questions(generated, findings)

        return validated if validated else fallback

    except Exception:
        # Keep the application usable if Ollama fails.
        return fallback
