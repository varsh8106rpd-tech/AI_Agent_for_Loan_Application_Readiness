from tools.completeness import check_completeness
from tools.financial_calculator import calculate_financial_summary
from tools.consistency_checker import check_consistency
from tools.result_verifier import verify_financial_summary


def run_readiness_agent(application: dict) -> dict:
    """Run a transparent tool-using workflow; no lending decision is made."""
    trace = []
    findings = []
    questions = []

    completeness = check_completeness(application)
    trace.append({"step": 1, "tool": "check_completeness", "result": completeness["summary"]})
    findings.extend(completeness["findings"])
    questions.extend(completeness["questions"])

    financial_summary = calculate_financial_summary(application)
    trace.append({"step": 2, "tool": "calculate_financial_summary", "result": "Calculated income, outgoings, disposable income and DTI."})

    consistency = check_consistency(application)
    trace.append({"step": 3, "tool": "check_consistency", "result": consistency["summary"]})
    findings.extend(consistency["findings"])
    questions.extend(consistency["questions"])

    verification = verify_financial_summary(application, financial_summary)
    trace.append({"step": 4, "tool": "verify_financial_summary", "result": verification["summary"]})
    if not verification["passed"]:
        findings.append("Financial summary verification failed; results require technical review.")
        questions.append("Please rerun or inspect the financial calculations before relying on this report.")

    if completeness["missing_items"] or financial_summary["input_errors"]:
        status = "Incomplete"
    elif consistency["issues"] or not verification["passed"]:
        status = "Needs clarification"
    else:
        status = "Ready for human review"

    return {
        "application_id": application.get("application_id", ""),
        "status": status,
        "findings": list(dict.fromkeys(findings)),
        "reviewer_questions": list(dict.fromkeys(questions)),
        "financial_summary": financial_summary,
        "verification": verification,
        "execution_trace": trace,
        "decision_boundary": "Readiness only. No approval, rejection, or creditworthiness decision.",
    }
