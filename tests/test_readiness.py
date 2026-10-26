from agent.orchestrator import run_readiness_agent


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
