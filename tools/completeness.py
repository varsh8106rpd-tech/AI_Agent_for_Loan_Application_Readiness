REQUIRED_FIELDS = ["application_id", "applicant_name", "employment_type"]
REQUIRED_DOCUMENTS = ["identity_information", "income_proof", "bank_financial_records"]


def check_completeness(application: dict) -> dict:
    missing = []
    findings = []
    questions = []

    for field in REQUIRED_FIELDS:
        value = application.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
            findings.append(f"Required field is missing: {field.replace('_', ' ')}.")
            questions.append(f"Please provide {field.replace('_', ' ')}.")

    documents = application.get("documents") or {}
    for document in REQUIRED_DOCUMENTS:
        if not documents.get(document, False):
            missing.append(f"document:{document}")
            findings.append(f"Required information/evidence not marked as supplied: {document.replace('_', ' ')}.")
            questions.append(f"Please supply or confirm {document.replace('_', ' ')}.")

    return {
        "missing_items": missing,
        "findings": findings,
        "questions": questions,
        "summary": "No missing required items found." if not missing else f"Found {len(missing)} missing required item(s).",
    }
