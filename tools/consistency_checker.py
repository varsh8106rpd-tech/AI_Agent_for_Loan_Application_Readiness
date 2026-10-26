def check_consistency(application: dict, tolerance: float = 1.0) -> dict:
    findings = []
    questions = []
    issues = []

    try:
        declared = float(application.get("declared_monthly_income"))
        recorded = float(application.get("record_monthly_income"))
        if declared < 0 or recorded < 0:
            issues.append("negative_income")
            findings.append("Declared or recorded income is negative.")
            questions.append("Please correct the negative income value.")
        elif abs(declared - recorded) > tolerance:
            issues.append("income_mismatch")
            findings.append(
                f"Declared monthly income (₹{declared:,.2f}) differs from supplied-record income (₹{recorded:,.2f})."
            )
            questions.append(
                "Please clarify the difference between declared monthly income and the amount shown in the supplied records."
            )
    except (TypeError, ValueError):
        issues.append("income_unavailable")
        findings.append("Income consistency could not be checked because one or both income values are missing or non-numeric.")
        questions.append("Please provide valid declared income and income-record figures.")

    summary = "No configured consistency issue found." if not issues else f"Found {len(issues)} consistency issue(s)."
    return {"issues": issues, "findings": findings, "questions": questions, "summary": summary}
