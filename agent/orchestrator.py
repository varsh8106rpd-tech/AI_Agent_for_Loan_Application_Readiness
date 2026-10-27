
from agent.llm_assistant import generate_reviewer_questions
from tools.completeness import check_completeness
from tools.financial_calculator import calculate_financial_summary
from tools.consistency_checker import check_consistency
from tools.result_verifier import verify_financial_summary


def valid_number(value):
    """Return True if value is a non-negative numeric input."""
    try:
        number = float(value)
        return number >= 0
    except (TypeError, ValueError):
        return False


def run_readiness_agent(application: dict) -> dict:
    """
    Check application readiness using Python tools and a local LLM.

    The LLM generates reviewer questions only. It does not control
    financial calculations, verification, or readiness status.
    """

    trace = []
    findings = []
    questions = []

    # 1. Check application completeness.
    completeness = check_completeness(application)

    trace.append({
        "step": len(trace) + 1,
        "tool": "check_completeness",
        "result": completeness["summary"],
    })

    findings.extend(completeness["findings"])
    questions.extend(completeness["questions"])

    # 2. Calculate the financial summary.
    financial_summary = calculate_financial_summary(application)

    input_errors = financial_summary["input_errors"]

    trace.append({
        "step": len(trace) + 1,
        "tool": "calculate_financial_summary",
        "result": (
            "Calculation completed with valid inputs."
            if not input_errors
            else "Input errors detected; review required."
        ),
    })

    # 3. Check income consistency only when both values are valid.
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
            "Income consistency could not be checked because "
            "valid income values are unavailable."
        )

        questions.append(
            "Please provide valid declared monthly income "
            "and supplied-record income."
        )

    # 4. Verify the financial summary only when inputs are valid.
    if not input_errors:
        verification = verify_financial_summary(
            application,
            financial_summary,
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

    if not verification["passed"] and not input_errors:
        findings.append(
            "Financial summary verification failed; "
            "technical review is required."
        )

        questions.append(
            "Please inspect the financial calculations before "
            "relying on this report."
        )

    # 5. Determine readiness using Python rules only.
    if completeness["missing_items"] or input_errors:
        status = "Incomplete"

    elif consistency["issues"] or not verification["passed"]:
        status = "Needs clarification"

    else:
        status = "Ready for human review"

    # 6. Ask the local LLM to improve reviewer questions.
    # The LLM cannot modify findings, calculations, or status.
    existing_questions = list(dict.fromkeys(questions))
    llm_questions = generate_reviewer_questions(
        findings=findings,
        existing_questions=existing_questions,
    )

    # Keep rule-based questions if the LLM returns unusable output.
    if (
        not isinstance(llm_questions, list)
        or not all(
            isinstance(question, str)
            for question in llm_questions
        )
    ):
        llm_questions = existing_questions

    llm_questions = [
        question.strip()
        for question in llm_questions
        if question.strip()
    ]

    if not llm_questions:
        llm_questions = existing_questions

    trace.append({
        "step": len(trace) + 1,
        "tool": "generate_reviewer_questions",
        "result": (
            "Local LLM generated reviewer questions."
            if llm_questions != existing_questions
            else "Existing reviewer questions retained."
        ),
    })

    # 7. Return the report.
    return {
        "application_id": application.get("application_id", ""),
        "status": status,
        "findings": list(dict.fromkeys(findings)),
        "reviewer_questions": llm_questions,
        "financial_summary": financial_summary,
        "verification": verification,
        "execution_trace": trace,
        "decision_boundary": (
            "Readiness only. No approval, rejection, "
            "or creditworthiness decision."
        ),
    }
