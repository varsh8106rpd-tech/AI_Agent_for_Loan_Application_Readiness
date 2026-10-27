from agent.orchestrator import run_readiness_agent
from tools.financial_calculator import calculate_financial_summary


def sample():
    return {
        "application_id": "SYN-001",
        "applicant_name": "Alex Sample",
        "employment_type": "Salaried",
        "declared_monthly_income": 60000,
        "record_monthly_income": 60000,
        "monthly_expenses": 20000,
        "monthly_debt_payments": 10000,
        "requested_loan_amount": 300000,
        "proposed_monthly_instalment": 5000,
        "documents": {
            "identity_information": True,
            "income_proof": True,
            "bank_financial_records": True,
        },
    }


def test_complete_consistent_application_is_ready_for_review():
    report = run_readiness_agent(sample())
    assert report["status"] == "Ready for human review"
    assert report["verification"]["passed"] is True


def test_missing_document_is_incomplete():
    application = sample()
    application["documents"]["income_proof"] = False
    report = run_readiness_agent(application)
    assert report["status"] == "Incomplete"


def test_income_mismatch_needs_clarification():
    application = sample()
    application["record_monthly_income"] = 55000
    report = run_readiness_agent(application)
    assert report["status"] == "Needs clarification"
    assert any("differs" in finding for finding in report["findings"])


def test_financial_calculations_are_transparent():
    report = run_readiness_agent(sample())
    summary = report["financial_summary"]
    assert summary["disposable_income"] == 30000
    assert summary["debt_to_income_ratio_percent"] == 16.67
    assert summary["disposable_income_after_proposed_instalment"] == 25000


def test_agent_never_makes_a_loan_approval_decision():
    report = run_readiness_agent(sample())

    assert report["status"] == "Ready for human review"
    assert "No approval" in report["decision_boundary"]
    assert "creditworthiness" in report["decision_boundary"]


def test_execution_trace_includes_llm_question_step():
    report = run_readiness_agent(sample())

    tool_names = [
        step["tool"] for step in report["execution_trace"]
    ]

    assert "check_completeness" in tool_names
    assert "calculate_financial_summary" in tool_names
    assert "check_consistency" in tool_names
    assert "verify_financial_summary" in tool_names
    assert "generate_reviewer_questions" in tool_names


def test_reviewer_questions_have_expected_type():
    report = run_readiness_agent(sample())

    assert isinstance(report["reviewer_questions"], list)
    assert all(
        isinstance(question, str)
        for question in report["reviewer_questions"]
    )

def test_negative_income_makes_application_incomplete():
    application = sample()
    application["declared_monthly_income"] = -1000

    report = run_readiness_agent(application)

    assert report["status"] == "Incomplete"
    assert report["financial_summary"]["input_errors"]


def test_missing_income_makes_application_incomplete():
    application = sample()
    application.pop("declared_monthly_income")

    report = run_readiness_agent(application)

    assert report["status"] == "Incomplete"
    assert report["financial_summary"]["input_errors"]


def test_zero_income_does_not_cause_division_by_zero():
    application = sample()
    application["declared_monthly_income"] = 0

    summary = calculate_financial_summary(application)

    assert summary["gross_monthly_income"] == 0
    assert summary["debt_to_income_ratio_percent"] is None
    assert summary["input_errors"] == []

def test_nan_income_is_rejected():
    application = sample()
    application["declared_monthly_income"] = float("nan")

    report = run_readiness_agent(application)

    assert report["status"] == "Incomplete"
    assert report["financial_summary"]["input_errors"]


def test_infinite_income_is_rejected():
    application = sample()
    application["declared_monthly_income"] = float("inf")

    report = run_readiness_agent(application)

    assert report["status"] == "Incomplete"
    assert report["financial_summary"]["input_errors"]
