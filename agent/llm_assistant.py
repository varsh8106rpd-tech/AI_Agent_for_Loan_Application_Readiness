
import json
import ollama


def generate_reviewer_questions(
    findings: list,
    existing_questions: list,
) -> list:
    """Generate concise, evidence-grounded reviewer questions."""

    fallback = list(dict.fromkeys(existing_questions))

    if not findings:
        return fallback

    prompt_data = {
        "verified_findings": findings,
        "existing_questions": fallback,
    }

    system_prompt = """
You are a cautious assistant supporting a human reviewer of
synthetic loan application documents.

Rules:
1. Use only facts explicitly present in the supplied findings.
2. Never assume a cause for a discrepancy.
3. Do not speculate about bonuses, job changes, layoffs,
   future income, or other circumstances unless explicitly
   stated in the findings.
4. Ask for clarification or supporting documentation.
5. Do not calculate figures or invent facts.
6. Do not approve or reject a loan or assess creditworthiness.
7. Return at most three distinct, concise questions.
8. Prefer direct questions that address the actual finding.
9. Return valid JSON with one key named "questions",
   containing a list of strings.
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

        result = json.loads(response["message"]["content"])
        generated = result.get("questions")

        if not isinstance(generated, list):
            return fallback

        if not all(
            isinstance(question, str)
            for question in generated
        ):
            return fallback

        # Remove empty and duplicate questions.
        cleaned = list(dict.fromkeys(
            question.strip()
            for question in generated
            if question.strip()
        ))

        # Do not display unsupported or excessive output.
        cleaned = cleaned[:3]

        return cleaned if cleaned else fallback

    except Exception:
        # Keep the application functional if Ollama is unavailable.
        return fallback
