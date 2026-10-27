
from tools.completeness import check_completeness
from tools.financial_calculator import calculate_financial_summary
from tools.consistency_checker import check_consistency
from tools.result_verifier import verify_financial_summary


def valid_number(value):
    """Return True if value is a non-negative numeric input."""
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def run_readiness_agent(application: dict) -> dict:
    """Select and execute tools according to application state."""

    trace = []
    findings = []
    questions = []

    # 1. Always check application completeness.
    completeness = check_completeness(application)
    trace.append({
        "step": len(trace) + 1,
        "tool": "check_completeness",
        "result": completeness["summary"],
    })
    findings.extend(completeness["findings"])
    questions.extend(completeness["questions"])

    # 2. Calculate the financial summary.
    # The calculator reports invalid or missing financial inputs.
    financial_summary = calculate_financial_summary(application)
    trace.append({
        "step": len(trace) + 1,
        "tool": "calculate_financial_summary",
        "result": (
            "Calculation completed with valid inputs."
            if not financial_summary["input_errors"]
            else "Input errors detected; review required."
        ),
    })

    # 3. Select consistency checking only when both income
    # values are available and valid.
    declared = application.get("declared_monthly_income")
    recorded = application.get("record_monthly_income")

    if valid_number(declared) and valid_number(recorded):
        consistency = check_consistency(application)
        trace.append({
            "step": len(trace) + 1,
            "tool": "check_consistency",
            "result": consistency["summary"],
        })
        findings.extend(consistency["findings"])
        questions.extend(consistency["questions"])
    else:
        consistency = {
            "issues": ["income_data_unavailable"],
            "findings": [],
            "questions": [],
        }
        trace.append({
            "step": len(trace) + 1,
            "tool": "check_consistency",
            "result": "Skipped: valid income values are required.",
        })
        findings.append(
            "Income consistency could not be checked because valid income values are unavailable."
        )
        questions.append(
            "Please provide valid declared monthly income and supplied-record income."
        )

    # 4. Verify calculations only if all financial inputs are valid.
    if not financial_summary["input_errors"]:
        verification = verify_financial_summary(
            application, financial_summary
        )
        trace.append({
            "step": len(trace) + 1,
            "tool": "verify_financial_summary",
            "result": verification["summary"],
        })
    else:
        verification = {
            "passed": False,
            "checks": {},
            "summary": "Skipped because financial inputs are invalid.",
        }
        trace.append({
            "step": len(trace) + 1,
            "tool": "verify_financial_summary",
            "result": "Skipped: correct the financial inputs first.",
        })

    if not verification["passed"] and not financial_summary["input_errors"]:
        findings.append(
            "Financial summary verification failed; technical review is required."
        )
        questions.append(
            "Please inspect the financial calculations before relying on this report."
        )

    # 5. Determine application readiness, never loan eligibility.
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
        "decision_boundary": (
            "Readiness only. No approval, rejection, "
            "or creditworthiness decision."
        ),
    }
